"""
Testes unitários para as integrações de canais (Telegram, WhatsApp, CoreAdapter)
e o diretório da Rede de Apoio.
"""

from unittest.mock import MagicMock, patch
import pytest

from src.channels.core_adapter import VoxChannelCore
from src.channels.telegram_bot import TelegramBot
from src.channels.whatsapp_bot import WhatsAppBot
from src.app.pages.rede_apoio import REDE_APOIO_DATA


@pytest.mark.unit
def test_core_adapter_anonymous_session():
    core = VoxChannelCore(salt="test_salt_123")
    sess1 = core.get_anonymous_session_id("telegram", "123456789")
    sess2 = core.get_anonymous_session_id("telegram", "123456789")
    sess_diff = core.get_anonymous_session_id("telegram", "987654321")
    sess_wa = core.get_anonymous_session_id("whatsapp", "123456789")

    # Mesmos parâmetros geram o mesmo hash determinístico
    assert sess1 == sess2
    # IDs diferentes geram hashes diferentes
    assert sess1 != sess_diff
    # Canais diferentes geram identificadores distintos
    assert sess1 != sess_wa
    # O identificador não deve conter o dado bruto
    assert "123456789" not in sess1
    assert sess1.startswith("tel_")


@pytest.mark.unit
@patch("src.channels.core_adapter.salvar_sessao")
@patch("src.channels.core_adapter.semantica")
@patch("src.channels.core_adapter.gerar_resposta")
@patch("src.channels.core_adapter.salvar_log_chat")
@patch("src.channels.core_adapter.inicializar_chat_modelo")
def test_core_adapter_process_user_message_success(
    mock_init_chat, mock_log_chat, mock_gerar_resp, mock_semantica, mock_salvar_sessao
):
    mock_semantica.return_value = ("retificacao", "Contexto sobre retificação no cartório", [101, 102])
    mock_gerar_resp.return_value = "Para retificar o nome, procure o cartório de registro civil."
    mock_init_chat.return_value = MagicMock()

    core = VoxChannelCore()
    res = core.process_user_message("telegram", "user_999", "Como faço para mudar meu nome?")

    assert res["success"] is True
    assert "cartório" in res["response_text"]
    assert res["matched_topic"] == "retificacao"
    assert res["reference_ids"] == [101, 102]
    mock_log_chat.assert_called_once()


@pytest.mark.unit
def test_core_adapter_process_empty_message():
    core = VoxChannelCore()
    res = core.process_user_message("whatsapp", "5511999999999", "   ")
    assert res["success"] is False
    assert "vazia" in res["response_text"]


@pytest.mark.unit
@patch("src.channels.core_adapter.semantica", side_effect=Exception("Database connection failure"))
@patch("src.channels.core_adapter.salvar_erro")
def test_core_adapter_process_error_handling(mock_salvar_erro, mock_semantica):
    mock_salvar_erro.return_value = "ERR-TEST-500"
    core = VoxChannelCore()
    # Mocking chat initialization to fail
    with patch.object(core, "get_or_create_chat", side_effect=Exception("LLM offline")):
        res = core.process_user_message("telegram", "user_1", "Olá!")
        assert res["success"] is False
        assert "imprevisto técnico" in res["response_text"]
        assert "ERR-TEST-500" in res["response_text"]


@pytest.mark.unit
def test_telegram_bot_is_configured():
    bot_unconfigured = TelegramBot(token="")
    assert bot_unconfigured.is_configured() is False

    bot_configured = TelegramBot(token="123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11")
    assert bot_configured.is_configured() is True


@pytest.mark.unit
def test_telegram_bot_message_splitting():
    bot = TelegramBot(token="dummy_token")
    sent_chunks = []

    def mock_make_request(method, payload, timeout=30):
        if method == "sendMessage":
            sent_chunks.append(payload["text"])
            return {"ok": True, "result": {"message_id": len(sent_chunks)}}
        return {"ok": True}

    bot._make_request = mock_make_request

    # Mensagem de 9000 caracteres
    long_text = ("Linha de texto explicativo sobre direitos e acolhimento.\n" * 160)
    assert len(long_text) > 4096

    success = bot.send_message(chat_id=12345, text=long_text)
    assert success is True
    # Deve ter dividido em múltiplos blocos
    assert len(sent_chunks) >= 2
    for chunk in sent_chunks:
        assert len(chunk) <= 4000


@pytest.mark.unit
def test_telegram_bot_commands():
    bot = TelegramBot(token="dummy_token")
    mock_send = MagicMock()
    bot.send_message = mock_send

    # Teste comando /start
    update_start = {"message": {"chat": {"id": 100}, "from": {"id": 200}, "text": "/start"}}
    bot.process_update(update_start)
    mock_send.assert_called_once()
    assert "Vox AI" in mock_send.call_args[0][1]

    # Teste comando /apoio
    mock_send.reset_mock()
    update_apoio = {"message": {"chat": {"id": 100}, "from": {"id": 200}, "text": "/apoio"}}
    bot.process_update(update_apoio)
    mock_send.assert_called_once()
    assert "Rede de Apoio" in mock_send.call_args[0][1]


@pytest.mark.unit
def test_whatsapp_webhook_verification():
    bot = WhatsAppBot(verify_token="meu_token_secreto")

    # Sucesso
    ok_params = {
        "hub.mode": "subscribe",
        "hub.verify_token": "meu_token_secreto",
        "hub.challenge": "1158201444",
    }
    success, challenge = bot.verify_webhook_challenge(ok_params)
    assert success is True
    assert challenge == "1158201444"

    # Token incorreto
    bad_params = {
        "hub.mode": "subscribe",
        "hub.verify_token": "token_errado",
        "hub.challenge": "1158201444",
    }
    success_bad, challenge_bad = bot.verify_webhook_challenge(bad_params)
    assert success_bad is False
    assert challenge_bad is None


@pytest.mark.unit
def test_whatsapp_extract_messages_from_webhook():
    bot = WhatsAppBot()
    sample_webhook_payload = {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "123456789",
                "changes": [
                    {
                        "value": {
                            "messaging_product": "whatsapp",
                            "metadata": {"display_phone_number": "15550234567"},
                            "contacts": [{"profile": {"name": "Alex"}, "wa_id": "5511999998888"}],
                            "messages": [
                                {
                                    "from": "5511999998888",
                                    "id": "wamid.HBgLMTU1NTAyMzQ1NjcVAgASGBQz",
                                    "timestamp": "1720000000",
                                    "text": {"body": "Como conseguir a PrEP pelo SUS?"},
                                    "type": "text",
                                }
                            ],
                        },
                        "field": "messages",
                    }
                ],
            }
        ],
    }

    extracted = bot.extract_messages_from_webhook(sample_webhook_payload)
    assert len(extracted) == 1
    assert extracted[0]["from"] == "5511999998888"
    assert extracted[0]["type"] == "text"
    assert extracted[0]["profile_name"] == "Alex"
    assert extracted[0]["raw_message"]["text"]["body"] == "Como conseguir a PrEP pelo SUS?"


@pytest.mark.unit
def test_whatsapp_handle_button_reply():
    bot = WhatsAppBot()
    bot.send_text_message = MagicMock()

    msg_info = {
        "from": "5511999998888",
        "message_id": "wamid.123",
        "type": "interactive",
        "raw_message": {
            "interactive": {
                "type": "button_reply",
                "button_reply": {"id": "btn_apoio", "title": "Rede de Apoio 🏠"},
            }
        },
    }

    bot.handle_incoming_message(msg_info)
    bot.send_text_message.assert_called_once()
    assert "Rede de Apoio Emergencial" in bot.send_text_message.call_args[0][1]


@pytest.mark.unit
def test_rede_apoio_dataset_integrity():
    assert len(REDE_APOIO_DATA) >= 10
    ufs_presentes = set(item["uf"] for item in REDE_APOIO_DATA)
    assert "SP" in ufs_presentes
    assert "RJ" in ufs_presentes
    assert "Nacional" in ufs_presentes

    for item in REDE_APOIO_DATA:
        assert item["nome"]
        assert item["categoria"] in [
            "Casas de Acolhimento",
            "Centros Públicos de Referência",
            "ONGs e Coletivos",
            "Saúde e Ambulatórios",
            "Profissionais Afirmativos",
        ]
        assert item["descricao"]
        assert isinstance(item["tags"], list)
        assert len(item["tags"]) > 0
        assert isinstance(item["gratuito"], bool)


@pytest.mark.unit
def test_whatsapp_message_splitting():
    bot = WhatsAppBot(phone_number_id="12345", access_token="secret_token")
    sent_payloads = []

    def mock_send_api(payload):
        sent_payloads.append(payload)
        return {"messages": [{"id": f"wamid.{len(sent_payloads)}"}]}

    bot._send_api_request = mock_send_api

    # Mensagem de 9000 caracteres
    long_text = ("Linha de texto informativo sobre retificação e direitos.\n" * 160)
    assert len(long_text) > 4096

    success = bot.send_text_message("5511999999999", long_text)
    assert success is True
    assert len(sent_payloads) >= 2
    for p in sent_payloads:
        assert len(p["text"]["body"]) <= 4000


@pytest.mark.unit
def test_whatsapp_extract_messages_status_webhook_safety():
    bot = WhatsAppBot()
    # Payload típico da Meta contendo apenas evento de status de entrega (sem "messages" ou com null)
    status_payload = {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "123456",
                "changes": [
                    {
                        "field": "messages",
                        "value": {
                            "messaging_product": "whatsapp",
                            "metadata": {"display_phone_number": "1555"},
                            "statuses": [{"id": "wamid.123", "status": "delivered"}],
                            "messages": None,
                        },
                    }
                ],
            }
        ],
    }
    extracted = bot.extract_messages_from_webhook(status_payload)
    assert extracted == []


@pytest.mark.unit
@patch("src.core.genai.transcrever_audio")
def test_whatsapp_handle_audio_message(mock_transcribe):
    mock_transcribe.return_value = "Quais são os meus direitos no trabalho?"
    bot = WhatsAppBot(phone_number_id="12345", access_token="token")
    bot.get_media_url = MagicMock(return_value="https://cdn.whatsapp.com/audio/123.ogg")
    bot.download_media_bytes = MagicMock(return_value=b"fake_ogg_bytes")
    bot.send_text_message = MagicMock(return_value=True)

    msg_info = {
        "from": "5511999998888",
        "message_id": "wamid.audio123",
        "type": "audio",
        "raw_message": {
            "audio": {"id": "media_999", "mime_type": "audio/ogg; codecs=opus"}
        },
    }

    with patch.object(bot.core, "process_user_message") as mock_core:
        mock_core.return_value = {"response_text": "Você tem direito à equiparação salarial..."}
        bot.handle_incoming_message(msg_info)
        mock_transcribe.assert_called_once()
        mock_core.assert_called_once_with(
            channel="whatsapp",
            user_id="5511999998888",
            message_text="Quais são os meus direitos no trabalho?",
        )


@pytest.mark.unit
def test_telegram_bot_commands_case_insensitive_and_mentions():
    bot = TelegramBot(token="dummy_token")
    mock_send = MagicMock()
    bot.send_message = mock_send

    # Teste comando em caixa alta /START
    bot.process_update({"message": {"chat": {"id": 100}, "from": {"id": 200}, "text": "/START"}})
    assert mock_send.call_count == 1
    assert "Vox AI" in mock_send.call_args[0][1]

    # Teste comando com menção de bot /ajuda@VoxAIBot
    mock_send.reset_mock()
    bot.process_update({"message": {"chat": {"id": 100}, "from": {"id": 200}, "text": "/ajuda@VoxAIBot"}})
    assert mock_send.call_count == 1
    assert "Sobre o Vox AI" in mock_send.call_args[0][1]

    # Teste comando /apoio em caixa mista /Apoio
    mock_send.reset_mock()
    bot.process_update({"message": {"chat": {"id": 100}, "from": {"id": 200}, "text": "/Apoio"}})
    assert mock_send.call_count == 1
    assert "Rede de Apoio" in mock_send.call_args[0][1]

    # Teste que texto com prefixo similar mas que NÃO é o comando não é interceptado como comando
    mock_send.reset_mock()
    with patch.object(bot.core, "process_user_message") as mock_core:
        mock_core.return_value = {"response_text": "Resposta processada pelo core."}
        bot.process_update({"message": {"chat": {"id": 100}, "from": {"id": 200}, "text": "/starting a new project"}})
        mock_core.assert_called_once()


@pytest.mark.unit
@patch("src.core.audio.configurar_api_gemini")
def test_transcrever_audio_mime_type_inference(mock_config_api):
    import io
    from src.core.genai import transcrever_audio

    mock_client = MagicMock()
    mock_config_api.return_value = mock_client
    mock_client.models.generate_content.return_value = MagicMock(text="Transcrição de teste")

    # Arquivo .ogg sem mime_type explícito deve inferir audio/ogg
    audio_ogg = io.BytesIO(b"fake_ogg")
    audio_ogg.name = "nota_de_voz.ogg"
    res = transcrever_audio(audio_ogg)
    assert res == "Transcrição de teste"
    call_contents = mock_client.models.generate_content.call_args[1]["contents"]
    part_obj = call_contents[1]
    assert part_obj.inline_data.mime_type == "audio/ogg"


@pytest.mark.unit
def test_rede_apoio_filters():
    # Teste de busca por termo
    termo = "acolhimento"
    resultado_termo = [
        item for item in REDE_APOIO_DATA
        if termo in f"{item['nome']} {item['cidade']} {item['descricao']} {' '.join(item['tags'])}".lower()
    ]
    assert len(resultado_termo) > 0

    # Teste de filtro por estado (SP)
    resultado_sp = [item for item in REDE_APOIO_DATA if item["uf"] in ("SP", "Nacional")]
    assert len(resultado_sp) >= 3

    # Teste de filtro somente gratuitos
    resultado_gratis = [item for item in REDE_APOIO_DATA if item.get("gratuito")]
    assert len(resultado_gratis) > 0
    assert all(item["gratuito"] for item in resultado_gratis)


@pytest.mark.unit
@patch("streamlit.title")
def test_render_rede_apoio_show_title_flag(mock_st_title):
    from src.app.pages.rede_apoio import render_rede_apoio
    with patch("streamlit.text_input", return_value=""), \
         patch("streamlit.selectbox", return_value="Todas as Categorias"), \
         patch("streamlit.checkbox", return_value=False), \
         patch("streamlit.columns", return_value=[MagicMock(), MagicMock(), MagicMock()]):
        render_rede_apoio(show_title=False)
        mock_st_title.assert_not_called()

        render_rede_apoio(show_title=True)
        mock_st_title.assert_called_once_with("🤝 Rede de Apoio e Acolhimento Vox")


"""
Testes unitários para o módulo core de áudio (STT e TTS com Gemini e fallback gTTS).
"""

import io
from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest

from src.core.audio import (
    _detectar_mime_audio,
    _pcm_to_wav,
    _sanitizar_texto,
    gerar_fala_gemini,
    transcrever_audio_gemini,
)


@pytest.mark.unit
class TestSanitizacaoEUtilitariosAudio:
    """Testes para funções utilitárias internas do módulo de áudio."""

    def test_sanitizar_texto_valido(self):
        texto = "Olá, tudo bem? Sou o Vox AI! Ajudo pessoas LGBTQIA+."
        resultado = _sanitizar_texto(texto)
        assert "Olá, tudo bem? Sou o Vox AI!" in resultado
        assert "LGBTQIA+" in resultado

    def test_sanitizar_texto_vazio_ou_none(self):
        assert _sanitizar_texto("") == ""
        assert _sanitizar_texto(None) == ""
        assert _sanitizar_texto("   ") == ""

    def test_sanitizar_texto_remove_caracteres_perigosos(self):
        texto = "<script>alert('hack');</script> Olá @ # $ % ^ & * [ ] { }"
        resultado = _sanitizar_texto(texto)
        assert "<" not in resultado
        assert ">" not in resultado
        assert "alert" in resultado
        assert "Olá" in resultado

    def test_sanitizar_texto_markdown_links_e_formatacao(self):
        texto = "Acesse o [Guia LGBTQIA+](https://vox.org.br/guia) ou ligue para o [Disque 100](tel:100). Veja mais em https://site.com."
        resultado = _sanitizar_texto(texto)
        assert "Guia LGBTQIA+" in resultado
        assert "Disque 100" in resultado
        assert "https" not in resultado
        assert "vox.org.br" not in resultado
        assert "site.com" not in resultado

    def test_detectar_mime_audio_formatos(self):
        # WAV
        assert _detectar_mime_audio(b"RIFF\x24\x00\x00\x00WAVEfmt ") == "audio/wav"
        # OGG
        assert _detectar_mime_audio(b"OggS\x00\x02\x00\x00") == "audio/ogg"
        # WebM
        assert _detectar_mime_audio(b"\x1a\x45\xdf\xa3\x9f\x42\x86") == "audio/webm"
        # FLAC
        assert _detectar_mime_audio(b"fLaC\x00\x00\x00\x22") == "audio/flac"
        # MP3 ID3
        assert _detectar_mime_audio(b"ID3\x04\x00\x00") == "audio/mp3"
        # MP3 sync frame
        assert _detectar_mime_audio(b"\xff\xfb\x90\x64") == "audio/mp3"
        # Fallback desconhecido
        assert _detectar_mime_audio(b"\x00\x01\x02\x03", fallback_mime="audio/raw") == "audio/raw"
        assert _detectar_mime_audio(b"", fallback_mime="audio/mp3") == "audio/mp3"

    def test_pcm_to_wav_cria_cabecalho_riff_valido(self):
        dados_pcm = b"\x00\x00" * 240  # Amostras PCM silenciosas
        wav_bytes = _pcm_to_wav(dados_pcm, sample_rate=24000, channels=1, sample_width=2)
        assert wav_bytes.startswith(b"RIFF")
        assert b"WAVE" in wav_bytes
        assert b"fmt " in wav_bytes
        assert b"data" in wav_bytes
        assert len(wav_bytes) > len(dados_pcm)


@pytest.mark.unit
class TestTranscricaoAudioGemini:
    """Testes unitários para transcrever_audio_gemini (Speech-to-Text)."""

    def test_transcrever_audio_gemini_sucesso_bytes(self):
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "Identidade de gênero e direitos sociais."
        mock_client.models.generate_content.return_value = mock_response

        audio_bytes = b"fake-audio-bytes-12345"
        resultado = transcrever_audio_gemini(
            audio_data=audio_bytes,
            mime_type="audio/mp3",
            client=mock_client,
        )

        assert resultado == "Identidade de gênero e direitos sociais."
        mock_client.models.generate_content.assert_called_once()
        _, kwargs = mock_client.models.generate_content.call_args
        assert len(kwargs["contents"]) == 2
        assert "Transcreva com máxima precisão" in kwargs["contents"][0]

    def test_transcrever_audio_gemini_sucesso_buffer(self):
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "Acolhimento e respeito a todas as identidades."
        mock_client.models.generate_content.return_value = mock_response

        buffer = io.BytesIO(b"audio-in-memory-buffer")
        resultado = transcrever_audio_gemini(
            audio_data=buffer,
            client=mock_client,
        )

        assert resultado == "Acolhimento e respeito a todas as identidades."
        mock_client.models.generate_content.assert_called_once()

    def test_transcrever_audio_gemini_sucesso_caminho_arquivo_str(self, tmp_path):
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "Áudio lido a partir de arquivo em disco."
        mock_client.models.generate_content.return_value = mock_response

        arquivo_audio = tmp_path / "pergunta.wav"
        arquivo_audio.write_bytes(b"RIFF\x24\x00\x00\x00WAVEfmt " + b"\x00" * 40)

        resultado = transcrever_audio_gemini(
            audio_data=str(arquivo_audio),
            client=mock_client,
        )

        assert resultado == "Áudio lido a partir de arquivo em disco."
        mock_client.models.generate_content.assert_called_once()
        _, kwargs = mock_client.models.generate_content.call_args
        part = kwargs["contents"][1]
        assert part.inline_data.mime_type == "audio/wav"

    def test_transcrever_audio_gemini_sucesso_caminho_pathlib(self, tmp_path):
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "Áudio via pathlib.Path."
        mock_client.models.generate_content.return_value = mock_response

        arquivo_audio = tmp_path / "depoimento.mp3"
        arquivo_audio.write_bytes(b"ID3\x04\x00\x00" + b"\x00" * 50)

        resultado = transcrever_audio_gemini(
            audio_data=arquivo_audio,
            client=mock_client,
        )

        assert resultado == "Áudio via pathlib.Path."
        mock_client.models.generate_content.assert_called_once()

    def test_transcrever_audio_gemini_arquivo_inexistente(self):
        mock_client = MagicMock()
        resultado = transcrever_audio_gemini(
            audio_data="/caminho/inexistente/de/audio.mp3",
            client=mock_client,
        )
        assert resultado is None
        mock_client.models.generate_content.assert_not_called()

    def test_transcrever_audio_gemini_sniff_magic_bytes_wav(self):
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "Transcrição com detecção automática de WAV."
        mock_client.models.generate_content.return_value = mock_response

        wav_bytes = b"RIFF\x24\x00\x00\x00WAVEfmt " + b"\x00" * 40
        resultado = transcrever_audio_gemini(wav_bytes, client=mock_client)

        assert resultado == "Transcrição com detecção automática de WAV."
        _, kwargs = mock_client.models.generate_content.call_args
        part = kwargs["contents"][1]
        assert part.inline_data.mime_type == "audio/wav"

    def test_transcrever_audio_gemini_autodetecta_tipo_uploaded_file(self):
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "Texto transcrito com sucesso."
        mock_client.models.generate_content.return_value = mock_response

        mock_file = MagicMock()
        mock_file.read.return_value = b"wav-bytes-data"
        mock_file.type = "audio/wav"

        resultado = transcrever_audio_gemini(
            audio_data=mock_file,
            client=mock_client,
        )

        assert resultado == "Texto transcrito com sucesso."
        mock_client.models.generate_content.assert_called_once()

    def test_transcrever_audio_gemini_dados_nulos_ou_vazios(self):
        mock_client = MagicMock()

        assert transcrever_audio_gemini(None, client=mock_client) is None
        assert transcrever_audio_gemini(b"", client=mock_client) is None
        assert transcrever_audio_gemini(io.BytesIO(b""), client=mock_client) is None

        mock_client.models.generate_content.assert_not_called()

    def test_transcrever_audio_gemini_tipo_invalido(self):
        mock_client = MagicMock()
        assert transcrever_audio_gemini(12345, client=mock_client) is None
        mock_client.models.generate_content.assert_not_called()

    @patch("src.core.audio.configurar_api_gemini", return_value=None)
    def test_transcrever_audio_gemini_sem_cliente(self, _mock_cfg):
        resultado = transcrever_audio_gemini(b"dados-de-audio")
        assert resultado is None

    def test_transcrever_audio_gemini_excecao_api(self):
        mock_client = MagicMock()
        mock_client.models.generate_content.side_effect = Exception("Erro 500: API Failure")

        resultado = transcrever_audio_gemini(b"dados-de-audio", client=mock_client)
        assert resultado is None

    @patch("streamlit.toast")
    def test_transcrever_audio_gemini_fallback_cascade_multi_model(self, mock_toast):
        mock_client = MagicMock()
        mock_resp_success = MagicMock(text="Transcrição recuperada com sucesso pelo modelo 2.")
        mock_client.models.generate_content.side_effect = [
            Exception("429 ResourceExhausted: Quota exceeded"),
            mock_resp_success,
        ]

        resultado = transcrever_audio_gemini(b"dados-de-audio", client=mock_client)
        assert resultado == "Transcrição recuperada com sucesso pelo modelo 2."
        assert mock_client.models.generate_content.call_count == 2
        mock_toast.assert_called_once()

    def test_transcrever_audio_gemini_resposta_sem_texto(self):
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.text = None
        mock_client.models.generate_content.return_value = mock_response

        resultado = transcrever_audio_gemini(b"dados-de-audio", client=mock_client)
        assert resultado is None

    def test_facade_genai_transcrever_audio(self):
        from src.core.genai import transcrever_audio

        with patch("src.core.audio.transcrever_audio_gemini") as mock_transc:
            mock_transc.return_value = "Transcrição via facade genai."
            resultado = transcrever_audio(b"audio-input")
            assert resultado == "Transcrição via facade genai."
            mock_transc.assert_called_once_with(b"audio-input")


@pytest.mark.unit
class TestSinteseFalaGemini:
    """Testes unitários para gerar_fala_gemini (Text-to-Speech com fallback)."""

    def test_gerar_fala_gemini_sucesso_audio_nativo(self):
        mock_client = MagicMock()
        mock_response = MagicMock()

        fake_wav = b"RIFF" + b"\x00" * 40 + b"WAVEfmt "
        mock_part = MagicMock()
        mock_part.inline_data.data = fake_wav
        mock_part.inline_data.mime_type = "audio/wav"

        mock_candidate = MagicMock()
        mock_candidate.content.parts = [mock_part]
        mock_response.candidates = [mock_candidate]
        mock_client.models.generate_content.return_value = mock_response

        buffer = gerar_fala_gemini(
            texto="Olá, como posso ajudar você hoje?",
            voz="Puck",
            client=mock_client,
        )

        assert isinstance(buffer, io.BytesIO)
        assert buffer.getvalue() == fake_wav
        mock_client.models.generate_content.assert_called_once()
        _, kwargs = mock_client.models.generate_content.call_args
        config = kwargs["config"]
        assert "AUDIO" in config.response_modalities
        assert config.speech_config.voice_config.prebuilt_voice_config.voice_name == "Puck"

    def test_gerar_fala_gemini_sucesso_pcm_converte_para_wav(self):
        mock_client = MagicMock()
        mock_response = MagicMock()

        pcm_raw = b"\x00\x01" * 120
        mock_part = MagicMock()
        mock_part.inline_data.data = pcm_raw
        mock_part.inline_data.mime_type = "audio/pcm;rate=24000"

        mock_candidate = MagicMock()
        mock_candidate.content.parts = [mock_part]
        mock_response.candidates = [mock_candidate]
        mock_client.models.generate_content.return_value = mock_response

        buffer = gerar_fala_gemini(
            texto="Teste de áudio PCM.",
            client=mock_client,
        )

        assert isinstance(buffer, io.BytesIO)
        conteudo = buffer.getvalue()
        assert conteudo.startswith(b"RIFF")
        assert b"WAVE" in conteudo

    def test_gerar_fala_gemini_multiplos_chunks_concatenacao(self):
        """Garante que respostas com múltiplos chunks não sofram truncamento prematuro."""
        mock_client = MagicMock()
        mock_response = MagicMock()

        chunk1 = b"\x00\x01" * 60
        chunk2 = b"\x00\x02" * 60
        chunk3 = b"\x00\x03" * 60

        part1 = MagicMock()
        part1.inline_data.data = chunk1
        part1.inline_data.mime_type = "audio/pcm;rate=24000"

        part2 = MagicMock()
        part2.inline_data.data = chunk2
        part2.inline_data.mime_type = "audio/pcm;rate=24000"

        part3 = MagicMock()
        part3.inline_data.data = chunk3
        part3.inline_data.mime_type = "audio/pcm;rate=24000"

        mock_candidate = MagicMock()
        mock_candidate.content.parts = [part1, part2, part3]
        mock_response.candidates = [mock_candidate]
        mock_client.models.generate_content.return_value = mock_response

        buffer = gerar_fala_gemini("Texto com múltiplos chunks", client=mock_client)
        assert isinstance(buffer, io.BytesIO)
        conteudo = buffer.getvalue()

        assert conteudo.startswith(b"RIFF")
        # Todos os três chunks devem estar presentes sequencialmente nos dados de áudio
        assert chunk1 in conteudo
        assert chunk2 in conteudo
        assert chunk3 in conteudo
        # O tamanho total deve contemplar os 3 blocos mais o cabeçalho WAV
        tamanho_pcm_total = len(chunk1) + len(chunk2) + len(chunk3)
        assert len(conteudo) >= tamanho_pcm_total + 44

    def test_gerar_fala_gemini_normalizacao_nome_voz(self):
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_part = MagicMock()
        mock_part.inline_data.data = b"RIFF" + b"\x00" * 40 + b"WAVE"
        mock_part.inline_data.mime_type = "audio/wav"
        mock_candidate = MagicMock()
        mock_candidate.content.parts = [mock_part]
        mock_response.candidates = [mock_candidate]
        mock_client.models.generate_content.return_value = mock_response

        # Teste com voz em minúsculo e espaços: " aoede " -> "Aoede"
        gerar_fala_gemini("Texto com voz aoede", voz=" aoede ", client=mock_client)
        _, kwargs = mock_client.models.generate_content.call_args
        config = kwargs["config"]
        assert config.speech_config.voice_config.prebuilt_voice_config.voice_name == "Aoede"

    def test_gerar_fala_gemini_voz_personalizada(self):
        mock_client = MagicMock()
        mock_response = MagicMock()

        mock_part = MagicMock()
        mock_part.inline_data.data = b"RIFFfake"
        mock_part.inline_data.mime_type = "audio/wav"

        mock_candidate = MagicMock()
        mock_candidate.content.parts = [mock_part]
        mock_response.candidates = [mock_candidate]
        mock_client.models.generate_content.return_value = mock_response

        gerar_fala_gemini(
            texto="Texto com voz Charon",
            voz="Charon",
            client=mock_client,
        )

        _, kwargs = mock_client.models.generate_content.call_args
        config = kwargs["config"]
        assert config.speech_config.voice_config.prebuilt_voice_config.voice_name == "Charon"

    def test_gerar_fala_gemini_nao_reencapsula_se_ja_wav(self):
        mock_client = MagicMock()
        mock_response = MagicMock()

        fake_wav = b"RIFF\x24\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00"
        mock_part = MagicMock()
        mock_part.inline_data.data = fake_wav
        mock_part.inline_data.mime_type = "audio/pcm"  # MIME incorreto, mas payload já é WAV

        mock_candidate = MagicMock()
        mock_candidate.content.parts = [mock_part]
        mock_response.candidates = [mock_candidate]
        mock_client.models.generate_content.return_value = mock_response

        buffer = gerar_fala_gemini("Texto teste", client=mock_client)
        # Não deve haver header RIFF aninhado duplicado
        assert buffer.getvalue().count(b"RIFF") == 1

    @patch("src.core.audio._gerar_fala_gtts")
    def test_gerar_fala_gemini_fallback_quando_api_falha(self, mock_fallback):
        mock_client = MagicMock()
        mock_client.models.generate_content.side_effect = Exception("400 Multi-modal output not supported")

        mock_buffer_fallback = io.BytesIO(b"mp3-fallback-gtts")
        mock_fallback.return_value = mock_buffer_fallback

        resultado = gerar_fala_gemini("Texto com falha no Gemini", client=mock_client)

        assert resultado == mock_buffer_fallback
        mock_fallback.assert_called_once()

    @patch("src.core.audio.configurar_api_gemini", return_value=None)
    @patch("src.core.audio._gerar_fala_gtts")
    def test_gerar_fala_gemini_fallback_quando_sem_cliente(self, mock_fallback, _mock_cfg):
        mock_buffer_fallback = io.BytesIO(b"mp3-fallback-sem-cliente")
        mock_fallback.return_value = mock_buffer_fallback

        resultado = gerar_fala_gemini("Texto sem cliente")

        assert resultado == mock_buffer_fallback
        mock_fallback.assert_called_once()

    @patch("src.core.audio._gerar_fala_gtts")
    def test_gerar_fala_gemini_fallback_quando_sem_partes_de_audio(self, mock_fallback):
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_candidate = MagicMock()
        mock_candidate.content.parts = []  # Nenhuma parte retornada
        mock_response.candidates = [mock_candidate]
        mock_client.models.generate_content.return_value = mock_response

        mock_buffer = io.BytesIO(b"fallback-dados")
        mock_fallback.return_value = mock_buffer

        resultado = gerar_fala_gemini("Texto sem partes", client=mock_client)
        assert resultado == mock_buffer
        mock_fallback.assert_called_once()

    @patch("src.core.audio.gTTS")
    def test_gerar_fala_gtts_executa_corretamente(self, mock_gtts_cls):
        mock_tts = MagicMock()

        def fake_write_to_fp(fp):
            fp.write(b"bytes-mp3-gtts")

        mock_tts.write_to_fp.side_effect = fake_write_to_fp
        mock_gtts_cls.return_value = mock_tts

        buffer = gerar_fala_gemini("Texto para síntese gTTS", client=None)
        assert isinstance(buffer, io.BytesIO)
        assert buffer.getvalue() == b"bytes-mp3-gtts"
        mock_gtts_cls.assert_called_once_with(text="Texto para síntese gTTS", lang="pt-br")

    @patch("src.core.audio.gTTS", side_effect=Exception("Falha total na conexão de rede"))
    def test_gerar_fala_resiliencia_falha_total(self, _mock_gtts):
        # Quando Gemini é nulo e gTTS também falha
        buffer = gerar_fala_gemini("Texto sob falha extrema", client=None)
        assert isinstance(buffer, io.BytesIO)
        assert buffer.getvalue() == b""

    def test_facade_utils_texto_para_audio(self):
        from src.utils import texto_para_audio

        with patch("src.core.audio.gerar_fala_gemini") as mock_gerar:
            mock_buffer = io.BytesIO(b"audio-via-utils")
            mock_gerar.return_value = mock_buffer

            resultado = texto_para_audio("Frase de teste para o Vox AI")
            assert resultado == mock_buffer
            mock_gerar.assert_called_once_with("Frase de teste para o Vox AI")

    def test_gerar_fala_gemini_audio_base64_decodificacao(self):
        import base64

        mock_client = MagicMock()
        mock_response = MagicMock()

        wav_bytes = b"RIFF" + b"\x00" * 36 + b"WAVE"
        b64_audio = base64.b64encode(wav_bytes).decode("utf-8")

        mock_part = MagicMock()
        mock_part.inline_data.data = b64_audio
        mock_part.inline_data.mime_type = "audio/wav"

        mock_candidate = MagicMock()
        mock_candidate.content.parts = [mock_part]
        mock_response.candidates = [mock_candidate]
        mock_client.models.generate_content.return_value = mock_response

        buffer = gerar_fala_gemini("Texto com áudio codificado em base64", client=mock_client)
        assert isinstance(buffer, io.BytesIO)
        assert buffer.getvalue() == wav_bytes

    def test_gerar_fala_gemini_pcm_custom_sample_rate(self):
        mock_client = MagicMock()
        mock_response = MagicMock()

        pcm_raw = b"\x00\x02" * 100
        mock_part = MagicMock()
        mock_part.inline_data.data = pcm_raw
        mock_part.inline_data.mime_type = "audio/pcm;rate=16000;bits=16"

        mock_candidate = MagicMock()
        mock_candidate.content.parts = [mock_part]
        mock_response.candidates = [mock_candidate]
        mock_client.models.generate_content.return_value = mock_response

        buffer = gerar_fala_gemini("Teste PCM com taxa customizada", client=mock_client)
        assert isinstance(buffer, io.BytesIO)
        assert buffer.getvalue().startswith(b"RIFF")

    def test_gerar_fala_gemini_override_modelo(self):
        mock_client = MagicMock()
        mock_response = MagicMock()

        mock_part = MagicMock()
        mock_part.inline_data.data = b"RIFFfake"
        mock_part.inline_data.mime_type = "audio/wav"
        mock_candidate = MagicMock()
        mock_candidate.content.parts = [mock_part]
        mock_response.candidates = [mock_candidate]
        mock_client.models.generate_content.return_value = mock_response

        gerar_fala_gemini("Texto teste", client=mock_client, model="gemini-2.5-flash-tts-custom")
        _, kwargs = mock_client.models.generate_content.call_args
        assert kwargs["model"] == "gemini-2.5-flash-tts-custom"

    def test_transcrever_audio_gemini_read_exception(self):
        mock_client = MagicMock()
        mock_file = MagicMock()
        mock_file.read.side_effect = IOError("Erro de leitura de disco ou buffer corrompido")

        resultado = transcrever_audio_gemini(mock_file, client=mock_client)
        assert resultado is None

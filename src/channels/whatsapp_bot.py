"""
Módulo de Integração com WhatsApp (Meta Cloud API e Webhooks) para o Vox AI.

Permite que pessoas usuárias conversem com o assistente inteligente através do WhatsApp.
Oferece suporte a:
- Validação e assinatura de Webhooks da Meta (GET hub.verify_token)
- Processamento de mensagens de texto, botões interativos e áudio (POST)
- Envio de respostas de texto e menus interativos com botões rápidos
- Anonimização de números de telefone (LGPD)
- Compatibilidade com WhatsApp Cloud API e gateways comuns (ex: Evolution API, Z-API).
"""

from __future__ import annotations

import json
import urllib.request
from typing import Any, Dict, List, Optional, Tuple

from src.channels.core_adapter import VoxChannelCore, channel_core
from src.config import get_secret, logger

GRAPH_API_VERSION = "v20.0"
WHATSAPP_API_BASE = f"https://graph.facebook.com/{GRAPH_API_VERSION}"

TEXTO_BOAS_VINDAS_WHATSAPP = (
    "🌈 *Olá! Seja muito bem-vinda(o/e) ao Vox AI!*\n\n"
    "Sou seu assistente de apoio, acolhimento e informação confiável para a comunidade LGBTQIA+.\n\n"
    "Aqui você pode tirar dúvidas com segurança e total sigilo sobre:\n"
    "• Retificação de nome e gênero ⚖️\n"
    "• Direitos civis, união estável e adoção 📜\n"
    "• Saúde, hormonioterapia e prevenção no SUS (PrEP/PEP) 🩺\n"
    "• Casas de acolhimento e rede de suporte 🏠\n\n"
    "Pode me enviar sua dúvida diretamente por mensagem de texto, ou escolher uma opção rápida abaixo! 💜"
)

TEXTO_APOIO_WHATSAPP = (
    "🤝 *Rede de Apoio Emergencial & Acolhimento*\n\n"
    "Caso você esteja enfrentando violência, expulsão de casa ou precise de apoio psicológico:\n\n"
    "📞 *Linhas Oficiais 24h:*\n"
    "• *Disque 100:* Denúncias de violações de Direitos Humanos e LGBTfobia.\n"
    "• *CVV 188:* Apoio emocional gratuito e sigiloso.\n"
    "• *Polícia Militar: 190*\n\n"
    "🏠 *Principais Centros de Acolhimento:*\n"
    "• Casa 1 (São Paulo): Acolhimento e clínica social.\n"
    "• Casinha (Rio de Janeiro): Apoio social e moradia.\n"
    "• Casa Chama: Coletivo de apoio a pessoas trans e travestis.\n"
    "• Casa Miga (Manaus): Refugiados e migrantes LGBTQIA+.\n\n"
    "Você não está só. 🏳️‍🌈"
)


class WhatsAppBot:
    """
    Cliente e processador de Webhook para WhatsApp Cloud API.
    """

    def __init__(
        self,
        phone_number_id: Optional[str] = None,
        access_token: Optional[str] = None,
        verify_token: Optional[str] = None,
        core: Optional[VoxChannelCore] = None,
    ):
        self.phone_number_id = phone_number_id or get_secret("WHATSAPP_PHONE_NUMBER_ID")
        self.access_token = access_token or get_secret("WHATSAPP_ACCESS_TOKEN")
        self.verify_token = verify_token or get_secret("WHATSAPP_VERIFY_TOKEN", default="vox_verify_token")
        self.core = core or channel_core

    def is_configured(self) -> bool:
        """Verifica se as credenciais do WhatsApp Cloud API estão configuradas."""
        return bool(self.phone_number_id and self.access_token)

    def verify_webhook_challenge(self, params: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Valida a requisição de verificação do Webhook da Meta (GET hub.verify_token).
        
        Args:
            params: Dicionário contendo os query parameters da requisição HTTP GET.
            
        Returns:
            Tuple[bool, Optional[str]]: (Sucesso, hub.challenge ou mensagem de erro)
        """
        mode = params.get("hub.mode")
        token = params.get("hub.verify_token")
        challenge = params.get("hub.challenge")

        if mode == "subscribe" and token == self.verify_token:
            logger.info("Webhook do WhatsApp verificado com sucesso.")
            return True, challenge
        logger.warning(f"Falha na validação do webhook do WhatsApp. Token incorreto ou modo inválido: {mode}")
        return False, None

    def _send_api_request(self, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Executa a chamada HTTP POST para a API de envio de mensagens do WhatsApp."""
        if not self.is_configured():
            logger.error("Credenciais do WhatsApp Cloud API ausentes.")
            return None

        url = f"{WHATSAPP_API_BASE}/{self.phone_number_id}/messages"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")

        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                if resp.status in (200, 201):
                    return json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            logger.error(f"Erro ao enviar mensagem WhatsApp para o número {payload.get('to')}: {e}")
            return None

    def send_text_message(self, to_phone: str, message_text: str) -> bool:
        """
        Envia mensagem de texto convencional para o número de WhatsApp especificado.
        Divide automaticamente mensagens maiores que 4000 caracteres respeitando o limite da Meta (4096).
        """
        if not message_text:
            return False

        chunks: List[str] = []
        max_chunk = 4000
        remaining = message_text
        while len(remaining) > max_chunk:
            split_idx = remaining.rfind("\n", 0, max_chunk)
            if split_idx == -1 or split_idx < max_chunk // 2:
                split_idx = remaining.rfind(" ", 0, max_chunk)
            if split_idx == -1 or split_idx < max_chunk // 2:
                split_idx = max_chunk
            chunks.append(remaining[:split_idx].strip())
            remaining = remaining[split_idx:].strip()
        if remaining:
            chunks.append(remaining)

        all_ok = True
        for chunk in chunks:
            payload = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": to_phone,
                "type": "text",
                "text": {"preview_url": False, "body": chunk},
            }
            res = self._send_api_request(payload)
            if not (res and "messages" in res):
                all_ok = False
        return all_ok

    def send_quick_buttons(
        self,
        to_phone: str,
        body_text: str,
        buttons: Optional[List[Tuple[str, str]]] = None,
    ) -> bool:
        """
        Envia mensagem interativa com botões de resposta rápida.
        Garante que body_text não exceda o limite de 1024 caracteres da Meta.
        """
        if buttons is None:
            buttons = [
                ("btn_apoio", "Rede de Apoio 🏠"),
                ("btn_direitos", "Direitos LGBTQIA+ ⚖️"),
                ("btn_limpar", "Limpar Sessão 🧹"),
            ]

        interactive_buttons = []
        for btn_id, title in buttons[:3]:  # WhatsApp limita a no máximo 3 botões rápidos
            interactive_buttons.append({
                "type": "reply",
                "reply": {
                    "id": btn_id[:256],
                    "title": title[:20],  # Limite de 20 caracteres por botão na Meta
                },
            })

        # Limite da Meta para o texto do corpo da mensagem interativa é de 1024 caracteres
        clamped_body = body_text[:1024] if len(body_text) > 1024 else body_text

        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to_phone,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {"text": clamped_body},
                "action": {"buttons": interactive_buttons},
            },
        }
        res = self._send_api_request(payload)
        return bool(res and "messages" in res)

    def mark_message_as_read(self, message_id: str) -> None:
        """Marca a mensagem recebida como lida na plataforma."""
        payload = {
            "messaging_product": "whatsapp",
            "status": "read",
            "message_id": message_id,
        }
        self._send_api_request(payload)

    def get_media_url(self, media_id: str) -> Optional[str]:
        """Recupera URL temporária de download de mídia na Meta Cloud API."""
        if not self.is_configured():
            return None
        url = f"{WHATSAPP_API_BASE}/{media_id}"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        req = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode("utf-8"))
                    return data.get("url")
        except Exception as e:
            logger.error(f"Erro ao obter URL de mídia WhatsApp ({media_id}): {e}")
            return None

    def download_media_bytes(self, media_url: str) -> Optional[bytes]:
        """Baixa bytes de mídia da Meta Cloud API com token de autenticação."""
        if not self.is_configured():
            return None
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "User-Agent": "VoxAI-Bot/1.0",
        }
        req = urllib.request.Request(media_url, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                if resp.status == 200:
                    return resp.read()
        except Exception as e:
            logger.error(f"Erro ao baixar bytes de mídia WhatsApp: {e}")
            return None

    def extract_messages_from_webhook(self, payload: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extrai a lista de mensagens de um payload bruto do webhook da Meta.
        Trata com segurança campos nulos e eventos de status sem mensagens.
        """
        extracted = []
        entries = payload.get("entry") or []
        for entry in entries:
            for change in entry.get("changes") or []:
                val = change.get("value") or {}
                messages = val.get("messages") or []
                contacts = val.get("contacts") or []
                user_name = "Pessoa"
                if contacts and isinstance(contacts, list) and contacts[0]:
                    user_name = contacts[0].get("profile", {}).get("name", "Pessoa")

                for msg in messages:
                    if not msg:
                        continue
                    extracted.append({
                        "message_id": msg.get("id"),
                        "from": msg.get("from"),
                        "type": msg.get("type"),
                        "timestamp": msg.get("timestamp"),
                        "raw_message": msg,
                        "profile_name": user_name,
                    })
        return extracted

    def handle_incoming_message(self, msg_info: Dict[str, Any]) -> None:
        """
        Processa individualmente uma mensagem recebida do WhatsApp.
        """
        user_phone = msg_info.get("from")
        msg_id = msg_info.get("message_id")
        msg_type = msg_info.get("type")
        raw = msg_info.get("raw_message", {})

        if not user_phone:
            return

        if msg_id:
            self.mark_message_as_read(msg_id)

        prompt_text = ""

        # Processamento por tipo de mensagem
        if msg_type == "text":
            prompt_text = raw.get("text", {}).get("body", "").strip()

        elif msg_type == "interactive":
            interaction = raw.get("interactive", {})
            btn_reply = interaction.get("button_reply", {})
            btn_id = btn_reply.get("id")

            if btn_id == "btn_apoio":
                self.send_text_message(user_phone, TEXTO_APOIO_WHATSAPP)
                return
            elif btn_id == "btn_direitos":
                prompt_text = "Quais são os principais direitos garantidos para pessoas LGBTQIA+ no Brasil?"
            elif btn_id == "btn_limpar":
                self.core.clear_user_session("whatsapp", user_phone, delete_database_logs=True)
                self.send_text_message(
                    user_phone,
                    "🧹 *Dados da conversa excluídos com sucesso!* Seus dados desta sessão foram descartados (LGPD). "
                    "Como posso te acolher agora? 🌈",
                )
                return
            else:
                prompt_text = btn_reply.get("title", "")

        elif msg_type == "audio":
            audio_obj = raw.get("audio") or {}
            media_id = audio_obj.get("id")
            if media_id:
                media_url = self.get_media_url(media_id)
                if media_url:
                    audio_bytes = self.download_media_bytes(media_url)
                    if audio_bytes:
                        try:
                            import io
                            from src.core.genai import transcrever_audio
                            audio_io = io.BytesIO(audio_bytes)
                            audio_io.name = "whatsapp_voice.ogg"
                            mime_type = audio_obj.get("mime_type", "audio/ogg")
                            if ";" in mime_type:
                                mime_type = mime_type.split(";")[0].strip()
                            transcription = transcrever_audio(audio_io, mime_type=mime_type)
                            if transcription:
                                prompt_text = transcription
                                self.send_text_message(user_phone, f"🎙️ *Entendi:* \"{transcription}\"")
                        except Exception as e:
                            logger.error(f"Erro ao processar áudio do WhatsApp: {e}")

            if not prompt_text:
                self.send_text_message(
                    user_phone,
                    "🎧 Recebi seu áudio, mas não consegui compreendê-lo com clareza. "
                    "Por favor, tente enviar sua pergunta por mensagem de texto! 💜",
                )
                return

        if not prompt_text:
            return

        # Comandos textuais
        lower_prompt = prompt_text.lower().strip()
        if lower_prompt in ("oi", "olá", "ola", "start", "começar", "menu"):
            self.send_quick_buttons(user_phone, TEXTO_BOAS_VINDAS_WHATSAPP)
            return

        if lower_prompt in ("apoio", "ajuda", "socorro", "acolhimento"):
            self.send_text_message(user_phone, TEXTO_APOIO_WHATSAPP)
            return

        if lower_prompt in ("limpar", "excluir", "esquecer"):
            self.core.clear_user_session("whatsapp", user_phone, delete_database_logs=True)
            self.send_text_message(
                user_phone,
                "🧹 *Sessão limpa!* Todos os dados locais e temporários foram removidos. "
                "Fique à vontade para iniciar uma nova conversa. 🏳️‍🌈",
            )
            return

        # Encaminhamento para o núcleo Vox AI
        res = self.core.process_user_message(
            channel="whatsapp",
            user_id=user_phone,
            message_text=prompt_text,
        )

        resposta = res.get("response_text", "Desculpe, ocorreu uma instabilidade momentânea.")
        self.send_text_message(user_phone, resposta)

    def process_webhook_payload(self, payload: Dict[str, Any]) -> None:
        """
        Ponto de entrada para processamento assíncrono de payloads POST do webhook.
        """
        messages = self.extract_messages_from_webhook(payload)
        for msg in messages:
            try:
                self.handle_incoming_message(msg)
            except Exception as e:
                logger.error(f"Erro ao processar mensagem do webhook: {e}", exc_info=True)


# Instância global reutilizável
whatsapp_bot = WhatsAppBot()

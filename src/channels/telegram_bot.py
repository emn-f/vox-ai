"""
Módulo de Integração com o Telegram para o Vox AI.

Permite a interação conversacional com o assistente inteligente através de um bot oficial no Telegram.
Oferece suporte a:
- Modo Long-Polling (para execução local ou containers)
- Modo Webhook (para APIs serverless ou endpoints HTTP)
- Comandos integrados (/start, /ajuda, /apoio, /limpar)
- Transcrição de mensagens de voz
- Anonimização de usuários (LGPD) e divisão automática de mensagens longas (>4096 caracteres).
"""

from __future__ import annotations

import io
import json
import time
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional

from src.channels.core_adapter import VoxChannelCore, channel_core
from src.config import get_secret, logger


TELEGRAM_API_BASE = "https://api.telegram.org/bot"

# Textos Padrão do Bot
MENSAGEM_BOAS_VINDAS = (
    "🌈 **Olá! Eu sou o Vox AI**, seu assistente de apoio, acolhimento e informação para a comunidade LGBTQIA+.\n\n"
    "Estou aqui para tirar dúvidas sobre:\n"
    "• Direitos e retificação de nome/gênero ⚖️\n"
    "• Saúde preventiva e acesso ao SUS (PrEP, PEP, hormonioterapia) 🩺\n"
    "• Rede de apoio, casas de acolhimento e coletivos parceiros 🏠\n"
    "• Escuta empática e suporte informativo 💜\n\n"
    "**Comandos Rápidos:**\n"
    "/apoio - Lista de contatos de emergência e casas de acolhimento\n"
    "/ajuda - Informações sobre o projeto e diretrizes de privacidade\n"
    "/limpar - Apaga o histórico da nossa conversa desta sessão (LGPD)\n\n"
    "Como posso te acolher ou apoiar hoje?"
)

MENSAGEM_AJUDA = (
    "✨ **Sobre o Vox AI no Telegram**\n\n"
    "O Vox AI é um projeto de código aberto sem fins lucrativos, criado para democratizar "
    "informações seguras, embasadas e livres de preconceito para a comunidade LGBTQIA+.\n\n"
    "🛡️ **Sua Privacidade:**\n"
    "Seu número e identificador do Telegram não são expostos nem comercializados. "
    "Usamos identificadores pseudo-anonimizados para proteger sua privacidade conforme a LGPD.\n\n"
    "🚨 **Emergências e Risco Imediato:**\n"
    "O Vox é uma IA de suporte informativo e **não substitui** serviços emergenciais humanos.\n"
    "• Violação de Direitos Humanos: **Disque 100**\n"
    "• Apoio Emocional e Prevenção ao Suicídio: **CVV 188** (Ligação Gratuita)\n"
    "• Emergência Policial: **190**"
)

MENSAGEM_APOIO = (
    "🤝 **Rede de Apoio e Acolhimento Emergencial**\n\n"
    "Se você precisa de abrigo, suporte psicológico ou auxílio jurídico imediato:\n\n"
    "🏠 **Casas de Acolhimento Parceiras:**\n"
    "• **Casa 1 (São Paulo/SP):** Acolhimento para jovens expulsos de casa e clínica social.\n"
    "• **Casinha Acolhimento (Rio de Janeiro/RJ):** Apoio integral a pessoas LGBTQIA+ em situação de rua.\n"
    "• **Casa Chama (SP):** Apoio a pessoas trans e travestis (saúde, jurídico e cultura).\n"
    "• **Casa Miga (Manaus/AM):** Acolhimento a refugiados e migrantes LGBTQIA+.\n\n"
    "📞 **Linhas Nacionais 24h:**\n"
    "• **Disque 100:** Direitos Humanos e denúncias de LGBTfobia.\n"
    "• **CVV 188:** Apoio emocional confidencial e gratuito.\n\n"
    "Você não está só. 🏳️‍🌈"
)


class TelegramBot:
    """
    Cliente para integração com a API de Bots do Telegram.
    """

    def __init__(
        self,
        token: Optional[str] = None,
        core: Optional[VoxChannelCore] = None,
    ):
        self.token = token or get_secret("TELEGRAM_BOT_TOKEN")
        self.core = core or channel_core
        self.api_url = f"{TELEGRAM_API_BASE}{self.token}" if self.token else ""

    def is_configured(self) -> bool:
        """Verifica se o token do Telegram foi informado."""
        return bool(self.token)

    def _make_request(
        self,
        method: str,
        payload: Optional[Dict[str, Any]] = None,
        timeout: int = 30,
    ) -> Optional[Dict[str, Any]]:
        """Executa uma requisição HTTP para a API do Telegram."""
        if not self.is_configured():
            logger.error("Token do bot Telegram não configurado.")
            return None

        url = f"{self.api_url}/{method}"
        data = None
        headers = {"Content-Type": "application/json"}

        if payload is not None:
            data = json.dumps(payload).encode("utf-8")

        req = urllib.request.Request(url, data=data, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=timeout) as response:
                if response.status == 200:
                    return json.loads(response.read().decode("utf-8"))
        except Exception as e:
            logger.error(f"Erro na chamada à API do Telegram ({method}): {e}")
            return None

    def send_message(
        self,
        chat_id: int | str,
        text: str,
        parse_mode: str = "Markdown",
        reply_markup: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Envia mensagem de texto para o chat do Telegram.
        Divide automaticamente mensagens maiores que 4000 caracteres.
        """
        if not text:
            return False

        # Dividir em blocos de até 4000 caracteres respeitando o limite do Telegram (4096)
        chunks: List[str] = []
        max_chunk = 4000
        remaining = text
        while len(remaining) > max_chunk:
            # Tenta quebrar em uma linha próxima
            split_idx = remaining.rfind("\n", 0, max_chunk)
            if split_idx == -1 or split_idx < max_chunk // 2:
                split_idx = max_chunk
            chunks.append(remaining[:split_idx].strip())
            remaining = remaining[split_idx:].strip()
        if remaining:
            chunks.append(remaining)

        success = True
        for chunk in chunks:
            payload: Dict[str, Any] = {
                "chat_id": chat_id,
                "text": chunk,
            }
            if parse_mode:
                payload["parse_mode"] = parse_mode
            if reply_markup:
                payload["reply_markup"] = reply_markup

            res = self._make_request("sendMessage", payload)
            if not res or not res.get("ok"):
                # Se falhar por erro de parsing do Markdown, tenta reenviar em texto puro
                payload.pop("parse_mode", None)
                res_retry = self._make_request("sendMessage", payload)
                if not res_retry or not res_retry.get("ok"):
                    success = False

        return success

    def send_chat_action(self, chat_id: int | str, action: str = "typing") -> None:
        """Envia status de 'digitando' para o Telegram."""
        self._make_request("sendChatAction", {"chat_id": chat_id, "action": action}, timeout=5)

    def get_file(self, file_id: str) -> Optional[Dict[str, Any]]:
        """Recupera metadados de arquivo armazenado no Telegram."""
        res = self._make_request("getFile", {"file_id": file_id})
        if res and res.get("ok"):
            return res.get("result")
        return None

    def download_file_bytes(self, file_path: str) -> Optional[bytes]:
        """Faz o download de um arquivo da CDN do Telegram."""
        if not self.is_configured():
            return None
        download_url = f"https://api.telegram.org/file/bot{self.token}/{file_path}"
        try:
            with urllib.request.urlopen(download_url, timeout=60) as resp:
                return resp.read()
        except Exception as e:
            logger.error(f"Erro ao baixar arquivo do Telegram: {e}")
            return None

    def handle_voice_message(self, chat_id: int | str, voice_obj: Dict[str, Any]) -> str:
        """Processa e transcreve mensagem de áudio enviada no Telegram."""
        file_id = voice_obj.get("file_id")
        if not file_id:
            return "Não foi possível obter os dados do áudio enviado."

        self.send_chat_action(chat_id, "record_voice")
        file_meta = self.get_file(file_id)
        if not file_meta or "file_path" not in file_meta:
            return "Erro ao obter o caminho do áudio no Telegram."

        audio_bytes = self.download_file_bytes(file_meta["file_path"])
        if not audio_bytes:
            return "Erro ao realizar o download do áudio."

        try:
            from src.core.genai import transcrever_audio

            # Prepara buffer de áudio
            audio_io = io.BytesIO(audio_bytes)
            audio_io.name = "telegram_voice.ogg"
            transcription = transcrever_audio(audio_io, mime_type="audio/ogg")
            if transcription:
                return transcription
            return "Não consegui entender com clareza o áudio gravado. Poderia enviar por texto?"
        except Exception as e:
            logger.error(f"Erro ao transcrever áudio do Telegram: {e}")
            return "Ocorreu uma falha temporária ao transcrever seu áudio."

    def process_update(self, update: Dict[str, Any]) -> None:
        """
        Processa um evento (Update) individual recebido do Telegram.
        """
        message = update.get("message") or update.get("edited_message")
        if not message:
            return

        chat = message.get("chat", {})
        chat_id = chat.get("id")
        user = message.get("from", {})
        user_id = str(user.get("id", chat_id))

        if not chat_id:
            return

        raw_text = (message.get("text") or "").strip()
        voice = message.get("voice") or message.get("audio")

        # 1. Tratamento de Comandos Específicos
        cmd = ""
        if raw_text.startswith("/"):
            first_token = raw_text.split()[0].lower()
            cmd = first_token.split("@")[0]

        if cmd == "/start":
            self.send_message(chat_id, MENSAGEM_BOAS_VINDAS)
            return

        if cmd in ("/ajuda", "/help"):
            self.send_message(chat_id, MENSAGEM_AJUDA)
            return

        if cmd in ("/apoio", "/suporte"):
            self.send_message(chat_id, MENSAGEM_APOIO)
            return

        if cmd in ("/limpar", "/clear"):
            sucesso = self.core.clear_user_session("telegram", user_id, delete_database_logs=True)
            if sucesso:
                self.send_message(
                    chat_id,
                    "🧹 **Histórico limpo com sucesso!** Seus dados desta sessão foram descartados. "
                    "Como posso te ajudar agora? 🏳️‍🌈",
                )
            else:
                self.send_message(chat_id, "🧹 Histórico local limpo com sucesso.")
            return

        text = raw_text

        # 2. Se for áudio, transcrever primeiro
        if voice:
            self.send_message(chat_id, "🎧 *Ouvindo seu áudio...*")
            transcrito = self.handle_voice_message(chat_id, voice)
            if not transcrito or transcrito.startswith("Não consegui") or transcrito.startswith("Erro"):
                self.send_message(chat_id, transcrito)
                return
            text = transcrito
            self.send_message(chat_id, f"🎙️ *Entendi:* \"{text}\"")

        if not text:
            return

        # 3. Notificar usuário que estamos processando
        self.send_chat_action(chat_id, "typing")

        # 4. Encaminhar para o Core do Vox AI
        res = self.core.process_user_message(
            channel="telegram",
            user_id=user_id,
            message_text=text,
        )

        # 5. Responder com o resultado
        resposta_final = res.get("response_text", "Desculpe, não consegui gerar uma resposta.")
        self.send_message(chat_id, resposta_final)

    def run_polling(self, poll_interval: float = 1.0) -> None:
        """
        Executa o loop de polling contínuo para ouvir novas mensagens do Telegram.
        """
        if not self.is_configured():
            logger.error("TELEGRAM_BOT_TOKEN não definido. Abortando polling.")
            return

        logger.info("🤖 Iniciando polling do Vox AI Telegram Bot...")
        offset = 0

        while True:
            try:
                updates_res = self._make_request(
                    "getUpdates",
                    {"offset": offset, "timeout": 20, "allowed_updates": ["message"]},
                    timeout=30,
                )
                if updates_res and updates_res.get("ok"):
                    results = updates_res.get("result", [])
                    for update in results:
                        update_id = update.get("update_id", 0)
                        offset = max(offset, update_id + 1)
                        self.process_update(update)

                time.sleep(poll_interval)
            except KeyboardInterrupt:
                logger.info("Bot encerrado pelo usuário.")
                break
            except Exception as e:
                logger.error(f"Erro no loop de polling do Telegram: {e}")
                time.sleep(5)


if __name__ == "__main__":
    bot = TelegramBot()
    if bot.is_configured():
        bot.run_polling()
    else:
        print("TELEGRAM_BOT_TOKEN não configurado. Defina a variável de ambiente.")

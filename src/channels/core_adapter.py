"""
Adaptador de Integração de Canais do Vox AI.

Centraliza a comunicação entre canais externos (como Telegram, WhatsApp, Discord, etc.)
e o núcleo de inteligência do Vox AI (RAG Semântico, Gemini LLM, persistência e auditoria LGPD).
"""

from __future__ import annotations

import hashlib
import uuid
from typing import Any, Dict, Optional

from src.config import logger
from src.core.database import (
    excluir_dados_sessao,
    salvar_erro,
    salvar_log_chat,
    salvar_sessao,
)
from src.core.genai import gerar_resposta, inicializar_chat_modelo
from src.core.semantica import semantica
from src.utils import git_version


class VoxChannelCore:
    """
    Controlador centralizado para processar mensagens recebidas de diferentes canais.
    
    Garante:
    - Anonimização dos identificadores de usuários conforme LGPD (Art. 6 e Art. 11).
    - Manutenção de histórico de sessão em memória por canal/usuário.
    - Consulta RAG à base de conhecimento (semântica).
    - Chamada ao modelo Gemini.
    - Gravação de logs de auditoria e tratamento de falhas.
    """

    def __init__(self, salt: str = "vox_lgbtqia_secure_salt"):
        self.salt = salt
        # Mapeamento de chave de canal para chat session do modelo Gemini
        self._user_chats: Dict[str, Any] = {}
        # Mapeamento de chave de canal para ID anônimo de sessão persistido
        self._user_sessions: Dict[str, str] = {}

    def get_anonymous_session_id(self, channel: str, user_id: str) -> str:
        """
        Gera um identificador de sessão pseudo-anônimo determinístico via SHA-256
        para evitar armazenamento de dados sensíveis diretamente vinculados ao telefone ou ID de usuário.
        """
        raw = f"{channel}:{user_id}:{self.salt}"
        hashed = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]
        return f"{channel[:3]}_{hashed}"

    def get_or_create_chat(self, channel_key: str) -> Any:
        """
        Recupera ou inicializa a instância do chat conversacional do Gemini para um usuário específico.
        """
        if channel_key not in self._user_chats:
            try:
                self._user_chats[channel_key] = inicializar_chat_modelo()
            except Exception as e:
                logger.error(f"Erro ao inicializar modelo de chat para canal {channel_key}: {e}")
                raise
        return self._user_chats[channel_key]

    def get_or_create_session(self, channel: str, user_id: str) -> str:
        """
        Recupera ou registra a sessão do usuário no banco de dados.
        """
        channel_key = f"{channel}:{user_id}"
        if channel_key not in self._user_sessions:
            sess_id = self.get_anonymous_session_id(channel, user_id)
            self._user_sessions[channel_key] = sess_id
            try:
                salvar_sessao(sess_id)
            except Exception as e:
                logger.warning(f"Aviso ao registrar sessão no Supabase para {sess_id}: {e}")
        return self._user_sessions[channel_key]

    def clear_user_session(self, channel: str, user_id: str, delete_database_logs: bool = False) -> bool:
        """
        Limpa a memória da conversa do usuário e, opcionalmente, exclui os dados no Supabase (LGPD).
        """
        channel_key = f"{channel}:{user_id}"
        sess_id = self._user_sessions.pop(channel_key, None)
        self._user_chats.pop(channel_key, None)

        if delete_database_logs and sess_id:
            try:
                return excluir_dados_sessao(sess_id)
            except Exception as e:
                logger.error(f"Erro ao excluir dados de sessão ({sess_id}): {e}")
                return False
        return True

    def process_user_message(
        self,
        channel: str,
        user_id: str,
        message_text: str,
    ) -> Dict[str, Any]:
        """
        Processa uma mensagem do usuário através do pipeline completo do Vox AI:
        1. Resolução de Sessão
        2. Busca Semântica (RAG)
        3. Inferência LLM (Gemini)
        4. Log e Auditoria
        """
        cleaned_text = (message_text or "").strip()
        if not cleaned_text:
            return {
                "success": False,
                "response_text": "Mensagem vazia recebida. Como posso te apoiar hoje? 🌈",
                "session_id": "",
                "reference_ids": [],
            }

        channel_key = f"{channel}:{user_id}"
        session_id = self.get_or_create_session(channel, user_id)
        ver = git_version() or "prod"

        try:
            # 1. Recuperação Semântica (RAG)
            tema_match = None
            descricao_match = None
            ids_referencia = []
            try:
                tema_match, descricao_match, ids_referencia = semantica(cleaned_text)
            except Exception as e_sem:
                logger.warning(f"Falha na busca semântica para canal {channel}: {e_sem}")

            info_adicional_contexto = descricao_match if tema_match else ""

            # 2. Inicialização / Reutilização de Chat
            chat = self.get_or_create_chat(channel_key)

            # 3. Geração de Resposta via LLM
            resposta = gerar_resposta(chat, cleaned_text, info_adicional_contexto)

            if not resposta:
                resposta = (
                    "Estou aqui com você, mas tive uma pequena dificuldade técnica temporária "
                    "para formular a resposta. Pode tentar perguntar de novo? 💜"
                )

            # 4. Registro no Banco de Dados
            try:
                salvar_log_chat(
                    session_id,
                    ver,
                    cleaned_text,
                    str(resposta),
                    ids_referencia or [],
                )
            except Exception as e_log:
                logger.error(f"Falha ao salvar log de chat do canal {channel}: {e_log}")

            return {
                "success": True,
                "response_text": resposta,
                "matched_topic": tema_match,
                "reference_ids": ids_referencia or [],
                "session_id": session_id,
            }

        except Exception as e:
            logger.error(f"Erro ao processar mensagem do canal {channel}: {e}", exc_info=True)
            try:
                error_id = salvar_erro(session_id, ver, e)
            except Exception:
                error_id = str(uuid.uuid4())[:8]

            friendly_error = (
                f"Olá! Tivemos um imprevisto técnico momentâneo ao processar sua solicitação.\n\n"
                f"Por favor, tente novamente em instantes. Caso persista, compartilhe o "
                f"código de diagnóstico com nossa equipe: **{error_id}** 🌈"
            )
            return {
                "success": False,
                "response_text": friendly_error,
                "error_id": error_id,
                "session_id": session_id,
                "reference_ids": [],
            }


# Instância global reutilizável
channel_core = VoxChannelCore()

"""
Camada de Serviço Central (Service Layer) do Vox AI.

Desacopla a lógica de negócio, orquestração de IA (GenAI/Gemini),
recuperação semântica (RAG via Supabase pgvector), síntese de áudio (gTTS)
e persistência de qualquer dependência direta do Streamlit.
"""

import base64
import uuid
from typing import Any, Dict, Generator, List, Optional

from src.api.models import (
    ChatMessage,
    ChatResponse,
    HealthResponse,
    RAGQueryResponse,
    ReferenceItem,
)
from src.config import logger
from src.core.database import (
    excluir_dados_sessao,
    get_categorias_erro,
    get_db_client,
    recuperar_contexto_inteligente,
    salvar_erro,
    salvar_log_chat,
    salvar_report,
    salvar_sessao,
)
from src.core.genai import (
    configurar_api_gemini,
    gerar_resposta,
    gerar_resposta_stream,
    inicializar_chat_modelo,
    transcrever_audio,
)
from src.core.semantica import semantica
from src.utils import git_version, texto_para_audio


class VoxService:
    """
    Serviço principal que gerencia o ciclo de vida das conversas,
    recuperação semântica e integração com modelos generativos.
    """

    def __init__(self):
        self._git_version = git_version()

    def ensure_session(self, session_id: Optional[str] = None) -> str:
        """
        Garante um ID de sessão válido e o registra no banco de dados.

        Args:
            session_id: ID existente (opcional). Se não fornecido, gera um UUID4.

        Returns:
            str: O session_id consolidado.
        """
        sess_id = session_id.strip() if session_id and session_id.strip() else str(uuid.uuid4())
        try:
            salvar_sessao(sess_id)
        except Exception as e:
            logger.warning(f"⚠️ Não foi possível salvar sessão no banco: {e}")
        return sess_id

    @staticmethod
    def _format_gemini_history(history: Optional[List[ChatMessage]]) -> Optional[List[Any]]:
        """Converte mensagens do modelo da API para tipos nativos do Google GenAI."""
        if not history:
            return None
        from google.genai import types
        formatted = []
        for msg in history:
            role = "model" if msg.role in ("model", "assistant") else "user"
            formatted.append(
                types.Content(
                    role=role,
                    parts=[types.Part.from_text(text=msg.content)],
                )
            )
        return formatted

    def chat(
        self,
        prompt: str,
        session_id: Optional[str] = None,
        include_audio: bool = False,
        history: Optional[List[ChatMessage]] = None,
    ) -> ChatResponse:
        """
        Processa uma mensagem do usuário de ponta a ponta:
        1. Assegura sessão
        2. Realiza RAG via busca semântica
        3. Invoca o modelo Gemini com as instruções da persona Vox
        4. Salva log da conversa
        5. Gera áudio TTS se solicitado

        Args:
            prompt: Pergunta ou mensagem do usuário.
            session_id: ID da sessão opcional.
            include_audio: Se True, anexa áudio base64 na resposta.
            history: Histórico opcional de turnos anteriores.

        Returns:
            ChatResponse: Objeto com resposta gerada, metadados de RAG e áudio opcional.
        """
        active_session_id = self.ensure_session(session_id)

        # 1. Recuperação Semântica (RAG)
        tema_match = None
        contexto_match = ""
        referencias_raw: Optional[List[Dict[str, Any]]] = None

        try:
            tema_match, contexto_match, referencias_raw = semantica(prompt)
            if not tema_match:
                contexto_match = ""
        except Exception as e_sem:
            logger.error(f"Erro ao executar busca semântica: {e_sem}", exc_info=True)

        # 2. Geração da resposta com a persona Vox
        try:
            gemini_history = self._format_gemini_history(history)
            chat_instance = inicializar_chat_modelo(history=gemini_history)
            resposta_texto = gerar_resposta(
                chat_instance,
                prompt,
                contexto_match or "",
            )
        except Exception as e_gen:
            err_id = salvar_erro(active_session_id, self._git_version, e_gen)
            logger.error(f"Erro ao gerar resposta com modelo (ID: {err_id}): {e_gen}", exc_info=True)

            err_msg_lower = str(e_gen).lower()
            if "429" in err_msg_lower or "quota" in err_msg_lower or "resourceexhausted" in err_msg_lower:
                resposta_texto = (
                    "Olá! O Vox está recebendo muitas mensagens de carinho e dúvidas no momento, "
                    "e atingimos o limite temporário de processamento. "
                    "Por favor, aguarde um minutinho e envie novamente! 💜"
                )
            elif "503" in err_msg_lower or "overloaded" in err_msg_lower:
                resposta_texto = (
                    "Ops! Os servidores de inteligência artificial estão enfrentando alta demanda temporária. "
                    "Que tal respirar fundo e tentar de novo em instantes? Estarei aqui esperando! 🏳️‍🌈"
                )
            else:
                resposta_texto = (
                    "Sinto muito, tive uma pequena instabilidade técnica ao processar sua mensagem. "
                    f"Nosso time já foi notificado (Código de suporte: {err_id}). "
                    "Se você estiver em situação de emergência ou precisando de acolhimento imediato, "
                    "lembre-se do Disque 100 (Direitos Humanos) ou 188 (CVV)."
                )

        # 3. Registro do Log de Conversa
        try:
            salvar_log_chat(
                session_id=active_session_id,
                git_version=self._git_version,
                prompt=prompt,
                response=resposta_texto,
                lista_kb_ids=referencias_raw,
            )
        except Exception as e_log:
            logger.warning(f"Falha ao salvar log de conversa: {e_log}")

        # 4. Síntese de Áudio (TTS) opcional
        audio_b64: Optional[str] = None
        if include_audio and resposta_texto:
            try:
                audio_buffer = texto_para_audio(resposta_texto)
                audio_b64 = base64.b64encode(audio_buffer.getvalue()).decode("utf-8")
            except Exception as e_audio:
                logger.warning(f"Falha ao gerar síntese de áudio: {e_audio}")

        # 5. Formatar referências estruturadas
        formatted_references: List[ReferenceItem] = []
        if referencias_raw:
            for item in referencias_raw:
                if isinstance(item, dict):
                    formatted_references.append(
                        ReferenceItem(
                            kb_id=item.get("kb_id") or str(item.get("id", "")),
                            similarity=item.get("similarity"),
                        )
                    )

        return ChatResponse(
            session_id=active_session_id,
            response=resposta_texto,
            topic=tema_match,
            references=formatted_references,
            audio_base64=audio_b64,
        )

    def chat_stream(
        self,
        prompt: str,
        session_id: Optional[str] = None,
        history: Optional[List[ChatMessage]] = None,
    ) -> Generator[str, None, None]:
        """
        Gera tokens em streaming para endpoints Server-Sent Events (SSE).

        Args:
            prompt: Pergunta do usuário.
            session_id: ID da sessão opcional.
            history: Histórico opcional de mensagens prévias.

        Yields:
            str: Fragmentos da resposta textual.
        """
        active_session_id = self.ensure_session(session_id)

        # RAG
        contexto_match = ""
        referencias_raw = None
        try:
            _, contexto_match, referencias_raw = semantica(prompt)
        except Exception as e:
            logger.warning(f"Erro no RAG durante streaming: {e}")

        gemini_history = self._format_gemini_history(history)
        chat_instance = inicializar_chat_modelo(history=gemini_history)
        resposta_acumulada: List[str] = []

        try:
            for chunk in gerar_resposta_stream(chat_instance, prompt, contexto_match or ""):
                resposta_acumulada.append(chunk)
                yield chunk
        except GeneratorExit:
            logger.info(f"Conexão SSE de streaming finalizada para sessão {active_session_id}.")
            raise
        except Exception as e:
            err_id = salvar_erro(active_session_id, self._git_version, e)
            logger.error(f"Erro no streaming de resposta: {e}")
            yield f"\n\n[Erro no processamento da resposta. Código: {err_id}]"
        finally:
            if resposta_acumulada:
                try:
                    salvar_log_chat(
                        session_id=active_session_id,
                        git_version=self._git_version,
                        prompt=prompt,
                        response="".join(resposta_acumulada),
                        lista_kb_ids=referencias_raw,
                    )
                except Exception as e:
                    logger.warning(f"Falha silenciosa ao salvar log do streaming: {e}")

    def transcribe(self, audio_file_bytes: bytes) -> str:
        """
        Transcreve um arquivo de áudio recebido em bytes utilizando o Gemini.

        Args:
            audio_file_bytes: Bytes brutos do áudio (MP3/WAV/etc).

        Returns:
            str: Texto transcrito.
        """
        texto = transcrever_audio(audio_file_bytes)
        if texto is None:
            raise RuntimeError("Não foi possível transcrever o áudio enviado.")
        return texto

    def rag_query(
        self,
        query: str,
        threshold: Optional[float] = None,
        limit: Optional[int] = None,
    ) -> RAGQueryResponse:
        """
        Executa a busca semântica direta na base de conhecimento.

        Args:
            query: Termo ou dúvida.
            threshold: Limite mínimo de similaridade.
            limit: Número máximo de chunks.

        Returns:
            RAGQueryResponse: Tópico, texto consolidado e referências.
        """
        tema, contexto, refs = semantica(query, threshold=threshold, limit=limit)
        return RAGQueryResponse(
            topic=tema,
            context=contexto,
            references=refs,
        )

    def submit_report(
        self,
        session_id: str,
        category_id: int,
        chat_history: str,
        comment: Optional[str] = None,
    ) -> bool:
        """
        Registra um reporte de usuário no banco de dados.
        """
        return salvar_report(
            session_id=session_id,
            git_version=self._git_version,
            chat_history=chat_history,
            category_id=category_id,
            comment=comment or "",
        )

    def get_categories(self) -> List[Dict[str, Any]]:
        """Retorna as categorias de reporte cadastradas."""
        return get_categorias_erro()

    def delete_session(self, session_id: str) -> bool:
        """
        Remove todos os dados de uma sessão para conformidade com a LGPD (Art. 18).
        """
        return excluir_dados_sessao(session_id)

    def health_check(self) -> HealthResponse:
        """
        Verifica a prontidão das conexões externas (Gemini e Supabase).
        """
        gemini_ok = configurar_api_gemini() is not None
        db_client = get_db_client()
        supabase_ok = db_client is not None

        status = "ok" if (gemini_ok and supabase_ok) else "degraded"

        return HealthResponse(
            status=status,
            version=self._git_version,
            gemini_configured=gemini_ok,
            supabase_configured=supabase_ok,
            environment="production",
        )

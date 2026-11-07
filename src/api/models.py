"""
Modelos de dados Pydantic para validação e serialização da API REST do Vox AI.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """Representa uma mensagem do histórico da conversa."""
    role: str = Field(..., description="Papel da mensagem: 'user' ou 'model'/'assistant'")
    content: str = Field(..., description="Conteúdo textual da mensagem")


class ChatRequest(BaseModel):
    """Corpo da requisição para o endpoint de chat."""
    prompt: str = Field(..., min_length=1, description="Texto da dúvida ou relato do usuário")
    session_id: Optional[str] = Field(None, description="Identificador único da sessão (UUID). Se omitido, é gerado automaticamente.")
    include_audio: bool = Field(False, description="Se True, gera e retorna o áudio TTS da resposta em base64")
    history: Optional[List[ChatMessage]] = Field(None, description="Histórico prévio de mensagens (opcional)")


class ReferenceItem(BaseModel):
    """Referência a um chunk da base de conhecimento utilizado no RAG."""
    kb_id: Optional[str] = Field(None, description="Identificador do chunk na base de conhecimento")
    similarity: Optional[float] = Field(None, description="Similaridade cosseno calculada")


class ChatResponse(BaseModel):
    """Resposta consolidada do assistente Vox AI."""
    session_id: str = Field(..., description="Identificador da sessão")
    response: str = Field(..., description="Texto gerado pelo modelo com a persona Vox")
    topic: Optional[str] = Field(None, description="Tópico identificado pela busca semântica RAG")
    references: Optional[List[ReferenceItem]] = Field(None, description="Lista de chunks e referências utilizadas")
    audio_base64: Optional[str] = Field(None, description="Áudio MP3 codificado em base64 (quando solicitado)")


class AudioTranscriptionResponse(BaseModel):
    """Resposta da transcrição de áudio via IA."""
    transcription: str = Field(..., description="Texto resultante da transcrição")


class RAGQueryRequest(BaseModel):
    """Requisição para consulta direta à base de conhecimento (RAG sem geração)."""
    query: str = Field(..., min_length=1, description="Pergunta ou termo para busca semântica")
    threshold: Optional[float] = Field(None, ge=0.0, le=1.0, description="Threshold mínimo de similaridade")
    limit: Optional[int] = Field(None, ge=1, le=50, description="Limite máximo de resultados")


class RAGQueryResponse(BaseModel):
    """Resposta da busca semântica no banco de conhecimento."""
    topic: Optional[str] = Field(None, description="Estratégia ou tópico identificado")
    context: Optional[str] = Field(None, description="Texto contextual concatenado para o LLM")
    references: Optional[List[Dict[str, Any]]] = Field(None, description="Metadados dos chunks correspondentes")


class ReportRequest(BaseModel):
    """Requisição de reporte de problema ou feedback de usuário."""
    session_id: str = Field(..., description="ID da sessão do usuário")
    category_id: int = Field(..., description="ID da categoria do erro")
    chat_history: str = Field(..., description="Histórico da conversa no momento do reporte")
    comment: Optional[str] = Field(None, description="Comentário descritivo opcional do usuário")


class ReportResponse(BaseModel):
    """Confirmação de recebimento do reporte."""
    success: bool = Field(..., description="Indica se o reporte foi salvo com sucesso")
    message: str = Field(..., description="Mensagem de status")


class ReportCategoryItem(BaseModel):
    """Categoria cadastrada para reporte de incidentes."""
    id: int
    label: str


class HealthResponse(BaseModel):
    """Status operacional do serviço e de suas dependências externas."""
    status: str = Field(..., description="'ok' ou 'degraded'")
    version: str = Field(..., description="Versão do software / tag git")
    gemini_configured: bool = Field(..., description="Indica se o cliente Google GenAI está pronto")
    supabase_configured: bool = Field(..., description="Indica se o cliente Supabase está pronto")
    environment: str = Field("production", description="Ambiente de execução")

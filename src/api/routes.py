"""
Rotas e Endpoints da API REST do Vox AI.
"""

from typing import List
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import StreamingResponse

from src.api.models import (
    AudioTranscriptionResponse,
    ChatRequest,
    ChatResponse,
    HealthResponse,
    RAGQueryRequest,
    RAGQueryResponse,
    ReportCategoryItem,
    ReportRequest,
    ReportResponse,
)
from src.api.service import VoxService

router = APIRouter()


def get_vox_service() -> VoxService:
    """Injeção de dependência do serviço central do Vox AI."""
    return VoxService()


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Verificação de Saúde do Serviço",
    tags=["Diagnóstico"],
)
def check_health(service: VoxService = Depends(get_vox_service)):
    """Retorna o status operacional da API, versão do software e conectividade com APIs externas."""
    return service.health_check()


@router.post(
    "/chat",
    response_model=ChatResponse,
    summary="Interação Conversacional com Persona Vox",
    tags=["Chat & IA"],
)
def chat_interaction(
    request: ChatRequest,
    service: VoxService = Depends(get_vox_service),
):
    """
    Processa o prompt do usuário aplicando a lógica RAG (Retrieval-Augmented Generation)
    e gerando a resposta assistida pela persona acolhedora do Vox.
    """
    try:
        return service.chat(
            prompt=request.prompt,
            session_id=request.session_id,
            include_audio=request.include_audio,
            history=request.history,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Falha interna ao processar requisição de chat: {e}",
        )


@router.post(
    "/chat/stream",
    summary="Streaming de Resposta Conversacional (SSE)",
    tags=["Chat & IA"],
)
def chat_streaming(
    request: ChatRequest,
    service: VoxService = Depends(get_vox_service),
):
    """
    Retorna a resposta do assistente em fluxo contínuo (Server-Sent Events)
    para renderização progressiva no cliente.
    """
    def event_generator():
        for chunk in service.chat_stream(
            prompt=request.prompt,
            session_id=request.session_id,
            history=request.history,
        ):
            # Formatação estrita SSE para preservar quebras de linha no payload de dados
            for line in chunk.split("\n"):
                yield f"data: {line}\n"
            yield "\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
    )


@router.post(
    "/transcribe",
    response_model=AudioTranscriptionResponse,
    summary="Transcrição de Áudio de Voz para Texto",
    tags=["Mídia"],
)
async def transcribe_audio_file(
    file: UploadFile = File(..., description="Arquivo de áudio gravado pelo usuário"),
    service: VoxService = Depends(get_vox_service),
):
    """
    Recebe um arquivo de áudio (MP3, WAV, WebM) e retorna a transcrição textual
    utilizando os modelos multimodais do Google Gemini.
    """
    if not file.content_type and not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Arquivo de áudio inválido ou ausente.",
        )

    try:
        content = await file.read()
        if len(content) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="O arquivo de áudio enviado está vazio.",
            )
        transcricao = service.transcribe(content)
        return AudioTranscriptionResponse(transcription=transcricao)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Falha na transcrição do áudio: {e}",
        )


@router.post(
    "/rag/query",
    response_model=RAGQueryResponse,
    summary="Busca Semântica Direta na Base de Conhecimento",
    tags=["RAG & Conhecimento"],
)
def query_knowledge_base(
    request: RAGQueryRequest,
    service: VoxService = Depends(get_vox_service),
):
    """
    Executa busca vetorial de similaridade no banco Supabase (pgvector)
    e retorna o tópico identificado e os chunks recuperados sem passar pelo modelo de texto.
    """
    return service.rag_query(
        query=request.query,
        threshold=request.threshold,
        limit=request.limit,
    )


@router.get(
    "/report/categories",
    response_model=List[ReportCategoryItem],
    summary="Categorias de Feedback e Incidentes",
    tags=["Moderação & Suporte"],
)
def list_report_categories(service: VoxService = Depends(get_vox_service)):
    """Lista as categorias pré-definidas para envio de relatórios e feedback."""
    return service.get_categories()


@router.post(
    "/report",
    response_model=ReportResponse,
    summary="Envio de Relatório / Feedback de Usuário",
    tags=["Moderação & Suporte"],
)
def submit_user_report(
    request: ReportRequest,
    service: VoxService = Depends(get_vox_service),
):
    """Registra uma denúncia, sugestão ou reporte de falha na conversa."""
    success = service.submit_report(
        session_id=request.session_id,
        category_id=request.category_id,
        chat_history=request.chat_history,
        comment=request.comment,
    )
    if success:
        return ReportResponse(
            success=True,
            message="Relatório registrado com sucesso. Agradecemos sua colaboração!",
        )
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Não foi possível salvar o relatório no banco de dados.",
    )


@router.delete(
    "/session/{session_id}",
    summary="Exclusão de Dados da Sessão (Conformidade LGPD)",
    tags=["Privacidade"],
)
def purge_session(
    session_id: str,
    service: VoxService = Depends(get_vox_service),
):
    """
    Atende ao Artigo 18 da Lei Geral de Proteção de Dados (LGPD - Direito ao Esquecimento),
    excluindo permanentemente todos os logs e registros vinculados a esta sessão.
    """
    success = service.delete_session(session_id)
    if success:
        return {"status": "success", "message": f"Dados da sessão {session_id} excluídos com sucesso."}
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Falha ao excluir dados da sessão no banco de dados.",
    )

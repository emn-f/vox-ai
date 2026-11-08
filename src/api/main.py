"""
Ponto de Entrada da Aplicação FastAPI do Vox AI Core Service.

Fornece uma API desacoplada, assíncrona e modularizada pronta para execução
em contêineres Docker, Hugging Face Spaces, Vercel ou instâncias em nuvem.
"""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.api.routes import router as api_router
from src.config import logger
from src.utils import git_version


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerenciamento de inicialização e encerramento da aplicação FastAPI."""
    version = git_version()
    logger.info(f"🌈 Iniciando Vox AI Core API Service (Versão: {version})...")
    yield
    logger.info("🛑 Encerrando Vox AI Core API Service...")


api_version = (git_version() or "v5.0.0").lstrip("v")
if not api_version:
    api_version = "5.0.0"

app = FastAPI(
    title="Vox AI - Core API",
    description=(
        "API desacoplada do Vox AI: Assistente virtual de apoio, cidadania e saúde LGBTQIA+ "
        "com Inteligência Artificial e busca semântica RAG (pgvector)."
    ),
    version=api_version,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Configuração de CORS para permitir acesso de frontends externos (React, Next.js, mobile, etc.)
cors_origins_str = os.getenv("CORS_ORIGINS", "*")
cors_origins = [origin.strip() for origin in cors_origins_str.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclusão do roteador sob o prefixo canônico /api/v1 e diretamente na raiz para conveniência
app.include_router(api_router, prefix="/api/v1")
app.include_router(api_router)


@app.get("/", summary="Boas-vindas da API", tags=["Geral"])
def root():
    """Endpoint raiz informativo."""
    return JSONResponse(
        content={
            "service": "Vox AI Core Service",
            "description": "Assistente de Apoio e Informação LGBTQIA+",
            "version": git_version(),
            "status": "online",
            "docs": "/docs",
            "endpoints": {
                "chat": "/api/v1/chat",
                "chat_stream": "/api/v1/chat/stream",
                "transcribe": "/api/v1/transcribe",
                "rag_query": "/api/v1/rag/query",
                "health": "/api/v1/health",
                "report": "/api/v1/report",
            },
        }
    )


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    uvicorn.run("src.api.main:app", host=host, port=port, reload=True)

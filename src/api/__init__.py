"""
Módulo de API REST do Vox AI.

Permite a execução desacoplada do core conversacional, RAG e transcrição
sem dependências do runtime da interface web Streamlit.
"""

from src.api.service import VoxService

__all__ = ["VoxService"]

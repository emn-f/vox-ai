"""
Módulo de Processamento de Busca Semântica do Vox AI.

Este módulo é responsável por gerenciar a etapa de recuperação de contexto (Retrieval-Augmented
Generation - RAG). Ele gera embeddings vetoriais a partir do prompt do usuário utilizando o
SDK do Google GenAI e consulta o banco de dados Supabase/PostgreSQL (via pgvector) para obter
os chunks de conhecimento mais similares e relevantes.

Principais Responsabilidades:
1. Conectar e autenticar no cliente da API Gemini.
2. Enviar a query do usuário para gerar o embedding correspondente.
3. Chamar a função de banco de dados para buscar e classificar o contexto inteligente.
4. Tratar erros específicos da API (como cota e indisponibilidade) de forma resiliente.
"""

from typing import Any

from google.genai import types
from google.genai.errors import APIError

from src.config import MODELO_SEMANTICO_NOME, TAMANHO_VETOR_SEMANTICO, logger
from src.core.database import recuperar_contexto_inteligente
from src.core.genai import configurar_api_gemini


def semantica(prompt: str) -> tuple[str | None, str | None, list[dict[str, Any]] | None]:
    """
    Gera o embedding vetorial para a pergunta do usuário e busca o contexto correspondente
    e relevante na base de dados de conhecimento do projeto.

    Args:
        prompt (str): Pergunta ou texto enviado pelo usuário.

    Returns:
        tuple[str | None, str | None, list[dict[str, Any]] | None]: Uma tupla contendo:
            - str | None: Nome do tópico vencedor ou estratégia de busca mapeada (ex: 'fallback_top5').
            - str | None: Bloco textual de contexto consolidado para alimentar o prompt de IA.
            - list[dict[str, Any]] | None: Lista de correspondências detalhadas (IDs, notas) para auditoria.
    """
    try:
        # 1. Configura e recupera o cliente da API do Gemini
        client = configurar_api_gemini()

        if not client:
            logger.warning("⚠️ Cliente Gemini não disponível para geração de embeddings semânticos.")
            return None, None, None

        # 2. Solicita a geração do embedding vetorial utilizando o modelo semântico
        #    A configuração define a tarefa como RETRIEVAL_QUERY e restringe as dimensões.
        response = client.models.embed_content(
            model=MODELO_SEMANTICO_NOME,
            contents=prompt,
            config=types.EmbedContentConfig(
                task_type="RETRIEVAL_QUERY",
                output_dimensionality=TAMANHO_VETOR_SEMANTICO,
            ),
        )

        # 3. Extrai o vetor gerado a partir da primeira resposta de embedding
        vetor_prompt = response.embeddings[0].values

        # 4. Executa a busca inteligente de similaridade no banco de dados (pgvector)
        #    Decide estrategicamente entre a expansão do tópico completo ou o fallback dos top-5 chunks.
        texto_contexto, fonte_identificadora, lista_ids = (
            recuperar_contexto_inteligente(vetor_prompt)
        )

        # Retorna os dados caso um contexto válido tenha sido recuperado com sucesso
        if texto_contexto:
            return fonte_identificadora, texto_contexto, lista_ids

        return None, None, None

    except APIError as e:
        # Tratamento estruturado de erros da API Gemini (erros de rede, limites, etc.)
        logger.error(
            f"❌ Erro de API do Gemini ao gerar embedding semântico (Código HTTP: {e.code}): {e}"
        )
        return None, None, None
    except Exception as e:
        logger.error(f"❌ Erro inesperado na geração do embedding semântico: {e}")
        return None, None, None

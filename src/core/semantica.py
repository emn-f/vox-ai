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

import re
from typing import Any

from google.genai import types
from google.genai.errors import APIError

from src.config import (
    LIMITE_TEMAS,
    MODELO_SEMANTICO_NOME,
    SEMANTICA_THRESHOLD,
    TAMANHO_VETOR_SEMANTICO,
    logger,
)
from src.core.database import recuperar_contexto_inteligente
from src.core.genai import configurar_api_gemini

# Conjunto de termos e expressões de saudação/small-talk trivial que não demandam busca na base de conhecimento
SAUDACOES_CONHECIDAS = {
    "oi", "oie", "oii", "oiii", "ola", "olá", "hey", "hello", "hi",
    "bom dia", "boa tarde", "boa noite", "opa", "e ai", "e aí", "eai",
    "tudo bem", "tudo bem?", "como vai", "como vai?", "tudo bom", "tudo bom?",
    "salve", "fala ai", "fala aí", "koé", "coe", "coé", "boa", "buenas"
}
TERMOS_SAUDACAO_BASE = {
    "oi", "ola", "olá", "hey", "hello", "hi", "opa", "eai", "salve",
    "tudo", "bem", "bom", "dia", "tarde", "noite", "vox", "ai",
    "como", "vai", "voce", "você", "ta", "tá"
}


def eh_saudacao(texto: str) -> bool:
    """
    Verifica se a mensagem enviada pelo usuário é puramente uma saudação, cumprimento
    ou início de conversa trivial (ex: 'hey', 'olá', 'bom dia', 'tudo bem?').

    Nesses casos, a busca vetorial (RAG) deve ser dispensada para evitar alucinações
    ou injeção de contextos espúrios na resposta de boas-vindas da persona.
    """
    if not texto or not texto.strip():
        return True

    texto_normalizado = texto.strip().lower()
    # Remove pontuação em toda a string para isolar palavras e expressões
    texto_sem_pontuacao = re.sub(r"[^\w\s]", " ", texto_normalizado)
    frase_limpa = " ".join(texto_sem_pontuacao.split())

    if not frase_limpa:
        return True

    if frase_limpa in SAUDACOES_CONHECIDAS:
        return True

    palavras = frase_limpa.split()
    if 1 <= len(palavras) <= 5 and all(p in TERMOS_SAUDACAO_BASE for p in palavras):
        return True

    return False


def semantica(
    prompt: str,
    threshold: float | None = None,
    limit: int | None = None,
) -> tuple[str | None, str | None, list[dict[str, Any]] | None]:
    """
    Gera o embedding vetorial para a pergunta do usuário e busca o contexto correspondente
    e relevante na base de dados de conhecimento do projeto.

    Args:
        prompt (str): Pergunta ou texto enviado pelo usuário.
        threshold (float | None): Limiar de similaridade cosseno opcional.
        limit (int | None): Número máximo de chunks candidatos inicial.

    Returns:
        tuple[str | None, str | None, list[dict[str, Any]] | None]: Uma tupla contendo:
            - str | None: Nome do tópico vencedor ou estratégia de busca mapeada (ex: 'fallback_top5').
            - str | None: Bloco textual de contexto consolidado para alimentar o prompt de IA.
            - list[dict[str, Any]] | None: Lista de correspondências detalhadas (IDs, notas) para auditoria.
    """
    # 0. Bypass de saudações e cumprimentos triviais: evita chamadas de embeddings e contextos espúrios
    if eh_saudacao(prompt):
        logger.info(f"👋 Entrada '{prompt}' identificada como saudação/small-talk. Dispensando RAG.")
        return None, None, None

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
            recuperar_contexto_inteligente(
                vetor_prompt,
                threshold=threshold if threshold is not None else SEMANTICA_THRESHOLD,
                limit=limit if limit is not None else LIMITE_TEMAS,
                query_texto=prompt,
            )
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

#!/usr/bin/env python3
"""
Script de Ingestão de Chunks na Knowledge Base (Vox AI).

Carrega os datasets JSON de enriquecimento da base de conhecimento (data/kb_enrichment/),
gera embeddings vetoriais de 1536 dimensões via Google GenAI (gemini-embedding-001)
e realiza a inserção/atualização idempotente no Supabase (knowledge_base).

Issues: #344, #345, #346, #347, #321, #320
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Garante que a raiz do projeto esteja no sys.path
CAMINHO_RAIZ = Path(__file__).resolve().parent.parent
if str(CAMINHO_RAIZ) not in sys.path:
    sys.path.insert(0, str(CAMINHO_RAIZ))

from src.config import (
    MODELO_SEMANTICO_NOME,
    TAMANHO_VETOR_SEMANTICO,
    get_secret,
    logger,
)
from src.core.db.client import get_db_client
from src.core.genai import configurar_api_gemini


DEFAULT_DATA_DIR = CAMINHO_RAIZ / "data" / "kb_enrichment"
_DEFAULT_SENTINEL = object()


def carregar_chunks_json(caminho: Path) -> List[Dict[str, Any]]:
    """
    Carrega chunks a partir de um arquivo JSON único ou de todos os arquivos JSON
    em um diretório especificado.

    Args:
        caminho: Caminho para arquivo JSON ou diretório contendo arquivos JSON.

    Returns:
        Lista de dicionários contendo os dados dos chunks.
    """
    chunks: List[Dict[str, Any]] = []

    if caminho.is_file():
        arquivos = [caminho]
    elif caminho.is_dir():
        arquivos = sorted(list(caminho.glob("*.json")))
    else:
        logger.error(f"❌ Caminho não encontrado: {caminho}")
        return []

    for arq in arquivos:
        try:
            with open(arq, "r", encoding="utf-8") as f:
                dados = json.load(f)
                itens = dados if isinstance(dados, list) else [dados] if isinstance(dados, dict) else []
                for item in itens:
                    if isinstance(item, dict):
                        topico = str(item.get("topico", "")).strip()
                        descricao = str(item.get("descricao", "")).strip()
                        if topico and descricao:
                            item_com_origem = dict(item)
                            item_com_origem["topico"] = topico
                            item_com_origem["descricao"] = descricao
                            item_com_origem["_origem_arquivo"] = arq.name
                            chunks.append(item_com_origem)
                        else:
                            logger.warning(f"⚠️ Item ignorado no arquivo {arq.name}: 'topico' ou 'descricao' vazio.")
                    else:
                        logger.warning(f"⚠️ Formato de item inválido no arquivo {arq.name}.")
        except Exception as e:
            logger.error(f"❌ Erro ao ler {arq.name}: {e}")

    return chunks


def gerar_embedding_chunk(
    texto: str,
    client_gemini: Any = _DEFAULT_SENTINEL,
    mock_local: bool = False,
) -> Optional[List[float]]:
    """
    Gera o vetor semântico de 1536 dimensões para o texto do chunk.

    Args:
        texto: Conteúdo textual a ser vetorizado.
        client_gemini: Cliente autenticado do Google GenAI.
        mock_local: Se True, gera um vetor sintético de 1536 floats para teste offline.

    Returns:
        Lista com 1536 floats ou None se indisponível.
    """
    if mock_local:
        # Gera vetor determinístico normalizado para testes offline
        import hashlib

        seed = int(hashlib.md5(texto.encode("utf-8")).hexdigest()[:8], 16)
        vetor_mock = [(float((seed + i) % 1000) / 1000.0) for i in range(TAMANHO_VETOR_SEMANTICO)]
        norm = sum(x * x for x in vetor_mock) ** 0.5 or 1.0
        return [round(x / norm, 6) for x in vetor_mock]

    client = (
        configurar_api_gemini()
        if client_gemini is _DEFAULT_SENTINEL
        else client_gemini
    )

    if not client:
        return None

    try:
        from google.genai import types

        resultado = client.models.embed_content(
            model=MODELO_SEMANTICO_NOME,
            contents=texto,
            config=types.EmbedContentConfig(
                task_type="RETRIEVAL_DOCUMENT",
                output_dimensionality=TAMANHO_VETOR_SEMANTICO,
            ),
        )
        if resultado.embeddings and len(resultado.embeddings) > 0:
            return resultado.embeddings[0].values
    except Exception as e:
        logger.error(f"❌ Falha ao calcular embedding via Gemini: {e}")

    return None


def verificar_registro_existente(
    supabase_client: Any,
    topico: str,
) -> Optional[Dict[str, Any]]:
    """
    Verifica se já existe registro com o mesmo tópico na tabela knowledge_base.
    Levanta RuntimeError se a consulta falhar para evitar decisões indevidas de inserção.

    Args:
        supabase_client: Cliente autenticado do Supabase.
        topico: Título/tópico do chunk.

    Returns:
        Dicionário com dados do registro existente ou None.
    """
    try:
        resp = (
            supabase_client.table("knowledge_base")
            .select("kb_id, topico, embedding")
            .eq("topico", topico)
            .limit(1)
            .execute()
        )
        if resp.data and len(resp.data) > 0:
            return resp.data[0]
        return None
    except Exception as e:
        logger.error(f"❌ Erro ao consultar existência do tópico '{topico}': {e}")
        raise RuntimeError(f"Falha na consulta ao banco de dados: {e}") from e


def obter_proximo_kb_id(supabase_client: Any) -> Optional[str]:
    """
    Obtém o próximo identificador sequencial (ex: vox-kb-0343) baseado no maior ID existente.
    Evita colisões quando a sequence do PostgreSQL (kb_id_seq) estiver defasada.
    """
    try:
        import re

        resp = (
            supabase_client.table("knowledge_base")
            .select("kb_id")
            .order("kb_id", desc=True)
            .limit(20)
            .execute()
        )
        if resp.data:
            numeros = [
                int(m.group(1))
                for r in resp.data
                if (m := re.search(r"(\d+)", str(r.get("kb_id", ""))))
            ]
            if numeros:
                return f"vox-kb-{max(numeros) + 1:04d}"
    except Exception as e:
        logger.warning(f"⚠️ Não foi possível determinar próximo kb_id dinâmico: {e}")
    return None


def ingerir_chunk(
    chunk: Dict[str, Any],
    supabase_client: Any = _DEFAULT_SENTINEL,
    client_gemini: Any = _DEFAULT_SENTINEL,
    dry_run: bool = False,
    local_mode: bool = False,
) -> Tuple[str, Optional[Dict[str, Any]]]:
    """
    Processa e insere um único chunk na knowledge_base com garantia de idempotência.

    Retorna:
        Tupla (status, detalhes) onde status é:
        - 'inserted': Registro novo inserido com sucesso.
        - 'updated_embedding': Registro já existia sem vetor e foi atualizado.
        - 'skipped': Registro já existia completamente.
        - 'dry_run': Simulação executada com sucesso.
        - 'local_processed': Processado em modo local/offline.
        - 'error': Falha durante o processamento.
    """
    topico = str(chunk.get("topico", "")).strip()
    descricao = str(chunk.get("descricao", "")).strip()
    eixo = chunk.get("eixo_tematico", "Geral")
    referencias = chunk.get("referencias", "")
    tags = chunk.get("tags", [])
    autor = chunk.get("autor", "Vox AI - Curadoria Especializada")
    kb_count = chunk.get("kb_count", 0)

    if not topico or not descricao:
        return "error", {"erro": "Chunk sem 'topico' ou 'descricao'"}

    # Resolução dos clientes: usa o explicitamente fornecido ou busca padrão
    client_db = get_db_client() if supabase_client is _DEFAULT_SENTINEL else supabase_client
    client_gen = (
        (None if local_mode else configurar_api_gemini())
        if client_gemini is _DEFAULT_SENTINEL
        else client_gemini
    )

    texto_embedding = descricao

    # 1. Simulação (Dry-Run)
    if dry_run:
        vetor = gerar_embedding_chunk(texto_embedding, client_gen, mock_local=local_mode)
        detalhes: Dict[str, Any] = {
            "topico": topico,
            "tem_vetor": vetor is not None,
            "dim": len(vetor) if vetor else 0,
        }
        if client_db is not None:
            try:
                existente = verificar_registro_existente(client_db, topico)
                detalhes["existente"] = existente is not None
                if existente:
                    detalhes["kb_id"] = existente.get("kb_id")
                    detalhes["tem_embedding_db"] = existente.get("embedding") is not None
            except Exception as e:
                detalhes["erro_db"] = str(e)
        return "dry_run", detalhes

    # 2. Modo local/offline explícito sem Supabase ativo
    if local_mode and client_db is None:
        vetor = gerar_embedding_chunk(texto_embedding, client_gen, mock_local=True)
        return "local_processed", {
            "topico": topico,
            "eixo_tematico": eixo,
            "tem_vetor": vetor is not None,
            "dim": len(vetor) if vetor else 0,
        }

    # 3. Modo real ou com supabase_client fornecido
    if not client_db:
        return "error", {
            "topico": topico,
            "erro": "Cliente Supabase não configurado ou indisponível.",
        }

    # Consulta existência do registro
    try:
        registro_existente = verificar_registro_existente(client_db, topico)
    except Exception as e:
        return "error", {"topico": topico, "erro": str(e)}

    if registro_existente:
        kb_id = registro_existente.get("kb_id")
        embedding_atual = registro_existente.get("embedding")

        # Se já existe e já tem embedding, não duplica nem sobrescreve
        if embedding_atual is not None:
            return "skipped", {"kb_id": kb_id, "topico": topico}

        # Se existe mas está sem embedding, calcula e atualiza
        novo_vetor = gerar_embedding_chunk(texto_embedding, client_gemini, mock_local=local_mode)
        if novo_vetor is None:
            return "error", {
                "kb_id": kb_id,
                "topico": topico,
                "erro": "Falha ao gerar embedding para registro existente com vetor nulo.",
            }

        try:
            client_db.table("knowledge_base").update({"embedding": novo_vetor}).eq("kb_id", kb_id).is_("embedding", "null").execute()
            return "updated_embedding", {"kb_id": kb_id, "topico": topico}
        except Exception as e:
            return "error", {"kb_id": kb_id, "topico": topico, "erro": str(e)}

    # Registro não existe: gera embedding e insere novo
    vetor = gerar_embedding_chunk(texto_embedding, client_gemini, mock_local=local_mode)

    payload = {
        "topico": topico,
        "eixo_tematico": eixo,
        "descricao": descricao,
        "referencias": referencias,
        "tags": tags,
        "autor": autor,
        "kb_count": kb_count,
        "embedding": vetor,
    }

    proximo_kb_id = obter_proximo_kb_id(client_db)
    if proximo_kb_id:
        payload["kb_id"] = proximo_kb_id

    try:
        resp = client_db.table("knowledge_base").insert(payload).execute()
        novo_id = resp.data[0].get("kb_id") if resp.data else (proximo_kb_id or "novo")
        return "inserted", {"kb_id": novo_id, "topico": topico}
    except Exception as e:
        return "error", {"topico": topico, "erro": str(e)}


def executar_ingestao(
    caminho: Path,
    dry_run: bool = False,
    local_mode: bool = False,
    supabase_client: Optional[Any] = None,
    gemini_client: Optional[Any] = None,
) -> Dict[str, int]:
    """
    Executa o fluxo completo de ingestão a partir dos arquivos de enriquecimento.

    Args:
        caminho: Diretório ou arquivo JSON de entrada.
        dry_run: Se True, apenas simula sem persistir no banco.
        local_mode: Se True, simula embeddings localmente sem chamada a API externa.
        supabase_client: Cliente Supabase opcional (para injeção/testes).
        gemini_client: Cliente Gemini opcional (para injeção/testes).

    Returns:
        Dicionário com a contagem de resultados por status.
    """
    print(f"📂 Carregando chunks a partir de: {caminho}")
    chunks = carregar_chunks_json(caminho)
    total = len(chunks)

    estatisticas: Dict[str, int] = {
        "total": total,
        "inserted": 0,
        "updated_embedding": 0,
        "skipped": 0,
        "dry_run": 0,
        "local_processed": 0,
        "error": 0,
    }

    if total == 0:
        print("⚠️ Nenhum chunk válido encontrado para ingestão.")
        return estatisticas

    print(f"🚀 Total de chunks encontrados: {total}")
    print(f"⚙️  Modo: {'DRY-RUN (Simulação)' if dry_run else 'EXECUÇÃO REAL'}")
    print(f"🧠 Embeddings: {'LOCAL (Mock 1536-dim)' if local_mode else 'GEMINI (gemini-embedding-001 1536-dim)'}")
    print("-" * 60)

    # Inicializa clientes uma única vez
    client_db = supabase_client
    if client_db is None and not local_mode:
        client_db = get_db_client()

    client_gen = gemini_client
    if client_gen is None and not local_mode:
        client_gen = configurar_api_gemini()

    if not dry_run and not local_mode and client_db is None:
        logger.error("❌ Conexão com Supabase indisponível. Para executar offline use --local ou --dry-run.")

    if not local_mode and client_gen is None:
        logger.warning("⚠️ Cliente Gemini não configurado; embeddings remotos não puderam ser gerados.")

    for idx, chunk in enumerate(chunks, 1):
        topico = chunk.get("topico", "Sem título")
        arquivo = chunk.get("_origem_arquivo", "")

        status, detalhes = ingerir_chunk(
            chunk=chunk,
            supabase_client=client_db,
            client_gemini=client_gen,
            dry_run=dry_run,
            local_mode=local_mode,
        )

        estatisticas[status] = estatisticas.get(status, 0) + 1

        icone = {
            "inserted": "✅ [INSERIDO]",
            "updated_embedding": "🔄 [VETORIZADO]",
            "skipped": "⏭️  [IGNORADO - JÁ EXISTE]",
            "dry_run": "🔍 [SIMULADO]",
            "local_processed": "📦 [LOCAL]",
            "error": "❌ [ERRO]",
        }.get(status, status)

        origem_str = f" ({arquivo})" if arquivo else ""
        print(f"[{idx:02d}/{total:02d}] {icone} {topico}{origem_str}")
        if status == "error":
            print(f"    └─ Detalhes: {detalhes}")

    print("-" * 60)
    tem_erros = estatisticas.get("error", 0) > 0
    if tem_erros:
        print("⚠️ Ingestão finalizada com FALHAS:")
    else:
        print("🏁 Ingestão concluída com sucesso:")
    print(f"   • Total de Chunks:         {estatisticas['total']}")
    print(f"   • Novos Inseridos:         {estatisticas.get('inserted', 0)}")
    print(f"   • Embeddings Atualizados:  {estatisticas.get('updated_embedding', 0)}")
    print(f"   • Já Existentes (Skipped): {estatisticas.get('skipped', 0)}")
    if dry_run:
        print(f"   • Simulados (Dry-Run):     {estatisticas.get('dry_run', 0)}")
    if estatisticas.get("local_processed", 0) > 0:
        print(f"   • Processados Localmente:  {estatisticas.get('local_processed', 0)}")
    print(f"   • Falhas/Erros:            {estatisticas.get('error', 0)}")
    print("-" * 60)

    return estatisticas


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingestão de Chunks na Knowledge Base (Vox AI)")
    parser.add_argument(
        "--path",
        "-p",
        type=Path,
        default=DEFAULT_DATA_DIR,
        help="Caminho para arquivo JSON ou diretório com datasets (padrão: data/kb_enrichment)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Executa a simulação sem persistir dados no banco de dados",
    )
    parser.add_argument(
        "--local",
        action="store_true",
        help="Executa com geração sintética de vetores 1536-dim para testes locais/offline",
    )

    args = parser.parse_args()
    stats = executar_ingestao(
        caminho=args.path,
        dry_run=args.dry_run,
        local_mode=args.local,
    )
    if stats.get("error", 0) > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()

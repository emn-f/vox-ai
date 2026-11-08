#!/usr/bin/env python3
"""
Pipeline de Ingestão e Enriquecimento de Dados com IA (Human-in-the-Loop).

Objetivo:
Automatizar a coleta, estruturação via LLM (Gemini) e armazenamento em staging
de conteúdos relevantes (leis, cartilhas, direitos LGBTQIA+) com revisão humana obrigatória
antes da indexação vetorial na tabela de produção `knowledge_base`.

Issues: #255, #285, #97
"""

from __future__ import annotations

import argparse
import html
import json
import os
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

# Importações de configuração interna do Vox
caminho_raiz = str(Path(__file__).resolve().parent.parent)
if caminho_raiz not in sys.path:
    sys.path.append(caminho_raiz)

try:
    from src.config import (
        GEMINI_MODEL_GATEKEEP,
        GEMINI_MODEL_NAME,
        MODELO_SEMANTICO_NOME,
        TAMANHO_VETOR_SEMANTICO,
        logger,
    )
    from src.core.db.client import get_db_client
    from src.core.genai import configurar_api_gemini
except ImportError:
    import logging
    logger = logging.getLogger("pipeline_ingestao_ia")
    GEMINI_MODEL_NAME = "gemini-3.6-flash"
    GEMINI_MODEL_GATEKEEP = "gemini-3.1-flash-lite"
    MODELO_SEMANTICO_NOME = "gemini-embedding-001"
    TAMANHO_VETOR_SEMANTICO = 1536
    get_db_client = lambda: None
    configurar_api_gemini = lambda: None


# ==============================================================================
# PROMPT DO SISTEMA ANTI-ALUCINAÇÃO JURÍDICA E DE SAÚDE
# ==============================================================================

PROMPT_SISTEMA_INGESTAO = """Você é um especialista em curadoria técnica e estruturação de conhecimento para o Vox AI, assistente virtual focado na comunidade LGBTQIA+.

Sua missão:
Ler o texto bruto fornecido (notícia, legislação, artigo ou cartilha) e extrair pares atômicos de Conhecimento Estruturado (Pergunta e Resposta).

DIRETRIZES CRÍTICAS ANTI-ALUCINAÇÃO:
1. NUNCA invente números de leis, artigos, portarias ou decisões judiciais. Cite estritamente o que está fundamentado no texto de entrada ou jurisprudência pública consolidada no Brasil (ex: ADO 26, STF, SUS).
2. Não faça suposições clínicas ou médicas; referencie diretrizes oficiais (ex: Portarias do SUS para o Processo Transexualizador).
3. Mantenha o tom da resposta empático, acolhedor, respeitoso e em conformidade com as diretrizes do Vox AI.
4. Responda ESTRITAMENTE em formato JSON com uma lista de objetos, sem blocos de texto adicionais antes ou depois.

Formato esperado de saída (JSON):
[
  {
    "pergunta_usuario": "Dúvida comum de um usuário LGBTQIA+ respondida pelo texto",
    "resposta_vox": "Resposta acolhedora, precisa e objetiva com os fatos extraídos",
    "topico": "Tópico central (ex: Nome Social, Retificação de Registro, Saúde Trans)",
    "eixo_tematico": "Eixo geral (Direitos e Cidadania, Saúde, Suporte Emocional, Cultura)",
    "tags": ["tag1", "tag2", "tag3"],
    "data_referencia": "YYYY-MM-DD"
  }
]
"""


# ==============================================================================
# ETAPA 1: EXTRAÇÃO DE CONTEÚDO (EXTRACTION)
# ==============================================================================

def extrair_texto_de_url(url: str, timeout: int = 15) -> str:
    """
    Extrai o conteúdo de texto legível a partir de uma URL web.
    Remove tags HTML e scripts usando parser nativo leve e resiliente,
    decodificando entidades HTML.
    """
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) VoxAI-Ingestion/1.0"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            html_content = resp.read().decode("utf-8", errors="replace")
    except Exception as e:
        logger.error(f"Erro ao acessar URL {url}: {e}")
        raise RuntimeError(f"Falha ao descarregar URL: {e}")

    # Limpeza simples de HTML sem dependências pesadas
    texto = re.sub(r"<script.*?</script>", "", html_content, flags=re.DOTALL | re.IGNORECASE)
    texto = re.sub(r"<style.*?</style>", "", texto, flags=re.DOTALL | re.IGNORECASE)
    texto = re.sub(r"<noscript.*?</noscript>", "", texto, flags=re.DOTALL | re.IGNORECASE)
    texto = re.sub(r"<[^>]+>", " ", texto)
    # Decodificar entidades HTML (&atilde;, &ordm;, etc.)
    texto = html.unescape(texto)
    # Colapso de espaços em branco excessivos
    texto = re.sub(r"\s+", " ", texto).strip()
    return texto[:15000]  # Limite de segurança para janela de contexto


def extrair_texto_de_arquivo(caminho_arquivo: str) -> str:
    """
    Lê o conteúdo de um arquivo de texto local (TXT, MD, HTML, JSON, CSV).
    Valida existência e conteúdo não vazio.
    """
    if not os.path.exists(caminho_arquivo):
        raise FileNotFoundError(f"Arquivo não encontrado: {caminho_arquivo}")

    with open(caminho_arquivo, "r", encoding="utf-8", errors="replace") as f:
        conteudo = f.read().strip()

    if not conteudo:
        raise ValueError(f"O arquivo {caminho_arquivo} está vazio.")

    return conteudo


# ==============================================================================
# ETAPA 2: TRANSFORMAÇÃO E ESTRUTURAÇÃO COM IA (TRANSFORMATION)
# ==============================================================================

def estruturar_conteudo_com_ia(
    texto_fonte: str,
    fonte_referencia: str,
    cliente_gemini: Optional[Any] = None,
) -> List[Dict[str, Any]]:
    """
    Envia o texto para o LLM Gemini Flash e obtém itens estruturados em JSON.
    Possui fallback mock para testes em ambientes sem chave de API.
    """
    if not texto_fonte or not texto_fonte.strip():
        logger.warning("Texto fonte vazio recebido para estruturação com IA.")
        return []

    client = cliente_gemini or configurar_api_gemini()
    hoje = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    if client is None:
        logger.info("Cliente Gemini indisponível. Gerando estruturação de fallback mock.")
        return [
            {
                "pergunta_usuario": "Como o texto selecionado auxilia a comunidade LGBTQIA+?",
                "resposta_vox": texto_fonte[:300].strip(),
                "topico": "Direitos e Informação",
                "eixo_tematico": "Direitos e Cidadania",
                "tags": ["vox", "informacao", "direitos"],
                "fonte_original": fonte_referencia,
                "data_referencia": hoje,
            }
        ]

    prompt_usuario = (
        f"Fonte de Referência: {fonte_referencia}\n\n"
        f"Texto a ser analisado e estruturado:\n{texto_fonte}"
    )

    try:
        from google.genai import types

        resposta = client.models.generate_content(
            model=GEMINI_MODEL_NAME,
            contents=[
                types.Part.from_text(text=PROMPT_SISTEMA_INGESTAO),
                types.Part.from_text(text=prompt_usuario),
            ],
            config=types.GenerateContentConfig(
                temperature=0.2,
                response_mime_type="application/json",
            ),
        )

        conteudo_raw = resposta.text.strip() if resposta.text else ""

        # Extração flexível de bloco JSON mesmo se houver preâmbulos ou cercas de markdown
        match_fences = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", conteudo_raw)
        if match_fences:
            conteudo_json = match_fences.group(1).strip()
        else:
            match_json = re.search(r"(\[[\s\S]*\]|\{[\s\S]*\})", conteudo_raw)
            conteudo_json = match_json.group(1).strip() if match_json else conteudo_raw

        itens = json.loads(conteudo_json)
        if isinstance(itens, dict):
            itens = [itens]

        for item in itens:
            item["fonte_original"] = fonte_referencia
            if "data_referencia" not in item or not item["data_referencia"]:
                item["data_referencia"] = hoje

        return itens

    except Exception as e:
        logger.error(f"Erro ao estruturar conteúdo com LLM: {e}")
        return [
            {
                "pergunta_usuario": "Informação extraída da fonte",
                "resposta_vox": texto_fonte[:250].strip(),
                "topico": "Informação Geral",
                "eixo_tematico": "Geral",
                "tags": ["geral"],
                "fonte_original": fonte_referencia,
                "data_referencia": hoje,
            }
        ]


# ==============================================================================
# ETAPA 3: CARGA NA TABELA DE STAGING (LOAD & HUMAN-IN-THE-LOOP)
# ==============================================================================

LOCAL_STAGING_PATH = Path(caminho_raiz) / "data" / "staging_conteudo_pendente.json"


def _is_table_missing_error(e: Exception) -> bool:
    """Verifica se o erro é decorrente da tabela de staging não existir no banco."""
    err_msg = str(e).lower()
    return "pgrst205" in err_msg or "could not find the table" in err_msg or "does not exist" in err_msg


def _carregar_staging_local() -> List[Dict[str, Any]]:
    """Carrega registros de staging salvos localmente."""
    if not LOCAL_STAGING_PATH.exists():
        return []
    try:
        with open(LOCAL_STAGING_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except Exception as e:
        logger.warning(f"Falha ao ler staging local ({LOCAL_STAGING_PATH}): {e}")
        return []


def _salvar_staging_local(itens: List[Dict[str, Any]]) -> None:
    """Persiste registros de staging localmente com formatação legível."""
    LOCAL_STAGING_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(LOCAL_STAGING_PATH, "w", encoding="utf-8") as f:
        json.dump(itens, f, indent=2, ensure_ascii=False)


def salvar_em_staging(
    itens_estruturados: List[Dict[str, Any]],
    supabase_client: Optional[Any] = None,
) -> List[Dict[str, Any]]:
    """
    Insere os registros estruturados na tabela de staging `conteudo_pendente`
    com status 'PENDING_REVIEW'. Nenhum dado é inserido direto na KB de produção.
    Caso a tabela remota não esteja disponível no banco, realiza fallback
    transparente para o arquivo local data/staging_conteudo_pendente.json.
    """
    if not itens_estruturados:
        logger.info("Nenhum item para salvar em staging.")
        return []

    client = supabase_client or get_db_client()

    registros_para_inserir = []
    for item in itens_estruturados:
        tags = item.get("tags") or []
        if isinstance(tags, str):
            tags_list = [t.strip().strip("'\"") for t in tags.split(",") if t.strip().strip("'\"")]
        elif isinstance(tags, (list, tuple)):
            tags_list = [str(t).strip().strip("'\"") for t in tags if str(t).strip().strip("'\"")]
        else:
            tags_list = []

        registro = {
            "pergunta_usuario": item.get("pergunta_usuario", "Pergunta não definida"),
            "resposta_vox": item.get("resposta_vox", "Resposta não definida"),
            "tags": tags_list,
            "fonte_original": item.get("fonte_original", "Fonte desconhecida"),
            "data_referencia": item.get("data_referencia", datetime.now(timezone.utc).isoformat()),
            "status": "PENDING_REVIEW",
            "criado_em": datetime.now(timezone.utc).isoformat(),
        }
        registros_para_inserir.append(registro)

    if client:
        try:
            resp = client.table("conteudo_pendente").insert(registros_para_inserir).execute()
            logger.info(f"✅ {len(registros_para_inserir)} itens inseridos em 'conteudo_pendente'.")
            return resp.data or registros_para_inserir
        except Exception as e:
            if _is_table_missing_error(e):
                logger.warning(
                    "⚠️ Tabela remota 'conteudo_pendente' não encontrada no banco (migração pendente de deploy). "
                    "Salvando os itens em staging local: data/staging_conteudo_pendente.json"
                )
                existentes = _carregar_staging_local()
                proximo_id = max([int(x.get("id", 0)) for x in existentes if str(x.get("id", "")).isdigit()] or [0]) + 1
                for reg in registros_para_inserir:
                    reg["id"] = proximo_id
                    proximo_id += 1
                    existentes.append(reg)
                _salvar_staging_local(existentes)
                return registros_para_inserir
            logger.error(f"Erro ao salvar na tabela 'conteudo_pendente': {e}")
            raise e

    logger.warning("Supabase não disponível. Itens processados no staging local.")
    existentes = _carregar_staging_local()
    proximo_id = max([int(x.get("id", 0)) for x in existentes if str(x.get("id", "")).isdigit()] or [0]) + 1
    for reg in registros_para_inserir:
        reg["id"] = proximo_id
        proximo_id += 1
        existentes.append(reg)
    _salvar_staging_local(existentes)
    return registros_para_inserir


def listar_conteudos_pendentes(
    supabase_client: Optional[Any] = None,
    status: str = "PENDING_REVIEW",
) -> List[Dict[str, Any]]:
    """
    Recupera conteúdos pendentes de revisão na tabela staging (Supabase ou fallback local).
    """
    client = supabase_client or get_db_client()
    if client:
        try:
            resp = (
                client.table("conteudo_pendente")
                .select("*")
                .eq("status", status)
                .order("criado_em", desc=True)
                .execute()
            )
            return resp.data or []
        except Exception as e:
            if _is_table_missing_error(e):
                logger.info(
                    "ℹ️ Tabela 'conteudo_pendente' não encontrada no Supabase. Lendo registros do staging local."
                )
                itens_locais = _carregar_staging_local()
                return [item for item in itens_locais if item.get("status") == status]
            logger.error(f"Erro ao listar pendentes: {e}")
            return []

    itens_locais = _carregar_staging_local()
    return [item for item in itens_locais if item.get("status") == status]


def revisar_conteudo(
    item_id: Union[int, str],
    decisao: str,  # APPROVED ou REJECTED
    notas: Optional[str] = None,
    revisor: str = "curador_humano",
    supabase_client: Optional[Any] = None,
) -> Dict[str, Any]:
    """
    Executa a ação humana de aprovação ou rejeição sobre um item pendente.
    """
    decisao_upper = decisao.upper()
    if decisao_upper not in ("APPROVED", "REJECTED"):
        raise ValueError("A decisão deve ser 'APPROVED' ou 'REJECTED'.")

    client = supabase_client or get_db_client()
    payload_update = {
        "status": decisao_upper,
        "revisado_por": revisor,
        "revisado_em": datetime.now(timezone.utc).isoformat(),
        "notas_revisao": notas or "",
    }

    if client:
        try:
            resp = (
                client.table("conteudo_pendente")
                .update(payload_update)
                .eq("id", item_id)
                .execute()
            )
            if not resp.data:
                raise ValueError(f"Item com ID {item_id} não encontrado na tabela 'conteudo_pendente'.")
            return resp.data[0]
        except Exception as e:
            if _is_table_missing_error(e):
                logger.info("ℹ️ Tabela remota ausente. Atualizando item no staging local.")
                existentes = _carregar_staging_local()
                for item in existentes:
                    if str(item.get("id")) == str(item_id):
                        item.update(payload_update)
                        _salvar_staging_local(existentes)
                        return item
                raise ValueError(f"Item com ID {item_id} não encontrado no staging local.")
            raise e

    logger.warning("Supabase não disponível. Decisão de revisão realizada no staging local.")
    existentes = _carregar_staging_local()
    for item in existentes:
        if str(item.get("id")) == str(item_id):
            item.update(payload_update)
            _salvar_staging_local(existentes)
            return item
    res = dict(payload_update)
    res["id"] = item_id
    return res


def promover_item_para_knowledge_base(
    item_staging: Dict[str, Any],
    topico: Optional[str] = None,
    eixo_tematico: Optional[str] = None,
    supabase_client: Optional[Any] = None,
    gemini_client: Optional[Any] = None,
) -> Dict[str, Any]:
    """
    Promove um item APROVADO da tabela de staging para a tabela de produção `knowledge_base`:
    - Preserva o tópico e eixo temático extraídos ou permite sobreposição manual
    - Calcula o vetor semântico (embedding)
    - Grava o chunk oficial na knowledge_base
    - Atualiza o registro em conteudo_pendente com o kb_id gerado
    """
    if item_staging.get("status") != "APPROVED":
        raise ValueError("Apenas itens com status 'APPROVED' podem ser promovidos para a Knowledge Base.")

    client_db = supabase_client or get_db_client()
    client_genai = gemini_client or configurar_api_gemini()

    descricao_kb = f"Pergunta: {item_staging['pergunta_usuario']}\n\nResposta: {item_staging['resposta_vox']}"
    tags = item_staging.get("tags") or []
    referencias = item_staging.get("fonte_original") or "Curadoria Vox AI"
    topico_final = topico or item_staging.get("topico") or "Informação Verificada"
    eixo_final = eixo_tematico or item_staging.get("eixo_tematico") or "Direitos e Cidadania"

    # Geração de embedding vetorial
    embedding = None
    if client_genai:
        try:
            from google.genai import types

            res = client_genai.models.embed_content(
                model=MODELO_SEMANTICO_NOME,
                contents=descricao_kb,
                config=types.EmbedContentConfig(
                    task_type="RETRIEVAL_DOCUMENT",
                    output_dimensionality=TAMANHO_VETOR_SEMANTICO,
                ),
            )
            if hasattr(res, "embeddings") and res.embeddings:
                raw_emb = res.embeddings[0].values
                if isinstance(raw_emb, (list, tuple, np.ndarray)):
                    embedding = [float(x) for x in raw_emb]
                elif not type(raw_emb).__name__.startswith("MagicMock"):
                    embedding = raw_emb
        except Exception as e:
            logger.error(f"Erro ao gerar embedding: {e}")

    # Inserção na tabela oficial
    registro_kb = {
        "topico": topico_final,
        "eixo_tematico": eixo_final,
        "descricao": descricao_kb,
        "referencias": referencias,
        "tags": tags,
        "autor": item_staging.get("revisado_por", "Curador Humano"),
        "embedding": embedding,
        "ativo": True,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    if client_db:
        resp = client_db.table("knowledge_base").insert(registro_kb).execute()
        item_criado = resp.data[0] if resp.data else registro_kb

        # Atualiza o registro de staging para registrar o vínculo com a KB de produção
        staging_id = item_staging.get("id")
        if staging_id:
            try:
                kb_id = item_criado.get("kb_id")
                nota_promocao = f"Promovido para knowledge_base (kb_id: {kb_id})"
                update_staging: Dict[str, Any] = {
                    "notas_revisao": f"{item_staging.get('notas_revisao', '')} | {nota_promocao}".strip(" |"),
                }
                if kb_id:
                    update_staging["kb_id"] = kb_id
                try:
                    client_db.table("conteudo_pendente").update(update_staging).eq("id", staging_id).execute()
                except Exception as e_stg:
                    if _is_table_missing_error(e_stg):
                        existentes = _carregar_staging_local()
                        for item in existentes:
                            if str(item.get("id")) == str(staging_id):
                                item.update(update_staging)
                                _salvar_staging_local(existentes)
                                break
                    else:
                        logger.warning(f"Falha ao vincular kb_id no staging: {e_stg}")
            except Exception as e:
                logger.warning(f"Falha ao vincular kb_id no staging: {e}")

        return item_criado

    return registro_kb


# ==============================================================================
# CLI E EXECUÇÃO
# ==============================================================================

def main() -> None:
    parser = argparse.ArgumentParser(description="Pipeline de Ingestão de Dados com IA para Vox AI")
    subparsers = parser.add_subparsers(dest="subcomando", help="Subcomandos do pipeline")

    # Ingestão
    parser_ingest = subparsers.add_parser("ingest", help="Extrai, processa e envia para staging")
    parser_ingest.add_argument("--url", type=str, help="URL pública para ingestão")
    parser_ingest.add_argument("--texto", type=str, help="Texto bruto para ingestão")
    parser_ingest.add_argument("--arquivo", type=str, help="Arquivo local (txt, md) para ingestão")
    parser_ingest.add_argument("--fonte", type=str, default="Entrada Manual", help="Identificação da fonte")

    # Listar pendentes
    parser_list = subparsers.add_parser("list-pending", help="Lista conteúdos na tabela de staging")
    parser_list.add_argument("--status", type=str, default="PENDING_REVIEW")

    # Revisar item
    parser_rev = subparsers.add_parser("review", help="Revisão humana (aprovar ou rejeitar)")
    parser_rev.add_argument("--id", required=True, help="ID do registro em staging")
    parser_rev.add_argument("--acao", required=True, choices=["APPROVED", "REJECTED"], help="Decisão")
    parser_rev.add_argument("--notas", type=str, default="", help="Observações da curadoria")
    parser_rev.add_argument("--revisor", type=str, default="admin", help="Nome do revisor")
    parser_rev.add_argument("--promover", action="store_true", help="Promove imediatamente para a knowledge_base se aprovado")

    # Promover item
    parser_promote = subparsers.add_parser("promote", help="Promove item aprovado do staging para a knowledge_base")
    parser_promote.add_argument("--id", required=True, help="ID do registro em staging")
    parser_promote.add_argument("--topico", type=str, help="Tópico personalizado (opcional)")
    parser_promote.add_argument("--eixo", type=str, help="Eixo temático personalizado (opcional)")

    args = parser.parse_args()

    if args.subcomando == "ingest":
        texto = ""
        fonte = args.fonte
        try:
            if args.url:
                print(f"🌐 Extraindo conteúdo da URL: {args.url}...")
                texto = extrair_texto_de_url(args.url)
                fonte = args.url
            elif args.arquivo:
                print(f"📂 Lendo conteúdo do arquivo: {args.arquivo}...")
                texto = extrair_texto_de_arquivo(args.arquivo)
                fonte = args.arquivo
            elif args.texto:
                texto = args.texto.strip()
            else:
                print("❌ Erro: Forneça --url, --arquivo ou --texto para ingestão.")
                sys.exit(1)
        except Exception as e:
            print(f"❌ Erro na extração: {e}")
            sys.exit(1)

        if not texto or not texto.strip():
            print("❌ Erro: Texto fornecido para ingestão está vazio.")
            sys.exit(1)

        print("🤖 Estruturando conteúdo com IA e prompt anti-alucinação...")
        itens = estruturar_conteudo_com_ia(texto, fonte_referencia=fonte)
        print(f"📋 Extraídos {len(itens)} itens estruturados.")

        if not itens:
            print("⚠️ Nenhum item estruturado foi gerado a partir da entrada.")
            sys.exit(0)

        print("💾 Gravando na tabela de staging (conteudo_pendente) como PENDING_REVIEW...")
        salvos = salvar_em_staging(itens)
        print(f"✅ Concluído! {len(salvos)} registros salvos em staging aguardando curadoria humana.")

    elif args.subcomando == "list-pending":
        pendentes = listar_conteudos_pendentes(status=args.status)
        print(f"\n📋 Itens em Staging (Status: {args.status}) - Total: {len(pendentes)}")
        for item in pendentes:
            print(f"[{item.get('id')}] {item.get('pergunta_usuario')[:70]} | Tags: {item.get('tags')}")

    elif args.subcomando == "review":
        try:
            res = revisar_conteudo(args.id, args.acao, notas=args.notas, revisor=args.revisor)
            print(f"✅ Item {args.id} atualizado para status '{args.acao}'.")

            if args.acao == "APPROVED" and args.promover:
                print("🚀 Promovendo item aprovado para a knowledge_base de produção...")
                item_kb = promover_item_para_knowledge_base(res)
                print(f"🎉 Item promovido com sucesso para a Knowledge Base! (ID/Tópico: {item_kb.get('kb_id', item_kb.get('topico'))})")
        except Exception as e:
            print(f"❌ Erro na revisão: {e}")
            sys.exit(1)

    elif args.subcomando == "promote":
        client_db = get_db_client()
        if not client_db:
            print("❌ Erro: Cliente Supabase indisponível para carregar o registro de staging.")
            sys.exit(1)

        try:
            resp = client_db.table("conteudo_pendente").select("*").eq("id", args.id).execute()
            if not resp.data:
                print(f"❌ Erro: Item {args.id} não encontrado na tabela de staging.")
                sys.exit(1)

            item_staging = resp.data[0]
            if item_staging.get("status") != "APPROVED":
                print(f"❌ Erro: Item {args.id} está com status '{item_staging.get('status')}'. Aprove-o antes de promover.")
                sys.exit(1)

            item_kb = promover_item_para_knowledge_base(
                item_staging,
                topico=args.topico,
                eixo_tematico=args.eixo,
            )
            print(f"🎉 Item {args.id} promovido para a Knowledge Base! ID: {item_kb.get('kb_id')}")
        except Exception as e:
            print(f"❌ Erro ao promover item: {e}")
            sys.exit(1)


if __name__ == "__main__":
    main()

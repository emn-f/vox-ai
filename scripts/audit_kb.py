#!/usr/bin/env python3
"""
Script de Auditoria, Limpeza e Diagnóstico da Base de Conhecimento (Vox AI).

Implementa as fases de Engenharia e Análise de Dados:
- Fase 1 (#306): Análise Exploratória e Limpeza (Data Cleaning & Anomalias)
- Fase 2 (#307): Manipulação Vetorial para RAG (Conversão de embeddings e cálculo de similaridade por cosseno)
- Fase 3 (#308): Diagnóstico e Visualização de Conhecimento (Data Viz: eixos, tags, evolução temporal)
- Auditoria Flashcard (#331): Inspeção estruturada dos chunks da knowledge_base.

Issues resolvidas: #285, #306, #307, #308, #331
"""

from __future__ import annotations

import argparse
import ast
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd

# Adiciona o diretório raiz ao path para importar módulos internos
caminho_raiz = str(Path(__file__).resolve().parent.parent)
if caminho_raiz not in sys.path:
    sys.path.append(caminho_raiz)

try:
    from src.config import TAMANHO_VETOR_SEMANTICO, logger
    from src.core.db.client import get_db_client
except ImportError:
    import logging
    logger = logging.getLogger("audit_kb")
    TAMANHO_VETOR_SEMANTICO = 1536
    get_db_client = lambda: None


# ==============================================================================
# FASE 1: Análise Exploratória e Limpeza de Dados (Issue #306)
# ==============================================================================

def carregar_dados_kb(
    caminho_csv: Optional[str] = None,
    usar_banco: bool = False,
    dados_mock: Optional[List[Dict[str, Any]]] = None,
) -> pd.DataFrame:
    """
    Carrega os dados da base de conhecimento a partir de um arquivo CSV,
    direto do Supabase ou a partir de dados em memória.
    """
    if dados_mock is not None:
        return pd.DataFrame(dados_mock)

    if caminho_csv and os.path.exists(caminho_csv):
        df = pd.read_csv(caminho_csv)
        return df

    if usar_banco:
        client = get_db_client()
        if client:
            resp = client.table("knowledge_base").select("*").execute()
            if resp.data:
                return pd.DataFrame(resp.data)
        logger.warning("Falha ao obter dados do banco. Utilizando dataset de fallback padrão.")

    # Dataset de demonstração/fallback para testes e execuções isoladas
    registros_exemplo = [
        {
            "kb_id": "vox-kb-0000",
            "topico": "N/A",
            "eixo_tematico": "N/A",
            "descricao": "Registro temporário de placeholder",
            "referencias": None,
            "tags": [],
            "created_at": "2024-01-10T12:00:00Z",
            "embedding": None,
        },
        {
            "kb_id": "vox-kb-0001",
            "topico": "Nome Social",
            "eixo_tematico": "Direitos e Cidadania",
            "descricao": "O Decreto nº 8.727/2016 garante o uso do nome social no âmbito da administração pública federal.",
            "referencias": "Decreto nº 8.727/2016",
            "tags": ["nome social", "direitos", "decreto"],
            "created_at": "2024-02-15T10:30:00Z",
            "embedding": [0.01] * TAMANHO_VETOR_SEMANTICO,
        },
        {
            "kb_id": "vox-kb-0002",
            "topico": "Processo Transexualizador SUS",
            "eixo_tematico": "Saúde",
            "descricao": "Portaria de Consolidação nº 2/2017 define as diretrizes do processo transexualizador no SUS.",
            "referencias": "Ministério da Saúde, Portaria nº 2/2017",
            "tags": ["saude", "transicao", "sus"],
            "created_at": "2024-03-20T14:15:00Z",
            "embedding": [0.02] * TAMANHO_VETOR_SEMANTICO,
        },
        {
            "kb_id": "vox-kb-0003",
            "topico": "Acolhimento",
            "eixo_tematico": "Suporte Emocional",
            "descricao": "Curta",  # Descrição muito curta para teste
            "referencias": "",
            "tags": None,
            "created_at": "2024-04-05T09:00:00Z",
            "embedding": None,
        },
    ]
    return pd.DataFrame(registros_exemplo)


def detectar_anomalias(
    df: pd.DataFrame,
    limite_caracteres_descricao: int = 30,
    dimensoes_validas: Optional[Tuple[int, ...]] = None,
) -> pd.DataFrame:
    """
    Identifica registros anômalos na base de conhecimento:
    - Campos obrigatórios nulos ou preenchidos com placeholders ('N/A', 'none', vazio)
    - Descrições excessivamente curtas ou sem conteúdo substancial
    - Falta de tags associadas
    - Embeddings ausentes, vazios ou com dimensões inválidas
    """
    if df.empty:
        return pd.DataFrame()

    anomalias = []
    placeholders_invalidos = {"n/a", "na", "none", "null", "", "undefined"}

    for idx, row in df.iterrows():
        motivos = []
        kb_id = str(row.get("kb_id", f"idx-{idx}"))
        topico_val = row.get("topico")
        topico = str(topico_val).strip().lower() if not pd.isna(topico_val) else ""
        eixo_val = row.get("eixo_tematico")
        eixo = str(eixo_val).strip().lower() if not pd.isna(eixo_val) else ""
        desc_val = row.get("descricao")
        descricao = str(desc_val).strip() if not pd.isna(desc_val) else ""
        tags = row.get("tags")
        embedding = row.get("embedding")

        # Inconsistência de Tópico / Eixo
        if pd.isna(topico_val) or not topico or topico in placeholders_invalidos:
            motivos.append("topico_invalido_ou_placeholder")
        if pd.isna(eixo_val) or not eixo or eixo in placeholders_invalidos:
            motivos.append("eixo_invalido_ou_placeholder")

        # Inconsistência de Descrição
        if pd.isna(desc_val) or not descricao or descricao.lower() in placeholders_invalidos:
            motivos.append("descricao_invalida_ou_placeholder")
        elif len(descricao) < limite_caracteres_descricao:
            motivos.append(f"descricao_muito_curta_ou_vazia ({len(descricao)} chars)")

        # Inconsistência de Tags
        tags_vazias = False
        if tags is None or (isinstance(tags, float) and pd.isna(tags)):
            tags_vazias = True
        elif isinstance(tags, (list, np.ndarray, tuple)) and len(tags) == 0:
            tags_vazias = True
        elif isinstance(tags, str) and tags.strip().lower() in ("", "[]", "{}", "none", "null"):
            tags_vazias = True

        if tags_vazias:
            motivos.append("tags_ausentes")

        # Inconsistência de Embedding
        vetor = converter_para_vetor_numpy(embedding)
        if embedding is None or (isinstance(embedding, float) and pd.isna(embedding)):
            motivos.append("embedding_nulo")
        elif isinstance(embedding, (list, tuple, np.ndarray)) and len(embedding) == 0:
            motivos.append("embedding_nulo")
        elif isinstance(embedding, str) and embedding.strip() in ("", "[]", "{}", "null", "none"):
            motivos.append("embedding_nulo")
        elif vetor is None:
            motivos.append("embedding_corrompido")
        elif dimensoes_validas and len(vetor) not in dimensoes_validas:
            motivos.append(f"embedding_dimensao_invalida ({len(vetor)})")

        if motivos:
            anomalias.append({
                "index": idx,
                "kb_id": kb_id,
                "topico": row.get("topico"),
                "eixo_tematico": row.get("eixo_tematico"),
                "tamanho_descricao": len(descricao),
                "motivos_anomalia": "; ".join(motivos),
                "dados_completos": row.to_dict(),
            })

    return pd.DataFrame(anomalias)


def limpar_base_conhecimento(
    df: pd.DataFrame,
    substituir_na: bool = True,
    remover_sem_descricao: bool = True,
) -> pd.DataFrame:
    """
    Executa rotinas de higienização dos dados:
    - Normalização de strings e remoção de espaços em branco
    - Trata valores 'N/A' e nulos usando .fillna()
    - Converte formatos de listas/tags (arrays Postgres, JSON, listas delimitadas por vírgula)
    """
    if df.empty:
        return df.copy()

    df_limpo = df.copy()

    # Normalizar valores do placeholder 'N/A' em strings
    colunas_texto = ["topico", "eixo_tematico", "descricao", "referencias"]
    for col in colunas_texto:
        if col in df_limpo.columns:
            df_limpo[col] = df_limpo[col].replace(
                to_replace=r"(?i)^\s*(n/a|na|null|none|undefined)\s*$",
                value=np.nan,
                regex=True,
            )

    if substituir_na:
        if "topico" in df_limpo.columns:
            df_limpo["topico"] = df_limpo["topico"].fillna("Tópico Geral")
        if "eixo_tematico" in df_limpo.columns:
            df_limpo["eixo_tematico"] = df_limpo["eixo_tematico"].fillna("Geral")
        if "referencias" in df_limpo.columns:
            df_limpo["referencias"] = df_limpo["referencias"].fillna("Não especificada")

    if remover_sem_descricao and "descricao" in df_limpo.columns:
        df_limpo = df_limpo.dropna(subset=["descricao"])
        df_limpo = df_limpo[df_limpo["descricao"].astype(str).str.strip().str.len() > 0]

    # Normalizar tags para lista padronizada de strings
    if "tags" in df_limpo.columns:
        def normalizar_tags(v: Any) -> List[str]:
            if v is None or (isinstance(v, float) and pd.isna(v)):
                return []
            if isinstance(v, (list, np.ndarray, tuple)):
                return [str(t).strip().strip("'\"").lower() for t in v if str(t).strip().strip("'\"")]
            if isinstance(v, str):
                v_clean = v.strip()
                if v_clean.startswith("{") and v_clean.endswith("}"):
                    # Formato Postgres array literal: {tag1,tag2}
                    v_clean = v_clean[1:-1]
                    return [p.strip().strip("'\"").lower() for p in v_clean.split(",") if p.strip().strip("'\"")]
                if v_clean.startswith("[") and v_clean.endswith("]"):
                    try:
                        parsed = ast.literal_eval(v_clean)
                        if isinstance(parsed, list):
                            return [str(t).strip().strip("'\"").lower() for t in parsed if str(t).strip().strip("'\"")]
                    except Exception:
                        # Fallback se ast.literal_eval falhar em lista com strings sem aspas: remove colchetes
                        v_clean = v_clean[1:-1]
                        return [p.strip().strip("'\"").lower() for p in v_clean.split(",") if p.strip().strip("'\"")]
                return [p.strip().strip("'\"").lower() for p in v_clean.split(",") if p.strip().strip("'\"")]
            return []

        df_limpo["tags"] = df_limpo["tags"].apply(normalizar_tags)

    return df_limpo.reset_index(drop=True)


# ==============================================================================
# FASE 2: Manipulação Vetorial para o RAG (Issue #307)
# ==============================================================================

def converter_para_vetor_numpy(valor: Any) -> Optional[np.ndarray]:
    """
    Converte uma representação de vetor (string CSV/JSON/Postgres, lista nativa, tupla)
    em um array NumPy de float32.
    Retorna None para valores nulos, vazios ou corrompidos.
    """
    if valor is None or (isinstance(valor, float) and pd.isna(valor)):
        return None

    if isinstance(valor, np.ndarray):
        if valor.size == 0 or np.isnan(valor).any() or np.isinf(valor).any():
            return None
        return valor.astype(np.float32)

    if isinstance(valor, (list, tuple)):
        if len(valor) == 0:
            return None
        try:
            arr = np.array(valor, dtype=np.float32)
            if np.isnan(arr).any() or np.isinf(arr).any():
                return None
            return arr
        except (ValueError, TypeError):
            return None

    if isinstance(valor, str):
        v_str = valor.strip()
        if not v_str or v_str.lower() in ("null", "none", "nan", "[]", "{}"):
            return None

        # Formato Postgres array "{0.1, 0.2}"
        if v_str.startswith("{") and v_str.endswith("}"):
            try:
                conteudo = v_str[1:-1]
                valores = [float(x.strip()) for x in conteudo.split(",") if x.strip()]
                if not valores:
                    return None
                arr = np.array(valores, dtype=np.float32)
                if np.isnan(arr).any() or np.isinf(arr).any():
                    return None
                return arr
            except (ValueError, TypeError) as e:
                logger.debug(f"Falha ao decodificar array Postgres: {e}")
                return None

        # Formato string de lista "[0.123, -0.456, ...]"
        if v_str.startswith("[") and v_str.endswith("]"):
            try:
                parsed = json.loads(v_str)
                if not parsed:
                    return None
                arr = np.array(parsed, dtype=np.float32)
                if np.isnan(arr).any() or np.isinf(arr).any():
                    return None
                return arr
            except Exception:
                try:
                    conteudo = v_str[1:-1]
                    valores = [float(x.strip()) for x in conteudo.split(",") if x.strip()]
                    if not valores:
                        return None
                    arr = np.array(valores, dtype=np.float32)
                    if np.isnan(arr).any() or np.isinf(arr).any():
                        return None
                    return arr
                except Exception as e:
                    logger.debug(f"Falha ao decodificar string vetorial: {e}")
                    return None

    return None


def calcular_similaridade_cosseno(
    vetor_a: Any,
    vetor_b: Any,
) -> float:
    """
    Calcula a similaridade por cosseno entre dois vetores:
    cos_sim = (A . B) / (||A|| * ||B||)
    Retorna 0.0 se algum vetor for nulo, tiver norma zero ou contiver valores NaN/Inf.
    """
    a = converter_para_vetor_numpy(vetor_a) if not isinstance(vetor_a, np.ndarray) else vetor_a
    b = converter_para_vetor_numpy(vetor_b) if not isinstance(vetor_b, np.ndarray) else vetor_b

    if a is None or b is None:
        return 0.0

    a = np.asarray(a, dtype=np.float32)
    b = np.asarray(b, dtype=np.float32)

    if a.size == 0 or b.size == 0:
        return 0.0

    if a.shape != b.shape:
        raise ValueError(f"Dimensões incompatíveis: {a.shape} vs {b.shape}")

    if np.isnan(a).any() or np.isnan(b).any() or np.isinf(a).any() or np.isinf(b).any():
        return 0.0

    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)

    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0

    dot_product = np.dot(a, b)
    val = dot_product / (norm_a * norm_b)
    if np.isnan(val) or np.isinf(val):
        return 0.0

    similarity = float(val)
    return max(-1.0, min(1.0, similarity))


def buscar_vizinhos_similares(
    df: pd.DataFrame,
    vetor_consulta: Any,
    coluna_vetor: str = "embedding",
    top_k: int = 3,
) -> List[Dict[str, Any]]:
    """
    Busca os top_k registros mais similares na base de conhecimento
    utilizando a similaridade por cosseno vetorial.
    Suporta vetor_consulta como array numpy, lista ou string formatada.
    """
    if df.empty or vetor_consulta is None:
        return []

    q_vec = converter_para_vetor_numpy(vetor_consulta)
    if q_vec is None:
        return []

    resultados = []
    for idx, row in df.iterrows():
        vetor_row = converter_para_vetor_numpy(row.get(coluna_vetor))
        if vetor_row is None:
            continue
        try:
            score = calcular_similaridade_cosseno(q_vec, vetor_row)
            resultados.append({
                "index": idx,
                "kb_id": row.get("kb_id"),
                "topico": row.get("topico"),
                "eixo_tematico": row.get("eixo_tematico"),
                "descricao": row.get("descricao"),
                "similarity": score,
            })
        except ValueError:
            continue

    resultados.sort(key=lambda x: x["similarity"], reverse=True)
    return resultados[:top_k]


# ==============================================================================
# FASE 3: Visualização e Diagnóstico de Conhecimento (Issue #308)
# ==============================================================================

def diagnosticar_distribuicao_tematica(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula a volumetria e percentual de registros por eixo temático.
    """
    if df.empty or "eixo_tematico" not in df.columns:
        return pd.DataFrame(columns=["eixo_tematico", "quantidade", "percentual"])

    contagem = df["eixo_tematico"].fillna("Não Informado").value_counts()
    total = len(df)
    diagnostico = pd.DataFrame({
        "eixo_tematico": contagem.index,
        "quantidade": contagem.values,
        "percentual": (contagem.values / total * 100).round(2),
    })
    return diagnostico


def diagnosticar_frequencia_tags(df: pd.DataFrame, top_n: int = 15) -> pd.DataFrame:
    """
    Calcula a contagem de frequência de tags explodidas do dataset.
    """
    if df.empty or "tags" not in df.columns:
        return pd.DataFrame(columns=["tag", "frequencia"])

    todas_tags = []
    for tags in df["tags"]:
        if isinstance(tags, (list, np.ndarray, tuple)):
            todas_tags.extend([str(t).strip().strip("'\"").lower() for t in tags if str(t).strip().strip("'\"")])
        elif isinstance(tags, str):
            partes = [p.strip().strip("'\"{}[]").lower() for p in tags.split(",") if p.strip().strip("'\"{}[]")]
            todas_tags.extend(partes)

    if not todas_tags:
        return pd.DataFrame(columns=["tag", "frequencia"])

    serie_tags = pd.Series(todas_tags).value_counts().head(top_n)
    return pd.DataFrame({"tag": serie_tags.index, "frequencia": serie_tags.values})


def diagnosticar_evolucao_temporal(
    df: pd.DataFrame,
    coluna_data: Optional[str] = None,
) -> pd.DataFrame:
    """
    Calcula a evolução histórica de inserções por período (mês/ano).
    Detecta automaticamente colunas temporais comuns ('created_at', 'criado_em', 'data_referencia').
    """
    if df.empty:
        return pd.DataFrame(columns=["periodo", "novos_itens", "acumulado"])

    col_escolhida = None
    if coluna_data and coluna_data in df.columns:
        col_escolhida = coluna_data
    else:
        for candidata in ["created_at", "criado_em", "data_referencia", "data"]:
            if candidata in df.columns:
                col_escolhida = candidata
                break

    if not col_escolhida:
        return pd.DataFrame(columns=["periodo", "novos_itens", "acumulado"])

    df_temp = df.copy()
    df_temp["data_parsed"] = pd.to_datetime(df_temp[col_escolhida], errors="coerce")
    df_temp = df_temp.dropna(subset=["data_parsed"])

    if df_temp.empty:
        return pd.DataFrame(columns=["periodo", "novos_itens", "acumulado"])

    df_temp["periodo"] = df_temp["data_parsed"].dt.strftime("%Y-%m")
    agrupado = df_temp.groupby("periodo").size().reset_index(name="novos_itens")
    agrupado = agrupado.sort_values("periodo").reset_index(drop=True)
    agrupado["acumulado"] = agrupado["novos_itens"].cumsum()
    return agrupado


def gerar_grafico_barras_ascii(
    rotulos: List[str],
    valores: List[int],
    titulo: str = "Distribuição",
    largura_maxima: int = 40,
) -> str:
    """
    Gera um gráfico de barras em modo texto ASCII limpo para o terminal.
    """
    if not rotulos or not valores:
        return f"=== {titulo} ===\n(Nenhum dado disponível)"

    max_val = max(valores) if max(valores) > 0 else 1
    max_label_len = max(len(str(lbl)) for lbl in rotulos)

    linhas = [f"=== {titulo} ==="]
    for lbl, val in zip(rotulos, valores):
        tamanho_barra = int((val / max_val) * largura_maxima)
        barra = "█" * tamanho_barra
        linhas.append(f"{str(lbl):<{max_label_len}} | {barra} ({val})")

    return "\n".join(linhas)


# ==============================================================================
# AUDITORIA FLASHCARD / ESTRUTURA DE REVISÃO (Issue #331)
# ==============================================================================

class AuditoriaFlashcard:
    """
    Estrutura de inspeção e auditoria para itens da base de conhecimento (Issue #331).
    Permite auditar chunk por chunk em formato flashcard interativo ou em lote.
    """

    def __init__(self, revisor: str = "auditor_vox"):
        self.revisor = revisor
        self.historico_auditoria: List[Dict[str, Any]] = []

    def formatar_flashcard(self, item: Dict[str, Any], numero: int = 1, total: int = 1) -> str:
        """
        Renderiza um flashcard estruturado de um chunk da knowledge_base.
        Trata valores nulos do pandas e quebra linhas de descrição com bordas alinhadas.
        """
        import textwrap

        kb_id = str(item.get("kb_id") or "N/A")
        topico_val = item.get("topico")
        topico = "Não Informado" if pd.isna(topico_val) or not str(topico_val).strip() else str(topico_val).strip()
        eixo_val = item.get("eixo_tematico")
        eixo = "Não Informado" if pd.isna(eixo_val) or not str(eixo_val).strip() else str(eixo_val).strip()

        desc_val = item.get("descricao")
        descricao = "" if pd.isna(desc_val) else str(desc_val).strip()

        ref_val = item.get("referencias")
        referencias = "Nenhuma informada" if pd.isna(ref_val) or not str(ref_val).strip() else str(ref_val).strip()

        tags_val = item.get("tags")
        if tags_val is None or (isinstance(tags_val, float) and pd.isna(tags_val)):
            tags_str = "Nenhuma"
        elif isinstance(tags_val, (list, tuple, np.ndarray)):
            tags_str = ", ".join(str(t) for t in tags_val) if len(tags_val) > 0 else "Nenhuma"
        else:
            tags_str = str(tags_val) if str(tags_val).strip() not in ("", "nan", "None") else "Nenhuma"

        embedding = item.get("embedding")
        vetor = converter_para_vetor_numpy(embedding)
        tem_vetor = f"✅ Presente ({len(vetor)}d)" if vetor is not None else "❌ Ausente"

        largura_interna = 73
        linhas_desc = textwrap.wrap(descricao[:500] if len(descricao) > 500 else descricao, width=largura_interna)
        if not linhas_desc:
            linhas_desc = ["(Sem descrição informada)"]

        desc_formatada = "\n".join(f"│ {l:<{largura_interna}} │" for l in linhas_desc)

        card = f"""┌{'─' * (largura_interna + 2)}┐
│ 📇 FLASHCARD DE AUDITORIA KB [{numero}/{total}] - ID: {kb_id:<{largura_interna - 37}} │
├{'─' * (largura_interna + 2)}┤
│ 📌 Eixo Temático: {eixo[:largura_interna - 20]:<{largura_interna - 20}} │
│ 🏷️ Tópico:        {topico[:largura_interna - 20]:<{largura_interna - 20}} │
│ 🔗 Referências:   {referencias[:largura_interna - 20]:<{largura_interna - 20}} │
│ 🏷️ Tags:          {tags_str[:largura_interna - 20]:<{largura_interna - 20}} │
│ 🧠 Vetor RAG:     {tem_vetor[:largura_interna - 20]:<{largura_interna - 20}} │
├{'─' * (largura_interna + 2)}┤
│ 📄 Conteúdo do Chunk / Descrição:{' ' * (largura_interna - 33)} │
{desc_formatada}
└{'─' * (largura_interna + 2)}┘"""
        return card

    def auditar_item(
        self,
        item: Dict[str, Any],
        decisao: str,  # APPROVED, NEEDS_REVISION, REJECTED, INSPECTED
        notas: str = "",
    ) -> Dict[str, Any]:
        """
        Registra a auditoria de um item com carimbo de data/hora e parecer técnico.
        """
        from datetime import timezone
        registro = {
            "kb_id": item.get("kb_id"),
            "topico": item.get("topico"),
            "eixo_tematico": item.get("eixo_tematico"),
            "decisao": decisao,
            "notas": notas,
            "revisor": self.revisor,
            "data_auditoria": datetime.now(timezone.utc).isoformat(),
        }
        self.historico_auditoria.append(registro)
        return registro

    def exportar_auditoria(self, caminho_arquivo: str) -> None:
        """
        Salva o log de auditoria em arquivo JSON ou CSV.
        """
        if caminho_arquivo.endswith(".csv"):
            pd.DataFrame(self.historico_auditoria).to_csv(caminho_arquivo, index=False)
        else:
            with open(caminho_arquivo, "w", encoding="utf-8") as f:
                json.dump(self.historico_auditoria, f, indent=2, ensure_ascii=False)


# ==============================================================================
# PIPELINE COMPLETO DE AUDITORIA & CLI
# ==============================================================================

def executar_diagnostico_completo(
    df: pd.DataFrame,
    caminho_export_anomalias: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Executa a auditoria completa de ponta a ponta:
    1. Limpeza e detecção de anomalias
    2. Estatísticas vetoriais
    3. Diagnóstico de Data Viz (eixos, tags, datas e curva acumulada)
    """
    print("🔍 [FASE 1] Executando Análise Exploratória e Detecção de Anomalias...")
    df_anomalias = detectar_anomalias(df)
    total_anomalias = len(df_anomalias)
    print(f"   ⚠️ Foram encontradas {total_anomalias} anomalias na base.")

    if total_anomalias > 0 and caminho_export_anomalias:
        df_anomalias.to_csv(caminho_export_anomalias, index=False)
        print(f"   💾 Anomalias exportadas com sucesso para: {caminho_export_anomalias}")

    df_limpo = limpar_base_conhecimento(df)
    print(f"   ✅ Base higienizada: {len(df_limpo)} registros válidos.")

    print("\n🧠 [FASE 2] Verificando Estrutura Vetorial para RAG...")
    vetores_validos = 0
    dimensoes_encontradas = set()
    for _, row in df.iterrows():
        v = converter_para_vetor_numpy(row.get("embedding"))
        if v is not None:
            vetores_validos += 1
            dimensoes_encontradas.add(len(v))

    print(f"   📊 Registros com vetores válidos: {vetores_validos}/{len(df)}")
    if dimensoes_encontradas:
        print(f"   📐 Dimensões vetoriais detectadas: {list(dimensoes_encontradas)}")

    print("\n📊 [FASE 3] Diagnóstico de Conhecimento e Visualização...")
    df_eixos = diagnosticar_distribuicao_tematica(df_limpo)
    if not df_eixos.empty:
        chart_eixos = gerar_grafico_barras_ascii(
            rotulos=df_eixos["eixo_tematico"].tolist(),
            valores=df_eixos["quantidade"].tolist(),
            titulo="Volumetria por Eixo Temático",
        )
        print(chart_eixos)

    df_tags = diagnosticar_frequencia_tags(df_limpo, top_n=8)
    if not df_tags.empty:
        chart_tags = gerar_grafico_barras_ascii(
            rotulos=df_tags["tag"].tolist(),
            valores=df_tags["frequencia"].tolist(),
            titulo="Top 8 Tags Mais Frequentes",
        )
        print("\n" + chart_tags)

    df_datas = diagnosticar_evolucao_temporal(df)
    if not df_datas.empty:
        chart_tempo = gerar_grafico_barras_ascii(
            rotulos=df_datas["periodo"].tolist(),
            valores=df_datas["acumulado"].tolist(),
            titulo="Curva Cronológica de Inserções (Acumulado)",
        )
        print("\n" + chart_tempo)
        print("📅 Detalhamento Mensal de Inserções:")
        for _, r in df_datas.iterrows():
            print(f"   • {r['periodo']}: +{r['novos_itens']} registros (acumulado: {r['acumulado']})")

    return {
        "total_registros": len(df),
        "total_limpos": len(df_limpo),
        "total_anomalias": total_anomalias,
        "vetores_validos": vetores_validos,
        "eixos": df_eixos.to_dict(orient="records") if not df_eixos.empty else [],
        "top_tags": df_tags.to_dict(orient="records") if not df_tags.empty else [],
        "evolucao_temporal": df_datas.to_dict(orient="records") if not df_datas.empty else [],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Auditoria e Análise da Base de Conhecimento Vox AI")
    parser.add_argument("--csv", type=str, help="Caminho para arquivo CSV da base")
    parser.add_argument("--db", action="store_true", help="Buscar dados diretamente do Supabase")
    parser.add_argument("--acao", choices=["diagnostico", "limpeza", "vetores", "flashcards"], default="diagnostico")
    parser.add_argument("--export-anomalias", type=str, help="Caminho para exportar anomalias detectadas em CSV")
    parser.add_argument("--export-auditoria", type=str, help="Caminho para exportar log de auditoria flashcards")
    parser.add_argument("--interativo", action="store_true", help="Habilita modo interativo de inspeção nos flashcards")
    args = parser.parse_args()

    df = carregar_dados_kb(caminho_csv=args.csv, usar_banco=args.db)

    if args.acao == "diagnostico":
        executar_diagnostico_completo(df, caminho_export_anomalias=args.export_anomalias)

    elif args.acao == "limpeza":
        anomalias = detectar_anomalias(df)
        print(f"Anomalias detectadas ({len(anomalias)}):")
        print(anomalias[["kb_id", "motivos_anomalia"]].to_string())
        df_limpo = limpar_base_conhecimento(df)
        print(f"\nDataset limpo possui {len(df_limpo)} linhas.")

    elif args.acao == "vetores":
        print("Teste de similaridade vetorial:")
        v1 = np.ones(TAMANHO_VETOR_SEMANTICO, dtype=np.float32)
        v2 = np.ones(TAMANHO_VETOR_SEMANTICO, dtype=np.float32)
        v_rand = np.random.randn(TAMANHO_VETOR_SEMANTICO).astype(np.float32)
        sim_identica = calcular_similaridade_cosseno(v1, v2)
        sim_rand = calcular_similaridade_cosseno(v1, v_rand)
        print(f"Similaridade idêntica: {sim_identica:.4f} (esperado: 1.0000)")
        print(f"Similaridade randômica: {sim_rand:.4f}")

    elif args.acao == "flashcards":
        auditor = AuditoriaFlashcard()
        total_cards = len(df)
        print(f"Iniciando sessão de auditoria com {total_cards} flashcards...")
        for i, row in df.iterrows():
            item_dict = row.to_dict()
            card = auditor.formatar_flashcard(item_dict, numero=i+1, total=total_cards)
            print(card)
            if args.interativo:
                try:
                    escolha = input("[A]provar, [R]ejeitar, [N]ecessita revisão, [P]ular, [S]air: ").strip().upper()
                except (EOFError, KeyboardInterrupt):
                    print("\nAuditoria finalizada antecipadamente.")
                    break
                if escolha == "S":
                    break
                elif escolha == "A":
                    notas = input("Observações (opcional): ").strip()
                    auditor.auditar_item(item_dict, decisao="APPROVED", notas=notas)
                elif escolha == "R":
                    notas = input("Motivo da rejeição: ").strip()
                    auditor.auditar_item(item_dict, decisao="REJECTED", notas=notas)
                elif escolha == "N":
                    notas = input("O que precisa ser revisado: ").strip()
                    auditor.auditar_item(item_dict, decisao="NEEDS_REVISION", notas=notas)
                else:
                    print("Item pulado sem registro.")
            else:
                # Em modo lote não interativo registra automaticamente como inspecionado
                auditor.auditar_item(item_dict, decisao="INSPECTED", notas="Auditoria automatizada")

        if args.export_auditoria:
            auditor.exportar_auditoria(args.export_auditoria)
            print(f"Auditoria salva em: {args.export_auditoria}")


if __name__ == "__main__":
    main()

"""
Módulo de Execução de Benchmark do Pipeline RAG do Vox AI.

Este módulo carrega os cenários do Golden Dataset mais recente, executa a busca semântica
no Supabase (pgvector), enriquece os metadados dos chunks e gera as respostas utilizando o Gemini.
"""
import os
import glob
import json
import time
import re
from datetime import datetime
from typing import List, Dict, Tuple, Any, Optional, Callable

from src.core.semantica import semantica
from src.core.database import get_db_client
from data.prompts.system_prompt import INSTRUCOES
from scripts.modules.config import gerar_resposta_com_fallback

db: Any = get_db_client()


def buscar_detalhes_chunks_kb(chunk_ids: List[int]) -> List[Dict[str, Any]]:
    """
    Busca os detalhes enriquecidos (tópico, eixo temático e descrição) dos chunks
    na tabela 'knowledge_base' do Supabase.

    Args:
        chunk_ids (List[int]): Lista de identificadores numéricos dos chunks (kb_id).

    Returns:
        List[Dict[str, Any]]: Lista de dicionários contendo os campos da tabela knowledge_base.
    """
    if not db or not chunk_ids:
        return []
    try:
        res = db.table("knowledge_base").select("kb_id, topico, eixo_tematico, descricao").in_("kb_id", chunk_ids).execute()
        return res.data if res.data else []
    except Exception as e:
        print(f"⚠️ Erro ao buscar detalhes dos chunks no Supabase: {e}")
        return []


def carregar_dataset_mais_recente(
    data_dir: str = "/workspaces/vox-cnpq/data",
    dataset_especifico: Optional[str] = None
) -> Tuple[List[Dict[str, Any]], str, str]:
    """
    Carrega um dataset de cenários para o pipeline.

    Se `dataset_especifico` for informado (via --dataset na CLI), carrega diretamente esse arquivo.
    Caso contrário, localiza o arquivo dataset_*.json de maior versão lexicográfica em `data_dir`.

    Args:
        data_dir (str): Diretório base onde os arquivos de dataset estão armazenados.
        dataset_especifico (Optional[str]): Caminho direto para um dataset específico (opcional).

    Returns:
        Tuple[List[Dict[str, Any]], str, str]: Uma tupla contendo:
            - List[Dict[str, Any]]: Lista de cenários carregados do arquivo JSON.
            - str: Identificador de versão do dataset (ex: '1.1').
            - str: Caminho absoluto do arquivo carregado.

    Raises:
        FileNotFoundError: Se o arquivo especificado ou nenhum dataset_*.json for encontrado.
    """
    if dataset_especifico:
        input_file: str = os.path.abspath(dataset_especifico)
        if not os.path.isfile(input_file):
            raise FileNotFoundError(f"❌ Dataset especificado não encontrado: {input_file}")
        print(f"📂 Usando dataset especificado via --dataset: {input_file}")
    else:
        candidatos: List[str] = sorted(glob.glob(os.path.join(data_dir, "dataset_*.json")), reverse=True)
        if not candidatos:
            raise FileNotFoundError(f"❌ Nenhum dataset_*.json encontrado em {data_dir}")
        input_file = candidatos[0]

    match = re.search(r"dataset_(.+)\.json$", os.path.basename(input_file))
    version: str = match.group(1) if match else "1.0"

    with open(input_file, "r", encoding="utf-8") as f:
        cenarios: List[Dict[str, Any]] = json.load(f)

    print(f"✅ Dataset v{version} carregado ({len(cenarios)} cenários): {input_file}")
    return cenarios, version, input_file



def executar_benchmark_rag(
    cenarios: List[Dict[str, Any]],
    callback_salvamento: Optional[Callable[[List[Dict[str, Any]]], None]] = None
) -> List[Dict[str, Any]]:
    """
    Executa o benchmark semântico completo para todos os cenários do dataset,
    recuperando o contexto no Supabase pgvector e gerando as respostas via Gemini.

    Args:
        cenarios (List[Dict[str, Any]]): Lista de cenários com perguntas e objetivos.
        callback_salvamento (Optional[Callable[[List[Dict[str, Any]]], None]]): Função callback opcional
            invocada a cada iteração para salvamento incremental.

    Returns:
        List[Dict[str, Any]]: Lista dos resultados processados com métricas de tempo e chunks recuperados.
    """
    print(f"\n🚀 [1/4] Executando Benchmark RAG ({len(cenarios)} cenários)...")
    resultados: List[Dict[str, Any]] = []

    for idx, cenario in enumerate(cenarios, 1):
        pergunta: str = cenario['pergunta']
        print(f"\n[Cenário {idx}/{len(cenarios)} | ID: {cenario['id']}] Categoria: {cenario['categoria']}")
        print(f"  Pergunta: '{pergunta}'")

        start_time: float = time.time()

        # Busca Semântica no Supabase (pgvector)
        tema_match, descricao_match, ids_referencia = semantica(pergunta)
        estrategia: str = tema_match if tema_match else "Sem correspondência na KB"
        chunk_ids: List[int] = [item['kb_id'] for item in ids_referencia if 'kb_id' in item] if ids_referencia else []

        chunks_detalhados: List[Dict[str, Any]] = buscar_detalhes_chunks_kb(chunk_ids)
        info_adicional: str = descricao_match if descricao_match else ""

        prompt_modelo: str = pergunta
        if info_adicional:
            prompt_modelo = (
                f"Prompt do Usuário: {pergunta}\n\n"
                f"Contexto interno da sua base de conhecimento: {info_adicional}\n\n"
                f"Responda à pergunta do usuário com base no contexto fornecido."
            )

        # Geração com Fallback de Keys
        resposta_texto: str = gerar_resposta_com_fallback(prompt_modelo, sys_instruction=INSTRUCOES)
        tempo_resposta: float = time.time() - start_time

        print(f"  Estratégia RAG: {estrategia}")
        print(f"  Chunks recuperados: {len(chunk_ids)} {chunk_ids}")
        print(f"  Tempo: {tempo_resposta:.2f}s")

        item_resultado: Dict[str, Any] = {
            "id": cenario['id'],
            "categoria": cenario['categoria'],
            "pergunta": pergunta,
            "objetivo": cenario['objetivo'],
            "estrategia_rag": estrategia,
            "chunk_ids": chunk_ids,
            "chunks_knowledge_base": chunks_detalhados,
            "tempo_resposta_segundos": round(tempo_resposta, 2),
            "resposta_gerada": resposta_texto,
            "gerado_em": datetime.now().isoformat()
        }

        resultados.append(item_resultado)

        if callback_salvamento:
            callback_salvamento(resultados)

        time.sleep(1.5)

    return resultados

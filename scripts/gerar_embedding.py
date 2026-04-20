import sys
import time
from pathlib import Path

from google.genai import types

from supabase import create_client

caminho_raiz = str(Path(__file__).resolve().parent.parent)

if caminho_raiz not in sys.path:
    sys.path.append(caminho_raiz)

from src.config import (  # noqa: E402
    MODELO_SEMANTICO_NOME,
    TAMANHO_VETOR_SEMANTICO,
    get_secret,
)
from src.core.genai import configurar_api_gemini

SUPABASE_URL = get_secret("supabase.url")
SUPABASE_KEY = get_secret("supabase.key")

def reindexar() -> None:
    print("🔌 Conectando aos serviços...")
    try:
        client = configurar_api_gemini()
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        print(f"❌ Erro de conexão. Verifique suas chaves. Detalhes: {e}")
        return
    print("🔍 Buscando registros na tabela 'knowledge_base' sem embedding...")

    response = (
        supabase.table("knowledge_base")
        .select("kb_id, topico, descricao")
        .is_("embedding", "null")
        .execute()
    )
    registros = response.data

    total = len(registros)
    if total == 0:
        print("✅ Nenhum registro pendente (com embedding nulo) encontrado.")
        return

    print(f"🚀 Encontrados {total} registros para reindexar.")
    print("🧠 Usando modelo: gemini-embedding-001 (1536 dimensões)")
    print("-" * 50)

    sucessos = 0
    erros = 0

    for i, row in enumerate(registros):
        kb_id = row['kb_id']
        descricao = row.get('descricao', '') or ''

        texto_para_embeddar = f"{descricao}"

        try:
            print(f"[{i+1}/{total}] Processando {kb_id}...", end=" ")

            result = client.models.embed_content(
                model=MODELO_SEMANTICO_NOME,
                contents=texto_para_embeddar,
                config=types.EmbedContentConfig(
                    task_type="RETRIEVAL_DOCUMENT",
                    output_dimensionality=TAMANHO_VETOR_SEMANTICO,
                ),
            )
            vetor = result.embeddings[0].values

            data_update = {"embedding": vetor}

            # Preenche o campo 'embedding' apenas se ele for nulo, para evitar sobrescrever embeddings existentes
            supabase.table('knowledge_base').update(data_update).eq('kb_id', kb_id).is_('embedding', 'null').execute()

            print("✅ Salvo")
            sucessos += 1

            time.sleep(0.5)

        except Exception as e:
            print(f"\n❌ ERRO no ID {kb_id}: {e}")
            erros += 1

    print("-" * 50)
    print("🏁 Processo finalizado!")
    print(f"✅ Sucessos: {sucessos}")
    print(f"❌ Falhas: {erros}")

if __name__ == "__main__":
    reindexar()

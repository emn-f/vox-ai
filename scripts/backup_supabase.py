#!/usr/bin/env python3
"""
Script de Backup do Supabase (Vox AI).

Exporta os dados das tabelas essenciais para arquivos JSON estruturados:
- knowledge_base
- sessions
- error_logs
- user_reports
- report_categories

Pode ser executado localmente via linha de comando ou automaticamente via GitHub Actions.
"""
import argparse
import datetime
import gzip
import json
import os
import sys
from pathlib import Path

# Ajustar PYTHONPATH para permitir importação de src
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from src.core.db.client import get_db_client
from src.config import logger

TABELAS_BACKUP = [
    "knowledge_base",
    "report_categories",
    "sessions",
    "error_logs",
    "user_reports",
]


def realizar_backup(output_dir: str = "backups", compress: bool = True) -> bool:
    """
    Realiza o backup das tabelas configuradas no Supabase.

    Args:
        output_dir: Diretório onde o backup será salvo.
        compress: Se True, compacta os arquivos em formato .json.gz.

    Returns:
        bool: True se o backup concluiu com sucesso, False caso contrário.
    """
    client = get_db_client()
    if not client:
        logger.error("❌ Não foi possível inicializar o cliente Supabase. Verifique as credenciais.")
        return False

    timestamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d_%H%M%S")
    target_path = Path(output_dir) / f"backup_{timestamp}"
    target_path.mkdir(parents=True, exist_ok=True)

    manifest = {
        "timestamp_utc": timestamp,
        "tables": {},
        "status": "success",
    }

    print(f"📦 Iniciando rotina de backup em: {target_path}")

    for tabela in TABELAS_BACKUP:
        try:
            print(f"  ⏳ Coletando dados da tabela: {tabela}...")
            # Coleta paginada simples para suportar tabelas grandes
            registros = []
            page_size = 1000
            offset = 0

            while True:
                response = client.table(tabela).select("*").range(offset, offset + page_size - 1).execute()
                batch = response.data or []
                registros.extend(batch)
                if len(batch) < page_size:
                    break
                offset += page_size

            total_registros = len(registros)
            print(f"  ✅ {tabela}: {total_registros} registros coletados.")

            if compress:
                file_name = f"{tabela}.json.gz"
                file_path = target_path / file_name
                with gzip.open(file_path, "wt", encoding="utf-8") as f:
                    json.dump(registros, f, ensure_ascii=False, indent=2, default=str)
            else:
                file_name = f"{tabela}.json"
                file_path = target_path / file_name
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(registros, f, ensure_ascii=False, indent=2, default=str)

            manifest["tables"][tabela] = {
                "records_count": total_registros,
                "file": file_name,
            }

        except Exception as e:
            logger.error(f"❌ Erro ao exportar tabela {tabela}: {e}")
            manifest["tables"][tabela] = {
                "records_count": 0,
                "error": str(e),
            }
            manifest["status"] = "partial_failure"

    # Salva o manifesto com resumo
    manifest_path = target_path / "manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    print(f"🎉 Backup finalizado com status: {manifest['status']}. Manifesto: {manifest_path}")
    return manifest["status"] == "success"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Backup de tabelas do Supabase (Vox AI)")
    parser.add_argument("--output-dir", default="backups", help="Diretório destino dos arquivos de backup")
    parser.add_argument("--no-compress", action="store_true", help="Salvar JSON sem compactação gzip")
    args = parser.parse_args()

    sucesso = realizar_backup(output_dir=args.output_dir, compress=not args.no_compress)
    sys.exit(0 if sucesso else 1)

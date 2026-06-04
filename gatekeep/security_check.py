import argparse
import sys
import os

# Adiciona o diretório raiz ao path para as importações do pacote gatekeep
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from gatekeep.colors import print_colored, COLOR_BLUE
from gatekeep.git_utils import get_git_files, get_git_diff_content
from gatekeep.secrets_check import check_secrets_in_files
from gatekeep.db_check import check_database_migrations
from gatekeep.ai_review import run_ai_code_review, sanitize_diff_for_ai, log_ai_event
from gatekeep.config_loader import load_secrets

def main():
    parser = argparse.ArgumentParser(description="Vox AI Security & Code Review Tool")
    parser.add_argument("--mode", choices=["pre-commit", "pre-push"], required=True)
    args = parser.parse_args()

    print_colored(f"\n🛡️ [Project Vox AI - Security] Mode: {args.mode}", COLOR_BLUE)

    # 1. Obter arquivos modificados
    files = get_git_files(args.mode)
    if not files:
        print("Nenhuma alteração detectada para verificar.")
        sys.exit(0)

    # 2. Verificação de Segredos (Executa em AMBOS os modos)
    if not check_secrets_in_files(files):
        sys.exit(1)

    # 3. Verificação de Migrations (Consistência DB)
    if not check_database_migrations(files, args.mode):
        sys.exit(1)

    # 4. Verificações Avançadas (Apenas PRE-PUSH)
    if args.mode == "pre-push":
        # Code Review IA
        full_diff = get_git_diff_content(args.mode)
        if full_diff:
            if not run_ai_code_review(full_diff):
                sys.exit(1)

    sys.exit(0)

if __name__ == "__main__":
    main()

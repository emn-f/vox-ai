import sys
import os
import re

# Adiciona a raiz do projeto ao sys.path para permitir importações do pacote gatekeep
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from gatekeep.utils.ui import print_colored, COLOR_RED, COLOR_GREEN, COLOR_YELLOW

# Regex para Conventional Commits
# Formato: tipo(escopo?): descrição
# Ex: feat: adiciona login
# Ex: fix(ui): corrige botão
# Tipos: feat, fix, docs, style, refactor, perf, test, build, ci, chore, revert
CONVENTIONAL_COMMIT_REGEX = (
    r"^(feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)(\(.+\))?!?: .+$"
)

def validate_commit_msg(msg_path):
    try:
        with open(msg_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            # A primeira linha é o "subject" do commit
            subject = lines[0].strip()

            # Pula validação para merges e reverts automáticos
            if subject.startswith("Merge") or subject.startswith("Revert"):
                return True

            if not re.match(CONVENTIONAL_COMMIT_REGEX, subject):
                print_colored(
                    "❌ Erro: Mensagem de commit fora do padrão Conventional Commits.",
                    COLOR_RED,
                )
                print_colored(f"   Mensagem atual: '{subject}'", COLOR_YELLOW)
                print_colored(
                    "   Formato esperado: <tipo>(<escopo opcional>): <descrição>",
                    COLOR_GREEN,
                )
                print_colored(
                    "   Consulte CONVENTIONAL_COMMITS.md para mais detalhes.\n",
                    COLOR_YELLOW,
                )
                return False

            return True

    except Exception as e:
        print(f"⚠️ Erro ao validar mensagem: {e}")
        return True  # Falha aberta para não bloquear em caso de erro de script


if __name__ == "__main__":
    # O git passa o caminho do arquivo temporário com a mensagem como 1º argumento
    if len(sys.argv) < 2:
        print("Uso: python validate_commit_msg.py <caminho_msg>")
        sys.exit(1)

    msg_file = sys.argv[1]
    if not validate_commit_msg(msg_file):
        sys.exit(1)

    sys.exit(0)

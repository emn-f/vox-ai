import sys
import re

# Regex para Conventional Commits
# Formato: tipo(escopo?): descrição
# Ex: feat: adiciona login
# Ex: fix(ui): corrige botão
# Tipos: feat, fix, docs, style, refactor, perf, test, build, ci, chore, revert
CONVENTIONAL_COMMIT_REGEX = (
    r"^(feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)(\(.+\))?!?: .+$"
)

COLOR_RED = "\033[91m"
COLOR_GREEN = "\033[92m"
COLOR_YELLOW = "\033[93m"
COLOR_RESET = "\033[0m"


def print_colored(msg, color=COLOR_RESET):
    if sys.stdout.isatty():
        print(f"{color}{msg}{COLOR_RESET}")
    else:
        print(msg)


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

import os
import sys
import stat


def generate_hook_script(hook_name):
    """Gera o script shell do hook de forma dinâmica."""

    # Script Shell cross-platform (Git Bash / Unix)
    # Tenta usar o python do venv local se existir, senão usa o python do PATH.
    # Isso torna o hook portável para outros devs que clonarem o repo.
    script = f"""#!/bin/sh
# Vox AI Git Hook: {hook_name}

# Cores
RED='\\033[0;31m'
NC='\\033[0m' # No Color

echo "running {hook_name} hook..."

# Define o caminho do script python relativo à raiz do git
SCRIPT_PATH="scripts/security_check.py"

# Verifica se estamos na raiz (onde scripts/ existe)
if [ ! -f "$SCRIPT_PATH" ]; then
    echo -e "${{RED}}❌ Erro: Não foi possível encontrar $SCRIPT_PATH. Execute o git da raiz do projeto.${{NC}}"
    exit 1
fi

# Tenta encontrar o Python correto
if [ -f ".venv/Scripts/python.exe" ]; then
    PYTHON_CMD=".venv/Scripts/python.exe"
elif [ -f ".venv/bin/python" ]; then
    PYTHON_CMD=".venv/bin/python"
elif [ -f "venv/Scripts/python.exe" ]; then
    PYTHON_CMD="venv/Scripts/python.exe"
elif [ -f "venv/bin/python" ]; then
    PYTHON_CMD="venv/bin/python"
else
    # Fallback para o python do sistema
    PYTHON_CMD="python"
fi

# Executa o script
"$PYTHON_CMD" "$SCRIPT_PATH" --mode {hook_name}
EXIT_CODE=$?

if [ $EXIT_CODE -ne 0 ]; then
    echo -e "${{RED}}❌ {hook_name} falhou. Ação abortada.${{NC}}"
    exit 1
fi

exit 0
"""
    return script


def install_hooks():
    print("🔧 Instalando Git Hooks (V2 - Portável)...")

    hooks_dir = os.path.join(".git", "hooks")
    if not os.path.exists(hooks_dir):
        print(
            f"❌ Diretório .git/hooks não encontrado. Certifique-se de estar na raiz de um repositório git."
        )
        return

    hooks_to_install = ["pre-commit", "pre-push"]

    for hook in hooks_to_install:
        content = generate_hook_script(hook)
        dest_path = os.path.join(hooks_dir, hook)

        try:
            with open(dest_path, "w", newline="\n") as f:
                f.write(content)

            # Tenta dar permissão de execução
            st = os.stat(dest_path)
            os.chmod(dest_path, st.st_mode | stat.S_IEXEC)
            print(f"✅ Hook '{hook}' atualizado em {dest_path}")

        except Exception as e:
            print(f"❌ Erro ao escrever {hook}: {e}")


if __name__ == "__main__":
    install_hooks()

import os
import sys
import stat


def get_python_path():
    """Retorna o caminho absoluto do Python a ser usado nos hooks."""
    base_dir = os.getcwd()

    # 1. Tentar localizar o venv padrão do projeto
    venv_python = os.path.join(base_dir, ".venv", "Scripts", "python.exe")
    if os.path.exists(venv_python):
        return venv_python.replace("\\", "/")

    # 2. Se não, usar o sys.executable atual (assumindo que o usuário rodou o install com o python correto)
    # Mas precisamos garantir que seja o python.exe e não um wrapper estranho
    exe = sys.executable.replace("\\", "/")
    return exe


def install_hooks():
    python_exe = get_python_path()
    print(f"🔧 Configurando hooks usando Python: {python_exe}")

    hooks_dir = os.path.join(".git", "hooks")
    if not os.path.exists(hooks_dir):
        # Tenta criar se não existir (raro em repo git válido)
        try:
            os.makedirs(hooks_dir)
        except:
            print(f"❌ Diretório {hooks_dir} não encontrado. Execute na raiz do repo.")
            return

    # Definir conteúdo dos scripts
    # Usamos aspas no caminho do python para lidar com espaços (Ex: Program Files)

    # PRE-COMMIT
    pre_commit_content = f"""#!/bin/sh
echo "🔒 [Vox AI] Verificação pré-commit..."
"{python_exe}" scripts/security_check.py --mode pre-commit
if [ $? -ne 0 ]; then
    echo "❌ Verificação falhou. Commit abortado."
    exit 1
fi
"""

    # PRE-PUSH
    pre_push_content = f"""#!/bin/sh
echo "🚀 [Vox AI] Verificação pré-push..."
"{python_exe}" scripts/security_check.py --mode pre-push
if [ $? -ne 0 ]; then
    echo "❌ Verificação falhou. Push abortado."
    exit 1
fi
"""

    # Escrever arquivos
    pc_path = os.path.join(hooks_dir, "pre-commit")
    with open(
        pc_path, "w", newline="\n"
    ) as f:  # newline='\n' para garantir LF (unix style) essencial para git hooks
        f.write(pre_commit_content)

    pp_path = os.path.join(hooks_dir, "pre-push")
    with open(pp_path, "w", newline="\n") as f:
        f.write(pre_push_content)

    # Permissões (Ignorado no Windows nativo, mas útil se usando WSL/Cygwin)
    try:
        st = os.stat(pc_path)
        os.chmod(pc_path, st.st_mode | stat.S_IEXEC)
        st = os.stat(pp_path)
        os.chmod(pp_path, st.st_mode | stat.S_IEXEC)
    except:
        pass

    print(f"✅ Hooks instalados: \n   - {pc_path}\n   - {pp_path}")


if __name__ == "__main__":
    install_hooks()

import subprocess
from typing import List

def get_git_metadata() -> dict:
    """
    Executa comandos do Git via subprocess para obter informações do HEAD ativo 
    (hash curto, branch ativa, última tag e mensagem de commit) para logs.

    Returns:
        dict: Dicionário contendo metadados de hash, branch, version e message.
    """
    try:
        commit_hash = (
            subprocess.check_output(["git", "rev-parse", "--short", "HEAD"])
            .decode()
            .strip()
        )
        branch = (
            subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"])
            .decode()
            .strip()
        )

        version = (
                subprocess.check_output(["git", "describe", "--tags", "--abbrev=0"])
                .decode()
                .strip()
            )
        
        try:
            msg = (
                subprocess.check_output(["git", "log", "-1", "--pretty=%B"])
                .decode()
                .strip()
            )
        except Exception:
            msg = "No Message"

        return {
            "hash": commit_hash,
            "branch": branch,
            "version": version,
            "message": msg,
        }
    except Exception:
        return {
            "hash": "Unknown",
            "branch": "Unknown",
            "version": "Unknown",
            "message": "Unknown",
        }

def get_git_files(mode: str) -> List[str]:
    """
    Executa comando 'git diff' para mapear a lista de arquivos alterados/modificados.

    Args:
        mode (str): O modo do hook ('pre-commit' verifica staged, 'pre-push' verifica commits locais).

    Returns:
        List[str]: Uma lista com caminhos relativos dos arquivos modificados.
    """
    cmd = []
    if mode == "pre-commit":
        cmd = ["git", "diff", "--name-only", "--cached"]
    elif mode == "pre-push":
        cmd = ["git", "diff", "--name-only", "origin/main..HEAD"]

    try:
        output = subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode()
        return [f.strip() for f in output.splitlines() if f.strip()]
    except subprocess.CalledProcessError:
        try:
            return (
                subprocess.check_output(["git", "diff", "--name-only", "--cached"])
                .decode()
                .splitlines()
            )
        except Exception:
            return []

def get_git_diff_content(mode: str) -> str:
    """
    Gera o texto completo do git diff correspondente às modificações atuais.

    Args:
        mode (str): O modo do hook ('pre-commit' ou 'pre-push').

    Returns:
        str: Texto completo formatado do diff git.
    """
    cmd = []
    if mode == "pre-commit":
        cmd = ["git", "diff", "--cached"]
    elif mode == "pre-push":
        cmd = ["git", "diff", "origin/main..HEAD"]

    try:
        return subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode()
    except Exception:
        return ""

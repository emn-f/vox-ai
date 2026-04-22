import subprocess
from typing import List

def get_git_metadata():
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

        try:
            version = (
                subprocess.check_output(["git", "describe", "--tags", "--abbrev=0"])
                .decode()
                .strip()
            )
        except Exception:
            version = "No Tag"

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
    """Retorna lista de nomes de arquivos modificados."""
    cmd = []
    if mode == "pre-commit":
        cmd = ["git", "diff", "--name-only", "--cached"]
    else:  # pre-push
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
    """Retorna o conteúdo do diff."""
    cmd = []
    if mode == "pre-commit":
        cmd = ["git", "diff", "--cached"]
    else:
        cmd = ["git", "diff", "origin/main..HEAD"]

    try:
        return subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode()
    except Exception:
        return ""

import datetime
import os
import shutil
import subprocess
import sys
from gatekeep.utils.git import get_git_metadata
from gatekeep.utils.ui import print_colored, COLOR_YELLOW

def log_ai_event(event_type: str, ai_response: str):
    """Registra eventos da IA no log e tenta abrir o arquivo em caso de bloqueio."""
    log_file = "ai_gatekeeper.log"
    meta = get_git_metadata()
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    entry = f"""
=============================================================================
TIMESTAMP: {now}
EVENT: {event_type}
VERSION: {meta['version']}
BRANCH: {meta['branch']}
COMMIT (HEAD): {meta['hash']}
MESSAGE: {meta['message']}

CODE REVIEWER FEEDBACK (Gemini):
{ai_response.strip()}
=============================================================================
"""
    try:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(entry)

        if "BLOCK" in event_type:
            _open_log_file(log_file)
    except Exception as e:
        print_colored(f"⚠️ Falha ao gravar log: {e}", COLOR_YELLOW)

def _open_log_file(log_file: str):
    """Tenta abrir o log no editor padrão ou VS Code/Notepad++."""
    try:
        if shutil.which("notepad++"):
            subprocess.Popen(["notepad++", log_file])
        elif shutil.which("code"):
            subprocess.Popen(["code", "-g", log_file])
        elif sys.platform == "win32":
            os.startfile(log_file)
        else:
            subprocess.Popen(["xdg-open", log_file])
    except Exception:
        pass  # Falha silenciosa se não conseguir abrir

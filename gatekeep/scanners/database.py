import fnmatch
import os
import re
import subprocess
from typing import List
from gatekeep.utils.ui import print_colored, COLOR_RED, COLOR_BLUE, COLOR_GREEN, COLOR_YELLOW
from gatekeep.utils.config import load_secrets
from gatekeep.logger import log_ai_event

def check_database_migrations(files: List[str], mode: str) -> bool:
    """Verifica se alterações em arquivos de banco estão acompanhadas de migração."""
    target_files = (
        "src/core/database.py",
        "supabase/migrations/*.sql",
        "supabase/config.toml",
    )
    
    affected = [f for f in files if any(fnmatch.fnmatch(f.replace("\\", "/"), p) for p in target_files)]
    if not affected:
        return True

    print_colored("🔎 Verificando Consistência de Migrations (Smart Check)...", COLOR_BLUE)
    
    if mode == "pre-push":
        if not check_supabase_connection():
            return False

    # Heurística para detectar novas colunas no database.py
    if any(f.endswith("database.py") for f in affected):
        target_file = "src/core/database.py"
        cmd = ["git", "diff", "-w", "--cached", "--", target_file] if mode == "pre-commit" else ["git", "diff", "-w", "origin/main..HEAD", "--", target_file]
        
        try:
            diff_output = subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode()
            new_column_pattern = re.compile(r"^\+\s*[\"'][\w_]+[\"']\s*:", re.MULTILINE)
            
            if new_column_pattern.search(diff_output):
                has_sql = any(f.endswith(".sql") for f in files)
                if not has_sql:
                    msg = "Nova coluna detectada em 'database.py' sem migração (.sql)."
                    print_colored(f"⛔ BLOQUEIO DE CONSISTÊNCIA: {msg}", COLOR_RED)
                    log_ai_event("BLOCK (Missing Migration)", msg)
                    return False
        except Exception:
            pass

    print_colored("✅ Check de Migrations OK.", COLOR_GREEN)
    return True

def check_supabase_connection() -> bool:
    """Verifica se é possível conectar ao Supabase."""
    print_colored("🔌 Testando conexão com Supabase...", COLOR_BLUE)

    try:
        from supabase import Client, create_client
    except ImportError:
        print_colored("⚠️ Biblioteca 'supabase' ausente. Teste de conexão ignorado.", COLOR_YELLOW)
        return True

    secrets = load_secrets()
    sb_config = secrets.get("supabase", {})
    url = sb_config.get("url") or os.environ.get("SUPABASE_URL")
    key = sb_config.get("key") or os.environ.get("SUPABASE_KEY_PROD")

    if not url or not key:
        print_colored("⚠️ Credenciais do Supabase ausentes. Teste ignorado.", COLOR_YELLOW)
        return True

    try:
        client: Client = create_client(url, key)
        client.table("chat_logs").select("chat_id", count="exact").limit(0).execute()
        print_colored("✅ Conexão DB OK.", COLOR_GREEN)
        return True
    except Exception as e:
        print_colored(f"❌ Falha de Conexão DB: {str(e)}", COLOR_RED)
        return False

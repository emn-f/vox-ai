import os
import re
import fnmatch
import subprocess
from typing import List
from gatekeep.colors import print_colored, COLOR_BLUE, COLOR_GREEN, COLOR_RED, COLOR_YELLOW
from gatekeep.config_loader import load_secrets

def check_supabase_connection() -> bool:
    """
    Testa de forma síncrona a conectividade com a API de banco do Supabase,
    executando uma chamada trivial na tabela 'chat_logs'.

    Returns:
        bool: True se a conexão obteve sucesso ou se o teste foi ignorado (sem chaves),
              False se a conexão falhou explicitamente.
    """
    print_colored("🔌 Testando conexão com Supabase...", COLOR_BLUE)

    try:
        from supabase import Client, create_client
    except ImportError:
        print_colored(
            "⚠️ Biblioteca 'supabase' ausente. Teste de conexão ignorado.", COLOR_YELLOW
        )
        return True

    secrets = load_secrets()
    sb_config = secrets.get("supabase", {})
    url = sb_config.get("url") or os.environ.get("SUPABASE_URL")
    key = sb_config.get("key") or os.environ.get("SUPABASE_KEY_PROD")

    if not url or not key:
        print_colored(
            "⚠️ Credenciais do Supabase ausentes (secrets.toml ou ENV). "
            "Teste de conexão ignorado (contexto sem credenciais, ex: fork PR).",
            COLOR_YELLOW,
        )
        return True

    try:
        client: Client = create_client(url, key)
        client.table("chat_logs").select("chat_id", count="exact").limit(0).execute()
        print_colored("✅ Conexão DB OK.", COLOR_GREEN)
        return True
    except Exception as e:
        print_colored(f"❌ Falha de Conexão DB: {str(e)}", COLOR_RED)
        return False

def check_database_migrations(files: List[str], mode: str) -> bool:
    """
    Verifica se alterações nos arquivos chave de banco de dados de produção do projeto
    (como queries e mapeamentos em database.py) vieram acompanhadas da respectiva migração SQL (.sql).
    Bloqueia commits que adicionam colunas ou tabelas sem o arquivo de migração.

    Args:
        files (List[str]): Lista de arquivos modificados obtida do git log/diff.
        mode (str): Modo de execução do hook (ex: 'pre-commit', 'pre-push').

    Returns:
        bool: True se o commit estiver consistente, False se houver alteração de banco sem SQL.
    """
    from gatekeep.ai_review import log_ai_event

    target_files = [
        "src/core/database.py",
        "supabase/migrations/*.sql",
        "supabase/config.toml",
    ]
    if not any(
        fnmatch.fnmatch(f.replace("\\", "/"), pattern)
        for f in files
        for pattern in target_files
    ):
        return True

    print_colored(
        "🔎 Verificando Consistência de Migrations (Smart Check)...", COLOR_BLUE
    )
    if mode == "pre-push":
        if not check_supabase_connection():
            return False

    cmd = []
    if mode == "pre-commit":
        cmd = ["git", "diff", "-w", "--cached", "--"] + target_files
    else:
        cmd = ["git", "diff", "-w", "origin/main..HEAD", "--"] + target_files

    try:
        diff_output = subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode()
    except Exception:
        return True

    new_column_pattern = re.compile(r"^\+\s*[\"'][\w_]+[\"']\s*:", re.MULTILINE)
    potential_schema_change = False
    if new_column_pattern.search(diff_output):
        potential_schema_change = True

    if not potential_schema_change:
        print_colored(
            "✅ Alteração em database.py detectada, mas parece segura (sem novas colunas).",
            COLOR_GREEN,
        )
        return True

    has_sql = any(f.endswith(".sql") for f in files)

    if not has_sql:
        msg = "Nova coluna detectada em 'database.py' sem migração (.sql)."
        print_colored(
            f"⛔ BLOQUEIO DE CONSISTÊNCIA: {msg}",
            COLOR_RED,
        )
        print_colored(
            "   O sistema detectou uma adição de campo (ex: 'chave': valor) no código,\n"
            "   mas nenhum arquivo .sql foi encontrado no commit.\n"
            "   - Por favor, gere o script de migração do Supabase.\n"
            "   - Se for um falso positivo, use 'git commit --no-verify'.",
            COLOR_YELLOW,
        )
        log_ai_event("BLOCK (Missing Migration)", msg)
        return False

    print_colored(
        "✅ Check de Migrations OK (Schema Change + .sql encontrado).", COLOR_GREEN
    )
    return True

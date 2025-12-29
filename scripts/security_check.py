import os
import sys
import re
import argparse
import subprocess
from typing import List, Optional, Any

# =============================================================================
# CONFIGURAÇÃO DE IMPORTS (TOML)
# =============================================================================
# Tenta importar bibliotecas TOML com fallback elegante.
# Prioridade: tomllib (Py 3.11+ stdlib) -> tomli (Moderno) -> toml (Legado)
try:
    import tomllib as toml
except ImportError:
    try:
        import tomli as toml
    except ImportError:
        try:
            import toml
        except ImportError:
            toml = None

# =============================================================================
# CONSTANTES E CONFIGURAÇÕES
# =============================================================================

# =============================================================================
# CONSTANTES E CONFIGURAÇÕES
# =============================================================================

# Constantes de Cores para Terminal
COLOR_RED = "\033[91m"
COLOR_GREEN = "\033[92m"
COLOR_YELLOW = "\033[93m"
COLOR_BLUE = "\033[94m"
COLOR_RESET = "\033[0m"


def print_colored(msg: str, color: str = COLOR_RESET):
    """Imprime mensagem colorida se o terminal suportar."""
    if sys.stdout.isatty():
        print(f"{color}{msg}{COLOR_RESET}")
    else:
        print(msg)


# Configuração da IA (Google Gemini)
# Modelo: gemini-2.5-flash (Mais recente detectado)
# Limite máximo de caracteres para envio à IA
SECRETS_PATTERNS = [
    (r"sk-[a-zA-Z0-9]{48}", "OpenAI API Key"),
    (r"ghp_[a-zA-Z0-9]{36}", "GitHub Personal Access Token"),
    (r"xox[baprs]-([0-9a-zA-Z]{10,48})?", "Slack Token"),
    (r"-----BEGIN PRIVATE KEY-----", "Generic Private Key"),
    (r"AIza[0-9A-Za-z-_]{35}", "Google API Key"),
    (r"\bey[A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.?[A-Za-z0-9-_.+/=]*", "Potential JWT/Token"),
    (
        r"(?i)(?:key|secret|password|token|auth|credential|jwt)\w*\s*=\s*['\"](?!__)[\w\-@\.]{24,}['\"]",
        "Generic High-Entropy Assignment",
    ),
]

# Palavras-chave que, se a IA mencionar, bloqueiam o push.
# Palavras-chave específicas que indicam problemas reais.
# Removemos termos genéricos para evitar falsos positivos quando a IA diz "Não foi encontrada vulnerabilidade crítica".
BLOCK_KEYWORDS = [
    "password exposed",
    "senha exposta",
    "sql injection",
    "remote code execution",
    "xss",
    "[block]",
    "rce",
    "exposed secret",
    "chave exposta",
]

# ...


def load_secrets() -> dict:
    """Carrega segredos do arquivo .streamlit/secrets.toml de forma segura."""
    secrets_path = os.path.join(os.getcwd(), ".streamlit", "secrets.toml")

    if not os.path.exists(secrets_path):
        return {}

    data = {}
    if not toml:
        # Tenta carregar mesmo sem biblioteca TOML via parseamento manual simples para chaves criticas
        # Mas idealmente avisa
        print_colored(
            "⚠️ Aviso: Nenhuma biblioteca TOML (tomllib/tomli) encontrada.", COLOR_YELLOW
        )

    try:
        # Tenta abrir como binário primeiro (tomllib/tomli)
        with open(secrets_path, "rb") as f:
            if toml and hasattr(toml, "load"):
                data = toml.load(f)
            else:
                raise ImportError("TOML lib falhou ou ausente")
    except Exception:
        # Fallback: Tenta ler como texto ou parse manual básico
        try:
            with open(secrets_path, "r", encoding="utf-8") as f:
                if toml:
                    data = toml.load(f)
                else:
                    # Parse manual de emergência para recuperar chaves simples
                    content = f.read()
                    for line in content.splitlines():
                        if "=" in line:
                            k, v = line.split("=", 1)
                            data[k.strip()] = v.strip().strip('"').strip("'")
        except Exception as e:
            print_colored(f"⚠️ Erro ao ler secrets.toml: {e}", COLOR_YELLOW)
            pass  # Segue vazio, mas avisou

    # Ajuste crítico: mapeia HF_TOKEN da raiz para dentro da estrutura esperada
    if "HF_TOKEN" in data:
        if "huggingface" not in data:
            data["huggingface"] = {}
        data["huggingface"]["token"] = data["HF_TOKEN"]

    return data


# =============================================================================
# CHECAGENS DE SEGURANÇA
# =============================================================================


def check_secrets_in_files(files: List[str]) -> bool:
    """Varre arquivos em busca de padrões de segredos."""
    print_colored("🔒 Iniciando verificação de segredos...", COLOR_BLUE)
    found_secrets = False

    # Caminho absoluto deste script para evitar auto-detecção
    current_script = os.path.abspath(__file__)

    for file_path in files:
        abs_path = os.path.abspath(file_path)

        if not os.path.exists(abs_path):
            continue

        # Pula o próprio script
        if abs_path == current_script:
            continue

        # Verificação rápida de tamanho (evita ler arquivos de bloqueio gigantes)
        try:
            if os.path.getsize(abs_path) > 1024 * 1024:  # > 1MB
                continue

            # Ler apenas como texto
            with open(abs_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            for pattern, name in SECRETS_PATTERNS:
                if re.search(pattern, content):
                    print_colored(
                        f"❌ ALERTA DE SEGURANÇA: {name} detectado em '{file_path}'",
                        COLOR_RED,
                    )
                    found_secrets = True

        except Exception:
            pass

    if found_secrets:
        print_colored(
            "⛔ Bloqueio: Segredos detectados no código. Remova-os antes de commitar.",
            COLOR_RED,
        )
        return False

    print_colored("✅ Nenhum segredo detectado.", COLOR_GREEN)
    return True


def check_database_migrations(files: List[str], mode: str) -> bool:
    """
    Verifica se alterações em arquivos chave de banco de dados (ex: database.py)
    estão acompanhadas de um arquivo de migração (.sql).
    Agora com heurística: Só trava se detectar adição de chaves em dicionários (novas colunas).
    """
    # 1. Filtra se database.py foi alterado
    target_file = "src/core/database.py"
    if not any(f.replace("\\", "/").endswith(target_file) for f in files):
        return True

    print_colored(
        "🔎 Verificando Consistência de Migrations (Smart Check)...", COLOR_BLUE
    )

    # 2. Obtém o diff ignorando espaços em branco (-w) para evitar falsos positivos de formatação
    cmd = []
    if mode == "pre-commit":
        cmd = ["git", "diff", "-w", "--cached", "--", target_file]
    else:
        # Pre-push
        cmd = ["git", "diff", "-w", "origin/master..HEAD", "--", target_file]

    try:
        # O diff pode falhar se o arquivo for novo ou deletado, mas tratamos com try
        diff_output = subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode()
    except Exception:
        return True

    # 3. Analisa se há adição de chaves de dicionário (ex: "coluna": valor)
    # Regex: Linha começando com +, espaço opcional, aspas, palavra, aspas, dois pontos
    # Exemplo match: + "comment": comment,
    new_column_pattern = re.compile(r"^\+\s*[\"'][\w_]+[\"']\s*:", re.MULTILINE)

    potential_schema_change = False
    if new_column_pattern.search(diff_output):
        potential_schema_change = True

    if not potential_schema_change:
        # Se mudou o arquivo mas não achou padrão de nova coluna, deixa passar (ex: log, refatoração)
        print_colored(
            "✅ Alteração em database.py detectada, mas parece segura (sem novas colunas).",
            COLOR_GREEN,
        )
        return True

    # 4. Se detectou mudança de schema, exige .sql
    has_sql = any(f.endswith(".sql") for f in files)

    if not has_sql:
        print_colored(
            "⛔ BLOQUEIO DE CONSISTÊNCIA: Nova coluna detectada em 'database.py' sem migração (.sql).",
            COLOR_RED,
        )
        print_colored(
            "   O sistema detectou uma adição de campo (ex: 'chave': valor) no código,\n"
            "   mas nenhum arquivo .sql foi encontrado no commit.\n"
            "   - Por favor, adicione o script de migração do Supabase.\n"
            "   - Se for um falso positivo, use 'git commit --no-verify'.",
            COLOR_YELLOW,
        )
        return False

    print_colored(
        "✅ Check de Migrations OK (Schema Change + .sql encontrado).", COLOR_GREEN
    )
    return True


# =============================================================================
# INTEGRAÇÕES (SUPABASE E GEMINI)
# =============================================================================


def check_supabase_connection() -> bool:
    """Verifica se é possível conectar ao Supabase com as credenciais atuais."""
    print_colored("🔌 Testando conexão com Supabase...", COLOR_BLUE)

    try:
        from supabase import create_client, Client
    except ImportError:
        print_colored("⚠️ Biblioteca 'supabase' ausente.", COLOR_YELLOW)
        return False

    secrets = load_secrets()
    sb_config = secrets.get("supabase", {})
    url = sb_config.get("url") or os.environ.get("SUPABASE_URL")
    key = sb_config.get("key") or os.environ.get("SUPABASE_KEY_PROD")

    if not url or not key:
        print_colored(
            "❌ Credenciais do Supabase ausentes (secrets.toml ou ENV).", COLOR_RED
        )
        return False

    try:
        client: Client = create_client(url, key)
        client.table("chat_logs").select("chat_id", count="exact").limit(0).execute()
        print_colored("✅ Conexão DB OK.", COLOR_GREEN)
        return True
    except Exception as e:
        print_colored(f"❌ Falha de Conexão DB: {str(e)}", COLOR_RED)
        return False


def sanitize_diff_for_ai(diff_text: str) -> str:
    """Remove linhas adicionadas que possam conter segredos antes de enviar para a IA."""
    sanitized_lines = []
    for line in diff_text.splitlines():
        if line.startswith("+") and any(
            re.search(p[0], line) for p in SECRETS_PATTERNS
        ):
            sanitized_lines.append("+ [REDACTED SECRET DETECTED]")
        else:
            sanitized_lines.append(line)
    return "\n".join(sanitized_lines)


def run_ai_code_review(diff_text: str) -> bool:
    """Submete o diff ao Gemini para revisão."""
    print_colored("🤖 Iniciando Code Review IA (Gemini)...", COLOR_BLUE)

    if not diff_text.strip():
        return True

    secrets = load_secrets()
    # Tenta achar a chave do Gemini em vários lugares comuns
    gemini_key = secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")

    if not gemini_key:
        print_colored(
            "⚠️ GEMINI_API_KEY não encontrada. Revisão IA pulada.", COLOR_YELLOW
        )
        return True

    try:
        import google.generativeai as genai

        genai.configure(api_key=gemini_key)
        model_name = "gemini-2.5-flash"
        model = genai.GenerativeModel(model_name)

        safe_diff = sanitize_diff_for_ai(diff_text)
        if len(safe_diff) > 20000:
            safe_diff = safe_diff[:20000] + "\n... (truncated)"

        prompt = (
            "ATENÇÃO: Você é um Gatekeeper de Segurança.\n"
            "Analise o git diff abaixo do projeto Vox AI.\n"
            "Regras:\n"
            "1. Se encontrar VULNERABILIDADE CRÍTICA (senha exposta, SQLi, chave de API) -> Inicie a resposta com '[BLOCK]' e explique o erro.\n"
            "2. Se encontrar BUG DE PRODUÇÃO (loop infinito, crash certo) -> Inicie a resposta com '[BLOCK]' e explique.\n"
            "3. Se for seguro (mesmo com débitos técnicos leves) -> Responda ESTRITAMENTE: '[PASS] Aprovado. So fale algo a mais se voce tiver alguma melhoria para sugerir.'\n"
            "   NÃO escreva resumos, NÃO elogie, NÃO explique nada se for aprovar. Seja mudo em caso de sucesso.\n\n"
            "DIFF DO CÓDIGO:\n"
            f"{safe_diff}"
        )

        response = model.generate_content(prompt)
        review_text = response.text

        if review_text:
            print(f"\n📝 Relatório Gemini:\n{review_text}\n")

            # 1. Verifica keywords críticas em QUALQUER lugar do texto (soberano sobre [PASS])
            # Isso garante que se a IA citar "password exposed" no meio do texto, bloqueia.
            lower_review = review_text.lower()
            if any(k in lower_review for k in BLOCK_KEYWORDS):
                triggered_word = next(k for k in BLOCK_KEYWORDS if k in lower_review)
                print_colored(
                    f"⛔ Bloqueio: Palavra-chave crítica '{triggered_word}' encontrada no relatório.",
                    COLOR_RED,
                )
                return False

            clean_review = review_text.strip().upper()
            
            # 2. Verifica tag de bloqueio explícito
            if clean_review.startswith("[BLOCK]"):
                print_colored(
                    "⛔ Bloqueio: IA solicitou bloqueio explícito ([BLOCK]).", COLOR_RED
                )
                return False

            # 3. Aprovação
            if clean_review.startswith("[PASS]"):
                print_colored("✅ IA Aprovou (Protocolo [PASS]).", COLOR_GREEN)
                return True
            
            # Fallback (sem tag clara) -> Bloqueia por segurança ou Passa com aviso?
            # Por segurança, melhor pedir para verificar manualmente se não entendeu.
            print_colored("⚠️ Resposta da IA inconclusiva (sem [PASS]/[BLOCK]). Verifique o log acima.", COLOR_YELLOW)
            return True # Deixa passar se não detectou perigo explícito (keywords já filtraram)


    except Exception as e:
        print_colored(f"⚠️ Erro ao consultar Gemini: {e}", COLOR_YELLOW)
        return True

    print_colored("✅ Revisão IA finalizada (Aprovado).", COLOR_GREEN)
    return True


# =============================================================================
# GIT UTILS
# =============================================================================


def get_git_files(mode: str) -> List[str]:
    """Retorna lista de nomes de arquivos modificados."""
    cmd = []
    if mode == "pre-commit":
        cmd = ["git", "diff", "--name-only", "--cached"]
    else:  # pre-push
        # Tenta detectar origin/master, se falhar, usa apenas staged/local changes como fallback
        cmd = ["git", "diff", "--name-only", "origin/master..HEAD"]

    try:
        output = subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode()
        return [f.strip() for f in output.splitlines() if f.strip()]
    except subprocess.CalledProcessError:
        # Fallback para diff cached se origin/master não existir (primeiro push de branch nova)
        try:
            return (
                subprocess.check_output(["git", "diff", "--name-only", "--cached"])
                .decode()
                .splitlines()
            )
        except:
            return []


def get_git_diff_content(mode: str) -> str:
    """Retorna o conteúdo do diff."""
    cmd = []
    if mode == "pre-commit":
        cmd = ["git", "diff", "--cached"]
    else:
        cmd = ["git", "diff", "origin/master..HEAD"]

    try:
        return subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode()
    except:
        return ""


# =============================================================================
# MAIN
# =============================================================================


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

    # 3. Verificações Avançadas (Apenas PRE-PUSH)
    # Evita latência no commit local, mas garante qualidade antes de subir.
    if args.mode == "pre-push":

        # a) Banco de Dados
        if not check_supabase_connection():
            sys.exit(1)

        # b) Code Review IA
        full_diff = get_git_diff_content(args.mode)
        if full_diff:
            if not run_ai_code_review(full_diff):
                sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()

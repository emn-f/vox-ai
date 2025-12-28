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

# Constantes de Cores para Terminal
COLOR_RED = "\033[91m"
COLOR_GREEN = "\033[92m"
COLOR_YELLOW = "\033[93m"
COLOR_BLUE = "\033[94m"
COLOR_RESET = "\033[0m"

# Configuração da IA (Google Gemini)
# Modelo: gemini-2.5-flash (Mais recente detectado)
# Limite máximo de caracteres para envio à IA
MAX_DIFF_CONTEXT = 20000

# Lista de padrões de Segredos (Regex, Descrição)
SECRETS_PATTERNS = [
    (r"sk-[a-zA-Z0-9]{48}", "OpenAI API Key"),
    (r"ghp_[a-zA-Z0-9]{36}", "GitHub Personal Access Token"),
    (r"xox[baprs]-([0-9a-zA-Z]{10,48})?", "Slack Token"),
    (r"-----BEGIN PRIVATE KEY-----", "Generic Private Key"),
    (r"AIza[0-9A-Za-z-_]{35}", "Google API Key"),
    (r"ey[A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.?[A-Za-z0-9-_.+/=]*", "Potential JWT/Token"),
    (r"(?i)(?:key|secret|password|token|auth|credential|jwt)\w*\s*=\s*['\"][\w\-@\.]{24,}['\"]", "Generic High-Entropy Assignment"),
]

# Palavras-chave que, se a IA mencionar na revisão, bloqueiam o push.
BLOCK_KEYWORDS = [
    "security vulnerability", "critical issue", "password exposed", 
    "sql injection", "vulnerabilidade crítica", "senha exposta",
    "remote code execution", "xss"
]

# =============================================================================
# FUNÇÕES UTILITÁRIAS
# =============================================================================

def print_colored(msg: str, color: str = COLOR_RESET):
    """Imprime mensagem colorida se o terminal suportar."""
    # Simples verificação se estamos em um TTY
    if sys.stdout.isatty():
        print(f"{color}{msg}{COLOR_RESET}")
    else:
        print(msg)

def load_secrets() -> dict:
    """Carrega segredos do arquivo .streamlit/secrets.toml de forma segura."""
    secrets_path = os.path.join(os.getcwd(), ".streamlit", "secrets.toml")
    
    if not os.path.exists(secrets_path):
        return {}

    data = {}
    if not toml:
        print_colored("⚠️ Aviso: Nenhuma biblioteca TOML encontrada (pip install tomli). Secrets.toml ignorado.", COLOR_YELLOW)
        return {}

    try:
        # Tenta abrir como binário primeiro (tomllib/tomli)
        with open(secrets_path, "rb") as f:
            if hasattr(toml, 'load'):
                data = toml.load(f)
            else:
                pass
    except:
        try:
             with open(secrets_path, "r", encoding="utf-8") as f:
                data = toml.load(f)
        except:
            pass
            
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
                    print_colored(f"❌ ALERTA DE SEGURANÇA: {name} detectado em '{file_path}'", COLOR_RED)
                    found_secrets = True
                    
        except Exception:
            # Arquivos que não puderem ser lidos (binários, links quebrados) são ignorados
            pass

    if found_secrets:
        print_colored("⛔ Bloqueio: Segredos detectados no código. Remova-os antes de commitar.", COLOR_RED)
        return False
        
    print_colored("✅ Nenhum segredo detectado.", COLOR_GREEN)
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
    key = sb_config.get("key") or os.environ.get("SUPABASE_KEY")

    if not url or not key:
        print_colored("❌ Credenciais do Supabase ausentes (secrets.toml ou ENV).", COLOR_RED)
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
        if line.startswith("+") and any(re.search(p[0], line) for p in SECRETS_PATTERNS):
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
    # Tenta achar a chave do Gemini em vários lugares comuns do secrets.toml
    gemini_key = (
        secrets.get("GEMINI_API_KEY") 
        or secrets.get("gemini", {}).get("api_key") 
        or secrets.get("google", {}).get("api_key")
        or os.environ.get("GEMINI_API_KEY")
    )
    
    if not gemini_key:
        print_colored("⚠️ GEMINI_API_KEY não encontrada. Revisão IA pulada.", COLOR_YELLOW)
        return True 

    try:
        import google.generativeai as genai
        
        genai.configure(api_key=gemini_key)
        
        # Tenta usar o modelo mais recente detectado nos testes (2.5), senão fallback para 1.5
        # Na prática, se o teste passou com 2.5, vamos forçar 2.5 para aproveitar os recursos
        model_name = "gemini-2.5-flash"
        
        model = genai.GenerativeModel(model_name)
        
        safe_diff = sanitize_diff_for_ai(diff_text)
        if len(safe_diff) > 20000: 
            safe_diff = safe_diff[:20000] + "\n... (truncated)"

        prompt = (
            "Você é um Engenheiro de Software Sênior e Especialista em Segurança.\n"
            "Analise o seguinte git diff do projeto Vox AI.\n"
            "Foque EXCLUSIVAMENTE em:\n"
            "1. VULNERABILIDADES DE SEGURANÇA CRÍTICAS (Ex: SQL Injection, XSS, Chaves Expostas, RCE).\n"
            "2. BUGS LÓGICOS GRAVES que podem quebrar a produção.\n"
            "3. Má utilização crítica de recursos (loops infinitos, memory leaks óbvios).\n\n"
            "Se o código estiver seguro, responda APENAS: '✅ Código Seguro. Nenhuma vulnerabilidade crítica encontrada.'\n"
            "Se encontrar problemas, seja direto, cite o arquivo/linha e explique o risco.\n"
            "Use Português Brasileiro.\n\n"
            f"DIFF:\n{safe_diff}"
        )

        response = model.generate_content(prompt)
        review_text = response.text

        if review_text:
            print(f"\n📝 Relatório Gemini:\n{review_text}\n")
            
            # Bloqueio baseado em keywords no output do Gemini
            lower_review = review_text.lower()
            if any(k in lower_review for k in BLOCK_KEYWORDS):
                print_colored("⛔ Bloqueio: Gemini apontou vulnerabilidade crítica.", COLOR_RED)
                return False
                
    except Exception as e:
        print_colored(f"⚠️ Erro ao consultar Gemini: {e}", COLOR_YELLOW)
        return True

    print_colored("✅ Revisão IA finalizada.", COLOR_GREEN)
    return True

# =============================================================================
# GIT UTILS
# =============================================================================

def get_git_files(mode: str) -> List[str]:
    """Retorna lista de nomes de arquivos modificados."""
    cmd = []
    if mode == "pre-commit":
        cmd = ["git", "diff", "--name-only", "--cached"]
    else: # pre-push
        # Tenta detectar origin/master, se falhar, usa apenas staged/local changes como fallback
        cmd = ["git", "diff", "--name-only", "origin/master..HEAD"]
        
    try:
        output = subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode()
        return [f.strip() for f in output.splitlines() if f.strip()]
    except subprocess.CalledProcessError:
        # Fallback para diff cached se origin/master não existir (primeiro push de branch nova)
        try:
            return subprocess.check_output(["git", "diff", "--name-only", "--cached"]).decode().splitlines()
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
    
    print_colored("✨ Tudo limpo! Procedendo...", COLOR_GREEN)
    sys.exit(0)

if __name__ == "__main__":
    main()

import os
import sys
import re
import argparse
import subprocess
from typing import List, Tuple
import requests

# Tenta importar bibliotecas de TOML na ordem de preferência/disponibilidade
try:
    import tomllib as toml  # Python 3.11+ stdlib
except ImportError:
    try:
        import tomli as toml  # Biblioteca moderna
    except ImportError:
        try:
            import toml  # Biblioteca mais antiga (mas comum)
        except ImportError:
            toml = None

# --- Configuração ---
SECRETS_PATTERNS = [
    (r"sk-[a-zA-Z0-9]{48}", "OpenAI API Key"),
    (r"ghp_[a-zA-Z0-9]{36}", "GitHub Personal Access Token"),
    (r"xox[baprs]-([0-9a-zA-Z]{10,48})?", "Slack Token"),
    (r"-----BEGIN PRIVATE KEY-----", "Generic Private Key"),
    (r"AIza[0-9A-Za-z-_]{35}", "Google API Key"),
]

# Modelo da Microsoft para Code Review
# Nota: Usamos a URL de inferência padrão; pode ser necessário ajuste fino dependendo do plano HF.
HF_API_URL = "https://api-inference.huggingface.co/models/microsoft/codereviewer"

def load_secrets():
    """Carrega segredos do .streamlit/secrets.toml se existir."""
    secrets_path = os.path.join(os.getcwd(), ".streamlit", "secrets.toml")
    if os.path.exists(secrets_path):
        if toml:
            try:
                with open(secrets_path, "rb") as f: # tomllib/tomli expect bytes usually, toml expects string
                    # Adaptação para diferentes libs toml
                    if hasattr(toml, 'load'):
                        # 'toml' library often takes a file object opened in text mode for 'load', 
                        # but 'tomli/tomllib' take binary. Let's try reading content first.
                        pass
                
                # Check library type by attribute
                with open(secrets_path, "rb") as fb:
                    if hasattr(toml, 'load'): 
                        # tomllib (std) or tomli
                        return toml.load(fb)
            except Exception:
                 # Fallback for 'toml' lib which might want text
                 with open(secrets_path, "r", encoding="utf-8") as ft:
                     return toml.load(ft)
        else:
            print("⚠️ Aviso: Biblioteca TOML não encontrada. Não foi possível ler secrets.toml.")
    return {}

def check_secrets(files: List[str]) -> bool:
    """Verifica se há segredos nos arquivos listados."""
    print("🔒 Iniciando verificação de segredos...")
    found_secrets = False
    
    current_script = os.path.abspath(__file__)
    
    for file_path in files:
        if not os.path.exists(file_path):
            continue
            
        # Ignora o próprio script de verificação para evitar falso positivo nos padrões regex
        if os.path.abspath(file_path) == current_script:
            continue
            
        # Pula arquivos binários ou grandes demais
        try:
            if os.path.getsize(file_path) > 1024 * 1024: # 1MB limit
                continue
                
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                
            for pattern, name in SECRETS_PATTERNS:
                if re.search(pattern, content):
                    print(f"❌ ALERTA DE SEGURANÇA: Possível {name} encontrado em {file_path}")
                    found_secrets = True
        except Exception as e:
            # Ignora erros de leitura em arquivos não textuais
            pass

    if found_secrets:
        print("⛔ Commit/Push bloqueado devido a segredos detectados.")
        return False
    print("✅ Nenhum segredo detectado.")
    return True

def check_supabase_connection() -> bool:
    """Verifica a conexão com o Supabase."""
    print("🔌 Testando conexão com Supabase...")
    try:
        from supabase import create_client, Client
    except ImportError:
        print("⚠️ Biblioteca 'supabase' não encontrada (pip install supabase).")
        return False

    secrets = load_secrets()
    sb_config = secrets.get("supabase", {})
    url = sb_config.get("url") or os.environ.get("SUPABASE_URL")
    key = sb_config.get("key") or os.environ.get("SUPABASE_KEY")

    if not url or not key:
        print("❌ Credenciais do Supabase não encontradas.")
        print("   Verifique .streamlit/secrets.toml ou variáveis de ambiente SUPABASE_URL/KEY.")
        return False

    try:
        client: Client = create_client(url, key)
        # Verifica conexão real
        # 'chat_logs' parece ser uma tabela central no sistema do usuário.
        # Buscamos 1 registro apenas para validar auth e rede.
        client.table("chat_logs").select("chat_id", count="exact").limit(1).execute()
        print("✅ Conexão com Supabase estabelecida com sucesso.")
        return True
    except Exception as e:
        print(f"❌ Falha na conexão com Supabase: {e}")
        return False

def ai_code_review(diff_text: str) -> bool:
    """Envia o diff para revisão da IA."""
    print("🤖 Iniciando revisão automotizada de código (Microsoft/CodeReviewer)...")
    
    secrets = load_secrets()
    hf_token = secrets.get("huggingface", {}).get("token") or os.environ.get("HF_TOKEN")
    
    if not hf_token:
        print("⚠️ Token do Hugging Face não encontrado (huggingface.token). Pulando revisão IA.")
        return True 
    
    if not diff_text.strip():
        return True

    # Preparar payload. O modelo Microsoft CodeReviewer é um T5 pré-treinado.
    # Ele gera comentários de revisão baseados no diff.
    headers = {"Authorization": f"Bearer {hf_token}"}
    
    # Tentativa de usar a API de inferência
    # Truncar diff para não estourar contexto (aprox 3000 chars)
    truncated_diff = diff_text[:3000]
    if len(diff_text) > 3000:
        truncated_diff += "\n... (truncated)"

    payload = {
        "inputs": truncated_diff,
        "parameters": {"max_new_tokens": 256}  # Limite de resposta
    }

    try:
        response = requests.post(HF_API_URL, headers=headers, json=payload, timeout=20)
        
        if response.status_code == 503:
            print("⏳ Modelo carregando ou indisponível temporariamente. Ignorando erro para não bloquear.")
            return True
            
        response.raise_for_status()
        
        # Parse da resposta
        output = response.json()
        
        # A API pode retornar uma lista de dicts ou um dict
        review_text = ""
        if isinstance(output, list) and len(output) > 0:
            review_text = output[0].get("generated_text", "")
        elif isinstance(output, dict):
            review_text = output.get("generated_text", "")
            
        if review_text:
            print("\n📝 Comentários da IA:")
            print(f"   {review_text}")
            
            # Bloqueio condicional
            # Adicionamos palavras chaves em PT-BR também caso o modelo seja multilíngue ou traduza
            block_keywords = [
                "security vulnerability", "critical issue", "password exposed", 
                "sql injection", "vulnerabilidade crítica", "senha exposta"
            ]
            
            if any(k in review_text.lower() for k in block_keywords):
                print("⛔ Bloqueio: IA detectou problema crítico de segurança.")
                return False
        else:
            print("ℹ️ IA não gerou comentários relevantes.")

    except Exception as e:
        print(f"⚠️ Erro na comunicação com IA: {e}")
        # Não bloqueamos falhas de rede da API de IA
        return True

    print("✅ Revisão de IA finalizada.")
    return True

def get_changed_files(mode):
    """Retorna lista de arquivos modificados."""
    try:
        if mode == "pre-commit":
            # Arquivos na staging area
            cmd = ["git", "diff", "--name-only", "--cached"]
        else:
            # Arquivos modificados em relação a master (para pre-push)
            # Tenta identificar branch base
            cmd = ["git", "diff", "--name-only", "origin/master..HEAD"]
            
        output = subprocess.check_output(cmd).decode()
        return [f.strip() for f in output.splitlines() if f.strip() and os.path.exists(f.strip())]
    except Exception:
        return []

def get_full_diff(mode):
    try:
        if mode == "pre-commit":
            return subprocess.check_output(["git", "diff", "--cached"]).decode()
        else:
            return subprocess.check_output(["git", "diff", "origin/master..HEAD"]).decode()
    except:
        return ""

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["pre-commit", "pre-push"], required=True)
    args = parser.parse_args()
    
    print(f"\n⚡ [Vox AI] Executando verificações: {args.mode}")
    
    files = get_changed_files(args.mode)
    if not files:
        print("Nenhum arquivo modificado detectado.")
        sys.exit(0)
        
    # 1. Check de Segredos (Sempre)
    if not check_secrets(files):
        sys.exit(1)
        
    # 2. Checks Avançados (Apenas Push)
    if args.mode == "pre-push":
        # Check BD
        if not check_supabase_connection():
            sys.exit(1)
            
        # Check IA
        diff_content = get_full_diff(args.mode)
        if not ai_code_review(diff_content):
            sys.exit(1)
            
    sys.exit(0)

if __name__ == "__main__":
    main()

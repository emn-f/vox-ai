import os
import re
from google import genai
from gatekeep.utils.ui import print_colored, COLOR_RED, COLOR_BLUE, COLOR_GREEN, COLOR_YELLOW
from gatekeep.utils.config import load_secrets
from gatekeep.logger import log_ai_event
from gatekeep.scanners.secrets import SECRETS_PATTERNS

GEMINI_MODEL_GATEKEEP = "gemini-1.5-flash-lite"

BLOCK_KEYWORDS = [
    "password exposed", "senha exposta", "sql injection", "remote code execution",
    "xss", "[block]", "rce", "exposed secret", "chave exposta"
]

def run_ai_code_review(diff_text: str) -> bool:
    """Submete o diff ao Gemini para revisão."""
    print_colored("🤖 Iniciando Code Review IA (Gemini)...", COLOR_BLUE)

    if not diff_text.strip():
        return True

    gemini_key = load_secrets().get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if not gemini_key:
        print_colored("⚠️ GEMINI_API_KEY não encontrada. Revisão IA pulada.", COLOR_YELLOW)
        return True

    try:
        safe_diff = _prepare_diff_for_ai(diff_text)
        client = genai.Client(api_key=gemini_key)
        response = client.models.generate_content(
            model="gemini-1.5-flash-lite", 
            contents=_create_ai_prompt(safe_diff)
        )

        return _process_ai_response(response.text)

    except Exception as e:
        print_colored(f"⚠️ Erro ao consultar Gemini: {e}", COLOR_YELLOW)
        return True

def _prepare_diff_for_ai(diff_text: str) -> str:
    """Sanitiza e trunca o diff."""
    sanitized_lines = []
    for line in diff_text.splitlines():
        if line.startswith("+") and any(re.search(p[0], line) for p in SECRETS_PATTERNS):
            sanitized_lines.append("+ [REDACTED SECRET DETECTED]")
        else:
            sanitized_lines.append(line)
    
    safe_diff = "\n".join(sanitized_lines)
    return safe_diff[:20000] + "\n... (truncated)" if len(safe_diff) > 20000 else safe_diff

def _create_ai_prompt(diff_content: str) -> str:
    return (
        "ATENÇÃO: Você é um Gatekeeper de Segurança.\n"
        "Analise o git diff abaixo do Projeto Vox.\n"
        "Regras:\n"
        "1. Se encontrar VULNERABILIDADE CRÍTICA -> Inicie com '[BLOCK]'.\n"
        "2. Se for seguro -> Responda ESTRITAMENTE: '[PASS] Aprovado.'\n\n"
        f"DIFF:\n{diff_content}"
    )

def _process_ai_response(review_text: str) -> bool:
    if not review_text: return True
    print(f"\n📝 Relatório Gemini:\n{review_text}\n")
    
    lower_review = review_text.lower()
    for k in BLOCK_KEYWORDS:
        if re.search(r"\b" + re.escape(k) + r"\b", lower_review):
            print_colored(f"⛔ Bloqueio: Palavra-chave '{k}' encontrada.", COLOR_RED)
            log_ai_event("BLOCK (Keyword Trigger)", review_text)
            return False

    if review_text.strip().upper().startswith("[BLOCK]"):
        print_colored("⛔ Bloqueio: IA solicitou bloqueio explícito.", COLOR_RED)
        log_ai_event("BLOCK (AI Explicit)", review_text)
        return False

    if review_text.strip().upper().startswith("[PASS]"):
        print_colored("✅ IA Aprovou.", COLOR_GREEN)
        return True

    return True

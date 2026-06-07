import datetime
import os
import re
import shutil
import subprocess
import sys
from google import genai
from gatekeep.colors import print_colored, COLOR_BLUE, COLOR_GREEN, COLOR_RED, COLOR_YELLOW
from gatekeep.config_loader import load_secrets
from gatekeep.git_utils import get_git_metadata

from src.config import GEMINI_MODEL_GATEKEEP

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
        pass

def sanitize_diff_for_ai(diff_text: str) -> str:
    """
    Sanitiza o diff de modificações, ofuscando chaves de API e segredos identificados 
    antes de enviar o texto para servidores de inteligência artificial de terceiros (compliance).

    Args:
        diff_text (str): O diff git em texto bruto.

    Returns:
        str: O diff higienizado e seguro.
    """
    from gatekeep.secrets_check import SECRETS_PATTERNS
    sanitized_lines = []
    for line in diff_text.splitlines():
        if line.startswith("+") and any(
            re.search(p[0], line) for p in SECRETS_PATTERNS
        ):
            sanitized_lines.append("+ # [REDACTED SECRET DETECTED]")
        else:
            sanitized_lines.append(line)
    return "\n".join(sanitized_lines)

def run_ai_code_review(diff_text: str) -> bool:
    """Submete o diff ao Gemini para revisão e avalia o resultado."""
    print_colored("🤖 Iniciando Code Review IA (Gemini)...", COLOR_BLUE)

    if not diff_text.strip():
        return True

    gemini_key = load_secrets().get("GEMINI_API_KEY") or os.environ.get(
        "GEMINI_API_KEY"
    )
    if not gemini_key:
        print_colored(
            "⚠️ GEMINI_API_KEY não encontrada. Revisão IA pulada.", COLOR_YELLOW
        )
        return True

    try:
        safe_diff = _prepare_diff_for_ai(diff_text)
        client = genai.Client(api_key=gemini_key)
        response = client.models.generate_content(
            model=GEMINI_MODEL_GATEKEEP, contents=_create_ai_prompt(safe_diff)
        )

        return _process_ai_response(response.text)

    except Exception as e:
        print_colored(f"❌ Erro ao consultar Gemini: {e}", COLOR_RED)
        print_colored(
            "⛔ BLOQUEIO: A revisão de código por IA (Gemini) é obrigatória antes do push e falhou ou está indisponível.\n"
            "   Tente novamente mais tarde quando o serviço for reestabelecido,\n"
            "   ou use 'git push --no-verify' em caso de extrema necessidade.",
            COLOR_YELLOW,
        )
        return False

def _prepare_diff_for_ai(diff_text: str) -> str:
    """
    Limpa o diff e limita o seu tamanho máximo (truncando se necessário) para evitar 
    estouros de contexto de tokens na API do Gemini.

    Args:
        diff_text (str): Texto bruto do diff.

    Returns:
        str: Texto do diff higienizado e truncado em tamanho seguro.
    """
    safe_diff = sanitize_diff_for_ai(diff_text)
    if len(safe_diff) > 20000:
        return safe_diff[:20000] + "\n... (truncated)"
    return safe_diff

def _create_ai_prompt(diff_content: str) -> str:
    """
    Gera as instruções do prompt do sistema para direcionar o Code Reviewer do Gemini.

    Args:
        diff_content (str): Texto estruturado do git diff.

    Returns:
        str: O prompt formatado.
    """
    return (
        "ATENÇÃO: Você é um Gatekeeper de Segurança.\n"
        "Analise o git diff abaixo do Projeto Vox.\n"
        "Regras:\n"
        "1. Se encontrar VULNERABILIDADE CRÍTICA (senha exposta, SQLi, chave de API) -> Inicie a resposta com '[BLOCK]' e explique o erro.\n"
        "2. Se encontrar BUG DE PRODUÇÃO (loop infinito, crash certo) -> Inicie a resposta com '[BLOCK]' e explique.\n"
        "3. Se for seguro (mesmo com débitos técnicos leves) -> Responda ESTRITAMENTE: '[PASS] Aprovado.' Só fale algo a mais se voce tiver alguma melhoria para sugerir.\n"
        "  NÃO escreva resumos, NÃO elogie, NÃO explique nada se for aprovar. Seja mudo em caso de sucesso.\n\n"
        "DIFF DO CÓDIGO:\n"
        f"{diff_content}"
    )

def _process_ai_response(review_text: str) -> bool:
    """
    Analisa sintaticamente o parecer retornado pela IA. Verifica a presença de 
    pedidos de bloqueio explícitos ('[BLOCK]') ou palavras-chave de segurança críticas.

    Args:
        review_text (str): O texto de retorno do Gemini.

    Returns:
        bool: True se o código foi aprovado no review de segurança, False se foi reprovado/bloqueado.
    """
    if not review_text:
        return True

    print(f"\n📝 Relatório Gemini:\n{review_text}\n")
    lower_review = review_text.lower()

    for k in BLOCK_KEYWORDS:
        if re.search(r"\b" + re.escape(k) + r"\b", lower_review):
            print_colored(
                f"⛔ Bloqueio: Palavra-chave crítica '{k}' encontrada.", COLOR_RED
            )
            log_ai_event("BLOCK (Keyword Trigger)", review_text)
            return False

    clean_review = review_text.strip().upper()
    if clean_review.startswith("[BLOCK]"):
        print_colored(
            "⛔ Bloqueio: IA solicitou bloqueio explícito ([BLOCK]).", COLOR_RED
        )
        log_ai_event("BLOCK (AI Explicit)", review_text)
        return False

    if clean_review.startswith("[PASS]"):
        content_body = re.sub(
            r"^\[PASS\]\s*(Aprovado\.?)?", "", review_text, flags=re.IGNORECASE
        ).strip()
        if len(content_body) > 10:
            print_colored("✅ IA Aprovou com sugestões de melhoria.", COLOR_GREEN)
            log_ai_event("PASS (With Suggestions)", review_text)
        else:
            print_colored("✅ IA Aprovou (Limpo).", COLOR_GREEN)
        return True

    print_colored("✅ Revisão IA finalizada (Aprovado).", COLOR_GREEN)
    return True

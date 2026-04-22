import os
import re
from typing import List
from gatekeep.utils.ui import print_colored, COLOR_RED, COLOR_BLUE, COLOR_GREEN
from gatekeep.logger import log_ai_event

SECRETS_PATTERNS = [
    (r"sk-[a-zA-Z0-9]{48}", "OpenAI API Key"),
    (r"ghp_[a-zA-Z0-9]{36}", "GitHub Personal Access Token"),
    (r"xox[baprs]-([0-9a-zA-Z]{10,48})?", "Slack Token"),
    (r"-----BEGIN PRIVATE KEY-----", "Generic Private Key"),
    (r"AIza[0-9A-Za-z-_]{35}", "Google API Key"),
    (
        r"\bey[A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.?[A-Za-z0-9-_.+/=]*",
        "Potential JWT/Token",
    ),
    (
        r"(?i)(?:key|secret|password|token|auth|credential|jwt)\w*\s*=\s*['\"](?!__)[\w\-@\.]{24,}['\"]",
        "Generic High-Entropy Assignment",
    ),
]

def check_secrets_in_files(files: List[str]) -> bool:
    """Varre arquivos em busca de padrões de segredos."""
    print_colored("🔒 Iniciando verificação de segredos...", COLOR_BLUE)
    found_secrets = False

    # Caminho absoluto deste script e do security_check.py para evitar auto-detecção
    current_script = os.path.abspath(__file__)
    main_script = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "security_check.py"))

    for file_path in files:
        abs_path = os.path.abspath(file_path)

        if not os.path.exists(abs_path):
            continue

        # Pula os scripts de segurança
        if abs_path == current_script or abs_path == main_script:
            continue

        # Verificação rápida de tamanho (evita ler arquivos gigantes)
        try:
            if os.path.getsize(abs_path) > 1024 * 1024:  # > 1MB
                continue

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
        msg = "Segredos detectados no código. Bloqueio automático de segurança."
        print_colored(
            f"⛔ Bloqueio: {msg} Remova-os antes de commitar.",
            COLOR_RED,
        )
        log_ai_event("BLOCK (Local Secret Check)", msg)
        return False

    print_colored("✅ Nenhum segredo detectado.", COLOR_GREEN)
    return True

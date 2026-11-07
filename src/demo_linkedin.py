"""
Demo Feature: Validador de Compliance e LGPD.
Arquivo criado para demonstração do Gatekeeper Vox AI no LinkedIn.
"""

from typing import Dict, Any

def audit_user_input(payload: Dict[str, Any]) -> bool:
    """
    Higieniza e verifica se os inputs contêm termos compatíveis com LGPD.
    """
    sensitive_keys = {"cpf", "rg", "credit_card"}
    return not any(key in payload for key in sensitive_keys)

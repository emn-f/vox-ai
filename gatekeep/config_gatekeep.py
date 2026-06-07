"""
Configurações e Segredos do Gatekeeper.
Carrega as chaves de acesso e configurações do arquivo '.streamlit/secrets.toml'.
Define o modelo de IA utilizado na revisão de segurança do Gatekeeper
"""

import os
import tomllib

# Modelo de IA utilizado na revisão de segurança do Gatekeeper
GEMINI_MODEL_GATEKEEP = "gemini-3.1-flash-lite"

def load_secrets() -> dict:
    """
    Carrega chaves e segredos de configuração do arquivo '.streamlit/secrets.toml'
    de forma segura, tratando falhas de parser.

    Returns:
        dict: Dicionário contendo os segredos mapeados do arquivo TOML.
    """
    secrets_path = os.path.join(os.getcwd(), ".streamlit", "secrets.toml")
    if not os.path.exists(secrets_path):
        return {}

    try:
        with open(secrets_path, "rb") as f:
            data = tomllib.load(f)
    except Exception:
        # Fallback para parsing manual caso o arquivo esteja com erros de sintaxe TOML
        data = _manual_toml_parse(secrets_path)

    # Mapeamento legado para HF_TOKEN se necessário
    if "HF_TOKEN" in data:
        if "huggingface" not in data:
            data["huggingface"] = {}
        data["huggingface"]["token"] = data["HF_TOKEN"]

    return data

def _manual_toml_parse(path: str) -> dict:
    """
    Realiza o parse manual do arquivo TOML em caso de falha de parser do tomllib,
    processando atribuições básicas chave-valor de forma sequencial.

    Args:
        path (str): Caminho físico do arquivo TOML.

    Returns:
        dict: Chaves e valores de configuração parseados.
    """
    data = {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if "=" in line and not line.startswith("#"):
                    k, v = line.split("=", 1)
                    data[k.strip()] = v.strip().strip('"').strip("'")
    except Exception:
        pass
    return data

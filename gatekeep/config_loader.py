import os

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

def load_secrets() -> dict:
    """Carrega segredos do arquivo .streamlit/secrets.toml de forma segura."""
    secrets_path = os.path.join(os.getcwd(), ".streamlit", "secrets.toml")
    if not os.path.exists(secrets_path):
        return {}

    data = {}
    if toml is None or not hasattr(toml, "load"):
        data = _manual_toml_parse(secrets_path)
    else:
        try:
            with open(secrets_path, "rb") as f:
                data = toml.load(f)
        except Exception:
            data = _manual_toml_parse(secrets_path)

    # Mapeamento legado para HF_TOKEN se necessário
    if "HF_TOKEN" in data:
        if "huggingface" not in data:
            data["huggingface"] = {}
        data["huggingface"]["token"] = data["HF_TOKEN"]

    return data

def _manual_toml_parse(path: str) -> dict:
    """Parse manual de emergência para chaves simples (key = value)."""
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

import os
import google.generativeai as genai
import tomllib
import pytest

def get_gemini_key():
    """
    Tenta recuperar a chave do Gemini de várias fontes:
    1. secrets.toml (Streamlit)
    2. Variáveis de ambiente
    """
    try:
        # Tenta ler do secrets.toml (várias formas comuns)
        if os.path.exists(".streamlit/secrets.toml"):
            with open(".streamlit/secrets.toml", "rb") as f:
                secrets = tomllib.load(f)
                return (
                    secrets.get("GEMINI_API_KEY")
                    or secrets.get("gemini", {}).get("api_key")
                    or secrets.get("google", {}).get("api_key")
                )
    except Exception:
        # Fallback manual se toml falhar
        try:
            with open(".streamlit/secrets.toml", "r", encoding="utf-8") as f:
                content = f.read()
                for line in content.splitlines():
                    if "GEMINI_API_KEY" in line and "=" in line:
                        return line.split("=")[1].strip().strip('"').strip("'")
        except:
            pass

    # Por fim, tenta variável de ambiente
    return os.environ.get("GEMINI_API_KEY")


def test_gemini_connection_and_generation():
    """
    Teste de integração:
    1. Verifica se a chave de API existe.
    2. Conecta no Gemini.
    3. Tenta gerar uma resposta simples ('OK').
    """
    api_key = get_gemini_key()

    # Falha se não tiver chave
    assert api_key is not None, "❌ Chave do Gemini não encontrada (GEMINI_API_KEY)."
    assert len(api_key) > 10, "❌ Chave do Gemini parece inválida ou curta demais."

    print(f"🔑 Chave encontrada (início): {api_key[:5]}...")

    try:
        genai.configure(api_key=api_key)

        # Lista modelos (apenas para debug se falhar)
        models = [
            m.name
            for m in genai.list_models()
            if "generateContent" in m.supported_generation_methods
        ]
        assert (
            len(models) > 0
        ), "❌ Nenhum modelo de geração de texto disponível na API."

        # Seleção de modelo
        model_name = "gemini-1.5-flash"
        if "models/gemini-1.5-flash" not in models:
            if "models/gemini-pro" in models:
                model_name = "gemini-pro"
            elif models:
                model_name = models[0].replace("models/", "")

        print(f"👉 Usando modelo: {model_name}")
        model = genai.GenerativeModel(model_name)

        # Teste de geração real
        response = model.generate_content("Responda apenas 'OK'.")

        assert response is not None, "❌ A resposta do modelo foi Nula."
        assert response.text is not None, "❌ O texto da resposta foi Nulo."
        assert len(response.text) > 0, "❌ A resposta veio vazia."

        print(f"✅ Resposta recebida: {response.text.strip()}")

    except Exception as e:
        pytest.fail(f"❌ Falha na comunicação com Gemini: {e}")

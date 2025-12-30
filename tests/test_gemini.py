import os
import google.generativeai as genai
import tomllib

def get_gemini_key():
    try:
        # Tenta ler do secrets.toml (várias formas comuns)
        with open(".streamlit/secrets.toml", "rb") as f:
            secrets = tomllib.load(f)
            return (
                secrets.get("GEMINI_API_KEY") 
                or secrets.get("gemini", {}).get("api_key") 
                or secrets.get("google", {}).get("api_key")
            )
    except Exception:
        # Tenta ler via regex simples se TOML falhar
         try:
            with open(".streamlit/secrets.toml", "r", encoding="utf-8") as f:
                content = f.read()
                for line in content.splitlines():
                    if "GEMINI_API_KEY" in line and "=" in line:
                         return line.split("=")[1].strip().strip('"').strip("'")
         except:
             pass
    return os.environ.get("GEMINI_API_KEY")

def test_gemini():
    api_key = get_gemini_key()
    if not api_key:
        print("❌ Chave do Gemini não encontrada.")
        return False

    print(f"🔑 Chave encontrada: {api_key[:5]}...{api_key[-3:]}")
    
    try:
        genai.configure(api_key=api_key)
        
        print("🔎 Listando modelos disponíveis para esta chave...")
        try:
             models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
             print(f"   Modelos encontrados: {models}")
             
             # Seleção inteligente
             model_name = 'gemini-1.5-flash'
             if 'models/gemini-1.5-flash' not in models:
                 # Fallback comum
                 if 'models/gemini-pro' in models:
                     model_name = 'gemini-pro'
                 elif models:
                     model_name = models[0].replace('models/', '')
                 else:
                     print("❌ Nenhum modelo de geração de texto disponível para esta chave.")
                     return False
                     
             print(f"👉 Usando modelo: {model_name}")
             model = genai.GenerativeModel(model_name)
             
             print("🤖 Enviando teste...")
             response = model.generate_content("Responda apenas 'OK'.")
             if response.text:
                print(f"✅ SUCESSO! Resposta: {response.text.strip()}")
                return True
                
        except Exception as e_list:
             print(f"❌ Erro ao listar/testar: {e_list}")
             return False

    except Exception as e:
        print(f"❌ ERRO GERAL: {e}")
        return False

if __name__ == "__main__":
    test_gemini()

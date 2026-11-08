"""
Módulo de Configuração Centralizada, Credenciais e Registros do Vox AI.

Este módulo gerencia o carregamento dinâmico de chaves da API Gemini a partir de secrets.toml,
implementa o mecanismo de rotação transparente de chaves em caso de esgotamento de cota (429),
configura variáveis de ambiente para o Supabase e provê o interceptador LoggerTee.
"""
import os
import sys
import tomllib
import logging
import warnings
import atexit
from datetime import datetime
from typing import List, Tuple, Optional
from google import genai
from google.genai import types
from google.genai.errors import APIError, ServerError, ClientError

# Silenciar avisos e logs ruidosos de terceiros antes de qualquer outro import
warnings.filterwarnings("ignore")
os.environ["PYTHONWARNINGS"] = "ignore"
os.environ["STREAMLIT_LOG_LEVEL"] = "error"
os.environ["STREAMLIT_CLIENT_LOG_LEVEL"] = "error"

# Desativar propagação e definir nível para ERROR nos loggers ruidosos
for log_name in [
    "streamlit",
    "streamlit.runtime",
    "streamlit.runtime.scriptrunner_utils",
    "streamlit.runtime.scriptrunner_utils.script_run_context",
    "streamlit.runtime.state.session_state_proxy",
    "google",
    "google_genai",
    "google_genai.models",
    "httpx",
    "httpcore",
    "urllib3",
    "postgrest",
    "supabase",
    "gtts"
]:
    lg = logging.getLogger(log_name)
    lg.setLevel(logging.ERROR)
    lg.propagate = False

# Resolução do caminho do vox-ai
VOX_AI_PATH: str = '/workspaces/vox-ai'
if not os.path.exists(VOX_AI_PATH):
    VOX_AI_PATH = '/home/holmes/dev/projeto-vox/vox-ai'

if VOX_AI_PATH not in sys.path:
    sys.path.append(VOX_AI_PATH)

# Carregamento de Secrets
SECRETS_PATH: str = os.path.join(VOX_AI_PATH, '.streamlit/secrets.toml')
if not os.path.exists(SECRETS_PATH):
    raise FileNotFoundError(f"Arquivo secrets.toml não encontrado em {SECRETS_PATH}")

with open(SECRETS_PATH, 'rb') as f:
    SECRETS: dict = tomllib.load(f)

# Configurar Supabase no ambiente
os.environ["SUPABASE_URL"] = SECRETS.get("supabase", {}).get("url", "")
os.environ["SUPABASE_KEY"] = SECRETS.get("supabase", {}).get("key", "")

# Lista de API Keys do Gemini com Fallback (carrega dinamicamente em ordem decrescente)
API_KEYS: List[Tuple[str, str]] = []
for k, v in SECRETS.items():
    if "GEMINI_API_KEY" in k and isinstance(v, str) and v.strip():
        API_KEYS.append((k, v.strip()))

# Ordenar em ordem decrescente (ex: GEMINI_API_KEY_6 -> GEMINI_API_KEY_5 ... -> GEMINI_API_KEY)
API_KEYS.sort(key=lambda x: x[0], reverse=True)

print(f"🔑 {len(API_KEYS)} API key(s) do Gemini carregada(s): {[k for k, _ in API_KEYS]}")

os.environ["GEMINI_API_KEY"] = API_KEYS[0][1]

# Configuração Global de Modelos do Gemini
MODELO_GERACAO_PADRAO: str = "gemini-3.5-flash-lite"
MODELOS_JUIZ_ELEGIVEIS: List[str] = ["gemini-3.5-flash-lite", "gemini-2.5-flash-lite", "gemini-2.5-flash", "gemini-3.6-flash", "gemini-1.5-flash"]

# Desativar handlers ruidosos do logging raiz
logging.getLogger().handlers = []
logging.getLogger("Vox AI").handlers = []
logging.getLogger("Vox AI").setLevel(logging.WARNING)

# Estado global do índice de chave atual
_current_key_idx: int = 0


def get_current_api_key() -> Tuple[str, str]:
    """
    Retorna o par (nome, valor) da API Key do Gemini atualmente ativa no ciclo.

    Returns:
        Tuple[str, str]: Tupla contendo o identificador da chave e o token secreto.
    """
    global _current_key_idx
    return API_KEYS[_current_key_idx]


def rotate_api_key() -> Tuple[str, str]:
    """
    Rotaciona imediatamente o apontador para a próxima API Key disponível na lista.

    Returns:
        Tuple[str, str]: Tupla contendo o novo identificador e a nova chave ativa.
    """
    global _current_key_idx
    prev_name: str = API_KEYS[_current_key_idx][0]
    _current_key_idx = (_current_key_idx + 1) % len(API_KEYS)
    new_name: str = API_KEYS[_current_key_idx][0]
    print(f"🔄 Cota/Limite em '{prev_name}'. Alternando imediatamente para '{new_name}'...")
    return API_KEYS[_current_key_idx]


def gerar_resposta_com_fallback(prompt: str, sys_instruction: Optional[str] = None) -> str:
    """
    Envia uma requisição ao modelo Gemini com tratamento resiliente e troca imediata de chave
    ao identificar estouro de cota (HTTP 429 ou RESOURCE_EXHAUSTED).

    Args:
        prompt (str): Texto da pergunta ou prompt estruturado para o modelo.
        sys_instruction (Optional[str]): Instruções do sistema (System Prompt) para a sessão.

    Returns:
        str: Texto completo da resposta gerada pelo modelo.

    Raises:
        RuntimeError: Se todas as chaves de API falharem ou esgotarem a cota disponível.
    """
    global _current_key_idx
    tentativas: int = 0
    total_keys: int = len(API_KEYS)

    while tentativas < total_keys:
        key_name, key_val = API_KEYS[_current_key_idx]
        client = genai.Client(api_key=key_val)

        config = types.GenerateContentConfig(system_instruction=sys_instruction) if sys_instruction else None
        chat = client.chats.create(model=MODELO_GERACAO_PADRAO, config=config, history=[])

        try:
            response = chat.send_message(prompt)
            return response.text
        except (ClientError, APIError, ServerError) as e:
            err_str: str = str(e)
            is_quota: bool = "429" in err_str or "RESOURCE_EXHAUSTED" in err_str

            if is_quota:
                rotate_api_key()
                tentativas += 1
            else:
                print(f"⚠️ Erro ao chamar Gemini com key '{key_name}': {e}")
                rotate_api_key()
                tentativas += 1

    raise RuntimeError("❌ Todas as API Keys esgotaram a cota ou falharam.")


def gerar_avaliacao_juiz_com_fallback(prompt_juiz: str) -> str:
    """
    Submete um prompt de avaliação científica ao LLM Juiz (em modo JSON estrito)
    com alternância imediata de chave ao detectar limite de requisições.

    Args:
        prompt_juiz (str): Prompt de avaliação no formato de tríade RAG e Chain-of-Thought.

    Returns:
        str: Resposta em string com a estrutura JSON retornada pelo modelo avaliador.

    Raises:
        RuntimeError: Se nenhuma chave de API conseguir processar a avaliação.
    """
    global _current_key_idx
    tentativas: int = 0
    total_keys: int = len(API_KEYS)

    while tentativas < total_keys:
        key_name, key_val = API_KEYS[_current_key_idx]
        client = genai.Client(api_key=key_val)

        for model_name in MODELOS_JUIZ_ELEGIVEIS:
            try:
                res = client.models.generate_content(
                    model=model_name,
                    contents=prompt_juiz,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        temperature=0.0
                    )
                )
                return res.text
            except (ClientError, APIError, ServerError) as e:
                err_str: str = str(e)
                is_quota: bool = "429" in err_str or "RESOURCE_EXHAUSTED" in err_str
                if is_quota:
                    break
            except Exception:
                break

        rotate_api_key()
        tentativas += 1

    raise RuntimeError("❌ LLM Juiz falhou em gerar avaliação com todas as chaves disponíveis.")


class LoggerTee:
    """
    Redirecionador duplo de fluxo que grava simultaneamente no terminal (stdout/stderr)
    e em arquivo físico de log, aplicando filtros de mensagens ruidosas de terceiros.
    """
    def __init__(self, log_path: str) -> None:
        """
        Inicializa o LoggerTee e registra o callback de fechamento automático.

        Args:
            log_path (str): Caminho absoluto para o arquivo de destino do log.
        """
        self.terminal = sys.__stdout__
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        self.log = open(log_path, "w", encoding="utf-8")
        atexit.register(self.close)

    def write(self, message: str) -> None:
        """
        Escreve a mensagem nos destinos se não corresponder aos padrões ruidosos filtrados.

        Args:
            message (str): Mensagem emitida no fluxo de saída.
        """
        if not message:
            return

        noisy_patterns: List[str] = [
            "missing scriptruncontext",
            "session state does not function",
            "http request:",
            "afc is enabled",
            "api gemini configurada",
            "httpx:",
            "httpcore:",
            "google_genai",
            "urllib3:",
            "postgrest:",
            "streamlit",
            "thread 'mainthread'"
        ]
        msg_lower: str = message.lower()
        if any(ign in msg_lower for ign in noisy_patterns):
            return
        self.terminal.write(message)
        self.log.write(message)
        self.log.flush()

    def flush(self) -> None:
        """Força o descarregamento dos buffers de escrita no terminal e no arquivo."""
        try:
            self.terminal.flush()
            self.log.flush()
        except Exception:
            pass

    def close(self) -> None:
        """Encerra com segurança o manipulador do arquivo de log."""
        try:
            self.log.flush()
            self.log.close()
        except Exception:
            pass


def init_logging(log_filename: str = "execucao_pipeline.log") -> str:
    """
    Inicializa a captura de logs filtrados gravando um novo arquivo indexado por timestamp.

    Args:
        log_filename (str): Nome base do arquivo de log.

    Returns:
        str: Caminho absoluto completo onde o log de sessão está sendo gravado.
    """
    log_dir: str = "/workspaces/vox-cnpq/scripts/logs"
    os.makedirs(log_dir, exist_ok=True)
    timestamp: str = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_path: str = os.path.join(log_dir, f"{timestamp}_{log_filename}")
    sys.stdout = LoggerTee(log_path)
    sys.stderr = LoggerTee(log_path)
    return log_path

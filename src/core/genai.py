"""
Módulo Core da API Gemini (Google GenAI) do Vox AI.

Este módulo gerencia a autenticação com o cliente Gemini, inicialização das sessões
conversacionais com a persona Vox e transcrição de mídias de áudio de forma desacoplada da UI.
"""
from typing import Optional, Any, Generator
import streamlit as st
from google import genai
from google.genai import types

from data.prompts.system_prompt import INSTRUCOES
from src.config import GEMINI_MODEL_NAME, GEMINI_FALLBACK_MODELS, get_secret, logger

_gemini_client_instance: Optional[genai.Client] = None


def configurar_api_gemini() -> Optional[genai.Client]:
    """
    Configura e inicializa o cliente da API do Google GenAI utilizando a chave armazenada.

    Returns:
        Optional[genai.Client]: Cliente configurado do Gemini ou None em caso de falha.
    """
    global _gemini_client_instance
    if _gemini_client_instance is not None:
        return _gemini_client_instance

    try:
        api_key: str = get_secret("GEMINI_API_KEY")
        if not api_key:
            logger.error("⚠️ GEMINI_API_KEY não encontrada nas variáveis de ambiente ou secrets.")
            return None

        _gemini_client_instance = genai.Client(api_key=api_key)
        logger.debug("API Gemini configurada com sucesso.")
        return _gemini_client_instance
    except Exception as e:
        logger.error(f"❌ Erro ao configurar a API do Gemini: {e}")
        return None


def inicializar_chat_modelo(client: Optional[genai.Client] = None, model: Optional[str] = None) -> Any:
    """
    Inicializa uma nova sessão de chat conversacional com o modelo Gemini, definindo
    as diretrizes de comportamento do assistente.

    Args:
        client (Optional[genai.Client]): Cliente Gemini. Se omitido, utiliza a instância global.
        model (Optional[str]): Nome do modelo Gemini. Se omitido, utiliza GEMINI_MODEL_NAME.

    Returns:
        Any: Instância ativa do chat conversacional do Gemini.
    """
    client_ativo = client or configurar_api_gemini()
    if not client_ativo:
        raise RuntimeError("Cliente Gemini não disponível para inicializar o chat.")

    sys_config = types.GenerateContentConfig(
        system_instruction=INSTRUCOES,
    )

    modelo_alvo = model or GEMINI_MODEL_NAME

    return client_ativo.chats.create(
        model=modelo_alvo,
        config=sys_config,
        history=[],
    )


def _obter_lista_modelos_fallback(chat: Any) -> list[str]:
    """
    Retorna a lista ordenada e sem duplicatas de modelos a serem tentados em cascata de fallback.
    Prioriza o modelo atualmente configurado no chat, seguido pelos modelos definidos em GEMINI_FALLBACK_MODELS.
    """
    modelos: list[str] = []

    modelo_chat = None
    if hasattr(chat, "_model") and isinstance(chat._model, str):
        modelo_chat = chat._model
    elif hasattr(chat, "model") and isinstance(chat.model, str):
        modelo_chat = chat.model

    if modelo_chat and isinstance(modelo_chat, str) and modelo_chat.strip():
        modelos.append(modelo_chat.strip())

    base_list = GEMINI_FALLBACK_MODELS if GEMINI_FALLBACK_MODELS else [GEMINI_MODEL_NAME]
    for m in base_list:
        if isinstance(m, str) and m.strip() and m.strip() not in modelos:
            modelos.append(m.strip())

    return modelos or [GEMINI_MODEL_NAME]


def _is_safety_error(e: Exception) -> bool:
    """
    Identifica se a exceção é decorrente de bloqueio por diretrizes de segurança/moderação (Safety/Policy).
    Evita falsos positivos com a palavra isolada 'blocked' presente em erros de cota ou rede.
    """
    try:
        from google.genai.errors import APIError
        if isinstance(e, APIError) and e.code in (429, 503, 500, 502, 504, 408):
            return False
    except Exception:
        pass

    err_str = str(e).lower()
    safety_terms = [
        "safety",
        "safety policy",
        "safety policies",
        "safety rating",
        "blocked due to safety",
        "blocked by safety",
        "content policy",
        "policy violation",
        "harm category",
        "diretrizes de prote",
    ]
    return any(term in err_str for term in safety_terms)


def _is_fallback_candidate(e: Exception) -> bool:
    """
    Verifica se a exceção ocorrida é elegível para acionar a troca de modelo por fallback:
    - Erros de cota/limite (HTTP 429 / ResourceExhausted)
    - Serviços indisponíveis/sobrecarregados (HTTP 503 / Unavailable / Overloaded)
    - Modelo não encontrado ou descontinuado (HTTP 404 / NOT_FOUND / not found)
    - Erros de rede, conexão ou timeout transitórios
    """
    if _is_safety_error(e):
        return False

    try:
        from google.genai.errors import APIError
        if isinstance(e, APIError):
            if e.code in (404, 429, 503, 500, 502, 504, 408):
                return True
            if e.code == 400:
                return False
    except Exception:
        pass

    try:
        import httpx
        if isinstance(e, (httpx.TransportError, httpx.NetworkError, httpx.TimeoutException)):
            return True
    except Exception:
        pass

    try:
        import requests
        if isinstance(e, (requests.ConnectionError, requests.Timeout)):
            return True
    except Exception:
        pass

    try:
        import urllib3.exceptions as ue
        if isinstance(e, (ue.HTTPError, ue.PoolError)):
            return True
    except Exception:
        pass

    if isinstance(e, (ConnectionError, TimeoutError, OSError)):
        return True

    palavras_chave_fallback = [
        "429",
        "resourceexhausted",
        "resource_exhausted",
        "quota",
        "503",
        "serviceunavailable",
        "service unavailable",
        "overloaded",
        "unavailable",
        "indisponível",
        "not found",
        "not_found",
        "404",
        "network",
        "rede",
        "connection",
        "timeout",
        "timed out",
        "econnreset",
        "socket",
    ]

    err_str = str(e).lower()
    return any(termo in err_str for termo in palavras_chave_fallback)


def _tratar_erro_genai(e: Exception) -> str:
    """
    Trata exceções não resolvidas da API Gemini:
    - Registra a ocorrência no banco via salvar_erro
    - Exibe mensagem amigável no Streamlit
    - Executa st.stop() para interromper o fluxo na interface
    """
    sess_id = "Unknown"
    git_ver = "Unknown"

    try:
        if hasattr(st, "session_state"):
            sess_id = st.session_state.get("session_id", "Unknown")
            git_ver = st.session_state.get("git_version_str", "Unknown")
    except Exception:
        pass

    if git_ver == "Unknown":
        try:
            from src.utils import git_version
            git_ver = git_version() or git_ver
        except Exception:
            pass

    from src.core.db.logs import salvar_erro
    error_id = salvar_erro(sess_id, git_ver, e)

    err_msg = str(e).lower()
    is_safety = _is_safety_error(e)
    is_quota = False
    is_unavailable = False

    try:
        from google.genai.errors import APIError
        if isinstance(e, APIError):
            if e.code == 429:
                is_quota = True
            elif e.code == 503:
                is_unavailable = True
    except Exception:
        pass

    if not (is_safety or is_quota or is_unavailable):
        if "resourceexhausted" in err_msg or "429" in err_msg or "quota" in err_msg:
            is_quota = True
        elif "503" in err_msg or "serviceunavailable" in err_msg or "overloaded" in err_msg or "indisponível" in err_msg:
            is_unavailable = True

    try:
        if is_safety:
            st.error(
                f"⚠️ **Essa pergunta não pode ser respondida pelo Vox.**\n\n"
                f"Por razões de segurança e acolhimento, sua mensagem ativou nossas diretrizes de proteção e não pôde ser processada.\n\n"
                f"*(Código do Erro: **{error_id}**)*",
                icon="🚫",
            )
        elif is_quota:
            st.error(
                f"Olá! O Vox está recebendo muitas mensagens de carinho e dúvidas no momento, e atingimos nosso limite de processamento temporário da API do Google. "
                f"Por favor, aguarde cerca de um minutinho e tente enviar sua mensagem novamente! 💜\n\n"
                f"*(Código do Erro: **{error_id}**)*",
                icon="⚠️",
            )
        elif is_unavailable:
            st.error(
                f"Ops! Os servidores da inteligência artificial estão com uma demanda muito alta agora e temporariamente instáveis. "
                f"Que tal respirar fundo, tomar uma água e tentar de novo em alguns instantes? Estarei aqui esperando! 🏳️‍🌈\n\n"
                f"*(Código do Erro: **{error_id}**)*",
                icon="⏳",
            )
        else:
            try:
                from src.app.ui import exibir_mensagem_erro
                exibir_mensagem_erro(error_id)
            except Exception:
                st.error(
                    f"Putz, algo deu errado por aqui :/\n\n"
                    f"Por favor, reporte este erro para nossa equipe informando o código: **{error_id}**",
                    icon="🚫",
                )
    except Exception as e_ui:
        logger.error(f"Erro ao exibir mensagem amigável no Streamlit: {e_ui}")

    st.stop()
    return error_id


def gerar_resposta_stream(chat: Any, prompt: str, info_adicional: str) -> Generator[str, None, None]:
    """
    Gera o fluxo de resposta do assistente Vox AI a partir do prompt do usuário e do contexto fornecido,
    com suporte a fallback automático entre modelos em caso de indisponibilidade ou estouro de cota.

    Args:
        chat: Instância ativa do chat conversacional do Gemini.
        prompt (str): Texto da pergunta do usuário.
        info_adicional (str): Informações de contexto recuperadas da base de dados.

    Yields:
        str: Fragmentos de texto da resposta gerada.
    """
    if chat is None:
        try:
            chat = inicializar_chat_modelo()
        except Exception as e_init:
            _tratar_erro_genai(e_init)
            return

    full_prompt_for_model = prompt
    if info_adicional:
        full_prompt_for_model = (
            f"Prompt do Usuário: {prompt}\n\n"
            f"Contexto interno da sua base de conhecimento, que o usuário NÃO forneceu "
            f"(use para embasar sua resposta): {info_adicional}\n\n"
            f"Responda à pergunta do usuário com base no contexto fornecido."
        )

    modelos = _obter_lista_modelos_fallback(chat)
    last_exception = None
    sucesso = False
    yielded_any = False

    for idx, modelo in enumerate(modelos):
        try:
            if hasattr(chat, "_model"):
                try:
                    chat._model = modelo
                except Exception:
                    pass
            elif hasattr(chat, "model"):
                try:
                    chat.model = modelo
                except Exception:
                    pass

            stream = chat.send_message_stream(full_prompt_for_model)
            for chunk in stream:
                texto = None
                if hasattr(chunk, "text") and chunk.text:
                    texto = chunk.text
                elif isinstance(chunk, str) and chunk:
                    texto = chunk

                if texto:
                    yielded_any = True
                    yield texto

            sucesso = True
            break
        except Exception as e:
            last_exception = e
            if yielded_any or not _is_fallback_candidate(e) or idx == len(modelos) - 1:
                break

            proximo_modelo = modelos[idx + 1]
            logger.warning(
                f"⚠️ Erro ao gerar resposta com modelo '{modelo}': {e}. "
                f"Alternando para fallback '{proximo_modelo}'..."
            )

    if not sucesso and last_exception is not None:
        _tratar_erro_genai(last_exception)


def gerar_resposta(chat: Any, prompt: str, info_adicional: str) -> str:
    """
    Gera a resposta completa do assistente Vox AI a partir da stream de texto,
    com suporte a fallback automático de modelos.

    Args:
        chat: Instância ativa do chat conversacional do Gemini.
        prompt (str): Texto da pergunta do usuário.
        info_adicional (str): Informações de contexto recuperadas da base de dados.

    Returns:
        str: Resposta textual consolidada do modelo.
    """
    return "".join(list(gerar_resposta_stream(chat, prompt, info_adicional)))


def transcrever_audio(audio_file: Any) -> Optional[str]:
    """
    Realiza a transcrição de um arquivo de áudio de voz para texto utilizando o modelo Gemini.

    Args:
        audio_file (Any): Arquivo ou buffer contendo o áudio gravado.

    Returns:
        Optional[str]: O texto transcrito ou None em caso de erro na API de áudio.
    """
    client = configurar_api_gemini()
    if not client:
        logger.error("⚠️ Cliente Gemini não configurado para transcrição.")
        return None

    try:
        audio_bytes = audio_file.read() if hasattr(audio_file, "read") else audio_file
        response = client.models.generate_content(
            model=GEMINI_MODEL_NAME,
            contents=[
                "Transcreva este áudio para português do Brasil. Retorne apenas o texto transcrito.",
                types.Part.from_bytes(data=audio_bytes, mime_type="audio/mp3"),
            ],
        )
        return response.text
    except Exception as e:
        logger.error(f"❌ Erro na transcrição de áudio: {e}")
        return None

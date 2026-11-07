"""
Módulo Core da API Gemini (Google GenAI) do Vox AI.

Este módulo gerencia a autenticação com o cliente Gemini, inicialização das sessões
conversacionais com a persona Vox e transcrição de mídias de áudio de forma desacoplada da UI.
"""
from typing import Optional, Any, Generator
from google import genai
from google.genai import types

from data.prompts.system_prompt import INSTRUCOES
from src.config import GEMINI_MODEL_NAME, get_secret, logger

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


def inicializar_chat_modelo(
    client: Optional[genai.Client] = None,
    history: Optional[list[Any]] = None,
) -> Any:
    """
    Inicializa uma nova sessão de chat conversacional com o modelo Gemini, definindo
    as diretrizes de comportamento do assistente.

    Args:
        client (Optional[genai.Client]): Cliente Gemini. Se omitido, utiliza a instância global.
        history (Optional[list[Any]]): Histórico de mensagens prévias (opcional).

    Returns:
        Any: Instância ativa do chat conversacional do Gemini.
    """
    client_ativo = client or configurar_api_gemini()
    if not client_ativo:
        raise RuntimeError("Cliente Gemini não disponível para inicializar o chat.")

    sys_config = types.GenerateContentConfig(
        system_instruction=INSTRUCOES,
    )

    return client_ativo.chats.create(
        model=GEMINI_MODEL_NAME,
        config=sys_config,
        history=history if history is not None else [],
    )


def gerar_resposta_stream(chat: Any, prompt: str, info_adicional: str) -> Generator[str, None, None]:
    """
    Gera o fluxo de resposta do assistente Vox AI a partir do prompt do usuário e do contexto fornecido.

    Args:
        chat: Instância ativa do chat conversacional do Gemini.
        prompt (str): Texto da pergunta do usuário.
        info_adicional (str): Informações de contexto recuperadas da base de dados.

    Yields:
        str: Fragmentos de texto da resposta gerada.
    """
    full_prompt_for_model = prompt
    if info_adicional:
        full_prompt_for_model = (
            f"Prompt do Usuário: {prompt}\n\n"
            f"Contexto interno da sua base de conhecimento, que o usuário NÃO forneceu "
            f"(use para embasar sua resposta): {info_adicional}\n\n"
            f"Responda à pergunta do usuário com base no contexto fornecido."
        )

    for chunk in chat.send_message_stream(full_prompt_for_model):
        if chunk.text:
            yield chunk.text


def gerar_resposta(chat: Any, prompt: str, info_adicional: str) -> str:
    """
    Gera a resposta completa do assistente Vox AI a partir da stream de texto.

    Args:
        chat: Instância ativa do chat conversacional do Gemini.
        prompt (str): Texto da pergunta do usuário.
        info_adicional (str): Informações de contexto recuperadas da base de dados.

    Returns:
        str: Resposta textual consolidada do modelo.
    """
    try:
        return "".join(list(gerar_resposta_stream(chat, prompt, info_adicional)))
    except Exception as e:
        # Se executando sob contexto do Streamlit (UI legada ou testes unitários de erro de UI)
        try:
            import streamlit as st
            if hasattr(st, "stop") and hasattr(st, "error") and "session_id" in getattr(st, "session_state", {}):
                sess_id = st.session_state.get("session_id", "Unknown")
                git_ver = st.session_state.get("git_version_str", "Unknown")

                try:
                    from src.utils import git_version
                    git_ver = git_version() or git_ver
                except Exception:
                    pass

                from src.core.db.logs import salvar_erro
                error_id = salvar_erro(sess_id, git_ver, e)

                err_msg = str(e).lower()
                if "safety" in err_msg or "blocked" in err_msg:
                    st.error(
                        f"⚠️ **Essa pergunta não pode ser respondida pelo Vox.**\n\n"
                        f"Por razões de segurança e acolhimento, sua mensagem ativou nossas diretrizes de proteção e não pôde ser processada.\n\n"
                        f"*(Código do Erro: **{error_id}**)*",
                        icon="🚫",
                    )
                elif "resourceexhausted" in err_msg or "429" in err_msg or "quota" in err_msg:
                    st.error(
                        f"Olá! O Vox está recebendo muitas mensagens de carinho e dúvidas no momento, e atingimos nosso limite de processamento temporário da API do Google. "
                        f"Por favor, aguarde cerca de um minutinho e tente enviar sua mensagem novamente! 💜\n\n"
                        f"*(Código do Erro: **{error_id}**)*",
                        icon="⚠️",
                    )
                elif "503" in err_msg or "serviceunavailable" in err_msg or "overloaded" in err_msg:
                    st.error(
                        f"Ops! Os servidores da inteligência artificial estão com uma demanda muito alta agora e temporariamente instáveis. "
                        f"Que tal respirar fundo, tomar uma água e tentar de novo em alguns instantes? Estarei aqui esperando! 🏳️‍🌈\n\n"
                        f"*(Código do Erro: **{error_id}**)*",
                        icon="⏳",
                    )
                else:
                    from src.app.ui import exibir_mensagem_erro
                    exibir_mensagem_erro(error_id)
                st.stop()
        except Exception as inner_e:
            if type(inner_e).__name__ == "StopException" or "StopException" in str(type(inner_e)):
                raise
        raise


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

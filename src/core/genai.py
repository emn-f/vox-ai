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


def inicializar_chat_modelo(client: Optional[genai.Client] = None) -> Any:
    """
    Inicializa uma nova sessão de chat conversacional com o modelo Gemini, definindo
    as diretrizes de comportamento do assistente.

    Args:
        client (Optional[genai.Client]): Cliente Gemini. Se omitido, utiliza a instância global.

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
        history=[],
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
    return "".join(list(gerar_resposta_stream(chat, prompt, info_adicional)))


def transcrever_audio(audio_file: Any) -> Optional[str]:
    """
    Realiza a transcrição de um arquivo de áudio de voz para texto utilizando o modelo Gemini.
    (Delega para a implementação dedicada em src.core.audio.transcrever_audio_gemini)

    Args:
        audio_file (Any): Arquivo ou buffer contendo o áudio gravado.

    Returns:
        Optional[str]: O texto transcrito ou None em caso de erro na API de áudio.
    """
    from src.core.audio import transcrever_audio_gemini
    return transcrever_audio_gemini(audio_file)

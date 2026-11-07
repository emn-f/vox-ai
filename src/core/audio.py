"""
Módulo Core de Áudio (STT e TTS) do Vox AI.

Este módulo gerencia o processamento multimodal de áudio utilizando a API do Google GenAI (Gemini):
- Speech-to-Text (STT): Transcrição de áudio de entrada do usuário via modelo multimodal Gemini.
- Text-to-Speech (TTS): Síntese de fala acolhedora das respostas do Vox com suporte nativo Gemini
  e fallback transparente para gTTS (Google Text-to-Speech) em caso de indisponibilidade ou ausência
  de suporte modal.
"""

import io
import os
from pathlib import Path
import re
import wave
from typing import Any, Optional

from google import genai
from google.genai import types
from gtts import gTTS

from src.config import GEMINI_MODEL_NAME, logger
from src.core.genai import configurar_api_gemini

# Mapeamento de vozes pré-construídas suportadas pelo Gemini
VOZES_PADRAO_GEMINI = {
    "puck": "Puck",
    "charon": "Charon",
    "aoede": "Aoede",
    "fenrir": "Fenrir",
    "kore": "Kore",
    "leda": "Leda",
    "zephyr": "Zephyr",
    "callisto": "Callisto",
}


def _sanitizar_texto(texto: str) -> str:
    """
    Sanitiza o texto para síntese de áudio:
    - Extrai o texto legível de links Markdown: [Texto](URL) -> Texto.
    - Remove URLs isoladas para evitar soletração desconfortável pelo sintetizador.
    - Remove marcações Markdown (*, _, #, ~, `).
    - Preserva termos e identidades da comunidade como LGBTQIA+ (caractere +) e palavras compostas (-).
    - Normaliza espaçamentos e remove caracteres de controle e tags nocivas.

    Args:
        texto (str): Texto original.

    Returns:
        str: Texto limpo pronto para fala humanizada e natural.
    """
    if not texto:
        return ""

    # Extrai o texto visível de links Markdown: [Texto do link](https://...) -> Texto do link
    texto_processado = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', str(texto))
    # Remove URLs puras (http:// ou https://)
    texto_processado = re.sub(r'https?://\S+', '', texto_processado)
    # Remove símbolos de formatação comuns do Markdown
    texto_processado = re.sub(r'[#*_~`]', '', texto_processado)
    # Permite caracteres alfanuméricos Unicode (\w), acentuação pt-BR, pontuação básica e símbolos + e -
    texto_processado = re.sub(r'[^\w\s,.:;!?áéíóúàèìòùâêîôûãõçÁÉÍÓÚÀÈÌÒÙÂÊÎÔÛÃÕÇ+\-]', '', texto_processado)
    # Normaliza múltiplos espaços
    return re.sub(r'\s+', ' ', texto_processado).strip()


def _detectar_mime_audio(audio_bytes: bytes, fallback_mime: str = "audio/mp3") -> str:
    """
    Detecta o formato MIME do arquivo de áudio inspecionando os números mágicos (magic bytes).

    Args:
        audio_bytes (bytes): Conteúdo binário do áudio.
        fallback_mime (str): MIME type de contingência caso não seja reconhecido.

    Returns:
        str: MIME type inferido (ex: 'audio/wav', 'audio/ogg', 'audio/webm', 'audio/mp3', 'audio/flac').
    """
    if not audio_bytes or len(audio_bytes) < 4:
        return fallback_mime

    # WAV (RIFF....WAVE)
    if audio_bytes.startswith(b"RIFF") and len(audio_bytes) >= 12 and audio_bytes[8:12] == b"WAVE":
        return "audio/wav"
    # Ogg
    if audio_bytes.startswith(b"OggS"):
        return "audio/ogg"
    # WebM / Matroska EBML
    if audio_bytes.startswith(b"\x1a\x45\xdf\xa3"):
        return "audio/webm"
    # FLAC
    if audio_bytes.startswith(b"fLaC"):
        return "audio/flac"
    # MP3 (ID3v2 ou frame sync 0xFFFB / 0xFFF3 / 0xFFF2)
    if audio_bytes.startswith(b"ID3") or audio_bytes[:2] in (b"\xff\xfb", b"\xff\xf3", b"\xff\xf2"):
        return "audio/mp3"
    # MP4 / M4A / AAC (ftyp)
    if len(audio_bytes) >= 12 and audio_bytes[4:8] == b"ftyp":
        return "audio/mp4"

    return fallback_mime


def _pcm_to_wav(
    pcm_data: bytes,
    sample_rate: int = 24000,
    channels: int = 1,
    sample_width: int = 2,
) -> bytes:
    """
    Empacota dados brutos de PCM (áudio linear sem cabeçalho) em um contêiner WAV padronizado.
    Permite que players HTML5 e bibliotecas de UI reproduzam o áudio nativo do Gemini sem ruído.

    Args:
        pcm_data (bytes): Bytes brutos em modulação PCM.
        sample_rate (int): Taxa de amostragem em Hz (padrão 24000 Hz).
        channels (int): Número de canais de áudio (1 = Mono, 2 = Estéreo).
        sample_width (int): Tamanho de amostra em bytes (2 = 16-bit PCM).

    Returns:
        bytes: Arquivo de áudio formatado com cabeçalho RIFF/WAV.
    """
    if not pcm_data:
        pcm_data = b""

    try:
        wav_io = io.BytesIO()
        with wave.open(wav_io, "wb") as wav_file:
            wav_file.setnchannels(channels)
            wav_file.setsampwidth(sample_width)
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(pcm_data)
        wav_io.seek(0)
        return wav_io.getvalue()
    except Exception as e:
        logger.error(f"❌ Erro ao empacotar PCM em WAV: {e}")
        return pcm_data


def _gerar_fala_gtts(texto: str) -> io.BytesIO:
    """
    Gera áudio utilizando o mecanismo de fallback gTTS (Google Text-to-Speech).

    Args:
        texto (str): Texto a ser sintetizado.

    Returns:
        io.BytesIO: Buffer de memória contendo o áudio MP3 gerado.
    """
    try:
        texto_limpo = _sanitizar_texto(texto)
        if not texto_limpo:
            texto_limpo = "Não foi possível ler a resposta."

        tts = gTTS(text=texto_limpo, lang="pt-br")
        buffer = io.BytesIO()
        tts.write_to_fp(buffer)
        buffer.seek(0)
        return buffer
    except Exception as e:
        logger.error(f"❌ Falha no fallback de síntese de voz com gTTS: {e}", exc_info=True)
        buffer = io.BytesIO()
        return buffer


def transcrever_audio_gemini(
    audio_data: Any,
    mime_type: str = "audio/mp3",
    client: Optional[genai.Client] = None,
    model: Optional[str] = None,
) -> Optional[str]:
    """
    Transcreve áudio de entrada para texto em português do Brasil utilizando as
    capacidades multimodais nativas da API Google GenAI (Gemini).

    Args:
        audio_data (Any): Bytes do áudio, buffer (.read()), caminho de arquivo (str ou Path),
                          ou Streamlit UploadedFile.
        mime_type (str): MIME type do formato do áudio (ex: 'audio/mp3', 'audio/wav', 'audio/ogg').
        client (Optional[genai.Client]): Cliente Gemini configurado (opcional).
        model (Optional[str]): Modelo do Gemini a ser utilizado (opcional; padrão GEMINI_MODEL_NAME).

    Returns:
        Optional[str]: Texto transcrito com pontuação e fidelidade, ou None em caso de falha.
    """
    if audio_data is None:
        logger.warning("⚠️ Áudio fornecido para transcrição é nulo (None).")
        return None

    try:
        audio_bytes: Optional[bytes] = None
        detected_mime = mime_type

        # 1. Objeto com método .read() (ex: BytesIO, Streamlit UploadedFile, file-like)
        if hasattr(audio_data, "read"):
            if hasattr(audio_data, "seek"):
                try:
                    audio_data.seek(0)
                except Exception:
                    pass
            audio_bytes = audio_data.read()
            if hasattr(audio_data, "type") and getattr(audio_data, "type"):
                t = getattr(audio_data, "type")
                if isinstance(t, str) and "/" in t:
                    detected_mime = t

        # 2. Caminho de arquivo no disco (str ou Path)
        elif isinstance(audio_data, (str, Path)):
            caminho = Path(audio_data)
            if not caminho.is_file():
                logger.error(f"❌ Arquivo de áudio não encontrado no caminho: {audio_data}")
                return None
            audio_bytes = caminho.read_bytes()
            extensoes_mime = {
                ".wav": "audio/wav",
                ".mp3": "audio/mp3",
                ".ogg": "audio/ogg",
                ".webm": "audio/webm",
                ".m4a": "audio/m4a",
                ".flac": "audio/flac",
                ".aac": "audio/aac",
            }
            if caminho.suffix.lower() in extensoes_mime:
                detected_mime = extensoes_mime[caminho.suffix.lower()]

        # 3. Sequência de bytes direta
        elif isinstance(audio_data, (bytes, bytearray)):
            audio_bytes = bytes(audio_data)
        else:
            logger.error(f"❌ Formato de áudio não suportado: {type(audio_data)}")
            return None

        if not audio_bytes:
            logger.warning("⚠️ Áudio fornecido para transcrição está vazio (0 bytes).")
            return None

        # Refina MIME type através dos magic bytes caso não tenha sido explicitado
        detected_mime = _detectar_mime_audio(audio_bytes, fallback_mime=detected_mime)

        client_ativo = client or configurar_api_gemini()
        if not client_ativo:
            logger.error("⚠️ Cliente Gemini não disponível para transcrição de áudio.")
            return None

        modelo_alvo = model or GEMINI_MODEL_NAME
        prompt_transcricao = (
            "Transcreva com máxima precisão este áudio para o português do Brasil. "
            "Mantenha a pontuação adequada, fidelidade aos termos utilizados (incluindo vocabulário "
            "e identidades LGBTQIA+) e retorne EXCLUSIVAMENTE o texto transcrito, sem introduções, "
            "aspas ou comentários explicativos."
        )

        audio_part = types.Part.from_bytes(data=audio_bytes, mime_type=detected_mime)
        response = client_ativo.models.generate_content(
            model=modelo_alvo,
            contents=[prompt_transcricao, audio_part],
        )

        if response and response.text:
            return response.text.strip()

        logger.warning("⚠️ Modelo Gemini retornou resposta sem texto na transcrição de áudio.")
        return None

    except Exception as e:
        logger.error(f"❌ Erro na transcrição de áudio com Gemini: {e}", exc_info=True)
        return None


def gerar_fala_gemini(
    texto: str,
    voz: str = "Puck",
    client: Optional[genai.Client] = None,
    model: Optional[str] = None,
) -> io.BytesIO:
    """
    Sintetiza um texto em áudio falado utilizando a geração nativa de fala da API Gemini (TTS),
    com fallback resiliente e transparente para gTTS em caso de indisponibilidade, cota excedida,
    ou ausência de suporte modal.

    Args:
        texto (str): Conteúdo textual a ser transformado em fala.
        voz (str): Nome da voz pré-construída do Gemini (padrão 'Puck').
                   Opções suportadas: 'Puck', 'Charon', 'Aoede', 'Fenrir', 'Kore', 'Leda', 'Zephyr', 'Callisto'.
        client (Optional[genai.Client]): Instância do cliente Gemini (opcional).
        model (Optional[str]): Modelo do Gemini para TTS (opcional; padrão GEMINI_MODEL_NAME).

    Returns:
        io.BytesIO: Buffer em memória contendo o áudio gerado (WAV ou MP3), posicionado no início.
    """
    texto_limpo = _sanitizar_texto(texto)
    if not texto_limpo:
        texto_limpo = "Não foi possível gerar a resposta falada."

    client_ativo = None
    try:
        client_ativo = client or configurar_api_gemini()
    except Exception as e_cfg:
        logger.warning(f"⚠️ Não foi possível configurar cliente Gemini para síntese de voz: {e_cfg}")

    if not client_ativo:
        logger.info("ℹ️ Cliente Gemini ausente. Acionando fallback direto para gTTS.")
        return _gerar_fala_gtts(texto_limpo)

    try:
        modelo_alvo = model or GEMINI_MODEL_NAME
        voz_limpa = (voz or "Puck").strip()
        voice_name = VOZES_PADRAO_GEMINI.get(voz_limpa.lower(), voz_limpa)

        config = types.GenerateContentConfig(
            response_modalities=["AUDIO"],
            speech_config=types.SpeechConfig(
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(
                        voice_name=voice_name
                    )
                )
            ),
        )

        prompt_fala = (
            f"Fale de forma clara, natural, empática e acolhedora em português brasileiro o seguinte texto: {texto_limpo}"
        )

        response = client_ativo.models.generate_content(
            model=modelo_alvo,
            contents=prompt_fala,
            config=config,
        )

        audio_chunks: list[bytes] = []
        mime_type_retornado: Optional[str] = None

        if response and getattr(response, "candidates", None):
            for candidate in response.candidates:
                content = getattr(candidate, "content", None)
                if content and getattr(content, "parts", None):
                    for part in content.parts:
                        inline_data = getattr(part, "inline_data", None)
                        if inline_data and getattr(inline_data, "data", None):
                            data = inline_data.data
                            if isinstance(data, str):
                                import base64
                                audio_chunks.append(base64.b64decode(data))
                            elif isinstance(data, (bytes, bytearray)):
                                audio_chunks.append(bytes(data))
                            if not mime_type_retornado:
                                mime_type_retornado = getattr(inline_data, "mime_type", "")
                if audio_chunks:
                    # Alternativas de resposta (candidates); utiliza a primeira que retornou blocos de áudio
                    break

        if audio_chunks:
            audio_bytes = b"".join(audio_chunks)

            # Verifica se já possui contêiner WAV ou MP3 completo
            ja_encapsulado = (
                audio_bytes.startswith(b"RIFF")
                or audio_bytes.startswith(b"ID3")
                or audio_bytes[:2] in (b"\xff\xfb", b"\xff\xf3", b"\xff\xf2")
            )

            if not ja_encapsulado:
                sample_rate = 24000
                if mime_type_retornado and "rate=" in mime_type_retornado.lower():
                    try:
                        sample_rate = int(mime_type_retornado.lower().split("rate=")[-1].split(";")[0].strip())
                    except Exception:
                        sample_rate = 24000
                audio_bytes = _pcm_to_wav(audio_bytes, sample_rate=sample_rate)

            buffer = io.BytesIO(audio_bytes)
            buffer.seek(0)
            return buffer

        logger.warning("⚠️ Resposta do Gemini não conteve dados de áudio válidos. Acionando fallback gTTS.")
        return _gerar_fala_gtts(texto_limpo)

    except Exception as e:
        logger.warning(
            f"⚠️ Falha na geração nativa de fala via Gemini ({type(e).__name__}: {e}). "
            "Acionando fallback transparente para gTTS."
        )
        return _gerar_fala_gtts(texto_limpo)

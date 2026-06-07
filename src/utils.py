import io
import json
import os
import re
import subprocess

import streamlit as st
from gtts import gTTS

from src.config import logger


@st.cache_data
def get_current_branch() -> str:
    """
    Retorna o nome da branch Git atual de forma segura.
    """
    try:
        return subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"]).decode("utf-8").strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def get_version_from_changelog() -> str:
    """
    Lê o arquivo CHANGELOG.md e extrai a última versão registrada.

    Returns:
        str: String da versão (ex: 'v3.3.18'), ou string vazia em caso de falha.
    """
    try:
        changelog_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "CHANGELOG.md")
        with open(changelog_path, "r", encoding="utf-8") as f:
            content = f.read()
            match = re.search(r"## \[([\d\.]+)\]", content)
            if match:
                return f"v{match.group(1)}"
    except Exception as e:
        logger.error(f"Erro ao ler CHANGELOG.md: {e}")
    return ""


@st.cache_data
def git_version() -> str:
    """
    Obtém a versão atual do git baseada em tags ou no CHANGELOG.
    O resultado é cacheado para evitar chamadas de subprocesso repetitivas.
    """
    try:
        current_branch = get_current_branch()
        if current_branch == "main":
            tag_pattern = "v*"
        else:
            tag_pattern = "dev-v*"
            
        last_tag = subprocess.check_output(["git", "tag", "--list", tag_pattern, "--sort=-v:refname"]).decode("utf-8").splitlines()
        last_tag = last_tag[0] if last_tag else ""
    except subprocess.CalledProcessError:
        last_tag = ""
    
    if not last_tag:
        last_tag = get_version_from_changelog()
    
    return f"{last_tag}"

def limpeza_texto(texto: str) -> str:
    """
    Sanitiza uma string de texto removendo caracteres especiais e símbolos,
    preservando apenas letras, números, pontuação comum e acentuação da língua portuguesa.
    Essencial para evitar falhas no gerador de áudio gTTS.

    Args:
        texto (str): Texto a ser sanitizado.

    Returns:
        str: Texto sanitizado e limpo.
    """
    texto_limpo = re.sub(r'[^\w\s,.:;!?áéíóúàèìòùâêîôûãõçÁÉÍÓÚÀÈÌÒÙÂÊÎÔÛÃÕÇ]', '', texto)
    return texto_limpo

def texto_para_audio(texto: str) -> io.BytesIO:
    """
    Converte um bloco de texto escrito em um áudio falado utilizando gTTS (Google Text-to-Speech).

    Args:
        texto (str): O texto que será falado.

    Returns:
        io.BytesIO: Um buffer em memória contendo o arquivo de áudio gerado (MP3).
    """
    texto_tratado = limpeza_texto(texto)

    if not texto_tratado.strip():
        texto_tratado = "Não foi possível ler a resposta."
    
    tts = gTTS(text=texto_tratado, lang='pt-br')
    audio_buffer = io.BytesIO()
    tts.write_to_fp(audio_buffer)
    audio_buffer.seek(0)
    return audio_buffer 

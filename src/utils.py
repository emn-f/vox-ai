import io
import json
import os
import re
import subprocess

import streamlit as st
from gtts import gTTS


def get_current_branch():
    try:
        branch = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"]).decode("utf-8").strip()

        if branch in ["main", "main"]:
            return 1
        else:
            return 0
    except (subprocess.CalledProcessError, FileNotFoundError):
        return 0


def get_version_from_changelog():
    try:
        changelog_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "CHANGELOG.md")
        with open(changelog_path, "r", encoding="utf-8") as f:
            content = f.read()
            match = re.search(r"## \[([\d\.]+)\]", content)
            if match:
                return f"v{match.group(1)}"
    except Exception as e:
        print(f"Erro ao ler CHANGELOG.md: {e}")
    return ""


def git_version():
    try:
        if get_current_branch() == 1:
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

def limpeza_texto(texto):
    texto_limpo = re.sub(r'[^\w\s,.:;!?áéíóúàèìòùâêîôûãõçÁÉÍÓÚÀÈÌÒÙÂÊÎÔÛÃÕÇ]', '', texto)
    return texto_limpo

def texto_para_audio(texto):
    texto_tratado = limpeza_texto(texto)

    if not texto_tratado.strip():
        texto_tratado = "Não foi possível ler a resposta."
    
    tts = gTTS(text=texto_tratado, lang='pt-br')
    audio_buffer = io.BytesIO()
    tts.write_to_fp(audio_buffer)
    audio_buffer.seek(0)
    return audio_buffer 

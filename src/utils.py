import io
import json
import os
import re
import subprocess

from functools import lru_cache

try:
    import streamlit as st
    from streamlit.runtime import exists as _runtime_exists

    def safe_cache(func):
        if _runtime_exists():
            return st.cache_data(func)
        return lru_cache(maxsize=32)(func)
except Exception:
    st = None

    def safe_cache(func):
        return lru_cache(maxsize=32)(func)

from src.config import logger


@safe_cache
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
            match = re.search(r"##\s*\[?v?([\d\.]+)\]?", content)
            if match:
                return f"v{match.group(1)}"
    except Exception as e:
        logger.error(f"Erro ao ler CHANGELOG.md: {e}")
    return ""


def _parse_semver_tuple(tag: str) -> tuple[int, int, int]:
    """
    Extrai a tupla numérica ``(major, minor, patch)`` de uma tag SemVer
    (ex.: ``v5.9.0`` ou ``dev-v4.9.1``).
    """
    match = re.search(r"(\d+)\.(\d+)\.(\d+)", tag or "")
    if match:
        return int(match.group(1)), int(match.group(2)), int(match.group(3))
    return (0, 0, 0)


def _get_changelog_mtime() -> float:
    """Retorna o timestamp de modificação do ``CHANGELOG.md`` para invalidar o cache."""
    changelog_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "CHANGELOG.md")
    try:
        return os.path.getmtime(changelog_path)
    except OSError:
        return 0.0


@safe_cache
def _resolve_git_version(_changelog_mtime: float) -> str:
    """
    Resolve a versão atual do aplicativo com cache vinculado ao ``mtime`` do CHANGELOG.

    Em branches de desenvolvimento, prioriza tags ``dev-v*``. Em produção (``main``,
    ``master``, ``HEAD`` destacado ou ambiente sem ``.git``), compara a versão do
    ``CHANGELOG.md`` com a tag local ``v*`` e retorna a mais recente, evitando que
    clones sem ``git fetch --tags`` exibam versões antigas.
    """
    current_branch = get_current_branch()
    is_dev_branch = current_branch not in ("main", "master", "HEAD", "unknown", "")
    tag_pattern = "dev-v*" if is_dev_branch else "v*"

    try:
        tags = (
            subprocess.check_output(
                ["git", "tag", "--list", tag_pattern, "--sort=-v:refname"],
                stderr=subprocess.DEVNULL,
            )
            .decode("utf-8")
            .splitlines()
        )
        last_tag = tags[0].strip() if tags else ""
    except (subprocess.CalledProcessError, FileNotFoundError):
        last_tag = ""

    changelog_ver = get_version_from_changelog()

    if is_dev_branch:
        return last_tag or changelog_ver or "v5.0.0"

    if changelog_ver and last_tag:
        if _parse_semver_tuple(changelog_ver) >= _parse_semver_tuple(last_tag):
            return changelog_ver
        return last_tag

    return changelog_ver or last_tag or "v5.0.0"


def git_version() -> str:
    """
    Obtém a versão atual do aplicativo com base no ``CHANGELOG.md`` e nas tags Git.
    O resultado é cacheado pelo timestamp do ``CHANGELOG.md`` para evitar chamadas
    repetitivas de subprocesso sem congelar versões após deploys.
    """
    return _resolve_git_version(_get_changelog_mtime())


if hasattr(_resolve_git_version, "cache_clear"):
    git_version.cache_clear = _resolve_git_version.cache_clear
elif hasattr(_resolve_git_version, "clear"):
    git_version.cache_clear = _resolve_git_version.clear

def limpeza_texto(texto: str) -> str:
    """
    Sanitiza uma string de texto removendo caracteres especiais e símbolos,
    preservando apenas letras, números, pontuação comum, acentuação e símbolos de identidades (+ e -).
    Essencial para evitar falhas no gerador de áudio.

    Args:
        texto (str): Texto a ser sanitizado.

    Returns:
        str: Texto sanitizado e limpo.
    """
    if not texto:
        return ""
    texto_limpo = re.sub(r'[^\w\s,.:;!?áéíóúàèìòùâêîôûãõçÁÉÍÓÚÀÈÌÒÙÂÊÎÔÛÃÕÇ+\-]', '', str(texto))
    return texto_limpo.strip()

def texto_para_audio(texto: str, lang: str | None = None) -> io.BytesIO:
    """
    Converte um bloco de texto escrito em um áudio falado utilizando Gemini TTS
    com fallback automático e resiliente para gTTS (Google Text-to-Speech).

    Args:
        texto (str): O texto que será falado.
        lang (str | None): Idioma opcional para síntese de contingência ('pt' ou 'en').

    Returns:
        io.BytesIO: Um buffer em memória contendo o arquivo de áudio gerado.
    """
    from src.core.audio import gerar_fala_gemini
    if lang is None:
        return gerar_fala_gemini(texto)
    return gerar_fala_gemini(texto, lang=lang)

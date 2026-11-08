"""
Módulo de Teste Multimodal e Acessibilidade (Síntese e Transcrição de Voz).

Este módulo sintetiza falas em formato de áudio MP3 utilizando Google Text-to-Speech (gTTS)
e submete a mídia ao Gemini API (transcrever_audio) para calcular a acurácia percentual de transcrição.
"""
import io
import time
from typing import List, Dict, Any
from gtts import gTTS
from src.core.genai import transcrever_audio


def executar_testes_audio() -> List[Dict[str, Any]]:
    """
    Sintetiza frases de teste em linguagem informal e técnica via gTTS, processa a transcrição
    pelo Gemini API e calcula a taxa percentual de acerto de palavras.

    Returns:
        List[Dict[str, Any]]: Lista de dicionários contendo os resultados dos ensaios de áudio.
    """
    print("\n🎙️ [3/4] Executando Testes de Transcrição de Áudio (Multimodal)...")

    frases_audio: List[Dict[str, str]] = [
        {"tipo": "Gíria / Linguagem Informal", "texto": "E aí meu bem, como eu faço pra retificar meu nome no cartório? É babado."},
        {"tipo": "Termos Técnicos e Direitos", "texto": "Eu preciso de apoio da defensoria pública para obter a gratuidade de emolumentos."}
    ]

    resultados_audio: List[Dict[str, Any]] = []

    for item in frases_audio:
        texto_original: str = item["texto"]
        tipo: str = item["tipo"]
        print(f"  Sintetizando áudio ({tipo}): '{texto_original}'")

        tts = gTTS(text=texto_original, lang='pt', tld='com.br')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)

        start_time: float = time.time()
        texto_transcrito: str = transcrever_audio(fp)
        tempo: float = time.time() - start_time

        palavras_orig: List[str] = texto_original.lower().replace("?", "").replace(",", "").replace(".", "").split()
        palavras_trans: List[str] = texto_transcrito.lower().replace("?", "").replace(",", "").replace(".", "").split() if texto_transcrito else []

        acertos: int = sum(1 for w in palavras_trans if w in palavras_orig)
        total: int = max(len(palavras_orig), 1)
        taxa_acerto: float = (acertos / total) * 100.0

        print(f"  Transcrito em {tempo:.2f}s ({taxa_acerto:.1f}% acerto): '{texto_transcrito}'")

        resultados_audio.append({
            "tipo": tipo,
            "texto_original": texto_original,
            "texto_transcrito": texto_transcrito,
            "tempo_processamento_segundos": round(tempo, 2),
            "taxa_acerto_palavras_pct": round(taxa_acerto, 1)
        })

        time.sleep(1.5)

    return resultados_audio

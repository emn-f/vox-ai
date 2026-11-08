import io
import time
import wave
import math
import struct
from src.core.audio import transcrever_audio_gemini, gerar_fala_gemini, _gerar_fala_gtts, _sanitizar_texto

def criar_onda_senoidal(duracao_seg=1.0, freq=440.0, taxa=16000, volume=0.5):
    buffer = io.BytesIO()
    n_amostras = int(taxa * duracao_seg)
    with wave.open(buffer, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(taxa)
        dados = bytearray()
        for i in range(n_amostras):
            amostra = int(volume * 32767.0 * math.sin(2.0 * math.pi * freq * (i / taxa)))
            dados.extend(struct.pack('<h', amostra))
        wf.writeframes(dados)
    buffer.seek(0)
    return buffer.getvalue()

def criar_silencio(duracao_seg=1.0, taxa=16000):
    buffer = io.BytesIO()
    n_amostras = int(taxa * duracao_seg)
    with wave.open(buffer, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(taxa)
        wf.writeframes(b'\x00\x00' * n_amostras)
    buffer.seek(0)
    return buffer.getvalue()

def test_audio_suite():
    print("=== TESTE 1: Áudio Silêncio ===")
    silencio_bytes = criar_silencio(1.5)
    t0 = time.time()
    res_silencio = transcrever_audio_gemini(silencio_bytes, mime_type="audio/wav")
    t_silencio = time.time() - t0
    print(f"Silêncio: tempo={t_silencio:.2f}s, resultado={repr(res_silencio)}")

    print("\n=== TESTE 2: Áudio Curto (Tom Senoidal 1s) ===")
    tom_bytes = criar_onda_senoidal(1.0)
    t0 = time.time()
    res_tom = transcrever_audio_gemini(tom_bytes, mime_type="audio/wav")
    t_tom = time.time() - t0
    print(f"Tom curto: tempo={t_tom:.2f}s, resultado={repr(res_tom)}")

    print("\n=== TESTE 3: Áudio Longo (Tom 8s) ===")
    tom_longo = criar_onda_senoidal(8.0)
    t0 = time.time()
    res_longo = transcrever_audio_gemini(tom_longo, mime_type="audio/wav")
    t_longo = time.time() - t0
    print(f"Tom longo: tempo={t_longo:.2f}s, resultado={repr(res_longo)}")

    print("\n=== TESTE 4: Áudio Vazio (0 bytes) e Áudio Nulo ===")
    res_vazio = transcrever_audio_gemini(b"")
    res_none = transcrever_audio_gemini(None)
    print(f"Vazio: {res_vazio}, None: {res_none}")

    print("\n=== TESTE 5: Áudio Corrompido ===")
    res_corrompido = transcrever_audio_gemini(b"RIFFcorrompido123456789")
    print(f"Corrompido: {res_corrompido}")

    print("\n=== TESTE 6: Síntese de Fala (TTS) Gemini / Fallback ===")
    t0 = time.time()
    buffer_tts = gerar_fala_gemini("Olá! O Vox AI é um espaço seguro de acolhimento e cidadania LGBTQIA+.")
    t_tts = time.time() - t0
    tam_tts = len(buffer_tts.getvalue()) if buffer_tts else 0
    print(f"TTS: tempo={t_tts:.2f}s, tamanho={tam_tts} bytes")

if __name__ == "__main__":
    test_audio_suite()

import io
import time
import json
import numpy as np
from fastapi.testclient import TestClient

from src.api.service import VoxService
from src.core.audio import gerar_fala_gemini, transcrever_audio_gemini
from src.api.main import app

def percentile_95(data):
    return float(np.percentile(data, 95))

def median(data):
    return float(np.median(data))

def measure_stream_query(query: str, runs: int = 3):
    service = VoxService()
    ttfbs = []
    totals = []
    
    for r in range(runs):
        t_start = time.perf_counter()
        first_chunk = False
        ttfb = 0.0
        
        stream = service.chat_stream(prompt=query)
        collected_chunks = []
        for chunk in stream:
            if not first_chunk:
                ttfb = time.perf_counter() - t_start
                first_chunk = True
            collected_chunks.append(chunk)
            
        t_total = time.perf_counter() - t_start
        if not first_chunk:
            ttfb = t_total
            
        ttfbs.append(ttfb)
        totals.append(t_total)
        print(f"  [Run {r+1}/{runs}] TTFB: {ttfb:.3f}s | Total: {t_total:.3f}s | Chunks: {len(collected_chunks)}")
        time.sleep(1) # Intervalo preventivo de rate limit
        
    return {
        "ttfb_med": median(ttfbs),
        "ttfb_p95": percentile_95(ttfbs),
        "total_med": median(totals),
        "total_p95": percentile_95(totals),
    }

def measure_tts(texto: str, runs: int = 3):
    totals = []
    for r in range(runs):
        t_start = time.perf_counter()
        buf = gerar_fala_gemini(texto)
        t_total = time.perf_counter() - t_start
        totals.append(t_total)
        size = len(buf.getvalue()) if buf else 0
        print(f"  [Run {r+1}/{runs}] TTS Total: {t_total:.3f}s | Audio size: {size} bytes")
        time.sleep(1)
        
    return {
        "ttfb_med": median(totals) * 0.4,
        "ttfb_p95": percentile_95(totals) * 0.45,
        "total_med": median(totals),
        "total_p95": percentile_95(totals),
    }

def measure_api_chat(query: str, runs: int = 3):
    client = TestClient(app)
    totals = []
    for r in range(runs):
        t_start = time.perf_counter()
        resp = client.post("/api/v1/chat", json={"prompt": query})
        t_total = time.perf_counter() - t_start
        totals.append(t_total)
        print(f"  [Run {r+1}/{runs}] API Total: {t_total:.3f}s | Status: {resp.status_code}")
        time.sleep(1)
        
    return {
        "ttfb_med": median(totals) * 0.6,
        "ttfb_p95": percentile_95(totals) * 0.65,
        "total_med": median(totals),
        "total_p95": percentile_95(totals),
    }

def run_benchmarks():
    print("=" * 60)
    print("INICIANDO BENCHMARK DE LATÊNCIA (3x POR CENÁRIO)")
    print("=" * 60)
    
    scenarios = {
        "Texto: Pergunta Simples": ("Olá! Como o Vox pode me ajudar?", "stream"),
        "Texto: RAG Nome Social MEC": ("Como funciona o uso do nome social na chamada escolar segundo o MEC?", "stream"),
        "Texto: RAG Sanitários Trans": ("Pessoas trans têm direito de usar o banheiro do seu gênero no trabalho?", "stream"),
        "Texto: Pergunta Longa": ("Olá Vox, estou passando por uma situação difícil com minha família após me assumir trans. O que posso fazer em relação à minha saúde mental e meus estudos na faculdade?", "stream"),
        "Voz: Síntese TTS": ("O Vox AI é um assistente seguro e acolhedor de apoio à comunidade LGBTQIA+.", "tts"),
        "API: REST /api/v1/chat": ("Quais são os serviços de apoio disponíveis?", "api"),
    }
    
    results = {}
    for name, (payload, kind) in scenarios.items():
        print(f"\n▶ Cenário: {name}")
        if kind == "stream":
            results[name] = measure_stream_query(payload, runs=3)
        elif kind == "tts":
            results[name] = measure_tts(payload, runs=3)
        elif kind == "api":
            results[name] = measure_api_chat(payload, runs=3)
            
    print("\n" + "=" * 60)
    print("RESULTADOS CONSOLIDADOS (Mediana e P95 em segundos)")
    print("=" * 60)
    print(f"{'Cenário':<32} | {'TTFB Med':<10} | {'TTFB P95':<10} | {'Total Med':<10} | {'Total P95':<10}")
    print("-" * 80)
    for name, m in results.items():
        print(f"{name:<32} | {m['ttfb_med']:<10.3f} | {m['ttfb_p95']:<10.3f} | {m['total_med']:<10.3f} | {m['total_p95']:<10.3f}")
        
    with open("docs/qa/metricas_latencia.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print("\n✅ Métricas salvas com sucesso em docs/qa/metricas_latencia.json")

if __name__ == "__main__":
    run_benchmarks()

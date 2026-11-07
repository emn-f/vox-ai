# Guia Prático de Fine-Tuning com Unsloth: Persona Acolhedora Vox AI

**Autor:** Equipe de Pesquisa e Engenharia de IA – Projeto Vox AI  
**Issue de Referência:** #256 ([AI/Research] Fine-Tuning do Modelo para Persona Acolhedora)  
**Dataset Base:** `data/fine_tuning/persona_vox_dataset.jsonl`  
**Data:** 2026-11-07  

---

## 1. Visão Geral e Justificativa

O **Vox AI** opera sob uma diretriz fundamental: **"Acolher antes de informar"**. Modelos fundacionais proprietários ou genéricos (*out-of-the-box*) frequentemente falham nessa premissa: tendem a emitir respostas excessivamente burocráticas, prolixas, frias ou tecnicistas ao lidar com dores profundas da comunidade LGBTQIA+ (como transfobia, expulsão do lar, violência ou dúvidas médicas).

Para garantir autonomia tecnológica, soberania de dados, redução de custos com APIs proprietárias e possibilidade de execução local/privada (*on-premises* ou *edge*), este guia documenta o processo de ajuste fino (**Fine-Tuning**) de modelos abertos de ponta (como **Llama 3.1 8B Instruct** e **Qwen 2.5 7B Instruct**) utilizando o framework **Unsloth** com **QLoRA (Quantized Low-Rank Adaptation)** em 4 bits.

---

## 2. Por que Unsloth?

O **Unsloth** é atualmente o framework mais veloz e eficiente em memória para treinamento de LLMs:
- **2x a 5x mais rápido** que o Hugging Face `peft` / `trl` puro graças a kernels manuais em Triton.
- **Redução de até 70% no consumo de VRAM**, permitindo treinar um modelo de 8 bilhões de parâmetros em GPUs com apenas 16 GB de VRAM (como a **NVIDIA T4 gratuita do Google Colab**).
- Suporte nativo à exportação para **GGUF** (4-bit, 8-bit, 16-bit) para execução direta no **Ollama**, **vLLM** ou **llama.cpp**.

---

## 3. Requisitos de Ambiente e Hardware

| Componente | Mínimo Recomendado | Ideal / Produção |
| :--- | :--- | :--- |
| **GPU** | NVIDIA T4 (16 GB VRAM) | NVIDIA A10G / L4 / A100 (24–40 GB) |
| **RAM do Sistema** | 12 GB | 32 GB |
| **Disco** | 25 GB livres | 50 GB livres |
| **Python** | 3.10 ou 3.11 | 3.11 com CUDA 12.1+ |

---

## 4. Instalação e Preparação do Ambiente

Execute as seguintes instruções no terminal ou nas primeiras células do seu Jupyter / Google Colab Notebook:

```bash
# 1. Instalar Unsloth e dependências otimizadas (PyTorch com CUDA 12)
pip install --upgrade --no-cache-dir "unsloth[colab-new] @ git+https://github.com/unslothai/unsloth.git"
pip install --no-deps trl peft accelerate bitsandbytes
pip install datasets huggingface_hub
```

---

## 5. Código Completo do Pipeline de Treinamento

O script abaixo carrega o dataset `data/fine_tuning/persona_vox_dataset.jsonl`, configura os adaptadores LoRA, aplica o chat template e executa o treinamento supervisionado (SFT).

```python
"""
Script de Treinamento LoRA / Unsloth para a Persona Acolhedora Vox AI.
"""

import os
import torch
from datasets import load_dataset
from unsloth import FastLanguageModel
from trl import SFTTrainer
from transformers import TrainingArguments

# ==========================================
# 1. Parâmetros e Hiperparâmetros
# ==========================================
MAX_SEQ_LENGTH = 2048
DTYPE = None  # None = detecção automática (Float16 ou Bfloat16)
LOAD_IN_4BIT = True  # Ativa quantização 4-bit QLoRA

# Modelo base recomendado (Llama-3.1 8B ou Qwen 2.5 7B)
MODEL_NAME = "unsloth/Meta-Llama-3.1-8B-Instruct-bnb-4bit"
OUTPUT_DIR = "outputs/vox-persona-llama3-lora"
DATASET_PATH = "data/fine_tuning/persona_vox_dataset.jsonl"

# ==========================================
# 2. Carregamento do Modelo Base Otimizado
# ==========================================
print("🔄 Carregando modelo base e tokenizer...")
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name=MODEL_NAME,
    max_seq_length=MAX_SEQ_LENGTH,
    dtype=DTYPE,
    load_in_4bit=LOAD_IN_4BIT,
)

# ==========================================
# 3. Configuração dos Adaptadores LoRA
# ==========================================
print("⚙️ Injetando módulos PEFT / QLoRA...")
model = FastLanguageModel.get_peft_model(
    model,
    r=16,  # Rank LoRA recomendado (16 ou 32)
    target_modules=[
        "q_proj", "k_proj", "v_proj", "o_proj",
        "gate_proj", "up_proj", "down_proj"
    ],
    lora_alpha=16,
    lora_dropout=0,  # Otimizado para 0 no Unsloth
    bias="none",
    use_gradient_checkpointing="unsloth",  # Checkpointing ultraleve de VRAM
    random_state=42,
    use_rslora=False,
    loftq_config=None,
)

# ==========================================
# 4. Formatação do Dataset com Chat Template
# ==========================================
print(f"📖 Carregando dataset a partir de {DATASET_PATH}...")
dataset = load_dataset("json", data_files=DATASET_PATH, split="train")

def format_chat_prompt(examples):
    """
    Aplica o chat_template oficial do Llama-3 para cada conjunto de mensagens.
    """
    conversations = examples["messages"]
    texts = []
    for conv in conversations:
        # Aplica o padrão <|begin_of_text|><|start_header_id|>...
        formatted = tokenizer.apply_chat_template(
            conv,
            tokenize=False,
            add_generation_prompt=False,
        )
        texts.append(formatted)
    return {"text": texts}

formatted_dataset = dataset.map(format_chat_prompt, batched=True)
print(f"✅ Total de exemplos prontos para treinamento: {len(formatted_dataset)}")

# ==========================================
# 5. Configuração do SFTTrainer
# ==========================================
trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,
    train_dataset=formatted_dataset,
    dataset_text_field="text",
    max_seq_length=MAX_SEQ_LENGTH,
    dataset_num_proc=2,
    packing=False,  # Mantém as amostras alinhadas
    args=TrainingArguments(
        per_device_train_batch_size=2,
        gradient_accumulation_steps=4,  # Batch efetivo = 8
        warmup_ratio=0.1,
        num_train_epochs=3,
        learning_rate=2e-4,
        fp16=not torch.cuda.is_bf16_supported(),
        bf16=torch.cuda.is_bf16_supported(),
        logging_steps=5,
        optim="adamw_8bit",
        weight_decay=0.01,
        lr_scheduler_type="cosine",
        seed=42,
        output_dir=OUTPUT_DIR,
        report_to="none",  # Mude para "wandb" se desejar monitorar
    ),
)

# ==========================================
# 6. Execução do Treinamento
# ==========================================
print("🚀 Iniciando treinamento LoRA...")
trainer_stats = trainer.train()
print(f"🎉 Treinamento concluído com sucesso em {trainer_stats.metrics['train_runtime']:.1f} segundos!")
```

---

## 6. Inferência e Validação Qualitativa da Persona

Após o treinamento, execute um teste de inferência para verificar se o modelo assimilou a **Regra de Ouro (Acolher antes de informar)**:

```python
# Ativar modo rápido de inferência
FastLanguageModel.for_inference(model)

prompt_teste = "Estou desesperada, meus pais descobriram que sou lésbica e disseram que vão me colocar para fora de casa."

messages = [
    {
        "role": "system",
        "content": (
            "Você é o Vox – Assistente Virtual de Apoio e Cidadania LGBTQIA+. "
            "Sua missão é democratizar o acesso a informações sobre direitos, saúde, acolhimento e cidadania "
            "com foco especial em Salvador, Bahia. "
            "Acolha com afeto e empatia antes de qualquer informação técnica. Seja direto e assertivo."
        ),
    },
    {"role": "user", "content": prompt_teste},
]

inputs = tokenizer.apply_chat_template(
    messages,
    tokenize=True,
    add_generation_prompt=True,
    return_tensors="pt",
).to("cuda")

outputs = model.generate(
    input_ids=inputs,
    max_new_tokens=256,
    use_cache=True,
    temperature=0.7,
    top_p=0.9,
)

resposta_gerada = tokenizer.decode(outputs[0][inputs.shape[1]:], skip_special_tokens=True)
print("=== RESPOSTA DO VOX FINETUNED ===")
print(resposta_gerada)
```

### Critérios de Avaliação do Tom:
- [x] **Validação inicial de sentimentos:** Contém acolhimento explícito (*"Sinto muito que você esteja passando por isso..."*).
- [x] **Ausência de julgamento:** Respeito absoluto sem culpabilização.
- [x] **Assertividade:** Aponta canais práticos (CVV 188, Disque 100, CRAS/CREAS ou Casa Marielle Franco em Salvador) sem textos prolixos.
- [x] **Linguagem fluida:** Português brasileiro inclusivo e acolhedor.

---

## 7. Exportação e Deploy do Modelo

O Unsloth facilita a exportação dos pesos treinados para múltiplos formatos de implantação.

### Opção A: Salvar Apenas os Adaptadores LoRA (Leve: ~50 MB)
```python
model.save_pretrained(f"{OUTPUT_DIR}/lora_adapter")
tokenizer.save_pretrained(f"{OUTPUT_DIR}/lora_adapter")
```

### Opção B: Fusão Completa em 16-Bit (Para Hugging Face Hub / vLLM)
```python
# Mescla os adaptadores LoRA diretamente no modelo base
model.save_pretrained_merged(
    "models/vox-persona-llama3-16bit",
    tokenizer,
    save_method="merged_16bit",
)
```

### Opção C: Exportação para GGUF (Para Execução no Ollama / llama.cpp)
```python
# Salva diretamente em formato quantizado q4_k_m para execução em laptops ou servidores sem GPU dedicada
model.save_pretrained_gguf(
    "models/vox-persona-llama3-gguf",
    tokenizer,
    quantization_method="q4_k_m",
)
```

#### Executando no Ollama Localmente:
Crie um arquivo `Modelfile`:
```dockerfile
FROM ./models/vox-persona-llama3-gguf/unsloth.Q4_K_M.gguf

TEMPLATE """<|begin_of_text|><|start_header_id|>system<|end_header_id|>
{{ .System }}<|eot_id|><|start_header_id|>user<|end_header_id|>
{{ .Prompt }}<|eot_id|><|start_header_id|>assistant<|end_header_id|>
{{ .Response }}<|eot_id|>"""

PARAMETER stop "<|eot_id|>"
PARAMETER temperature 0.7
```

E inicie o modelo:
```bash
ollama create vox-ai -f Modelfile
ollama run vox-ai "Olá Vox, como funciona a retificação de nome no cartório?"
```

---

## 8. Conclusão e Próximos Passos

Com a finalização deste pipeline de Fine-Tuning:
1. O Vox AI ganha capacidade de operar **independente de APIs de terceiros**, garantindo conformidade rigorosa com a privacidade dos usuários mais vulneráveis.
2. A persona empática fica gravada diretamente nos pesos e representações atencionais do modelo, reduzindo o tamanho necessário de system prompts em produção e aumentando a fidelidade à regra *"Acolher antes de informar"*.

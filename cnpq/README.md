# Vox AI: Inteligência Artificial e Ética no Acesso a Direitos Civis

Este repositório contém o artigo científico e a especificação técnica do projeto **Vox AI**, submetido ao **32º Prêmio Jovem Cientista (Edição 2026)** do CNPq na Categoria **Estudante do Ensino Superior** sob a linha de pesquisa **Inteligência Artificial & Ética**.

O projeto foi desenvolvido no âmbito do Bacharelado em Engenharia de Software da **Universidade Católica do Salvador (UCSAL)**, na Escola de Computação e Tecnologia da Informação (ECTI).

## Autoria

* **Autor:** Emanuel Arlan Sousa Silva Ferreira (`emanuel.ferreira@ucsal.edu.br`)
* **Orientadora:** Prof. Me. Angela Peixoto Santana (`angela.santana@pro.ucsal.br`)
* **Instituição:** Universidade Católica do Salvador (UCSAL)
* *Unidade:* Escola de Computação e Tecnologia da Informação (ECTI)
* *Curso:* Bacharelado em Engenharia de Software


## Sobre o Vox AI

O **Vox AI** é um sistema conversacional *open-source* projetado para democratizar o acesso a informações sobre direitos civis, suporte legal e acolhimento voltados à comunidade LGBT no Brasil.

Para contornar os problemas de viés algorítmico, desinformação e alucinações comuns em grandes modelos de linguagem (LLMs) comerciais, o Vox AI adota uma arquitetura de **Recuperação Aumentada de Geração (RAG)** desacoplada. Isso garante que as respostas fornecidas sejam estritamente embasadas em uma base de conhecimento curada contendo documentos oficiais, normas vigentes, jurisprudências do TST, provimentos do CNJ e resoluções do CNE/MEC.

Saiba mais sobre o Projeto Vox AI em [https://github.com/emn-f/vox-ai](https://github.com/emn-f/vox-ai).

## ⚙️ Arquitetura do Sistema

A solução de software é estruturada em camadas desacopladas:

1. **Interface do Usuário (Frontend):** Desenvolvida em **Streamlit (Python)**, permitindo interações via chat textual ou áudio.
2. **Embeddings & Banco Vetorial:** Conversão de textos em vetores de **1536 dimensões** persistidos no **Supabase** via extensão **pgvector**.
3. **Engine RAG Otimizada:** Busca semântica com limiar estrito de similaridade de cosseno (`SEMANTICA_THRESHOLD = 0.58`) e estratégia de fallback para $Top\text{-}3$ fragmentos.
4. **Geração & System Prompt Anti-Alucinação:** Processamento via **Gemini API** sob instrução de sistema que impõe tom acolhedor, refutação a *jailbreaks*, neutralidade e direcionamento a canais de emergência (Disque 100, Ligue 180, CVV 188).
5. **Avaliação Quantitativa (LLM-as-a-Judge CoT):** Pipeline próprio de validação inspirado no framework Ragas, avaliando as métricas da Tríade RAG (*Faithfulness*, *Answer Relevance*, *Context Precision* e *Context Recall*) em 65 cenários de teste (*Golden Datasets v1.0 a v1.3*).
6. **Governança & LGPD (Anonymity by Design):** Ausência total de captura de PII (nome, CPF, e-mail ou IP) e gerenciamento de sessões efêmeras via UUID.

## 📂 Estrutura do Repositório

```text
datasets/                # Golden Datasets de avaliação (v1.0, v1.1, v1.2, v1.3)
resultados/              # Logs JSON dos benchmarks e relatórios de avaliação
  ├── benchmarks/        # Histórico de execuções JSON
  ├── relatorios/        # Relatórios executivos Markdown gerados via IA
  └── dashboard.html     # Dashboard visual interativo das métricas RAG
scripts/                 # Pipeline de execução e avaliação
docs/                    # Documentação técnica estendida (DATASET, PIPELINE, REPRODUCAO)

```

## 🐳 Ambiente de Desenvolvimento via Dev Container

Para garantir um ambiente de desenvolvimento padronizado e reprodutível, este repositório conta com suporte a **Dev Containers** (VS Code / Docker).

O container já vem pré-configurado com:
* **Python 3.11+** e todas as dependências do `requirements.txt` pré-instaladas;
* **TeX Live Completo** (incluindo os pacotes `abntex2`, `memoir`, `xurl`, `amsmath` e utilitários de idioma em português) para compilação local do artigo LaTeX sem necessidade de instalações adicionais no sistema operacional hospedeiro; e
* Suporte nativo à extensão do **LaTeX Workshop** no VS Code.

### Como Executar no Dev Container

1. Certifique-se de ter o **Docker** e o **VS Code** (com a extensão *Dev Containers*) instalados na sua máquina.
2. Abra a pasta do projeto no VS Code.
3. Quando solicitado no canto inferior direito, clique em **"Reopen in Container"** (ou abra a paleta de comandos via `Ctrl+Shift+P` / `Cmd+Shift+P` e escolha `Dev Containers: Reopen in Container`).
4. O VS Code construirá o container e deixará o ambiente pronto para compilar o PDF com `pdflatex` e rodar os scripts em Python com `python3`.


## 📊 Como Executar o Pipeline de Avaliação RAG

Para rodar os benchmarks quantitativos sobre os *Golden Datasets*:

```bash
# Instalar dependências Python
pip install -r requirements.txt

# Executar o pipeline completo (Benchmark + LLM Juiz + LGPD Audit + Dashboard)
python3 scripts/run_pipeline.py

# Gera dashboard isoladamente
python3 scripts/gerar_dashboard.py

```

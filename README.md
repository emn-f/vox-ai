---
title: Vox AI
emoji: 🏳️‍🌈
colorFrom: purple
colorTo: red
sdk: streamlit
sdk_version: 1.67.0
python_version: 3.13
app_file: vox_ai.py
pinned: false
license: gpl-3.0
short_description: Open-Source AI Assistant powered by Gemini
tags:
  - lgbtq
  - ai
  - chatbot
  - gemini
  - portuguese
---

<div align="center">

# 🏳️‍🌈 Vox AI: Assistente de Apoio e Informação LGBTQIA+


![Build Status](https://img.shields.io/github/actions/workflow/status/emn-f/vox-ai/production_pipeline.yml?branch=main&label=Build&logo=github&style=flat-square)
![Prod Version](https://img.shields.io/github/v/release/emn-f/vox-ai?include_prereleases&label=main&color=2ea44f&style=flat-square)
![License](https://img.shields.io/github/license/emn-f/vox-ai?style=flat-square&color=blue)

![Python](https://img.shields.io/badge/Python-3.13-3776AB?logo=python&style=flat-square)
![Streamlit](https://img.shields.io/badge/Deploy-Streamlit-FF4B4B?logo=streamlit&style=flat-square)
![Hugging Face](https://img.shields.io/badge/Mirror-Hugging%20Face-FFD21E?logo=huggingface&style=flat-square&logoColor=black)
![Supabase](https://img.shields.io/badge/DB-Supabase-3ECF8E?logo=supabase&style=flat-square)
![Gemini](https://img.shields.io/badge/AI-Gemini-8E75B2?logo=google&style=flat-square)

### [Acesse aqui o Vox AI](https://vox-ai.streamlit.app/) | [Dashboard](https://emn-f.github.io/vox-ai/) | [Documentação Técnica](https://emn-f.github.io/vox-ai-docs/)

</div>

O **Vox AI** é um chatbot de apoio e informação a comunidade LGBTQIA+. Nossa missão é ser um ponto de apoio digital seguro, oferecendo informações confiáveis, orientação e acolhimento para a comunidade e seus aliados. O Vox AI usa tecnologia para combater a desinformação e promover cidadania, respeito e dignidade.

## 📋 Sumário
* [📊 Métricas e Status](#-métricas-e-status)
* [✨ Funcionalidades](#-funcionalidades)
* [💻 Tecnologias Utilizadas](#-tecnologias-utilizadas)
* [🤖 Automação e CI/CD](#-automação-e-cicd)
* [🤝 Como Contribuir](#-como-contribuir)
* [⚖️ Governança e Ética](#️-governança-e-ética)
* [📝 Licença](#-licença)
* [🤝 Parceria com a Casa de Cultura Marielle Franco](#--parceria-com-a-casa-de-cultura-marielle-franco)
* [👥 Equipe](#-equipe)
* [📬 Contato](#-contato)

## 📊 Métricas e Status

### Qualidade e Automação
![Tests](https://img.shields.io/badge/Tests-Pytest%20%7C%20Unit%20%26%20Integration-34D058?style=flat-square&logo=pytest)
![Security Review](https://img.shields.io/github/actions/workflow/status/emn-f/vox-ai/security_review.yml?branch=develop&style=flat-square&logo=githubcheck&label=Code%20Review)
![HF Mirror](https://img.shields.io/github/actions/workflow/status/emn-f/vox-ai/deploy_hugging_face.yml?branch=main&style=flat-square&logo=huggingface&label=HF%20Mirror)
![DB Sync](https://img.shields.io/github/actions/workflow/status/emn-f/vox-ai/deploy_db.yml?branch=main&style=flat-square&logo=supabase&label=DB%20Last%20Sync)
![Last Update](https://img.shields.io/github/last-commit/emn-f/vox-ai/main?style=flat-square&logo=github&label=Last%20Update)

### Atividade e Evolução
![Commits Last Release](https://img.shields.io/github/commits-since/emn-f/vox-ai/v5.0.0?style=flat-square&logo=git&label=Commits%20since%20last%20release&color=007acc)
![Closed Issues](https://img.shields.io/github/issues-closed/emn-f/vox-ai?style=flat-square&logo=github&label=Issues%20Resolved&color=28a745)
![Closed PRs](https://img.shields.io/github/issues-pr-closed/emn-f/vox-ai?style=flat-square&logo=github&label=PRs%20Merged&color=6f42c1)

### Estrutura e Manutenibilidade
![Repo Size](https://img.shields.io/github/repo-size/emn-f/vox-ai?style=flat-square&logo=github&label=Repo%20Size)
![Files](https://img.shields.io/github/directory-file-count/emn-f/vox-ai?style=flat-square&label=Files)

## ✨ Funcionalidades

* **Interface Acolhedora:** Chatbot intuitivo e acessível em Streamlit com suporte completo a streaming de respostas e feedback em tempo real.
* **Voz & Áudio Nativo (STT & TTS):** Entrada de voz com transcrição multimodal via Gemini e síntese de voz (TTS) nativa em alta fidelidade (24 kHz PCM WAV) com fallback automático.
* **Busca Semântica & RAG Inteligente:** Recuperação contextual enriquecida sobre direitos LGBTQIA+, retificação de nome social (MEC), rede de acolhimento local (Salvador/Camaçari) e diretrizes trabalhistas corporativas.
* **Resiliência Multi-Modelo:** Fallback automático em cascata entre modelos Google Gemini caso o principal atinja limites de cota ou indisponibilidade.
* **Rede de Apoio Integrada:** Diretório com busca e filtros por cidade, categoria e contato de centros de referência, ONGs e delegacias especializadas.
* **Core Desacoplado & API REST:** Arquitetura desacoplada com FastAPI (`src/api/`) para execução headless, integrações de canais (WhatsApp/Telegram) e microsserviços.
* **Pipeline de Ingestão & Auditoria:** Sistema de moderação com IA e Human-in-the-Loop (`conteudo_pendente`) e ferramentas de auditoria e métricas vetoriais da base (`scripts/audit_kb.py`).
* **Segurança e Gatekeep:** Varreduras SAST com Semgrep, validação estrita de segredos e pipeline de backup automatizado do banco no Supabase.

## 💻 Tecnologias Utilizadas

* **Core & Backend:** Python 3.13, Streamlit, FastAPI, Uvicorn.
* **Inteligência Artificial:** Google Gemini (Flash, Flash-Lite, Audio STT & TTS).
* **Embeddings & Vector Store:** Google GenAI Embeddings (`gemini-embedding-001`), PostgreSQL (`pgvector`) no Supabase.
* **Segurança & SAST:** Semgrep (v1.183.0), Pre-Push Gatekeep Scanner, Supabase RLS.
* **DevOps & CI/CD:** GitHub Actions (Node 22 LTS, setup-python@v5, setup-uv@v5, Supabase CLI v2.84.2), Git Cliff, Hugging Face Spaces (Streamlit SDK 1.67.0).

## 🤖 Automação e CI/CD

* **Versionamento Semântico Automatizado:** Tags `vX.Y.Z` geradas dinamicamente com base em Conventional Commits.
* **Changelog Contínuo:** Histórico detalhado gerado via Git Cliff (`cliff.toml`).
* **Deploy de Banco de Dados:** Aplicação controlada e idempotente de migrações no Supabase.
* **Deploy Contínuo:** Espelhamento automático para Hugging Face Spaces com ambiente validado.
* **Backups e Manutenção:** Backups semanais validados com manifesto e rotina keep-alive automática.

## 🤝 Como Contribuir

Contribuições são bem-vindas! Consulte nosso [**Guia de Contribuição**](https://github.com/emn-f/vox-ai/blob/main/.github/CONTRIBUTING.md) para detalhes sobre padrões de commit, setup e fluxo de desenvolvimento.


## ⚖️ Governança e Ética

Segurança e respeito são pilares do Vox. Consulte nossos documentos oficiais:

* [**Código de Conduta**](.github/CODE_OF_CONDUCT.md): Nossos pactos de convivência.
* [**Política de Privacidade**](docs/legal/PRIVACY_POLICY.md): Como tratamos dados (100% anônimos).
* [**Política de Segurança**](.github/SECURITY.md): Como reportar vulnerabilidades.
* [**Termos de Uso**](docs/legal/TERMS_OF_USE.md): O que você precisa ter em mente ao utilizar o Vox AI.

## 📝 Licença

Licenciado sob a **Licença GNU GPLv3**. Veja o arquivo [LICENSE](LICENSE).

## 🤝 Parceria com a Casa de Cultura Marielle Franco

O Projeto Vox tem uma parceria oficial com a **Casa de Cultura Marielle Franco**, instituição de acolhimento independente em Salvador (BA). A Casa atua como ponto de escuta e validação de nossos conteúdos, garantindo que a tecnologia esteja alinhada com as reais necessidades da comunidade.

## 👥 Equipe

**Tech Lead:** [Emanuel Ferreira](https://github.com/emn-f)

**Developer:** [Rodrigo Santos](https://github.com/rodrigosantos-eng)

**Outros colaboradores:** Alicia Batista, Brenda Pires, Fernanda Souza, Kauã Araujo, Lucca Pertigas, Marcio Ventura.

## 📬 Contato

* **E-mail:** [assistentedeapoiolgbtvox@gmail.com](mailto:assistentedeapoiolgbtvox@gmail.com)
* **Instagram:** [@projetovoxai](https://www.instagram.com/projetovoxai/)
* **Linktree:** [linktr.ee/vox_ai](https://linktr.ee/vox_ai)
---

<div align="left">
    <p>© 2026 Vox AI: Segurança para ser quem você é.</p>
</div>
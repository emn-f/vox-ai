---
title: Vox AI
emoji: 🏳️‍🌈
colorFrom: purple
colorTo: red
sdk: streamlit
sdk_version: 1.52.2
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

### [Acesse aqui o Vox AI](https://vox-ai.streamlit.app/) | [Dashboard no GitPages](https://emn-f.github.io/vox-ai/)

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
![Security Review](https://img.shields.io/github/actions/workflow/status/emn-f/vox-ai/security_review.yml?branch=main&style=flat-square&logo=githubcheck&label=Code%20Review)
![HF Mirror](https://img.shields.io/github/actions/workflow/status/emn-f/vox-ai/deploy_hugging_face.yml?branch=main&style=flat-square&logo=huggingface&label=HF%20Mirror)
![DB Sync](https://img.shields.io/github/actions/workflow/status/emn-f/vox-ai/deploy_db.yml?branch=main&style=flat-square&logo=supabase&label=DB%20Last%20Sync)
![Last Update](https://img.shields.io/github/last-commit/emn-f/vox-ai/main?style=flat-square&logo=github&label=Last%20Update)

### Atividade e Evolução
![Commits Last Release](https://img.shields.io/github/commits-since/emn-f/vox-ai/v3.2.14?style=flat-square&logo=git&label=Commits%20since%20last%20release&color=007acc)
![Closed Issues](https://img.shields.io/github/issues-closed/emn-f/vox-ai?style=flat-square&logo=github&label=Issues%20Resolved&color=28a745)
![Closed PRs](https://img.shields.io/github/issues-pr-closed/emn-f/vox-ai?style=flat-square&logo=github&label=PRs%20Merged&color=6f42c1)

### Estrutura e Manutenibilidade
![Repo Size](https://img.shields.io/github/repo-size/emn-f/vox-ai?style=flat-square&logo=github&label=Repo%20Size)
![Files](https://img.shields.io/github/directory-file-count/emn-f/vox-ai?style=flat-square&label=Files)

## ✨ Funcionalidades

* **Interface Acolhedora:** Chatbot intuitivo desenvolvido com Streamlit, focado na experiência do usuário.
* **Busca Semântica (RAG):** Respostas embasadas em uma base de conhecimento curada, utilizando `SentenceTransformers` para garantir precisão e evitar alucinações.
* **IA Generativa:** Integração com Google Gemini, instruído para atuar com empatia e segurança.
* **Sistema de Denúncia:** Ferramenta integrada ao chat para reportar respostas inadequadas, alucinações ou violações, com categorização e comentários.
* **Feedback Loop:** Mecanismo de avaliação integrado para melhoria contínua baseada na opinião da comunidade.
* **Portal de Transparência:** Um [Dashboard](https://emn-f.github.io/vox-ai/) público para acompanhar changelogs, status da base de dados e outras métricas do projeto.

## 💻 Tecnologias Utilizadas

* **Core:** Python 3.13, Streamlit.
* **IA:** Google Gemini Flash (modelo `gemini-flash-latest`).
* **RAG:** Google GenAI Embeddings (`gemini-embedding-001`).
* **Dados:** Supabase (Banco Relacional, Vetorial e Logs).
* **DevOps:** GitHub Actions (CI/CD), Git Cliff (Changelog), Hugging Face (Deploy), uv (Gestão de Dependências).

## 🤖 Automação e CI/CD

* **Versionamento Semântico:** Tags geradas automaticamente em releases.
* **Changelog Automático:** Gerado via Git Cliff a cada atualização.
* **Deploy de Banco de Dados:** Aplicação automática de migrações no Supabase.
* **Deploy Contínuo:** Espelhamento automático para o Hugging Face Spaces.

## 🤝 Como Contribuir

Contribuições são bem-vindas! Consulte nosso [**Guia de Contribuição**](https://github.com/emn-f/vox-ai/blob/main/.github/CONTRIBUTING.md) para detalhes sobre padrões de commit, setup e fluxo de desenvolvimento.


## ⚖️ Governança e Ética

Segurança e respeito são pilares do Vox. Consulte nossos documentos oficiais:

* [**Código de Conduta**](CODE_OF_CONDUCT.md): Nossos pactos de convivência.
* [**Política de Privacidade**](PRIVACY_POLICY.md): Como tratamos dados (100% anônimos).
* [**Política de Segurança**](SECURITY.md): Como reportar vulnerabilidades.

## 📝 Licença

Licenciado sob a **Licença GNU GPLv3**. Veja o arquivo [LICENSE](LICENSE).

## 🤝 Parceria com a Casa de Cultura Marielle Franco

O Projeto Vox tem uma parceria oficial com a **Casa de Cultura Marielle Franco**, instituição de acolhimento independente em Salvador (BA). A Casa atua como ponto de escuta e validação de nossos conteúdos, garantindo que a tecnologia esteja alinhada com as reais necessidades da comunidade.

## 👥 Equipe

**Liderança Técnica:** [Emanuel Ferreira](https://github.com/emn-f)

**Colaboradores (Curadoria):** Alicia Batista, Brenda Pires, Fernanda Souza, Kauã Araujo, Lucca Pertigas, Marcio Ventura.

## 📬 Contato

* **E-mail:** [assistentedeapoiolgbtvox@gmail.com](mailto:assistentedeapoiolgbtvox@gmail.com)
* **Instagram:** [@projetovoxai](https://www.instagram.com/projetovoxai/)
* **Linktree:** [linktr.ee/vox_ai](https://linktr.ee/vox_ai)


<div align="center">
<p>🤖 Vox AI: conversas que importam 🏳️‍🌈</p>
</div>

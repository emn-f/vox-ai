---
title: Vox AI
emoji: 🏳️‍🌈
colorFrom: purple
colorTo: red
sdk: streamlit
sdk_version: 1.52.2
python_version: 3.11
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


![Build Status](https://img.shields.io/github/actions/workflow/status/emn-f/vox-ai/production_pipeline.yml?branch=master&label=Build&logo=github&style=flat-square)
![Prod Version](https://img.shields.io/github/v/release/emn-f/vox-ai?label=Prod&color=2ea44f&style=flat-square)
![Dev Version](https://img.shields.io/github/v/tag/emn-f/vox-ai?include_prereleases&label=Dev&color=orange&style=flat-square)
![License](https://img.shields.io/github/license/emn-f/vox-ai?style=flat-square&color=blue)

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&style=flat-square)
![Streamlit](https://img.shields.io/badge/Deploy-Streamlit-FF4B4B?logo=streamlit&style=flat-square)
![Supabase](https://img.shields.io/badge/Backend-Supabase-3ECF8E?logo=supabase&style=flat-square)
![Gemini](https://img.shields.io/badge/AI-Gemini-8E75B2?logo=google&style=flat-square)
![Hugging Face](https://img.shields.io/badge/Mirror-Hugging%20Face-FFD21E?logo=huggingface&style=flat-square&logoColor=black)

### [Acesse aqui o Vox AI](https://assistentevox.streamlit.app/) | [Dashboard no GitPages](https://emn-f.github.io/vox-ai/)

</div>

O **Vox AI** é um chatbot de apoio e informação a comunidade LGBTQIA+. Nossa missão é ser um ponto de apoio digital seguro, oferecendo informações confiáveis, orientação e acolhimento para a comunidade e seus aliados. O Vox AI usa tecnologia para combater a desinformação e promover cidadania, respeito e dignidade.

## 📋 Sumário
* [✨ Funcionalidades](#-funcionalidades)
* [💻 Tecnologias Utilizadas](#-tecnologias-utilizadas)
* [🤖 Automação e CI/CD](#-automação-e-cicd)
* [🤝 Como Contribuir](#-como-contribuir)
* [⚖️ Governança e Ética](#️-governança-e-ética)
* [📝 Licença](#-licença)
* [🤝 Parceria com a Casa de Cultura Marielle Franco](#--parceria-com-a-casa-de-cultura-marielle-franco)
* [👥 Equipe](#-equipe)
* [📬 Contato](#-contato)


## ✨ Funcionalidades

* **Interface Acolhedora:** Chatbot intuitivo desenvolvido com Streamlit, focado na experiência do usuário.
* **Busca Semântica (RAG):** Respostas embasadas em uma base de conhecimento curada, utilizando `SentenceTransformers` para garantir precisão e evitar alucinações.
* **IA Generativa:** Integração com Google Gemini, instruído para atuar com empatia e segurança.
* **Sistema de Denúncia:** Ferramenta integrada ao chat para reportar respostas inadequadas, alucinações ou violações, com categorização e comentários.
* **Feedback Loop:** Mecanismo de avaliação integrado para melhoria contínua baseada na opinião da comunidade.
* **Portal de Transparência:** Um [Dashboard](https://emn-f.github.io/vox-ai/) público para acompanhar changelogs, status da base de dados e outras métricas do projeto.

## 💻 Tecnologias Utilizadas

* **Core:** Python 3.11+, Streamlit.
* **IA:** Google Gemini Flash (modelo `gemini-flash-latest`), Sentence-Transformers (RAG).
* **Dados:** Supabase (Banco Vetorial e Logs).
* **DevOps:** GitHub Actions (CI/CD), Git Cliff (Changelog), Hugging Face (Deploy).

## 🤖 Automação e CI/CD

* **Versionamento Semântico:** Tags geradas automaticamente em releases.
* **Changelog Automático:** Gerado via Git Cliff a cada atualização.
* **Sync de Dados:** Sincronização automática entre Google Sheets e JSON.
* **Deploy Contínuo:** Espelhamento automático para o Hugging Face Spaces.

## 🤝 Como Contribuir

Contribuições são bem-vindas! Consulte nosso [**Guia de Contribuição**](CONTRIBUTING.md) para detalhes sobre padrões de commit, setup e fluxo de desenvolvimento.


## ⚖️ Governança e Ética

Segurança e respeito são pilares do Vox. Consulte nossos documentos oficiais:

* [**Código de Conduta**](CODE_OF_CONDUCT.md): Nossos pactos de convivência.
* [**Política de Privacidade**](PRIVACY_POLICY.md): Como tratamos dados (100% anônimos).
* [**Política de Segurança**](SECURITY.md): Como reportar vulnerabilidades.

## 📝 Licença

Licenciado sob a **Licença GNU GPLv3**. Veja o arquivo [LICENSE](LICENSE).

## 🤝 Parceria com a Casa de Cultura Marielle Franco

O Projeto Vox AI tem uma parceria oficial com a **Casa de Cultura Marielle Franco**, instituição de acolhimento independente em Salvador (BA). A Casa atua como ponto de escuta e validação de nossos conteúdos, garantindo que a tecnologia esteja alinhada com as reais necessidades da comunidade.

## 👥 Equipe

**Liderança Técnica:** [Emanuel Ferreira](https://github.com/emn-f)

**Colaboradores (Curadoria):** Alicia Batista, Brenda Pires, Fernanda Souza, Kauã Araujo, Lucca Pertigas, Marcio Ventura.

## 📬 Contato

* **E-mail:** [assistentedeapoiolgbtvox@gmail.com](mailto:assistentedeapoiolgbtvox@gmail.com)
* **Instagram:** [@projetovoxai](https://www.instagram.com/projetovoxai/)
* **Linktree:** [linktr.ee/vox_ai](https://linktr.ee/vox_ai)

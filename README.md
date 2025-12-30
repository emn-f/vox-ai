---
title: Vox AI
emoji: 🏳️‍🌈
colorFrom: red
colorTo: red
sdk: docker
app_port: 8501
tags:
- streamlit
pinned: false
license: gpl
short_description: Open-Source AI Assistant powered by Gemini & Neural Search
---

# 🏳️‍🌈 Projeto Vox AI: Assistente de Apoio e Informação LGBTQIA+

[![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat-square&logo=Streamlit&logoColor=white)](https://streamlit.io/)
[![Gemini](https://img.shields.io/badge/Gemini-8E75B8?style=flat-square&logo=google&logoColor=white)](https://ai.google.dev/)
[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-FFD21E?style=flat-square&logo=huggingface&logoColor=black)](https://huggingface.co/)
[![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-2088FF?style=flat-square&logo=github-actions&logoColor=white)](https://docs.github.com/en/actions)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg?style=flat-square)](https://www.gnu.org/licenses/gpl-3.0)

### [Acesse aqui o Vox AI](https://assistentevox.streamlit.app/) | [Dashboard no GitPages](https://emn-f.github.io/vox-ai/)

## 📋 Sumário
* [💡 Sobre o Projeto](#-sobre-o-projeto)
* [✨ Funcionalidades](#-funcionalidades)
* [💻 Tecnologias Utilizadas](#-tecnologias-utilizadas)
* [🤖 Automação e CI/CD](#-automação-e-cicd)
* [🤝 Como Contribuir](#-como-contribuir)
* [⚖️ Governança e Ética](#️-governança-e-ética)
* [📝 Licença](#-licença)
* [🤝 Parceria com a Casa de Cultura Marielle Franco](#--parceria-com-a-casa-de-cultura-marielle-franco)
* [👥 Equipe](#-equipe)
* [📬 Contato](#-contato)

## 💡 Sobre o Projeto
O **Vox AI** é um chatbot de apoio e informação a comunidade LGBTQIA+.

### Missão
Ser um ponto de apoio digital seguro, oferecendo informações confiáveis, orientação e acolhimento para a comunidade e seus aliados. O Vox AI usa tecnologia para combater a desinformação e promover cidadania, respeito e dignidade.

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

# Manual de Identidade Visual — Vox AI 🏳️‍🌈

> **Versão:** 1.0.0  
> **Status:** Aprovado  
> **Tema Central:** Acolhimento, Tecnologia Humanizada e Orgulho Interseccional

---

## 1. Conceito e Propósito da Marca

O **Vox AI** é um assistente de inteligência artificial dedicado a fornecer acolhimento, orientação jurídica, saúde preventiva e apoio emocional para a comunidade LGBTQIA+.

A identidade visual do Vox traduz visualmente:
1. **Acolhimento e Empatia:** Formas arredondadas e curvas suaves que transmitem segurança e escuta ativa.
2. **Voz e Presença:** Elementos de onda sonora (soundwaves) e balão de fala que representam o direito de se expressar e ser ouvido.
3. **Diversidade e Orgulho:** Gradiente contínuo inspirado na bandeira do orgulho interseccional (Gilbert Baker + Progress Pride), simbolizando a multiplicidade de identidades.
4. **Precisão e Segurança Tecnológica:** Tipografia geométrica contemporânea e paleta de alto contraste, alinhada aos padrões de acessibilidade (WCAG 2.1 AA/AAA).

---

## 2. Paleta de Cores

A paleta de cores do Vox AI é estruturada em três camadas: **Cores Institucionais**, **Gradiente do Orgulho (Pride Ribbon)** e **Cores Neutras de Superfície**.

### 2.1 Cores Principais do Gradiente Pride

O gradiente do orgulho é a assinatura viva do Vox AI, aplicado em bordas, detalhes tipográficos e ondas de áudio:

| Cor | Nome do Tom | HEX | RGB | Função / Aplicação |
|---|---|---|---|---|
| 🔴 | **Coral Passion** | `#FF1E56` | `rgb(255, 30, 86)` | Amor, vida e visceralidade; início do gradiente |
| 🟠 | **Sun Orange** | `#FF7A00` | `rgb(255, 122, 0)` | Energia, cura e criatividade |
| 🟡 | **Luminous Yellow** | `#FFD600` | `rgb(255, 214, 0)` | Luz solar, clareza e esperança |
| 🟢 | **Mint Green** | `#05DF9D` | `rgb(5, 223, 157)` | Natureza, renovação e saúde |
| 🔵 | **Cyan Electric** | `#00B4D8` | `rgb(0, 180, 216)` | Serenidade, comunicação e clareza digital |
| 🟣 | **Deep Violet** | `#7209B7` | `rgb(114, 9, 183)` | Espírito, dignidade, acolhimento institucional |
| 💖 | **Vibrant Magenta** | `#F72585` | `rgb(247, 37, 133)` | Empatia, calor humano e visibilidade |

### 2.2 Cores Neutras e de Fundo (Dark Mode First)

| Aplicação | HEX | RGB | Uso |
|---|---|---|---|
| **Background Principal** | `#0E091B` | `rgb(14, 9, 27)` | Fundo imersivo escuro (Dark surface) |
| **Surface Card** | `#161226` | `rgb(22, 18, 38)` | Cartões, balões de chat e containers |
| **Border Accent** | `#2B2347` | `rgb(43, 35, 71)` | Contornos sutis com opacidade |
| **Texto Primário** | `#FFFFFF` | `rgb(255, 255, 255)` | Títulos de alto destaque |
| **Texto Secundário** | `#E2E8F0` | `rgb(226, 232, 240)` | Subtítulos e botões principais |
| **Texto Suave / Muted** | `#94A3B8` | `rgb(148, 163, 184)` | Descrições e notas de rodapé |

---

## 3. Tipografia

A tipografia do Vox AI prioriza máxima legibilidade em dispositivos móveis, telas de baixa resolução e acessibilidade para pessoas neurodivergentes ou com baixa visão.

### 3.1 Família Primária
- **Display & Títulos:** `Plus Jakarta Sans`, `Inter`, `system-ui`, `-apple-system`, `sans-serif`.
- **Texto Corrido (Body):** `Inter`, `Roboto`, `Segoe UI`, `sans-serif`.
- **Código & IDs de Erro:** `JetBrains Mono`, `Fira Code`, `ui-monospace`, `monospace`.

### 3.2 Escala Tipográfica
- **Hero Title (Display 1):** 48px – 64px (Bold / Black 800-900)
- **Título de Seção (H1):** 32px – 40px (Bold 700)
- **Subtítulo (H2):** 24px – 28px (Semi-Bold 600)
- **Cabeçalho de Card (H3):** 18px – 20px (Medium 500)
- **Corpo de Texto (Body):** 15px – 16px (Regular 400, line-height 1.6)
- **Legendas e Badges (Caption):** 12px – 13px (Medium 500, uppercase ou pill)

---

## 4. Elementos do Logo e Iconografia

### 4.1 O Símbolo (Icon Mark)
O ícone do Vox AI é formado pela união de:
1. **O Balão de Escuta Ativa:** Contorno elíptico dinâmico que evoca diálogo seguro e sem julgamentos.
2. **O Espectro Sonoro (Soundwave Bars):** Seis barras verticais com bordas arredondadas representando a voz, cada uma colorida com um tom do arco-íris inclusivo.
3. **A Estrela Affirmative:** Ponto de luz no topo direito simbolizando esperança, esclarecimento e novos horizontes.

### 4.2 Arquivos Vetoriais Disponíveis

| Arquivo | Caminho | Proporção | Uso Recomendado |
|---|---|---|---|
| **Logo Horizontal** | `static/branding/logo.svg` | 800 x 240 (10:3) | Headers, documentação, apresentações, site oficial |
| **Ícone / Avatar** | `static/branding/icon.svg` | 512 x 512 (1:1) | Foto de perfil (WhatsApp, Telegram, Instagram), favicon, app launcher |
| **Banner Hero** | `static/branding/banner.svg` | 1200 x 480 (5:2) | README no GitHub, cards de compartilhamento OpenGraph, canais do Telegram |

---

## 5. Aplicação nos Canais de Atendimento

### 5.1 Web (Streamlit UI)
- Utiliza o gradiente rainbow no título da barra lateral e detalhes dos balões de chat.
- Avatar do assistente: `static/branding/icon.svg` ou emoji temático `🌈`.
- Fundo consistente com as superfícies escuras `#0E091B` e cartões em `#161226`.

### 5.2 Bot Telegram (@vox_lgbtqia_bot)
- **Avatar:** `static/branding/icon.svg` exportado em alta densidade (512x512).
- **Banner de Apresentação:** `static/branding/banner.svg` na mensagem de `/start` ou no canal informativo.
- **Estilo de Mensagens:** Uso de emojis afirmativos (`🌈`, `💜`, `⚖️`, `🩺`, `🛡️`) e formatação Markdown clara.

### 5.3 Canal WhatsApp (Business / Cloud API)
- **Foto de Perfil:** `static/branding/icon.svg` circularizado com margem de segurança de 15%.
- **Recados / Status:** *"Vox AI: Assistente de acolhimento e informação LGBTQIA+"*.
- **Botões Interativos:** Textos diretos com no máximo 20 caracteres por ação rápida.

---

## 6. Diretrizes de Uso Correto (Do's & Don'ts)

### ✅ Permitido (Do's)
- Manter a proporção 1:1 e margem de respiro mínima de 20% ao redor do ícone.
- Aplicar o gradiente oficial completo (`#FF1E56` até `#7209B7`) nas aplicações primárias da marca.
- Assegurar contraste mínimo de 4.5:1 (WCAG AA) para qualquer texto informativo contra o fundo.

### ❌ Proibido (Don'ts)
- Não rotacionar, distorcer ou esticar o balão e as barras de áudio.
- Não alterar a ordem das cores do espectro da bandeira do orgulho.
- Não utilizar fontes manuscritas, decorativas ou de baixa legibilidade junto ao logotipo.
- Não posicionar o logotipo sobre fundos fotográficos saturados sem máscara de contraste escura.

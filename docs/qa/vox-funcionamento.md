# Como o Vox AI Funciona (Visão do Usuário & Tempos de Resposta)

O **Vox AI** é um assistente virtual e espaço seguro de acolhimento, orientação e acesso a informações confiáveis para a comunidade LGBTQIA+. A aplicação combina uma interface acessível e responsiva construída em **Streamlit**, um mecanismo de inteligência artificial generativa multimodelo alimentado pela **Google Gemini API** e uma base de conhecimento curada e auditada com recuperação semântica **RAG (pgvector no Supabase)**.

Este documento descreve a experiência e o funcionamento do sistema sob o ponto de vista do usuário final em ambiente de Desenvolvimento (`Dev`), cobrindo os fluxos de texto, voz, diretórios de apoio e serviços analíticos, acompanhados das métricas reais de tempo de resposta.

---

## 1. Fluxo de Interação por Texto

### 1.1 Primeira Interação e Boas-Vindas
Ao acessar a URL do Vox AI (`http://localhost:8501`), o usuário é recebido por uma mensagem acolhedora que explica a proposta do projeto, estabelece os canais de urgência (Ligue 188 do CVV e Disque 100 dos Direitos Humanos na barra lateral) e convida à conversa livre de julgamentos.

### 1.2 Perguntas Diretas e Escopo de Acolhimento
Quando o usuário faz uma pergunta geral ou introdutória (ex: *"Como você pode me acolher e ajudar hoje?"*):
1. O texto é enviado através do campo de entrada inferior (`st.chat_input`).
2. **Bypass Inteligente de Saudações (`eh_saudacao`)**: Saudações e cumprimentos diretos (ex: *"olá"*, *"bom dia"*, *"tudo bem?"*, *"hey vox"*) são detectados preventivamente em `src/core/semantica.py`. Nesses casos, a consulta vetorial RAG é dispensada deliberadamente, evitando a injeção espúria de chunks factuais e mantendo a conversa calorosa, natural e imediata.
3. O Vox AI responde em tom empático, sintetizando seus três pilares fundamentais:
   - **Direitos e Cidadania**: leis, retificação de documentos, certidões e canais de denúncia.
   - **Saúde**: cuidados de saúde afirmativa, prevenção combinada (PrEP/PEP), saúde mental e SUS.
   - **Acolhimento**: redes de suporte, casas de abrigo e coletivos comunitários.
4. A resposta é transmitida em *streaming*, gerando os primeiros fragmentos visíveis quase instantaneamente.

### 1.3 Perguntas Aprofundadas com RAG (Recuperação de Conhecimento)
Quando a dúvida envolve normas jurídicas, resoluções institucionais ou locais de atendimento:
1. O sistema gera uma representação vetorial (embedding de 1536 dimensões) da pergunta do usuário via `gemini-embedding-001`.
2. Consulta a tabela `knowledge_base` no Supabase utilizando a extensão `pgvector`, calculando a similaridade de cosseno.
3. Se houver correspondência semântica acima do limiar configurado (`SEMANTICA_THRESHOLD = 0.62`):
   - Os chunks de conhecimento curados são recuperados e injetados de forma invisível no prompt do modelo como contexto factual.
   - **Segregação de Chunks de Desenvolvedor**: Tópicos voltados estritamente à infraestrutura do projeto (`Como Contribuir`, `Padrões de Commit`, `Acesso ao Banco de Dados`) são filtrados da recuperação comum e só são acionados se o usuário fizer uma pergunta explícita sobre contribuição de código (`eh_pergunta_desenvolvedor`). Isso impede que instruções internas de git ou banco vazem nas orientações acolhedoras ao público geral.
   - O modelo Gemini gera uma resposta fundamentada na lei ou diretriz oficial, sem alucinações.
4. Exemplos validados em QA:
   - **Nome Social no Ensino**: Portarias MEC nº 1.612/2011 e nº 33/2018 e Decreto nº 8.727/2016, assegurando nome social em listas de chamada, diários de classe, carteirinhas e diplomas.
   - **Rede Local Salvador e Camaçari**: Casa de Acolhimento Marielle Franco (com WhatsApp institucional para triagem e sigilo de endereço), DECRADI Salvador e encaminhamentos ao CREAS em Camaçari.
   - **Sanitários Corporativos**: Diretrizes e jurisprudências do TST e STF assegurando o uso do banheiro conforme a identidade de gênero autodeclarada, proibindo o isolamento ou a imposição de sanitários de PCD.
   - **História LGBTQIA+**: O marco histórico de 17 de maio de 1990, quando a OMS retirou a homossexualidade da Classificação Internacional de Doenças (CID), originando o Dia Internacional contra a LGBTfobia (IDAHOBIT).

### 1.4 Tratamento de Perguntas Fora de Escopo
Se o usuário fizer perguntas alheias ao domínio (como cotações de ações financeiras ou receitas culinárias):
- O Vox AI recusa educadamente, esclarece que seu escopo é focado em direitos, saúde e cidadania LGBTQIA+, e reitera sua disponibilidade para temas de apoio.

### 1.5 Robustez a Entradas Extremas
- **Espaços vazios / Whitespace**: O sistema valida e descarta automaticamente entradas compostas exclusivamente por espaços em branco (`prompt.strip()`), impedindo a criação de balões vazios e evitando consultas desnecessárias à base vetorial e ao modelo de IA. Na API REST, o Pydantic rejeita tais entradas com HTTP 422.
- **Textos Longos e Desabafos (500+ caracteres)**: O assistente prioriza a escuta afetiva, valida os sentimentos de dor ou ansiedade causados por rejeição familiar e propõe um plano de passos práticos escalonados (apoio psicológico pelo SUS/CVV 188, construção de rede de afeto e garantias legais de Nome Social).
- **Caracteres Especiais e Emojis (`🏳️‍🌈 < > & " ' ⚧️`)**: Sanitizados sem injeção de HTML, quebra de renderização ou erros de parsing.

---

## 2. Fluxo de Interação por Voz

O Vox AI conta com suporte nativo e contingencial para voz tanto na entrada (STT) quanto na saída (TTS):

### 2.1 Ouvir a Resposta (Text-to-Speech - TTS)
- Cada mensagem emitida pelo assistente possui um botão **🔊 Ouvir**.
- **Alerta de Espera Visual (`st.spinner`)**: Ao clicar, a interface apresenta imediatamente o indicador visual animado `🎙️ Gerando áudio com voz humanizada... Por favor, aguarde um instante`, garantindo que o usuário saiba que a síntese de fala está sendo processada.
- **Cache de Áudio em Sessão (`audio_cache_{i}`)**: O arquivo de áudio sintetizado é armazenado em `st.session_state[f"audio_cache_{i}"]`. Reproduções futuras da mesma mensagem na mesma sessão ocorrem de forma instantânea sem realizar novas requisições de rede ou consumir cotas da API.
- Ao clicar, o sistema aciona `src/core/audio.py`:
  - **Mecanismo Primário**: Geração de áudio nativo multimodal via API do Gemini (`gemini-2.5-flash-preview-tts` / `gemini-3.8-flash-tts`).
  - **Mecanismo de Resiliência (Fallback)**: Caso a cota diária do modelo esteja temporariamente esgotada (HTTP 429) ou haja oscilação de rede, o Vox AI aciona de forma transparente a síntese do `gTTS` (Google Text-to-Speech em português).
- O player nativo HTML5 `<audio>` é renderizado na tela, com controles de reprodução, barra de progresso e volume.

### 2.2 Gravação e Transcrição (Speech-to-Text - STT)
- O usuário dispõe de um botão com ícone de microfone **🎙️** ao lado do campo de mensagem.
- Um popover interativo do Streamlit abre um gravador integrado (`st.audio_input`).
- O usuário grava seu relato; ao finalizar, os dados de áudio são empacotados e transcritos com alta fidelidade para português pelo modelo multimodal do Gemini.
- Caso o áudio contenha silêncio ou seja corrompido, o pipeline trata o erro graciosamente sem travar a interface.

---

## 3. Rede de Apoio & Acolhimento (Diretório Integrado)

Na barra lateral, o botão **🤝 Rede de Apoio & Acolhimento** abre uma modal centralizada com:
1. **Contatos de Emergência Imediata**: Disque 100 (Direitos Humanos), CVV 188 e 190 (Polícia Militar).
2. **Filtros Dinâmicos**: Busca textual em tempo real, seleção por Categoria (Moradia, Saúde, Jurídico), filtro por Estado (SP, RJ, BA, AM, etc.) e alternador para iniciativas 100% gratuitas/SUS.
3. **Cartões Informativos Verificados**: Informações completas de locais emblemáticos como Casa 1, Casinha Acolhimento, Casa Chama e Casa Miga, contendo descrição, tags, links diretos e canais de WhatsApp.
4. **Estado Vazio Confortável**: Quando uma busca não encontra resultados, é exibida mensagem orientando a expansão dos filtros, sem quebras de layout.

---

## 4. Tempos de Resposta e Métricas de Desempenho

As medições foram coletadas em ambiente Dev rodando localmente, executando cada cenário por 3 repetições consecutivas com medição precisa de TTFB (*Time to First Byte* / primeiro chunk gerado) e Tempo Total de resposta:

| Cenário de Interação | TTFB Mediana (s) | TTFB P95 (s) | Tempo Total Mediana (s) | Tempo Total P95 (s) |
| :--- | :---: | :---: | :---: | :---: |
| **Texto: Pergunta Simples** | 6.869 | 7.940 | 8.028 | 9.825 |
| **Texto: RAG Nome Social MEC** | 6.992 | 7.239 | 8.436 | 8.490 |
| **Texto: RAG Sanitários Trans** | 5.997 | 6.053 | 7.649 | 7.913 |
| **Texto: Pergunta Longa (500+ chars)** | 2.283 | 8.255 | 3.598 | 11.049 |
| **Voz: Síntese de Fala (TTS)** | 0.507 | 0.812 | 1.267 | 1.804 |
| **API Desacoplada: REST `/api/v1/chat`** | 2.089 | 20.873 | 3.482 | 32.112* |

*\* Nota sobre P95 da API: O tempo elevado no percentil 95 da API deveu-se à exaustão da cota do modelo principal `gemini-3.6-flash`, momento em que o sistema acionou a cascata automática de fallback até obter resposta bem-sucedida do modelo `gemini-3.1-flash-lite`.*

---

## 5. Conclusão de Usabilidade

A experiência de uso em ambiente Dev comprova que o Vox AI cumpre com excelência o seu compromisso de acolhimento seguro: a linguagem é calorosa e respeitosa, o RAG assegura precisão legal e geográfica, a voz garante acessibilidade e o mecanismo de contingência preserva a disponibilidade mesmo diante de esgotamento de cotas de APIs externas.

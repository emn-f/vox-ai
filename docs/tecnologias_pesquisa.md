# Relatório de Pesquisa Tecnológica e Postura de Segurança — Vox AI 🛡️

> **Issues Vinculadas:**  
> • #175: [DOCS] Tecnologias para pesquisar e talvez aplicar no Vox (Scanbot)  
> • #304: [DOCS] Tecnologias para pesquisar e talvez aplicar no Vox (Semgrep)  
> • #305: [DOCS] Avaliação de ferramentas de OCR, Escaneamento e Segurança de Documentos  
> **Status:** Pesquisa Concluída & Recomendações Arquiteturais Aprovadas  
> **Data:** Novembro de 2026

---

## 1. Introdução

Como uma plataforma focada no acolhimento de pessoas em situação de vulnerabilidade e no tratamento de dados sensíveis (LGPD Art. 11 — orientação sexual, identidade de gênero e saúde), a segurança da informação, a privacidade e a eficiência das tecnologias de apoio são pilares inegociáveis do Vox AI.

Este documento consolida a análise técnica e de viabilidade de duas frentes tecnológicas estratégicas:
1. **Semgrep (SAST e Varredura Automatizada de Código & Segredos)** — Issues #175 e #304.
2. **Scanbot SDK e Tecnologias de Escaneamento/OCR de Documentos** — Issues #175 e #305.
3. **Mapeamento de Postura de Segurança Integrada (AppSec & LLMSec)**.

---

## 2. Análise Tecnológica: Semgrep (SAST & Detecção de Vulnerabilidades)

### 2.1 O que é o Semgrep?
O **Semgrep** é um motor de análise estática de código (SAST - *Static Application Security Testing*) rápido, de código aberto e baseado em padrões semânticos de AST (Árvore Sintática Abstrata). Diferente de linters puramente regex, o Semgrep compreende a semântica da linguagem Python, identificando fluxos de dados vulneráveis, vazamento de segredos e más práticas em tempo de compilação ou CI/CD.

### 2.2 Comparativo: Semgrep vs. Outras Ferramentas

| Critério | Semgrep | Bandit | SonarQube | Gitleaks |
|---|---|---|---|---|
| **Velocidade de Execução** | Muito Alta (~15-30s em CI) | Alta (~10s) | Baixa (~3-8 min) | Extremamente Alta (~5s) |
| **Suporte a Linguagens** | Multi-linguagem (Python, JS, YAML, SQL) | Apenas Python | Multi-linguagem | Apenas detecção de strings |
| **Regras Customizadas** | Sintaxe intuitiva YAML/Code | Complexo (plugins Python) | Complexo (Java) | Expressões Regulares |
| **Detecção de Segredos** | Sim (`p/secrets`) | Não | Sim | Sim (Especializado) |
| **Custo de Licenciamento** | Open Source (CLI gratuito) | Open Source | Comercial / Community limitada | Open Source |

### 2.3 Regras de Varredura Adotadas no Vox AI
Integrado via `.github/workflows/security_semgrep.yml`, o pipeline do Vox AI executa os seguintes pacotes oficiais de regras:
- `p/security-audit`: Varredura exaustiva de vulnerabilidades de injeção e deserialização.
- `p/owasp-top-ten`: Cobertura direta das 10 principais falhas de segurança da OWASP.
- `p/python`: Melhores práticas de segurança específicas do ecossistema Python (FastAPI, Streamlit, Supabase Client, etc.).
- `p/secrets`: Detecção de chaves de API expostas em código (ex: `AIza...`, tokens do Supabase e Hugging Face).

### 2.4 Regras Customizadas para LGPD (Vox Tailored Rules)
Foi desenhada uma regra Semgrep customizada para evitar logging acidental de dados pessoais de usuários:
```yaml
rules:
  - id: vox-prevent-pii-logging
    patterns:
      - pattern-either:
          - pattern: logger.$METHOD(..., $USER.cpf, ...)
          - pattern: logger.$METHOD(..., $USER.telefone, ...)
          - pattern: logger.$METHOD(..., $USER.nome_registro, ...)
    message: "Possível vazamento de dado sensível em logs! Anonimize o identificador antes de logar."
    languages: [python]
    severity: ERROR
```

### 2.5 Veredito e Próximos Passos
- **Decisão:** Aprovado para adoção imediata na pipeline de CI/CD.
- **Implementação:** Workflow `.github/workflows/security_semgrep.yml` ativado em pull requests e branches principais.

---

## 3. Análise Tecnológica: Scanbot SDK & Tecnologias de OCR

### 3.1 Casos de Uso no Vox AI
No apoio a pessoas trans e travestis, um dos principais gargalos burocráticos no Brasil é a **retificação de prenome e gênero diretamente em cartórios de Registro Civil** (Provimento nº 73/2018 do CNJ). O processo exige a apresentação de mais de 10 certidões negativas (Justiça Federal, Estadual, Eleitoral, Militar, Protesto de Títulos).

O caso de uso mapeado para escaneamento inteligente é:
1. **Verificação de Documentos para Retificação:** Leitura e conferência automática de certidões para avisar se alguma está vencida ou ilegível antes de a pessoa gastar dinheiro no cartório.
2. **Mascaramento e Redação de CPF/RG na Origem:** Desfocar ou ocultar dados ultra-sensíveis (ex: CPF antigo ou prenome anterior) *no dispositivo* antes de qualquer upload.

### 3.2 Avaliação do Scanbot SDK

O **Scanbot SDK** é uma solução de ponta para escaneamento móvel e extração de dados via OCR (Optical Character Recognition) em iOS, Android, Flutter e React Native.

#### Pontos Fortes:
- **Processamento 100% On-Device (Offline):** Nenhum documento ou imagem escaneada precisa sair do aparelho da pessoa usuária para a nuvem. Isso elimina o risco de vazamento de dados de saúde ou identificação civil.
- **Filtros de Otimização e Detecção de Borda:** Corrige perspectiva, rugas no papel e sombras em fotos tiradas com celular humilde.
- **Detecção de Tipos Documentais:** Reconhece RG brasileiro, CNH e certidões cívicas.

#### Pontos de Atenção / Desafios:
- **Modelo Comercial Fechado:** O Scanbot é um SDK proprietário com licenciamento corporativo anual com custo elevado para projetos sociais/open-source.
- **Necessidade de Aplicativo Nativo:** O Vox AI atualmente é primariamente Web (Streamlit) e Canais (Telegram / WhatsApp). O Scanbot exige um aplicativo móvel compilado (React Native / Flutter / Kotlin / Swift).

### 3.3 Comparativo de Tecnologias de OCR e Escaneamento

| Solução | Processamento | Precisão em Certidões BR | Custo | Adequação ao Vox AI |
|---|---|---|---|---|
| **Scanbot SDK** | 100% On-Device (Offline) | Altíssima | Alto (Licença Anual) | Excelente para futuro App Nativo (v4+) |
| **Tesseract OCR (Open Source)** | Local / Serverless | Média (exige pré-processamento) | Gratuito / OSS | Alta para protótipos de backend |
| **Google Document AI** | Nuvem (GCP) | Altíssima | Pago por página | Moderada (requer consentimento explícito LGPD) |
| **Apple Vision / Android ML Kit** | On-Device (Nativo) | Alta | Gratuito | Ideal para app móvel comunitário |

### 3.4 Veredito e Recomendações
1. **Curto Prazo (v3.x):** Manter o foco do Vox AI em orientações passo-a-passo textuais e listas de checagem interativas na Web/Canais.
2. **Médio Prazo (v4.0 App Mobile):** Submeter proposta ao programa de apoio a iniciativas sociais sem fins lucrativos da Scanbot (*Scanbot Social Impact License*) ou utilizar **ML Kit On-Device** para mascaramento offline de certidões.

---

## 4. Postura Geral de Segurança da Informação (Security Posture)

```
[ Camada 1: Código & CI/CD ]
   └── Semgrep SAST + Gatekeep Pre-Push + Dependabot Vulnerability Scanning
[ Camada 2: Dados & Banco ]
   └── Supabase PostgreSQL RLS (Row Level Security) + Criptografia AES em repouso
[ Camada 3: Privacidade & LGPD ]
   └── Identificadores Pseudo-Anonimizados (SHA-256 + Salt) + Minimização de Histórico
[ Camada 4: Modelo & LLM ]
   └── System Prompts com Blindagem contra Jailbreak e Detecção de Red Flags
```

### 4.1 Principais Ações Implementadas
- **Anonimização em Canais:** Integrações de WhatsApp e Telegram não registram números de telefone ou IDs em texto aberto no Supabase.
- **Exclusão a Pedido:** Comandos `/limpar` e botão de exclusão de dados ativos em todos os canais de atendimento.
- **Auditoria Contínua:** Logs estruturados associados à versão do Git para rastreabilidade de bugs sem exposição de conteúdo confidencial.

---

## 5. Conclusão

A integração do **Semgrep** eleva a maturidade do repositório Vox AI aos mais altos padrões de segurança de software de código aberto, mitigando riscos antes mesmo do merge. A pesquisa sobre **Scanbot** estabelece as bases técnicas e o modelo de privacidade para quando o Vox evoluir para um aplicativo móvel nativo de assistência documental.

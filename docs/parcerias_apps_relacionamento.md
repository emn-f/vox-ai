# Blueprint de Parcerias com Aplicativos de Relacionamento — Vox AI 🏳️‍🌈

> **Issue:** #191 — Parcerias com apps de relacionamentos  
> **Status:** Proposta Técnica e Estratégica Oficial  
> **Público-Alvo:** Equipes de Segurança (Trust & Safety), Produto e Parcerias de apps como Tinder, Grindr, Bumble, Hornet, Scruff, Her e canais afins.

---

## 1. Visão Geral e Justificativa Social

O Brasil figura entre os países com os maiores índices de violência contra pessoas LGBTQIA+, especialmente mulheres trans e travestis. No ecossistema digital, aplicativos de relacionamento tornaram-se canais prioritários de socialização e afeto, mas também palcos frequentes de:
- **Golpes do Encontro e Extorsão:** Sequestros-relâmpago, violência física e extorsão após o match.
- **Desinformação Crítica em Saúde Sexual:** Dúvidas sobre janela de PEP (Profilaxia Pós-Exposição ao HIV em até 72h) e acesso ao SUS.
- **Transfobia, Assédio e Discriminação Sistemática:** Rejeições violentas, doxxing e exposição não consentida.

O **Vox AI** propõe uma parceria de valor mútuo (Trust & Safety + ESG): integrar a inteligência artificial do Vox como a **Central de Segurança, Cuidado e Acolhimento Oficial** dentro ou conectada aos principais aplicativos de relacionamento em operação no Brasil.

---

## 2. Pilares de Atuação Integrada

```
+-------------------------------------------------------------------------+
|                  APLICATIVO DE RELACIONAMENTO PARCEIRO                   |
+--------------------+---------------------+--------------------+---------+
                     |                     |                    |
        [1. Check de Segurança]  [2. Saúde & PEP 72h]   [3. SOS Pânico]
                     |                     |                    |
+--------------------+---------------------+--------------------+---------+
|                         VOX AI PARTNERS GATEWAY                         |
|                    (mTLS, Zero-Knowledge, LGPD Art. 11)                 |
+--------------------+---------------------+--------------------+---------+
                     |                     |                    |
            [RAG Especializado]   [Base SUS / PEP]   [Rede de Apoio]
```

### 2.1 Prevenção de Golpes e Red Flags
- Verificação proativa de comportamentos suspeitos reportados pela própria pessoa usuária (ex: insistência em locais ermos, pedidos de dinheiro, perfis sem verificação).
- Dicas automatizadas de segurança antes do primeiro encontro presencial (*Check-in de Segurança Vox*).

### 2.2 Guia de Saúde Sexual e Profilaxia de Urgência (PEP/PrEP)
- Se a pessoa relata uma exposição de risco no chat ou busca orientação: orientação imediata sobre a **PEP (Profilaxia Pós-Exposição)** em até 72 horas no SUS.
- Localização automatizada do serviço público 24h mais próximo (UPAs e Centros de Testagem e Aconselhamento - CTA).

### 2.3 Botão do Pânico e Acolhimento em Crise
- Acesso rápido a suporte psicológico imediato (CVV 188), denúncias de LGBTfobia (Disque 100) e rede de casas de acolhimento parceiras da Rede Vox.

---

## 3. Modelos de Integração Técnica

### Modelo A: Widget Embutido (In-App WebView SDK)
- Um botão de atalho *"Central Vox de Segurança & Acolhimento"* integrado ao perfil ou nas configurações do app.
- Abertura de uma interface leve e fluida, pré-autenticada via JWT temporário, sem transferência de dados pessoais sensíveis.

### Modelo B: Assistente Conversacional no Chat ("@Vox")
- No fluxo de conversa entre matches, o usuário pode digitar `@vox segurança` ou tocar no ícone de escudo para receber orientações privadas visíveis apenas para ele(a/e).

### Modelo C: API B2B Server-to-Server
- Integração de microsserviços via REST/JSON com mTLS para consulta de serviços de acolhimento e validação de diretrizes de saúde.

---

## 4. Especificação da API de Parcerias (RESTful v1)

### 4.1 Check de Segurança Contextual
Avalia uma dúvida ou situação descrita pela pessoa usuária e devolve orientações de mitigação de risco com acolhimento humanizado.

- **Endpoint:** `POST /api/v1/partners/dating/safety-check`
- **Headers:**
  - `Authorization: Bearer <PARTNER_TOKEN>`
  - `Content-Type: application/json`
  - `X-Vox-Partner-ID: <PARTNER_SLUG>`

#### Request Body
```json
{
  "session_token": "anon_9f83acb14e",
  "topic": "safe_meetup",
  "user_context": {
    "is_trans": true,
    "city": "São Paulo",
    "uf": "SP"
  },
  "query": "A pessoa quer me encontrar num lugar isolado e não quer fazer chamada de vídeo antes. É seguro?"
}
```

#### Response (200 OK)
```json
{
  "risk_level": "medium_high",
  "alerts": [
    "Recusa de chamada de vídeo ou verificação de foto é um sinal frequente de perfil falso.",
    "Encontros em locais privados ou isolados aumentam o risco de violência ou extorsão."
  ],
  "recommendations": [
    "Insista em marcar o primeiro encontro em um local público e movimentado (ex: café, shopping ou praça iluminada).",
    "Compartilhe sua localização em tempo real com uma pessoa de sua extrema confiança.",
    "Nunca aceite carona de pessoas desconhecidas no primeiro encontro."
  ],
  "affirmative_message": "Sua segurança e integridade vêm sempre em primeiro lugar. Confie na sua intuição! 💜",
  "emergency_contacts": {
    "disque_100": true,
    "cvv_188": true,
    "policia_190": true
  }
}
```

---

### 4.2 Localizador Emergencial de PEP / PrEP (Saúde Sexual 24h)
Retorna as unidades públicas do SUS mais próximas aptas a dispensar Profilaxia Pós-Exposição (PEP) em caráter de urgência.

- **Endpoint:** `POST /api/v1/partners/dating/pep-prep-locator`

#### Request Body
```json
{
  "latitude": -23.55052,
  "longitude": -46.633308,
  "service_type": "PEP_EMERGENCY_24H",
  "max_distance_km": 15
}
```

#### Response (200 OK)
```json
{
  "time_critical_notice": "A PEP deve ser iniciada preferencialmente nas primeiras duas horas e no máximo até 72 horas após a exposição de risco. O atendimento no SUS é 100% gratuito e sigiloso.",
  "facilities": [
    {
      "name": "UPA 24h Vergueiro",
      "address": "Rua Vergueiro, 2500 - Vila Mariana, São Paulo - SP",
      "distance_km": 2.4,
      "open_24h": true,
      "services": ["PEP", "Testagem Rápida HIV/IST", "Acolhimento Emergencial"],
      "phone": "(11) 5080-0000"
    },
    {
      "name": "Centro de Testagem e Aconselhamento (CTA) Henfil",
      "address": "Rua Libero Badaró, 119 - Centro, São Paulo - SP",
      "distance_km": 3.8,
      "open_24h": false,
      "hours": "Segunda a Sexta, 07:00 às 19:00",
      "services": ["PEP", "PrEP", "Preservativos", "Autotestes"]
    }
  ]
}
```

---

### 4.3 Acionamento de Botão do Pânico / SOS Afirmativo
Permite ao app encaminhar a pessoa para a central de acolhimento e contatar rede de suporte segura.

- **Endpoint:** `POST /api/v1/partners/dating/panic-alert`

#### Request Body
```json
{
  "session_token": "anon_9f83acb14e",
  "alert_type": "physical_threat",
  "location": {
    "latitude": -23.55052,
    "longitude": -46.633308
  }
}
```

#### Response (200 OK)
```json
{
  "status": "alert_processed",
  "immediate_actions": [
    {
      "action": "call_police",
      "number": "190",
      "label": "Ligar para o 190 Imediatamente"
    },
    {
      "action": "call_human_rights",
      "number": "100",
      "label": "Denunciar Violação (Disque 100)"
    }
  ],
  "safe_shelters_nearby": [
    {
      "name": "Casa 1 — Acolhimento LGBTQIA+",
      "distance_km": 1.8,
      "contact": "(11) 3104-5858"
    }
  ]
}
```

---

## 5. Diretrizes de Privacidade e LGPD (Art. 11)

A orientação sexual e a identidade de gênero são categorizadas como **Dados Pessoais Sensíveis** pela LGPD (Lei nº 13.709/2018).

Para resguardar integralmente os usuários, a integração com apps de relacionamento adota:
1. **Zero-Knowledge Architecture:** O Vox AI **não armazena** o nome real, telefone, histórico de matches ou fotos trocadas nos apps.
2. **Identificadores Efêmeros:** Tokens de sessão gerados criptograficamente com expiração de curto prazo (TTL máximo de 2 horas).
3. **Sem Perfilamento Comercial:** Proibição contratual absoluta de uso das interações de suporte para recomendação de anúncios ou enriquecimento de dados de marketing.
4. **Direito ao Esquecimento:** Botão de eliminação imediata de sessão em qualquer etapa do fluxo.

---

## 6. Proposta de Valor para as Plataformas Parceiras

- **Redução de Incidentes Críticos:** Queda mensurável em casos de golpes e violência associados à plataforma.
- **Selo de Plataforma Segura & Inclusiva:** Concessão do selo *"Parceria Oficial Vox AI — Comunidade Protegida"*, elevando a reputação de marca e atratividade para o público LGBTQIA+.
- **Cumprimento de Metas ESG e Direitos Humanos:** Relatórios agregados e anonimizados de impacto social e prevenção de violências.
- **Retenção de Pessoas Usuárias:** Usuários que se sentem protegidos permanecem mais tempo ativos e engajados na plataforma.

# Documentação Técnica do Golden Dataset - Vox AI

Este documento detalha a taxonomia, versão e cobertura temática do acervo de testes utilizado para a validação empírica da plataforma Vox AI.

## Visão Geral do Acervo (65 Cenários)

O acervo de testes é dividido em 4 conjuntos de avaliação progressiva para testar a acurácia normativa, a resiliência a ruídos linguísticos e a precisão do *retriever* vetorial no Supabase.

| Versão | Cenários | Foco do Teste | Arquivo de Origem |
| :---: | :---: | :--- | :--- |
| **v1.0** | 35 | Baseline acadêmico amplo sobre Direitos Civis, Saúde e Legislação Nacional | `data/dataset_1.0.json` |
| **v1.1** | 10 | Resiliência a erros de digitação, gírias e linguagem informal da internet | `data/dataset_1.1.json` |
| **v1.2** | 10 | Validação de novidades normativas (MEC, TST, Provimento 73/CNJ, DECRIN Salvador) | `data/dataset_1.2.json` |
| **v1.3** | 10 | Consultas ruidosas e informais sobre a rede local de acolhimento de Salvador e RMS | `data/dataset_1.3.json` |


## Distribuição por Eixo Temático

1. **Direitos Civis e Legislação (18 cenários):** Provimento nº 73/2018 do CNJ, retificação extrajudicial, casamento igualitário (Resolução 175/CNJ), adoção homoparental e gratuidade via CPC Art. 98.
2. **Segurança e Violência (14 cenários):** Equiparação da LGBTfobia ao crime de racismo pelo STF (ADO 26/MI 4733), aplicação da Lei Maria da Penha a mulheres trans e atuação da DECRIN em Salvador.
3. **Saúde e Bem-Estar (15 cenários):** Processo Transexualizador no SUS (Portaria 2.803/2013), prevenção combinada (PrEP/PEP), doação de sangue (ADI 5543) e ambulatórios de Salvador (Multicentro Carlos Gomes e CEDAP/SESAB).
4. **Educação e Sociedade (10 cenários):** Uso do Nome Social na Educação Básica e Superior (Resolução CNE/CP nº 1/2018), Enem, cotas trans em universidades e prevenção ao bullying.
5. **Limitação de Escopo (4 cenários):** Contenção de recomendações comerciais, recusa de opiniões pessoais e direcionamento a canais de apoio.
6. **Blindagem Ética (4 cenários):** Refutação ativa a terapias de conversão ("cura gay") e bloqueio de discursos de ódio com embasamento nas diretrizes da OMS e do CFP.

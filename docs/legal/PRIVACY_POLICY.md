# Política de Privacidade do Vox AI

Última atualização: 6 de junho de 2026

**Visão geral e Conformidade com a LGPD**

O Vox AI é um assistente de apoio e informação voltado para a comunidade LGBTQIA+. Temos o compromisso de proteger a sua privacidade e de processar quaisquer dados em conformidade com a **Lei Geral de Proteção de Dados Pessoais (LGPD - Lei nº 13.709/2018)**. 

Esta Política de Privacidade explica de forma clara e objetiva quais dados tratamos, por que o fazemos, quais bases legais justificam esse tratamento e quais as medidas técnicas e administrativas adotadas para assegurar a proteção de suas informações. Quando mencionamos “dados” neste documento, referimo-nos principalmente aos logs de conversas (perguntas e respostas) e relatórios de feedback.

**Escopo**

Esta política se aplica a todos os usuários do serviço Vox AI e a todos os dados gerados pelas interações no chat do assistente.

## 1. Dados coletados

Coletamos apenas o mínimo necessário para melhorar a qualidade do serviço. Os itens coletados incluem:

- Texto das interações: o prompt enviado pelo usuário e a resposta gerada pelo assistente.
- Identificador de sessão anônimo: um código aleatório que agrupa mensagens de uma mesma conversa para análise de fluxo e contexto. Esse identificador não contém nem está vinculado a informações pessoais.

## 2. O que NÃO coletamos

Nós não coletamos, nem armazenamos, nem solicitamos:

- Nomes reais, e-mails, telefones ou outros dados de contato pessoais.
- Endereços IP, coordenadas de GPS ou dados de localização.
- Identificadores de dispositivos que possam ser usados para rastrear você fora do serviço.

Se você compartilhar voluntariamente dados pessoais nas mensagens (por exemplo, escrever seu e-mail dentro do chat), esses dados poderão ser armazenados nas conversas. Recomendamos não inserir informações pessoais nas interações.

## 3. Finalidades do tratamento

Utilizamos os dados coletados para:

- Melhorar a qualidade das respostas e corrigir erros.
- Entender padrões de uso e as dúvidas mais frequentes da comunidade.
- Treinar e ajustar modelos de IA de forma anônima e agregada.

Os dados não são usados para fins publicitários ou para venda a terceiros.

## 4. Base legal para o Tratamento (Art. 7º da LGPD)

Em conformidade com a LGPD, o tratamento dos dados no Vox AI justifica-se pelas seguintes bases legais:

- **Legítimo Interesse (Art. 7º, IX, LGPD):** Para a melhoria contínua das respostas do assistente, suporte à comunidade e garantia do funcionamento técnico adequado do serviço. Sempre equilibramos este legítimo interesse com a expectativa legítima de privacidade do usuário, garantindo que as interações sejam desassociadas de dados pessoais identificáveis.
- **Execução do Serviço / Consentimento (Art. 7º, I, LGPD):** Para o processamento das mensagens enviadas pelo usuário em tempo real no chat, viabilizando a resposta do assistente (e a transferência internacional necessária descrita na Seção 7).

## 5. Retenção e eliminação dos dados

Mantemos as conversas e os registros de sessão por um período limitado para permitir análises e melhorias contínuas. Politicamente recomendamos reter esses dados por até 12 meses, salvo necessidade operacional diferente, após o qual serão eliminados ou agregados de forma irreversível.

Se você quiser solicitar a exclusão de registros associados a uma conversa específica, informe o código de sessão correspondente (quando disponível). Como as interações são anônimas por padrão, pode não ser possível identificar e excluir conversas sem esse identificador.

## 6. Medidas de Segurança e Proteção de Dados (Art. 46 da LGPD)

Para manter a segurança das interações e a privacidade dos usuários, adotamos medidas técnicas, organizacionais e administrativas em conformidade com o Art. 46 da LGPD:

- **Privacidade por Padrão (Privacy by Design):** O sistema foi projetado para operar sem necessidade de cadastro, autenticação ou identificação do usuário. A arquitetura minimiza ativamente a coleta de informações pessoais.
- **Criptografia e Proteção de Dados:** 
  - Toda transmissão de dados entre o navegador do usuário e nossos servidores é criptografada em trânsito utilizando protocolos TLS/HTTPS.
  - Os logs armazenados no banco de dados (Supabase) utilizam criptografia em repouso (AES-256).
- **Anonimização de Denúncias e Feedbacks:** O sistema de relatórios de erros ou respostas inadequadas (`user_reports`) armazena apenas o texto reportado e a categoria do problema, sem vincular a identidade do relator.
- **Controle e Restrição de Acesso:** Apenas membros autorizados da equipe de desenvolvimento do Vox AI têm acesso às credenciais administrativas do banco de dados para auditoria e manutenção técnica. As credenciais de produção são estritamente protegidas e separadas do código público.
- **Prevenção de Coleta de Dados Sensíveis:** Instruímos e desaconselhamos ativamente os usuários a não inserirem dados pessoais sensíveis (como nome completo, CPF, e-mail ou telefone) no chat de conversas.
- **Plano de Resposta a Incidentes:** Caso seja detectado qualquer vazamento ou incidente de segurança envolvendo dados de interações, a equipe do Vox AI notificará prontamente os canais oficiais do projeto e os órgãos competentes (como a Autoridade Nacional de Proteção de Dados - ANPD), conforme exigido pela LGPD.

## 7. Compartilhamento, sub-processadores e transferência internacional

Para prestar e melhorar o serviço, compartilhamos os dados estritamente necessários com provedores de infraestrutura e processadores de dados essenciais, todos contratualmente obrigados a manter o sigilo e a segurança das informações de acordo com a LGPD:

- **Google Gemini API (Google LLC):** Processamento do texto das mensagens para geração das respostas de Inteligência Artificial.
- **Supabase (Supabase Inc.):** Hospedagem e armazenamento do banco de dados relacional e logs de auditoria.

### Transferência Internacional de Dados (Art. 33 da LGPD)
O uso das APIs de inteligência artificial (Google Gemini) e da infraestrutura de banco de dados (Supabase) envolve o processamento de dados em servidores localizados fora do território nacional (principalmente nos Estados Unidos). Ao utilizar o Vox AI, você declara estar ciente e concordar com a transferência internacional de suas mensagens para fins exclusivos de processamento e resposta da inteligência artificial, de acordo com as salvaguardas contratuais e práticas globais de segurança da informação exigidas.

## 8. Usuários menores de idade

O serviço não é destinado especificamente a menores de idade; incentivamos que responsáveis acompanhem o uso. Caso uma mensagem contenha dados pessoais de menores, trate-a com cautela e evite inserir informações sensíveis no chat.

## 9. Direitos dos titulares

Por tratar-se, em sua grande maioria, de dados anônimos, o exercício direto de alguns direitos (acesso, portabilidade, eliminação) pode ser limitado. Ainda assim, você pode:

- Solicitar informações sobre esta política e seu cumprimento.
- Pedir a exclusão de um registro específico informando o código de sessão quando disponível.

Para solicitações relacionadas a dados, utilize o contato abaixo.

## 10. Alterações desta política

Podemos atualizar esta política periodicamente. Alterações relevantes serão comunicadas no repositório do projeto e, quando possível, dentro do próprio serviço. Recomendamos verificar a data de “Última atualização” no topo deste documento.

## 11. Contato

Para dúvidas, reclamações ou solicitações relacionadas a privacidade, entre em contato:

- E‑mail: assistentedeapoiolgbtvox@gmail.com
- Repositório do projeto: https://github.com/emn-f/vox-ai

Obrigado por confiar no Vox AI. Trabalhamos para oferecer um ambiente seguro, respeitoso e útil para toda a comunidade.

---
© 2026 Projeto Vox
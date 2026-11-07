-- Migration: 20261107200000_enrich_knowledge_base.sql
-- Enriquecimento da Knowledge Base do Vox AI:
-- 1. Resoluções do MEC sobre Nome Social em chamadas escolares e diplomas (Issue #345)
-- 2. Rede de apoio local de Salvador e Camaçari - DECRADI, Casarão, Casa Marielle (Issue #346)
-- 3. Diretrizes trabalhistas sobre sanitários corporativos por pessoas trans - MTE/OIT/TST (Issue #347)
-- 4. História do 17 de Maio de 1990 e despatologização da homossexualidade e identidades trans na OMS (Issue #321)

INSERT INTO public.knowledge_base (topico, eixo_tematico, descricao, referencias, tags, autor, kb_count)
VALUES
(
  'Nome Social na Educação Básica - Resolução CNE/CP 01/2018',
  'Educação e Cidadania',
  'A Resolução CNE/CP nº 01/2018 assegura o uso do nome social de estudantes travestis e transexuais em todos os registros escolares da educação básica no Brasil. Estabelece que o nome social deve ser utilizado nas listas de chamada diárias, diários de classe, boletins, cadastros acadêmicos e comunicações internas. Para estudantes maiores de 18 anos, basta a autodeclaração; para menores de 18 anos, o requerimento deve ser apresentado pelos responsáveis legais.',
  'Resolução CNE/CP nº 01, de 19 de janeiro de 2018; Lei de Diretrizes e Bases da Educação Nacional (LDB).',
  ARRAY['educacao', 'nome social', 'escola', 'chamada', 'mec', 'cne', 'trans'],
  'Vox AI - Curadoria Especializada',
  0
),
(
  'Nome Social no Ensino Superior e Rede Federal - Portaria MEC 33/2018',
  'Educação e Cidadania',
  'A Portaria MEC nº 33/2018 regulamenta o uso e inclusão do nome social de estudantes, professores e servidores travestis e transexuais no âmbito do Ministério da Educação e das instituições federais de ensino superior e técnico. Determina que documentos de circulação interna, carteiras de estudante, e-mails institucionais, certificados e declarações devem constar com destaque o nome social escolhido pela pessoa.',
  'Portaria MEC nº 33, de 17 de janeiro de 2018.',
  ARRAY['ensino superior', 'universidade', 'nome social', 'mec', 'documentos', 'trans'],
  'Vox AI - Curadoria Especializada',
  0
),
(
  'Emissão e Reemissão de Diplomas com Nome Retificado',
  'Educação e Cidadania',
  'Estudantes e egressos que realizaram a retificação de nome e gênero no registro civil têm direito garantido à reemissão de seus diplomas de graduação, pós-graduação e ensino médio com o novo nome. O Parecer CNE/CP nº 14/2017 e diretrizes do MEC vedam qualquer menção constrangedora, anotações vexatórias ou indicação do nome anterior no documento reemitido. As instituições de ensino não podem cobrar taxas abusivas ou impor obstáculos burocráticos para a reemissão.',
  'Parecer CNE/CP nº 14/2017; Portaria Normativa MEC nº 22/2016; Provimento nº 73/2018 do CNJ.',
  ARRAY['diploma', 'retificacao', 'universidade', 'graduacao', 'mec', 'nome civil', 'trans'],
  'Vox AI - Curadoria Especializada',
  0
),
(
  'DECRADI Salvador - Delegacia de Combate à Discriminação',
  'Segurança Pública e Direitos Humanos',
  'A Delegacia Especial de Crimes de Discriminação e Intolerância (DECRADI) de Salvador/BA é a unidade policial especializada na apuração de crimes motivados por homofobia, transfobia, racismo, intolerância religiosa e preconceito social. Localizada no Complexo Policial dos Barris (Vale dos Barris, s/n, Salvador - BA), presta atendimento humanizado às vítimas e encaminhamento para a rede de acolhimento social e jurídico.',
  'Polícia Civil do Estado da Bahia (PCBA); DECRADI Salvador; Complexo dos Barris.',
  ARRAY['decradi', 'salvador', 'denuncia', 'homofobia', 'transfobia', 'delegacia', 'bahia', 'policia civil'],
  'Vox AI - Curadoria Especializada',
  0
),
(
  'CPDD-LGBT e Casarão da Diversidade - Salvador',
  'Rede de Acolhimento e Cidadania',
  'O Centro de Promoção e Defesa dos Direitos LGBT da Bahia (CPDD-LGBT), sediado no Casarão da Diversidade (Rua do Tijolo, nº 8, Centro Histórico / Pelourinho, Salvador - BA), oferece suporte gratuito nas áreas de atendimento psicológico, assistência social e assessoria jurídica para retificação de prenome e gênero, além de enfrentamento à LGBTfobia e violação de direitos.',
  'Secretaria de Justiça e Direitos Humanos da Bahia (SJDH); Casarão da Diversidade Salvador.',
  ARRAY['casarao da diversidade', 'cpdd-lgbt', 'salvador', 'acolhimento', 'apoio juridico', 'psicologia', 'bahia'],
  'Vox AI - Curadoria Especializada',
  0
),
(
  'Casa Marielle Franco e Acolhimento em Salvador e RMS',
  'Rede de Acolhimento e Cidadania',
  'A Casa Marielle Franco e centros parceiros da Região Metropolitana de Salvador (RMS) oferecem abrigo e proteção temporária para jovens e adultos LGBTQIA+ em situação de extrema vulnerabilidade social, expulsão do núcleo familiar ou ameaça física. O acesso se dá através de triagem socioassistencial articulada com centros de referência e movimentos sociais da Grande Salvador.',
  'Rede de Proteção e Acolhimento LGBTQIA+ da Bahia; Movimento de Mulheres e Pessoas Negras e LGBT.',
  ARRAY['casa marielle franco', 'acolhimento', 'abrigo', 'salvador', 'camacari', 'rms', 'vulnerabilidade'],
  'Vox AI - Curadoria Especializada',
  0
),
(
  'Rede de Proteção Social e Apoio LGBT em Camaçari',
  'Rede de Acolhimento e Cidadania',
  'No município de Camaçari/BA, o atendimento à população LGBTQIA+ em situação de violência ou vulnerabilidade é realizado prioritariamente pelos Centros de Referência Especializados de Assistência Social (CREAS) e pelo CRAS local vinculados à Secretaria do Desenvolvimento Social e Cidadania (SEDES Camaçari). Em casos de crimes de intolerância, a 18ª Delegacia Territorial de Camaçari e a DECRADI Salvador atuam na recepção das ocorrências.',
  'SEDES Camaçari; CREAS Camaçari; 18ª Delegacia Territorial de Camaçari.',
  ARRAY['camacari', 'creas', 'assistencia social', 'acolhimento', 'delegacia', 'apoio local', 'bahia'],
  'Vox AI - Curadoria Especializada',
  0
),
(
  'Uso de Sanitários Corporativos por Pessoas Trans',
  'Direito do Trabalho e Relações Corporativas',
  'Pessoas trans têm o direito assegurado de utilizar os sanitários e vestiários do ambiente de trabalho correspondentes à sua identidade de gênero autopercebida. A jurisprudência do Tribunal Superior do Trabalho (TST) e o Supremo Tribunal Federal (STF - RE 845.779) estabelecem que proibir o acesso de mulheres trans ao banheiro feminino ou de homens trans ao banheiro masculino constitui discriminação por gênero e violação à dignidade da pessoa humana.',
  'STF - Recurso Extraordinário 845.779; Jurisprudência consolidada do Tribunal Superior do Trabalho (TST); Art. 1º, III e Art. 5º, X da CF/88.',
  ARRAY['trabalho', 'banheiro', 'sanitarios', 'trans', 'tst', 'stf', 'identidade de genero', 'clt'],
  'Vox AI - Curadoria Especializada',
  0
),
(
  'Assédio Moral Laboral e Restrição de Sanitários',
  'Direito do Trabalho e Relações Corporativas',
  'Obrigar colaboradores transgênero a utilizar banheiros de pessoas com deficiência (PCD), banheiros isolados ou distantes da equipe, ou o sanitário em desacordo com seu gênero, configura assédio moral e gera o dever da empresa de indenizar por dano moral (in re ipsa). As empresas devem orientar e capacitar líderes e funcionários sobre o respeito à diversidade e às identidades de gênero.',
  'Convenção 111 da OIT (Discriminação em Matéria de Emprego e Ocupação); Código Civil, Arts. 186 e 927; TST - AIRR 1000632-15.2017.5.02.0084.',
  ARRAY['assedio moral', 'dano moral', 'empresa', 'rh', 'banheiro', 'trans', 'oit 111', 'diversidade'],
  'Vox AI - Curadoria Especializada',
  0
),
(
  'Diretrizes do MTE e OIT 111 contra Discriminação no Trabalho',
  'Direito do Trabalho e Relações Corporativas',
  'A Convenção nº 111 da OIT, internalizada no Brasil, e as portarias do Ministério do Trabalho e Emprego (MTE) impõem o dever de erradicar qualquer forma de discriminação nas relações de trabalho. Políticas corporativas de inclusão e conduta devem garantir tratamento igualitário, adoção irrestrita do nome social em crachás e sistemas corporativos e acesso irrestrito aos espaços comuns.',
  'Convenção nº 111 da Organização Internacional do Trabalho (OIT); Portaria MTP nº 1.224/2023; Decreto nº 62.150/1968.',
  ARRAY['mte', 'oit', 'clt', 'discriminacao', 'nome social', 'inclusao', 'trabalho'],
  'Vox AI - Curadoria Especializada',
  0
),
(
  'História do 17 de Maio de 1990 - Despatologização pela OMS',
  'História e Memória do Movimento LGBTQIA+',
  'No dia 17 de maio de 1990, a Assembleia Geral da Organização Mundial da Saúde (OMS) aprovou a exclusão oficial da homossexualidade da Classificação Internacional de Doenças (CID). Com essa decisão pioneira, a homossexualidade deixou de ser classificada como doença mental, desvio ou perversão perante a medicina internacional, consolidando-se como uma variação natural e legítima da sexualidade humana.',
  'Organização Mundial da Saúde (OMS); 43ª Assembleia Mundial da Saúde (17 de maio de 1990); Resolução WHA43.24.',
  ARRAY['17 de maio', 'oms', 'despatologizacao', 'historia lgbt', 'saude mental', 'cid', 'direitos humanos'],
  'Vox AI - Curadoria Especializada',
  0
),
(
  'Origem do IDAHOBIT - Dia Internacional de Luta contra a LGBTfobia',
  'História e Memória do Movimento LGBTQIA+',
  'Em comemoração histórica à retirada da homossexualidade da CID pela OMS em 17 de maio de 1990, instituiu-se mundialmente o Dia Internacional de Combate à Homofobia, Transfobia e Bifobia (IDAHOBIT). A data é símbolo de mobilização global pelos direitos humanos, celebração da diversidade e denúncia das violências e preconceitos sofridos pela população LGBTQIA+.',
  'Comitê IDAHO / IDAHOBIT; Resoluções da ONU sobre Orientação Sexual e Identidade de Gênero.',
  ARRAY['17 de maio', 'idahobit', 'combate a homofobia', 'transfobia', 'bifobia', 'mobilizacao', 'onu'],
  'Vox AI - Curadoria Especializada',
  0
),
(
  'Despatologização das Identidades Trans na CID-11',
  'História e Memória do Movimento LGBTQIA+',
  'Dando continuidade ao processo de despatologização iniciado em 1990, a OMS publicou a 11ª revisão da Classificação Internacional de Doenças (CID-11), aprovada em 2019 e em vigor desde 2022, na qual as identidades trans foram integralmente retiradas do capítulo de transtornos mentais. O termo foi reclassificado como ''Incongruência de Gênero'' dentro do capítulo de Condições Relacionadas à Saúde Sexual, assegurando o acesso a cuidados de saúde e processo transexualizador sem estigma psiquiátrico.',
  'Organização Mundial da Saúde (OMS) - CID-11 (Classificação Internacional de Doenças 11ª Revisão, 2019/2022).',
  ARRAY['cid-11', 'oms', 'trans', 'despatologizacao', 'incongruencia de genero', 'saude trans', 'direitos trans'],
  'Vox AI - Curadoria Especializada',
  0
);

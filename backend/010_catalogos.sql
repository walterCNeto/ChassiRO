-- ============================================================
-- 010_catalogos.sql
-- Reguladores, tipos de entidade, segmentos, atividades canônicas
-- ============================================================

BEGIN;

-- ---------- REGULADORES ----------
INSERT INTO reguladores (id, nome, natureza, instrumento, descricao, site) VALUES
('REG_CMN',     'Conselho Monetário Nacional', 'normativo_superior', 'Resolução CMN',
    'Órgão superior do SFN. Edita normas estruturantes do SFN.', 'https://www.bcb.gov.br/estabilidadefinanceira/buscanormas'),
('REG_BCB',     'Banco Central do Brasil', 'normativo_supervisao', 'Resolução BCB / Circular / Carta-Circular',
    'Autarquia normativa e supervisora do SFN.', 'https://www.bcb.gov.br'),
('REG_CVM',     'Comissão de Valores Mobiliários', 'normativo_supervisao', 'Resolução CVM',
    'Autarquia normativa e supervisora do mercado de valores mobiliários.', 'https://www.gov.br/cvm'),
('REG_CNSP',    'Conselho Nacional de Seguros Privados', 'normativo_superior', 'Resolução CNSP',
    'Órgão superior do SNSP.', 'https://www.gov.br/cnsp'),
('REG_SUSEP',   'Superintendência de Seguros Privados', 'normativo_supervisao', 'Circular SUSEP',
    'Autarquia normativa e supervisora do SNSP.', 'https://www.gov.br/susep'),
('REG_PREVIC',  'Superintendência Nacional de Previdência Complementar', 'normativo_supervisao', 'Instrução PREVIC',
    'Autarquia supervisora das EFPCs.', 'https://www.gov.br/previc'),
('REG_CNPC',    'Conselho Nacional de Previdência Complementar', 'normativo_superior', 'Resolução CNPC',
    'Órgão superior do regime de previdência complementar fechada.', NULL),
('REG_COAF',    'Conselho de Controle de Atividades Financeiras', 'uif', 'Resolução COAF',
    'Unidade de Inteligência Financeira do Brasil. Recebe RIFs.', 'https://www.gov.br/coaf'),
('REG_ANPD',    'Autoridade Nacional de Proteção de Dados', 'autoridade_dados', 'Resolução ANPD',
    'Autoridade fiscalizadora da LGPD.', 'https://www.gov.br/anpd'),
('REG_B3',      'B3 S.A. - Brasil, Bolsa, Balcão', 'auto_regulador', 'Ofício Circular B3',
    'Bolsa de valores e auto-reguladora de mercado.', 'https://www.b3.com.br'),
('REG_BSM',     'BSM Supervisão de Mercados', 'auto_regulador', 'Ofício BSM',
    'Auto-reguladora dos participantes do mercado B3.', 'https://www.bsmsupervisao.com.br'),
('REG_ANBIMA',  'Associação Brasileira das Entidades dos Mercados Financeiro e de Capitais',
    'associativo', 'Códigos ANBIMA', 'Auto-regulação voluntária via Códigos.', 'https://www.anbima.com.br');

-- ---------- TIPOS DE ENTIDADE ----------
INSERT INTO tipos_entidade (id, nome, grupo, descricao) VALUES
-- Bancário (sob BCB)
('ENT_BANCO_MULTIPLO',      'Banco Múltiplo', 'bancario',
    'Instituição financeira com pelo menos duas carteiras (comercial obrigatória se houver depósito à vista).'),
('ENT_BANCO_COMERCIAL',     'Banco Comercial', 'bancario',
    'Captação de depósitos à vista e operações de crédito de curto/médio prazo.'),
('ENT_BANCO_INVESTIMENTO',  'Banco de Investimento', 'bancario',
    'Operações de financiamento de longo prazo, underwriting, M&A.'),
('ENT_BANCO_DESENV',        'Banco de Desenvolvimento', 'bancario',
    'Banco estadual ou federal voltado a financiamento de desenvolvimento.'),
('ENT_BANCO_COOP',          'Banco Cooperativo', 'bancario',
    'Banco controlado por cooperativas de crédito.'),
('ENT_CAIXA_ECON',          'Caixa Econômica', 'bancario',
    'Instituição com atribuições especiais (CEF é única).'),
('ENT_BANCO_CAMBIO',        'Banco de Câmbio', 'bancario',
    'Instituição especializada em câmbio.'),
('ENT_SCFI',                'Sociedade de Crédito, Financiamento e Investimento', 'bancario',
    'Conhecida como financeira. Crédito ao consumidor.'),
('ENT_SCD',                 'Sociedade de Crédito Direto', 'bancario',
    'Fintech de crédito (Res CMN 4.656/2018).'),
('ENT_SEP',                 'Sociedade de Empréstimo Entre Pessoas', 'bancario',
    'Plataforma de peer-to-peer lending regulada (Res CMN 4.656/2018).'),
('ENT_COOP_CRED',           'Cooperativa de Crédito', 'bancario',
    'Sociedade cooperativa que opera crédito a associados.'),
('ENT_IP',                  'Instituição de Pagamento', 'bancario',
    'Habilitada a emitir, credenciar ou prover serviços de pagamento.'),
('ENT_AGENCIA_FOMENTO',     'Agência de Fomento', 'bancario',
    'Instituição estadual de fomento ao desenvolvimento.'),
('ENT_ARRENDAMENTO',        'Sociedade de Arrendamento Mercantil', 'bancario',
    'Operações de leasing.'),
-- Mercado de capitais
('ENT_DTVM',                'Distribuidora de Títulos e Valores Mobiliários', 'mercado_capitais',
    'Distribuição e intermediação. Reguladora primária BCB; CVM secundária.'),
('ENT_CTVM',                'Corretora de Títulos e Valores Mobiliários', 'mercado_capitais',
    'Corretagem em bolsa e balcão organizado.'),
('ENT_ADM_CARTEIRAS',       'Administrador / Gestor de Recursos', 'mercado_capitais',
    'Categoria 1 (gestor) ou Categoria 2 (administrador fiduciário).'),
('ENT_CUSTODIANTE',         'Custodiante Qualificado', 'mercado_capitais',
    'Custódia de valores mobiliários sob registro CVM.'),
('ENT_ESCRITURADOR',        'Escriturador', 'mercado_capitais',
    'Escrituração de ativos (ações, debêntures, cotas).'),
-- Seguros e capitalização
('ENT_SEGURADORA',          'Sociedade Seguradora', 'seguros',
    'Sociedade autorizada a operar seguros.'),
('ENT_RESSEG_LOCAL',        'Resseguradora Local', 'seguros',
    'Resseguradora constituída no Brasil.'),
('ENT_CAPITALIZACAO',       'Sociedade de Capitalização', 'capitalizacao',
    'Títulos de capitalização (Lei 11.795/08 e correlatas).'),
-- Previdência
('ENT_EAPC',                'Entidade Aberta de Previdência Complementar', 'previdencia',
    'Previdência complementar aberta (PGBL/VGBL).'),
('ENT_EFPC',                'Entidade Fechada de Previdência Complementar', 'previdencia',
    'Fundos de pensão patrocinados.'),
-- Conglomerado
('ENT_CONGLOMERADO',        'Conglomerado Prudencial', 'conglomerado',
    'Entidade lógica que consolida o grupo (Res CMN 4.553/2017).');

-- ---------- TIPO ENTIDADE x REGULADOR ----------
INSERT INTO tipo_entidade_regulador (tipo_entidade_id, regulador_id, papel) VALUES
-- Bancos: BCB primário; COAF e ANPD secundários universalmente
('ENT_BANCO_MULTIPLO',     'REG_BCB',   'primario'),
('ENT_BANCO_MULTIPLO',     'REG_CMN',   'primario'),
('ENT_BANCO_MULTIPLO',     'REG_COAF',  'secundario'),
('ENT_BANCO_MULTIPLO',     'REG_ANPD',  'secundario'),
('ENT_BANCO_COMERCIAL',    'REG_BCB',   'primario'),
('ENT_BANCO_COMERCIAL',    'REG_CMN',   'primario'),
('ENT_BANCO_COMERCIAL',    'REG_COAF',  'secundario'),
('ENT_BANCO_COMERCIAL',    'REG_ANPD',  'secundario'),
('ENT_BANCO_INVESTIMENTO', 'REG_BCB',   'primario'),
('ENT_BANCO_INVESTIMENTO', 'REG_CMN',   'primario'),
('ENT_BANCO_INVESTIMENTO', 'REG_CVM',   'secundario'),
('ENT_BANCO_INVESTIMENTO', 'REG_COAF',  'secundario'),
('ENT_BANCO_INVESTIMENTO', 'REG_ANPD',  'secundario'),
('ENT_BANCO_DESENV',       'REG_BCB',   'primario'),
('ENT_BANCO_DESENV',       'REG_CMN',   'primario'),
('ENT_BANCO_COOP',         'REG_BCB',   'primario'),
('ENT_BANCO_COOP',         'REG_CMN',   'primario'),
('ENT_CAIXA_ECON',         'REG_BCB',   'primario'),
('ENT_CAIXA_ECON',         'REG_CMN',   'primario'),
('ENT_BANCO_CAMBIO',       'REG_BCB',   'primario'),
('ENT_BANCO_CAMBIO',       'REG_CMN',   'primario'),
('ENT_SCFI',               'REG_BCB',   'primario'),
('ENT_SCFI',               'REG_CMN',   'primario'),
('ENT_SCD',                'REG_BCB',   'primario'),
('ENT_SCD',                'REG_CMN',   'primario'),
('ENT_SEP',                'REG_BCB',   'primario'),
('ENT_SEP',                'REG_CMN',   'primario'),
('ENT_COOP_CRED',          'REG_BCB',   'primario'),
('ENT_COOP_CRED',          'REG_CMN',   'primario'),
('ENT_IP',                 'REG_BCB',   'primario'),
('ENT_IP',                 'REG_CMN',   'primario'),
('ENT_AGENCIA_FOMENTO',    'REG_BCB',   'primario'),
('ENT_ARRENDAMENTO',       'REG_BCB',   'primario'),
-- DTVM/CTVM: BCB primário, CVM e auto-reguladores secundários
('ENT_DTVM',               'REG_BCB',     'primario'),
('ENT_DTVM',               'REG_CVM',     'secundario'),
('ENT_DTVM',               'REG_B3',      'secundario'),
('ENT_DTVM',               'REG_BSM',     'secundario'),
('ENT_DTVM',               'REG_ANBIMA',  'secundario'),
('ENT_CTVM',               'REG_BCB',     'primario'),
('ENT_CTVM',               'REG_CVM',     'secundario'),
('ENT_CTVM',               'REG_B3',      'secundario'),
('ENT_CTVM',               'REG_BSM',     'secundario'),
('ENT_CTVM',               'REG_ANBIMA',  'secundario'),
-- Asset / administradores: CVM primária
('ENT_ADM_CARTEIRAS',      'REG_CVM',     'primario'),
('ENT_ADM_CARTEIRAS',      'REG_ANBIMA',  'secundario'),
('ENT_ADM_CARTEIRAS',      'REG_COAF',    'secundario'),
('ENT_CUSTODIANTE',        'REG_CVM',     'primario'),
('ENT_CUSTODIANTE',        'REG_BCB',     'secundario'),
('ENT_ESCRITURADOR',       'REG_CVM',     'primario'),
('ENT_ESCRITURADOR',       'REG_B3',      'secundario'),
-- Seguros: SUSEP primária; CNSP normativa superior
('ENT_SEGURADORA',         'REG_SUSEP',   'primario'),
('ENT_SEGURADORA',         'REG_CNSP',    'primario'),
('ENT_SEGURADORA',         'REG_COAF',    'secundario'),
('ENT_SEGURADORA',         'REG_ANPD',    'secundario'),
('ENT_RESSEG_LOCAL',       'REG_SUSEP',   'primario'),
('ENT_RESSEG_LOCAL',       'REG_CNSP',    'primario'),
('ENT_CAPITALIZACAO',      'REG_SUSEP',   'primario'),
('ENT_CAPITALIZACAO',      'REG_CNSP',    'primario'),
-- Previdência
('ENT_EAPC',               'REG_SUSEP',   'primario'),
('ENT_EAPC',               'REG_CNSP',    'primario'),
('ENT_EFPC',               'REG_PREVIC',  'primario'),
('ENT_EFPC',               'REG_CNPC',    'primario');

-- ---------- SEGMENTOS ----------
INSERT INTO segmentos (id, regulador_id, nome, descricao, ordem) VALUES
('S1', 'REG_BCB', 'S1 - BACEN', 'ET >= 10% PIB ou atividade internacional relevante (Res CMN 4.553)', 1),
('S2', 'REG_BCB', 'S2 - BACEN', 'ET < 10% e >= 1% PIB sem atividade internacional relevante', 2),
('S3', 'REG_BCB', 'S3 - BACEN', 'ET < 1% e >= 0,1% PIB', 3),
('S4', 'REG_BCB', 'S4 - BACEN', 'ET < 0,1% PIB', 4),
('S5', 'REG_BCB', 'S5 - BACEN', 'Demais, sob estrutura simplificada de gestao de riscos', 5),
('SUS_GRANDE', 'REG_SUSEP', 'Grande porte', 'Seguradoras de grande porte (referencial)', 1),
('SUS_MEDIO',  'REG_SUSEP', 'Médio porte',  'Seguradoras de médio porte (referencial)', 2),
('SUS_PEQUENO','REG_SUSEP', 'Pequeno porte','Seguradoras de pequeno porte (referencial)', 3),
('SUS_MICRO',  'REG_SUSEP', 'Microporte',   'Seguradoras de micro porte (referencial)', 4);

-- ---------- ATIVIDADES CANÔNICAS ----------
INSERT INTO atividades_canonicas (id, nome, grupo, descricao) VALUES
-- Captação e crédito
('ATV_DEPOSITO_VISTA',         'Depósito à vista', 'captacao', NULL),
('ATV_DEPOSITO_PRAZO',         'Depósito a prazo (CDB, RDB)', 'captacao', NULL),
('ATV_POUPANCA',               'Caderneta de poupança', 'captacao', NULL),
('ATV_LCI_LCA',                'LCI / LCA', 'captacao', NULL),
('ATV_LF',                     'Letra Financeira', 'captacao', NULL),
('ATV_LIG',                    'Letra Imobiliária Garantida', 'captacao', NULL),
('ATV_CAPTACAO_EXTERIOR',      'Captação no exterior', 'captacao', NULL),
('ATV_CREDITO_PF',             'Crédito pessoa física', 'credito', NULL),
('ATV_CREDITO_PJ',             'Crédito pessoa jurídica', 'credito', NULL),
('ATV_CREDITO_CONSIGNADO',     'Crédito consignado', 'credito', NULL),
('ATV_CREDITO_VEICULAR',       'Crédito veicular', 'credito', NULL),
('ATV_CREDITO_IMOBILIARIO',    'Crédito imobiliário (SFH/SFI)', 'credito', NULL),
('ATV_CREDITO_RURAL',          'Crédito rural e agroindustrial', 'credito', NULL),
('ATV_CARTAO_CREDITO',         'Cartão de crédito (emissor)', 'credito', NULL),
('ATV_LEASING',                'Arrendamento mercantil', 'credito', NULL),
-- Câmbio
('ATV_CAMBIO_COMERCIAL',       'Câmbio comercial', 'cambio', NULL),
('ATV_CAMBIO_FINANCEIRO',      'Câmbio financeiro', 'cambio', NULL),
('ATV_CAMBIO_TURISMO',         'Câmbio turismo', 'cambio', NULL),
('ATV_TRADE_FINANCE',          'Trade finance / cartas de crédito', 'cambio', NULL),
-- Pagamentos
('ATV_PIX',                    'PIX', 'pagamentos', NULL),
('ATV_TED_DOC',                'TED / DOC', 'pagamentos', NULL),
('ATV_BOLETO',                 'Boleto bancário', 'pagamentos', NULL),
('ATV_CARTAO_CREDENCIADOR',    'Cartões (credenciador / sub-credenciador)', 'pagamentos', NULL),
('ATV_OPEN_FINANCE',           'Open Finance', 'pagamentos', NULL),
-- Tesouraria
('ATV_TRADING_PROPRIO',        'Trading proprietário', 'tesouraria', NULL),
('ATV_ALM',                    'Gestão de ativos e passivos', 'tesouraria', NULL),
-- Mercado de capitais
('ATV_DISTRIBUICAO_VM',        'Distribuição de valores mobiliários', 'mercado_capitais', NULL),
('ATV_GESTAO_RECURSOS',        'Gestão de recursos (asset management)', 'mercado_capitais', NULL),
('ATV_ADM_FIDUCIARIA',         'Administração fiduciária de fundos', 'mercado_capitais', NULL),
('ATV_CUSTODIA_QUALIFICADA',   'Custódia qualificada', 'mercado_capitais', NULL),
('ATV_ESCRITURACAO',           'Escrituração de ativos', 'mercado_capitais', NULL),
('ATV_RESEARCH',               'Research / análise de valores mobiliários', 'mercado_capitais', NULL),
('ATV_FORMADOR_MERCADO',       'Formador de mercado', 'mercado_capitais', NULL),
-- Seguros
('ATV_SUBSCRICAO_VIDA',        'Subscrição de seguro de vida', 'seguros', NULL),
('ATV_SUBSCRICAO_NAO_VIDA',    'Subscrição de seguro não-vida (P&C)', 'seguros', NULL),
('ATV_RESSEGURO',              'Resseguro', 'seguros', NULL),
('ATV_CAPITALIZACAO',          'Capitalização', 'seguros', NULL),
('ATV_PREVIDENCIA_ABERTA',     'Previdência aberta (PGBL/VGBL)', 'previdencia', NULL),
('ATV_PREVIDENCIA_FECHADA',    'Previdência fechada (EFPC)', 'previdencia', NULL);

COMMIT;

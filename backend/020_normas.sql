-- ============================================================
-- 020_normas.sql
-- Top normas estruturantes com aplicabilidade
-- ATENCAO: numeros, datas e status devem ser revalidados contra
-- a base oficial dos reguladores antes de uso operacional.
-- ============================================================

BEGIN;

-- ---------- NORMAS ----------

-- Legislacao superior (universal SFN/SNSP)
INSERT INTO normas (id, tipo, numero, ano, regulador_id, ementa, status, vigencia_inicio, notas) VALUES
('LEX_4595_64',   'lei', '4.595', 1964, 'REG_CMN',
    'Lei da Reforma Bancaria. Cria CMN e BCB; estrutura o SFN.',
    'vigente', '1964-12-31', 'Lei estruturante. Aplica-se de forma informativa a todo SFN.'),
('LEX_6385_76',   'lei', '6.385', 1976, 'REG_CVM',
    'Cria a CVM e dispoe sobre o mercado de valores mobiliarios.',
    'vigente', '1976-12-07', NULL),
('LEX_DL_73_66',  'decreto_lei', '73', 1966, 'REG_CNSP',
    'Sistema Nacional de Seguros Privados. Estrutura SUSEP, CNSP, IRB.',
    'vigente', '1966-11-21', NULL),
('LEX_LC_109_01', 'lei_complementar', 'LC 109', 2001, 'REG_CNPC',
    'Regime de previdencia complementar (aberta e fechada).',
    'vigente', '2001-05-29', NULL),
('LEX_LC_105_01', 'lei_complementar', 'LC 105', 2001, 'REG_BCB',
    'Sigilo das operacoes financeiras.',
    'vigente', '2001-01-10', NULL),
('LEX_9613_98',   'lei', '9.613', 1998, 'REG_COAF',
    'Crimes de lavagem de dinheiro e PLD-FT. Cria o COAF.',
    'vigente', '1998-03-03', 'Alterada substancialmente pela Lei 12.683/2012.'),
('LEX_12846_13',  'lei', '12.846', 2013, 'REG_BCB',
    'Lei Anticorrupcao. Responsabilizacao administrativa e civil de PJ.',
    'vigente', '2013-08-01', NULL),
('LEX_13709_18',  'lei', '13.709', 2018, 'REG_ANPD',
    'LGPD - Lei Geral de Protecao de Dados Pessoais.',
    'vigente', '2018-08-14', 'Em vigor desde 2020. Sancao a partir de 2021.'),
('LEX_8078_90',   'lei', '8.078', 1990, 'REG_BCB',
    'Codigo de Defesa do Consumidor.',
    'vigente', '1990-09-11', 'Aplica-se quando ha relacao de consumo bancaria.');

-- Normas BACEN/CMN estruturantes
INSERT INTO normas (id, tipo, numero, ano, regulador_id, titulo, ementa, status, vigencia_inicio, notas) VALUES
('RES_CMN_4557_17', 'res_cmn', '4.557', 2017, 'REG_CMN',
    'Estrutura de gerenciamento de riscos e capital',
    'Dispoe sobre a estrutura de gerenciamento continuo e integrado de riscos (GIR) e capital.',
    'vigente', '2017-02-23',
    'Norma central do RCSA brasileiro. Aplicacao diferenciada por segmento.'),
('RES_CMN_4553_17', 'res_cmn', '4.553', 2017, 'REG_CMN',
    'Segmentacao prudencial S1-S5',
    'Estabelece segmentacao das instituicoes financeiras para fins de aplicacao proporcional da regulacao prudencial.',
    'vigente', '2017-01-30', NULL),
('RES_CMN_4193_13', 'res_cmn', '4.193', 2013, 'REG_CMN',
    'Apuracao de capital regulamentar',
    'Apuracao dos requerimentos minimos de Patrimonio de Referencia (PR), Capital Nivel I e Capital Principal (Basileia III).',
    'vigente', '2013-03-01', NULL),
('RES_BCB_200_22',  'res_bcb', '200', 2022, 'REG_BCB',
    'Estrutura simplificada de gerenciamento de riscos',
    'Estrutura simplificada e continua de gerenciamento de riscos para instituicoes do segmento S3, S4 e S5.',
    'vigente', '2022-03-11', NULL),
('RES_CMN_4893_21', 'res_cmn', '4.893', 2021, 'REG_CMN',
    'Politica de seguranca cibernetica e contratacao de servicos de processamento e armazenamento em nuvem',
    'Dispoe sobre politica de seguranca cibernetica e os requisitos para contratacao de servicos de processamento e armazenamento de dados em nuvem.',
    'vigente', '2021-02-26', NULL),
('RES_CMN_4943_21', 'res_cmn', '4.943', 2021, 'REG_CMN',
    'Sistema de controles internos',
    'Estabelece principios para o sistema de controles internos das instituicoes financeiras.',
    'vigente', '2021-09-15',
    'Atualizou disciplina anterior da 2.554/98.'),
('RES_CMN_4945_21', 'res_cmn', '4.945', 2021, 'REG_CMN',
    'PRSAC - Politica de Responsabilidade Social, Ambiental e Climatica',
    'Estabelece a Politica de Responsabilidade Social, Ambiental e Climatica das instituicoes financeiras.',
    'vigente', '2021-09-15', NULL),
('RES_CMN_4860_20', 'res_cmn', '4.860', 2020, 'REG_CMN',
    'Componente organizacional de Ouvidoria',
    'Dispoe sobre a constituicao e o funcionamento de componente organizacional de ouvidoria pelas instituicoes financeiras.',
    'vigente', '2020-10-23', NULL),
('CIR_BCB_3978_20', 'circ_bcb', '3.978', 2020, 'REG_BCB',
    'PLD-FT no SFN',
    'Dispoe sobre politicas, procedimentos e controles de PLD-FT no ambito do SFN.',
    'vigente', '2020-01-23',
    'Substituiu Circular 3.461.'),
('RES_CMN_4502_16', 'res_cmn', '4.502', 2016, 'REG_CMN',
    'Plano de Recuperacao',
    'Plano de Recuperacao a ser elaborado pelas instituicoes do segmento S1.',
    'vigente', '2016-06-30',
    'Aplica-se apenas a S1.'),
('RES_CMN_4966_21', 'res_cmn', '4.966', 2021, 'REG_CMN',
    'Provisoes para perdas associadas a risco de credito',
    'Conceitos e criterios contabeis aplicaveis a instrumentos financeiros e provisoes (alinhamento a IFRS 9 / CPC 48).',
    'vigente', '2021-11-25',
    'Producao de efeitos a partir de 2025.');

-- Normas CVM estruturantes
INSERT INTO normas (id, tipo, numero, ano, regulador_id, titulo, ementa, status, vigencia_inicio, notas) VALUES
('RES_CVM_35_21',  'res_cvm', '35',  2021, 'REG_CVM',
    'Conduta de distribuicao e suitability',
    'Normas de conduta a serem observadas pelos integrantes do sistema de distribuicao de valores mobiliarios e suitability.',
    'vigente', '2021-05-26', NULL),
('RES_CVM_50_21',  'res_cvm', '50',  2021, 'REG_CVM',
    'PLD-FT no mercado de valores mobiliarios',
    'PLD-FT aplicaveis aos integrantes do sistema de distribuicao e participantes do mercado de valores mobiliarios.',
    'vigente', '2021-08-31', NULL),
('RES_CVM_21_21',  'res_cvm', '21',  2021, 'REG_CVM',
    'Administracao de carteiras de valores mobiliarios',
    'Atividade de administracao de carteiras (categorias 1 - gestor e 2 - administrador fiduciario).',
    'vigente', '2021-02-26', NULL),
('RES_CVM_175_22', 'res_cvm', '175', 2022, 'REG_CVM',
    'Fundos de Investimento (regime unico)',
    'Estabelece o regime unico para fundos de investimento (consolidacao das antigas instrucoes 555, 356, 472 etc.).',
    'vigente', '2022-12-23',
    'Marco regulatorio dos fundos. Substitui multiplas instrucoes anteriores.');

-- Normas SUSEP/CNSP estruturantes
INSERT INTO normas (id, tipo, numero, ano, regulador_id, titulo, ementa, status, vigencia_inicio, notas) VALUES
('RES_CNSP_416_21', 'res_cnsp', '416', 2021, 'REG_CNSP',
    'Estrutura de gestao de riscos e controles internos',
    'Dispoe sobre a estrutura de gestao de riscos, controles internos e auditoria interna a ser implantada pelas sociedades supervisionadas.',
    'vigente', '2021-07-29', 'Equivalente da 4.557 para o universo SUSEP.'),
('CIR_SUSEP_648_21','circ_susep', '648', 2021, 'REG_SUSEP',
    'ORSA - autoavaliacao de riscos e solvencia',
    'Procedimentos para autoavaliacao de riscos e solvencia (ORSA).',
    'vigente', '2021-12-15', NULL);

-- Codigos ANBIMA (auto-regulacao voluntaria)
INSERT INTO normas (id, tipo, numero, ano, regulador_id, titulo, ementa, status, notas) VALUES
('COD_ANBIMA_DISTR', 'codigo_anbima', 'Distribuicao', NULL, 'REG_ANBIMA',
    'Codigo ANBIMA de Distribuicao de Produtos de Investimento',
    'Auto-regulacao voluntaria para distribuicao de produtos de investimento.',
    'vigente',
    'Aplica-se apenas a aderentes ANBIMA.'),
('COD_ANBIMA_GEST',  'codigo_anbima', 'Adm e Gestao', NULL, 'REG_ANBIMA',
    'Codigo ANBIMA de Administracao e Gestao de Recursos de Terceiros',
    'Auto-regulacao voluntaria para adm fiduciaria e gestao.',
    'vigente',
    'Aplica-se apenas a aderentes ANBIMA.');

-- ---------- ARTIGOS-CHAVE (granularidade fina seletiva) ----------

INSERT INTO norma_artigos (norma_id, numero, secao, tema) VALUES
('RES_CMN_4557_17', '38',  NULL, 'RCSA - autoavaliacao de riscos e controles'),
('RES_CMN_4557_17', '50',  NULL, 'Continuidade de negocios'),
('RES_CMN_4557_17', '56',  NULL, 'Apetite ao risco (RAS)'),
('RES_CMN_4557_17', '21',  NULL, 'Risco de credito'),
('RES_CMN_4557_17', '32',  NULL, 'Risco operacional'),
('RES_CMN_4557_17', '40',  NULL, 'Risco de liquidez'),
('CIR_BCB_3978_20', '6',   NULL, 'Avaliacao interna de risco PLD-FT'),
('CIR_BCB_3978_20', '20',  NULL, 'KYC - cadastro de clientes'),
('CIR_BCB_3978_20', '32',  NULL, 'Monitoramento e selecao de operacoes'),
('CIR_BCB_3978_20', '44',  NULL, 'Comunicacao ao COAF'),
('RES_CMN_4893_21', '3',   NULL, 'Politica de seguranca cibernetica'),
('RES_CMN_4893_21', '13',  NULL, 'Plano de acao e resposta a incidentes'),
('RES_CMN_4893_21', '18',  NULL, 'Contratacao de servicos em nuvem');

-- ---------- APLICABILIDADE: TIPOS DE ENTIDADE ----------

-- Res CMN 4.557 - aplica a todas IFs sob BCB
INSERT INTO norma_aplicabilidade_tipo_entidade (norma_id, tipo_entidade_id) VALUES
('RES_CMN_4557_17', 'ENT_BANCO_MULTIPLO'),
('RES_CMN_4557_17', 'ENT_BANCO_COMERCIAL'),
('RES_CMN_4557_17', 'ENT_BANCO_INVESTIMENTO'),
('RES_CMN_4557_17', 'ENT_BANCO_DESENV'),
('RES_CMN_4557_17', 'ENT_BANCO_COOP'),
('RES_CMN_4557_17', 'ENT_CAIXA_ECON'),
('RES_CMN_4557_17', 'ENT_BANCO_CAMBIO'),
('RES_CMN_4557_17', 'ENT_SCFI'),
('RES_CMN_4557_17', 'ENT_DTVM'),
('RES_CMN_4557_17', 'ENT_CTVM');

-- Res CMN 4.553 - todas IFs do BCB
INSERT INTO norma_aplicabilidade_tipo_entidade (norma_id, tipo_entidade_id)
SELECT 'RES_CMN_4553_17', id FROM tipos_entidade WHERE grupo IN ('bancario','mercado_capitais') AND id <> 'ENT_ADM_CARTEIRAS';

-- Res CMN 4.193 - bancos e DTVM/CTVM
INSERT INTO norma_aplicabilidade_tipo_entidade (norma_id, tipo_entidade_id) VALUES
('RES_CMN_4193_13', 'ENT_BANCO_MULTIPLO'),
('RES_CMN_4193_13', 'ENT_BANCO_COMERCIAL'),
('RES_CMN_4193_13', 'ENT_BANCO_INVESTIMENTO'),
('RES_CMN_4193_13', 'ENT_BANCO_DESENV'),
('RES_CMN_4193_13', 'ENT_BANCO_COOP'),
('RES_CMN_4193_13', 'ENT_CAIXA_ECON'),
('RES_CMN_4193_13', 'ENT_BANCO_CAMBIO');

-- Res BCB 200 - estrutura simplificada
INSERT INTO norma_aplicabilidade_tipo_entidade (norma_id, tipo_entidade_id) VALUES
('RES_BCB_200_22', 'ENT_BANCO_MULTIPLO'),
('RES_BCB_200_22', 'ENT_BANCO_COMERCIAL'),
('RES_BCB_200_22', 'ENT_SCFI'),
('RES_BCB_200_22', 'ENT_SCD'),
('RES_BCB_200_22', 'ENT_SEP'),
('RES_BCB_200_22', 'ENT_COOP_CRED'),
('RES_BCB_200_22', 'ENT_IP');

-- Res CMN 4.893 (ciber) - todas IFs sob BCB
INSERT INTO norma_aplicabilidade_tipo_entidade (norma_id, tipo_entidade_id)
SELECT 'RES_CMN_4893_21', id FROM tipos_entidade WHERE grupo = 'bancario';

-- Res CMN 4.943 (controles internos) - todas IFs sob BCB
INSERT INTO norma_aplicabilidade_tipo_entidade (norma_id, tipo_entidade_id)
SELECT 'RES_CMN_4943_21', id FROM tipos_entidade WHERE grupo = 'bancario';

-- Res CMN 4.945 (PRSAC) - todas IFs sob BCB
INSERT INTO norma_aplicabilidade_tipo_entidade (norma_id, tipo_entidade_id)
SELECT 'RES_CMN_4945_21', id FROM tipos_entidade WHERE grupo = 'bancario';

-- Res CMN 4.860 (ouvidoria) - todas IFs sob BCB
INSERT INTO norma_aplicabilidade_tipo_entidade (norma_id, tipo_entidade_id)
SELECT 'RES_CMN_4860_20', id FROM tipos_entidade WHERE grupo = 'bancario';

-- Circ BCB 3.978 (PLD) - todas IFs sob BCB
INSERT INTO norma_aplicabilidade_tipo_entidade (norma_id, tipo_entidade_id)
SELECT 'CIR_BCB_3978_20', id FROM tipos_entidade WHERE grupo = 'bancario';

-- Res CMN 4.502 (Plano de Recuperacao) - apenas grandes (S1)
INSERT INTO norma_aplicabilidade_tipo_entidade (norma_id, tipo_entidade_id) VALUES
('RES_CMN_4502_16', 'ENT_BANCO_MULTIPLO'),
('RES_CMN_4502_16', 'ENT_BANCO_COMERCIAL'),
('RES_CMN_4502_16', 'ENT_BANCO_INVESTIMENTO'),
('RES_CMN_4502_16', 'ENT_CAIXA_ECON');

-- Res CMN 4.966 (IFRS 9) - todas IFs sob BCB
INSERT INTO norma_aplicabilidade_tipo_entidade (norma_id, tipo_entidade_id)
SELECT 'RES_CMN_4966_21', id FROM tipos_entidade WHERE grupo = 'bancario';

-- CVM
INSERT INTO norma_aplicabilidade_tipo_entidade (norma_id, tipo_entidade_id) VALUES
('RES_CVM_35_21',  'ENT_DTVM'),
('RES_CVM_35_21',  'ENT_CTVM'),
('RES_CVM_35_21',  'ENT_BANCO_INVESTIMENTO'),
('RES_CVM_50_21',  'ENT_DTVM'),
('RES_CVM_50_21',  'ENT_CTVM'),
('RES_CVM_50_21',  'ENT_ADM_CARTEIRAS'),
('RES_CVM_50_21',  'ENT_CUSTODIANTE'),
('RES_CVM_21_21',  'ENT_ADM_CARTEIRAS'),
('RES_CVM_175_22', 'ENT_ADM_CARTEIRAS'),
('RES_CVM_175_22', 'ENT_CUSTODIANTE'),
('RES_CVM_175_22', 'ENT_DTVM'),
('RES_CVM_175_22', 'ENT_CTVM');

-- SUSEP
INSERT INTO norma_aplicabilidade_tipo_entidade (norma_id, tipo_entidade_id) VALUES
('RES_CNSP_416_21', 'ENT_SEGURADORA'),
('RES_CNSP_416_21', 'ENT_RESSEG_LOCAL'),
('RES_CNSP_416_21', 'ENT_CAPITALIZACAO'),
('RES_CNSP_416_21', 'ENT_EAPC'),
('CIR_SUSEP_648_21','ENT_SEGURADORA'),
('CIR_SUSEP_648_21','ENT_RESSEG_LOCAL');

-- ANBIMA
INSERT INTO norma_aplicabilidade_tipo_entidade (norma_id, tipo_entidade_id) VALUES
('COD_ANBIMA_DISTR', 'ENT_DTVM'),
('COD_ANBIMA_DISTR', 'ENT_CTVM'),
('COD_ANBIMA_DISTR', 'ENT_BANCO_INVESTIMENTO'),
('COD_ANBIMA_GEST',  'ENT_ADM_CARTEIRAS');

-- Universal: LGPD aplica a TODOS os tipos de entidade
INSERT INTO norma_aplicabilidade_tipo_entidade (norma_id, tipo_entidade_id)
SELECT 'LEX_13709_18', id FROM tipos_entidade WHERE id <> 'ENT_CONGLOMERADO';

-- Universal: Lei 9.613 (PLD)
INSERT INTO norma_aplicabilidade_tipo_entidade (norma_id, tipo_entidade_id)
SELECT 'LEX_9613_98', id FROM tipos_entidade WHERE id <> 'ENT_CONGLOMERADO';

-- Universal: Lei Anticorrupcao
INSERT INTO norma_aplicabilidade_tipo_entidade (norma_id, tipo_entidade_id)
SELECT 'LEX_12846_13', id FROM tipos_entidade WHERE id <> 'ENT_CONGLOMERADO';

-- ---------- APLICABILIDADE: SEGMENTOS ----------

-- 4.557 aplica a S1, S2, S3, S4 (S5 segue a estrutura simplificada Res BCB 200)
INSERT INTO norma_aplicabilidade_segmento (norma_id, segmento_id) VALUES
('RES_CMN_4557_17', 'S1'),
('RES_CMN_4557_17', 'S2'),
('RES_CMN_4557_17', 'S3'),
('RES_CMN_4557_17', 'S4');

-- BCB 200 aplica a S3, S4, S5
INSERT INTO norma_aplicabilidade_segmento (norma_id, segmento_id) VALUES
('RES_BCB_200_22', 'S3'),
('RES_BCB_200_22', 'S4'),
('RES_BCB_200_22', 'S5');

-- Plano de Recuperacao apenas S1
INSERT INTO norma_aplicabilidade_segmento (norma_id, segmento_id) VALUES
('RES_CMN_4502_16', 'S1');

-- ---------- APLICABILIDADE: ATIVIDADES ----------

-- Codigos ANBIMA por atividade
INSERT INTO norma_aplicabilidade_atividade (norma_id, atividade_id) VALUES
('COD_ANBIMA_DISTR', 'ATV_DISTRIBUICAO_VM'),
('COD_ANBIMA_GEST',  'ATV_GESTAO_RECURSOS'),
('COD_ANBIMA_GEST',  'ATV_ADM_FIDUCIARIA');

-- CVM 35 e suitability — exige distribuicao de VM
INSERT INTO norma_aplicabilidade_atividade (norma_id, atividade_id) VALUES
('RES_CVM_35_21', 'ATV_DISTRIBUICAO_VM');

-- CVM 175 — gestao ou administracao fiduciaria
INSERT INTO norma_aplicabilidade_atividade (norma_id, atividade_id) VALUES
('RES_CVM_175_22', 'ATV_GESTAO_RECURSOS'),
('RES_CVM_175_22', 'ATV_ADM_FIDUCIARIA'),
('RES_CVM_175_22', 'ATV_CUSTODIA_QUALIFICADA');

COMMIT;

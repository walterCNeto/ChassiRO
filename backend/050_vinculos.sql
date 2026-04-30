-- ============================================================
-- 050_vinculos.sql
-- Vinculos norma <-> processo, norma <-> risco, processo <-> risco
-- ATENCAO: tipo_vinculo e materialidade default sao SUGESTOES
-- iniciais. Cada instituicao deve revisar conforme sua realidade.
-- ============================================================

BEGIN;

-- ============================================================
-- VINCULO NORMA -> PROCESSO
-- ============================================================

-- Res CMN 4.557 (GIR) - primaria em todos os nodes de gestao de riscos
INSERT INTO vinculo_norma_processo (norma_id, processo_id, artigo_ref, tipo_vinculo) VALUES
('RES_CMN_4557_17', 'P0.U.2',     NULL,  'primaria'),
('RES_CMN_4557_17', 'P1.U.2.1',   NULL,  'primaria'),
('RES_CMN_4557_17', 'P1.U.2.2',   NULL,  'primaria'),
('RES_CMN_4557_17', 'P1.U.2.3',   NULL,  'primaria'),
('RES_CMN_4557_17', 'P1.U.2.4',   NULL,  'primaria'),
('RES_CMN_4557_17', 'P1.U.2.5',   NULL,  'primaria'),
('RES_CMN_4557_17', 'P1.U.2.7',   NULL,  'primaria'),
('RES_CMN_4557_17', 'P2.U.2.2.1', '38',  'primaria'),
('RES_CMN_4557_17', 'P0.U.9',     '50',  'secundaria'),
('RES_CMN_4557_17', 'P1.U.1.3',   '56',  'primaria');

-- Res CMN 4.553 (segmentacao)
INSERT INTO vinculo_norma_processo (norma_id, processo_id, tipo_vinculo) VALUES
('RES_CMN_4553_17', 'P0.U.1',     'primaria'),
('RES_CMN_4553_17', 'P1.U.12.4',  'primaria');

-- Res CMN 4.193 (capital)
INSERT INTO vinculo_norma_processo (norma_id, processo_id, tipo_vinculo) VALUES
('RES_CMN_4193_13', 'P0.B.3',     'primaria'),
('RES_CMN_4193_13', 'P0.U.12',    'primaria'),
('RES_CMN_4193_13', 'P1.U.2.7',   'primaria'),
('RES_CMN_4193_13', 'P0.CG.2',    'primaria');

-- Res BCB 200 (estrutura simplificada)
INSERT INTO vinculo_norma_processo (norma_id, processo_id, tipo_vinculo) VALUES
('RES_BCB_200_22', 'P0.U.2',  'primaria'),
('RES_BCB_200_22', 'P1.U.2.2','primaria'),
('RES_BCB_200_22', 'P1.U.2.5','primaria');

-- Res CMN 4.893 (ciber e nuvem)
INSERT INTO vinculo_norma_processo (norma_id, processo_id, artigo_ref, tipo_vinculo) VALUES
('RES_CMN_4893_21', 'P0.U.8',     '3',  'primaria'),
('RES_CMN_4893_21', 'P1.U.8.1',   '3',  'primaria'),
('RES_CMN_4893_21', 'P1.U.8.4',   '13', 'primaria'),
('RES_CMN_4893_21', 'P1.U.7.3',   '18', 'primaria'),
('RES_CMN_4893_21', 'P0.U.10',    '18', 'secundaria');

-- Res CMN 4.943 (controles internos)
INSERT INTO vinculo_norma_processo (norma_id, processo_id, tipo_vinculo) VALUES
('RES_CMN_4943_21', 'P0.U.3',     'primaria'),
('RES_CMN_4943_21', 'P0.U.5',     'primaria'),
('RES_CMN_4943_21', 'P1.U.3.2',   'primaria');

-- Res CMN 4.945 (PRSAC)
INSERT INTO vinculo_norma_processo (norma_id, processo_id, tipo_vinculo) VALUES
('RES_CMN_4945_21', 'P0.U.1',  'primaria'),
('RES_CMN_4945_21', 'P0.U.2',  'secundaria'),
('RES_CMN_4945_21', 'P1.U.1.2','primaria');

-- Res CMN 4.860 (Ouvidoria)
INSERT INTO vinculo_norma_processo (norma_id, processo_id, tipo_vinculo) VALUES
('RES_CMN_4860_20', 'P0.U.13',    'primaria'),
('RES_CMN_4860_20', 'P1.U.13.2',  'primaria'),
('RES_CMN_4860_20', 'P1.U.13.3',  'primaria');

-- Circ BCB 3.978 (PLD)
INSERT INTO vinculo_norma_processo (norma_id, processo_id, artigo_ref, tipo_vinculo) VALUES
('CIR_BCB_3978_20', 'P0.U.4',     NULL, 'primaria'),
('CIR_BCB_3978_20', 'P1.U.4.1',   '20', 'primaria'),
('CIR_BCB_3978_20', 'P1.U.4.2',   '32', 'primaria'),
('CIR_BCB_3978_20', 'P1.U.4.3',   '44', 'primaria'),
('CIR_BCB_3978_20', 'P1.U.4.5',   '6',  'primaria'),
('CIR_BCB_3978_20', 'P1.U.4.6',   NULL, 'primaria'),
('CIR_BCB_3978_20', 'P2.U.4.1.1', '20', 'primaria'),
('CIR_BCB_3978_20', 'P2.U.4.1.2', NULL, 'primaria'),
('CIR_BCB_3978_20', 'P2.U.4.1.3', NULL, 'primaria');

-- Res CMN 4.502 (Plano de Recuperacao - apenas S1)
INSERT INTO vinculo_norma_processo (norma_id, processo_id, tipo_vinculo) VALUES
('RES_CMN_4502_16', 'P0.CG.3',    'primaria'),
('RES_CMN_4502_16', 'P1.U.2.6',   'primaria'),
('RES_CMN_4502_16', 'P1.CG.3.1',  'primaria'),
('RES_CMN_4502_16', 'P1.CG.3.2',  'primaria'),
('RES_CMN_4502_16', 'P1.CG.3.3',  'primaria');

-- Res CMN 4.966 (IFRS 9)
INSERT INTO vinculo_norma_processo (norma_id, processo_id, tipo_vinculo) VALUES
('RES_CMN_4966_21', 'P1.B.2.6',   'primaria'),
('RES_CMN_4966_21', 'P1.U.12.1',  'secundaria');

-- LGPD - aplica em todos os processos de tratamento de dados, primaria nos especificos
INSERT INTO vinculo_norma_processo (norma_id, processo_id, tipo_vinculo) VALUES
('LEX_13709_18', 'P0.U.15',     'primaria'),
('LEX_13709_18', 'P1.U.15.1',   'primaria'),
('LEX_13709_18', 'P1.U.15.2',   'primaria'),
('LEX_13709_18', 'P1.U.15.3',   'primaria'),
('LEX_13709_18', 'P1.U.15.4',   'primaria'),
('LEX_13709_18', 'P1.U.15.5',   'primaria'),
('LEX_13709_18', 'P1.U.15.6',   'primaria'),
('LEX_13709_18', 'P0.U.7',      'secundaria'),
('LEX_13709_18', 'P0.U.8',      'secundaria'),
('LEX_13709_18', 'P2.U.4.1.1',  'secundaria');

-- Lei 9.613 (PLD)
INSERT INTO vinculo_norma_processo (norma_id, processo_id, tipo_vinculo) VALUES
('LEX_9613_98', 'P0.U.4',     'primaria'),
('LEX_9613_98', 'P1.U.4.3',   'primaria');

-- Lei Anticorrupcao
INSERT INTO vinculo_norma_processo (norma_id, processo_id, tipo_vinculo) VALUES
('LEX_12846_13', 'P1.U.3.3',  'primaria'),
('LEX_12846_13', 'P1.U.3.4',  'primaria'),
('LEX_12846_13', 'P1.U.3.5',  'secundaria');

-- LC 105 (sigilo)
INSERT INTO vinculo_norma_processo (norma_id, processo_id, tipo_vinculo) VALUES
('LEX_LC_105_01', 'P0.U.3',     'informativa'),
('LEX_LC_105_01', 'P0.U.7',     'informativa'),
('LEX_LC_105_01', 'P0.U.15',    'secundaria');

-- CDC
INSERT INTO vinculo_norma_processo (norma_id, processo_id, tipo_vinculo) VALUES
('LEX_8078_90', 'P0.U.13',    'primaria'),
('LEX_8078_90', 'P1.U.14.3',  'primaria');

-- CVM 35 (suitability)
INSERT INTO vinculo_norma_processo (norma_id, processo_id, tipo_vinculo) VALUES
('RES_CVM_35_21', 'P0.MC.1',     'primaria'),
('RES_CVM_35_21', 'P1.MC.1.1',   'primaria'),
('RES_CVM_35_21', 'P1.MC.1.3',   'primaria'),
('RES_CVM_35_21', 'P1.U.3.6',    'secundaria');

-- CVM 50 (PLD MercCap)
INSERT INTO vinculo_norma_processo (norma_id, processo_id, tipo_vinculo) VALUES
('RES_CVM_50_21', 'P0.U.4',   'primaria'),
('RES_CVM_50_21', 'P1.U.4.1', 'primaria'),
('RES_CVM_50_21', 'P1.U.4.2', 'primaria');

-- CVM 21 (Adm Carteiras)
INSERT INTO vinculo_norma_processo (norma_id, processo_id, tipo_vinculo) VALUES
('RES_CVM_21_21', 'P0.MC.2',    'primaria'),
('RES_CVM_21_21', 'P0.MC.3',    'primaria'),
('RES_CVM_21_21', 'P1.MC.2.2',  'primaria'),
('RES_CVM_21_21', 'P1.MC.2.4',  'primaria');

-- CVM 175 (Fundos)
INSERT INTO vinculo_norma_processo (norma_id, processo_id, tipo_vinculo) VALUES
('RES_CVM_175_22', 'P0.MC.2',    'primaria'),
('RES_CVM_175_22', 'P0.MC.3',    'primaria'),
('RES_CVM_175_22', 'P0.MC.4',    'primaria'),
('RES_CVM_175_22', 'P1.MC.2.1',  'primaria'),
('RES_CVM_175_22', 'P1.MC.2.5',  'primaria'),
('RES_CVM_175_22', 'P1.MC.3.2',  'primaria');

-- CNSP 416 (gestao riscos seguros)
INSERT INTO vinculo_norma_processo (norma_id, processo_id, tipo_vinculo) VALUES
('RES_CNSP_416_21', 'P0.U.2',     'primaria'),
('RES_CNSP_416_21', 'P0.U.3',     'primaria'),
('RES_CNSP_416_21', 'P0.U.5',     'primaria'),
('RES_CNSP_416_21', 'P0.S.3',     'secundaria');

-- SUSEP 648 (ORSA)
INSERT INTO vinculo_norma_processo (norma_id, processo_id, tipo_vinculo) VALUES
('CIR_SUSEP_648_21', 'P1.U.2.7',  'primaria'),
('CIR_SUSEP_648_21', 'P1.U.2.2',  'primaria'),
('CIR_SUSEP_648_21', 'P0.S.3',    'secundaria');

-- ANBIMA Distribuicao
INSERT INTO vinculo_norma_processo (norma_id, processo_id, tipo_vinculo) VALUES
('COD_ANBIMA_DISTR', 'P0.MC.1',    'primaria'),
('COD_ANBIMA_DISTR', 'P1.MC.1.1',  'primaria');

-- ANBIMA Adm e Gestao
INSERT INTO vinculo_norma_processo (norma_id, processo_id, tipo_vinculo) VALUES
('COD_ANBIMA_GEST', 'P0.MC.2',    'primaria'),
('COD_ANBIMA_GEST', 'P0.MC.3',    'primaria');

-- ============================================================
-- VINCULO NORMA -> RISCO
-- ============================================================

INSERT INTO vinculo_norma_risco (norma_id, risco_id, tipo_vinculo) VALUES
-- 4.557 cobre todos os riscos universais
('RES_CMN_4557_17','R0.U.1','primaria'),
('RES_CMN_4557_17','R0.U.2','primaria'),
('RES_CMN_4557_17','R0.U.3','primaria'),
('RES_CMN_4557_17','R0.U.4','primaria'),
('RES_CMN_4557_17','R0.U.6','secundaria'),
-- 4.193 capital -> credito, mercado, operacional
('RES_CMN_4193_13','R0.U.1','primaria'),
('RES_CMN_4193_13','R0.U.2','primaria'),
('RES_CMN_4193_13','R0.U.4','primaria'),
-- 4.893 ciber
('RES_CMN_4893_21','R0.U.5','primaria'),
('RES_CMN_4893_21','R0.U.4','secundaria'),
-- 4.943 controles internos
('RES_CMN_4943_21','R0.U.4','primaria'),
('RES_CMN_4943_21','R0.U.6','primaria'),
-- 4.945 PRSAC
('RES_CMN_4945_21','R0.U.11','primaria'),
('RES_CMN_4945_21','R0.U.10','secundaria'),
-- 3.978 e 9.613 PLD
('CIR_BCB_3978_20','R0.U.8','primaria'),
('LEX_9613_98',    'R0.U.8','primaria'),
-- LGPD
('LEX_13709_18','R0.U.13','primaria'),
('LEX_13709_18','R0.U.5', 'secundaria'),
-- Anticorrupcao
('LEX_12846_13','R0.U.8','secundaria'),
('LEX_12846_13','R0.U.7','secundaria'),
-- 4.502 Plano de Recuperacao
('RES_CMN_4502_16','R0.U.3','primaria'),
('RES_CMN_4502_16','R0.U.9','secundaria'),
-- 4.966 IFRS 9
('RES_CMN_4966_21','R0.U.1','primaria'),
-- CVM 35 suitability
('RES_CVM_35_21','R0.MC.1','primaria'),
('RES_CVM_35_21','R0.U.7','primaria'),
-- CVM 21
('RES_CVM_21_21','R0.MC.4','primaria'),
('RES_CVM_21_21','R0.U.4','secundaria'),
-- CVM 175
('RES_CVM_175_22','R0.MC.3','primaria'),
('RES_CVM_175_22','R0.MC.4','primaria'),
-- CNSP 416
('RES_CNSP_416_21','R0.U.4','primaria'),
('RES_CNSP_416_21','R0.S.1','primaria'),
('RES_CNSP_416_21','R0.S.2','primaria'),
-- ORSA
('CIR_SUSEP_648_21','R0.S.2','primaria'),
('CIR_SUSEP_648_21','R0.U.3','primaria');

-- ============================================================
-- MATRIZ PROCESSO x RISCO (com materialidade default 1-5)
-- ============================================================

-- Apenas amostras representativas - cobertura completa em iteracao posterior

-- Credito (P0.B.2) endereca riscos de credito, operacional, conformidade
INSERT INTO vinculo_processo_risco (processo_id, risco_id, materialidade_default) VALUES
('P0.B.2',     'R0.U.1', 5),
('P0.B.2',     'R0.U.4', 4),
('P0.B.2',     'R0.U.6', 3),
('P1.B.2.1',   'R0.U.1', 5),
('P1.B.2.1',   'R0.U.4', 3),
('P1.B.2.2',   'R0.U.1', 5),
('P1.B.2.2',   'R0.U.12',4),
('P1.B.2.6',   'R0.U.1', 5),
('P1.B.2.6',   'R0.U.12',4),
('P2.B.2.2.1', 'R0.U.12',5),
('P2.B.2.2.1', 'R0.U.1', 5);

-- Tesouraria (P0.B.3)
INSERT INTO vinculo_processo_risco (processo_id, risco_id, materialidade_default) VALUES
('P0.B.3',  'R0.U.2', 5),
('P0.B.3',  'R0.U.3', 5),
('P0.B.3',  'R0.U.4', 3),
('P0.B.3',  'R0.B.1', 5),
('P0.B.3',  'R0.B.3', 4);

-- Cambio (P0.B.4)
INSERT INTO vinculo_processo_risco (processo_id, risco_id, materialidade_default) VALUES
('P0.B.4',  'R0.U.2', 5),
('P0.B.4',  'R0.U.4', 4),
('P0.B.4',  'R0.U.6', 4),
('P0.B.4',  'R0.U.8', 3);

-- Pagamentos (P0.B.5)
INSERT INTO vinculo_processo_risco (processo_id, risco_id, materialidade_default) VALUES
('P0.B.5',     'R0.U.4', 5),
('P0.B.5',     'R0.U.5', 5),
('P0.B.5',     'R0.U.6', 4),
('P0.B.5',     'R0.U.8', 4),
('P1.B.5.2',   'R0.U.5', 5),
('P1.B.5.2',   'R0.U.8', 4),
('P1.B.5.6',   'R0.U.13',4),
('P1.B.5.6',   'R0.U.6', 4);

-- TI e Ciber (P0.U.7 e P0.U.8)
INSERT INTO vinculo_processo_risco (processo_id, risco_id, materialidade_default) VALUES
('P0.U.7',  'R0.U.4', 5),
('P0.U.7',  'R0.U.5', 5),
('P0.U.7',  'R0.U.13',4),
('P0.U.8',  'R0.U.5', 5),
('P0.U.8',  'R0.U.4', 4),
('P0.U.8',  'R0.U.13',4);

-- PLD (P0.U.4)
INSERT INTO vinculo_processo_risco (processo_id, risco_id, materialidade_default) VALUES
('P0.U.4',     'R0.U.8', 5),
('P0.U.4',     'R0.U.6', 4),
('P0.U.4',     'R0.U.10',3),
('P1.U.4.1',   'R0.U.8', 5),
('P1.U.4.2',   'R0.U.8', 5),
('P1.U.4.3',   'R0.U.8', 4);

-- LGPD (P0.U.15)
INSERT INTO vinculo_processo_risco (processo_id, risco_id, materialidade_default) VALUES
('P0.U.15',    'R0.U.13',5),
('P0.U.15',    'R0.U.10',3),
('P1.U.15.4',  'R0.U.13',5),
('P1.U.15.4',  'R0.U.5', 4);

-- Distribuicao VM (P0.MC.1)
INSERT INTO vinculo_processo_risco (processo_id, risco_id, materialidade_default) VALUES
('P0.MC.1',    'R0.MC.1',5),
('P0.MC.1',    'R0.MC.2',4),
('P0.MC.1',    'R0.U.7', 5),
('P1.MC.1.1',  'R0.MC.1',5),
('P1.MC.1.3',  'R0.MC.2',5);

-- Asset (P0.MC.2)
INSERT INTO vinculo_processo_risco (processo_id, risco_id, materialidade_default) VALUES
('P0.MC.2',    'R0.MC.3',5),
('P0.MC.2',    'R0.MC.4',5),
('P0.MC.2',    'R0.MC.7',4),
('P0.MC.2',    'R0.U.12',4),
('P1.MC.2.5',  'R0.MC.3',5);

-- Seguros - Subscricao
INSERT INTO vinculo_processo_risco (processo_id, risco_id, materialidade_default) VALUES
('P0.S.1', 'R0.S.1', 5),
('P0.S.1', 'R0.U.4', 3),
('P0.S.1', 'R0.U.7', 4);

-- Seguros - Sinistros
INSERT INTO vinculo_processo_risco (processo_id, risco_id, materialidade_default) VALUES
('P0.S.2', 'R0.S.3', 5),
('P0.S.2', 'R0.U.4', 4),
('P0.S.2', 'R0.S.4', 4);

-- Seguros - Reservas
INSERT INTO vinculo_processo_risco (processo_id, risco_id, materialidade_default) VALUES
('P0.S.3', 'R0.S.2', 5),
('P0.S.3', 'R0.U.12',4),
('P0.S.3', 'R0.S.5', 4);

-- Conglomerado
INSERT INTO vinculo_processo_risco (processo_id, risco_id, materialidade_default) VALUES
('P0.CG.1','R0.CG.2',5),
('P0.CG.1','R0.CG.1',4),
('P0.CG.4','R0.CG.3',5),
('P0.CG.4','R0.CG.4',4),
('P0.CG.4','R0.CG.1',5);

COMMIT;

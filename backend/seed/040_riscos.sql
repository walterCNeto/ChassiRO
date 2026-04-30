-- ============================================================
-- 040_riscos.sql
-- Hierarquia de riscos R0 -> R1
-- ============================================================

BEGIN;

-- ============================================================
-- R0 + R1 UNIVERSAL
-- ============================================================

INSERT INTO riscos (id, codigo, nome, nivel, nucleo, parent_id, categoria_basileia) VALUES
('R0.U.1', 'R0.U.1', 'Risco de Credito',                     0, 'U', NULL, 'credito'),
('R0.U.2', 'R0.U.2', 'Risco de Mercado',                     0, 'U', NULL, 'mercado'),
('R0.U.3', 'R0.U.3', 'Risco de Liquidez',                    0, 'U', NULL, 'liquidez'),
('R0.U.4', 'R0.U.4', 'Risco Operacional',                    0, 'U', NULL, 'operacional'),
('R0.U.5', 'R0.U.5', 'Risco Cibernetico',                    0, 'U', NULL, 'operacional'),
('R0.U.6', 'R0.U.6', 'Risco de Conformidade',                0, 'U', NULL, 'operacional'),
('R0.U.7', 'R0.U.7', 'Risco de Conduta',                     0, 'U', NULL, 'operacional'),
('R0.U.8', 'R0.U.8', 'Risco de PLD-FT',                      0, 'U', NULL, 'operacional'),
('R0.U.9', 'R0.U.9', 'Risco Estrategico',                    0, 'U', NULL, 'estrategico'),
('R0.U.10','R0.U.10','Risco Reputacional',                   0, 'U', NULL, 'reputacional'),
('R0.U.11','R0.U.11','Risco Socioambiental e Climatico',     0, 'U', NULL, 'rsac'),
('R0.U.12','R0.U.12','Risco de Modelo',                      0, 'U', NULL, 'operacional'),
('R0.U.13','R0.U.13','Risco de Privacidade (LGPD)',          0, 'U', NULL, 'operacional');

-- R1 Universal (decomposicoes de R0)
INSERT INTO riscos (id, codigo, nome, nivel, nucleo, parent_id) VALUES
-- Credito
('R1.U.1.1','R1.U.1.1','Inadimplencia (counterparty default)',1,'U','R0.U.1'),
('R1.U.1.2','R1.U.1.2','Migracao de rating',                  1,'U','R0.U.1'),
('R1.U.1.3','R1.U.1.3','Concentracao',                        1,'U','R0.U.1'),
('R1.U.1.4','R1.U.1.4','Recuperacao (LGD)',                   1,'U','R0.U.1'),
('R1.U.1.5','R1.U.1.5','Garantias',                           1,'U','R0.U.1'),
-- Mercado
('R1.U.2.1','R1.U.2.1','Taxa de juros (banking + trading book)',1,'U','R0.U.2'),
('R1.U.2.2','R1.U.2.2','Cambial',                             1,'U','R0.U.2'),
('R1.U.2.3','R1.U.2.3','Acoes',                               1,'U','R0.U.2'),
('R1.U.2.4','R1.U.2.4','Commodities',                         1,'U','R0.U.2'),
('R1.U.2.5','R1.U.2.5','Spread / base',                       1,'U','R0.U.2'),
-- Liquidez
('R1.U.3.1','R1.U.3.1','Funding',                             1,'U','R0.U.3'),
('R1.U.3.2','R1.U.3.2','Liquidez de mercado',                 1,'U','R0.U.3'),
('R1.U.3.3','R1.U.3.3','Intradia',                            1,'U','R0.U.3'),
-- Operacional
('R1.U.4.1','R1.U.4.1','Pessoas (erro humano, fraude interna)',1,'U','R0.U.4'),
('R1.U.4.2','R1.U.4.2','Processos (falha de processo, modelagem)',1,'U','R0.U.4'),
('R1.U.4.3','R1.U.4.3','Sistemas e tecnologia',               1,'U','R0.U.4'),
('R1.U.4.4','R1.U.4.4','Eventos externos (fraude externa, desastres)',1,'U','R0.U.4'),
('R1.U.4.5','R1.U.4.5','Risco legal',                         1,'U','R0.U.4'),
('R1.U.4.6','R1.U.4.6','Terceiros e quarteirizacao',          1,'U','R0.U.4'),
-- Cibernetico
('R1.U.5.1','R1.U.5.1','Indisponibilidade',                   1,'U','R0.U.5'),
('R1.U.5.2','R1.U.5.2','Vazamento e confidencialidade',       1,'U','R0.U.5'),
('R1.U.5.3','R1.U.5.3','Integridade e fraude por intrusao',   1,'U','R0.U.5'),
('R1.U.5.4','R1.U.5.4','Ransomware e extorsao',               1,'U','R0.U.5'),
-- Conformidade
('R1.U.6.1','R1.U.6.1','Nao cumprimento de norma vigente',    1,'U','R0.U.6'),
('R1.U.6.2','R1.U.6.2','Falha em tempestividade de adequacao',1,'U','R0.U.6'),
('R1.U.6.3','R1.U.6.3','Sancao regulatoria',                  1,'U','R0.U.6'),
-- Conduta
('R1.U.7.1','R1.U.7.1','Misselling',                          1,'U','R0.U.7'),
('R1.U.7.2','R1.U.7.2','Praticas comerciais abusivas',        1,'U','R0.U.7'),
('R1.U.7.3','R1.U.7.3','Conflito de interesses',              1,'U','R0.U.7'),
('R1.U.7.4','R1.U.7.4','Manipulacao de mercado / insider',    1,'U','R0.U.7'),
-- PLD-FT
('R1.U.8.1','R1.U.8.1','Lavagem de dinheiro',                 1,'U','R0.U.8'),
('R1.U.8.2','R1.U.8.2','Financiamento ao terrorismo',         1,'U','R0.U.8'),
('R1.U.8.3','R1.U.8.3','Sancoes (listas restritivas)',        1,'U','R0.U.8'),
('R1.U.8.4','R1.U.8.4','Corrupcao e suborno',                 1,'U','R0.U.8'),
-- Estrategico
('R1.U.9.1','R1.U.9.1','Erro de tese ou posicionamento',      1,'U','R0.U.9'),
('R1.U.9.2','R1.U.9.2','Disrupcao competitiva',               1,'U','R0.U.9'),
('R1.U.9.3','R1.U.9.3','Falha de execucao de plano',          1,'U','R0.U.9'),
-- Reputacional
('R1.U.10.1','R1.U.10.1','Incidentes publicos',               1,'U','R0.U.10'),
('R1.U.10.2','R1.U.10.2','Cobertura midiatica negativa',      1,'U','R0.U.10'),
('R1.U.10.3','R1.U.10.3','Crise nas redes sociais',           1,'U','R0.U.10'),
('R1.U.10.4','R1.U.10.4','ESG-washing',                       1,'U','R0.U.10'),
-- RSAC
('R1.U.11.1','R1.U.11.1','Risco fisico (agudo e cronico)',    1,'U','R0.U.11'),
('R1.U.11.2','R1.U.11.2','Risco de transicao',                1,'U','R0.U.11'),
('R1.U.11.3','R1.U.11.3','Risco social (DH, trabalho, comunidades)',1,'U','R0.U.11'),
-- Modelo
('R1.U.12.1','R1.U.12.1','Especificacao inadequada',          1,'U','R0.U.12'),
('R1.U.12.2','R1.U.12.2','Implementacao incorreta',           1,'U','R0.U.12'),
('R1.U.12.3','R1.U.12.3','Uso indevido (model misuse)',       1,'U','R0.U.12'),
('R1.U.12.4','R1.U.12.4','Drift e degradacao',                1,'U','R0.U.12'),
-- Privacidade
('R1.U.13.1','R1.U.13.1','Vazamento de dados pessoais',       1,'U','R0.U.13'),
('R1.U.13.2','R1.U.13.2','Tratamento sem base legal',         1,'U','R0.U.13'),
('R1.U.13.3','R1.U.13.3','Nao atendimento a direitos de titular',1,'U','R0.U.13');

-- ============================================================
-- R0 BANCARIO (especificos)
-- ============================================================

INSERT INTO riscos (id, codigo, nome, nivel, nucleo, parent_id) VALUES
('R0.B.1', 'R0.B.1', 'Risco de descasamento de prazos (gap)', 0, 'B', NULL),
('R0.B.2', 'R0.B.2', 'Risco de pre-pagamento e recompra',     0, 'B', NULL),
('R0.B.3', 'R0.B.3', 'Risco de funding wholesale',            0, 'B', NULL),
('R0.B.4', 'R0.B.4', 'Risco de imagem em corrida bancaria',   0, 'B', NULL);

-- ============================================================
-- R0 MERCADO DE CAPITAIS
-- ============================================================

INSERT INTO riscos (id, codigo, nome, nivel, nucleo, parent_id) VALUES
('R0.MC.1','R0.MC.1','Risco de adequacao (suitability)',           0,'MC',NULL),
('R0.MC.2','R0.MC.2','Risco de execucao (best execution)',         0,'MC',NULL),
('R0.MC.3','R0.MC.3','Risco de marcacao a mercado',                0,'MC',NULL),
('R0.MC.4','R0.MC.4','Risco de segregacao patrimonial',            0,'MC',NULL),
('R0.MC.5','R0.MC.5','Risco de liquidacao (settlement)',           0,'MC',NULL),
('R0.MC.6','R0.MC.6','Risco de chinese wall',                      0,'MC',NULL),
('R0.MC.7','R0.MC.7','Risco de conflito (gestor x distribuidor)',  0,'MC',NULL);

-- ============================================================
-- R0 SEGUROS
-- ============================================================

INSERT INTO riscos (id, codigo, nome, nivel, nucleo, parent_id) VALUES
('R0.S.1','R0.S.1','Risco de subscricao',                          0,'S',NULL),
('R0.S.2','R0.S.2','Risco de provisionamento',                     0,'S',NULL),
('R0.S.3','R0.S.3','Risco de sinistralidade',                      0,'S',NULL),
('R0.S.4','R0.S.4','Risco de catastrofe',                          0,'S',NULL),
('R0.S.5','R0.S.5','Risco de longevidade',                         0,'S',NULL),
('R0.S.6','R0.S.6','Risco de mortalidade',                         0,'S',NULL),
('R0.S.7','R0.S.7','Risco de invalidez/morbidade',                 0,'S',NULL),
('R0.S.8','R0.S.8','Risco de contraparte de resseguro',            0,'S',NULL),
('R0.S.9','R0.S.9','Risco de cancelamento (lapse)',                0,'S',NULL);

-- ============================================================
-- R0 CONGLOMERADO
-- ============================================================

INSERT INTO riscos (id, codigo, nome, nivel, nucleo, parent_id) VALUES
('R0.CG.1','R0.CG.1','Risco de contagio intragrupo',               0,'CG',NULL),
('R0.CG.2','R0.CG.2','Risco de concentracao consolidada',          0,'CG',NULL),
('R0.CG.3','R0.CG.3','Risco de conflito estrutural',               0,'CG',NULL),
('R0.CG.4','R0.CG.4','Risco de arbitragem regulatoria interna',    0,'CG',NULL),
('R0.CG.5','R0.CG.5','Risco de modelo agregado',                   0,'CG',NULL),
('R0.CG.6','R0.CG.6','Risco reputacional cruzado',                 0,'CG',NULL);

COMMIT;

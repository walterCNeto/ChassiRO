-- ============================================================
-- 030_processos.sql
-- Hierarquia de processos P0 -> P2/P3 conforme nucleo
-- ============================================================

BEGIN;

-- ============================================================
-- NUCLEO U - UNIVERSAL (P0 + P1 + P2)
-- ============================================================

-- P0 Universal
INSERT INTO processos (id, codigo, nome, nivel, nucleo, parent_id, descricao) VALUES
('P0.U.1',  'P0.U.1',  'Governanca Corporativa e Estrategia', 0, 'U', NULL, NULL),
('P0.U.2',  'P0.U.2',  'Gestao Integrada de Riscos (GIR)',    0, 'U', NULL, NULL),
('P0.U.3',  'P0.U.3',  'Conformidade e Etica',                 0, 'U', NULL, NULL),
('P0.U.4',  'P0.U.4',  'PLD-FT e Sancoes',                     0, 'U', NULL, NULL),
('P0.U.5',  'P0.U.5',  'Auditoria Interna',                    0, 'U', NULL, NULL),
('P0.U.6',  'P0.U.6',  'Recursos Humanos',                     0, 'U', NULL, NULL),
('P0.U.7',  'P0.U.7',  'Tecnologia da Informacao',             0, 'U', NULL, NULL),
('P0.U.8',  'P0.U.8',  'Seguranca Cibernetica',                0, 'U', NULL, NULL),
('P0.U.9',  'P0.U.9',  'Continuidade de Negocio (BCM)',        0, 'U', NULL, NULL),
('P0.U.10', 'P0.U.10', 'Terceiros e Suprimentos',              0, 'U', NULL, NULL),
('P0.U.11', 'P0.U.11', 'Juridico e Contencioso',               0, 'U', NULL, NULL),
('P0.U.12', 'P0.U.12', 'Financeiro Proprio e Contabilidade',   0, 'U', NULL, NULL),
('P0.U.13', 'P0.U.13', 'Ouvidoria e Atendimento ao Cliente',   0, 'U', NULL, NULL),
('P0.U.14', 'P0.U.14', 'Comunicacao Institucional e Marketing',0, 'U', NULL, NULL),
('P0.U.15', 'P0.U.15', 'Privacidade e Protecao de Dados (LGPD)',0,'U', NULL, NULL);

-- P1 Universal
INSERT INTO processos (id, codigo, nome, nivel, nucleo, parent_id) VALUES
-- P1 Governanca
('P1.U.1.1', 'P1.U.1.1', 'Estrutura de governanca (conselhos, comites, alcadas)', 1, 'U', 'P0.U.1'),
('P1.U.1.2', 'P1.U.1.2', 'Planejamento estrategico',                              1, 'U', 'P0.U.1'),
('P1.U.1.3', 'P1.U.1.3', 'Apetite ao risco (RAS)',                                1, 'U', 'P0.U.1'),
('P1.U.1.4', 'P1.U.1.4', 'Remuneracao e incentivos',                              1, 'U', 'P0.U.1'),
('P1.U.1.5', 'P1.U.1.5', 'Sucessao e desenvolvimento de lideranca',               1, 'U', 'P0.U.1'),
-- P1 GIR
('P1.U.2.1', 'P1.U.2.1', 'Identificacao de riscos',                               1, 'U', 'P0.U.2'),
('P1.U.2.2', 'P1.U.2.2', 'Avaliacao e mensuracao',                                1, 'U', 'P0.U.2'),
('P1.U.2.3', 'P1.U.2.3', 'Mitigacao e tratamento',                                1, 'U', 'P0.U.2'),
('P1.U.2.4', 'P1.U.2.4', 'Monitoramento (KRIs)',                                  1, 'U', 'P0.U.2'),
('P1.U.2.5', 'P1.U.2.5', 'Reporte de riscos',                                     1, 'U', 'P0.U.2'),
('P1.U.2.6', 'P1.U.2.6', 'Plano de Recuperacao e resolucao',                      1, 'U', 'P0.U.2'),
('P1.U.2.7', 'P1.U.2.7', 'ICAAP/ILAAP/ORSA',                                      1, 'U', 'P0.U.2'),
-- P1 Conformidade
('P1.U.3.1', 'P1.U.3.1', 'Mapeamento e monitoramento normativo',                  1, 'U', 'P0.U.3'),
('P1.U.3.2', 'P1.U.3.2', 'Avaliacao de aderencia (compliance reviews)',           1, 'U', 'P0.U.3'),
('P1.U.3.3', 'P1.U.3.3', 'Programa de integridade e etica',                       1, 'U', 'P0.U.3'),
('P1.U.3.4', 'P1.U.3.4', 'Canal de denuncias (whistleblowing)',                   1, 'U', 'P0.U.3'),
('P1.U.3.5', 'P1.U.3.5', 'Conflito de interesses e partes relacionadas',          1, 'U', 'P0.U.3'),
('P1.U.3.6', 'P1.U.3.6', 'Conduta de mercado e prevencao a abusos',               1, 'U', 'P0.U.3'),
-- P1 PLD-FT
('P1.U.4.1', 'P1.U.4.1', 'KYC (conheca seu cliente)',                             1, 'U', 'P0.U.4'),
('P1.U.4.2', 'P1.U.4.2', 'Monitoramento transacional',                            1, 'U', 'P0.U.4'),
('P1.U.4.3', 'P1.U.4.3', 'Comunicacao ao COAF (RIF)',                             1, 'U', 'P0.U.4'),
('P1.U.4.4', 'P1.U.4.4', 'Listas restritivas e sancoes',                          1, 'U', 'P0.U.4'),
('P1.U.4.5', 'P1.U.4.5', 'Avaliacao interna de riscos PLD-FT',                    1, 'U', 'P0.U.4'),
('P1.U.4.6', 'P1.U.4.6', 'Treinamento PLD-FT',                                    1, 'U', 'P0.U.4'),
-- P1 Auditoria Interna
('P1.U.5.1', 'P1.U.5.1', 'Plano anual baseado em riscos',                         1, 'U', 'P0.U.5'),
('P1.U.5.2', 'P1.U.5.2', 'Execucao de trabalhos',                                 1, 'U', 'P0.U.5'),
('P1.U.5.3', 'P1.U.5.3', 'Reporte e follow-up',                                   1, 'U', 'P0.U.5'),
('P1.U.5.4', 'P1.U.5.4', 'Avaliacao de qualidade (interna e externa)',            1, 'U', 'P0.U.5'),
-- P1 RH
('P1.U.6.1', 'P1.U.6.1', 'Recrutamento e selecao',                                1, 'U', 'P0.U.6'),
('P1.U.6.2', 'P1.U.6.2', 'Onboarding e background check',                         1, 'U', 'P0.U.6'),
('P1.U.6.3', 'P1.U.6.3', 'Capacitacao e desenvolvimento',                         1, 'U', 'P0.U.6'),
('P1.U.6.4', 'P1.U.6.4', 'Gestao de desempenho',                                  1, 'U', 'P0.U.6'),
('P1.U.6.5', 'P1.U.6.5', 'Cultura, clima e ESG humano',                           1, 'U', 'P0.U.6'),
('P1.U.6.6', 'P1.U.6.6', 'Folha de pagamento e beneficios',                       1, 'U', 'P0.U.6'),
('P1.U.6.7', 'P1.U.6.7', 'Saude e seguranca ocupacional',                         1, 'U', 'P0.U.6'),
('P1.U.6.8', 'P1.U.6.8', 'Desligamento',                                          1, 'U', 'P0.U.6'),
-- P1 TI
('P1.U.7.1', 'P1.U.7.1', 'Arquitetura e desenvolvimento',                         1, 'U', 'P0.U.7'),
('P1.U.7.2', 'P1.U.7.2', 'Infraestrutura e operacoes',                            1, 'U', 'P0.U.7'),
('P1.U.7.3', 'P1.U.7.3', 'Computacao em nuvem',                                   1, 'U', 'P0.U.7'),
('P1.U.7.4', 'P1.U.7.4', 'Gestao de mudancas',                                    1, 'U', 'P0.U.7'),
('P1.U.7.5', 'P1.U.7.5', 'Gestao de incidentes e problemas',                      1, 'U', 'P0.U.7'),
('P1.U.7.6', 'P1.U.7.6', 'Gestao de identidades e acessos (IAM)',                 1, 'U', 'P0.U.7'),
('P1.U.7.7', 'P1.U.7.7', 'Gestao de dados e qualidade',                           1, 'U', 'P0.U.7'),
('P1.U.7.8', 'P1.U.7.8', 'Inteligencia artificial e modelos',                     1, 'U', 'P0.U.7'),
-- P1 Cibernetica
('P1.U.8.1', 'P1.U.8.1', 'Politica e governanca de ciberseguranca',               1, 'U', 'P0.U.8'),
('P1.U.8.2', 'P1.U.8.2', 'Prevencao (pentests, hardening, SOC)',                  1, 'U', 'P0.U.8'),
('P1.U.8.3', 'P1.U.8.3', 'Deteccao (SIEM, threat intel)',                         1, 'U', 'P0.U.8'),
('P1.U.8.4', 'P1.U.8.4', 'Resposta a incidentes',                                 1, 'U', 'P0.U.8'),
('P1.U.8.5', 'P1.U.8.5', 'Recuperacao de incidentes',                             1, 'U', 'P0.U.8'),
('P1.U.8.6', 'P1.U.8.6', 'Gestao de vulnerabilidades',                            1, 'U', 'P0.U.8'),
-- P1 BCM
('P1.U.9.1', 'P1.U.9.1', 'BIA (analise de impacto nos negocios)',                 1, 'U', 'P0.U.9'),
('P1.U.9.2', 'P1.U.9.2', 'Estrategia de continuidade',                            1, 'U', 'P0.U.9'),
('P1.U.9.3', 'P1.U.9.3', 'Planos (BCP, DRP, plano de crise)',                     1, 'U', 'P0.U.9'),
('P1.U.9.4', 'P1.U.9.4', 'Testes de continuidade',                                1, 'U', 'P0.U.9'),
('P1.U.9.5', 'P1.U.9.5', 'Site alternativo',                                      1, 'U', 'P0.U.9'),
-- P1 Terceiros
('P1.U.10.1','P1.U.10.1','Estrategia de sourcing',                                1, 'U', 'P0.U.10'),
('P1.U.10.2','P1.U.10.2','Due diligence de terceiros',                            1, 'U', 'P0.U.10'),
('P1.U.10.3','P1.U.10.3','Contratacao e SLAs',                                    1, 'U', 'P0.U.10'),
('P1.U.10.4','P1.U.10.4','Monitoramento e gestao de desempenho',                  1, 'U', 'P0.U.10'),
('P1.U.10.5','P1.U.10.5','Riscos de quarteirizacao',                              1, 'U', 'P0.U.10'),
('P1.U.10.6','P1.U.10.6','Encerramento e transicao',                              1, 'U', 'P0.U.10'),
-- P1 Juridico
('P1.U.11.1','P1.U.11.1','Contratos e pareceres',                                 1, 'U', 'P0.U.11'),
('P1.U.11.2','P1.U.11.2','Contencioso civel',                                     1, 'U', 'P0.U.11'),
('P1.U.11.3','P1.U.11.3','Contencioso trabalhista',                               1, 'U', 'P0.U.11'),
('P1.U.11.4','P1.U.11.4','Contencioso fiscal e regulatorio',                      1, 'U', 'P0.U.11'),
('P1.U.11.5','P1.U.11.5','Provisionamento de contingencias',                      1, 'U', 'P0.U.11'),
-- P1 Financeiro/Contabil
('P1.U.12.1','P1.U.12.1','Contabilidade societaria e regulatoria (COSIF/IFRS)',   1, 'U', 'P0.U.12'),
('P1.U.12.2','P1.U.12.2','Controladoria e fechamento',                            1, 'U', 'P0.U.12'),
('P1.U.12.3','P1.U.12.3','Tributario',                                            1, 'U', 'P0.U.12'),
('P1.U.12.4','P1.U.12.4','Reporte regulatorio (DLO, IFR etc.)',                   1, 'U', 'P0.U.12'),
('P1.U.12.5','P1.U.12.5','Demonstracoes financeiras e auditoria externa',         1, 'U', 'P0.U.12'),
-- P1 Ouvidoria
('P1.U.13.1','P1.U.13.1','Canais de atendimento (SAC)',                           1, 'U', 'P0.U.13'),
('P1.U.13.2','P1.U.13.2','Ouvidoria (instancia recursal)',                        1, 'U', 'P0.U.13'),
('P1.U.13.3','P1.U.13.3','Tratamento de reclamacoes de reguladores',              1, 'U', 'P0.U.13'),
('P1.U.13.4','P1.U.13.4','Indicadores de atendimento e satisfacao',               1, 'U', 'P0.U.13'),
-- P1 Comunicacao
('P1.U.14.1','P1.U.14.1','Comunicacao interna',                                   1, 'U', 'P0.U.14'),
('P1.U.14.2','P1.U.14.2','Comunicacao externa e relacoes com a imprensa',         1, 'U', 'P0.U.14'),
('P1.U.14.3','P1.U.14.3','Material publicitario e conformidade',                  1, 'U', 'P0.U.14'),
('P1.U.14.4','P1.U.14.4','Gestao de crise reputacional',                          1, 'U', 'P0.U.14'),
-- P1 LGPD
('P1.U.15.1','P1.U.15.1','Mapeamento de tratamento de dados (RoPA)',              1, 'U', 'P0.U.15'),
('P1.U.15.2','P1.U.15.2','Bases legais e consentimento',                          1, 'U', 'P0.U.15'),
('P1.U.15.3','P1.U.15.3','Direitos dos titulares',                                1, 'U', 'P0.U.15'),
('P1.U.15.4','P1.U.15.4','Gestao de incidentes de privacidade',                   1, 'U', 'P0.U.15'),
('P1.U.15.5','P1.U.15.5','Encarregado (DPO) e relacionamento com ANPD',           1, 'U', 'P0.U.15'),
('P1.U.15.6','P1.U.15.6','Privacy by design',                                     1, 'U', 'P0.U.15');

-- P2 Universal (apenas onde a granularidade adiciona valor analitico)
INSERT INTO processos (id, codigo, nome, nivel, nucleo, parent_id) VALUES
-- P2 Governanca > Estrutura
('P2.U.1.1.1','P2.U.1.1.1','Composicao e funcionamento do Conselho de Administracao', 2,'U','P1.U.1.1'),
('P2.U.1.1.2','P2.U.1.1.2','Comites estatutarios (auditoria, riscos, remuneracao)',   2,'U','P1.U.1.1'),
('P2.U.1.1.3','P2.U.1.1.3','Alcadas e delegacoes',                                    2,'U','P1.U.1.1'),
-- P2 GIR > Avaliacao
('P2.U.2.2.1','P2.U.2.2.1','RCSA (autoavaliacao)',                                    2,'U','P1.U.2.2'),
('P2.U.2.2.2','P2.U.2.2.2','Cenarios e estresse',                                     2,'U','P1.U.2.2'),
('P2.U.2.2.3','P2.U.2.2.3','Quantificacao para capital',                              2,'U','P1.U.2.2'),
-- P2 GIR > Reporte
('P2.U.2.5.1','P2.U.2.5.1','Reporte interno (alta administracao)',                    2,'U','P1.U.2.5'),
('P2.U.2.5.2','P2.U.2.5.2','Reporte regulatorio',                                     2,'U','P1.U.2.5'),
('P2.U.2.5.3','P2.U.2.5.3','Reporte publico (Pilar 3 / equivalente)',                 2,'U','P1.U.2.5'),
-- P2 PLD > KYC
('P2.U.4.1.1','P2.U.4.1.1','Onboarding e due diligence inicial',                      2,'U','P1.U.4.1'),
('P2.U.4.1.2','P2.U.4.1.2','PEP (pessoa exposta politicamente)',                      2,'U','P1.U.4.1'),
('P2.U.4.1.3','P2.U.4.1.3','Revisao periodica e atualizacao cadastral',               2,'U','P1.U.4.1');

-- ============================================================
-- NUCLEO B - BANCARIO (P0 + P1 + P2 selecionados)
-- ============================================================

-- P0 Bancario
INSERT INTO processos (id, codigo, nome, nivel, nucleo, parent_id, descricao) VALUES
('P0.B.1', 'P0.B.1', 'Intermediacao Financeira (Captacao)',           0, 'B', NULL, NULL),
('P0.B.2', 'P0.B.2', 'Intermediacao Financeira (Credito)',            0, 'B', NULL, NULL),
('P0.B.3', 'P0.B.3', 'Tesouraria e Mercados',                         0, 'B', NULL, NULL),
('P0.B.4', 'P0.B.4', 'Cambio e Comercio Exterior',                    0, 'B', NULL, NULL),
('P0.B.5', 'P0.B.5', 'Meios de Pagamento e Liquidacao',               0, 'B', NULL, NULL),
('P0.B.6', 'P0.B.6', 'Custodia e Liquidacao Bancaria',                0, 'B', NULL, NULL),
('P0.B.7', 'P0.B.7', 'Operacoes Estruturadas e Banking de Investimento',0,'B', NULL, NULL);

-- P1 Bancario
INSERT INTO processos (id, codigo, nome, nivel, nucleo, parent_id) VALUES
-- Captacao
('P1.B.1.1', 'P1.B.1.1', 'Captacao de depositos a vista, poupanca e a prazo', 1, 'B', 'P0.B.1'),
('P1.B.1.2', 'P1.B.1.2', 'Emissao de instrumentos (CDB, LCI, LCA, LF, LIG)',  1, 'B', 'P0.B.1'),
('P1.B.1.3', 'P1.B.1.3', 'Operacoes compromissadas (passivas)',               1, 'B', 'P0.B.1'),
('P1.B.1.4', 'P1.B.1.4', 'Captacao no exterior',                              1, 'B', 'P0.B.1'),
-- Credito
('P1.B.2.1', 'P1.B.2.1', 'Originacao',                                        1, 'B', 'P0.B.2'),
('P1.B.2.2', 'P1.B.2.2', 'Analise e decisao',                                 1, 'B', 'P0.B.2'),
('P1.B.2.3', 'P1.B.2.3', 'Acompanhamento e cobranca',                         1, 'B', 'P0.B.2'),
('P1.B.2.4', 'P1.B.2.4', 'Cessao e securitizacao',                            1, 'B', 'P0.B.2'),
('P1.B.2.5', 'P1.B.2.5', 'Garantias',                                         1, 'B', 'P0.B.2'),
('P1.B.2.6', 'P1.B.2.6', 'Provisionamento (IFRS 9 / 4.966)',                  1, 'B', 'P0.B.2'),
-- Tesouraria
('P1.B.3.1', 'P1.B.3.1', 'Gestao de caixa e liquidez intradia',               1, 'B', 'P0.B.3'),
('P1.B.3.2', 'P1.B.3.2', 'Gestao de ativos e passivos (ALM)',                 1, 'B', 'P0.B.3'),
('P1.B.3.3', 'P1.B.3.3', 'Funding plan e estrutura de capital',               1, 'B', 'P0.B.3'),
('P1.B.3.4', 'P1.B.3.4', 'Trading proprietario (banking x trading book)',     1, 'B', 'P0.B.3'),
('P1.B.3.5', 'P1.B.3.5', 'Hedge accounting',                                  1, 'B', 'P0.B.3'),
('P1.B.3.6', 'P1.B.3.6', 'Recolhimento compulsorio',                          1, 'B', 'P0.B.3'),
-- Cambio
('P1.B.4.1', 'P1.B.4.1', 'Cambio comercial',                                  1, 'B', 'P0.B.4'),
('P1.B.4.2', 'P1.B.4.2', 'Cambio financeiro',                                 1, 'B', 'P0.B.4'),
('P1.B.4.3', 'P1.B.4.3', 'Cambio turismo',                                    1, 'B', 'P0.B.4'),
('P1.B.4.4', 'P1.B.4.4', 'ACC/ACE',                                           1, 'B', 'P0.B.4'),
('P1.B.4.5', 'P1.B.4.5', 'Trade finance e cartas de credito',                 1, 'B', 'P0.B.4'),
('P1.B.4.6', 'P1.B.4.6', 'Reporte ao SISBACEN/CCS',                           1, 'B', 'P0.B.4'),
-- Pagamentos
('P1.B.5.1', 'P1.B.5.1', 'TED, DOC e transferencias',                         1, 'B', 'P0.B.5'),
('P1.B.5.2', 'P1.B.5.2', 'PIX (DICT, ICOM, MED)',                             1, 'B', 'P0.B.5'),
('P1.B.5.3', 'P1.B.5.3', 'Boleto bancario',                                   1, 'B', 'P0.B.5'),
('P1.B.5.4', 'P1.B.5.4', 'Cartoes (emissor, credenciador, bandeira)',         1, 'B', 'P0.B.5'),
('P1.B.5.5', 'P1.B.5.5', 'Liquidacao STR e SLB',                              1, 'B', 'P0.B.5'),
('P1.B.5.6', 'P1.B.5.6', 'Open Finance',                                      1, 'B', 'P0.B.5');

-- P2 Bancario seletivos (Originacao, Analise, Cobranca)
INSERT INTO processos (id, codigo, nome, nivel, nucleo, parent_id) VALUES
('P2.B.2.1.1','P2.B.2.1.1','Credito PF (consignado, pessoal, cartao, veicular, imobiliario)', 2,'B','P1.B.2.1'),
('P2.B.2.1.2','P2.B.2.1.2','Credito PJ (capital de giro, investimento)',                       2,'B','P1.B.2.1'),
('P2.B.2.1.3','P2.B.2.1.3','Credito rural e agroindustrial',                                   2,'B','P1.B.2.1'),
('P2.B.2.1.4','P2.B.2.1.4','Credito imobiliario (SFH, SFI)',                                   2,'B','P1.B.2.1'),
('P2.B.2.1.5','P2.B.2.1.5','Credito de fomento e direcionado',                                 2,'B','P1.B.2.1'),
('P2.B.2.2.1','P2.B.2.2.1','Underwriting e modelagem de risco',                                2,'B','P1.B.2.2'),
('P2.B.2.2.2','P2.B.2.2.2','Comites e alcadas',                                                2,'B','P1.B.2.2'),
('P2.B.2.2.3','P2.B.2.2.3','Documentacao e formalizacao',                                      2,'B','P1.B.2.2'),
('P2.B.2.3.1','P2.B.2.3.1','Monitoramento de carteira',                                        2,'B','P1.B.2.3'),
('P2.B.2.3.2','P2.B.2.3.2','Cobranca amigavel',                                                2,'B','P1.B.2.3'),
('P2.B.2.3.3','P2.B.2.3.3','Recuperacao judicial e write-off',                                 2,'B','P1.B.2.3'),
('P2.B.2.3.4','P2.B.2.3.4','Renegociacao e reestruturacao',                                    2,'B','P1.B.2.3');

-- ============================================================
-- NUCLEO MC - MERCADO DE CAPITAIS (P0 + P1)
-- ============================================================

INSERT INTO processos (id, codigo, nome, nivel, nucleo, parent_id) VALUES
('P0.MC.1','P0.MC.1','Distribuicao de Valores Mobiliarios', 0,'MC',NULL),
('P0.MC.2','P0.MC.2','Gestao de Recursos (Asset Management)',0,'MC',NULL),
('P0.MC.3','P0.MC.3','Administracao Fiduciaria',            0,'MC',NULL),
('P0.MC.4','P0.MC.4','Custodia Qualificada',                0,'MC',NULL),
('P0.MC.5','P0.MC.5','Escrituracao',                        0,'MC',NULL),
('P0.MC.6','P0.MC.6','Negociacao por Conta Propria (Trading)',0,'MC',NULL),
('P0.MC.7','P0.MC.7','Pesquisa e Analise',                  0,'MC',NULL),
-- P1 MC
('P1.MC.1.1','P1.MC.1.1','Cadastro e suitability',                          1,'MC','P0.MC.1'),
('P1.MC.1.2','P1.MC.1.2','Recebimento e processamento de ordens',           1,'MC','P0.MC.1'),
('P1.MC.1.3','P1.MC.1.3','Best execution',                                  1,'MC','P0.MC.1'),
('P1.MC.1.4','P1.MC.1.4','Confirmacao e contranota',                        1,'MC','P0.MC.1'),
('P1.MC.1.5','P1.MC.1.5','Distribuicao de ofertas publicas (CVM 160 / 175)',1,'MC','P0.MC.1'),
('P1.MC.2.1','P1.MC.2.1','Constituicao de fundos e veiculos',               1,'MC','P0.MC.2'),
('P1.MC.2.2','P1.MC.2.2','Politica de investimento e enquadramento',        1,'MC','P0.MC.2'),
('P1.MC.2.3','P1.MC.2.3','Decisao de investimento',                         1,'MC','P0.MC.2'),
('P1.MC.2.4','P1.MC.2.4','Risk management de portfolios',                   1,'MC','P0.MC.2'),
('P1.MC.2.5','P1.MC.2.5','Marcacao a mercado',                              1,'MC','P0.MC.2'),
('P1.MC.2.6','P1.MC.2.6','Distribuicao entre cotistas',                     1,'MC','P0.MC.2'),
('P1.MC.3.1','P1.MC.3.1','Constituicao e estruturacao',                     1,'MC','P0.MC.3'),
('P1.MC.3.2','P1.MC.3.2','Controladoria de cotas',                          1,'MC','P0.MC.3'),
('P1.MC.3.3','P1.MC.3.3','Reporte ao cotista',                              1,'MC','P0.MC.3'),
('P1.MC.3.4','P1.MC.3.4','Tesouraria e custodia',                           1,'MC','P0.MC.3'),
('P1.MC.3.5','P1.MC.3.5','Compliance fiduciario',                           1,'MC','P0.MC.3'),
('P1.MC.4.1','P1.MC.4.1','Liquidacao e settlement',                         1,'MC','P0.MC.4'),
('P1.MC.4.2','P1.MC.4.2','Eventos corporativos',                            1,'MC','P0.MC.4'),
('P1.MC.4.3','P1.MC.4.3','Conciliacao',                                     1,'MC','P0.MC.4'),
('P1.MC.4.4','P1.MC.4.4','Segregacao patrimonial',                          1,'MC','P0.MC.4');

-- ============================================================
-- NUCLEO S - SEGUROS (P0 + P1)
-- ============================================================

INSERT INTO processos (id, codigo, nome, nivel, nucleo, parent_id) VALUES
('P0.S.1','P0.S.1','Subscricao',                          0,'S',NULL),
('P0.S.2','P0.S.2','Sinistros',                           0,'S',NULL),
('P0.S.3','P0.S.3','Reservas Tecnicas',                   0,'S',NULL),
('P0.S.4','P0.S.4','Resseguro',                           0,'S',NULL),
('P0.S.5','P0.S.5','Investimento de Reservas',            0,'S',NULL),
('P0.S.6','P0.S.6','Comercializacao e Corretagem',        0,'S',NULL),
('P1.S.1.1','P1.S.1.1','Avaliacao de risco a segurar',    1,'S','P0.S.1'),
('P1.S.1.2','P1.S.1.2','Pricing e tarifa',                1,'S','P0.S.1'),
('P1.S.1.3','P1.S.1.3','Aceitacao e emissao da apolice',  1,'S','P0.S.1'),
('P1.S.1.4','P1.S.1.4','Endossos e renovacoes',           1,'S','P0.S.1'),
('P1.S.2.1','P1.S.2.1','Aviso e abertura',                1,'S','P0.S.2'),
('P1.S.2.2','P1.S.2.2','Regulacao e pericia',             1,'S','P0.S.2'),
('P1.S.2.3','P1.S.2.3','Indenizacao e pagamento',         1,'S','P0.S.2'),
('P1.S.2.4','P1.S.2.4','Sub-rogacao e salvados',          1,'S','P0.S.2'),
('P1.S.2.5','P1.S.2.5','Combate a fraude em sinistros',   1,'S','P0.S.2'),
('P1.S.3.1','P1.S.3.1','PPNG',                            1,'S','P0.S.3'),
('P1.S.3.2','P1.S.3.2','IBNR / IBNeR',                    1,'S','P0.S.3'),
('P1.S.3.3','P1.S.3.3','PSL',                             1,'S','P0.S.3'),
('P1.S.3.4','P1.S.3.4','Outras provisoes tecnicas',       1,'S','P0.S.3'),
('P1.S.3.5','P1.S.3.5','Teste de adequacao de passivos (TAP)',1,'S','P0.S.3'),
('P1.S.4.1','P1.S.4.1','Estrategia de resseguro',         1,'S','P0.S.4'),
('P1.S.4.2','P1.S.4.2','Contratos de resseguro',          1,'S','P0.S.4'),
('P1.S.4.3','P1.S.4.3','Recuperacao de resseguro',        1,'S','P0.S.4'),
('P1.S.4.4','P1.S.4.4','Risco de contraparte de resseguro',1,'S','P0.S.4');

-- ============================================================
-- NUCLEO P - PREVIDENCIA (P0 + P1)
-- ============================================================

INSERT INTO processos (id, codigo, nome, nivel, nucleo, parent_id) VALUES
('P0.P.1','P0.P.1','Acumulacao',              0,'P',NULL),
('P0.P.2','P0.P.2','Concessao de Beneficios', 0,'P',NULL),
('P0.P.3','P0.P.3','Atuaria',                 0,'P',NULL),
('P1.P.1.1','P1.P.1.1','Adesao de participantes',           1,'P','P0.P.1'),
('P1.P.1.2','P1.P.1.2','Recebimento de contribuicoes',      1,'P','P0.P.1'),
('P1.P.1.3','P1.P.1.3','Aplicacao financeira',              1,'P','P0.P.1'),
('P1.P.2.1','P1.P.2.1','Calculo e elegibilidade',           1,'P','P0.P.2'),
('P1.P.2.2','P1.P.2.2','Pagamento de aposentadorias',       1,'P','P0.P.2'),
('P1.P.2.3','P1.P.2.3','Resgates e portabilidade',          1,'P','P0.P.2'),
('P1.P.3.1','P1.P.3.1','Avaliacao atuarial anual',          1,'P','P0.P.3'),
('P1.P.3.2','P1.P.3.2','Hipoteses biometricas e financeiras',1,'P','P0.P.3'),
('P1.P.3.3','P1.P.3.3','Equilibrio tecnico',                1,'P','P0.P.3');

-- ============================================================
-- NUCLEO C - CAPITALIZACAO (P0)
-- ============================================================

INSERT INTO processos (id, codigo, nome, nivel, nucleo, parent_id) VALUES
('P0.C.1','P0.C.1','Subscricao de titulos',  0,'C',NULL),
('P0.C.2','P0.C.2','Sorteios',                0,'C',NULL),
('P0.C.3','P0.C.3','Resgates e devolucoes',   0,'C',NULL);

-- ============================================================
-- NUCLEO CG - CONGLOMERADO (P0 + P1)
-- ============================================================

INSERT INTO processos (id, codigo, nome, nivel, nucleo, parent_id) VALUES
('P0.CG.1','P0.CG.1','GIR Consolidada',                   0,'CG',NULL),
('P0.CG.2','P0.CG.2','ICAAP/ILAAP',                       0,'CG',NULL),
('P0.CG.3','P0.CG.3','Plano de Recuperacao (Res 4.502)',  0,'CG',NULL),
('P0.CG.4','P0.CG.4','Gestao de Operacoes Intragrupo',    0,'CG',NULL),
('P0.CG.5','P0.CG.5','Reporte Regulatorio Consolidado',   0,'CG',NULL),
('P1.CG.1.1','P1.CG.1.1','Consolidacao de exposicoes',           1,'CG','P0.CG.1'),
('P1.CG.1.2','P1.CG.1.2','Risco de concentracao consolidada',    1,'CG','P0.CG.1'),
('P1.CG.1.3','P1.CG.1.3','Reporte de riscos consolidado',        1,'CG','P0.CG.1'),
('P1.CG.2.1','P1.CG.2.1','Avaliacao de adequacao de capital',    1,'CG','P0.CG.2'),
('P1.CG.2.2','P1.CG.2.2','Avaliacao de adequacao de liquidez',   1,'CG','P0.CG.2'),
('P1.CG.2.3','P1.CG.2.3','Cenarios e estresse consolidados',     1,'CG','P0.CG.2'),
('P1.CG.3.1','P1.CG.3.1','Indicadores de gatilho',               1,'CG','P0.CG.3'),
('P1.CG.3.2','P1.CG.3.2','Opcoes de recuperacao',                1,'CG','P0.CG.3'),
('P1.CG.3.3','P1.CG.3.3','Governanca da execucao',               1,'CG','P0.CG.3'),
('P1.CG.4.1','P1.CG.4.1','Politica de partes relacionadas',      1,'CG','P0.CG.4'),
('P1.CG.4.2','P1.CG.4.2','Pricing de transferencia',             1,'CG','P0.CG.4'),
('P1.CG.4.3','P1.CG.4.3','Aprovacao e monitoramento',            1,'CG','P0.CG.4'),
('P1.CG.5.1','P1.CG.5.1','Pilar 3 consolidado',                  1,'CG','P0.CG.5'),
('P1.CG.5.2','P1.CG.5.2','DLO consolidado',                      1,'CG','P0.CG.5'),
('P1.CG.5.3','P1.CG.5.3','DRSAC consolidado',                    1,'CG','P0.CG.5');

COMMIT;

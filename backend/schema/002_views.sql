-- ============================================================
-- Views de análise e consumo
-- Cobrem as 5 lentes definidas: cobertura, densidade, P×R, hierarquia, consumo
-- ============================================================

BEGIN;

-- ------------------------------------------------------------
-- V1. Hierarquia expandida de processos com path legível
-- ------------------------------------------------------------
DROP VIEW IF EXISTS v_processos_hierarquia CASCADE;
CREATE VIEW v_processos_hierarquia AS
WITH RECURSIVE tree AS (
    SELECT
        id, codigo, nome, nivel, nucleo, parent_id,
        codigo::TEXT AS path,
        nome::TEXT AS path_nomes,
        1 AS depth
    FROM processos
    WHERE parent_id IS NULL
    UNION ALL
    SELECT
        p.id, p.codigo, p.nome, p.nivel, p.nucleo, p.parent_id,
        t.path || ' > ' || p.codigo,
        t.path_nomes || ' > ' || p.nome,
        t.depth + 1
    FROM processos p
    JOIN tree t ON p.parent_id = t.id
)
SELECT * FROM tree;

COMMENT ON VIEW v_processos_hierarquia IS
    'Hierarquia expandida com path. Util para drill-down e relatorios.';

-- ------------------------------------------------------------
-- V2. Hierarquia expandida de riscos com path legível
-- ------------------------------------------------------------
DROP VIEW IF EXISTS v_riscos_hierarquia CASCADE;
CREATE VIEW v_riscos_hierarquia AS
WITH RECURSIVE tree AS (
    SELECT
        id, codigo, nome, nivel, nucleo, parent_id,
        codigo::TEXT AS path,
        nome::TEXT AS path_nomes,
        1 AS depth
    FROM riscos
    WHERE parent_id IS NULL
    UNION ALL
    SELECT
        r.id, r.codigo, r.nome, r.nivel, r.nucleo, r.parent_id,
        t.path || ' > ' || r.codigo,
        t.path_nomes || ' > ' || r.nome,
        t.depth + 1
    FROM riscos r
    JOIN tree t ON r.parent_id = t.id
)
SELECT * FROM tree;

-- ------------------------------------------------------------
-- V3. Densidade regulatória por processo
--      Quantas normas tocam cada processo, segmentado por tipo de vínculo
-- ------------------------------------------------------------
DROP VIEW IF EXISTS v_densidade_regulatoria CASCADE;
CREATE VIEW v_densidade_regulatoria AS
SELECT
    p.id AS processo_id,
    p.codigo AS processo_codigo,
    p.nome AS processo_nome,
    p.nivel,
    p.nucleo,
    COUNT(*) FILTER (WHERE v.tipo_vinculo = 'primaria') AS qtd_primarias,
    COUNT(*) FILTER (WHERE v.tipo_vinculo = 'secundaria') AS qtd_secundarias,
    COUNT(*) FILTER (WHERE v.tipo_vinculo = 'informativa') AS qtd_informativas,
    COUNT(*) AS qtd_total
FROM processos p
LEFT JOIN vinculo_norma_processo v ON v.processo_id = p.id
GROUP BY p.id, p.codigo, p.nome, p.nivel, p.nucleo;

COMMENT ON VIEW v_densidade_regulatoria IS
    'Quantas normas tocam cada processo. Lente 2 do framework de analise.';

-- ------------------------------------------------------------
-- V4. Cobertura regulatória — normas órfãs
--      Normas vigentes sem nenhum processo dono
-- ------------------------------------------------------------
DROP VIEW IF EXISTS v_normas_orfas CASCADE;
CREATE VIEW v_normas_orfas AS
SELECT
    n.id, n.tipo, n.numero, n.ano, n.ementa, n.regulador_id
FROM normas n
LEFT JOIN vinculo_norma_processo v ON v.norma_id = n.id
WHERE n.status = 'vigente'
  AND v.id IS NULL;

COMMENT ON VIEW v_normas_orfas IS
    'Normas vigentes sem processo vinculado - gap critico de cobertura.';

-- ------------------------------------------------------------
-- V5. Processos sem norma associada
--      Processos puramente operacionais ou que precisam de mapeamento
-- ------------------------------------------------------------
DROP VIEW IF EXISTS v_processos_sem_norma CASCADE;
CREATE VIEW v_processos_sem_norma AS
SELECT
    p.id, p.codigo, p.nome, p.nivel, p.nucleo
FROM processos p
LEFT JOIN vinculo_norma_processo v ON v.processo_id = p.id
WHERE v.id IS NULL
  AND p.nivel >= 1;  -- ignoramos P0 que naturalmente nao tem vinculo direto

-- ------------------------------------------------------------
-- V6. Matriz processo x risco com materialidade
-- ------------------------------------------------------------
DROP VIEW IF EXISTS v_matriz_processo_risco CASCADE;
CREATE VIEW v_matriz_processo_risco AS
SELECT
    p.codigo AS processo_codigo,
    p.nome AS processo_nome,
    p.nucleo AS processo_nucleo,
    r.codigo AS risco_codigo,
    r.nome AS risco_nome,
    r.nucleo AS risco_nucleo,
    vpr.materialidade_default
FROM vinculo_processo_risco vpr
JOIN processos p ON p.id = vpr.processo_id
JOIN riscos r ON r.id = vpr.risco_id;

-- ------------------------------------------------------------
-- V7. Aplicabilidade resumida da norma
--      Tipos de entidade, segmentos e atividades aos quais a norma se aplica
-- ------------------------------------------------------------
DROP VIEW IF EXISTS v_aplicabilidade_norma CASCADE;
CREATE VIEW v_aplicabilidade_norma AS
SELECT
    n.id AS norma_id,
    n.tipo,
    n.numero,
    n.ano,
    n.regulador_id,
    n.status,
    COALESCE(
        (SELECT array_agg(tipo_entidade_id ORDER BY tipo_entidade_id)
         FROM norma_aplicabilidade_tipo_entidade
         WHERE norma_id = n.id),
        ARRAY[]::TEXT[]
    ) AS tipos_entidade,
    COALESCE(
        (SELECT array_agg(segmento_id ORDER BY segmento_id)
         FROM norma_aplicabilidade_segmento
         WHERE norma_id = n.id),
        ARRAY[]::TEXT[]
    ) AS segmentos,
    COALESCE(
        (SELECT array_agg(atividade_id ORDER BY atividade_id)
         FROM norma_aplicabilidade_atividade
         WHERE norma_id = n.id),
        ARRAY[]::TEXT[]
    ) AS atividades
FROM normas n;

COMMENT ON VIEW v_aplicabilidade_norma IS
    'Visao consolidada de quem deve aplicar cada norma. Vazios significam "sem restricao".';

-- ------------------------------------------------------------
-- V8. Estatísticas globais do chassi
-- ------------------------------------------------------------
DROP VIEW IF EXISTS v_chassi_stats CASCADE;
CREATE VIEW v_chassi_stats AS
SELECT
    (SELECT COUNT(*) FROM reguladores WHERE ativo) AS reguladores_ativos,
    (SELECT COUNT(*) FROM tipos_entidade WHERE ativo) AS tipos_entidade,
    (SELECT COUNT(*) FROM segmentos) AS segmentos,
    (SELECT COUNT(*) FROM atividades_canonicas) AS atividades,
    (SELECT COUNT(*) FROM normas WHERE status = 'vigente') AS normas_vigentes,
    (SELECT COUNT(*) FROM normas) AS normas_total,
    (SELECT COUNT(*) FROM processos) AS processos_total,
    (SELECT COUNT(*) FROM processos WHERE nivel = 0) AS processos_p0,
    (SELECT COUNT(*) FROM riscos) AS riscos_total,
    (SELECT COUNT(*) FROM riscos WHERE nivel = 0) AS riscos_r0,
    (SELECT COUNT(*) FROM vinculo_norma_processo) AS vinculos_norma_processo,
    (SELECT COUNT(*) FROM vinculo_processo_risco) AS vinculos_processo_risco,
    (SELECT version FROM chassi_versions WHERE is_current) AS versao_atual;

COMMIT;

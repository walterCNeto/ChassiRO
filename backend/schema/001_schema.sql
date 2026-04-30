-- ============================================================
-- Chassi de Controles Internos - DDL
-- Postgres 16
-- Compatível com SQLite após adaptação (CHECK em vez de ENUM, sem ltree)
-- ============================================================

BEGIN;

-- Limpeza idempotente (apenas em DEV)
DROP TABLE IF EXISTS api_usage_log CASCADE;
DROP TABLE IF EXISTS api_keys CASCADE;
DROP TABLE IF EXISTS chassi_changelog CASCADE;
DROP TABLE IF EXISTS chassi_versions CASCADE;
DROP TABLE IF EXISTS vinculo_processo_risco CASCADE;
DROP TABLE IF EXISTS vinculo_norma_risco CASCADE;
DROP TABLE IF EXISTS vinculo_norma_processo CASCADE;
DROP TABLE IF EXISTS norma_aplicabilidade_atividade CASCADE;
DROP TABLE IF EXISTS norma_aplicabilidade_segmento CASCADE;
DROP TABLE IF EXISTS norma_aplicabilidade_tipo_entidade CASCADE;
DROP TABLE IF EXISTS norma_artigos CASCADE;
DROP TABLE IF EXISTS normas CASCADE;
DROP TABLE IF EXISTS riscos CASCADE;
DROP TABLE IF EXISTS processos CASCADE;
DROP TABLE IF EXISTS tipo_entidade_regulador CASCADE;
DROP TABLE IF EXISTS atividades_canonicas CASCADE;
DROP TABLE IF EXISTS segmentos CASCADE;
DROP TABLE IF EXISTS tipos_entidade CASCADE;
DROP TABLE IF EXISTS reguladores CASCADE;

-- ============================================================
-- 1. CATÁLOGOS DE DOMÍNIO
-- ============================================================

CREATE TABLE reguladores (
    id              TEXT PRIMARY KEY,
    nome            TEXT NOT NULL,
    natureza        TEXT NOT NULL CHECK (natureza IN
                        ('normativo_superior','normativo_supervisao',
                         'auto_regulador','associativo','uif','autoridade_dados')),
    instrumento     TEXT NOT NULL,
    descricao       TEXT,
    site            TEXT,
    ativo           BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE reguladores IS 'Catálogo de reguladores e auto-reguladores (BCB, CVM, SUSEP etc.)';

CREATE TABLE tipos_entidade (
    id              TEXT PRIMARY KEY,
    nome            TEXT NOT NULL,
    grupo           TEXT NOT NULL CHECK (grupo IN
                        ('bancario','mercado_capitais','seguros',
                         'previdencia','capitalizacao','outros','conglomerado')),
    descricao       TEXT,
    ativo           BOOLEAN NOT NULL DEFAULT TRUE
);

COMMENT ON TABLE tipos_entidade IS 'Tipos canônicos de entidade regulada (banco múltiplo, DTVM, seguradora etc.)';

CREATE TABLE tipo_entidade_regulador (
    tipo_entidade_id    TEXT NOT NULL REFERENCES tipos_entidade(id),
    regulador_id        TEXT NOT NULL REFERENCES reguladores(id),
    papel               TEXT NOT NULL CHECK (papel IN ('primario','secundario')),
    PRIMARY KEY (tipo_entidade_id, regulador_id)
);

COMMENT ON TABLE tipo_entidade_regulador IS 'Quem regula que tipo de entidade, em que papel';

CREATE TABLE segmentos (
    id              TEXT PRIMARY KEY,
    regulador_id    TEXT NOT NULL REFERENCES reguladores(id),
    nome            TEXT NOT NULL,
    descricao       TEXT,
    ordem           INT NOT NULL DEFAULT 0
);

COMMENT ON TABLE segmentos IS 'Segmentações prudenciais (S1-S5 BACEN, equivalentes SUSEP, categorias CVM)';

CREATE TABLE atividades_canonicas (
    id              TEXT PRIMARY KEY,
    nome            TEXT NOT NULL,
    grupo           TEXT NOT NULL,
    descricao       TEXT
);

COMMENT ON TABLE atividades_canonicas IS 'Vocabulário controlado de atividades reguladas (câmbio comercial, PIX, distribuição VM etc.)';

-- ============================================================
-- 2. PROCESSOS (hierarquia P0 -> P4)
-- ============================================================

CREATE TABLE processos (
    id              TEXT PRIMARY KEY,
    codigo          TEXT NOT NULL UNIQUE,
    nome            TEXT NOT NULL,
    nivel           SMALLINT NOT NULL CHECK (nivel BETWEEN 0 AND 4),
    nucleo          TEXT NOT NULL CHECK (nucleo IN ('U','B','MC','S','P','C','CG')),
    parent_id       TEXT REFERENCES processos(id) ON DELETE RESTRICT,
    descricao       TEXT,
    owner_tipico    TEXT,
    -- coerência de hierarquia
    CONSTRAINT chk_processo_root_nivel0
        CHECK ((parent_id IS NULL AND nivel = 0) OR (parent_id IS NOT NULL AND nivel > 0))
);

CREATE INDEX idx_processos_parent ON processos(parent_id);
CREATE INDEX idx_processos_nucleo_nivel ON processos(nucleo, nivel);

COMMENT ON TABLE processos IS 'Hierarquia de processos do chassi. Nivel 0 = macroatividade; nivel 4 = atividade controlavel.';
COMMENT ON COLUMN processos.nucleo IS 'U=universal, B=bancario, MC=mercado capitais, S=seguros, P=previdencia, C=capitalizacao, CG=conglomerado';

-- ============================================================
-- 3. RISCOS (hierarquia R0 -> R4)
-- ============================================================

CREATE TABLE riscos (
    id              TEXT PRIMARY KEY,
    codigo          TEXT NOT NULL UNIQUE,
    nome            TEXT NOT NULL,
    nivel           SMALLINT NOT NULL CHECK (nivel BETWEEN 0 AND 4),
    nucleo          TEXT NOT NULL CHECK (nucleo IN ('U','B','MC','S','P','C','CG')),
    parent_id       TEXT REFERENCES riscos(id) ON DELETE RESTRICT,
    descricao       TEXT,
    categoria_basileia  TEXT,
    CONSTRAINT chk_risco_root_nivel0
        CHECK ((parent_id IS NULL AND nivel = 0) OR (parent_id IS NOT NULL AND nivel > 0))
);

CREATE INDEX idx_riscos_parent ON riscos(parent_id);
CREATE INDEX idx_riscos_nucleo_nivel ON riscos(nucleo, nivel);

COMMENT ON TABLE riscos IS 'Hierarquia de riscos do chassi. Nivel 0 = categoria macro; nivel 4 = causa-raiz controlavel.';

-- ============================================================
-- 4. NORMAS (catálogo regulatório)
-- ============================================================

CREATE TABLE normas (
    id                  TEXT PRIMARY KEY,
    tipo                TEXT NOT NULL CHECK (tipo IN
                            ('lei','lei_complementar','decreto','decreto_lei',
                             'res_cmn','res_bcb','circ_bcb','carta_circ_bcb','instr_bcb',
                             'res_cvm','instr_cvm',
                             'res_cnsp','circ_susep',
                             'res_cnpc','instr_previc',
                             'res_coaf','res_anpd',
                             'codigo_anbima','oficio_b3','oficio_bsm',
                             'outros')),
    numero              TEXT NOT NULL,
    ano                 INT,
    regulador_id        TEXT NOT NULL REFERENCES reguladores(id),
    titulo              TEXT,
    ementa              TEXT NOT NULL,
    status              TEXT NOT NULL CHECK (status IN
                            ('vigente','revogada','parcialmente_revogada',
                             'em_consulta','revogada_tacita')),
    vigencia_inicio     DATE,
    vigencia_fim        DATE,
    norma_mae_id        TEXT REFERENCES normas(id) ON DELETE SET NULL,
    url_oficial         TEXT,
    fonte_consulta      TEXT,
    notas               TEXT,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_normas_regulador ON normas(regulador_id);
CREATE INDEX idx_normas_tipo ON normas(tipo);
CREATE INDEX idx_normas_status ON normas(status);
CREATE INDEX idx_normas_norma_mae ON normas(norma_mae_id);

COMMENT ON TABLE normas IS 'Catálogo central de normas. Status reflete vigência atual.';

CREATE TABLE norma_artigos (
    id              BIGSERIAL PRIMARY KEY,
    norma_id        TEXT NOT NULL REFERENCES normas(id) ON DELETE CASCADE,
    numero          TEXT NOT NULL,
    secao           TEXT,
    tema            TEXT,
    descricao       TEXT
);

CREATE INDEX idx_norma_artigos_norma ON norma_artigos(norma_id);
CREATE UNIQUE INDEX idx_norma_artigos_unique
    ON norma_artigos(norma_id, numero, COALESCE(secao, ''));

COMMENT ON TABLE norma_artigos IS 'Artigos relevantes das normas estruturantes (granularidade fina opcional).';

-- ============================================================
-- 5. APLICABILIDADE DA NORMA (tabelas N:N)
-- ============================================================

CREATE TABLE norma_aplicabilidade_tipo_entidade (
    norma_id        TEXT NOT NULL REFERENCES normas(id) ON DELETE CASCADE,
    tipo_entidade_id TEXT NOT NULL REFERENCES tipos_entidade(id),
    PRIMARY KEY (norma_id, tipo_entidade_id)
);

CREATE TABLE norma_aplicabilidade_segmento (
    norma_id        TEXT NOT NULL REFERENCES normas(id) ON DELETE CASCADE,
    segmento_id     TEXT NOT NULL REFERENCES segmentos(id),
    PRIMARY KEY (norma_id, segmento_id)
);

CREATE TABLE norma_aplicabilidade_atividade (
    norma_id        TEXT NOT NULL REFERENCES normas(id) ON DELETE CASCADE,
    atividade_id    TEXT NOT NULL REFERENCES atividades_canonicas(id),
    PRIMARY KEY (norma_id, atividade_id)
);

COMMENT ON TABLE norma_aplicabilidade_tipo_entidade IS
    'Lista de tipos de entidade aos quais a norma se aplica. Vazio = aplica a todos os tipos compatíveis com o regulador.';
COMMENT ON TABLE norma_aplicabilidade_segmento IS
    'Lista de segmentos prudenciais aos quais a norma se aplica. Vazio = sem restrição de segmento.';
COMMENT ON TABLE norma_aplicabilidade_atividade IS
    'Lista de atividades canônicas requeridas para a norma se aplicar. Vazio = sem restrição de atividade.';

-- ============================================================
-- 6. VÍNCULOS (o coração analítico do chassi)
-- ============================================================

CREATE TABLE vinculo_norma_processo (
    id              BIGSERIAL PRIMARY KEY,
    norma_id        TEXT NOT NULL REFERENCES normas(id) ON DELETE CASCADE,
    processo_id     TEXT NOT NULL REFERENCES processos(id) ON DELETE CASCADE,
    artigo_ref      TEXT,
    tipo_vinculo    TEXT NOT NULL CHECK (tipo_vinculo IN
                        ('primaria','secundaria','informativa')),
    notas           TEXT
);

CREATE INDEX idx_vnp_norma ON vinculo_norma_processo(norma_id);
CREATE INDEX idx_vnp_processo ON vinculo_norma_processo(processo_id);
CREATE INDEX idx_vnp_tipo ON vinculo_norma_processo(tipo_vinculo);
CREATE UNIQUE INDEX idx_vnp_unique
    ON vinculo_norma_processo(norma_id, processo_id, COALESCE(artigo_ref, ''));

COMMENT ON TABLE vinculo_norma_processo IS
    'Vínculo norma-processo qualificado por tipo. Primária: o processo é DONO do cumprimento. Secundária: contribui. Informativa: princípios apenas.';

CREATE TABLE vinculo_norma_risco (
    id              BIGSERIAL PRIMARY KEY,
    norma_id        TEXT NOT NULL REFERENCES normas(id) ON DELETE CASCADE,
    risco_id        TEXT NOT NULL REFERENCES riscos(id) ON DELETE CASCADE,
    tipo_vinculo    TEXT NOT NULL CHECK (tipo_vinculo IN
                        ('primaria','secundaria','informativa')),
    notas           TEXT,
    UNIQUE (norma_id, risco_id)
);

CREATE INDEX idx_vnr_norma ON vinculo_norma_risco(norma_id);
CREATE INDEX idx_vnr_risco ON vinculo_norma_risco(risco_id);

COMMENT ON TABLE vinculo_norma_risco IS
    'Norma associada à categoria/causa de risco que ela endereça.';

CREATE TABLE vinculo_processo_risco (
    id                  BIGSERIAL PRIMARY KEY,
    processo_id         TEXT NOT NULL REFERENCES processos(id) ON DELETE CASCADE,
    risco_id            TEXT NOT NULL REFERENCES riscos(id) ON DELETE CASCADE,
    materialidade_default SMALLINT NOT NULL DEFAULT 3
        CHECK (materialidade_default BETWEEN 1 AND 5),
    notas               TEXT,
    UNIQUE (processo_id, risco_id)
);

CREATE INDEX idx_vpr_processo ON vinculo_processo_risco(processo_id);
CREATE INDEX idx_vpr_risco ON vinculo_processo_risco(risco_id);

COMMENT ON TABLE vinculo_processo_risco IS
    'Matriz P x R com materialidade default sugerida (1-5). Cliente pode override em sua instância.';

-- ============================================================
-- 7. VERSIONAMENTO E CHANGELOG
-- ============================================================

CREATE TABLE chassi_versions (
    id              TEXT PRIMARY KEY,
    version         TEXT NOT NULL UNIQUE,
    released_at     TIMESTAMPTZ NOT NULL,
    notas           TEXT,
    is_current      BOOLEAN NOT NULL DEFAULT FALSE
);

COMMENT ON TABLE chassi_versions IS 'Versionamento semântico do chassi como produto. is_current=TRUE em apenas 1 linha.';

CREATE UNIQUE INDEX idx_chassi_versions_current
    ON chassi_versions(is_current) WHERE is_current = TRUE;

CREATE TABLE chassi_changelog (
    id              BIGSERIAL PRIMARY KEY,
    version_id      TEXT NOT NULL REFERENCES chassi_versions(id),
    change_type     TEXT NOT NULL CHECK (change_type IN
                        ('add','remove','modify','deprecate')),
    entity_type     TEXT NOT NULL,
    entity_id       TEXT NOT NULL,
    description     TEXT NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_chassi_changelog_version ON chassi_changelog(version_id);

-- ============================================================
-- 8. API SURFACE (somente operacional - sem dado de cliente)
-- ============================================================

CREATE TABLE api_keys (
    id              BIGSERIAL PRIMARY KEY,
    key_hash        TEXT NOT NULL UNIQUE,
    nome            TEXT NOT NULL,
    tier            TEXT NOT NULL CHECK (tier IN ('free','pro','enterprise')),
    rate_limit_per_minute INT NOT NULL DEFAULT 60,
    ativo           BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at      TIMESTAMPTZ
);

COMMENT ON TABLE api_keys IS 'Chaves de API. Armazena apenas hash, nunca a chave em claro.';

CREATE TABLE api_usage_log (
    id              BIGSERIAL PRIMARY KEY,
    api_key_id      BIGINT REFERENCES api_keys(id),
    endpoint        TEXT NOT NULL,
    status_code     INT NOT NULL,
    latency_ms      INT,
    ts              TIMESTAMPTZ NOT NULL DEFAULT NOW()
    -- INTENCIONAL: nao logamos parametros de query.
    -- Cliente passa atributos da entidade dele e nao queremos coletar essa inteligencia.
);

CREATE INDEX idx_api_usage_log_ts ON api_usage_log(ts);
CREATE INDEX idx_api_usage_log_key ON api_usage_log(api_key_id);

COMMENT ON TABLE api_usage_log IS
    'Telemetria operacional. NAO loga payload da query - mantem o produto whitelabel/passivo.';

COMMIT;

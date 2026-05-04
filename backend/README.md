# Chassi de Controles Internos — Backend

Catálogo regulatório versionado e colaborativo para o sistema de controles
internos das instituições financeiras brasileiras. Mapeia normas, processos,
riscos e seus vínculos qualificados em um único modelo de dados.

> API leve e idempotente. O consumidor passa atributos categóricos da
> entidade dele (tipo, segmento, atividades) e recebe a fatia aplicável.

## O que tem aqui

```
backend/
├── schema/
│   ├── 001_schema.sql      DDL completo (Postgres 16)
│   └── 002_views.sql       Views analiticas
├── seed/
│   ├── 010_catalogos.sql   Reguladores, tipos de entidade, segmentos, atividades
│   ├── 020_normas.sql      ~30 normas estruturantes + aplicabilidade
│   ├── 030_processos.sql   Hierarquia P0-P2 (universal e bancario completos)
│   ├── 040_riscos.sql      Hierarquia R0-R1 (universal completa)
│   ├── 050_vinculos.sql    Vinculos norma-processo, norma-risco, processo-risco
│   └── 099_versao.sql      Metadata da versao do chassi
├── export/
│   ├── export.py           CLI Python: to-json, to-sqlite, stats
│   └── requirements.txt
├── docker-compose.yml      Postgres com schema+seeds auto-carregados
├── Makefile                Atalhos de uso
└── .env.example            Variaveis de conexao
```

## Quickstart

```bash
# 1. Subir o Postgres com schema e seeds carregados
make up

# 2. Ver estatisticas do chassi
make stats

# 3. Instalar deps Python e exportar
make install
make export-all
```

Vai gerar `chassi.json` e `chassi.sqlite` no root do projeto.

## Modelo de dados

```
reguladores                 catalogo de orgaos (BCB, CVM, SUSEP, ANBIMA...)
tipos_entidade              25 tipos canonicos (banco multiplo, DTVM, seguradora...)
tipo_entidade_regulador     N:N com papel (primario / secundario)
segmentos                   S1-S5 BCB e equivalentes SUSEP
atividades_canonicas        vocabulario controlado (cambio, PIX, distribuicao VM...)

processos                   hierarquia P0->P4, parent_id, com nucleo (U, B, MC, S, P, C, CG)
riscos                      hierarquia R0->R4, parent_id, com nucleo
normas                      catalogo central com tipo, status, vigencia
norma_artigos               granularidade fina opcional
norma_aplicabilidade_*      3 tabelas N:N - tipos de entidade, segmentos, atividades

vinculo_norma_processo      tipo_vinculo: primaria | secundaria | informativa
vinculo_norma_risco         categoria/causa de risco enderecada
vinculo_processo_risco      matriz P x R com materialidade default 1-5

chassi_versions             versionamento semantico (is_current = TRUE em apenas 1)
chassi_changelog            log de adicoes/remocoes/modificacoes

api_keys                    operacional - hash apenas
api_usage_log               operacional - sem payload
```

### Hierarquia paralela P x R

Decisao chave: processos e riscos seguem hierarquias paralelas. Controles
alocam no nivel mais granular do risco (R3/R4) e agregam para cima. Mesma
logica para processos. P3/P4 sao opcionais por instancia - sao ativados
quando o processo e critico ou regulado em detalhe.

### Vinculo qualificado

Vinculos norma-processo nao sao binarios. Tres niveis:

- **primaria** - o processo e DONO do cumprimento da norma
- **secundaria** - contribui mas nao e o dono
- **informativa** - principios apenas (norma estruturante de ordem superior)

Isso permite distinguir cobertura efetiva (so primaria) de cobertura
nominal (qualquer vinculo).

### Tres camadas de federacao

- **Nucleo Conglomerado (CG)** - riscos so existem no nivel agregado: contagio intragrupo, concentracao consolidada, conflito estrutural, arbitragem regulatoria interna
- **Nucleos Setoriais (B, MC, S, P, C)** - bancario, mercado de capitais, seguros, previdencia, capitalizacao
- **Nucleo Universal (U)** - processos e riscos comuns a qualquer entidade regulada

## Aplicacoes suportadas

O chassi serve as varias aplicacoes do sistema de controles internos:

- **Mapeamento de processos e controles** - base de processos hierarquizada
- **RCSA** (autoavaliacao de riscos e controles, art. 38 da Res 4.557)
- **Gap analysis** regulatorio por entidade e segmento
- **Plano de monitoramento de controles**
- **Reporte regulatorio** estruturado

## Views analiticas (cinco lentes)

```sql
-- 1. Cobertura regulatoria - normas vigentes sem processo dono
SELECT * FROM v_normas_orfas;

-- 2. Densidade regulatoria - processos mais regulados
SELECT * FROM v_densidade_regulatoria
ORDER BY qtd_total DESC LIMIT 10;

-- 3. Matriz P x R com materialidade
SELECT * FROM v_matriz_processo_risco
WHERE materialidade_default >= 4;

-- 4. Hierarquia expandida com path
SELECT path, path_nomes FROM v_processos_hierarquia
WHERE nucleo = 'B';

-- 5. Aplicabilidade consolidada de uma norma
SELECT * FROM v_aplicabilidade_norma WHERE norma_id = 'RES_CMN_4557_17';

-- Estatisticas globais
SELECT * FROM v_chassi_stats;
```

## Modalidades de consumo

### 1. Snapshot baixavel

```bash
make export-json     # gera chassi.json (~500KB-2MB)
make export-sqlite   # gera chassi.sqlite (autocontido)
```

O cliente baixa, importa para o ambiente dele e roda offline.

### 2. API REST (proxima iteracao)

Endpoints idempotentes:
```
GET /v1/normas?aplica_a=BANCO_MULTIPLO&segmento=S2&atividade=cambio_comercial
GET /v1/processos?nucleo=B&nivel_max=2
GET /v1/instancia    # passa o cartao da entidade, recebe a fatia ativa
```

### 3. SDK / biblioteca (npm/pip - futuro)

Pacote que embute o snapshot e a engine de filtragem.

## Como filtrar a fatia aplicavel a uma instituicao

Pseudocodigo:

```python
# Atributos da instituicao (passados na consulta - nao armazenados)
entity = {
    "tipo_entidade": "ENT_BANCO_MULTIPLO",
    "segmento": "S2",
    "atividades": ["ATV_DEPOSITO_VISTA", "ATV_CREDITO_PJ", "ATV_CAMBIO_COMERCIAL"]
}

# Filtra normas aplicaveis
SELECT n.*
FROM normas n
WHERE n.status = 'vigente'
  AND (
    -- Sem restricao de tipo OU tipo do consumidor esta na lista
    NOT EXISTS (SELECT 1 FROM norma_aplicabilidade_tipo_entidade WHERE norma_id = n.id)
    OR EXISTS (SELECT 1 FROM norma_aplicabilidade_tipo_entidade
               WHERE norma_id = n.id AND tipo_entidade_id = :tipo_entidade)
  )
  AND (
    NOT EXISTS (SELECT 1 FROM norma_aplicabilidade_segmento WHERE norma_id = n.id)
    OR EXISTS (SELECT 1 FROM norma_aplicabilidade_segmento
               WHERE norma_id = n.id AND segmento_id = :segmento)
  )
  AND (
    NOT EXISTS (SELECT 1 FROM norma_aplicabilidade_atividade WHERE norma_id = n.id)
    OR EXISTS (SELECT 1 FROM norma_aplicabilidade_atividade
               WHERE norma_id = n.id AND atividade_id = ANY(:atividades))
  );
```

A logica e: **vazio = sem restricao**. Se uma norma nao tem nenhum tipo de
entidade listado, ela aplica a qualquer tipo compativel com o regulador.
Se tem lista, aplica somente a quem esta na lista.

## Adicionando normas, processos ou vinculos

Edite o seed correspondente, depois:

```bash
make reset      # recarrega tudo
make stats      # confere
make export-all # regenera snapshot
```

Ao adicionar uma norma:
1. INSERT em `normas`
2. (opcional) INSERT em `norma_artigos`
3. INSERT em `norma_aplicabilidade_*` para definir quem deve aplicar
4. INSERT em `vinculo_norma_processo` com tipo_vinculo
5. INSERT em `vinculo_norma_risco` com tipo_vinculo

Veja o [guia de contribuicao](../CONTRIBUTING.md) para o passo a passo de
um Pull Request.

## Limitacoes conhecidas (v0.1.0)

- Numeros, datas e status das normas seedadas precisam ser **revalidados
  contra a base oficial dos reguladores** antes de uso operacional. O seed
  usa marcos publicos mas nao foi auditado linha a linha.
- P3/P4 detalhados ainda nao estao seedados - apenas P0+P1, com P2 seletivos.
- R2/R3/R4 ainda nao estao seedados.
- Cobertura de cartas-circulares e oficios da B3/BSM e parcial.
- Sem biblioteca de KRIs nem de controles-modelo (pretendido para v0.2).

## Filosofia

> O valor esta no **catalogo curado e versionado**, nao no codigo.
> O codigo e simples - publico, sob MIT. O que e dificil de reproduzir
> sozinho e a curadoria regulatoria continua - e por isso a curadoria
> e colaborativa.

Por isso a API e leve e nao recebe dado da instituicao. Toda inteligencia
esta no chassi; o cliente passa atributos e recebe filtragem. Isso e o que
permite tres modalidades de consumo (API, snapshot, SDK) compartilharem o
mesmo nucleo logico.
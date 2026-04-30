# Chassi de Controles Internos — API

API REST sobre o catálogo regulatório do Chassi. Carrega `chassi.json` em
memória no startup; sem dependência de banco de dados em runtime.

## Endpoints

```
GET  /                           Info do projeto
GET  /health                     Health check + contagens
GET  /docs                       Swagger UI interativo
GET  /redoc                      Redoc

GET  /v1/reguladores             Lista reguladores
GET  /v1/reguladores/{id}        Detalhe
GET  /v1/tipos-entidade          Lista (filtro: ?grupo=)
GET  /v1/tipos-entidade/{id}     Detalhe
GET  /v1/segmentos               Lista (filtro: ?regulador=)
GET  /v1/atividades              Lista (filtro: ?grupo=)

GET  /v1/normas                  Lista (filtros: ?aplica_a=, ?segmento=,
                                  ?atividade=, ?regulador=, ?status=,
                                  ?tipo=, ?busca=)
GET  /v1/normas/{id}             Detalhe completo (artigos, aplicabilidade,
                                  vinculos com processos e riscos)

GET  /v1/processos               Lista (?nucleo=, ?nivel_max=, ?parent=)
GET  /v1/processos/{id}          Detalhe (children, vinculos)

GET  /v1/riscos                  Lista (?nucleo=, ?nivel_max=, ?parent=,
                                  ?categoria=)
GET  /v1/riscos/{id}             Detalhe (children, vinculos)

GET  /v1/vinculos/norma-processo (?norma=, ?processo=, ?tipo=)
GET  /v1/vinculos/norma-risco    (?norma=, ?risco=, ?tipo=)
GET  /v1/vinculos/processo-risco (?processo=, ?risco=, ?materialidade_min=)

POST /v1/instancia               Filtragem combinada por entidade
                                  (body: {tipo_entidade, segmento?, atividades[]})

GET  /v1/chassi/version          Versao atual
GET  /v1/chassi/versions         Historico
GET  /v1/chassi/stats            Estatisticas globais
GET  /v1/chassi/snapshot.json    Download do snapshot completo
```

## Rodar localmente

Pré-requisitos: Python 3.11+, snapshot `chassi.json` gerado.

```bash
# 1. Gere o snapshot (uma vez)
cd backend
make export-json
cp chassi.json ../api/  # ou setar CHASSI_SNAPSHOT_PATH

# 2. Instale deps
cd ../api
pip install -r requirements.txt

# 3. Rode
cd ..
uvicorn api.main:app --reload --port 8000
```

Abre `http://localhost:8000/docs` no navegador para o Swagger UI.

### Testes rápidos

```bash
# Health
curl http://localhost:8000/health

# Stats
curl http://localhost:8000/v1/chassi/stats | jq

# Normas aplicaveis a um banco multiplo S2
curl 'http://localhost:8000/v1/normas?aplica_a=ENT_BANCO_MULTIPLO&segmento=S2' | jq 'length'

# Detalhe de uma norma
curl http://localhost:8000/v1/normas/RES_CMN_4557_17 | jq

# Filtragem combinada (instancia)
curl -X POST http://localhost:8000/v1/instancia \
  -H 'Content-Type: application/json' \
  -d '{
    "tipo_entidade": "ENT_BANCO_MULTIPLO",
    "segmento": "S2",
    "atividades": ["ATV_DEPOSITO_VISTA", "ATV_CAMBIO_COMERCIAL"]
  }' | jq '.contagens'
```

## Deploy no Fly.io

Pré-requisitos:

- Conta em https://fly.io (free tier disponível)
- `flyctl` instalado: https://fly.io/docs/hands-on/install-flyctl/

```bash
# Login (uma vez)
flyctl auth login

# Gera o snapshot mais recente em backend/chassi.json
cd backend
make export-json
cd ..

# Deploy (do raiz do repo, onde está o Dockerfile e fly.toml)
flyctl launch --no-deploy --copy-config   # primeira vez apenas
# (escolha um nome único; responda "no" para Postgres e Redis)

flyctl deploy
```

A API fica em `https://<nome-do-app>.fly.dev`.

### Atualizando o catálogo

Quando o conteúdo do catálogo mudar (PR aceito), regenera o snapshot e faz
um novo deploy:

```bash
cd backend
make export-json
cd ..
flyctl deploy
```

## Arquitetura

```
┌──────────────────────────┐
│  backend/ (Postgres)     │  ← edição do catálogo (PRs)
│  schema + seeds          │
└────────────┬─────────────┘
             │ make export-json
             ▼
   ┌─────────────────────┐
   │   chassi.json       │  ← artefato versionado por release
   │   (~180 KB)         │
   └─────────┬───────────┘
             │ COPY no Dockerfile
             ▼
   ┌─────────────────────┐
   │  api/ (FastAPI)     │  ← carrega em memória no startup
   │  read-only          │     responde em < 5ms
   └─────────────────────┘
             │ flyctl deploy
             ▼
   https://chassiro-api.fly.dev
```

O snapshot é construído offline, em ambiente de autoria com Postgres. A API
em produção apenas serve o JSON estático. Isso permite hospedar de graça
(o app dorme entre requisições) e tem latência muito baixa.

## Variáveis de ambiente

- `CHASSI_SNAPSHOT_PATH` — caminho explícito para o `chassi.json`.
  Se não definida, busca em `./chassi.json`, `../backend/chassi.json`, `/app/chassi.json`.
- `PORT` — porta de escuta (default 8000)

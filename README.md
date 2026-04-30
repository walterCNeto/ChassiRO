# Chassi de Controles Internos

> Catálogo regulatório versionado para o sistema de controles internos das instituições financeiras brasileiras.

[![Status](https://img.shields.io/badge/status-alpha-9c2c25?style=flat-square)](https://github.com/walterCNeto/ChassiRO)
[![Version](https://img.shields.io/badge/version-0.1.0-1a1814?style=flat-square)](./CHANGELOG.md)
[![OpenAPI](https://img.shields.io/badge/OpenAPI-3.1-1a1814?style=flat-square)](./web/openapi.yaml)
[![License](https://img.shields.io/badge/license-proprietary-3d3a35?style=flat-square)](#licença)

Mapeia normas, processos, riscos e seus vínculos qualificados em um único modelo
de dados — a base do sistema de controles internos exigido pela Res CMN 4.943
e correlatas. Reguladores cobertos: **CMN · BCB · CVM · CNSP · SUSEP · PREVIC ·
COAF · ANPD · ANBIMA · B3 · BSM**.

API whitelabel passiva — o consumidor passa atributos categóricos da entidade
dele (tipo, segmento, atividades) e recebe a fatia aplicável. **Nenhum dado de
cliente é armazenado.**

## Para quem

Audiência primária: **bancos múltiplos, comerciais, de investimento e
instituições do conglomerado prudencial**. O catálogo cobre, naturalmente, as
atividades adjacentes que bancos exercem — distribuição de valores
mobiliários (CVM), corretora coligada, asset management, e os reguladores que
incidem sobre essas atividades.

## Como o chassi se encaixa na operação do banco

```
              ┌──────────────────────────────────────────────┐
              │          Novas normas (CMN, BCB,             │
              │          CVM, SUSEP, ANBIMA…)                │
              └────────────────────┬─────────────────────────┘
                                   │ entrada contínua
                                   ▼
   ┌─────────┐  ┌─────────┐  ┌──────────────────┐  ┌──────────┐
   │  RCSA   │  │   BIA   │  │    Auditoria     │  │  Custos  │
   └────┬────┘  └────┬────┘  └────────┬─────────┘  └────┬─────┘
        │            │                │                 │
        │   sistemas-satélites do banco já existentes   │
        │            │                │                 │
        ▼            ▼                ▼                 ▼
   ╔══════════════════════════════════════════════════════════╗
   ║                                                          ║
   ║                  Camada de IA (tradução)                 ║
   ║       fontes heterogêneas → vocabulário do chassi        ║
   ║                                                          ║
   ╠══════════════════════════════════════════════════════════╣
   ║                                                          ║
   ║              ⬛ Chassi Geral (CG) ⬛                      ║
   ║                                                          ║
   ║              normas × processos × riscos                 ║
   ║              hierarquias N0→N4 / R0→R4                   ║
   ║                                                          ║
   ║                d(CG)                                     ║
   ║               ─────── ≈ 0       (núcleo estável)         ║
   ║                 dt                                       ║
   ║                                                          ║
   ╚══════════════════════════════════════════════════════════╝
                                   │
                                   ▼
              ┌──────────────────────────────────────────────┐
              │  Indicadores · Apontamentos · Cobertura      │
              │  → Ambiente de controles coerente            │
              └──────────────────────────────────────────────┘
```

O chassi é o **núcleo estável** — o catálogo regulatório varia muito pouco
no tempo, daí a anotação `d(CG)/dt ≈ 0`. Em volta dele, cada banco já tem
seus próprios sistemas: RCSA em planilha ou ferramenta proprietária, BIA na
área de continuidade, sistemas de RH (PeopleSoft e congêneres), sistema de
custos, plano de auditoria, áreas de resultado.

Hoje, esses sistemas falam vocabulários diferentes — cada um inventou o
próprio mapa de processos e a própria taxonomia de riscos. **O chassi é o
esqueleto comum** que orquestra todos eles, e uma camada de IA atua como
tradutor: pega a entrada heterogênea (uma matriz de RCSA exportada do
PeopleSoft, uma planilha de BIA, um plano de auditoria) e a encaixa no
vocabulário canônico de processos e riscos do chassi.

O resultado é um **ambiente de controles coerente** com indicadores
agregáveis, apontamentos rastreáveis até a norma de origem, e cobertura
mensurável (cobertura nominal × cobertura efetiva, via vínculos
qualificados).

## O que sustenta

O chassi serve as várias aplicações do sistema de controles internos:

- **Mapeamento de processos e controles** — base de processos hierarquizada
- **RCSA** (autoavaliação de riscos e controles, art. 38 da Res 4.557)
- **BIA** (análise de impacto nos negócios, Res 4.557 art. 50)
- **Plano de auditoria interna** baseado em risco
- **Gap analysis** regulatório por entidade e segmento
- **Plano de monitoramento de controles**
- **Reporte regulatório** estruturado

## Estrutura do repositório

```
ChassiRO/
├── backend/          Schema Postgres + seeds + export Python
│   ├── schema/       DDL e views
│   ├── seed/         Catálogos, normas, processos, riscos, vínculos
│   ├── export/       CLI Python (to-json, to-sqlite, stats)
│   └── docker-compose.yml
│
└── web/              Landing institucional + docs OpenAPI
    ├── index.html    Landing comercial
    ├── docs.html     Reference da API (Redoc)
    ├── openapi.yaml  Especificação OpenAPI 3.1
    └── redoc.standalone.js
```

## Status de cada componente

| Componente              | Status         | Observação                                        |
|-------------------------|----------------|---------------------------------------------------|
| Schema Postgres + seeds | ✅ v0.1.0       | 28 normas, 245 processos, 90 riscos, 97 vínculos |
| Export JSON / SQLite    | ✅ v0.1.0       | 174KB JSON · 160KB SQLite                         |
| Landing + docs          | ✅ v0.1.0       | Estático, deploy em qualquer hosting              |
| API REST (FastAPI)      | 🚧 planejado   | Próxima iteração                                  |
| Camada de IA (tradução) | 🚧 planejado   | Conectores para RCSA, BIA, RH, Custos             |
| SDK npm / pip           | 📅 Q3          | Após API estável                                  |
| Validação regulatória   | 🚧 contínuo    | Conferência contra base oficial dos reguladores   |

## Quickstart

### Backend (catálogo + export)

```bash
cd backend
make up              # Postgres com schema+seeds carregados (precisa Docker)
make stats           # estatísticas do chassi
make install         # deps Python
make export-all      # gera chassi.json + chassi.sqlite
```

### Web (landing + docs)

```bash
cd web
python -m http.server 8765
# abre http://localhost:8765/index.html
```

## Filosofia

> O moat é o catálogo curado e versionado, não o código.

Toda instituição financeira convive com a mesma planilha esquecida — a lista
das normas que se aplicam a ela e dos controles que materializam o
cumprimento delas. O Chassi a escreve uma vez, versiona, mantém. O
consumidor passa atributos, recebe a fatia.

Três camadas de federação compõem o catálogo:

- **Núcleo Universal (U)** — processos e riscos comuns a qualquer entidade regulada
- **Núcleos Setoriais** (B, MC, S, P, C) — bancário, mercado de capitais, seguros, previdência, capitalização
- **Núcleo Conglomerado (CG)** — riscos que só existem no nível agregado

Hierarquias paralelas P0→P4 (processos) e R0→R4 (riscos) com vínculos
qualificados em três tipos: `primária` (o processo é dono), `secundária`
(contribui), `informativa` (princípios apenas).

## Licença

Copyright © 2026 WCN Softwares.

Esquema de dados, scripts de export e código de apresentação são tornados
públicos para inspeção e estudo. O **conteúdo do catálogo regulatório**
(normas seedadas, processos, riscos, vínculos qualificados, materialidades
default) é de uso comercial restrito e licenciado separadamente.

Para licenciamento comercial: walter.correa.neto@gmail.com

## Roadmap

**v0.2** — top-150 normas BCB incluindo cartas-circulares, P3/P4 detalhados
com controles-modelo, biblioteca inicial de KRIs por risco, integração com
indicadores de denúncia do BACEN.

**v0.3** — camada de IA com conectores para fontes do banco (RCSA, BIA,
sistemas de RH, custos, auditoria), módulo de cobertura por entidade
(relatórios automáticos de gap), tracker de mudanças com diff semântico.

**v1.0** — auditoria regulatória independente do conteúdo, certificação por
órgão técnico, SLA contratual, on-prem opcional.

## Contato

walter.correa.neto@gmail.com

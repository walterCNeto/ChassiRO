# Changelog

Todas as mudanças relevantes do **conteúdo do catálogo** e do **código** são
registradas aqui. O versionamento segue [SemVer](https://semver.org/lang/pt-BR/).

## [0.1.0] — 2026-04-30

### Adicionado

#### Catálogo regulatório
- 12 reguladores: CMN, BCB, CVM, CNSP, SUSEP, PREVIC, CNPC, COAF, ANPD, B3, BSM, ANBIMA
- 25 tipos de entidade canônicos (banco múltiplo, DTVM, seguradora, EAPC, EFPC etc.)
- 9 segmentos prudenciais (S1–S5 BCB e equivalentes SUSEP)
- 39 atividades canônicas (captação, crédito, câmbio, pagamentos, distribuição VM etc.)
- 28 normas estruturantes vigentes:
  - Leis: 4.595/64, 6.385/76, DL 73/66, LC 109/01, LC 105/01, 9.613/98, 12.846/13, 13.709/18 (LGPD), 8.078/90 (CDC)
  - CMN/BCB: Res 4.557/17 (GIR), 4.553/17 (segmentação), 4.193/13 (capital), BCB 200/22, 4.893/21 (ciber), 4.943/21 (controles), 4.945/21 (PRSAC), 4.860/20 (ouvidoria), Circ 3.978/20 (PLD), 4.502/16, 4.966/21 (IFRS 9)
  - CVM: 35/21 (suitability), 50/21, 21/21, 175/22 (fundos)
  - SUSEP/CNSP: 416/21 (gestão de riscos), 648/21 (ORSA)
  - ANBIMA: Distribuição, Adm e Gestão
- 13 artigos-chave anotados (Res 4.557, Circ 3.978, Res 4.893)
- 224 entradas de aplicabilidade por tipo de entidade
- 8 entradas de aplicabilidade por segmento
- 7 entradas de aplicabilidade por atividade

#### Hierarquia P × R
- 245 processos com hierarquia P0 → P2 (universal e bancário) e P0 → P1 (demais núcleos)
- 90 riscos com hierarquia R0 → R1 (universal completa) e R0 (demais núcleos)
- 97 vínculos norma → processo qualificados (primária / secundária / informativa)
- 34 vínculos norma → risco
- 68 entradas da matriz processo × risco com materialidade default 1–5

#### Schema e ferramental
- DDL completo Postgres 16 (compatível com SQLite após adaptação)
- 8 views analíticas (densidade regulatória, normas órfãs, matriz P×R, hierarquia expandida etc.)
- Export Python via Click CLI: `to-json`, `to-sqlite`, `stats`
- Docker Compose com schema + seeds auto-carregados
- Makefile com atalhos (up, down, reset, psql, stats, export-*)

#### Web (landing + docs)
- Landing institucional single-file (HTML+CSS+JS, sem build)
- Página de docs com Redoc auto-hospedado (sem CDN runtime)
- Especificação OpenAPI 3.1: 20 paths em 7 tags, 18 schemas, 2 servers
- Estética: Fraunces + Manrope + IBM Plex Mono · paleta papel-tinta com accent vinho-carimbo

### Limitações conhecidas
- Números, datas e status das normas precisam ser revalidados contra a base
  oficial dos reguladores antes de uso operacional
- P3/P4 detalhados ainda não estão seedados
- R2/R3/R4 ainda não estão seedados
- Cobertura de cartas-circulares e ofícios B3/BSM é parcial
- API REST ainda não implementada (apenas spec)

[0.1.0]: https://github.com/walterCNeto/ChassiRO/releases/tag/v0.1.0

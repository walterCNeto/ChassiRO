---
name: 📜 Adicionar uma norma nova
about: Propor inclusão de uma norma regulatória ainda não presente no catálogo
title: "feat(norma): [REGULADOR] Nº/ANO — ementa curta"
labels: ["catalog", "new-norm"]
---

## Identificação da norma

- **Tipo**: (lei, lei complementar, res_cmn, res_bcb, circ_bcb, res_cvm, etc.)
- **Número**:
- **Ano**:
- **Regulador**: (CMN, BCB, CVM, SUSEP, CNSP, COAF, ANPD, ANBIMA, B3, BSM, ...)
- **Status**: (vigente, parcialmente_revogada, ...)
- **URL oficial**:

## Ementa (texto curto descrevendo o tema)

(uma frase ou parágrafo breve resumindo do que a norma trata)

## Aplicabilidade

A quais tipos de entidade essa norma se aplica? (ENT_BANCO_MULTIPLO,
ENT_DTVM, ENT_SEGURADORA, etc.)

A quais segmentos prudenciais? (S1-S5, ou todos?)

A quais atividades canônicas? (ATV_CAMBIO_COMERCIAL, ATV_PIX, etc, ou
nenhum filtro de atividade?)

## Vínculos com processos

Quais processos do chassi são impactados primariamente por essa norma?
(use os IDs de `backend/seed/030_processos.sql`)

Exemplo:

- `P0.U.4` (PLD-FT) — primária
- `P1.U.4.1` (KYC) — primária
- `P1.U.4.2` (Monitoramento) — secundária

## Vínculos com riscos (opcional, se óbvio)

- `R0.U.8` (Risco de PLD-FT) — primária
- ...

## Artigos-chave (opcional)

Há algum artigo específico que mereça anotação separada em `norma_artigos`?

- art. NN — tema do artigo
- art. NN — tema do artigo

## Observações adicionais

(qualquer coisa que ajude na revisão — interpretação contestada, normas
relacionadas, prazo de adequação, etc.)

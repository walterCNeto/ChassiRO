# Como contribuir

O Chassi de Controles Internos é um **bem público colaborativo** — um catálogo
regulatório curado para o sistema financeiro brasileiro, mantido por quem usa.
Toda contribuição que melhore a precisão, a cobertura ou a usabilidade é
bem-vinda.

Este documento explica como propor mudanças. Não é longo de propósito — o
processo é leve.

## Tipos de contribuição mais comuns

**Adicionar uma norma nova.** Uma resolução do CMN/BCB/CVM/SUSEP foi
publicada e ainda não está no catálogo? Abra um Pull Request adicionando a
norma no `backend/seed/020_normas.sql`, a aplicabilidade nos seeds
correspondentes e o vínculo com processos em `050_vinculos.sql`.

**Corrigir uma norma existente.** Número errado, data de vigência incorreta,
status desatualizado, vínculo qualificado mal classificado (uma norma
marcada como `primária` que deveria ser `secundária`, por exemplo).

**Adicionar um processo ou risco.** Especialmente em níveis P3/P4 e R2/R3/R4
que ainda estão pouco populados na v0.1.

**Corrigir bugs no schema, no export ou na landing.** Issues de SQL, edge
cases no `export.py`, quebras de layout responsivo, etc.

**Documentação.** Melhorar o README, o CHANGELOG, exemplos de queries, FAQ
da landing.

## Processo

### 1. Antes de codar, abra uma Issue (para mudanças não-triviais)

Para correções pequenas (typo no README, ajuste em uma linha do seed) você
pode ir direto pro PR. Mas para qualquer coisa que mude estrutura, adicione
norma nova, ou faça mudança grande na landing — abra uma Issue primeiro
descrevendo a proposta. Isso evita você gastar tempo num PR que vai precisar
ser refeito.

Use o template de Issue que mais se aproxima do que você quer propor.

### 2. Forke o repositório e crie um branch descritivo

```bash
git clone https://github.com/SEU-USUARIO/ChassiRO.git
cd ChassiRO
git checkout -b add-res-cmn-XXXX
```

Convenções de branch:
- `add-res-cmn-NNNN` — adiciona norma do CMN
- `fix-vinculo-NNN` — corrige vínculo
- `feat-views-densidade` — nova view ou feature
- `docs-readme` — documentação

### 3. Faça suas mudanças

Antes do commit, valide localmente que o catálogo continua carregando:

```bash
cd backend
make reset       # apaga e recarrega o Postgres do zero
make stats       # confere os números
```

Se você mudou seeds e os números de `make stats` não bateram com o esperado,
algo está errado.

### 4. Commit com mensagem descritiva

Convenção (não obrigatória, mas ajuda no histórico):

- `feat: adiciona Res CMN 4.967/24 sobre risco climático`
- `fix: corrige vigência da Circ BCB 3.978`
- `docs: ajusta exemplos de query no README`
- `refactor: separa view de densidade em duas`

### 5. Abra o Pull Request

No PR, descreva:

- **O que** mudou (uma frase)
- **Por que** (link pra norma oficial, ou pra Issue, ou pra discussão)
- **Como validar** (queries que confirmam a mudança, screenshots se for visual)

Não precisa ser longo. Um PR bem feito tem 3-5 linhas de descrição.

### 6. Revisão

Hoje a revisão é feita pelo mantenedor (Walter C. Neto). PRs simples e bem
documentados fazem merge em 1-3 dias. PRs maiores podem precisar de discussão.

Quando o projeto crescer, o time de mantenedores cresce junto — contribuidores
recorrentes são convidados a se tornar revisores.

## Padrões de qualidade

### Para mudanças no catálogo regulatório

**Toda norma adicionada precisa**:

1. Ser uma norma vigente (ou que esteve vigente, com status correto)
2. Ter número, ano e regulador corretos verificáveis na fonte oficial
3. Ter aplicabilidade declarada (tipos de entidade, segmentos, atividades)
4. Ter pelo menos um vínculo norma→processo
5. Ter URL oficial no campo `url_oficial` quando possível

**Toda mudança de vínculo precisa explicar**:

- Por que é `primária`, `secundária` ou `informativa`
- Se a classificação muda (de secundária para primária, por ex), justificar
  no PR

### Para mudanças no código

- Schema SQL deve ser compatível com Postgres 16 e razoavelmente portável pra
  SQLite (após adaptação no export)
- Python: sem novas dependências sem justificativa
- HTML/CSS: sem novas dependências de runtime; tudo single-file ou local

## O que NÃO entra no catálogo

Para preservar o foco do produto, certas coisas ficam de fora:

- **Conteúdo proprietário de instituição específica.** Nada que veio de
  política interna de banco, manual privado, ou consultoria proprietária.
  Apenas conteúdo público das fontes oficiais e textos próprios da
  comunidade.
- **Avaliações subjetivas como dados.** Materialidades default são
  sugestões iniciais — quem instancia o chassi sobrepõe com o que faz
  sentido na realidade dele. Não tente debater "quanto é a materialidade
  real do risco operacional em pagamentos" no catálogo.
- **Conteúdo de outros países.** O escopo é o sistema financeiro
  brasileiro. Forks regionais (Chile, México, etc) seriam projetos
  separados.

## Código de conduta

Este projeto adota o [Contributor Covenant 2.1](./CODE_OF_CONDUCT.md). A
discussão técnica pode ser dura — a discussão pessoal não.

## Como discutir uma mudança regulatória

Disagreements sobre interpretação de norma vão acontecer. Quando acontecerem:

1. Cite a fonte oficial primeiro (texto da norma, comunicado do regulador)
2. Argumente em cima do texto, não em cima de prática de mercado (o catálogo
   reflete o que está escrito, não o que é feito)
3. Quando houver ambiguidade genuína, registre como `notas` no seed em vez
   de escolher uma interpretação arbitrária

## Atribuição

Toda contribuição aceita aparece no histórico do Git e no
`CONTRIBUTORS.md` (gerado periodicamente). Você é creditado
automaticamente.

A licença do conteúdo (CC BY 4.0) significa que quem usar o catálogo
precisa atribuir ao projeto coletivamente — não a contribuidores
individuais.

## Dúvidas

Abra uma Issue com o label `question`. Não é necessário pedir permissão
pra contribuir.

—

[Walter C. Neto](https://waltercneto.github.io/) · mantenedor inicial

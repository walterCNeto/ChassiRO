# ChassiRO — Pipeline Analítico

Ferramenta em Python que transforma o catálogo do ChassiRO em uma leitura
operacional do ambiente de controles. Lê CSVs internos da casa, combina
com seis fontes externas públicas, e gera um parecer estruturado, um
nine-box e uma tabela consolidada em uma única execução.

> **Manual completo (PDF):** [`../docs/manual.pdf`](../docs/manual.pdf)

## O que ele faz

```
   13 CSVs de entrada                              3 outputs
   ──────────────────                              ─────────
   apontamentos.csv                                resultado_consolidado.csv
   kris.csv                                        nine_box.html
   autoavaliacao.csv                               parecer.md
   bia_continuidade.csv                ─►
   auditoria_plano.csv                ─pipeline─►
   monitoramento_2linha.csv            ─►
   materialidade_interna.csv           ┌───────────┐
   riscos_declarados.csv               │  catálogo │
   mapa_taxonomia.csv                  │  ChassiRO │
                                       │ (offline  │
   procedentes_bacen.csv               │  ou API)  │
   procon_reclamacoes.csv              └───────────┘
   cvm_sancoes.csv
   anbima_sancoes.csv
   midia_adversa.csv
   reclame_aqui.csv
```

## Quickstart

```bash
# 1. Dependência (apenas em modo online)
python -m pip install requests

# 2. Rodar com os dados sintéticos do Banco Modelo S.A. (modo offline)
cd tools
python analisar.py --offline

# 3. Conferir os outputs
ls output/
# resultado_consolidado.csv  nine_box.html  parecer.md
```

Abra `output/nine_box.html` no navegador. Abra `output/parecer.md` em
qualquer editor de Markdown ou no GitHub web.

## Modos de execução

| Modo | Comando | Quando usar |
|---|---|---|
| Offline | `python analisar.py --offline` | Ambientes corporativos, auditoria, reprodutibilidade |
| Online | `python analisar.py` | Garante a versão mais recente do catálogo |

O modo offline lê `../backend/chassi.json` (snapshot do catálogo
versionado no repo). O modo online consulta `chassiro-api.fly.dev`.

## Modelo conceitual

O pipeline trabalha com 3 dimensões:

- **Eixo X** do nine-box: ambiente de controles (verde / amarelo / vermelho)
- **Eixo Y** do nine-box: impacto inerente (baixo / médio / alto)
- **Tamanho da bolha**: cobertura — % de riscos declarados nos processos
  da casa que receberam algum sinal nos últimos 12 meses

A cor das células do grid (vermelho-rosado / amarelo-mostarda /
verde-musgo) indica o quadrante: crítico (−), atenção (0), ok (+).

### Fontes que alimentam o ambiente de controles

**Internas:**
- `apontamentos.csv` — apontamentos de auditoria, regulador, gestão
- `kris.csv` — indicadores chave com histórico 6m
- `autoavaliacao.csv` — autoavaliação das áreas
- `monitoramento_2linha.csv` — atividades ativas de Riscos & Controles, Compliance, Privacidade
- `auditoria_plano.csv` — plano anual de auditoria

**Externas (todas públicas):**
- `procedentes_bacen.csv` — Painel de Reclamações do BACEN
- `cvm_sancoes.csv` — Processos Sancionadores da CVM SAS
- `anbima_sancoes.csv` — Cartas, Termos e Julgamentos ANBIMA
- `procon_reclamacoes.csv` — Procon
- `midia_adversa.csv` — menções negativas em imprensa
- `reclame_aqui.csv` — histórico mensal Reclame Aqui

### Calibração interna

- `materialidade_interna.csv` — materialidade aprovada pelo CRO (peso dobrado)
- `riscos_declarados.csv` — riscos identificados por processo (denominador da cobertura)
- `mapa_taxonomia.csv` — tradutor entre taxonomia da casa e IDs canônicos do chassi

## Pesos das fontes externas

| Fonte | Peso | Cap |
|---|---|---|
| BACEN procedente | 0.5 cada | 6.0 |
| BACEN tendência de piora | +1.5 | — |
| CVM SAS julgado | 2.0 cada | 6.0 |
| CVM SAS em curso | 1.0 cada | 6.0 |
| ANBIMA Carta de Recomendação | 0.3 cada | 3.0 |
| ANBIMA Termo de Compromisso | 0.5 cada | 3.0 |
| ANBIMA Julgamento | 1.5 cada | 3.0 |
| Procon procedente | 0.3 cada | 3.0 |
| Mídia adversa (sev≥4) | 1.0 cada | 4.0 |
| Mídia adversa (sev=3) | 0.4 cada | 4.0 |
| Reclame Aqui (queda 0.5+) | até 2.0 | — |

CVM tem peso maior porque é regulador estatal com poder sancionador.
ANBIMA é autorregulador, peso médio. Os pesos são parâmetros explícitos em
`calcular_score_controles()` — você pode ajustar para refletir o perfil de
risco da sua casa.

## Plugando os seus dados reais

Os 13 CSVs em `demo/` são sintéticos (Banco Modelo S.A., banco múltiplo S2
fictício). Para usar com dados reais:

1. Substitua o conteúdo de cada CSV mantendo as colunas
2. Atualize `mapa_taxonomia.csv` com sua taxonomia real
3. Atribua materialidade interna em `materialidade_interna.csv`
4. **Declare riscos por processo** em `riscos_declarados.csv` — esse é o
   passo mais trabalhoso, mas é o que define o denominador da cobertura
5. Substitua fontes externas com seus dados, ou deixe vazias (apenas
   cabeçalho) se não se aplicam à sua operação
6. Rode `python analisar.py --offline`

Veja o **manual em PDF** ([`../docs/manual.pdf`](../docs/manual.pdf)) para
o passo a passo detalhado.

## Cadência sugerida

| Frequência | Atividade |
|---|---|
| Trimestral | Atualizar BACEN, CVM, mídia, Reclame Aqui, apontamentos, KRIs. Levar parecer ao Comitê de Risco Operacional. |
| Semestral | Atualizar ANBIMA (alinha com Relatório de Supervisão semestral), revisar plano de auditoria. |
| Anual | Revisar mapeamento de taxonomia, riscos declarados por processo, BIA. |
| Sob demanda | Atualizar imediatamente após sanção, evento operacional ou mudança organizacional. |

## Limitações conhecidas

- Cada execução é snapshot do momento. Para tendência ao longo do tempo,
  versione os outputs em `output/historico/AAAA-Qn/`.
- Catálogo cobre 28 normas e 90 R0/R1 — não exaustivo. Próximas versões
  expandem.
- Algumas fontes externas exigem coleta manual hoje (CVM SAS, ANBIMA).
  Scrapers automáticos estão no roadmap.

## Licença

MIT (código) + CC BY 4.0 (dados sintéticos). Ver `../LICENSE` e
`../LICENSE-DATA` no repositório raiz.

## Contribuir

Issues e PRs em [github.com/walterCNeto/ChassiRO](https://github.com/walterCNeto/ChassiRO).

Para discussões sobre metodologia de pesos, sugestões de novas fontes
externas públicas, ou correções no mapeamento de taxonomia, abra uma
Issue com a tag `pipeline`.

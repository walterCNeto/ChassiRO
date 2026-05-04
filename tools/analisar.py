"""
Pipeline de análise do Chassi de Controles Internos.

Lê 6 CSVs em ./demo/, traduz pra taxonomia canônica do chassi via
mapa_taxonomia, consulta a API pública do chassi pra puxar materialidade
e processos vinculados, calcula scores de impacto e controles por R0,
e gera 3 outputs:

    output/resultado_consolidado.csv   tabela mestre por R0
    output/nine_box.html               dashboard interativo
    output/parecer.md                  parecer estruturado pra Word/PDF

Uso:

    python3 analisar.py
    python3 analisar.py --demo-dir demo --out-dir output
    python3 analisar.py --offline   # usa snapshot local (chassi.json) em vez da API

Dependências: nenhuma além de Python 3.9+ stdlib + requests (opcional).
Quando rodando offline, requests não é necessário.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import os
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

# Tentamos requests, mas funcionamos sem ele em modo offline
try:
    import requests
except ImportError:
    requests = None  # type: ignore


API_BASE = os.environ.get("CHASSI_API", "https://chassiro-api.fly.dev")


# ============================================================
# Carregamento dos dados
# ============================================================


def read_csv(path: Path) -> list[dict]:
    """Lê CSV com separador `;` e encoding utf-8-sig."""
    if not path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {path}")
    with open(path, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f, delimiter=";"))


# ============================================================
# Cliente do chassi (API pública ou snapshot local)
# ============================================================


class ChassiClient:
    """Acesso unificado ao catálogo, online ou via snapshot."""

    def __init__(self, offline: bool = False, snapshot_path: str | None = None):
        self.offline = offline
        self.snapshot: dict[str, Any] | None = None
        self.cache: dict[str, Any] = {}

        if offline:
            sp = snapshot_path or os.environ.get("CHASSI_SNAPSHOT_PATH")
            if not sp:
                # Tentar caminhos padrão
                for cand in ["chassi.json", "../backend/chassi.json", "/tmp/chassi.json"]:
                    if Path(cand).is_file():
                        sp = cand
                        break
            if not sp or not Path(sp).is_file():
                raise FileNotFoundError(
                    "Modo offline: snapshot não encontrado. "
                    "Defina --snapshot ou CHASSI_SNAPSHOT_PATH."
                )
            with open(sp, encoding="utf-8") as f:
                self.snapshot = json.load(f)
            self._build_offline_indexes()
            print(f"[chassi] Modo offline. Snapshot v{self.snapshot.get('_metadata', {}).get('version', '?')}")
        else:
            if requests is None:
                raise RuntimeError(
                    "Modo online requer 'requests'. Instale com: pip install requests "
                    "ou rode com --offline."
                )
            # Health check
            try:
                r = requests.get(f"{API_BASE}/health", timeout=10)
                r.raise_for_status()
                meta = r.json()
                print(f"[chassi] API online: {API_BASE} (v{meta.get('version')})")
            except Exception as e:
                raise RuntimeError(
                    f"API do chassi inacessível em {API_BASE}: {e}\n"
                    f"Tente rodar com --offline e --snapshot caminho/para/chassi.json"
                ) from e

    # --- modo offline ---

    def _build_offline_indexes(self):
        s = self.snapshot
        self._risco_by_id = {r["id"]: r for r in s.get("riscos", [])}
        self._processo_by_id = {p["id"]: p for p in s.get("processos", [])}
        self._norma_by_id = {n["id"]: n for n in s.get("normas", [])}

        self._vinc_pr: dict[str, list[dict]] = defaultdict(list)
        self._vinc_pr_by_proc: dict[str, list[dict]] = defaultdict(list)
        for v in s.get("vinculo_processo_risco", []):
            self._vinc_pr[v["risco_id"]].append(v)
            self._vinc_pr_by_proc[v["processo_id"]].append(v)

        self._vinc_np: dict[str, list[dict]] = defaultdict(list)
        for v in s.get("vinculo_norma_processo", []):
            self._vinc_np[v["processo_id"]].append(v)

        self._vinc_nr: dict[str, list[dict]] = defaultdict(list)
        for v in s.get("vinculo_norma_risco", []):
            self._vinc_nr[v["risco_id"]].append(v)

    # --- API unificada ---

    def get_risco(self, risco_id: str) -> dict | None:
        if risco_id in self.cache:
            return self.cache[risco_id]

        if self.offline:
            r = self._risco_by_id.get(risco_id)
            if not r:
                return None
            data = {
                **r,
                "vinculos_processo": self._vinc_pr.get(risco_id, []),
                "vinculos_norma": self._vinc_nr.get(risco_id, []),
            }
        else:
            try:
                resp = requests.get(f"{API_BASE}/v1/riscos/{risco_id}", timeout=10)
                if resp.status_code == 404:
                    return None
                resp.raise_for_status()
                data = resp.json()
            except Exception as e:
                print(f"  [aviso] falha consultar {risco_id}: {e}", file=sys.stderr)
                return None

        self.cache[risco_id] = data
        return data

    def get_processo(self, processo_id: str) -> dict | None:
        if self.offline:
            return self._processo_by_id.get(processo_id)
        try:
            resp = requests.get(f"{API_BASE}/v1/processos/{processo_id}", timeout=10)
            if resp.status_code == 404:
                return None
            resp.raise_for_status()
            return resp.json()
        except Exception:
            return None

    def get_root_id(self, risco_id: str) -> str:
        """Sobe a hierarquia até o R0."""
        cur = risco_id
        for _ in range(5):
            r = self.get_risco(cur)
            if not r:
                return cur
            parent = r.get("parent_id")
            if not parent:
                return cur
            cur = parent
        return cur


# ============================================================
# Aplicação do mapa de taxonomia
# ============================================================


def aplicar_mapa(rows: list[dict], mapa: dict[str, dict], col_categoria: str) -> list[dict]:
    """Anota cada row com 'risco_id_chassi' e 'confianca' baseado na categoria interna."""
    out = []
    for r in rows:
        cat = (r.get(col_categoria) or "").strip()
        m = mapa.get(cat)
        rid = m["risco_id_chassi"] if m else ""
        conf = m["confianca"] if m else "n/a"
        out.append({**r, "_risco_id": rid, "_confianca_mapa": conf})
    return out


def normalizar_data(s: str) -> dt.date | None:
    """Aceita dd/mm/yyyy."""
    s = (s or "").strip()
    if not s:
        return None
    try:
        return dt.datetime.strptime(s, "%d/%m/%Y").date()
    except ValueError:
        return None


# ============================================================
# Cálculo dos scores
# ============================================================


def calcular_score_controles(
    apontamentos_r: list[dict],
    kris_r: list[dict],
    autoavals_r: list[dict],
    procedentes_bacen_r: list[dict] | None = None,
    procon_r: list[dict] | None = None,
    midia_r: list[dict] | None = None,
    reclame_aqui: list[dict] | None = None,
    cvm_r: list[dict] | None = None,
    anbima_r: list[dict] | None = None,
    cobertura_pct: float = 50.0,
    confianca_degradada: bool = False,  # mantido por compat, mas ignorado
) -> tuple[float, str, list[str]]:
    """
    Score de 0-10. Quanto MAIOR, pior o ambiente de controles.

    Combina sinais internos (apontamentos, KRIs, autoavaliação) e externos
    (BACEN procedentes, Procon, mídia adversa, Reclame Aqui, CVM SAS, ANBIMA).

    Pesos das fontes externas:
    - BACEN procedente: 0.5 cada, cap 6.0
    - CVM SAS julgado: 2.0 cada (regulador estatal, peso alto). Em curso: 1.0. Cap 6.0.
    - ANBIMA: Carta Recomendação 0.3, Termo Compromisso 0.5, Julgamento 1.5. Cap 3.0.
    - Procon: 0.3 cada, cap 3.0
    - Mídia adversa sev≥4: 1.0 cada; sev=3: 0.4. Cap 4.0.
    - Reclame Aqui: queda na nota → penalidade até 2.0

    Retorna (score, classificacao, justificativas).
    """
    procedentes_bacen_r = procedentes_bacen_r or []
    procon_r = procon_r or []
    midia_r = midia_r or []
    reclame_aqui = reclame_aqui or []
    cvm_r = cvm_r or []
    anbima_r = anbima_r or []

    score = 0.0
    just = []

    # === 1. Apontamentos internos ===
    pesos_sev = {"Crítico": 4.0, "Alto": 2.0, "Médio": 1.0, "Baixo": 0.5}
    abertos_score = 0.0
    abertos_count = 0
    reg_count = 0

    for a in apontamentos_r:
        if a.get("status") not in ("Aberto", "Em remediação"):
            continue
        peso = pesos_sev.get(a.get("severidade", ""), 0.5)
        if a.get("origem") in ("BCB", "CVM"):
            peso *= 2
            reg_count += 1
        abertos_score += peso
        abertos_count += 1

    if abertos_count > 0:
        score += abertos_score
        just.append(
            f"{abertos_count} apontamento(s) aberto(s)"
            + (f" — {reg_count} de regulador" if reg_count else "")
            + f" — peso {abertos_score:.1f}"
        )

    # === 2. KRIs ===
    pesos_kri = {"Vermelho": 3.0, "Amarelo": 1.0, "Verde": 0.0}
    kri_score = 0.0
    kri_vermelho = 0
    kri_amarelo = 0
    kri_piorando = 0

    for k in kris_r:
        peso = pesos_kri.get(k.get("status_mes", ""), 0)
        kri_score += peso
        if k.get("status_mes") == "Vermelho":
            kri_vermelho += 1
        elif k.get("status_mes") == "Amarelo":
            kri_amarelo += 1

        hist = (k.get("historico_6m") or "").split(",")
        if len(hist) == 6:
            cores_para_num = {"verde": 0, "amarelo": 1, "vermelho": 2}
            primeiros = sum(cores_para_num.get(h.strip(), 0) for h in hist[:3])
            ultimos = sum(cores_para_num.get(h.strip(), 0) for h in hist[3:])
            if ultimos > primeiros + 1:
                kri_score += 1.0
                kri_piorando += 1

    if kri_score > 0:
        score += kri_score
        just.append(
            f"KRIs: {kri_vermelho} vermelho(s), {kri_amarelo} amarelo(s)"
            + (f", {kri_piorando} em piora 6m" if kri_piorando else "")
        )

    # === 3. Autoavaliação (eficácia invertida) ===
    if autoavals_r:
        ef_media = sum(int(a.get("eficacia_controles", 3)) for a in autoavals_r) / len(autoavals_r)
        ajuste_ef = (3 - ef_media)
        score += ajuste_ef
        just.append(f"Eficácia autoavaliada média {ef_media:.1f}/5 (ajuste {ajuste_ef:+.1f})")

    # === 4. Procedentes BACEN (peso ALTO — é regulador e é público) ===
    if procedentes_bacen_r:
        # Peso 5 por procedente. Só procedentes (não improcedentes).
        proc_count = sum(1 for p in procedentes_bacen_r if p.get("procedencia") == "Procedente")
        if proc_count > 0:
            # Cap em 30 pra não explodir o score
            proc_peso = min(proc_count * 0.5, 6.0)
            score += proc_peso

            # Tendência: proc nos últimos 90 dias vs. 90-180 dias
            recentes_90 = sum(1 for p in procedentes_bacen_r
                              if p.get("procedencia") == "Procedente"
                              and _dias_atras(p.get("data_reclamacao", "")) <= 90)
            entre_90_180 = sum(1 for p in procedentes_bacen_r
                               if p.get("procedencia") == "Procedente"
                               and 90 < _dias_atras(p.get("data_reclamacao", "")) <= 180)

            piorando_bcb = recentes_90 > entre_90_180 * 1.3 and recentes_90 >= 3
            if piorando_bcb:
                score += 1.5
                just.append(
                    f"BACEN: {proc_count} procedente(s) — peso {proc_peso:.1f} "
                    f"({recentes_90} nos últimos 90d vs. {entre_90_180} no período anterior — TENDÊNCIA EM ALTA +1.5)"
                )
            else:
                just.append(f"BACEN: {proc_count} procedente(s) — peso {proc_peso:.1f}")

    # === 5. Procon (peso médio) ===
    if procon_r:
        proc_count = sum(1 for p in procon_r if p.get("procedencia") == "Procedente")
        if proc_count > 0:
            proc_peso = min(proc_count * 0.3, 3.0)
            score += proc_peso
            just.append(f"Procon: {proc_count} procedente(s) — peso {proc_peso:.1f}")

    # === 6. Mídia adversa (severidade ≥3 conta) ===
    if midia_r:
        mid_score = 0.0
        n_alta = sum(1 for m in midia_r if int(m.get("severidade_percebida", 0)) >= 4)
        n_media = sum(1 for m in midia_r if int(m.get("severidade_percebida", 0)) == 3)
        if n_alta or n_media:
            mid_score = n_alta * 1.0 + n_media * 0.4
            mid_score = min(mid_score, 4.0)
            score += mid_score
            just.append(
                f"Mídia adversa: {n_alta} severidade alta + {n_media} média — peso {mid_score:.1f}"
            )

    # === 6.1. CVM SAS (regulador estatal — peso alto) ===
    if cvm_r:
        cvm_score = 0.0
        # Julgados com penalidade pesam mais que em curso
        n_julgado = sum(1 for c in cvm_r if c.get("status") in ("Julgado", "Encerrado"))
        n_em_curso = sum(1 for c in cvm_r if c.get("status") == "Em curso")
        cvm_score = n_julgado * 2.0 + n_em_curso * 1.0
        cvm_score = min(cvm_score, 6.0)
        if cvm_score > 0:
            score += cvm_score
            just.append(
                f"CVM SAS: {n_julgado} julgado(s) + {n_em_curso} em curso — peso {cvm_score:.1f}"
            )

    # === 6.2. ANBIMA (autorregulador — peso médio) ===
    if anbima_r:
        anb_score = 0.0
        n_carta = sum(1 for a in anbima_r if a.get("tipo_documento") == "Carta de Recomendação")
        n_termo = sum(1 for a in anbima_r if a.get("tipo_documento") == "Termo de Compromisso")
        n_jul = sum(1 for a in anbima_r if a.get("tipo_documento") == "Julgamento")
        anb_score = n_carta * 0.3 + n_termo * 0.5 + n_jul * 1.5
        anb_score = min(anb_score, 3.0)
        if anb_score > 0:
            score += anb_score
            partes = []
            if n_carta:
                partes.append(f"{n_carta} carta(s)")
            if n_termo:
                partes.append(f"{n_termo} termo(s)")
            if n_jul:
                partes.append(f"{n_jul} julgamento(s)")
            just.append(f"ANBIMA: {' + '.join(partes)} — peso {anb_score:.1f}")

    # === 7. Reclame Aqui (sinal de tendência) ===
    if reclame_aqui and len(reclame_aqui) >= 6:
        # Comparar últimos 3 meses com 3 anteriores
        ult_3 = reclame_aqui[-3:]
        ant_3 = reclame_aqui[-6:-3]
        nota_ult = sum(float(r.get("nota_geral", 0)) for r in ult_3) / 3
        nota_ant = sum(float(r.get("nota_geral", 0)) for r in ant_3) / 3
        delta = nota_ant - nota_ult  # positivo = piorou (nota caiu)
        if delta >= 0.5:
            ajuste_ra = min(delta * 2, 2.0)
            score += ajuste_ra
            just.append(
                f"Reclame Aqui: nota caiu de {nota_ant:.1f} para {nota_ult:.1f} (-{delta:.1f}) — peso {ajuste_ra:.1f}"
            )
        elif nota_ult < 6.5:
            score += 1.0
            just.append(f"Reclame Aqui: nota baixa {nota_ult:.1f}/10 — peso 1.0")

    # === 8. Modulação por COBERTURA ===
    # Se cobertura é baixa, "ausência de evidência" é fraca — score sobe.
    # Se cobertura é alta e há poucos sinais, validação confiável — score se mantém baixo.
    sinais_negativos = score  # snapshot antes do ajuste de cobertura
    if cobertura_pct < 30 and sinais_negativos < 3:
        # Pouca evidência em qualquer direção, e baixa cobertura: ambiente desconhecido
        score += 2.0
        just.append(
            f"⚠ COBERTURA BAIXA ({cobertura_pct:.0f}%): score elevado em +2.0 "
            f"— ausência de apontamentos não é validação"
        )
    elif cobertura_pct < 50 and sinais_negativos < 2:
        score += 1.0
        just.append(
            f"Cobertura limitada ({cobertura_pct:.0f}%): score elevado em +1.0"
        )
    elif cobertura_pct >= 70 and sinais_negativos < 2:
        # Cobertura alta + poucos sinais = validação confiável (sem ajuste, score já baixo)
        just.append(f"Cobertura alta ({cobertura_pct:.0f}%): ambiente validado")

    # Normalizar para 0-10
    score = max(0.0, min(10.0, score))

    # Classificar
    if score >= 6.0:
        classif = "vermelho"
    elif score >= 3.0:
        classif = "amarelo"
    else:
        classif = "verde"

    return score, classif, just


def _dias_atras(data_str: str) -> int:
    """Retorna dias entre uma data no formato dd/mm/yyyy e hoje."""
    d = normalizar_data(data_str)
    if not d:
        return 9999
    return (dt.date.today() - d).days


# ============================================================
# Cálculo de cobertura (3 linhas de defesa)
# ============================================================


def calcular_cobertura_processo(
    processo_id: str,
    riscos_declarados_no_processo: list[dict],
    todas_fontes_por_risco: dict[str, list[str]],
) -> tuple[float, dict, list[str]]:
    """
    Calcula cobertura de um PROCESSO: % de riscos declarados que receberam
    algum sinal nos últimos 12 meses.

    `riscos_declarados_no_processo`: linhas do CSV riscos_declarados.csv
        filtradas para esse processo específico.
    `todas_fontes_por_risco`: dict { risco_id: [lista de fontes que tocaram esse risco] }
        Onde fontes podem ser: 'apontamento', 'kri', 'autoaval', 'monit_2l',
        'audit_plano', 'bacen', 'procon', 'midia', 'reclame_aqui'.

    Retorna (cobertura_pct, detalhes, riscos_sem_sinal).
    """
    if not riscos_declarados_no_processo:
        return 0.0, {"declarados": 0, "avaliados": 0}, []

    avaliados = []
    sem_sinal = []
    for d in riscos_declarados_no_processo:
        rid = d.get("risco_chassi_id")
        # também conta se o RISCO PAI (R0) recebeu sinal, para R1 declarados
        rid_pai = ".".join(rid.split(".")[:3]) if rid.startswith("R1") else rid
        # Considera "avaliado" se o risco específico OU o R0 pai recebeu algum sinal
        sinais = todas_fontes_por_risco.get(rid, []) + todas_fontes_por_risco.get(rid_pai, [])
        sinais = list(set(sinais))
        if sinais:
            avaliados.append({"risco": rid, "fontes": sinais})
        else:
            sem_sinal.append({
                "risco_id": rid,
                "risco_nome": d.get("risco_nome", ""),
                "severidade": d.get("severidade_inerente"),
                "declarado_por": d.get("declarado_por"),
            })

    pct = 100.0 * len(avaliados) / len(riscos_declarados_no_processo)
    detalhes = {
        "declarados": len(riscos_declarados_no_processo),
        "avaliados": len(avaliados),
        "sem_sinal": len(sem_sinal),
    }
    return pct, detalhes, sem_sinal


def calcular_cobertura_r0(
    r0_id: str,
    declaracoes_r0: list[dict],
    coberturas_processos: dict[str, dict],
) -> tuple[float, dict]:
    """
    Calcula cobertura de um R0: média ponderada das coberturas dos processos
    onde esse R0 (ou seus filhos R1) foram declarados.

    Peso de cada processo = número de declarações desse R0 (família) nesse processo.
    """
    if not declaracoes_r0:
        return 0.0, {"processos": 0, "declarados_total": 0, "avaliados_total": 0}

    # Coletar processos únicos que declararam esse R0
    processos_envolvidos = {}  # processo_id -> count de declaracoes
    for d in declaracoes_r0:
        pid = d.get("processo_chassi_id")
        processos_envolvidos[pid] = processos_envolvidos.get(pid, 0) + 1

    # Média ponderada
    soma_pct = 0.0
    soma_pesos = 0
    declarados_total = 0
    avaliados_total = 0
    for pid, peso in processos_envolvidos.items():
        cob_proc = coberturas_processos.get(pid)
        if not cob_proc:
            continue
        soma_pct += cob_proc["pct"] * peso
        soma_pesos += peso
        # Mas pra contadores totais, contar só as declarações desse R0 nesse processo
        # (não as outras declarações do processo). Pra simplicidade aqui usamos
        # os totais do processo — mais informativo.
        declarados_total += cob_proc["detalhes"]["declarados"]
        avaliados_total += cob_proc["detalhes"]["avaliados"]

    if soma_pesos == 0:
        return 0.0, {"processos": 0, "declarados_total": 0, "avaliados_total": 0}

    pct = soma_pct / soma_pesos
    detalhes = {
        "processos": len(processos_envolvidos),
        "declarados_total": declarados_total,
        "avaliados_total": avaliados_total,
        "lista_processos": list(processos_envolvidos.keys()),
    }
    return pct, detalhes


def calcular_score_impacto(
    risco: dict,
    chassi: ChassiClient,
    bia_rows: list[dict],
    autoavals_r: list[dict],
    materialidade_interna: dict | None = None,
) -> tuple[float, str, list[str]]:
    """
    Score de 1-5 do impacto inerente.

    Prioriza MATERIALIDADE INTERNA (decidida pela casa, aprovada pelo CRO).
    Default do chassi entra apenas como contexto/fallback.
    Adicionalmente: criticidade BIA + impacto autoavaliado.
    """
    just = []
    contribs = []
    rid = risco.get("id", "")

    # === 1. Materialidade INTERNA (peso máximo, sempre prevalece) ===
    materialidade_chassi = 0
    n_vinc = 0
    nucleos_processos: set[str] = set()
    for v in risco.get("vinculos_processo", []):
        m = v.get("materialidade_default") or 0
        if m > materialidade_chassi:
            materialidade_chassi = m
        n_vinc += 1
        proc = chassi.get_processo(v["processo_id"])
        if proc:
            nucleos_processos.add(proc.get("nucleo", ""))

    if materialidade_interna and rid in materialidade_interna:
        m_int = materialidade_interna[rid]
        m_val = int(m_int.get("materialidade", 3))
        # Peso DOBRADO — materialidade interna domina
        contribs.append(m_val)
        contribs.append(m_val)

        com = (m_int.get("comentario_interno") or "")[:80]
        aprovador = m_int.get("aprovado_por", "?")
        data = m_int.get("data_aprovacao", "?")
        just.append(
            f"Materialidade interna: {m_val}/5 — {com}"
            + (f" (aprovada por {aprovador} em {data})" if aprovador != "?" else "")
        )

        # Comparar com default chassi
        if materialidade_chassi > 0 and abs(m_val - materialidade_chassi) >= 2:
            just.append(
                f"Default chassi seria {materialidade_chassi}/5 ({n_vinc} processos vinculados) — divergência intencional"
            )
    else:
        # Fallback: materialidade do chassi
        if materialidade_chassi > 0:
            contribs.append(materialidade_chassi)
            just.append(
                f"Materialidade default chassi (FALLBACK — sem materialidade interna definida): "
                f"{materialidade_chassi}/5 ({n_vinc} processos vinculados)"
            )
        else:
            contribs.append(2.5)
            just.append("Sem materialidade interna nem vínculo no chassi; default 2.5")

    # === 2. Criticidade BIA — sinal complementar para riscos universais ===
    if bia_rows and "U" in nucleos_processos:
        criticos_bia = sum(1 for b in bia_rows if b.get("criticidade") == "Crítico")
        if criticos_bia >= 5:
            contribs.append(4.0)
            just.append(f"BIA: {criticos_bia} processos críticos no banco (sinal indireto)")

    # === 3. Impacto autoavaliado ===
    if autoavals_r:
        imp_max = max(int(a.get("impacto", 3)) for a in autoavals_r)
        contribs.append(imp_max)
        just.append(f"Impacto autoavaliado máximo: {imp_max}/5")

    # Score = média dos contribuintes (materialidade interna entra dobrado, então domina)
    if contribs:
        score = sum(contribs) / len(contribs)
    else:
        score = 2.5

    # Classificar com pontos de corte mais espalhados
    if score >= 4.0:
        classif = "alto"
    elif score >= 3.0:
        classif = "medio"
    else:
        classif = "baixo"

    return score, classif, just


# ============================================================
# Pipeline principal
# ============================================================


def consolidar(demo_dir: Path, out_dir: Path, offline: bool, snapshot_path: str | None):
    print(f"==> Lendo CSVs de {demo_dir}/")
    apontamentos = read_csv(demo_dir / "apontamentos.csv")
    kris = read_csv(demo_dir / "kris.csv")
    autoavaliacao = read_csv(demo_dir / "autoavaliacao.csv")
    bia = read_csv(demo_dir / "bia_continuidade.csv")
    plano_audit = read_csv(demo_dir / "auditoria_plano.csv")
    mapa_rows = read_csv(demo_dir / "mapa_taxonomia.csv")

    # Novas fontes (v2). Lemos com tolerância — se faltarem, seguimos.
    def read_csv_optional(path: Path) -> list[dict]:
        try:
            return read_csv(path)
        except FileNotFoundError:
            return []

    materialidade_rows = read_csv_optional(demo_dir / "materialidade_interna.csv")
    procedentes_bacen = read_csv_optional(demo_dir / "procedentes_bacen.csv")
    procon = read_csv_optional(demo_dir / "procon_reclamacoes.csv")
    reclame_aqui = read_csv_optional(demo_dir / "reclame_aqui.csv")
    midia = read_csv_optional(demo_dir / "midia_adversa.csv")
    monit_2l = read_csv_optional(demo_dir / "monitoramento_2linha.csv")
    riscos_declarados = read_csv_optional(demo_dir / "riscos_declarados.csv")
    cvm_sancoes = read_csv_optional(demo_dir / "cvm_sancoes.csv")
    anbima_sancoes = read_csv_optional(demo_dir / "anbima_sancoes.csv")

    print(
        f"    [internas] {len(apontamentos)} apontamentos | "
        f"{len(kris)} kris | "
        f"{len(autoavaliacao)} autoavals | "
        f"{len(bia)} bias | "
        f"{len(plano_audit)} audit | "
        f"{len(monit_2l)} monit. 2L"
    )
    print(
        f"    [externas] {len(procedentes_bacen)} BACEN | "
        f"{len(procon)} Procon | "
        f"{len(cvm_sancoes)} CVM | "
        f"{len(anbima_sancoes)} ANBIMA | "
        f"{len(reclame_aqui)} Reclame Aqui | "
        f"{len(midia)} mídia"
    )
    print(
        f"    [calibração] {len(materialidade_rows)} R0 com materialidade interna | "
        f"{len(riscos_declarados)} riscos declarados em processos"
    )

    # Mapa como dict
    mapa = {r["termo_interno"]: r for r in mapa_rows if r.get("risco_id_chassi")}
    print(f"    {len(mapa)} entradas mapeadas (de {len(mapa_rows)})")

    # Materialidade interna como dict
    materialidade_interna = {
        m["risco_id_chassi"]: m for m in materialidade_rows if m.get("risco_id_chassi")
    }

    # ===== Aplicar tradução =====
    print()
    print("==> Aplicando tradução de taxonomia")
    apontamentos = aplicar_mapa(apontamentos, mapa, "categoria_interna")
    kris = aplicar_mapa(kris, mapa, "categoria_interna")
    plano_audit = aplicar_mapa(plano_audit, mapa, "categoria_interna")

    # Novas fontes externas: aplicar mapa também
    procedentes_bacen = aplicar_mapa(procedentes_bacen, mapa, "categoria_bacen")
    procon = aplicar_mapa(procon, mapa, "categoria_procon")
    midia = aplicar_mapa(midia, mapa, "categoria_tema")
    cvm_sancoes = aplicar_mapa(cvm_sancoes, mapa, "categoria_infracao")
    anbima_sancoes = aplicar_mapa(anbima_sancoes, mapa, "categoria_infracao")

    sem_mapa_apont = sum(1 for a in apontamentos if not a["_risco_id"])
    sem_mapa_kri = sum(1 for k in kris if not k["_risco_id"])
    sem_mapa_bcb = sum(1 for p in procedentes_bacen if not p["_risco_id"])
    sem_mapa_procon = sum(1 for p in procon if not p["_risco_id"])
    sem_mapa_midia = sum(1 for m in midia if not m["_risco_id"])
    sem_mapa_cvm = sum(1 for c in cvm_sancoes if not c["_risco_id"])
    sem_mapa_anbima = sum(1 for a in anbima_sancoes if not a["_risco_id"])
    if sem_mapa_apont:
        print(f"    [aviso] {sem_mapa_apont} apontamentos sem mapeamento")
    if sem_mapa_kri:
        print(f"    [aviso] {sem_mapa_kri} KRIs sem mapeamento")
    if sem_mapa_bcb:
        print(f"    [aviso] {sem_mapa_bcb} BACEN sem mapeamento")
    if sem_mapa_procon:
        print(f"    [aviso] {sem_mapa_procon} Procon sem mapeamento")
    if sem_mapa_midia:
        print(f"    [aviso] {sem_mapa_midia} mídia sem mapeamento")
    if sem_mapa_cvm:
        print(f"    [aviso] {sem_mapa_cvm} CVM sem mapeamento")
    if sem_mapa_anbima:
        print(f"    [aviso] {sem_mapa_anbima} ANBIMA sem mapeamento")

    # ===== Conectar ao chassi =====
    print()
    print("==> Conectando ao chassi")
    chassi = ChassiClient(offline=offline, snapshot_path=snapshot_path)

    # ===== Agregar por R0 =====
    print()
    print("==> Subindo da hierarquia: R1.x.y → R0.x")

    def root_de(rid: str) -> str:
        return chassi.get_root_id(rid) if rid else ""

    # Anotar root_id em cada item de TODAS as fontes
    for a in apontamentos:
        a["_r0"] = root_de(a["_risco_id"])
    for k in kris:
        k["_r0"] = root_de(k["_risco_id"])
    for a in plano_audit:
        a["_r0"] = root_de(a["_risco_id"])
    for p in procedentes_bacen:
        p["_r0"] = root_de(p["_risco_id"])
    for p in procon:
        p["_r0"] = root_de(p["_risco_id"])
    for m in midia:
        m["_r0"] = root_de(m["_risco_id"])
    for c in cvm_sancoes:
        c["_r0"] = root_de(c["_risco_id"])
    for a in anbima_sancoes:
        a["_r0"] = root_de(a["_risco_id"])

    # Coletar R0s presentes em qualquer fonte + R0s com materialidade interna definida
    r0_set = set()
    for a in apontamentos:
        if a["_r0"]:
            r0_set.add(a["_r0"])
    for k in kris:
        if k["_r0"]:
            r0_set.add(k["_r0"])
    for p in procedentes_bacen:
        if p["_r0"]:
            r0_set.add(p["_r0"])
    for p in procon:
        if p["_r0"]:
            r0_set.add(p["_r0"])
    for m in midia:
        if m["_r0"]:
            r0_set.add(m["_r0"])
    for c in cvm_sancoes:
        if c["_r0"]:
            r0_set.add(c["_r0"])
    for a in anbima_sancoes:
        if a["_r0"]:
            r0_set.add(a["_r0"])
    # Materialidade interna também conta — risco que a casa atribuiu materialidade
    # é risco que entrou no radar formal mesmo que não tenha apontamentos
    for rid in materialidade_interna:
        r0_set.add(rid)

    print(f"    {len(r0_set)} R0 distintos identificados")

    # ===== Construir índice "fontes_por_risco" =====
    # Para cada risco_id (R0 ou R1), lista de tipos de fontes que tocaram ele.
    # Usado para determinar se um risco DECLARADO foi efetivamente avaliado.
    print()
    print("==> Construindo índice de fontes por risco")
    fontes_por_risco: dict[str, list[str]] = defaultdict(list)

    for a in apontamentos:
        rid = a.get("_risco_id")
        if rid:
            # Status "Fechado" ainda conta como evidência de que houve análise
            fontes_por_risco[rid].append("apontamento")
            if a.get("_r0"):
                fontes_por_risco[a["_r0"]].append("apontamento")

    for k in kris:
        rid = k.get("_risco_id")
        if rid:
            fontes_por_risco[rid].append("kri")
            if k.get("_r0"):
                fontes_por_risco[k["_r0"]].append("kri")

    for av in autoavaliacao:
        # Autoavaliação não tem risco_id direto; mas a área está autoavaliando
        # uma série de riscos. Vamos contar como sinal pra todos os R0 que
        # têm apontamentos/KRIs daquela área. Aqui só registraremos uma flag global.
        # (Mais à frente, quando processarmos o R0, levamos em conta autoavaliação
        # da área dona do processo)
        pass

    for a in plano_audit:
        rid = a.get("_risco_id")
        status = a.get("status", "")
        if rid and status in ("Concluído", "Em execução", "Planejado"):
            fontes_por_risco[rid].append(f"audit_plano_{status.lower()}")
            if a.get("_r0"):
                fontes_por_risco[a["_r0"]].append(f"audit_plano_{status.lower()}")

    for m in monit_2l:
        rid = m.get("risco_id_chassi")
        if rid:
            fontes_por_risco[rid].append("monit_2l")
            # também propagar pro R0 se for R1
            if rid.startswith("R1"):
                r0_pai = ".".join(rid.split(".")[:3])
                if r0_pai != rid:
                    fontes_por_risco[r0_pai].append("monit_2l")

    for p in procedentes_bacen:
        rid = p.get("_risco_id")
        if rid and p.get("procedencia") == "Procedente":
            fontes_por_risco[rid].append("bacen")
            if p.get("_r0"):
                fontes_por_risco[p["_r0"]].append("bacen")

    for p in procon:
        rid = p.get("_risco_id")
        if rid and p.get("procedencia") == "Procedente":
            fontes_por_risco[rid].append("procon")
            if p.get("_r0"):
                fontes_por_risco[p["_r0"]].append("procon")

    for m in midia:
        rid = m.get("_risco_id")
        if rid and int(m.get("severidade_percebida", 0)) >= 3:
            fontes_por_risco[rid].append("midia")
            if m.get("_r0"):
                fontes_por_risco[m["_r0"]].append("midia")

    for c in cvm_sancoes:
        rid = c.get("_risco_id")
        if rid:
            fontes_por_risco[rid].append("cvm")
            if c.get("_r0"):
                fontes_por_risco[c["_r0"]].append("cvm")

    for a in anbima_sancoes:
        rid = a.get("_risco_id")
        if rid:
            fontes_por_risco[rid].append("anbima")
            if a.get("_r0"):
                fontes_por_risco[a["_r0"]].append("anbima")

    print(f"    {len(fontes_por_risco)} riscos distintos com pelo menos 1 sinal")

    # ===== Calcular cobertura por PROCESSO =====
    print()
    print("==> Calculando cobertura por processo")
    coberturas_processos: dict[str, dict] = {}
    riscos_sem_sinal_por_proc: dict[str, list[dict]] = {}

    declaracoes_por_proc: dict[str, list[dict]] = defaultdict(list)
    for d in riscos_declarados:
        pid = d.get("processo_chassi_id")
        if pid:
            declaracoes_por_proc[pid].append(d)

    for pid, declaracoes in declaracoes_por_proc.items():
        # IMPORTANTE: autoavaliação assinada da área dona do processo conta
        # como sinal também — replica nas declarações
        # (heurística simples: se há autoavaliação, considera todos os riscos
        # daquele processo "tocados" por autoaval)
        # Pra simplificar nesse v4, deixamos só os sinais já indexados.
        cob_pct, detalhes, sem_sinal = calcular_cobertura_processo(
            pid, declaracoes, fontes_por_risco
        )
        coberturas_processos[pid] = {
            "pct": cob_pct,
            "detalhes": detalhes,
            "sem_sinal": sem_sinal,
        }
        if sem_sinal:
            riscos_sem_sinal_por_proc[pid] = sem_sinal

    print(f"    {len(coberturas_processos)} processos com cobertura calculada")

    # ===== Calcular scores por R0 =====
    print()
    print("==> Calculando scores")

    # Para cada R0, buscar declarações onde ele (ou R1 filho) aparece
    declaracoes_por_r0: dict[str, list[dict]] = defaultdict(list)
    for d in riscos_declarados:
        rid = d.get("risco_chassi_id", "")
        # se R1, sobe pra R0
        r0 = ".".join(rid.split(".")[:3]) if rid.startswith("R1") else rid
        declaracoes_por_r0[r0].append(d)

    consolidado = []
    for r0_id in sorted(r0_set):
        risco = chassi.get_risco(r0_id)
        if not risco:
            print(f"    [aviso] R0 {r0_id} não encontrado no chassi")
            continue

        # Subset de cada fonte para esse R0
        apont_r = [a for a in apontamentos if a["_r0"] == r0_id]
        kris_r = [k for k in kris if k["_r0"] == r0_id]
        bcb_r = [p for p in procedentes_bacen if p["_r0"] == r0_id]
        procon_r = [p for p in procon if p["_r0"] == r0_id]
        midia_r = [m for m in midia if m["_r0"] == r0_id]
        cvm_r = [c for c in cvm_sancoes if c["_r0"] == r0_id]
        anbima_r = [a for a in anbima_sancoes if a["_r0"] == r0_id]

        # Áreas envolvidas: das fontes internas
        areas_apont = set(a.get("area", "") for a in apont_r if a.get("area"))
        areas_kri = set(k.get("area", "") for k in kris_r if k.get("area"))
        areas_do_r0 = areas_apont | areas_kri

        # Autoavaliação: das áreas envolvidas
        autoavals_r = [
            av for av in autoavaliacao
            if av.get("area") in areas_do_r0
        ] if areas_do_r0 else []

        # === Calcular COBERTURA do R0 (agregando processos) ===
        decl_r0 = declaracoes_por_r0.get(r0_id, [])
        cob_pct, cob_detalhes = calcular_cobertura_r0(
            r0_id, decl_r0, coberturas_processos
        )

        # Lista de riscos declarados para esse R0 que NÃO foram avaliados
        riscos_sem_sinal_r0 = []
        for d in decl_r0:
            rid_decl = d.get("risco_chassi_id")
            r0_pai = ".".join(rid_decl.split(".")[:3]) if rid_decl.startswith("R1") else rid_decl
            sinais = fontes_por_risco.get(rid_decl, []) + fontes_por_risco.get(r0_pai, [])
            if not sinais:
                riscos_sem_sinal_r0.append({
                    "risco_id": rid_decl,
                    "risco_nome": d.get("risco_nome", ""),
                    "processo": d.get("processo_chassi_id", ""),
                    "declarado_por": d.get("declarado_por", ""),
                    "severidade": d.get("severidade_inerente"),
                })

        # Construir descrição da cobertura — definido aqui antes de usar
        if cob_detalhes["declarados_total"] == 0:
            cob_fonte = "sem riscos declarados (núcleo não opera ou não mapeado)"
            # Para R0 sem declarações, NÃO penalizamos a cobertura — é N/A
            cob_pct_display = -1.0
        else:
            cob_fonte = (
                f"{cob_detalhes['avaliados_total']}/{cob_detalhes['declarados_total']} "
                f"riscos declarados em {cob_detalhes['processos']} processo(s) com sinal"
            )
            cob_pct_display = cob_pct

        # Score de controles (cobertura entra como modulador, mas N/A se zero declarações)
        cob_para_score = cob_pct_display if cob_pct_display >= 0 else 50.0  # neutro se N/A
        sc, sc_class, sc_just = calcular_score_controles(
            apont_r, kris_r, autoavals_r,
            procedentes_bacen_r=bcb_r,
            procon_r=procon_r,
            midia_r=midia_r,
            reclame_aqui=reclame_aqui,
            cvm_r=cvm_r,
            anbima_r=anbima_r,
            cobertura_pct=cob_para_score,
            confianca_degradada=False,
        )

        # Score de impacto (com materialidade interna)
        si, si_class, si_just = calcular_score_impacto(
            risco, chassi, bia, autoavals_r,
            materialidade_interna=materialidade_interna,
        )

        # Quadrante nine-box
        idx_x = {"verde": 2, "amarelo": 1, "vermelho": 0}[sc_class]
        idx_y = {"baixo": 2, "medio": 1, "alto": 0}[si_class]
        quadrante = f"({idx_x},{idx_y})"

        consolidado.append({
            "r0_id": r0_id,
            "r0_nome": risco.get("nome", ""),
            "nucleo": risco.get("nucleo", ""),
            "categoria_basileia": risco.get("categoria_basileia", ""),
            "score_impacto": round(si, 2),
            "classe_impacto": si_class,
            "score_controles": round(sc, 2),
            "classe_controles": sc_class,
            "quadrante": quadrante,
            "n_apontamentos": len(apont_r),
            "n_apontamentos_abertos": sum(1 for a in apont_r if a.get("status") in ("Aberto", "Em remediação")),
            "n_apontamentos_criticos": sum(1 for a in apont_r if a.get("severidade") == "Crítico"),
            "n_apontamentos_regulador": sum(1 for a in apont_r if a.get("origem") in ("BCB", "CVM")),
            "n_kris": len(kris_r),
            "n_kris_vermelho": sum(1 for k in kris_r if k.get("status_mes") == "Vermelho"),
            "n_kris_amarelo": sum(1 for k in kris_r if k.get("status_mes") == "Amarelo"),
            "n_bacen_procedente": sum(1 for p in bcb_r if p.get("procedencia") == "Procedente"),
            "n_procon_procedente": sum(1 for p in procon_r if p.get("procedencia") == "Procedente"),
            "n_midia_alta_severidade": sum(1 for m in midia_r if int(m.get("severidade_percebida", 0)) >= 4),
            "n_cvm_julgado": sum(1 for c in cvm_r if c.get("status") in ("Julgado", "Encerrado")),
            "n_cvm_em_curso": sum(1 for c in cvm_r if c.get("status") == "Em curso"),
            "n_anbima_carta": sum(1 for a in anbima_r if a.get("tipo_documento") == "Carta de Recomendação"),
            "n_anbima_termo": sum(1 for a in anbima_r if a.get("tipo_documento") == "Termo de Compromisso"),
            "n_anbima_julgamento": sum(1 for a in anbima_r if a.get("tipo_documento") == "Julgamento"),
            "tem_materialidade_interna": "sim" if r0_id in materialidade_interna else "não",
            "n_riscos_declarados": len(decl_r0),
            "n_riscos_avaliados": len(decl_r0) - len(riscos_sem_sinal_r0),
            "n_riscos_sem_sinal": len(riscos_sem_sinal_r0),
            "cobertura_pct": round(cob_pct_display, 1) if cob_pct_display >= 0 else "n/a",
            "cobertura_fonte": cob_fonte,
            "riscos_sem_sinal_detalhe": " | ".join(
                f"{x['risco_id']} em {x['processo']}" for x in riscos_sem_sinal_r0[:5]
            ) if riscos_sem_sinal_r0 else "",
            "areas_envolvidas": " | ".join(sorted(areas_do_r0)),
            "justificativa_controles": " ; ".join(sc_just),
            "justificativa_impacto": " ; ".join(si_just),
        })

    # Ordenar por urgência (alto impacto + vermelho primeiro)
    ordem_imp = {"alto": 0, "medio": 1, "baixo": 2}
    ordem_ctrl = {"vermelho": 0, "amarelo": 1, "verde": 2}
    consolidado.sort(key=lambda r: (ordem_imp[r["classe_impacto"]], ordem_ctrl[r["classe_controles"]]))

    # ===== Escrever CSV consolidado =====
    out_dir.mkdir(parents=True, exist_ok=True)
    csv_path = out_dir / "resultado_consolidado.csv"
    with open(csv_path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(consolidado[0].keys()), delimiter=";")
        w.writeheader()
        w.writerows(consolidado)
    print()
    print(f"==> {csv_path} ({len(consolidado)} R0)")

    # ===== Gerar nine-box HTML =====
    nb_path = out_dir / "nine_box.html"
    with open(nb_path, "w", encoding="utf-8") as f:
        f.write(gerar_nine_box_html(consolidado))
    print(f"==> {nb_path}")

    # ===== Gerar parecer =====
    par_path = out_dir / "parecer.md"
    with open(par_path, "w", encoding="utf-8") as f:
        f.write(gerar_parecer_md(consolidado))
    print(f"==> {par_path}")

    print()
    print("Concluído.")
    return consolidado


# ============================================================
# Geração do nine-box HTML
# ============================================================


def gerar_nine_box_html(consolidado: list[dict]) -> str:
    """Gera HTML standalone com nine-box interativo."""
    # Distribui R0 nos 9 quadrantes
    cels: dict[tuple[int, int], list[dict]] = defaultdict(list)
    for r in consolidado:
        x, y = r["quadrante"].strip("()").split(",")
        cels[(int(x), int(y))].append(r)

    # Construir células
    # Quadrantes → tom semafórico:
    #   crítico  (X=vermelho, Y=alto/médio/baixo)  → fundo vermelho-suave
    #   atenção  (X=amarelo, qualquer Y)            → fundo amarelo-suave
    #   ok       (X=verde, qualquer Y)              → fundo verde-suave
    # Linhas (impacto): linha topo (alto) tem saturação maior, baixo é mais claro.
    def quadrante_cls(x: int, y: int) -> str:
        # x: 0=vermelho 1=amarelo 2=verde
        # y: 0=alto 1=médio 2=baixo
        col = {0: "q-red", 1: "q-yellow", 2: "q-green"}[x]
        row = {0: "row-alto", 1: "row-med", 2: "row-baixo"}[y]
        return f"{col} {row}"

    def render_celula(x: int, y: int) -> str:
        items = cels.get((x, y), [])
        cls_quad = quadrante_cls(x, y)
        if not items:
            return f'<div class="cel vazia {cls_quad}">—</div>'
        bolhas = []
        for r in items:
            # Tamanho da bolha pelo inverso da cobertura (cobertura alta = bolha pequena)
            cob_raw = r.get("cobertura_pct", 50)
            if cob_raw == "n/a":
                size_cls = "tam-na"
                cob_label = "sem riscos declarados"
            else:
                cob = float(cob_raw)
                if cob >= 70:
                    size_cls = "tam-pequena"
                    cob_label = f"cob alta {cob:.0f}%"
                elif cob >= 40:
                    size_cls = "tam-media"
                    cob_label = f"cob média {cob:.0f}%"
                else:
                    size_cls = "tam-grande"
                    cob_label = f"cob baixa {cob:.0f}%"
            bolha = f"""
                <div class="bolha {size_cls}" data-id="{r['r0_id']}" title="{cob_label}">
                    <strong>{r['r0_id']}</strong>
                    <span>{r['r0_nome']}</span>
                </div>
            """
            bolhas.append(bolha)
        return f'<div class="cel {cls_quad}">{"".join(bolhas)}</div>'

    # Y de cima pra baixo: alto(0), médio(1), baixo(2)
    grid = ""
    labels_y = ["Alto", "Médio", "Baixo"]
    labels_x = ["Vermelho", "Amarelo", "Verde"]
    for y in [0, 1, 2]:
        grid += f'<div class="row"><div class="lbl-y">{labels_y[y]}</div>'
        for x in [0, 1, 2]:
            grid += render_celula(x, y)
        grid += "</div>"

    # Tabela detalhada
    tabela_rows = ""
    for r in consolidado:
        cor_ctrl = {"vermelho": "#C8323F", "amarelo": "#D9A547", "verde": "#5E8A6B"}[r["classe_controles"]]
        intensidade_imp = {"alto": "1.0", "medio": "0.7", "baixo": "0.45"}[r["classe_impacto"]]
        # Indicador de fontes externas que dispararam
        ext_signals = []
        if int(r.get("n_bacen_procedente", 0)) > 0:
            ext_signals.append(f"🏛 BCB:{r['n_bacen_procedente']}")
        n_cvm = int(r.get("n_cvm_julgado", 0)) + int(r.get("n_cvm_em_curso", 0))
        if n_cvm > 0:
            ext_signals.append(f"🏛 CVM:{n_cvm}")
        if int(r.get("n_procon_procedente", 0)) > 0:
            ext_signals.append(f"⚖ Procon:{r['n_procon_procedente']}")
        n_anb = int(r.get("n_anbima_carta", 0)) + int(r.get("n_anbima_termo", 0)) + int(r.get("n_anbima_julgamento", 0))
        if n_anb > 0:
            ext_signals.append(f"⚖ ANBIMA:{n_anb}")
        if int(r.get("n_midia_alta_severidade", 0)) > 0:
            ext_signals.append(f"📰 Mídia:{r['n_midia_alta_severidade']}")
        ext_str = " ".join(ext_signals) if ext_signals else "—"
        # Marcador de materialidade
        mat_marker = "✓ interna" if r.get("tem_materialidade_interna") == "sim" else "default"

        # Cobertura visual
        cob_raw = r.get("cobertura_pct", 0)
        if cob_raw == "n/a":
            cob_class = "cob-na"
            cob_label = "n/a"
            cob_pct_str = ""
        else:
            cob = float(cob_raw)
            if cob >= 70:
                cob_class = "cob-alta"
                cob_label = "alta"
            elif cob >= 40:
                cob_class = "cob-media"
                cob_label = "média"
            else:
                cob_class = "cob-baixa"
                cob_label = "baixa"
            cob_pct_str = f" {cob:.0f}%"
        cob_warn = ""

        tabela_rows += f"""
        <tr>
          <td><code>{r['r0_id']}</code></td>
          <td>{r['r0_nome']}</td>
          <td><span class="pill" style="background:{cor_ctrl}">{r['classe_controles']}</span> ({r['score_controles']:.1f})</td>
          <td><span class="pill" style="background:rgba(40,40,40,{intensidade_imp})">{r['classe_impacto']}</span> ({r['score_impacto']:.1f}) <small style="opacity:0.55">[{mat_marker}]</small></td>
          <td><span class="cob-pill {cob_class}">{cob_label}{cob_pct_str}{cob_warn}</span></td>
          <td>{r['n_apontamentos_abertos']}/{r['n_apontamentos']}</td>
          <td>{r['n_kris_vermelho']}V/{r['n_kris_amarelo']}A/{r['n_kris']}</td>
          <td><span class="ext-pill">{ext_str}</span></td>
          <td class="just">{r['justificativa_controles']}</td>
        </tr>
        """

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<title>Nine-box — Banco Modelo S.A.</title>
<style>
:root {{
    --bg: #F5F1E8;
    --ink: #1F2421;
    --vinho: #8B2C2C;
    --linha: #1F2421;
    --verde: #5E8A6B;
    --amarelo: #D9A547;
    --vermelho: #C8323F;
}}
* {{ box-sizing: border-box; }}
body {{
    margin: 0;
    padding: 40px;
    background: var(--bg);
    color: var(--ink);
    font-family: Georgia, "Times New Roman", serif;
    font-size: 15px;
    line-height: 1.5;
}}
.container {{ max-width: 1200px; margin: 0 auto; }}
h1 {{ font-size: 32px; margin: 0 0 8px; font-weight: 400; }}
h1 em {{ color: var(--vinho); font-style: italic; }}
.sub {{ font-family: ui-monospace, "JetBrains Mono", monospace; font-size: 11px; letter-spacing: 0.18em; text-transform: uppercase; color: var(--ink); opacity: 0.6; margin-bottom: 32px; }}
h2 {{ font-size: 20px; margin: 48px 0 16px; font-weight: 400; }}

/* Nine-box */
.ninebox {{
    display: grid;
    grid-template-columns: 60px 1fr;
    gap: 0;
    margin: 32px 0;
}}
.lbl-axis {{
    grid-column: 1 / 2;
    grid-row: 1 / 4;
    writing-mode: vertical-rl;
    transform: rotate(180deg);
    text-align: center;
    font-family: ui-monospace, monospace;
    font-size: 10px;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    padding: 20px 0;
    align-self: center;
}}
.grid {{
    grid-column: 2 / 3;
    display: flex;
    flex-direction: column;
    border: 1.5px solid var(--linha);
}}
.row {{
    display: grid;
    grid-template-columns: 80px 1fr 1fr 1fr;
    border-bottom: 1.5px solid var(--linha);
}}
.row:last-child {{ border-bottom: none; }}
.lbl-y {{
    background: #E8E1D2;
    border-right: 1.5px solid var(--linha);
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: ui-monospace, monospace;
    font-size: 10px;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    padding: 8px;
}}
.cel {{
    border-right: 1.5px solid var(--linha);
    min-height: 180px;
    padding: 12px;
    display: flex;
    flex-wrap: wrap;
    align-content: flex-start;
    gap: 8px;
}}
.cel:last-child {{ border-right: none; }}
.cel.vazia {{
    color: rgba(31,36,33, 0.2);
    align-items: center;
    justify-content: center;
    font-size: 30px;
}}

/* Cores semafóricas POR QUADRANTE — esse é o sinal principal do nine-box */
/* Coluna determina o tom (verde/amarelo/vermelho), linha determina saturação */
.cel.q-red.row-alto    {{ background: rgba(184, 84, 84, 0.32); }}
.cel.q-red.row-med     {{ background: rgba(184, 84, 84, 0.20); }}
.cel.q-red.row-baixo   {{ background: rgba(184, 84, 84, 0.10); }}

.cel.q-yellow.row-alto  {{ background: rgba(217, 165, 71, 0.32); }}
.cel.q-yellow.row-med   {{ background: rgba(217, 165, 71, 0.20); }}
.cel.q-yellow.row-baixo {{ background: rgba(217, 165, 71, 0.10); }}

.cel.q-green.row-alto   {{ background: rgba(94, 138, 107, 0.32); }}
.cel.q-green.row-med    {{ background: rgba(94, 138, 107, 0.20); }}
.cel.q-green.row-baixo  {{ background: rgba(94, 138, 107, 0.10); }}

/* Bolhas: cor neutra única — apenas identificam QUEM está em cada quadrante */
.bolha {{
    background: var(--ink);
    color: var(--bg);
    padding: 8px 10px;
    font-size: 12px;
    line-height: 1.3;
    border-radius: 2px;
    cursor: default;
    transition: transform 0.15s;
}}
.bolha:hover {{ transform: translateY(-2px); }}
.bolha strong {{ font-family: ui-monospace, monospace; font-size: 11px; display: block; opacity: 0.7; }}
.bolha span {{ display: block; max-width: 200px; }}

/* Tamanhos por cobertura — bolha pequena = alta cobertura, grande = baixa */
.bolha.tam-pequena {{ padding: 6px 8px; font-size: 11px; }}
.bolha.tam-pequena strong {{ font-size: 10px; }}
.bolha.tam-pequena span {{ font-size: 11px; max-width: 160px; }}

.bolha.tam-media {{ padding: 8px 10px; font-size: 12px; }}

.bolha.tam-grande {{ padding: 11px 13px; font-size: 13px; box-shadow: 0 2px 4px rgba(0,0,0,0.18); }}
.bolha.tam-grande strong {{ font-size: 12px; }}
.bolha.tam-grande span {{ font-size: 13px; max-width: 220px; font-weight: 600; }}

/* Cobertura N/A: bolha muito discreta */
.bolha.tam-na {{ padding: 6px 8px; font-size: 11px; opacity: 0.45; font-style: italic; background: rgba(31,36,33, 0.55); }}
.bolha.tam-na strong {{ font-size: 10px; }}
.bolha.tam-na span {{ font-size: 11px; max-width: 160px; }}

/* Legenda do nine-box */
.legenda-ninebox {{
    display: flex;
    gap: 60px;
    margin-top: 28px;
    padding: 18px 22px;
    border: 1px solid var(--linha);
    background: rgba(255,255,255,0.4);
}}
.leg-bloco {{ flex: 1; }}
.leg-titulo {{
    font-family: ui-monospace, monospace;
    font-size: 10px;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: rgba(0,0,0,0.55);
    margin-bottom: 12px;
}}
.leg-itens {{ display: flex; flex-wrap: wrap; gap: 18px; }}
.leg-item {{
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 12.5px;
    color: var(--ink);
}}
.leg-quad {{
    display: inline-block;
    width: 22px;
    height: 22px;
    border: 1px solid rgba(0,0,0,0.15);
}}
.leg-quad.q-red    {{ background: rgba(184, 84, 84, 0.32); }}
.leg-quad.q-yellow {{ background: rgba(217, 165, 71, 0.32); }}
.leg-quad.q-green  {{ background: rgba(94, 138, 107, 0.32); }}
.leg-bolha {{
    display: inline-block;
    background: var(--ink);
    border-radius: 2px;
}}
.leg-bolha.leg-pq {{ width: 14px; height: 14px; }}
.leg-bolha.leg-md {{ width: 18px; height: 18px; }}
.leg-bolha.leg-gd {{ width: 24px; height: 24px; }}
.leg-bolha.leg-na {{ width: 14px; height: 14px; opacity: 0.45; font-style: italic; background: rgba(31,36,33, 0.55); }}

.lbl-x-row {{
    display: grid;
    grid-template-columns: 60px 80px 1fr 1fr 1fr;
    margin-top: 4px;
}}
.lbl-x {{
    text-align: center;
    font-family: ui-monospace, monospace;
    font-size: 10px;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    padding-top: 8px;
}}

/* Tabela */
table {{
    width: 100%;
    border-collapse: collapse;
    margin: 16px 0;
    font-size: 13px;
}}
th, td {{
    text-align: left;
    padding: 10px 12px;
    border-bottom: 1px solid rgba(31,36,33, 0.15);
    vertical-align: top;
}}
th {{
    font-weight: 600;
    font-family: ui-monospace, monospace;
    font-size: 11px;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    background: #E8E1D2;
    border-bottom: 2px solid var(--linha);
}}
code {{ font-family: ui-monospace, monospace; font-size: 12px; background: rgba(0,0,0,0.05); padding: 2px 5px; border-radius: 3px; }}
.pill {{
    color: white;
    padding: 2px 8px;
    border-radius: 999px;
    font-size: 11px;
    font-weight: 600;
}}
.ext-pill {{
    font-size: 11px;
    font-family: ui-monospace, monospace;
    color: rgba(31,36,33, 0.75);
    line-height: 1.6;
}}
.cob-pill {{
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 11px;
    font-weight: 600;
}}
.cob-pill.cob-alta {{ background: #5E8A6B; color: white; }}
.cob-pill.cob-media {{ background: #D9A547; color: white; }}
.cob-pill.cob-baixa {{ background: #B85454; color: white; }}
.cob-pill.cob-na {{ background: rgba(0,0,0,0.1); color: rgba(0,0,0,0.4); font-style: italic; }}
.just {{ font-size: 12px; color: rgba(31,36,33, 0.7); max-width: 350px; }}

footer {{ margin-top: 64px; padding-top: 24px; border-top: 1px solid rgba(0,0,0,0.1); font-size: 12px; color: rgba(0,0,0,0.5); font-family: ui-monospace, monospace; }}
</style>
</head>
<body>
<div class="container">
  <div class="sub">PARECER · CHASSI DE CONTROLES INTERNOS · 2026.Q1</div>
  <h1>Nine-box: <em>impacto × controles</em></h1>
  <p>Banco Modelo S.A. · {len(consolidado)} grandes temas de risco identificados ·
  classificação derivada de {sum(r['n_apontamentos'] for r in consolidado)} apontamentos
  e {sum(r['n_kris'] for r in consolidado)} indicadores.</p>

  <h2>Distribuição</h2>
  <div class="ninebox">
    <div class="lbl-axis">Impacto (inerente)</div>
    <div class="grid">
      {grid}
    </div>
  </div>
  <div class="lbl-x-row">
    <div></div><div></div>
    <div class="lbl-x">Crítico</div>
    <div class="lbl-x">Atenção</div>
    <div class="lbl-x">Ok</div>
  </div>
  <div style="text-align:center; font-family:ui-monospace,monospace; font-size:10px; letter-spacing:0.2em; text-transform:uppercase; margin-top:12px; color:rgba(0,0,0,0.6);">Ambiente de controles →</div>

  <div class="legenda-ninebox">
    <div class="leg-bloco">
      <div class="leg-titulo">Quadrante</div>
      <div class="leg-itens">
        <div class="leg-item"><span class="leg-quad q-red"></span><span>Crítico (−)</span></div>
        <div class="leg-item"><span class="leg-quad q-yellow"></span><span>Atenção (0)</span></div>
        <div class="leg-item"><span class="leg-quad q-green"></span><span>Ok (+)</span></div>
      </div>
    </div>
    <div class="leg-bloco">
      <div class="leg-titulo">Cobertura (tamanho da bolha)</div>
      <div class="leg-itens">
        <div class="leg-item"><span class="leg-bolha leg-pq"></span><span>Alta (≥70%)</span></div>
        <div class="leg-item"><span class="leg-bolha leg-md"></span><span>Média</span></div>
        <div class="leg-item"><span class="leg-bolha leg-gd"></span><span>Baixa (&lt;40%)</span></div>
        <div class="leg-item"><span class="leg-bolha leg-na"></span><span>n/a (não opera)</span></div>
      </div>
    </div>
  </div>

  <h2>Detalhamento por R0</h2>
  <table>
    <thead>
      <tr>
        <th>ID</th><th>Risco</th><th>Controles</th><th>Impacto</th><th>Cobertura</th>
        <th>Apont. abertos/total</th><th>KRIs V/A/total</th><th>Sinais externos</th><th>Justificativa</th>
      </tr>
    </thead>
    <tbody>
      {tabela_rows}
    </tbody>
  </table>

  <p style="font-size: 12px; color: rgba(0,0,0,0.55); margin-top: 16px;">
    Cobertura mede a proporção de riscos declarados nos processos do banco que
    receberam algum sinal (apontamento, KRI, monitoramento, autoavaliação,
    auditoria, sinal externo) nos últimos 12 meses. Bolha pequena = ambiente
    validado; bolha grande = riscos declarados sem nenhum sinal (ponto cego).
  </p>

  <footer>
    Gerado em {dt.datetime.now().strftime('%d/%m/%Y %H:%M')} ·
    Catálogo: chassiro-api.fly.dev ·
    Código MIT, dados CC BY 4.0
  </footer>
</div>
</body>
</html>
"""


# ============================================================
# Geração do parecer Markdown
# ============================================================


def gerar_parecer_md(consolidado: list[dict]) -> str:
    """Gera parecer estruturado em Markdown."""
    meses = ["", "janeiro", "fevereiro", "março", "abril", "maio", "junho",
             "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]
    h = dt.date.today()
    hoje = f"{h.day} de {meses[h.month]} de {h.year}"
    total = len(consolidado)

    # Quadrantes críticos
    criticos = [r for r in consolidado if r["classe_impacto"] == "alto" and r["classe_controles"] == "vermelho"]
    atencao = [r for r in consolidado if (r["classe_impacto"] == "alto" and r["classe_controles"] == "amarelo")
               or (r["classe_impacto"] == "medio" and r["classe_controles"] == "vermelho")]
    confortaveis = [r for r in consolidado if r["classe_impacto"] in ("baixo", "medio") and r["classe_controles"] == "verde"]

    # Contadores de cobertura (ignorando R0 sem declarações)
    def _cob_num(r):
        v = r.get("cobertura_pct")
        if v == "n/a" or v is None or v == "":
            return None
        try:
            return float(v)
        except ValueError:
            return None

    n_cob_alta = sum(1 for r in consolidado if (_cob_num(r) or -1) >= 70)
    n_cob_media = sum(1 for r in consolidado if (c := _cob_num(r)) is not None and 40 <= c < 70)
    n_cob_baixa = sum(1 for r in consolidado if (c := _cob_num(r)) is not None and c < 40)
    n_sem_decl = sum(1 for r in consolidado if _cob_num(r) is None)
    # Riscos sub-monitorados: cobertura baixa E há declarações nos processos
    riscos_submonitorados = [
        r for r in consolidado
        if (c := _cob_num(r)) is not None
        and c < 40
        and int(r.get("n_riscos_declarados", 0)) > 0
    ]
    total_decl_sem_sinal = sum(int(r.get("n_riscos_sem_sinal", 0)) for r in consolidado)

    md = f"""# Parecer de Controles Internos — Banco Modelo S.A.
## Ciclo 2026.Q1

Data: {hoje}

---

## 1. Sumário executivo

Foram analisados **{total} grandes temas de risco** (R0) presentes no Chassi de
Controles Internos, com base em (1) **fontes internas** — apontamentos de
auditoria, indicadores de risco (KRIs), autoavaliação das áreas, plano anual
de auditoria, BIA de continuidade, monitoramento de 2ª linha — e (2) **fontes
externas públicas** — procedentes BACEN, processos sancionadores CVM SAS,
sanções ANBIMA, Procon, mídia adversa e Reclame Aqui — e (3) **calibração
interna** — materialidade aprovada pela casa para cada risco.

A classificação combinada (impacto inerente × ambiente de controles) revela:

- **{len(criticos)} risco(s) em quadrante crítico** (alto impacto + controles vermelhos)
- **{len(atencao)} risco(s) em zona de atenção** (alto impacto + amarelo, ou médio + vermelho)
- **{len(confortaveis)} risco(s) em zona confortável** (impacto não-alto + controles verdes)

A análise da **cobertura** (% de riscos declarados nos processos do banco que
receberam algum sinal — apontamento, KRI, autoavaliação, monitoramento de 2ª
linha, auditoria, BACEN procedente, mídia adversa — nos últimos 12 meses)
evidencia:

- **{n_cob_alta} risco(s) com cobertura alta** (≥70%) — ambiente validado
- **{n_cob_media} risco(s) com cobertura média** (40-70%) — monitorado parcialmente
- **{n_cob_baixa} risco(s) com cobertura baixa** (<40%) — ambiente sub-monitorado
- **{n_sem_decl} risco(s) sem declarações** — núcleo não opera no banco ou ainda não mapeado
- **{total_decl_sem_sinal} risco(s) declarado(s) em processos** sem nenhum sinal nos últimos 12 meses — necessitam priorização no plano de avaliação

"""

    if criticos:
        md += "## 2. Riscos em quadrante crítico\n\nRequer ação imediata e visibilidade no comitê de risco:\n\n"
        for r in criticos:
            md += f"### {r['r0_id']} — {r['r0_nome']}\n\n"
            md += f"- **Áreas envolvidas**: {r['areas_envolvidas']}\n"
            md += f"- **Apontamentos**: {r['n_apontamentos_abertos']} aberto(s) de {r['n_apontamentos']} totais"
            if r['n_apontamentos_regulador']:
                md += f", **{r['n_apontamentos_regulador']} de regulador (BCB/CVM)**"
            if r['n_apontamentos_criticos']:
                md += f", **{r['n_apontamentos_criticos']} de severidade crítica**"
            md += "\n"
            md += f"- **KRIs**: {r['n_kris_vermelho']} vermelho(s), {r['n_kris_amarelo']} amarelo(s) de {r['n_kris']} totais\n"
            # Sinais externos
            ext = []
            if int(r.get("n_bacen_procedente", 0)) > 0:
                ext.append(f"{r['n_bacen_procedente']} procedente(s) BACEN")
            if int(r.get("n_cvm_julgado", 0)) > 0:
                ext.append(f"{r['n_cvm_julgado']} processo(s) CVM julgado(s)")
            if int(r.get("n_cvm_em_curso", 0)) > 0:
                ext.append(f"{r['n_cvm_em_curso']} processo(s) CVM em curso")
            if int(r.get("n_procon_procedente", 0)) > 0:
                ext.append(f"{r['n_procon_procedente']} procedente(s) Procon")
            n_anb = int(r.get("n_anbima_carta", 0)) + int(r.get("n_anbima_termo", 0)) + int(r.get("n_anbima_julgamento", 0))
            if n_anb > 0:
                detalhes_anb = []
                if int(r.get("n_anbima_carta", 0)) > 0:
                    detalhes_anb.append(f"{r['n_anbima_carta']} carta(s)")
                if int(r.get("n_anbima_termo", 0)) > 0:
                    detalhes_anb.append(f"{r['n_anbima_termo']} termo(s)")
                if int(r.get("n_anbima_julgamento", 0)) > 0:
                    detalhes_anb.append(f"{r['n_anbima_julgamento']} julgamento(s)")
                ext.append(f"ANBIMA: {' + '.join(detalhes_anb)}")
            if int(r.get("n_midia_alta_severidade", 0)) > 0:
                ext.append(f"{r['n_midia_alta_severidade']} mídia(s) alta severidade")
            if ext:
                md += f"- **Sinais externos**: {', '.join(ext)}\n"
            md += f"- **Score de controles**: {r['score_controles']:.1f}/10 ({r['classe_controles']})\n"
            md += f"- **Score de impacto**: {r['score_impacto']:.1f}/5 ({r['classe_impacto']}) — materialidade {'interna' if r.get('tem_materialidade_interna') == 'sim' else 'default chassi (fallback)'}\n"
            cob_raw = r.get('cobertura_pct')
            if cob_raw == "n/a":
                md += f"- **Cobertura**: n/a — {r.get('cobertura_fonte', '?')}\n"
            else:
                cob = float(cob_raw)
                cob_label = "alta" if cob >= 70 else "média" if cob >= 40 else "baixa"
                md += f"- **Cobertura**: {cob_label} ({cob:.0f}%) — {r.get('cobertura_fonte', '?')}\n"
            md += f"- **Justificativa controles**: {r['justificativa_controles']}\n"
            md += f"- **Justificativa impacto**: {r['justificativa_impacto']}\n\n"

    if atencao:
        md += "## 3. Riscos em zona de atenção\n\nMonitoramento próximo e plano de ação no horizonte de 90-180 dias:\n\n"
        # Substituir | das areas_envolvidas por · pra não quebrar a tabela markdown
        md += "| Risco | Áreas | Apont. | KRIs V/A | Externos | C / I |\n"
        md += "|-------|-------|--------|----------|----------|-------|\n"
        for r in atencao:
            areas_safe = r['areas_envolvidas'][:60].replace('|', '·')
            ext_short = []
            if int(r.get("n_bacen_procedente", 0)) > 0:
                ext_short.append(f"BCB {r['n_bacen_procedente']}")
            n_cvm_at = int(r.get("n_cvm_julgado", 0)) + int(r.get("n_cvm_em_curso", 0))
            if n_cvm_at > 0:
                ext_short.append(f"CVM {n_cvm_at}")
            if int(r.get("n_procon_procedente", 0)) > 0:
                ext_short.append(f"Procon {r['n_procon_procedente']}")
            n_anb_at = int(r.get("n_anbima_carta", 0)) + int(r.get("n_anbima_termo", 0)) + int(r.get("n_anbima_julgamento", 0))
            if n_anb_at > 0:
                ext_short.append(f"ANBIMA {n_anb_at}")
            if int(r.get("n_midia_alta_severidade", 0)) > 0:
                ext_short.append(f"Mídia {r['n_midia_alta_severidade']}")
            ext_cell = ", ".join(ext_short) if ext_short else "—"
            md += f"| **{r['r0_id']}** {r['r0_nome']} | {areas_safe} | {r['n_apontamentos_abertos']}/{r['n_apontamentos']} | {r['n_kris_vermelho']}/{r['n_kris_amarelo']} | {ext_cell} | {r['score_controles']:.1f} / {r['score_impacto']:.1f} |\n"
        md += "\n"

    if confortaveis:
        md += "## 4. Riscos em zona confortável\n\nAmbiente adequado, manter monitoramento padrão:\n\n"
        for r in confortaveis:
            areas_safe = r['areas_envolvidas'].replace('|', '·').strip()
            if not areas_safe:
                areas_safe = "_sem ocorrências internas — apenas materialidade atribuída_"
            md += f"- **{r['r0_id']}** {r['r0_nome']} ({areas_safe})\n"
        md += "\n"

    # ==== Seção 5: Alertas de cobertura ====
    if riscos_submonitorados:
        md += "## 5. Alertas de cobertura\n\n"
        md += (
            f"Há **{total_decl_sem_sinal} risco(s) declarado(s)** em processos do banco "
            f"que NÃO receberam nenhum sinal (apontamento, KRI, monitoramento, autoavaliação, "
            f"auditoria, sinal externo) nos últimos 12 meses. Isso significa que esses "
            f"riscos foram identificados como relevantes pelas áreas, mas não foram "
            f"efetivamente avaliados — são pontos cegos do ambiente de controles.\n\n"
        )
        md += "Os R0 mais sub-monitorados (cobertura <40% e com riscos declarados):\n\n"
        for r in riscos_submonitorados[:15]:
            decl = int(r.get("n_riscos_declarados", 0))
            avaliados = int(r.get("n_riscos_avaliados", 0))
            md += (
                f"- **{r['r0_id']}** {r['r0_nome']}: {avaliados}/{decl} riscos avaliados "
                f"({float(r.get('cobertura_pct', 0)):.0f}% cobertura)"
            )
            sem_sinal = r.get("riscos_sem_sinal_detalhe", "")
            if sem_sinal:
                md += f"\n  - Sem sinal: {sem_sinal}"
            md += "\n"
        md += "\n"

    md += """## 6. Recomendações

1. Para os riscos em quadrante crítico: alocar tratamento imediato com responsável
   nomeado pelo CRO, status reportado semanalmente até remediação.
2. Para os riscos em zona de atenção: incluir em pauta do próximo comitê
   de risco operacional e definir cronograma de remediação até final de Q2/2026.
3. Para os riscos em zona confortável: manter cobertura nos ciclos regulares de
   autoavaliação e auditoria.
4. Para os riscos sub-monitorados (cobertura baixa): priorizar inclusão no plano
   anual de auditoria, em monitoramento contínuo de 2ª linha, ou na próxima rodada
   de autoavaliação.

## 7. Metodologia

**Score de controles** (eixo X do nine-box) combina:
- **Apontamentos internos** abertos, com peso por severidade (Crítico 4, Alto 2, Médio 1, Baixo 0.5). Apontamentos de **regulador** (BCB/CVM) têm peso dobrado.
- **KRIs**: Vermelho 3, Amarelo 1. Penalidade adicional de 1 ponto por KRI com tendência de piora nos últimos 6 meses.
- **Eficácia autoavaliada** das áreas (escala 1-5). Eficácia 5 reduz score, eficácia 1 aumenta.
- **Procedentes BACEN** (peso 0.5 cada, cap 6). Penalidade adicional de 1.5 quando há tendência de piora vs. trimestre anterior.
- **CVM SAS** (regulador estatal — peso alto): processo julgado com penalidade contribui 2.0 cada; em curso 1.0 cada. Cap 6.0.
- **ANBIMA** (autorregulador — peso médio): Carta de Recomendação 0.3 cada, Termo de Compromisso 0.5 cada, Julgamento 1.5 cada. Cap 3.0.
- **Procon procedente** (peso 0.3 cada, cap 3).
- **Mídia adversa**: severidade ≥4 contribui 1.0 cada; severidade 3 contribui 0.4. Cap 4.
- **Reclame Aqui**: queda de 0.5+ na nota geral nos últimos 3 meses penaliza até 2 pontos. Nota absoluta <6.5 penaliza 1.

Escala 0-10. Verde <3, amarelo 3-6, vermelho ≥6.

**Score de impacto** (eixo Y do nine-box):
- **Materialidade interna** atribuída pela casa (CRO, Comitê de Risco) tem **peso dobrado** e prevalece.
- **Materialidade default do chassi** entra como fallback documentado quando a casa ainda não atribuiu materialidade interna.
- **Criticidade BIA** (sinal indireto para riscos universais).
- **Impacto autoavaliado** pelas áreas.

Escala 1-5. Baixo <2.5, médio 2.5-4, alto ≥4.

**Cobertura** (3ª dimensão do modelo):
- A cobertura mede **% de riscos declarados nos processos do banco que receberam algum sinal** nos últimos 12 meses.
- O denominador vem da planilha `riscos_declarados.csv`: declaração interna do banco, "no processo P, identificamos os riscos R₁, R₂, ..." (cada área dona declara). Áreas que não operam um núcleo (ex: seguros) não declaram nada para esses processos.
- O numerador vem do conjunto de TODAS as fontes: apontamentos, KRIs, autoavaliações, monitoramento de 2ª linha, plano de auditoria, BACEN procedente, Procon, mídia adversa. Se um risco declarado aparece em qualquer uma delas, conta como "avaliado".
- Cobertura por R0 = média ponderada das coberturas dos processos onde o R0 (ou seus filhos R1) foram declarados.
- A cobertura modula o score de controles: cobertura baixa + zero sinais = "ambiente desconhecido" (score sobe +2), em vez de assumir "ambiente bom".
- O nine-box reflete a cobertura no **tamanho da bolha**: bolhas pequenas = alta cobertura validada; bolhas grandes = baixa cobertura (riscos declarados sem nenhuma análise).

**Tradução de taxonomia** interna para IDs canônicos via `mapa_taxonomia.csv`.

---

*Parecer gerado automaticamente pelo pipeline ChassiRO em {hora}.*
*Catálogo regulatório: github.com/walterCNeto/ChassiRO · API: chassiro-api.fly.dev*
""".replace("{hora}", dt.datetime.now().strftime("%d/%m/%Y %H:%M"))

    return md


# ============================================================
# Entry point
# ============================================================


def main():
    parser = argparse.ArgumentParser(description="Pipeline de análise ChassiRO")
    parser.add_argument("--demo-dir", type=Path, default=Path("demo"),
                        help="Diretório com os 6 CSVs (default: demo)")
    parser.add_argument("--out-dir", type=Path, default=Path("output"),
                        help="Diretório de saída (default: output)")
    parser.add_argument("--offline", action="store_true",
                        help="Usa snapshot local em vez da API")
    parser.add_argument("--snapshot", type=str, default=None,
                        help="Caminho pro chassi.json (modo offline)")
    args = parser.parse_args()

    consolidar(args.demo_dir, args.out_dir, args.offline, args.snapshot)


if __name__ == "__main__":
    main()

"""
Loader do snapshot do Chassi.

Carrega `chassi.json` em memória no startup e expõe estruturas indexadas
para lookups O(1) por id, e índices auxiliares para filtros frequentes.

O loader procura o snapshot em três caminhos (na ordem):
  1. variável de ambiente CHASSI_SNAPSHOT_PATH (se definida)
  2. ./chassi.json (relativo ao cwd)
  3. ../backend/chassi.json (quando rodando de api/)

Se nenhum encontrado, levanta FileNotFoundError com mensagem clara.
"""

from __future__ import annotations

import json
import os
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


SNAPSHOT_CANDIDATES = [
    lambda: os.environ.get("CHASSI_SNAPSHOT_PATH"),
    lambda: "chassi.json",
    lambda: "../backend/chassi.json",
    lambda: "backend/chassi.json",
    lambda: "/app/chassi.json",
]


@dataclass
class Chassi:
    """Snapshot do catálogo carregado em memória, com índices."""

    # Metadados
    metadata: dict[str, Any] = field(default_factory=dict)
    version: str = ""
    released_at: str = ""

    # Tabelas brutas (listas de dicts, idênticas ao JSON)
    reguladores: list[dict] = field(default_factory=list)
    tipos_entidade: list[dict] = field(default_factory=list)
    tipo_entidade_regulador: list[dict] = field(default_factory=list)
    segmentos: list[dict] = field(default_factory=list)
    atividades_canonicas: list[dict] = field(default_factory=list)
    processos: list[dict] = field(default_factory=list)
    riscos: list[dict] = field(default_factory=list)
    normas: list[dict] = field(default_factory=list)
    norma_artigos: list[dict] = field(default_factory=list)
    norma_aplicabilidade_tipo_entidade: list[dict] = field(default_factory=list)
    norma_aplicabilidade_segmento: list[dict] = field(default_factory=list)
    norma_aplicabilidade_atividade: list[dict] = field(default_factory=list)
    vinculo_norma_processo: list[dict] = field(default_factory=list)
    vinculo_norma_risco: list[dict] = field(default_factory=list)
    vinculo_processo_risco: list[dict] = field(default_factory=list)
    chassi_versions: list[dict] = field(default_factory=list)
    chassi_changelog: list[dict] = field(default_factory=list)

    # Índices por id (para lookups rápidos)
    regulador_by_id: dict[str, dict] = field(default_factory=dict)
    tipo_entidade_by_id: dict[str, dict] = field(default_factory=dict)
    segmento_by_id: dict[str, dict] = field(default_factory=dict)
    atividade_by_id: dict[str, dict] = field(default_factory=dict)
    processo_by_id: dict[str, dict] = field(default_factory=dict)
    risco_by_id: dict[str, dict] = field(default_factory=dict)
    norma_by_id: dict[str, dict] = field(default_factory=dict)

    # Índices auxiliares
    artigos_by_norma: dict[str, list[dict]] = field(default_factory=dict)
    aplic_tipo_by_norma: dict[str, set[str]] = field(default_factory=dict)
    aplic_segmento_by_norma: dict[str, set[str]] = field(default_factory=dict)
    aplic_atividade_by_norma: dict[str, set[str]] = field(default_factory=dict)
    vinculos_processo_by_norma: dict[str, list[dict]] = field(default_factory=dict)
    vinculos_norma_by_processo: dict[str, list[dict]] = field(default_factory=dict)
    vinculos_risco_by_norma: dict[str, list[dict]] = field(default_factory=dict)
    vinculos_norma_by_risco: dict[str, list[dict]] = field(default_factory=dict)
    vinculos_risco_by_processo: dict[str, list[dict]] = field(default_factory=dict)
    vinculos_processo_by_risco: dict[str, list[dict]] = field(default_factory=dict)
    children_by_processo: dict[str | None, list[dict]] = field(default_factory=dict)
    children_by_risco: dict[str | None, list[dict]] = field(default_factory=dict)

    @classmethod
    def load(cls, path: str | Path | None = None) -> "Chassi":
        """Carrega o snapshot do disco e constrói índices."""
        snapshot_path = _resolve_snapshot_path(path)
        with open(snapshot_path, encoding="utf-8") as f:
            raw = json.load(f)

        c = cls()
        c.metadata = raw.get("_metadata", {})
        c.version = c.metadata.get("version", "")
        c.released_at = c.metadata.get("released_at", "")

        for key in [
            "reguladores",
            "tipos_entidade",
            "tipo_entidade_regulador",
            "segmentos",
            "atividades_canonicas",
            "processos",
            "riscos",
            "normas",
            "norma_artigos",
            "norma_aplicabilidade_tipo_entidade",
            "norma_aplicabilidade_segmento",
            "norma_aplicabilidade_atividade",
            "vinculo_norma_processo",
            "vinculo_norma_risco",
            "vinculo_processo_risco",
            "chassi_versions",
            "chassi_changelog",
        ]:
            setattr(c, key, raw.get(key, []))

        c._build_indexes()
        return c

    def _build_indexes(self) -> None:
        # Lookups por id
        self.regulador_by_id = {r["id"]: r for r in self.reguladores}
        self.tipo_entidade_by_id = {t["id"]: t for t in self.tipos_entidade}
        self.segmento_by_id = {s["id"]: s for s in self.segmentos}
        self.atividade_by_id = {a["id"]: a for a in self.atividades_canonicas}
        self.processo_by_id = {p["id"]: p for p in self.processos}
        self.risco_by_id = {r["id"]: r for r in self.riscos}
        self.norma_by_id = {n["id"]: n for n in self.normas}

        # Índices auxiliares
        artigos: dict[str, list[dict]] = defaultdict(list)
        for a in self.norma_artigos:
            artigos[a["norma_id"]].append(a)
        self.artigos_by_norma = dict(artigos)

        aplic_tipo: dict[str, set[str]] = defaultdict(set)
        for r in self.norma_aplicabilidade_tipo_entidade:
            aplic_tipo[r["norma_id"]].add(r["tipo_entidade_id"])
        self.aplic_tipo_by_norma = dict(aplic_tipo)

        aplic_seg: dict[str, set[str]] = defaultdict(set)
        for r in self.norma_aplicabilidade_segmento:
            aplic_seg[r["norma_id"]].add(r["segmento_id"])
        self.aplic_segmento_by_norma = dict(aplic_seg)

        aplic_ativ: dict[str, set[str]] = defaultdict(set)
        for r in self.norma_aplicabilidade_atividade:
            aplic_ativ[r["norma_id"]].add(r["atividade_id"])
        self.aplic_atividade_by_norma = dict(aplic_ativ)

        vnp: dict[str, list[dict]] = defaultdict(list)
        vnp_rev: dict[str, list[dict]] = defaultdict(list)
        for v in self.vinculo_norma_processo:
            vnp[v["norma_id"]].append(v)
            vnp_rev[v["processo_id"]].append(v)
        self.vinculos_processo_by_norma = dict(vnp)
        self.vinculos_norma_by_processo = dict(vnp_rev)

        vnr: dict[str, list[dict]] = defaultdict(list)
        vnr_rev: dict[str, list[dict]] = defaultdict(list)
        for v in self.vinculo_norma_risco:
            vnr[v["norma_id"]].append(v)
            vnr_rev[v["risco_id"]].append(v)
        self.vinculos_risco_by_norma = dict(vnr)
        self.vinculos_norma_by_risco = dict(vnr_rev)

        vpr: dict[str, list[dict]] = defaultdict(list)
        vpr_rev: dict[str, list[dict]] = defaultdict(list)
        for v in self.vinculo_processo_risco:
            vpr[v["processo_id"]].append(v)
            vpr_rev[v["risco_id"]].append(v)
        self.vinculos_risco_by_processo = dict(vpr)
        self.vinculos_processo_by_risco = dict(vpr_rev)

        # Hierarquia (children_of)
        ch_p: dict[str | None, list[dict]] = defaultdict(list)
        for p in self.processos:
            ch_p[p.get("parent_id")].append(p)
        self.children_by_processo = dict(ch_p)

        ch_r: dict[str | None, list[dict]] = defaultdict(list)
        for r in self.riscos:
            ch_r[r.get("parent_id")].append(r)
        self.children_by_risco = dict(ch_r)


def _resolve_snapshot_path(explicit: str | Path | None) -> Path:
    if explicit:
        p = Path(explicit)
        if p.is_file():
            return p
        raise FileNotFoundError(f"Snapshot indicado nao encontrado: {p}")

    for getter in SNAPSHOT_CANDIDATES:
        candidate = getter()
        if not candidate:
            continue
        p = Path(candidate)
        if p.is_file():
            return p

    raise FileNotFoundError(
        "chassi.json nao encontrado. Defina CHASSI_SNAPSHOT_PATH ou rode "
        "`make export-json` em backend/ para gera-lo."
    )

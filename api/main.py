"""
Chassi de Controles Internos - API REST.

API leve e idempotente sobre o snapshot estatico do catalogo regulatorio.
Carrega `chassi.json` em memoria no startup; sem dependencia de banco de
dados em runtime.

Para rodar local:
    uvicorn api.main:app --reload --port 8000

Para producao:
    uvicorn api.main:app --host 0.0.0.0 --port $PORT --workers 2
"""

from __future__ import annotations

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse

from .loader import Chassi
from .schemas import (
    AtividadeCanonica,
    ChassiStats,
    ChassiVersion,
    HTTPError,
    InstanciaInput,
    InstanciaOutput,
    Norma,
    NormaDetalhe,
    Processo,
    ProcessoDetalhe,
    Regulador,
    Risco,
    RiscoDetalhe,
    Segmento,
    TipoEntidade,
    VinculoNormaProcesso,
    VinculoNormaRisco,
    VinculoProcessoRisco,
)


# ============================================================
# Lifespan: carrega o snapshot uma unica vez no startup
# ============================================================


@asynccontextmanager
async def lifespan(app: FastAPI):
    snapshot_path = os.environ.get("CHASSI_SNAPSHOT_PATH")
    chassi = Chassi.load(snapshot_path)
    app.state.chassi = chassi
    print(
        f"[chassi-api] Snapshot carregado: v{chassi.version} "
        f"({len(chassi.normas)} normas, "
        f"{len(chassi.processos)} processos, "
        f"{len(chassi.riscos)} riscos)"
    )
    yield


app = FastAPI(
    title="Chassi de Controles Internos - API",
    description=(
        "API leve e idempotente sobre o catalogo regulatorio versionado e "
        "colaborativo do Chassi de Controles Internos. "
        "Codigo MIT, conteudo CC BY 4.0. "
        "Repositorio: https://github.com/walterCNeto/ChassiRO"
    ),
    version="0.1.0",
    lifespan=lifespan,
    contact={
        "name": "Walter C. Neto",
        "url": "https://waltercneto.github.io/",
        "email": "walter.correa.neto@gmail.com",
    },
    license_info={
        "name": "MIT (code) + CC BY 4.0 (data)",
        "url": "https://github.com/walterCNeto/ChassiRO",
    },
)


# CORS aberto - dados publicos
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


def _chassi() -> Chassi:
    return app.state.chassi


# ============================================================
# Root e health
# ============================================================


@app.get("/", include_in_schema=False)
async def root():
    return JSONResponse(
        {
            "name": "Chassi de Controles Internos - API",
            "version": _chassi().version,
            "docs": "/docs",
            "openapi": "/openapi.json",
            "repo": "https://github.com/walterCNeto/ChassiRO",
            "site": "https://waltercneto.github.io/ChassiRO/",
        }
    )


@app.get("/health", include_in_schema=False)
async def health():
    c = _chassi()
    return {
        "status": "ok",
        "version": c.version,
        "released_at": c.released_at,
        "counts": {
            "normas": len(c.normas),
            "processos": len(c.processos),
            "riscos": len(c.riscos),
        },
    }


# ============================================================
# Catalogos basicos
# ============================================================


@app.get(
    "/v1/reguladores",
    response_model=list[Regulador],
    tags=["Catalogos"],
    summary="Lista reguladores",
)
async def list_reguladores():
    return _chassi().reguladores


@app.get(
    "/v1/reguladores/{regulador_id}",
    response_model=Regulador,
    tags=["Catalogos"],
    responses={404: {"model": HTTPError}},
)
async def get_regulador(regulador_id: str):
    item = _chassi().regulador_by_id.get(regulador_id)
    if not item:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Regulador nao encontrado")
    return item


@app.get(
    "/v1/tipos-entidade",
    response_model=list[TipoEntidade],
    tags=["Catalogos"],
    summary="Lista tipos de entidade",
)
async def list_tipos_entidade(
    grupo: str | None = Query(
        None, description="Filtra por grupo (bancario, mercado_capitais, ...)"
    ),
):
    items = _chassi().tipos_entidade
    if grupo:
        items = [t for t in items if t.get("grupo") == grupo]
    return items


@app.get(
    "/v1/tipos-entidade/{tipo_id}",
    response_model=TipoEntidade,
    tags=["Catalogos"],
    responses={404: {"model": HTTPError}},
)
async def get_tipo_entidade(tipo_id: str):
    item = _chassi().tipo_entidade_by_id.get(tipo_id)
    if not item:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Tipo de entidade nao encontrado")
    return item


@app.get(
    "/v1/segmentos",
    response_model=list[Segmento],
    tags=["Catalogos"],
    summary="Lista segmentos prudenciais",
)
async def list_segmentos(
    regulador: str | None = Query(None, description="Filtra por regulador (REG_BCB, REG_SUSEP)")
):
    items = _chassi().segmentos
    if regulador:
        items = [s for s in items if s.get("regulador_id") == regulador]
    return items


@app.get(
    "/v1/atividades",
    response_model=list[AtividadeCanonica],
    tags=["Catalogos"],
    summary="Lista atividades canonicas",
)
async def list_atividades(
    grupo: str | None = Query(
        None, description="Filtra por grupo (captacao, credito, cambio, ...)"
    ),
):
    items = _chassi().atividades_canonicas
    if grupo:
        items = [a for a in items if a.get("grupo") == grupo]
    return items


# ============================================================
# Normas
# ============================================================


@app.get(
    "/v1/normas",
    response_model=list[Norma],
    tags=["Normas"],
    summary="Lista normas com filtros opcionais",
)
async def list_normas(
    aplica_a: str | None = Query(
        None, description="ID do tipo de entidade. Filtra normas aplicaveis."
    ),
    segmento: str | None = Query(
        None, description="ID do segmento. Filtra normas aplicaveis."
    ),
    atividade: str | None = Query(
        None, description="ID da atividade. Filtra normas aplicaveis."
    ),
    regulador: str | None = Query(
        None, description="ID do regulador. Filtra por origem da norma."
    ),
    status_: str | None = Query(
        "vigente", alias="status", description="Status (vigente, revogada, ...). Default: vigente"
    ),
    tipo: str | None = Query(
        None, description="Tipo da norma (lei, res_cmn, circ_bcb, ...)"
    ),
    busca: str | None = Query(
        None, description="Busca textual na ementa/titulo (case-insensitive)"
    ),
):
    c = _chassi()
    out = []
    busca_lc = busca.lower() if busca else None

    for n in c.normas:
        # Filtro por status
        if status_ and n.get("status") != status_:
            continue
        # Filtro por regulador
        if regulador and n.get("regulador_id") != regulador:
            continue
        # Filtro por tipo
        if tipo and n.get("tipo") != tipo:
            continue
        # Filtro por aplicabilidade tipo_entidade
        if aplica_a:
            tipos_norma = c.aplic_tipo_by_norma.get(n["id"], set())
            if tipos_norma and aplica_a not in tipos_norma:
                continue
        # Filtro por segmento
        if segmento:
            segs_norma = c.aplic_segmento_by_norma.get(n["id"], set())
            if segs_norma and segmento not in segs_norma:
                continue
        # Filtro por atividade
        if atividade:
            ativs_norma = c.aplic_atividade_by_norma.get(n["id"], set())
            if ativs_norma and atividade not in ativs_norma:
                continue
        # Busca textual
        if busca_lc:
            haystack = " ".join(
                str(x).lower()
                for x in [n.get("titulo"), n.get("ementa"), n.get("numero")]
                if x
            )
            if busca_lc not in haystack:
                continue
        out.append(n)

    return out


@app.get(
    "/v1/normas/{norma_id}",
    response_model=NormaDetalhe,
    tags=["Normas"],
    responses={404: {"model": HTTPError}},
    summary="Detalhe de uma norma com vinculos e aplicabilidade",
)
async def get_norma(norma_id: str):
    c = _chassi()
    n = c.norma_by_id.get(norma_id)
    if not n:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Norma nao encontrada")
    return {
        **n,
        "artigos": c.artigos_by_norma.get(norma_id, []),
        "aplicabilidade_tipo_entidade": sorted(c.aplic_tipo_by_norma.get(norma_id, set())),
        "aplicabilidade_segmento": sorted(c.aplic_segmento_by_norma.get(norma_id, set())),
        "aplicabilidade_atividade": sorted(c.aplic_atividade_by_norma.get(norma_id, set())),
        "vinculos_processo": c.vinculos_processo_by_norma.get(norma_id, []),
        "vinculos_risco": c.vinculos_risco_by_norma.get(norma_id, []),
    }


# ============================================================
# Processos
# ============================================================


@app.get(
    "/v1/processos",
    response_model=list[Processo],
    tags=["Processos"],
    summary="Lista processos",
)
async def list_processos(
    nucleo: str | None = Query(None, description="Nucleo (U, B, MC, S, P, C, CG)"),
    nivel_max: int | None = Query(None, ge=0, le=4, description="Nivel maximo (0-4)"),
    parent: str | None = Query(None, description="Filtra filhos diretos de um parent_id"),
):
    out = _chassi().processos
    if nucleo:
        out = [p for p in out if p.get("nucleo") == nucleo]
    if nivel_max is not None:
        out = [p for p in out if (p.get("nivel") or 0) <= nivel_max]
    if parent:
        out = [p for p in out if p.get("parent_id") == parent]
    return out


@app.get(
    "/v1/processos/{processo_id}",
    response_model=ProcessoDetalhe,
    tags=["Processos"],
    responses={404: {"model": HTTPError}},
    summary="Detalhe de um processo com filhos e vinculos",
)
async def get_processo(processo_id: str):
    c = _chassi()
    p = c.processo_by_id.get(processo_id)
    if not p:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Processo nao encontrado")
    return {
        **p,
        "children": c.children_by_processo.get(processo_id, []),
        "vinculos_norma": c.vinculos_norma_by_processo.get(processo_id, []),
        "vinculos_risco": c.vinculos_risco_by_processo.get(processo_id, []),
    }


# ============================================================
# Riscos
# ============================================================


@app.get(
    "/v1/riscos",
    response_model=list[Risco],
    tags=["Riscos"],
    summary="Lista riscos",
)
async def list_riscos(
    nucleo: str | None = Query(None, description="Nucleo (U, B, MC, S, P, C, CG)"),
    nivel_max: int | None = Query(None, ge=0, le=4),
    parent: str | None = Query(None, description="Filtra filhos diretos de um parent_id"),
    categoria: str | None = Query(None, description="categoria_basileia (credito, mercado, ...)"),
):
    out = _chassi().riscos
    if nucleo:
        out = [r for r in out if r.get("nucleo") == nucleo]
    if nivel_max is not None:
        out = [r for r in out if (r.get("nivel") or 0) <= nivel_max]
    if parent:
        out = [r for r in out if r.get("parent_id") == parent]
    if categoria:
        out = [r for r in out if r.get("categoria_basileia") == categoria]
    return out


@app.get(
    "/v1/riscos/{risco_id}",
    response_model=RiscoDetalhe,
    tags=["Riscos"],
    responses={404: {"model": HTTPError}},
    summary="Detalhe de um risco com filhos e vinculos",
)
async def get_risco(risco_id: str):
    c = _chassi()
    r = c.risco_by_id.get(risco_id)
    if not r:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Risco nao encontrado")
    return {
        **r,
        "children": c.children_by_risco.get(risco_id, []),
        "vinculos_norma": c.vinculos_norma_by_risco.get(risco_id, []),
        "vinculos_processo": c.vinculos_processo_by_risco.get(risco_id, []),
    }


# ============================================================
# Vinculos (lookups diretos)
# ============================================================


@app.get(
    "/v1/vinculos/norma-processo",
    response_model=list[VinculoNormaProcesso],
    tags=["Vinculos"],
    summary="Lista vinculos norma->processo",
)
async def list_vinc_norma_processo(
    norma: str | None = Query(None, description="Filtra por norma_id"),
    processo: str | None = Query(None, description="Filtra por processo_id"),
    tipo: str | None = Query(
        None, description="Filtra por tipo_vinculo (primaria, secundaria, informativa)"
    ),
):
    out = _chassi().vinculo_norma_processo
    if norma:
        out = [v for v in out if v.get("norma_id") == norma]
    if processo:
        out = [v for v in out if v.get("processo_id") == processo]
    if tipo:
        out = [v for v in out if v.get("tipo_vinculo") == tipo]
    return out


@app.get(
    "/v1/vinculos/norma-risco",
    response_model=list[VinculoNormaRisco],
    tags=["Vinculos"],
    summary="Lista vinculos norma->risco",
)
async def list_vinc_norma_risco(
    norma: str | None = Query(None),
    risco: str | None = Query(None),
    tipo: str | None = Query(None),
):
    out = _chassi().vinculo_norma_risco
    if norma:
        out = [v for v in out if v.get("norma_id") == norma]
    if risco:
        out = [v for v in out if v.get("risco_id") == risco]
    if tipo:
        out = [v for v in out if v.get("tipo_vinculo") == tipo]
    return out


@app.get(
    "/v1/vinculos/processo-risco",
    response_model=list[VinculoProcessoRisco],
    tags=["Vinculos"],
    summary="Lista vinculos processo->risco (matriz P x R)",
)
async def list_vinc_processo_risco(
    processo: str | None = Query(None),
    risco: str | None = Query(None),
    materialidade_min: int | None = Query(None, ge=1, le=5),
):
    out = _chassi().vinculo_processo_risco
    if processo:
        out = [v for v in out if v.get("processo_id") == processo]
    if risco:
        out = [v for v in out if v.get("risco_id") == risco]
    if materialidade_min is not None:
        out = [v for v in out if (v.get("materialidade_default") or 0) >= materialidade_min]
    return out


# ============================================================
# Instancia (a peca-chave: filtragem combinada por entidade)
# ============================================================


@app.post(
    "/v1/instancia",
    response_model=InstanciaOutput,
    tags=["Instancia"],
    summary="Retorna a fatia do catalogo aplicavel a uma entidade",
    description=(
        "Recebe os atributos categoricos da entidade (tipo, segmento, atividades) "
        "e devolve as normas, processos e riscos aplicaveis. "
        "**Nenhum dado e armazenado** - a chamada e idempotente e sem efeito colateral."
    ),
)
async def post_instancia(input: InstanciaInput):
    c = _chassi()

    # Valida ids
    if input.tipo_entidade not in c.tipo_entidade_by_id:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            f"tipo_entidade desconhecido: {input.tipo_entidade}",
        )
    if input.segmento and input.segmento not in c.segmento_by_id:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            f"segmento desconhecido: {input.segmento}",
        )
    for a in input.atividades:
        if a not in c.atividade_by_id:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                f"atividade desconhecida: {a}",
            )

    atividades = set(input.atividades)
    aplicaveis_normas: list[dict] = []

    for n in c.normas:
        if n.get("status") != "vigente":
            continue

        # Tipo de entidade
        tipos_norma = c.aplic_tipo_by_norma.get(n["id"], set())
        if tipos_norma and input.tipo_entidade not in tipos_norma:
            continue

        # Segmento (se fornecido)
        if input.segmento:
            segs_norma = c.aplic_segmento_by_norma.get(n["id"], set())
            if segs_norma and input.segmento not in segs_norma:
                continue

        # Atividade (se fornecida lista nao vazia)
        if atividades:
            ativs_norma = c.aplic_atividade_by_norma.get(n["id"], set())
            if ativs_norma and not (atividades & ativs_norma):
                continue

        aplicaveis_normas.append(n)

    # Processos: pegamos todos os processos amarrados (primaria/secundaria)
    # a alguma das normas aplicaveis. Tambem incluimos seus ancestrais.
    norma_ids = {n["id"] for n in aplicaveis_normas}
    processo_ids: set[str] = set()
    for nid in norma_ids:
        for v in c.vinculos_processo_by_norma.get(nid, []):
            if v.get("tipo_vinculo") in ("primaria", "secundaria"):
                processo_ids.add(v["processo_id"])

    # Adiciona ancestrais (P0 raiz para cada P1/P2/P3)
    expanded: set[str] = set()
    for pid in processo_ids:
        cur = pid
        while cur and cur not in expanded:
            expanded.add(cur)
            p = c.processo_by_id.get(cur)
            if not p:
                break
            cur = p.get("parent_id")
    aplicaveis_processos = [
        c.processo_by_id[p] for p in expanded if p in c.processo_by_id
    ]
    aplicaveis_processos.sort(key=lambda x: x["codigo"])

    # Riscos: similar
    risco_ids: set[str] = set()
    for nid in norma_ids:
        for v in c.vinculos_risco_by_norma.get(nid, []):
            if v.get("tipo_vinculo") in ("primaria", "secundaria"):
                risco_ids.add(v["risco_id"])
    # tambem riscos vinculados a processos aplicaveis
    for pid in expanded:
        for v in c.vinculos_risco_by_processo.get(pid, []):
            risco_ids.add(v["risco_id"])
    expanded_r: set[str] = set()
    for rid in risco_ids:
        cur = rid
        while cur and cur not in expanded_r:
            expanded_r.add(cur)
            r = c.risco_by_id.get(cur)
            if not r:
                break
            cur = r.get("parent_id")
    aplicaveis_riscos = [
        c.risco_by_id[r] for r in expanded_r if r in c.risco_by_id
    ]
    aplicaveis_riscos.sort(key=lambda x: x["codigo"])

    return {
        "entidade": input,
        "versao_chassi": c.version,
        "normas": aplicaveis_normas,
        "processos": aplicaveis_processos,
        "riscos": aplicaveis_riscos,
        "contagens": {
            "normas": len(aplicaveis_normas),
            "processos": len(aplicaveis_processos),
            "riscos": len(aplicaveis_riscos),
        },
    }


# ============================================================
# Chassi (metadados, versao, snapshot)
# ============================================================


@app.get(
    "/v1/chassi/version",
    tags=["Chassi"],
    summary="Versao atual do chassi",
)
async def get_version():
    c = _chassi()
    return {
        "version": c.version,
        "released_at": c.released_at,
        "metadata": c.metadata,
    }


@app.get(
    "/v1/chassi/versions",
    response_model=list[ChassiVersion],
    tags=["Chassi"],
    summary="Historico de versoes",
)
async def list_versions():
    return _chassi().chassi_versions


@app.get(
    "/v1/chassi/stats",
    response_model=ChassiStats,
    tags=["Chassi"],
    summary="Estatisticas globais do chassi",
)
async def get_stats():
    c = _chassi()
    normas_vigentes = sum(1 for n in c.normas if n.get("status") == "vigente")
    p0 = sum(1 for p in c.processos if p.get("nivel") == 0)
    r0 = sum(1 for r in c.riscos if r.get("nivel") == 0)
    return {
        "versao_atual": c.version,
        "reguladores_ativos": sum(1 for r in c.reguladores if r.get("ativo")),
        "tipos_entidade": len(c.tipos_entidade),
        "segmentos": len(c.segmentos),
        "atividades": len(c.atividades_canonicas),
        "normas_vigentes": normas_vigentes,
        "normas_total": len(c.normas),
        "processos_total": len(c.processos),
        "processos_p0": p0,
        "riscos_total": len(c.riscos),
        "riscos_r0": r0,
        "vinculos_norma_processo": len(c.vinculo_norma_processo),
        "vinculos_processo_risco": len(c.vinculo_processo_risco),
        "vinculos_norma_risco": len(c.vinculo_norma_risco),
    }


@app.get(
    "/v1/chassi/snapshot.json",
    tags=["Chassi"],
    summary="Download do snapshot completo em JSON",
    response_class=FileResponse,
)
async def download_snapshot_json():
    """Retorna o arquivo chassi.json (mesmo conteudo que a API serve)."""
    from .loader import _resolve_snapshot_path
    p = _resolve_snapshot_path(os.environ.get("CHASSI_SNAPSHOT_PATH"))
    return FileResponse(
        p,
        media_type="application/json",
        filename="chassi.json",
    )

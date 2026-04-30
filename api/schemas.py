"""
Schemas de resposta da API (Pydantic).

Mantem compatibilidade com o openapi.yaml manual em web/openapi.yaml.
Modelos sao 'lazy' — aceitam campos extras do snapshot sem quebrar.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class _Base(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)


# ============================================================
# Catalogos basicos
# ============================================================


class Regulador(_Base):
    id: str
    nome: str
    natureza: str | None = None
    instrumento: str | None = None
    descricao: str | None = None
    site: str | None = None
    ativo: bool = True


class TipoEntidade(_Base):
    id: str
    nome: str
    grupo: str | None = None
    descricao: str | None = None
    ativo: bool = True


class Segmento(_Base):
    id: str
    regulador_id: str | None = None
    nome: str
    descricao: str | None = None
    ordem: int | None = None


class AtividadeCanonica(_Base):
    id: str
    nome: str
    grupo: str | None = None
    descricao: str | None = None


# ============================================================
# Normas
# ============================================================


class NormaArtigo(_Base):
    id: int
    norma_id: str
    numero: str | None = None
    secao: str | None = None
    tema: str | None = None
    descricao: str | None = None


class Norma(_Base):
    id: str
    tipo: str
    numero: str
    ano: int | None = None
    regulador_id: str | None = None
    titulo: str | None = None
    ementa: str | None = None
    status: str
    vigencia_inicio: date | None = None
    vigencia_fim: date | None = None
    norma_mae_id: str | None = None
    url_oficial: str | None = None


class NormaDetalhe(Norma):
    artigos: list[NormaArtigo] = Field(default_factory=list)
    aplicabilidade_tipo_entidade: list[str] = Field(default_factory=list)
    aplicabilidade_segmento: list[str] = Field(default_factory=list)
    aplicabilidade_atividade: list[str] = Field(default_factory=list)
    vinculos_processo: list["VinculoNormaProcesso"] = Field(default_factory=list)
    vinculos_risco: list["VinculoNormaRisco"] = Field(default_factory=list)


# ============================================================
# Processos / Riscos
# ============================================================


class Processo(_Base):
    id: str
    codigo: str
    nome: str
    nivel: int
    nucleo: str
    parent_id: str | None = None
    descricao: str | None = None
    owner_tipico: str | None = None


class ProcessoDetalhe(Processo):
    children: list[Processo] = Field(default_factory=list)
    vinculos_norma: list["VinculoNormaProcesso"] = Field(default_factory=list)
    vinculos_risco: list["VinculoProcessoRisco"] = Field(default_factory=list)


class Risco(_Base):
    id: str
    codigo: str
    nome: str
    nivel: int
    nucleo: str
    parent_id: str | None = None
    descricao: str | None = None
    categoria_basileia: str | None = None


class RiscoDetalhe(Risco):
    children: list[Risco] = Field(default_factory=list)
    vinculos_norma: list["VinculoNormaRisco"] = Field(default_factory=list)
    vinculos_processo: list["VinculoProcessoRisco"] = Field(default_factory=list)


# ============================================================
# Vinculos
# ============================================================


TipoVinculo = Literal["primaria", "secundaria", "informativa"]


class VinculoNormaProcesso(_Base):
    id: int
    norma_id: str
    processo_id: str
    artigo_ref: str | None = None
    tipo_vinculo: TipoVinculo
    notas: str | None = None


class VinculoNormaRisco(_Base):
    id: int
    norma_id: str
    risco_id: str
    tipo_vinculo: TipoVinculo
    notas: str | None = None


class VinculoProcessoRisco(_Base):
    id: int
    processo_id: str
    risco_id: str
    materialidade_default: int = Field(ge=1, le=5)
    notas: str | None = None


# ============================================================
# Instancia (filtragem por entidade)
# ============================================================


class InstanciaInput(BaseModel):
    """Atributos categoricos da entidade consumidora."""

    tipo_entidade: str = Field(
        ..., description="ID do tipo de entidade (ex: ENT_BANCO_MULTIPLO)"
    )
    segmento: str | None = Field(
        None, description="ID do segmento (ex: S2). Opcional."
    )
    atividades: list[str] = Field(
        default_factory=list,
        description="Lista de IDs de atividades canonicas (ex: ATV_CAMBIO_COMERCIAL)",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "tipo_entidade": "ENT_BANCO_MULTIPLO",
                "segmento": "S2",
                "atividades": ["ATV_DEPOSITO_VISTA", "ATV_CAMBIO_COMERCIAL"],
            }
        }
    )


class InstanciaOutput(BaseModel):
    """Fatia do catalogo aplicavel a uma instancia."""

    entidade: InstanciaInput
    versao_chassi: str
    normas: list[Norma]
    processos: list[Processo]
    riscos: list[Risco]
    contagens: dict[str, int]


# ============================================================
# Chassi (metadados)
# ============================================================


class ChassiVersion(_Base):
    id: str
    version: str
    released_at: datetime | str
    notas: str | None = None
    is_current: bool | None = None


class ChassiStats(BaseModel):
    versao_atual: str
    reguladores_ativos: int
    tipos_entidade: int
    segmentos: int
    atividades: int
    normas_vigentes: int
    normas_total: int
    processos_total: int
    processos_p0: int
    riscos_total: int
    riscos_r0: int
    vinculos_norma_processo: int
    vinculos_processo_risco: int
    vinculos_norma_risco: int


# ============================================================
# Erro padrao
# ============================================================


class HTTPError(BaseModel):
    detail: str


# Resolve forward references
NormaDetalhe.model_rebuild()
ProcessoDetalhe.model_rebuild()
RiscoDetalhe.model_rebuild()

# =============================================================
# Chassi de Controles Internos - API
# Imagem Docker multi-stage para deploy em Fly.io / Railway / GCR
# =============================================================

FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Dependencias
COPY api/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Codigo da API
COPY api /app/api

# Snapshot do catalogo (gerado por backend/export/export.py)
# Em CI/CD pode ser injetado por um job que regenera antes do build.
COPY backend/chassi.json /app/chassi.json

ENV CHASSI_SNAPSHOT_PATH=/app/chassi.json
ENV PORT=8000

EXPOSE 8000

# Healthcheck simples
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request,sys; urllib.request.urlopen('http://127.0.0.1:8000/health',timeout=3); sys.exit(0)" || exit 1

CMD ["sh", "-c", "uvicorn api.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 2"]

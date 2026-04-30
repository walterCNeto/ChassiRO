# Chassi de Controles Internos - Makefile
# ============================================================

.PHONY: help up down reset psql stats export-json export-sqlite export-all install clean

DC := docker compose
PYTHON := python3

help:
	@echo "Chassi de Controles Internos - comandos disponiveis"
	@echo ""
	@echo "  make up              Sobe Postgres e carrega schema+seeds (primeira vez)"
	@echo "  make down            Para Postgres (mantem dados)"
	@echo "  make reset           Apaga volumes e recarrega tudo do zero"
	@echo "  make psql            Abre psql interativo no container"
	@echo "  make stats           Mostra estatisticas do chassi"
	@echo "  make export-json     Gera chassi.json"
	@echo "  make export-sqlite   Gera chassi.sqlite"
	@echo "  make export-all      Gera ambos os formatos"
	@echo "  make install         Instala deps Python para export"
	@echo "  make clean           Remove arquivos exportados"

up:
	$(DC) up -d
	@echo ""
	@echo "Aguardando Postgres ficar healthy..."
	@until $(DC) exec -T postgres pg_isready -U chassi -d chassi >/dev/null 2>&1; do sleep 1; done
	@echo "Postgres pronto em localhost:5432 (user: chassi / db: chassi)"

down:
	$(DC) down

reset:
	$(DC) down -v
	$(DC) up -d
	@echo ""
	@echo "Reset completo. Aguardando Postgres..."
	@until $(DC) exec -T postgres pg_isready -U chassi -d chassi >/dev/null 2>&1; do sleep 1; done
	@echo "Postgres pronto e re-seedado."

psql:
	$(DC) exec postgres psql -U chassi -d chassi

stats:
	$(DC) exec postgres psql -U chassi -d chassi -c "SELECT * FROM v_chassi_stats;"

install:
	$(PYTHON) -m pip install -r export/requirements.txt

export-json:
	cd export && $(PYTHON) export.py to-json --output ../chassi.json

export-sqlite:
	cd export && $(PYTHON) export.py to-sqlite --output ../chassi.sqlite

export-all: export-json export-sqlite
	@ls -lh chassi.json chassi.sqlite 2>/dev/null

clean:
	rm -f chassi.json chassi.sqlite

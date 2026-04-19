# ═══════════════════════════════════════════════════════════════════════════
# Churn Deuna — Makefile de orquestación
# ═══════════════════════════════════════════════════════════════════════════

.PHONY: all install model model-data model-train frontend clean help

# ── Variables ─────────────────────────────────────────────────────────────
PYTHON    := python3
PIP       := pip
STREAMLIT := streamlit

# ── Targets ──────────────────────────────────────────────────────────────

help: ## Muestra esta ayuda
	@echo ""
	@echo "🔮 Churn Deuna — Comandos disponibles"
	@echo "══════════════════════════════════════"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'
	@echo ""

install: ## Instala todas las dependencias (modelo + frontend)
	$(PIP) install -r model/requirements.txt
	$(PIP) install -r frontend/requirements.txt

install-model: ## Instala solo dependencias del modelo
	$(PIP) install -r model/requirements.txt

install-frontend: ## Instala solo dependencias del frontend
	$(PIP) install -r frontend/requirements.txt

model-data: ## Genera las 3 tablas raw + churn_labels
	@echo "📦 Generando data sintética..."
	$(PYTHON) -m src.data.generar_dim_merchants
	$(PYTHON) -m src.data.generar_fact_performance
	$(PYTHON) -m src.data.generar_fact_support_tickets

model-train: ## Construye MDT, entrena (60/20/20), SHAP y predice
	$(PYTHON) -m model.feature_engineering
	$(PYTHON) -m model.train_model

model: model-data model-train ## Pipeline completo: data → MDT → train → SHAP → scoring
	@echo "✅ Pipeline completo. Outputs en outputs_modelo/"

frontend: ## Levanta el dashboard Streamlit
	@echo "🎨 Levantando dashboard..."
	$(STREAMLIT) run frontend/app.py

all: model frontend ## Pipeline completo + dashboard

clean: ## Limpia artefactos generados
	rm -f outputs_modelo/*.pkl
	rm -f outputs_modelo/*.json
	rm -f outputs_modelo/*.csv
	rm -f outputs_modelo/*.parquet
	rm -f outputs_modelo/*.png
	rm -f data/raw/*.csv data/raw/*.parquet
	rm -f data/processed/*.parquet
	find . -type d -name "__pycache__" -not -path "./.venv/*" -exec rm -rf {} + 2>/dev/null || true
	@echo "🧹 Limpieza completada."

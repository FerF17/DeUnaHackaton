# ═══════════════════════════════════════════════════════════════════════════
# Churn Deuna — Makefile de orquestación
# ═══════════════════════════════════════════════════════════════════════════

.PHONY: all install model frontend clean help

# ── Variables ─────────────────────────────────────────────────────────────
PYTHON  := python
PIP     := pip
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

model: ## Ejecuta el pipeline completo del modelo
	@echo "🧠 Ejecutando pipeline del modelo..."
	$(PYTHON) -m model.data_simulation
	$(PYTHON) -m model.feature_engineering
	$(PYTHON) -m model.train_model
	$(PYTHON) -m model.explain
	$(PYTHON) -m model.predict
	@echo "✅ Pipeline completo. Outputs en outputs/"

model-train: ## Solo entrena el modelo (asume datos ya existen)
	$(PYTHON) -m model.train_model
	$(PYTHON) -m model.explain
	$(PYTHON) -m model.predict

frontend: ## Levanta el dashboard Streamlit
	@echo "🎨 Levantando dashboard..."
	$(STREAMLIT) run frontend/app.py

all: model frontend ## Pipeline completo + dashboard

clean: ## Limpia artefactos generados
	rm -rf outputs/model/*.pkl
	rm -rf outputs/model/*.json
	rm -rf outputs/figures/*.png
	rm -rf outputs/predictions.csv
	rm -rf outputs/shap_values.parquet
	rm -rf data/raw/*.csv
	rm -rf data/processed/*.parquet
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@echo "🧹 Limpieza completada."

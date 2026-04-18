# 🧠 Equipo Modelo — Pipeline de Churn Deuna

Este directorio contiene todo el pipeline de Machine Learning. **Solo el equipo de modelo debe editar archivos aquí.**

---

## Archivos

| Archivo | Descripción |
|---|---|
| `data_simulation.py` | Genera dataset sintético (2000 comercios × 12 meses) |
| `feature_engineering.py` | Construye la MDT con ventanas, deltas, agregados y ratios |
| `train_model.py` | Entrena XGBoost + métricas + umbral óptimo F1 |
| `explain.py` | SHAP: importancia global + valores individuales |
| `predict.py` | Scoring + segmentación (Roja/Amarilla/Baja/Muy Baja) |

---

## Pipeline de ejecución

```bash
# Desde la raíz del proyecto
python -m model.data_simulation        # 1. Generar datos sintéticos
python -m model.feature_engineering    # 2. Construir MDT
python -m model.train_model            # 3. Entrenar XGBoost
python -m model.explain                # 4. Generar SHAP
python -m model.predict                # 5. Scoring final

# O todo a la vez:
make model
```

---

## ¿Qué produce? (Contrato con Frontend)

El pipeline produce los siguientes artefactos en `outputs/`:

| Archivo | Formato | Consumido por |
|---|---|---|
| `outputs/predictions.csv` | CSV | Dashboard Streamlit |
| `outputs/model/metrics.json` | JSON | Página de métricas |
| `outputs/model/churn_model.pkl` | Pickle | Solo modelo |
| `outputs/shap_values.parquet` | Parquet | Explorador individual |
| `outputs/figures/shap_summary.png` | PNG | Página de modelo |
| `outputs/figures/shap_bar.png` | PNG | Página de modelo |

> ⚠️ **No modifiques el esquema de `predictions.csv` sin coordinar con el equipo de frontend.** Ver `docs/contrato_datos.md`.

---

## Convenciones

- Todas las configuraciones están en `config/settings.py`
- El target siempre es `churn_30d`
- Seed global: `42`
- Test size: `25%`
- Imports: usar `from config.settings import PATHS` en lugar de hardcodear rutas

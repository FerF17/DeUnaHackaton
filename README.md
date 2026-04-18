# 🔮 Modelo de Churn Deuna — Reto 3 Datos, Interact2Hack 2026

**"Antes de que se vayan"** — Scoring predictivo de abandono de comerciantes B2B para Deuna.

El modelo identifica comercios con alto riesgo de dejar de transar en los próximos 30 días y los segmenta en niveles de alerta accionables por el equipo comercial. El dashboard Streamlit permite visualizar y explorar los resultados.

---

## Criterios de éxito cumplidos

| Criterio del reto | Resultado |
|---|---|
| AUC > 0.75 (orientativo) | **AUC 0.885** en test |
| Variables explicativas coherentes con negocio | Top features: volatilidad de transacciones, recencia, decline rate, tickets de soporte |
| Plan de acción ejecutable sin recursos nuevos | [docs/plan_accion.md](docs/plan_accion.md) |
| Output consumible por el equipo de front | Dashboard Streamlit + [outputs/predictions.csv](outputs/predictions.csv) |

---

## Estructura del Proyecto (2 Equipos)

```
churn_deuna/
│
├── config/                          ⚙️  Configuración centralizada
│   └── settings.py                  Paths, constantes, seed
│
├── model/                           🧠 EQUIPO MODELO
│   ├── data_simulation.py           Genera dataset sintético (2000 comercios × 12 meses)
│   ├── feature_engineering.py       MDT con ventanas, deltas, agregados y ratios
│   ├── train_model.py               XGBoost + métricas + umbral óptimo F1
│   ├── explain.py                   SHAP: importancia global + valores individuales
│   ├── predict.py                   Scoring + segmentación (Roja/Amarilla/Baja/Muy Baja)
│   ├── requirements.txt             Dependencias del modelo
│   └── README.md                    → Guía del equipo modelo
│
├── frontend/                        🎨 EQUIPO FRONTEND
│   ├── app.py                       Landing page del dashboard
│   ├── pages/
│   │   ├── 1_📊_Dashboard.py        Vista ejecutiva del churn
│   │   ├── 2_🔍_Explorador.py       Drill-down por comercio individual
│   │   └── 3_📈_Modelo.py           Métricas del modelo y SHAP globales
│   ├── components/                  Gráficos, filtros y KPIs reutilizables
│   ├── utils/                       Carga de datos desde outputs/
│   ├── assets/                      CSS custom
│   ├── requirements.txt             Dependencias del frontend
│   └── README.md                    → Guía del equipo frontend
│
├── data/                            📂 Datos
│   ├── raw/                         merchants.csv, monthly_activity.csv, churn_labels.csv
│   └── processed/                   mdt_churn.parquet
│
├── outputs/                         🤝 CONTRATO DE INTERFAZ
│   ├── model/                       churn_model.pkl, metrics.json
│   ├── figures/                     shap_summary.png, shap_bar.png
│   ├── predictions.csv              Input para el dashboard
│   └── shap_values.parquet          Valores SHAP por comercio
│
├── notebooks/                       📓 Notebooks
│   └── 01_modelo_churn.ipynb        Pipeline end-to-end con EDA
│
├── docs/                            📖 Documentación
│   ├── diccionario_variables.md     Diccionario de todas las variables
│   ├── plan_accion.md               Plan de acción por nivel de riesgo
│   └── contrato_datos.md            Contrato de interfaz entre equipos
│
├── Makefile                         🔧 Orquestación
├── requirements.txt                 Dependencias globales
└── .gitignore
```

### Flujo de datos entre equipos

```
┌─────────────────────┐         outputs/          ┌─────────────────────┐
│   🧠 EQUIPO MODELO  │ ──────────────────────▶  │  🎨 EQUIPO FRONTEND │
│                     │   predictions.csv        │                     │
│  data_simulation    │   metrics.json           │  app.py             │
│  feature_eng        │   shap_values.parquet    │  pages/Dashboard    │
│  train_model        │   shap_*.png             │  pages/Explorador   │
│  explain            │                          │  pages/Modelo       │
│  predict            │                          │                     │
└─────────────────────┘                          └─────────────────────┘
```

---

## Inicio Rápido

```bash
# 1. Instalar todo
make install

# 2. Ejecutar pipeline del modelo
make model

# 3. Levantar dashboard
make frontend
```

### Comandos disponibles

| Comando | Descripción |
|---|---|
| `make install` | Instala dependencias de ambos equipos |
| `make install-model` | Solo dependencias del modelo |
| `make install-frontend` | Solo dependencias del frontend |
| `make model` | Pipeline completo: datos → MDT → XGBoost → SHAP → scoring |
| `make model-train` | Solo entrena (asume datos existen) |
| `make frontend` | Levanta el dashboard Streamlit |
| `make all` | Modelo + frontend |
| `make clean` | Limpia artefactos generados |
| `make help` | Lista todos los comandos |

---

## Decisiones técnicas

| Decisión | Justificación |
|---|---|
| **XGBoost** como clasificador | Estado del arte en datos tabulares B2B; documentación de Deuna lo recomienda explícitamente sobre redes neuronales por su superior interpretabilidad. |
| **SHAP** para explicabilidad | Valores aditivos con base matemática sólida; permite explicación global (qué variables predicen churn) e individual (por qué este comercio en particular). |
| **Ventanas 0–4 meses + deltas** | Replica el patrón del flujo productivo Databricks de modelos similares; captura aceleración de deterioro. |
| **Segmentación por percentil** | Misma lógica del flujo de referencia (P95/P89/P82). Hace la priorización independiente del volumen absoluto de la cartera. |
| **Target binario a 30 días** | Alineado con el hilo operativo del reto; se consolida la ventana de acción comercial a 30 días. |
| **Umbral óptimo F1** | Balancea precisión y recall; se guarda en `metrics.json` para uso del dashboard. |
| **Streamlit** para dashboard | Framework Python-nativo; permite al equipo de frontend iterar rápido sin JS/HTML. |
| **Arquitectura 2 equipos** | Separación clara modelo/frontend con contrato de datos. Permite trabajo paralelo sin conflictos. |

---

## Variables más predictivas (Top 10 SHAP)

1. `tx_std_12m` — volatilidad de transacciones (12 meses)
2. `n_transacciones_0` — transacciones del mes actual
3. `volatilidad_tx_6m` — std/mean de transacciones (6 meses)
4. `dias_desde_ult_tx_1` — recencia mes anterior
5. `volumen_std_12m` — volatilidad de volumen
6. `tx_sum_3m` — volumen de transacciones últimos 3 meses
7. `decline_rate_6m` — tasa de rechazos
8. `dias_desde_ult_tx_0` — recencia del mes de corte
9. `dias_resolucion_soporte_1` — latencia soporte mes anterior
10. `dias_resolucion_soporte_0` — latencia soporte mes actual

---

## Próximos pasos recomendados

1. **Calibración** — aplicar isotonic regression para que `probabilidad_churn` sea una probabilidad real (útil para el ROI del plan de acción).
2. **Análisis de supervivencia** — migrar a Cox / XGBoost-AFT para predecir *tiempo hasta churn*, no solo probabilidad en ventana fija.
3. **Reentrenamiento mensual** — re-scoring con la nueva fecha de corte al cierre de cada mes.
4. **A/B test del plan de acción** — medir lift real de las intervenciones comerciales.

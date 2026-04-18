# 🎨 Equipo Frontend — Dashboard Streamlit de Churn Deuna

Este directorio contiene todo el frontend del dashboard. **Solo el equipo de frontend debe editar archivos aquí.**

---

## Estructura

```
frontend/
├── app.py                  ← Landing page (entry point)
├── pages/
│   ├── 1_📊_Dashboard.py   ← Vista ejecutiva: segmentos, regiones, top comercios
│   ├── 2_🔍_Explorador.py  ← Drill-down por comercio individual + SHAP
│   └── 3_📈_Modelo.py      ← Métricas del modelo y gráficos SHAP globales
├── components/
│   ├── charts.py           ← Gráficos reutilizables (Plotly)
│   ├── filters.py          ← Sidebar de filtros compartidos
│   └── kpis.py             ← Tarjetas KPI
├── utils/
│   └── data_loader.py      ← Carga de datos desde outputs/ (contrato)
├── assets/
│   └── style.css           ← Estilos custom dark mode
├── requirements.txt
└── README.md
```

---

## Cómo levantar

```bash
# Desde la raíz del proyecto
streamlit run frontend/app.py

# O usando Make:
make frontend
```

---

## ¿De dónde vienen los datos?

El frontend **no ejecuta ningún modelo**. Solo consume los artefactos que el equipo de modelo produce en `outputs/`:

| Archivo | ¿Para qué lo usamos? |
|---|---|
| `outputs/predictions.csv` | Tablas, gráficos, filtros |
| `outputs/model/metrics.json` | Gauges de rendimiento |
| `outputs/shap_values.parquet` | Explorador individual |
| `outputs/figures/shap_*.png` | Imágenes SHAP globales |

> ⚠️ **Si el equipo de modelo cambia el schema de estos archivos, deben coordinarlo con nosotros.** Ver `docs/contrato_datos.md`.

---

## Convenciones

- Toda carga de datos va en `utils/data_loader.py` con `@st.cache_data`
- Los gráficos reutilizables van en `components/charts.py`
- Los filtros compartidos van en `components/filters.py`
- Los estilos van en `assets/style.css`, nunca inline
- Layout siempre `wide`
- Usar paleta de colores definida en `components/charts.py`

## Dependencias

```bash
pip install -r frontend/requirements.txt
```

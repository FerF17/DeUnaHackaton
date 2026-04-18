# Contrato de Datos — Equipos Modelo ↔ Frontend

Este documento define el **contrato de interfaz** entre el equipo de modelo (productor) y el equipo de frontend (consumidor). Ningún equipo debe modificar los archivos del otro sin coordinar cambios en este contrato.

---

## Directorio compartido: `outputs/`

```
outputs/
├── model/
│   ├── churn_model.pkl           ← Solo modelo (no consumido por frontend)
│   ├── metrics.json              ← Métricas de evaluación
│   └── feature_columns.json      ← Columnas usadas en el modelo
├── figures/
│   ├── shap_summary.png          ← SHAP beeswarm plot
│   └── shap_bar.png              ← SHAP bar plot
├── predictions.csv               ← Scoring por comercio
└── shap_values.parquet           ← Valores SHAP individuales
```

---

## Schema: `predictions.csv`

| Columna | Tipo | Ejemplo | Obligatoria |
|---|---|---|---|
| `comercio_id` | string | `M000042` | ✅ |
| `fecha_corte` | datetime | `2026-03-01` | ✅ |
| `probabilidad_churn` | float [0,1] | `0.8734` | ✅ |
| `prob_rank` | float [0,1] | `0.9850` | ✅ |
| `segmento_churn` | string (enum) | `ALERTA_ROJA` | ✅ |
| `mcc_segmento` | string | `retail` | ✅ |
| `region` | string | `Pichincha` | ✅ |
| `tipo_persona` | string | `PERSONA_NATURAL` | ✅ |
| `tenure_meses` | int | `18` | ✅ |
| `volumen_sum_6m` | float | `245000.50` | ✅ |
| `tx_sum_6m` | float | `1250` | ✅ |
| `recencia_bucket_0` | string | `menos_5` | ✅ |

### Valores válidos de `segmento_churn`

| Valor | Percentil |
|---|---|
| `ALERTA_ROJA` | ≥ 95 |
| `ALERTA_AMARILLA` | 89–95 |
| `BAJA_PROBABILIDAD` | 82–89 |
| `MUY_BAJA_PROBABILIDAD` | < 82 |

---

## Schema: `metrics.json`

```json
{
  "auc": 0.8850,
  "pr_auc": 0.7200,
  "precision": 0.7800,
  "recall": 0.6500,
  "f1": 0.7100,
  "threshold": 0.3200,
  "n_train": 1500,
  "n_test": 500,
  "churn_rate_train": 0.18,
  "churn_rate_test": 0.18
}
```

Todos los campos son obligatorios.

---

## Schema: `shap_values.parquet`

- Una fila por comercio (muestra de 500)
- Columna `comercio_id` (string) obligatoria
- Resto de columnas: nombres de features transformados (con prefijo `num__` o `cat__`)
- Valores: float (SHAP value)

---

## Schema: `feature_columns.json`

```json
{
  "numeric": ["n_transacciones_0", "volumen_total_0", ...],
  "categorical": ["mcc_segmento", "region", "tipo_persona", "recencia_bucket_0"]
}
```

---

## Proceso de cambio

1. El equipo que quiere cambiar el schema **crea un issue** o lo comunica directamente
2. Ambos equipos revisan el impacto
3. Se actualiza este documento
4. Se implementa el cambio de forma coordinada

> ⚠️ **Romper el contrato sin coordinar bloqueará al otro equipo.**

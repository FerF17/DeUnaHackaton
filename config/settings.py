"""Configuración centralizada de paths y constantes del proyecto.

Ambos equipos (modelo y frontend) importan de aquí para evitar
paths hardcodeados y garantizar consistencia.

Uso:
    from config.settings import PATHS
    df = pd.read_csv(PATHS.PREDICTIONS)
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


# ── Raíz del proyecto ────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class _Paths:
    """Registro inmutable de todos los paths del proyecto."""

    # Datos
    RAW_DIR: Path = PROJECT_ROOT / "data" / "raw"
    PROCESSED_DIR: Path = PROJECT_ROOT / "data" / "processed"
    MERCHANTS: Path = PROJECT_ROOT / "data" / "raw" / "merchants.csv"
    MONTHLY_ACTIVITY: Path = PROJECT_ROOT / "data" / "raw" / "monthly_activity.csv"
    CHURN_LABELS: Path = PROJECT_ROOT / "data" / "raw" / "churn_labels.csv"
    MDT: Path = PROJECT_ROOT / "data" / "processed" / "mdt_churn.parquet"

    # Outputs del modelo (CONTRATO entre equipos)
    OUTPUT_DIR: Path = PROJECT_ROOT / "outputs"
    MODEL_DIR: Path = PROJECT_ROOT / "outputs" / "model"
    MODEL_PKL: Path = PROJECT_ROOT / "outputs" / "model" / "churn_model.pkl"
    METRICS_JSON: Path = PROJECT_ROOT / "outputs" / "model" / "metrics.json"
    FEATURE_COLS_JSON: Path = PROJECT_ROOT / "outputs" / "model" / "feature_columns.json"
    FIGURES_DIR: Path = PROJECT_ROOT / "outputs" / "figures"
    SHAP_SUMMARY_PNG: Path = PROJECT_ROOT / "outputs" / "figures" / "shap_summary.png"
    SHAP_BAR_PNG: Path = PROJECT_ROOT / "outputs" / "figures" / "shap_bar.png"
    PREDICTIONS: Path = PROJECT_ROOT / "outputs" / "predictions.csv"
    SHAP_VALUES: Path = PROJECT_ROOT / "outputs" / "shap_values.parquet"


PATHS = _Paths()

# ── Constantes del modelo ────────────────────────────────────────────────────
TARGET = "churn_30d"
ID_COLS = ["comercio_id", "fecha_corte"]
CATEGORICAL_COLS = ["mcc_segmento", "region", "tipo_persona", "recencia_bucket_0"]
SEED = 42
TEST_SIZE = 0.25

"""Funciones de gráficos reutilizables para el dashboard."""
from __future__ import annotations

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd


# Paleta de colores del proyecto
SEGMENT_PALETTE = {
    "ALERTA_ROJA": "#ef4444",
    "ALERTA_AMARILLA": "#f59e0b",
    "BAJA_PROBABILIDAD": "#10b981",
    "MUY_BAJA_PROBABILIDAD": "#6366f1",
}

# Layout base reutilizable
BASE_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#e2e8f0", family="Inter, sans-serif"),
    xaxis=dict(gridcolor="rgba(255,255,255,0.1)"),
    yaxis=dict(gridcolor="rgba(255,255,255,0.1)"),
)


def create_segment_donut(df: pd.DataFrame) -> go.Figure:
    """Crea un gráfico de donut con la distribución de segmentos."""
    seg_counts = df["segmento_churn"].value_counts().reset_index()
    seg_counts.columns = ["Segmento", "Comercios"]

    fig = px.pie(
        seg_counts,
        names="Segmento",
        values="Comercios",
        color="Segmento",
        color_discrete_map=SEGMENT_PALETTE,
        hole=0.45,
    )
    fig.update_layout(**BASE_LAYOUT, legend=dict(orientation="h", y=-0.15), margin=dict(t=10, b=40))
    return fig


def create_risk_bar(df: pd.DataFrame, group_col: str, label: str) -> go.Figure:
    """Crea un gráfico de barras horizontales de riesgo promedio por grupo."""
    risk = (
        df.groupby(group_col)["probabilidad_churn"]
        .mean()
        .sort_values(ascending=True)
        .reset_index()
    )
    fig = px.bar(
        risk,
        x="probabilidad_churn",
        y=group_col,
        orientation="h",
        color="probabilidad_churn",
        color_continuous_scale=["#10b981", "#f59e0b", "#ef4444"],
        labels={"probabilidad_churn": "Prob. Churn Promedio", group_col: label},
    )
    fig.update_layout(**BASE_LAYOUT, coloraxis_showscale=False, margin=dict(t=10, b=10))
    return fig


def create_probability_histogram(df: pd.DataFrame, highlight_value: float | None = None) -> go.Figure:
    """Histograma de distribución de probabilidades con línea de corte opcional."""
    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=df["probabilidad_churn"],
        nbinsx=50,
        marker_color="rgba(99, 102, 241, 0.6)",
        name="Distribución",
    ))
    if highlight_value is not None:
        fig.add_vline(
            x=highlight_value,
            line_dash="dash",
            line_color="#ef4444",
            line_width=3,
        )
    fig.update_layout(
        **BASE_LAYOUT,
        xaxis_title="Probabilidad de Churn",
        yaxis_title="N° de Comercios",
        margin=dict(t=10, b=30),
    )
    return fig

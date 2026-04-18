"""Filtros reutilizables para la sidebar del dashboard."""
from __future__ import annotations

import pandas as pd
import streamlit as st


def render_sidebar_filters(df: pd.DataFrame) -> pd.DataFrame:
    """Renderiza filtros en la sidebar y devuelve el DataFrame filtrado."""
    with st.sidebar:
        st.markdown("### 🎛️ Filtros")

        # Filtro por segmento
        segmentos = ["Todos"] + sorted(df["segmento_churn"].unique().tolist())
        seg_selected = st.selectbox("Segmento de Riesgo:", segmentos, key="filter_segmento")

        # Filtro por región
        regiones = ["Todas"] + sorted(df["region"].dropna().unique().tolist())
        region_selected = st.selectbox("Región:", regiones, key="filter_region")

        # Filtro por MCC
        mccs = ["Todos"] + sorted(df["mcc_segmento"].dropna().unique().tolist())
        mcc_selected = st.selectbox("Segmento MCC:", mccs, key="filter_mcc")

        # Filtro por tipo persona
        tipos = ["Todos"] + sorted(df["tipo_persona"].dropna().unique().tolist())
        tipo_selected = st.selectbox("Tipo de Persona:", tipos, key="filter_tipo")

        # Filtro por rango de probabilidad
        st.markdown("---")
        prob_range = st.slider(
            "Rango de Probabilidad:",
            min_value=0.0,
            max_value=1.0,
            value=(0.0, 1.0),
            step=0.01,
            key="filter_prob_range",
        )

    # Aplicar filtros
    filtered = df.copy()

    if seg_selected != "Todos":
        filtered = filtered[filtered["segmento_churn"] == seg_selected]

    if region_selected != "Todas":
        filtered = filtered[filtered["region"] == region_selected]

    if mcc_selected != "Todos":
        filtered = filtered[filtered["mcc_segmento"] == mcc_selected]

    if tipo_selected != "Todos":
        filtered = filtered[filtered["tipo_persona"] == tipo_selected]

    filtered = filtered[
        (filtered["probabilidad_churn"] >= prob_range[0])
        & (filtered["probabilidad_churn"] <= prob_range[1])
    ]

    # Mostrar resumen de filtro
    with st.sidebar:
        st.markdown("---")
        st.markdown(f"**📌 Mostrando:** {len(filtered):,} de {len(df):,} comercios")

    return filtered

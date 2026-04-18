"""📊 Dashboard — Vista ejecutiva del churn

Distribución de segmentos, análisis por dimensión de negocio y top comercios en riesgo.
"""
import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from frontend.utils.data_loader import load_predictions
from frontend.components.filters import render_sidebar_filters
from frontend.components.kpis import render_segment_kpis

st.set_page_config(page_title="Dashboard — Churn Deuna", page_icon="📊", layout="wide")

# CSS
css_path = Path(__file__).parent.parent / "assets" / "style.css"
if css_path.exists():
    st.markdown(f"<style>{css_path.read_text()}</style>", unsafe_allow_html=True)


def main():
    st.markdown("## 📊 Dashboard de Churn")
    st.markdown("Vista ejecutiva de la cartera de comerciantes y segmentación de riesgo.")

    predictions = load_predictions()
    if predictions is None:
        st.error("No se encontraron predicciones. Ejecuta `make model` primero.")
        return

    # ── Filtros ───────────────────────────────────────────────────────────────
    df = render_sidebar_filters(predictions)

    # ── KPIs por segmento ─────────────────────────────────────────────────────
    render_segment_kpis(df)

    st.markdown("---")

    # ── Gráficos ──────────────────────────────────────────────────────────────
    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("### 🎯 Distribución por Segmento de Riesgo")
        seg_counts = df["segmento_churn"].value_counts().reset_index()
        seg_counts.columns = ["Segmento", "Comercios"]
        color_map = {
            "ALERTA_ROJA": "#ef4444",
            "ALERTA_AMARILLA": "#f59e0b",
            "BAJA_PROBABILIDAD": "#10b981",
            "MUY_BAJA_PROBABILIDAD": "#6366f1",
        }
        fig_seg = px.pie(
            seg_counts, names="Segmento", values="Comercios",
            color="Segmento", color_discrete_map=color_map,
            hole=0.45,
        )
        fig_seg.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#e2e8f0"),
            legend=dict(orientation="h", y=-0.15),
            margin=dict(t=10, b=40),
        )
        st.plotly_chart(fig_seg, use_container_width=True)

    with col_right:
        st.markdown("### 🗺️ Riesgo Promedio por Región")
        region_risk = (
            df.groupby("region")["probabilidad_churn"]
            .mean()
            .sort_values(ascending=True)
            .reset_index()
        )
        fig_region = px.bar(
            region_risk,
            x="probabilidad_churn",
            y="region",
            orientation="h",
            color="probabilidad_churn",
            color_continuous_scale=["#10b981", "#f59e0b", "#ef4444"],
            labels={"probabilidad_churn": "Prob. Churn Promedio", "region": "Región"},
        )
        fig_region.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#e2e8f0"),
            coloraxis_showscale=False,
            margin=dict(t=10, b=10),
            xaxis=dict(gridcolor="rgba(255,255,255,0.1)"),
            yaxis=dict(gridcolor="rgba(255,255,255,0.1)"),
        )
        st.plotly_chart(fig_region, use_container_width=True)

    # ── Segunda fila de gráficos ──────────────────────────────────────────────
    col2_left, col2_right = st.columns(2)

    with col2_left:
        st.markdown("### 🏪 Riesgo por Segmento MCC")
        mcc_risk = (
            df.groupby("mcc_segmento")
            .agg(
                prob_media=("probabilidad_churn", "mean"),
                n_comercios=("comercio_id", "count"),
            )
            .reset_index()
        )
        fig_mcc = px.bar(
            mcc_risk,
            x="mcc_segmento",
            y="prob_media",
            color="prob_media",
            color_continuous_scale=["#10b981", "#f59e0b", "#ef4444"],
            text="n_comercios",
            labels={"prob_media": "Prob. Churn Media", "mcc_segmento": "Segmento MCC"},
        )
        fig_mcc.update_traces(texttemplate="%{text} comercios", textposition="outside")
        fig_mcc.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#e2e8f0"),
            coloraxis_showscale=False,
            margin=dict(t=10, b=10),
            xaxis=dict(gridcolor="rgba(255,255,255,0.1)"),
            yaxis=dict(gridcolor="rgba(255,255,255,0.1)"),
        )
        st.plotly_chart(fig_mcc, use_container_width=True)

    with col2_right:
        st.markdown("### 👤 Distribución por Tipo de Persona")
        persona_risk = (
            df.groupby("tipo_persona")
            .agg(
                prob_media=("probabilidad_churn", "mean"),
                n_comercios=("comercio_id", "count"),
            )
            .reset_index()
        )
        fig_persona = px.bar(
            persona_risk,
            x="tipo_persona",
            y="n_comercios",
            color="prob_media",
            color_continuous_scale=["#10b981", "#ef4444"],
            text="n_comercios",
            labels={"n_comercios": "Comercios", "tipo_persona": "Tipo de Persona"},
        )
        fig_persona.update_traces(texttemplate="%{text}", textposition="outside")
        fig_persona.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#e2e8f0"),
            coloraxis_showscale=False,
            margin=dict(t=10, b=10),
            xaxis=dict(gridcolor="rgba(255,255,255,0.1)"),
            yaxis=dict(gridcolor="rgba(255,255,255,0.1)"),
        )
        st.plotly_chart(fig_persona, use_container_width=True)

    # ── Top 20 comercios en riesgo ────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### 🚨 Top 20 Comercios en Mayor Riesgo")
    top20 = df.nlargest(20, "probabilidad_churn")[
        ["comercio_id", "probabilidad_churn", "segmento_churn",
         "mcc_segmento", "region", "tipo_persona", "volumen_sum_6m", "tx_sum_6m"]
    ].reset_index(drop=True)
    top20.index = top20.index + 1

    st.dataframe(
        top20.style.format({
            "probabilidad_churn": "{:.2%}",
            "volumen_sum_6m": "${:,.0f}",
            "tx_sum_6m": "{:,.0f}",
        }).background_gradient(subset=["probabilidad_churn"], cmap="RdYlGn_r"),
        use_container_width=True,
        height=500,
    )


if __name__ == "__main__":
    main()

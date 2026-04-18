"""📈 Modelo — Métricas y explicabilidad global

Muestra las métricas del modelo, distribución de probabilidades y gráficos SHAP globales.
"""
import json
import sys
from pathlib import Path

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from frontend.utils.data_loader import load_predictions, load_metrics

st.set_page_config(page_title="Modelo — Churn Deuna", page_icon="📈", layout="wide")

css_path = Path(__file__).parent.parent / "assets" / "style.css"
if css_path.exists():
    st.markdown(f"<style>{css_path.read_text()}</style>", unsafe_allow_html=True)


def main():
    st.markdown("## 📈 Rendimiento del Modelo")
    st.markdown("Métricas detalladas, distribución de probabilidades y explicabilidad global.")

    predictions = load_predictions()
    metrics = load_metrics()

    if metrics is None:
        st.error("No se encontraron métricas. Ejecuta `make model` primero.")
        return

    # ── Métricas principales ──────────────────────────────────────────────────
    st.markdown("### 🏆 Métricas de Evaluación")

    col1, col2, col3 = st.columns(3)

    with col1:
        # Gauge de AUC-ROC
        fig_auc = go.Figure(go.Indicator(
            mode="gauge+number",
            value=metrics["auc"],
            title={"text": "AUC-ROC", "font": {"color": "#e2e8f0"}},
            number={"font": {"color": "#e2e8f0"}},
            gauge={
                "axis": {"range": [0, 1], "tickcolor": "#e2e8f0"},
                "bar": {"color": "#6366f1"},
                "bgcolor": "rgba(0,0,0,0)",
                "steps": [
                    {"range": [0, 0.5], "color": "rgba(239,68,68,0.2)"},
                    {"range": [0.5, 0.75], "color": "rgba(245,158,11,0.2)"},
                    {"range": [0.75, 1], "color": "rgba(16,185,129,0.2)"},
                ],
                "threshold": {
                    "line": {"color": "#10b981", "width": 4},
                    "thickness": 0.75,
                    "value": 0.75,
                },
            },
        ))
        fig_auc.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            font={"color": "#e2e8f0"},
            height=250,
            margin=dict(t=50, b=10),
        )
        st.plotly_chart(fig_auc, use_container_width=True)

    with col2:
        fig_pr = go.Figure(go.Indicator(
            mode="gauge+number",
            value=metrics["pr_auc"],
            title={"text": "AUC-PR", "font": {"color": "#e2e8f0"}},
            number={"font": {"color": "#e2e8f0"}},
            gauge={
                "axis": {"range": [0, 1], "tickcolor": "#e2e8f0"},
                "bar": {"color": "#8b5cf6"},
                "bgcolor": "rgba(0,0,0,0)",
                "steps": [
                    {"range": [0, 0.3], "color": "rgba(239,68,68,0.2)"},
                    {"range": [0.3, 0.6], "color": "rgba(245,158,11,0.2)"},
                    {"range": [0.6, 1], "color": "rgba(16,185,129,0.2)"},
                ],
            },
        ))
        fig_pr.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            font={"color": "#e2e8f0"},
            height=250,
            margin=dict(t=50, b=10),
        )
        st.plotly_chart(fig_pr, use_container_width=True)

    with col3:
        fig_f1 = go.Figure(go.Indicator(
            mode="gauge+number",
            value=metrics["f1"],
            title={"text": "F1 Score", "font": {"color": "#e2e8f0"}},
            number={"font": {"color": "#e2e8f0"}},
            gauge={
                "axis": {"range": [0, 1], "tickcolor": "#e2e8f0"},
                "bar": {"color": "#ec4899"},
                "bgcolor": "rgba(0,0,0,0)",
                "steps": [
                    {"range": [0, 0.4], "color": "rgba(239,68,68,0.2)"},
                    {"range": [0.4, 0.7], "color": "rgba(245,158,11,0.2)"},
                    {"range": [0.7, 1], "color": "rgba(16,185,129,0.2)"},
                ],
            },
        ))
        fig_f1.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            font={"color": "#e2e8f0"},
            height=250,
            margin=dict(t=50, b=10),
        )
        st.plotly_chart(fig_f1, use_container_width=True)

    # ── Tabla de métricas detalladas ──────────────────────────────────────────
    st.markdown("---")

    detail_col1, detail_col2 = st.columns(2)

    with detail_col1:
        st.markdown("### 📋 Métricas Detalladas")
        metrics_display = {
            "AUC-ROC": f"{metrics['auc']:.4f}",
            "AUC-PR": f"{metrics['pr_auc']:.4f}",
            "Precision": f"{metrics['precision']:.4f}",
            "Recall": f"{metrics['recall']:.4f}",
            "F1 Score": f"{metrics['f1']:.4f}",
            "Umbral Óptimo F1": f"{metrics['threshold']:.4f}",
            "N° Train": f"{metrics['n_train']:,}",
            "N° Test": f"{metrics['n_test']:,}",
            "Churn Rate Train": f"{metrics['churn_rate_train']:.2%}",
            "Churn Rate Test": f"{metrics['churn_rate_test']:.2%}",
        }
        for k, v in metrics_display.items():
            st.markdown(f"**{k}:** `{v}`")

    with detail_col2:
        st.markdown("### 📊 Distribución de Probabilidades")
        if predictions is not None:
            fig_dist = px.histogram(
                predictions,
                x="probabilidad_churn",
                nbins=50,
                color="segmento_churn",
                color_discrete_map={
                    "ALERTA_ROJA": "#ef4444",
                    "ALERTA_AMARILLA": "#f59e0b",
                    "BAJA_PROBABILIDAD": "#10b981",
                    "MUY_BAJA_PROBABILIDAD": "#6366f1",
                },
                labels={"probabilidad_churn": "Probabilidad de Churn"},
            )
            fig_dist.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#e2e8f0"),
                barmode="stack",
                legend=dict(orientation="h", y=-0.2),
                margin=dict(t=10, b=40),
                xaxis=dict(gridcolor="rgba(255,255,255,0.1)"),
                yaxis=dict(gridcolor="rgba(255,255,255,0.1)"),
            )
            st.plotly_chart(fig_dist, use_container_width=True)

    # ── SHAP global ───────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### 🧠 Importancia Global de Variables (SHAP)")

    figures_dir = Path(__file__).resolve().parent.parent.parent / "outputs" / "figures"

    shap_col1, shap_col2 = st.columns(2)

    with shap_col1:
        shap_bar = figures_dir / "shap_bar.png"
        if shap_bar.exists():
            st.image(str(shap_bar), caption="Top 20 Features por Importancia SHAP", use_container_width=True)
        else:
            st.info("Ejecuta `python -m model.explain` para generar gráficos SHAP.")

    with shap_col2:
        shap_summary = figures_dir / "shap_summary.png"
        if shap_summary.exists():
            st.image(str(shap_summary), caption="SHAP Summary Plot (Beeswarm)", use_container_width=True)
        else:
            st.info("Ejecuta `python -m model.explain` para generar gráficos SHAP.")


if __name__ == "__main__":
    main()

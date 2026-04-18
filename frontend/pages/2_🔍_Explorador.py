"""🔍 Explorador — Drill-down por comercio individual

Busca un comercio por ID y analiza su probabilidad de churn,
segmento, y las razones principales según SHAP.
"""
import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from frontend.utils.data_loader import load_predictions, load_shap_values

st.set_page_config(page_title="Explorador — Churn Deuna", page_icon="🔍", layout="wide")

css_path = Path(__file__).parent.parent / "assets" / "style.css"
if css_path.exists():
    st.markdown(f"<style>{css_path.read_text()}</style>", unsafe_allow_html=True)


SEGMENT_COLORS = {
    "ALERTA_ROJA": "#ef4444",
    "ALERTA_AMARILLA": "#f59e0b",
    "BAJA_PROBABILIDAD": "#10b981",
    "MUY_BAJA_PROBABILIDAD": "#6366f1",
}

SEGMENT_EMOJI = {
    "ALERTA_ROJA": "🔴",
    "ALERTA_AMARILLA": "🟡",
    "BAJA_PROBABILIDAD": "🟢",
    "MUY_BAJA_PROBABILIDAD": "⚪",
}


def main():
    st.markdown("## 🔍 Explorador de Comercios")
    st.markdown("Busca un comercio específico y analiza las razones de su riesgo de churn.")

    predictions = load_predictions()
    shap_df = load_shap_values()

    if predictions is None:
        st.error("No se encontraron predicciones. Ejecuta `make model` primero.")
        return

    # ── Búsqueda ──────────────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown("### 🔎 Buscar Comercio")
        comercio_ids = predictions["comercio_id"].sort_values().tolist()
        selected_id = st.selectbox(
            "Selecciona un comercio:",
            options=comercio_ids,
            index=0,
            key="explorador_comercio_id",
        )

        # Búsqueda rápida por segmento
        st.markdown("---")
        st.markdown("### ⚡ Acceso Rápido")
        segmento_filter = st.selectbox(
            "Filtrar por segmento:",
            ["Todos"] + list(SEGMENT_COLORS.keys()),
            key="explorador_segmento",
        )
        if segmento_filter != "Todos":
            filtered = predictions[predictions["segmento_churn"] == segmento_filter]
            if not filtered.empty:
                selected_id = st.selectbox(
                    f"Comercios en {segmento_filter}:",
                    filtered["comercio_id"].tolist(),
                    key="explorador_filtered_id",
                )

    # ── Datos del comercio ────────────────────────────────────────────────────
    row = predictions[predictions["comercio_id"] == selected_id]
    if row.empty:
        st.warning(f"Comercio {selected_id} no encontrado.")
        return

    row = row.iloc[0]
    segmento = row["segmento_churn"]
    color = SEGMENT_COLORS.get(segmento, "#6366f1")
    emoji = SEGMENT_EMOJI.get(segmento, "⚪")

    # ── Ficha del comercio ────────────────────────────────────────────────────
    st.markdown(f"### {emoji} Comercio: `{selected_id}`")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(
            f"""
            <div class="kpi-card" style="border-left: 4px solid {color};">
                <div class="kpi-value" style="color: {color};">{row['probabilidad_churn']:.1%}</div>
                <div class="kpi-label">Probabilidad de Churn</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            f"""
            <div class="kpi-card" style="border-left: 4px solid {color};">
                <div class="kpi-value">{emoji} {segmento.replace('_', ' ').title()}</div>
                <div class="kpi-label">Segmento</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-value">{row.get('mcc_segmento', 'N/A')}</div>
                <div class="kpi-label">MCC Segmento</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col4:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-value">{row.get('region', 'N/A')}</div>
                <div class="kpi-label">Región</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ── Métricas del comercio ─────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### 📋 Métricas del Comercio")

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Tipo Persona", row.get("tipo_persona", "N/A"))
    m2.metric("Tenure (meses)", f"{row.get('tenure_meses', 0):.0f}")
    m3.metric("Volumen 6m", f"${row.get('volumen_sum_6m', 0):,.0f}")
    m4.metric("Transacciones 6m", f"{row.get('tx_sum_6m', 0):,.0f}")

    # ── Posición en la distribución ───────────────────────────────────────────
    st.markdown("---")
    st.markdown("### 📊 Posición en la Distribución de Riesgo")

    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=predictions["probabilidad_churn"],
        nbinsx=50,
        marker_color="rgba(99, 102, 241, 0.5)",
        name="Todos los comercios",
    ))
    fig.add_vline(
        x=row["probabilidad_churn"],
        line_dash="dash",
        line_color=color,
        line_width=3,
        annotation_text=f"{selected_id}: {row['probabilidad_churn']:.1%}",
        annotation_font_color=color,
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e2e8f0"),
        xaxis_title="Probabilidad de Churn",
        yaxis_title="N° de Comercios",
        margin=dict(t=30, b=30),
        xaxis=dict(gridcolor="rgba(255,255,255,0.1)"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.1)"),
    )
    st.plotly_chart(fig, use_container_width=True)

    # ── SHAP individual ──────────────────────────────────────────────────────
    if shap_df is not None and selected_id in shap_df["comercio_id"].values:
        st.markdown("---")
        st.markdown("### 🧠 ¿Por qué este comercio tiene este riesgo? (Top 10 SHAP)")

        shap_row = shap_df[shap_df["comercio_id"] == selected_id].iloc[0]
        feature_cols = [c for c in shap_df.columns if c != "comercio_id"]
        shap_vals = shap_row[feature_cols].astype(float)
        top_features = shap_vals.abs().nlargest(10)
        top_shap = shap_vals[top_features.index].sort_values()

        fig_shap = go.Figure()
        colors = ["#ef4444" if v > 0 else "#10b981" for v in top_shap.values]
        fig_shap.add_trace(go.Bar(
            y=[name.replace("num__", "").replace("cat__", "") for name in top_shap.index],
            x=top_shap.values,
            orientation="h",
            marker_color=colors,
        ))
        fig_shap.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#e2e8f0"),
            xaxis_title="Impacto SHAP (→ más churn | ← menos churn)",
            margin=dict(t=10, b=10, l=200),
            xaxis=dict(gridcolor="rgba(255,255,255,0.1)"),
            yaxis=dict(gridcolor="rgba(255,255,255,0.1)"),
            height=400,
        )
        st.plotly_chart(fig_shap, use_container_width=True)

        st.info(
            "📖 **Lectura:** Las barras rojas empujan hacia churn; las verdes protegen. "
            "Los features al tope son los más influyentes para este comercio."
        )
    else:
        st.info(
            "ℹ️ No hay valores SHAP disponibles para este comercio. "
            "Ejecuta `python -m model.explain` para generarlos (muestra de 500)."
        )


if __name__ == "__main__":
    main()

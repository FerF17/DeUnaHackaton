"""Tarjetas KPI reutilizables."""
from __future__ import annotations

import pandas as pd
import streamlit as st


def render_segment_kpis(df: pd.DataFrame) -> None:
    """Renderiza tarjetas KPI por cada segmento de riesgo."""
    segments = {
        "ALERTA_ROJA":              ("🔴", "#ef4444"),
        "ALERTA_AMARILLA":          ("🟡", "#f59e0b"),
        "BAJA_PROBABILIDAD":        ("🟢", "#10b981"),
        "MUY_BAJA_PROBABILIDAD":    ("⚪", "#6366f1"),
    }

    cols = st.columns(4)

    for col, (seg, (emoji, color)) in zip(cols, segments.items()):
        count = len(df[df["segmento_churn"] == seg])
        pct = count / max(len(df), 1)

        with col:
            st.markdown(
                f"""
                <div class="kpi-card" style="border-top: 3px solid {color};">
                    <div class="kpi-value" style="color: {color};">{count}</div>
                    <div class="kpi-label">{emoji} {seg.replace('_', ' ').title()}</div>
                    <div class="kpi-sublabel">{pct:.1%} del total</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

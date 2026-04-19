"""🏠 Churn Deuna — Dashboard Ejecutivo

Landing page del dashboard de predicción de churn de comerciantes B2B.
Muestra KPIs principales y navegación a la página Ejecutiva.
"""
import sys
from pathlib import Path

import streamlit as st

# Asegurar imports del proyecto
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from frontend.utils.data_loader import load_predictions, load_metrics

# ── Configuración de la página ────────────────────────────────────────────────
st.set_page_config(
    page_title="Churn Deuna — Dashboard",
    page_icon="💜",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Cargar CSS custom
css_path = Path(__file__).parent / "assets" / "style.css"
if css_path.exists():
    st.markdown(f"<style>{css_path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)

# Ruta relativa de la página Ejecutiva (con emoji y tilde)
EJECUTIVO_PAGE = "pages/📊 Ejecutivo D'Una.py"
LOGO_URL = "https://res.cloudinary.com/doy9vd3pj/image/upload/q_auto/f_auto/v1776540402/unnamed_ooahqu.png"


def render_sidebar() -> None:
    with st.sidebar:
        st.markdown(
            f"""
            <div style='text-align:center; padding: 8px 0 18px;'>
                <img src='{LOGO_URL}' width='120' style='border-radius: 14px; box-shadow: 0 8px 24px rgba(124,58,237,0.35);' />
                <p style='margin: 10px 0 0; color:#CBD5E1; font-weight:700; letter-spacing:0.04em;'>Churn Intelligence</p>
                <p style='margin: 2px 0 0; color:#94A3B8; font-size:12px;'>Powered by DeUna</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.divider()

        st.markdown("#### 🧭 Navegación")
        st.page_link("app.py", label="🏠 Inicio", use_container_width=True)
        st.page_link(EJECUTIVO_PAGE, label="📊 Panel Ejecutivo", use_container_width=True)

        st.divider()

        st.markdown(
            "<p style='color:#94A3B8; font-size:12px; line-height:1.5;'>"
            "Dashboard predictivo de abandono de comerciantes afiliados a DeUna. "
            "Datos actualizados cada 24 horas.</p>",
            unsafe_allow_html=True,
        )

        st.markdown(
            "<p style='text-align:center; color:#64748B; font-size:11px; margin-top:18px;'>"
            "Reto 3 — Interact2Hack 2026</p>",
            unsafe_allow_html=True,
        )


def render_header() -> None:
    st.markdown(
        f"""
        <div class="header-container">
            <h1 style="display:flex; align-items:center; justify-content:center; gap:14px; margin-bottom:0;">
                <img src="{LOGO_URL}" width="52" style="border-radius:12px;">
                Churn Deuna
            </h1>
            <p class="subtitle">Sistema predictivo de abandono de comerciantes B2B</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_kpis(predictions) -> None:
    total = len(predictions)
    alerta_roja = len(predictions[predictions["nivel_riesgo"].isin(["Crítico", "Alto"])])
    alerta_amarilla = len(predictions[predictions["nivel_riesgo"] == "Medio"])
    prob_media = predictions["probabilidad_churn"].mean()

    st.markdown(
        f"""
        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-value">{total:,}</div>
                <div class="kpi-label">Comercios Scoreados</div>
            </div>
            <div class="kpi-card kpi-danger">
                <div class="kpi-value">{alerta_roja:,}</div>
                <div class="kpi-label">🔴 Alerta Roja</div>
            </div>
            <div class="kpi-card kpi-warning">
                <div class="kpi-value">{alerta_amarilla:,}</div>
                <div class="kpi-label">🟡 Alerta Amarilla</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-value">{prob_media:.1%}</div>
                <div class="kpi-label">Prob. Media de Churn</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_model_metrics(metrics) -> None:
    st.markdown("### 📊 Rendimiento del Modelo (Test)")
    test_metrics = metrics.get("splits", {}).get("test", {})

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("AUC-ROC", f"{test_metrics.get('auc_roc', 0):.3f}")
    m2.metric("AUC-PR", f"{test_metrics.get('auc_pr', 0):.3f}")
    m3.metric("F1 Score", f"{test_metrics.get('f1', 0):.3f}")
    m4.metric("Umbral F1", f"{metrics.get('threshold', 0):.3f}")


def render_navigation() -> None:
    st.markdown("### 🧭 Explora el Dashboard")
    st.markdown(
        "<p style='color:#94A3B8; margin-top:-8px; margin-bottom:18px;'>"
        "Accede a cada vista del Panel Ejecutivo con un clic.</p>",
        unsafe_allow_html=True,
    )

    sections = [
        ("📊", "Resumen", "Panel ejecutivo de riesgo y KPIs principales a 30 días."),
        ("📅", "Cohortes", "Evolución de probabilidad de abandono según mes de onboarding."),
        ("💼", "Inteligencia", "Workspace de retención con sugerencias de Next Best Action."),
        ("🗺️", "Geoespacial", "Focos geográficos con alta concentración de riesgo."),
        ("🔍", "Perfil Profundo", "Radiografía individual y drivers de abandono (SHAP)."),
    ]

    # Fila 1: 3 tarjetas  |  Fila 2: 2 tarjetas — responsive gracias a CSS
    row1 = st.columns(3)
    row2 = st.columns(3)

    slots = list(row1) + list(row2[:2])
    for col, (icon, title, desc) in zip(slots, sections):
        with col:
            st.markdown(
                f"""
                <div class="nav-card">
                    <h3>{icon} {title}</h3>
                    <p>{desc}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.page_link(
                EJECUTIVO_PAGE,
                label=f"Abrir {title} →",
                use_container_width=True,
            )

    # Botón principal destacado
    st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
    cta_col = st.columns([1, 2, 1])[1]
    with cta_col:
        st.page_link(
            EJECUTIVO_PAGE,
            label="🚀 Ir al Panel Ejecutivo Completo",
            use_container_width=True,
        )


def main() -> None:
    render_sidebar()
    render_header()

    predictions = load_predictions()
    metrics = load_metrics()

    if predictions is None:
        st.error(
            "⚠️ No se encontraron predicciones. Ejecuta primero el pipeline del modelo:\n\n"
            "```bash\nmake model\n```"
        )
        return

    render_kpis(predictions)
    st.markdown("---")

    if metrics:
        render_model_metrics(metrics)
        st.markdown("---")

    render_navigation()

    st.markdown("---")
    st.caption("Reto 3 — Interact2Hack 2026 · \"Antes de que se vayan\" · DeUna Churn Intelligence")


if __name__ == "__main__":
    main()

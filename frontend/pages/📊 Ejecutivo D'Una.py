"""📊 Panel Ejecutivo D'Una — Churn Intelligence.

Tabs: Resumen, Cohortes, Inteligencia, Geoespacial, Perfil Profundo.
"""
import textwrap
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

# ==========================================
# 1. CONFIGURACIÓN DE LA PÁGINA Y ESTILOS
# ==========================================
st.set_page_config(
    page_title="D'Una Churn Intelligence",
    page_icon="💜",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Paleta de marca DeUna (morado/magenta)
DEUNA_PRIMARY = "#4C1D80"
DEUNA_ACCENT = "#A855F7"
DEUNA_MAGENTA = "#EC4899"

# Paleta semántica de niveles de riesgo
RISK_COLORS = {
    "Crítico": "#EF4444",
    "Alto": "#F97316",
    "Medio": "#FBBF24",
    "Bajo": "#10B981",
}

LOGO_URL = "https://res.cloudinary.com/doy9vd3pj/image/upload/q_auto/f_auto/v1776540402/unnamed_ooahqu.png"

# Cargar CSS global compartido con el landing
css_path = Path(__file__).resolve().parent.parent / "assets" / "style.css"
if css_path.exists():
    st.markdown(f"<style>{css_path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)


# ==========================================
# 2. CARGA DE DATOS
# ==========================================
@st.cache_data(ttl=300)
def load_data() -> pd.DataFrame:
    data_path = (
        Path(__file__).resolve().parent.parent.parent
        / "outputs_modelo"
        / "fact_churn_predictions.csv"
    )
    df = pd.read_csv(data_path, sep=None, engine="python")
    df.columns = df.columns.str.strip()
    return df


df = load_data()

# ==========================================
# 3. BARRA LATERAL (SIDEBAR) & FILTROS
# ==========================================
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
    st.page_link("pages/📊 Ejecutivo D'Una.py", label="📊 Panel Ejecutivo", use_container_width=True)

    st.divider()

    st.markdown("### 🎛️ Filtros Globales")
    st.markdown(
        "<p style='color: #94A3B8; font-size: 13px; margin-bottom: 14px;'>"
        "Ajusta los parámetros del portafolio</p>",
        unsafe_allow_html=True,
    )

    selected_region = st.multiselect(
        "📍 Región",
        options=sorted(df["region"].dropna().unique()),
        default=sorted(df["region"].dropna().unique()),
        help="Segmenta los comercios por ubicación geográfica",
    )

    selected_segmento = st.multiselect(
        "🏢 Segmento Comercial",
        options=sorted(df["segmento_comercial"].dropna().unique()),
        default=sorted(df["segmento_comercial"].dropna().unique()),
    )

    selected_risk = st.multiselect(
        "🚨 Nivel de Riesgo",
        options=list(RISK_COLORS.keys()),
        default=list(RISK_COLORS.keys()),
    )

    if st.button("🔄 Restablecer filtros", use_container_width=True):
        # Rerun fuerza que Streamlit redibuje con los defaults arriba
        for key in ("_year_filter",):
            st.session_state.pop(key, None)
        st.rerun()

    st.divider()
    st.markdown(
        "<p style='text-align: center; color: #64748B; font-size: 12px;'>"
        "D'Una Churn Intelligence v1.0</p>",
        unsafe_allow_html=True,
    )

# Máscara base (sidebar)
mask_sidebar = (
    df["region"].isin(selected_region)
    & df["segmento_comercial"].isin(selected_segmento)
    & df["nivel_riesgo"].isin(selected_risk)
)

# ==========================================
# 3.5. HEADER + FILTRO AÑO
# ==========================================
st.markdown(
    f"""
    <div style='display:flex; align-items:center; gap:14px; margin-bottom:10px;'>
        <img src='{LOGO_URL}' width='44' style='border-radius:10px;'>
        <div>
            <h2 style='margin:0; background: linear-gradient(135deg,#4C1D80 0%,#A855F7 50%,#EC4899 100%);
                       -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text;
                       font-weight:800; letter-spacing:-0.02em;'>Panel Ejecutivo D'Una</h2>
            <p style='margin:2px 0 0; color:#94A3B8; font-size:13px;'>Churn Intelligence · Comerciantes B2B</p>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

anios_disponibles = sorted(
    list(set(df["mes_onboarding"].dropna().str[:4])), reverse=True
)

col_year_label, col_year_select = st.columns([1, 3])
with col_year_label:
    st.markdown(
        "<div style='margin-top:8px; color:#CBD5E1; font-size:13px; font-weight:600;'>"
        "📅 Cohorte (Año Onboarding)</div>",
        unsafe_allow_html=True,
    )
with col_year_select:
    selected_year_onboarding = st.multiselect(
        "Filtro Año Onboarding",
        options=anios_disponibles,
        default=[],
        placeholder="Todos los años (selecciona para filtrar)...",
        label_visibility="collapsed",
        key="_year_filter",
    )

if selected_year_onboarding:
    df_filtered = df[mask_sidebar & (df["mes_onboarding"].str[:4].isin(selected_year_onboarding))]
else:
    df_filtered = df[mask_sidebar]

if df_filtered.empty:
    st.warning("⚠️ Ningún comercio coincide con los filtros seleccionados. Ajusta la selección.")
    st.stop()

# ==========================================
# 4. TABS (VISTAS PRINCIPALES)
# ==========================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Resumen",
    "📅 Cohortes",
    "💼 Inteligencia",
    "🗺️ Geoespacial",
    "🔍 Perfil Profundo",
])

# ------------------------------------------
# TAB 1: RESUMEN EJECUTIVO
# ------------------------------------------
with tab1:
    st.markdown("### 📊 Panel Ejecutivo de Riesgo de Abandono (Próximos 30 días)")
    st.markdown(
        "<p style='color:#94A3B8; margin-bottom:18px;'>"
        "Visión general de la salud del portafolio y exposición al riesgo.</p>",
        unsafe_allow_html=True,
    )

    total_merchants = len(df_filtered)
    merchants_at_risk = len(df_filtered[df_filtered["nivel_riesgo"].isin(["Alto", "Crítico"])])
    churn_rate = (merchants_at_risk / total_merchants) * 100 if total_merchants else 0
    tpv_at_risk = df_filtered[df_filtered["nivel_riesgo"].isin(["Alto", "Crítico"])]["clv_proyectado"].sum()
    score_promedio = df_filtered["score_salud"].mean() if total_merchants else 0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Comercios", f"{total_merchants:,}")
    col2.metric(
        "Comercios en Riesgo",
        f"{merchants_at_risk:,}",
        delta=f"{churn_rate:.1f}% Tasa Riesgo",
        delta_color="inverse",
    )
    col3.metric(
        "CLV en Riesgo (USD)",
        f"${tpv_at_risk:,.0f}",
        delta="Proyectado a 30 días",
        delta_color="off",
    )
    col4.metric(
        "Salud del Portafolio",
        f"{score_promedio:.1f} / 100",
        delta="Score Promedio",
        delta_color="normal",
    )

    st.divider()

    col_chart1, col_chart2 = st.columns([1, 1])

    with col_chart1:
        risk_counts = df_filtered["nivel_riesgo"].value_counts().reset_index()
        risk_counts.columns = ["Nivel de Riesgo", "Cantidad"]

        fig_pie = px.pie(
            risk_counts,
            values="Cantidad",
            names="Nivel de Riesgo",
            color="Nivel de Riesgo",
            color_discrete_map=RISK_COLORS,
            hole=0.7,
        )
        fig_pie.update_traces(
            textposition="auto",
            textinfo="percent+label",
            textfont=dict(color="#F8FAFC", size=13),
            marker=dict(line=dict(color="#0B0F19", width=3)),
            hoverinfo="label+percent+value",
        )
        fig_pie.update_layout(
            title=dict(text="Distribución por Nivel de Riesgo", font=dict(size=17, color="#F8FAFC")),
            showlegend=False,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(t=50, b=20, l=20, r=20),
            annotations=[
                dict(
                    text=f"{total_merchants:,}<br>Comercios",
                    x=0.5,
                    y=0.5,
                    font_size=15,
                    font_color="#CBD5E1",
                    showarrow=False,
                )
            ],
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    with col_chart2:
        ciiu_risk = (
            df_filtered.groupby("tipo_negocio_desc")["probabilidad_churn"]
            .mean()
            .reset_index()
            .sort_values("probabilidad_churn", ascending=True)
        )

        fig_bar = px.bar(
            ciiu_risk,
            x="probabilidad_churn",
            y="tipo_negocio_desc",
            orientation="h",
            text="probabilidad_churn",
        )
        fig_bar.update_traces(
            marker=dict(
                color=ciiu_risk["probabilidad_churn"],
                colorscale=[[0, DEUNA_PRIMARY], [0.5, DEUNA_ACCENT], [1, DEUNA_MAGENTA]],
                line_width=0,
            ),
            texttemplate="%{text:.1%}",
            textposition="auto",
            textfont=dict(color="#F8FAFC", size=12),
        )
        fig_bar.update_layout(
            title=dict(text="Riesgo Promedio por Segmento", font=dict(size=17, color="#F8FAFC")),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#E2E8F0"),
            xaxis=dict(showgrid=False, visible=False),
            yaxis=dict(showgrid=False, title="", tickfont=dict(size=12)),
            margin=dict(t=50, b=20, l=10, r=20),
        )
        st.plotly_chart(fig_bar, use_container_width=True)

# ------------------------------------------
# TAB 2: MATRIZ DE COHORTES
# ------------------------------------------
with tab2:
    st.markdown("### 📅 Análisis de Cohortes")
    st.markdown(
        "<p style='color:#94A3B8; margin-bottom:18px;'>"
        "Evolución de la probabilidad de abandono según el mes de onboarding y segmento comercial.</p>",
        unsafe_allow_html=True,
    )

    cohort_data = (
        df_filtered.groupby(["mes_onboarding", "segmento_comercial"])["probabilidad_churn"]
        .mean()
        .reset_index()
    )
    cohort_pivot = cohort_data.pivot(
        index="mes_onboarding", columns="segmento_comercial", values="probabilidad_churn"
    ).fillna(0)

    custom_color_scale = [
        [0.0, "#1E1B38"],
        [0.4, DEUNA_PRIMARY],
        [0.75, DEUNA_ACCENT],
        [1.0, DEUNA_MAGENTA],
    ]

    fig_heatmap = px.imshow(
        cohort_pivot,
        labels=dict(x="", y="", color="Probabilidad Churn"),
        x=cohort_pivot.columns,
        y=cohort_pivot.index,
        color_continuous_scale=custom_color_scale,
        aspect="auto",
        text_auto=".1%",
    )
    fig_heatmap.update_traces(
        xgap=4,
        ygap=4,
        hovertemplate="<b>Mes:</b> %{y}<br><b>Segmento:</b> %{x}<br><b>Riesgo:</b> %{z:.1%}<extra></extra>",
        textfont=dict(family="Inter", color="#F8FAFC", size=12),
    )
    fig_heatmap.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#E2E8F0", family="Inter"),
        margin=dict(t=10, b=30, l=10, r=10),
        xaxis=dict(side="bottom", tickfont=dict(size=12, color="#CBD5E1"), showgrid=False),
        yaxis=dict(tickfont=dict(size=12, color="#CBD5E1"), showgrid=False, autorange="reversed"),
        coloraxis_showscale=False,
    )

    st.markdown(
        "<div style='background:rgba(30,27,56,0.55); padding:18px; border-radius:14px; "
        "border:1px solid rgba(168,85,247,0.18);'>",
        unsafe_allow_html=True,
    )
    st.plotly_chart(fig_heatmap, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ------------------------------------------
# TAB 3: INTELIGENCIA DE CUENTAS
# ------------------------------------------
with tab3:
    head_col1, head_col2 = st.columns([3, 1])

    with head_col1:
        st.markdown("### 💼 Workspace de Retención")
        st.markdown(
            "<p style='color:#94A3B8; margin-bottom:16px;'>"
            "Lista priorizada de comercios con acciones de retención sugeridas (Next Best Action).</p>",
            unsafe_allow_html=True,
        )

    # Copia para no mutar df_filtered
    work_df = df_filtered.copy()
    if "ejecutivo_cuenta" not in work_df.columns:
        work_df["ejecutivo_cuenta"] = np.where(
            work_df["segmento_comercial"] == "Microempresa", "Auto-gestionado", "KAM Asignado"
        )

    display_cols = [
        "merchant_id",
        "nombre_comercio",
        "nivel_riesgo",
        "probabilidad_churn",
        "clv_proyectado",
        "nba_sugerida",
        "ejecutivo_cuenta",
    ]
    table_df = work_df[display_cols].sort_values(by="probabilidad_churn", ascending=False).copy()

    def format_risk_icon(val: str) -> str:
        icons = {"Crítico": "🔴 Crítico", "Alto": "🟠 Alto", "Medio": "🟡 Medio", "Bajo": "🟢 Bajo"}
        return icons.get(val, val)

    table_df["nivel_riesgo"] = table_df["nivel_riesgo"].apply(format_risk_icon)

    with head_col2:
        st.markdown("<div style='height:38px;'></div>", unsafe_allow_html=True)
        csv = table_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="⬇️ Exportar Plan (CSV)",
            data=csv,
            file_name="plan_retencion_deuna.csv",
            mime="text/csv",
            use_container_width=True,
        )

    st.dataframe(
        table_df,
        column_config={
            "merchant_id": st.column_config.TextColumn("ID Comercio", width="small"),
            "nombre_comercio": st.column_config.TextColumn("Nombre", width="medium"),
            "nivel_riesgo": st.column_config.TextColumn("Alerta", width="small"),
            "probabilidad_churn": st.column_config.ProgressColumn(
                "Riesgo de Fuga",
                help="Probabilidad calculada por el modelo predictivo (0 a 1)",
                format="%.2f",
                min_value=0,
                max_value=1,
            ),
            "clv_proyectado": st.column_config.NumberColumn(
                "CLV en Riesgo",
                help="Valor proyectado a 30 días",
                format="$ %.0f",
            ),
            "nba_sugerida": st.column_config.TextColumn(
                "Next Best Action (Sugerencia)", width="large"
            ),
            "ejecutivo_cuenta": st.column_config.TextColumn("Ejecutivo"),
        },
        hide_index=True,
        use_container_width=True,
        height=450,
    )

# ------------------------------------------
# TAB 4: MAPA GEOESPACIAL
# ------------------------------------------
with tab4:
    st.markdown("### 🗺️ Focos Geográficos de Riesgo")
    st.markdown(
        "<p style='color:#94A3B8; margin-bottom:16px;'>"
        "Identifica zonas con alta concentración de riesgo para enfocar visitas de campo y campañas locales.</p>",
        unsafe_allow_html=True,
    )

    col_map, col_geo_kpi = st.columns([3, 1])

    with col_map:
        fig_map = px.scatter_mapbox(
            df_filtered,
            lat="latitud",
            lon="longitud",
            color="nivel_riesgo",
            size="clv_proyectado",
            color_discrete_map=RISK_COLORS,
            hover_name="nombre_comercio",
            hover_data={
                "nivel_riesgo": True,
                "probabilidad_churn": ":.1%",
                "clv_proyectado": ":$,.0f",
                "latitud": False,
                "longitud": False,
            },
            zoom=5.5,
            center={"lat": -1.8312, "lon": -78.1834},
            mapbox_style="carto-darkmatter",
        )
        fig_map.update_traces(marker=dict(opacity=0.85, sizemin=5))
        fig_map.update_layout(
            margin={"r": 0, "t": 0, "l": 0, "b": 0},
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            showlegend=True,
            legend=dict(
                title=dict(text=""),
                yanchor="top",
                y=0.98,
                xanchor="left",
                x=0.02,
                bgcolor="rgba(15, 23, 42, 0.85)",
                font=dict(color="#E2E8F0", size=12),
                bordercolor="rgba(168,85,247,0.35)",
                borderwidth=1,
                itemsizing="constant",
            ),
        )

        st.markdown(
            "<div style='border:1px solid rgba(168,85,247,0.25); border-radius:14px; "
            "overflow:hidden; box-shadow: 0 4px 18px rgba(15,10,35,0.35);'>",
            unsafe_allow_html=True,
        )
        st.plotly_chart(fig_map, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_geo_kpi:
        st.markdown(
            "<h4 style='font-size:16px; color:#F8FAFC; margin:4px 0 14px;'>"
            "📍 Top Zonas en Alerta</h4>",
            unsafe_allow_html=True,
        )

        df_risk_geo = df_filtered[df_filtered["nivel_riesgo"].isin(["Alto", "Crítico"])]

        if not df_risk_geo.empty:
            risk_by_region = (
                df_risk_geo.groupby("region")
                .agg(comercios=("merchant_id", "count"), clv_peligro=("clv_proyectado", "sum"))
                .reset_index()
                .sort_values("comercios", ascending=False)
                .head(4)
            )

            for _, row in risk_by_region.iterrows():
                st.markdown(
                    f"""
                    <div style='background: rgba(30,27,56,0.75); padding:14px 16px; border-radius:12px;
                                margin-bottom:10px; border:1px solid rgba(168,85,247,0.2);
                                border-left:4px solid #EF4444;'>
                        <p style='margin:0; font-size:12px; color:#94A3B8; font-weight:700;
                                  text-transform:uppercase; letter-spacing:0.05em;'>{row['region']}</p>
                        <p style='margin:4px 0 0; font-size:22px; color:#F8FAFC; font-weight:800;'>
                            {row['comercios']}
                            <span style='font-size:12px; color:#EF4444; font-weight:600;'> locales</span>
                        </p>
                        <p style='margin:2px 0 0; font-size:12px; color:#94A3B8;'>
                            Riesgo: ${row['clv_peligro']:,.0f} USD
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.info("No hay comercios en riesgo Alto/Crítico en la selección actual.")

        st.markdown(
            "<p style='font-size:12px; color:#64748B; line-height:1.4; margin-top:8px;'>"
            "*El panel muestra las regiones con mayor volumen de locales en riesgo "
            "<b>Alto</b> o <b>Crítico</b>.</p>",
            unsafe_allow_html=True,
        )

# ------------------------------------------
# TAB 5: PERFIL PROFUNDO
# ------------------------------------------
with tab5:
    st.markdown("### 🔍 Análisis a Nivel de Cuenta (Explainable AI)")
    st.markdown(
        "<p style='color:#94A3B8; margin-bottom:16px;'>"
        "Radiografía individual para entender los conductores de fuga.</p>",
        unsafe_allow_html=True,
    )

    formated_merchants = df_filtered["merchant_id"] + " - " + df_filtered["nombre_comercio"]
    selected_option = st.selectbox(
        "Busca o Selecciona un Comercio:",
        formated_merchants.tolist(),
    )

    if selected_option:
        selected_merchant_id = selected_option.split(" - ")[0]
        merchant_data = df_filtered[df_filtered["merchant_id"] == selected_merchant_id].iloc[0]

        col_prof1, col_prof2 = st.columns([1, 1.5])

        with col_prof1:
            risk_color = RISK_COLORS.get(merchant_data["nivel_riesgo"], "#F8FAFC")

            profile_html = textwrap.dedent(
                f"""
                <div style='background:rgba(30,27,56,0.8); padding:22px; border-radius:14px;
                            border:1px solid rgba(168,85,247,0.25);'>
                    <h3 style='margin:0; color:#F8FAFC; font-size:20px;'>{merchant_data['nombre_comercio']}</h3>
                    <p style='color:#94A3B8; font-size:12px; margin-bottom:18px; font-family:monospace;'>
                        ID: {merchant_data['merchant_id']}
                    </p>
                    <div style='display:flex; justify-content:space-between; border-bottom:1px solid rgba(168,85,247,0.18);
                                padding-bottom:8px; margin-bottom:8px;'>
                        <span style='color:#94A3B8; font-size:13px;'>Segmento</span>
                        <span style='color:#F8FAFC; font-weight:600;'>{merchant_data['segmento_comercial']}</span>
                    </div>
                    <div style='display:flex; justify-content:space-between; border-bottom:1px solid rgba(168,85,247,0.18);
                                padding-bottom:8px; margin-bottom:8px;'>
                        <span style='color:#94A3B8; font-size:13px;'>Región</span>
                        <span style='color:#F8FAFC; font-weight:600;'>{merchant_data['region']}</span>
                    </div>
                    <div style='background:#0F172A; padding:14px; border-radius:10px; text-align:center;
                                border-left:4px solid {risk_color}; margin:18px 0;'>
                        <p style='margin:0; color:#94A3B8; font-size:12px;'>PROBABILIDAD DE FUGA</p>
                        <h2 style='margin:5px 0; color:{risk_color}; font-size:30px;'>
                            {merchant_data['probabilidad_churn']*100:.1f}%
                        </h2>
                    </div>
                    <div style='background:linear-gradient(135deg, rgba(124,58,237,0.18), rgba(236,72,153,0.14));
                                border:1px dashed {DEUNA_ACCENT}; padding:14px; border-radius:10px;'>
                        <p style='margin:0; color:{DEUNA_ACCENT}; font-size:12px; font-weight:800;'>💡 NEXT BEST ACTION</p>
                        <p style='margin:6px 0 0; color:#F8FAFC; font-size:14px;'>{merchant_data['nba_sugerida']}</p>
                    </div>
                </div>
                """
            )
            st.markdown(profile_html, unsafe_allow_html=True)

        with col_prof2:
            with st.container():
                st.markdown(
                    textwrap.dedent(
                        """
                        <div style='background:rgba(15,23,42,0.7); padding:18px; border-radius:14px;
                                    border:1px solid rgba(168,85,247,0.2); margin-bottom:12px;'>
                            <h4 style='color:#F8FAFC; margin:0;'>Principales Drivers de Abandono</h4>
                            <p style='color:#94A3B8; font-size:13px; margin:4px 0 0;'>
                                Impacto de variables en el modelo (SHAP).
                            </p>
                        </div>
                        """
                    ),
                    unsafe_allow_html=True,
                )

                driver_1 = str(merchant_data["driver_1_nombre"]).replace("_", " ").title()
                driver_2 = str(merchant_data["driver_2_nombre"]).replace("_", " ").title()

                shap_df = pd.DataFrame(
                    {
                        "Driver": [driver_1, driver_2],
                        "Impacto": [
                            merchant_data["driver_1_shap"],
                            merchant_data["driver_2_shap"],
                        ],
                    }
                ).sort_values(by="Impacto")

                fig_shap = px.bar(shap_df, x="Impacto", y="Driver", orientation="h", text_auto=".3f")
                fig_shap.update_traces(
                    marker=dict(
                        color=shap_df["Impacto"],
                        colorscale=[[0, DEUNA_PRIMARY], [1, DEUNA_MAGENTA]],
                    ),
                    width=0.4,
                    textposition="auto",
                    cliponaxis=False,
                )
                fig_shap.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#E2E8F0"),
                    xaxis=dict(showgrid=True, gridcolor="rgba(168,85,247,0.12)"),
                    yaxis=dict(showgrid=False, title=""),
                    margin=dict(t=20, b=20, l=10, r=20),
                    height=300,
                )
                st.plotly_chart(fig_shap, use_container_width=True)

# modules/anuncios_publicitarios.py

import pandas as pd
import plotly.express as px
import streamlit as st

# Colores por periodo
YEAR_COLORS = {
    "2023": "#e74c3c",
    "2024": "#3498db",
    "2025": "#2ecc71",
    "2026 (E y F)": "#f39c12",
}

YEAR_ORDER = ["2023", "2024", "2025", "2026 (E y F)"]


def load_anuncios_publicitarios_data():
    """Carga datos fijos de anuncios publicitarios."""
    data = [
        {"AÑO": "2023", "N_CERT_EMITIDOS": 360, "RECAUDACION": 25292.20},
        {"AÑO": "2024", "N_CERT_EMITIDOS": 348, "RECAUDACION": 30868.90},
        {"AÑO": "2025", "N_CERT_EMITIDOS": 456, "RECAUDACION": 36344.30},
        {"AÑO": "2026 (E y F)", "N_CERT_EMITIDOS": 46, "RECAUDACION": 4168.20},
    ]

    df = pd.DataFrame(data)

    # Forzar a texto para que Plotly no lo trate como numérico
    df["AÑO"] = df["AÑO"].astype(str)

    return df


def estadisticas_generales(df):
    """Mostrar KPIs generales."""
    st.subheader("📊 Estadísticas Generales")

    c1, c2, c3, c4 = st.columns(4)

    total_certificados = int(df["N_CERT_EMITIDOS"].sum())
    total_recaudado = float(df["RECAUDACION"].sum())
    periodo_max_cert = df.loc[df["N_CERT_EMITIDOS"].idxmax(), "AÑO"]
    promedio_certificados = df["N_CERT_EMITIDOS"].mean()

    c1.metric("📄 Total Certificados", f"{total_certificados:,}")
    c2.metric("💰 Recaudación Total", f"S/ {total_recaudado:,.2f}")
    c3.metric("🏆 Periodo Más Activo", periodo_max_cert)
    c4.metric("📈 Promedio Certificados", f"{promedio_certificados:.1f}")


def grafico_certificados_emitidos(df):
    """Gráfico de barras de certificados emitidos por año."""
    st.subheader("📄 Certificados Emitidos por Año")

    fig = px.bar(
        df,
        x="AÑO",
        y="N_CERT_EMITIDOS",
        color="AÑO",
        text="N_CERT_EMITIDOS",
        color_discrete_map=YEAR_COLORS,
        category_orders={"AÑO": YEAR_ORDER},
        height=420,
        labels={
            "AÑO": "Año",
            "N_CERT_EMITIDOS": "N° de Certificados Emitidos"
        }
    )

    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis_title="Año",
        yaxis_title="N° de Certificados Emitidos",
        showlegend=False
    )

    # Forzar eje categórico
    fig.update_xaxes(type="category")

    fig.update_traces(
        textposition="outside",
        marker_line_color="rgba(0,0,0,0.3)",
        marker_line_width=2
    )

    st.plotly_chart(fig, use_container_width=True)


def grafico_recaudacion(df):
    """Gráfico de barras de recaudación por año."""
    st.subheader("💰 Recaudación por Año")

    fig = px.bar(
        df,
        x="AÑO",
        y="RECAUDACION",
        color="AÑO",
        text="RECAUDACION",
        color_discrete_map=YEAR_COLORS,
        category_orders={"AÑO": YEAR_ORDER},
        height=420,
        labels={
            "AÑO": "Año",
            "RECAUDACION": "Recaudación (S/)"
        }
    )

    fig.update_traces(
        texttemplate="S/ %{y:,.2f}",
        textposition="outside",
        marker_line_color="rgba(0,0,0,0.3)",
        marker_line_width=2
    )

    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis_title="Año",
        yaxis_title="Recaudación (S/)",
        showlegend=False
    )

    # Forzar eje categórico
    fig.update_xaxes(type="category")

    st.plotly_chart(fig, use_container_width=True)


def grafico_comparativo(df):
    """Gráfico comparativo entre certificados y recaudación."""
    st.subheader("📈 Comparativo General")

    df_chart = df.copy()

    fig = px.scatter(
        df_chart,
        x="N_CERT_EMITIDOS",
        y="RECAUDACION",
        color="AÑO",
        size="N_CERT_EMITIDOS",
        text="AÑO",
        color_discrete_map=YEAR_COLORS,
        category_orders={"AÑO": YEAR_ORDER},
        height=450,
        labels={
            "N_CERT_EMITIDOS": "N° de Certificados Emitidos",
            "RECAUDACION": "Recaudación (S/)"
        }
    )

    fig.update_traces(
        textposition="top center",
        marker=dict(line=dict(width=1, color="rgba(0,0,0,0.3)"))
    )

    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis_title="N° de Certificados Emitidos",
        yaxis_title="Recaudación (S/)"
    )

    st.plotly_chart(fig, use_container_width=True)


def tabla_resumen(df):
    """Tabla resumen de anuncios publicitarios."""
    st.subheader("📋 Tabla Resumen")

    tabla_df = df.copy()
    tabla_df = tabla_df.rename(columns={
        "AÑO": "Año",
        "N_CERT_EMITIDOS": "N° Cert. Emitidos",
        "RECAUDACION": "Recaudación"
    })

    st.dataframe(
        tabla_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Año": st.column_config.TextColumn("Año", width="medium"),
            "N° Cert. Emitidos": st.column_config.NumberColumn("N° Cert. Emitidos", format="%d"),
            "Recaudación": st.column_config.NumberColumn("Recaudación", format="S/ %.2f"),
        }
    )


def observaciones(df):
    """Bloque de observaciones automáticas."""
    st.subheader("📝 Observaciones")

    periodo_max_cert = df.loc[df["N_CERT_EMITIDOS"].idxmax(), "AÑO"]
    periodo_max_rec = df.loc[df["RECAUDACION"].idxmax(), "AÑO"]

    st.info(
        f"""
- El periodo con mayor cantidad de certificados emitidos fue **{periodo_max_cert}**.
- El periodo con mayor recaudación fue **{periodo_max_rec}**.
- El registro **2026 (E y F)** corresponde únicamente a **enero y febrero**.
"""
    )


def show_anuncios_publicitarios_module():
    """Módulo completo de Anuncios Publicitarios."""
    st.header("📢 Módulo de Anuncios Publicitarios")
    st.markdown("---")

    df = load_anuncios_publicitarios_data()

    if df is None or df.empty:
        st.error("No se pudieron cargar los datos.")
        return

    estadisticas_generales(df)
    st.markdown("---")

    grafico_certificados_emitidos(df)
    st.markdown("---")

    grafico_recaudacion(df)
    st.markdown("---")

    grafico_comparativo(df)
    st.markdown("---")

    tabla_resumen(df)
    st.markdown("---")

    observaciones(df)
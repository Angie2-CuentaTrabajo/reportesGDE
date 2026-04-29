import pandas as pd
import plotly.express as px
import streamlit as st

# Colores por periodo
YEAR_COLORS = {
    "2023": "#e74c3c",
    "2024": "#3498db",
    "2025": "#2ecc71",
    "2026 (Ene-Abr)": "#f39c12",
}

YEAR_ORDER = ["2023", "2024", "2025", "2026 (Ene-Abr)"]

RISK_COLORS = {
    "MEDIO": "#3498db",
    "ALTOS Y MUY ALTOS": "#e74c3c",
    "IMPROCEDENTES": "#95a5a6",
}


def load_licencias_funcionamiento_data():
    """Carga los datos fijos de Licencias de Funcionamiento."""

    # Detalle transcrito del cuadro fuente
    detalle_data = [
        {"PERIODO": "2023", "RIESGO_DETALLE": "MEDIO", "RIESGO_AGRUPADO": "MEDIO", "EXPEDIENTES": 500, "COSTO": 200.90, "TOTAL": 100450.00},
        {"PERIODO": "2023", "RIESGO_DETALLE": "ALTOS Y MUY ALTOS", "RIESGO_AGRUPADO": "ALTOS Y MUY ALTOS", "EXPEDIENTES": 300, "COSTO": 678.90, "TOTAL": 203670.00},
        {"PERIODO": "2023", "RIESGO_DETALLE": "IMPROCEDENTES", "RIESGO_AGRUPADO": "IMPROCEDENTES", "EXPEDIENTES": 50, "COSTO": 200.90, "TOTAL": 10045.00},

        {"PERIODO": "2024", "RIESGO_DETALLE": "MEDIO", "RIESGO_AGRUPADO": "MEDIO", "EXPEDIENTES": 600, "COSTO": 200.90, "TOTAL": 120540.00},
        {"PERIODO": "2024", "RIESGO_DETALLE": "ALTOS Y MUY ALTOS", "RIESGO_AGRUPADO": "ALTOS Y MUY ALTOS", "EXPEDIENTES": 200, "COSTO": 678.90, "TOTAL": 135780.00},
        {"PERIODO": "2024", "RIESGO_DETALLE": "IMPROCEDENTES", "RIESGO_AGRUPADO": "IMPROCEDENTES", "EXPEDIENTES": 100, "COSTO": 200.90, "TOTAL": 20090.00},

        {"PERIODO": "2025", "RIESGO_DETALLE": "MEDIO", "RIESGO_AGRUPADO": "MEDIO", "EXPEDIENTES": 600, "COSTO": 200.90, "TOTAL": 120540.00},
        {"PERIODO": "2025", "RIESGO_DETALLE": "ALTOS Y MUY ALTOS", "RIESGO_AGRUPADO": "ALTOS Y MUY ALTOS", "EXPEDIENTES": 350, "COSTO": 678.90, "TOTAL": 237615.00},
        {"PERIODO": "2025", "RIESGO_DETALLE": "IMPROCEDENTES", "RIESGO_AGRUPADO": "IMPROCEDENTES", "EXPEDIENTES": 60, "COSTO": 200.90, "TOTAL": 12054.00},

        {"PERIODO": "2026 (Ene-Abr)", "RIESGO_DETALLE": "MEDIO DEL MES DE ENERO", "RIESGO_AGRUPADO": "MEDIO", "EXPEDIENTES": 67, "COSTO": 200.90, "TOTAL": 13460.30},
        {"PERIODO": "2026 (Ene-Abr)", "RIESGO_DETALLE": "MEDIO DEL MES DE FEBRERO", "RIESGO_AGRUPADO": "MEDIO", "EXPEDIENTES": 67, "COSTO": 193.20, "TOTAL": 12944.00},
        {"PERIODO": "2026 (Ene-Abr)", "RIESGO_DETALLE": "MEDIO DEL MES DE MARZO", "RIESGO_AGRUPADO": "MEDIO", "EXPEDIENTES": 61, "COSTO": 193.20, "TOTAL": 11785.20},
        {"PERIODO": "2026 (Ene-Abr)", "RIESGO_DETALLE": "MEDIO DEL MES DE ABRIL", "RIESGO_AGRUPADO": "MEDIO", "EXPEDIENTES": 29, "COSTO": 193.20, "TOTAL": 5602.80},
        {"PERIODO": "2026 (Ene-Abr)", "RIESGO_DETALLE": "ALTOS Y MUY ALTOS DEL MES DE ENERO", "RIESGO_AGRUPADO": "ALTOS Y MUY ALTOS", "EXPEDIENTES": 5, "COSTO": 678.90, "TOTAL": 3395.00},
        {"PERIODO": "2026 (Ene-Abr)", "RIESGO_DETALLE": "ALTOS Y MUY ALTOS DEL MES DE FEBRERO", "RIESGO_AGRUPADO": "ALTOS Y MUY ALTOS", "EXPEDIENTES": 5, "COSTO": 678.90, "TOTAL": 3395.00},
        {"PERIODO": "2026 (Ene-Abr)", "RIESGO_DETALLE": "ALTO DEL MES DE MARZO", "RIESGO_AGRUPADO": "ALTOS Y MUY ALTOS", "EXPEDIENTES": 3, "COSTO": 356.40, "TOTAL": 1069.20},
        {"PERIODO": "2026 (Ene-Abr)", "RIESGO_DETALLE": "ALTO DEL MES DE ABRIL", "RIESGO_AGRUPADO": "ALTOS Y MUY ALTOS", "EXPEDIENTES": 1, "COSTO": 356.40, "TOTAL": 356.40},
        {"PERIODO": "2026 (Ene-Abr)", "RIESGO_DETALLE": "MUY ALTO DEL MES DE MARZO", "RIESGO_AGRUPADO": "ALTOS Y MUY ALTOS", "EXPEDIENTES": 27, "COSTO": 631.20, "TOTAL": 17042.40},
        {"PERIODO": "2026 (Ene-Abr)", "RIESGO_DETALLE": "MUY ALTO DEL MES DE ABRIL", "RIESGO_AGRUPADO": "ALTOS Y MUY ALTOS", "EXPEDIENTES": 20, "COSTO": 631.20, "TOTAL": 12624.00},
        {"PERIODO": "2026 (Ene-Abr)", "RIESGO_DETALLE": "IMPROCEDENTES", "RIESGO_AGRUPADO": "IMPROCEDENTES", "EXPEDIENTES": 3, "COSTO": 200.90, "TOTAL": 603.00},
    ]

    # Resumen anual según el total consolidado mostrado en tu cuadro
    resumen_data = [
        {"PERIODO": "2023", "EXPEDIENTES": 850, "RECAUDACION": 314165.00},
        {"PERIODO": "2024", "EXPEDIENTES": 900, "RECAUDACION": 276410.00},
        {"PERIODO": "2025", "EXPEDIENTES": 1010, "RECAUDACION": 370209.00},
        {"PERIODO": "2026 (Ene-Abr)", "EXPEDIENTES": 288, "RECAUDACION": 82276.00},
    ]

    detalle_df = pd.DataFrame(detalle_data)
    resumen_df = pd.DataFrame(resumen_data)

    detalle_df["PERIODO"] = pd.Categorical(detalle_df["PERIODO"], categories=YEAR_ORDER, ordered=True)
    resumen_df["PERIODO"] = pd.Categorical(resumen_df["PERIODO"], categories=YEAR_ORDER, ordered=True)

    return detalle_df, resumen_df


def estadisticas_generales(resumen_df):
    st.subheader("📊 Estadísticas Generales")

    c1, c2, c3, c4 = st.columns(4)

    total_expedientes = int(resumen_df["EXPEDIENTES"].sum())
    total_recaudado = float(resumen_df["RECAUDACION"].sum())
    periodo_max = resumen_df.loc[resumen_df["RECAUDACION"].idxmax(), "PERIODO"]
    promedio_expedientes = resumen_df["EXPEDIENTES"].mean()

    c1.metric("📁 Total Expedientes", f"{total_expedientes:,}")
    c2.metric("💰 Recaudación Total", f"S/ {total_recaudado:,.2f}")
    c3.metric("🏆 Mayor Recaudación", str(periodo_max))
    c4.metric("📈 Promedio Expedientes", f"{promedio_expedientes:.1f}")


def grafico_expedientes(resumen_df):
    st.subheader("📁 Expedientes por Año")

    fig = px.bar(
        resumen_df,
        x="PERIODO",
        y="EXPEDIENTES",
        color="PERIODO",
        text="EXPEDIENTES",
        color_discrete_map=YEAR_COLORS,
        category_orders={"PERIODO": YEAR_ORDER},
        height=420,
        labels={"PERIODO": "Año", "EXPEDIENTES": "N° de Expedientes"}
    )

    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis_title="Año",
        yaxis_title="N° de Expedientes",
        showlegend=False
    )

    fig.update_xaxes(type="category")
    fig.update_traces(
        textposition="outside",
        marker_line_color="rgba(0,0,0,0.3)",
        marker_line_width=2
    )

    st.plotly_chart(fig, use_container_width=True)


def grafico_recaudacion(resumen_df):
    st.subheader("💰 Recaudación por Año")

    fig = px.bar(
        resumen_df,
        x="PERIODO",
        y="RECAUDACION",
        color="PERIODO",
        text="RECAUDACION",
        color_discrete_map=YEAR_COLORS,
        category_orders={"PERIODO": YEAR_ORDER},
        height=420,
        labels={"PERIODO": "Año", "RECAUDACION": "Recaudación (S/)"}
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

    fig.update_xaxes(type="category")

    st.plotly_chart(fig, use_container_width=True)


def grafico_riesgo_apilado(detalle_df):
    st.subheader("📚 Expedientes por Riesgo")

    riesgo_resumen = (
        detalle_df.groupby(["PERIODO", "RIESGO_AGRUPADO"], observed=False)["EXPEDIENTES"]
        .sum()
        .reset_index()
    )

    fig = px.bar(
        riesgo_resumen,
        x="PERIODO",
        y="EXPEDIENTES",
        color="RIESGO_AGRUPADO",
        barmode="stack",
        category_orders={"PERIODO": YEAR_ORDER},
        color_discrete_map=RISK_COLORS,
        height=450,
        labels={
            "PERIODO": "Año",
            "EXPEDIENTES": "N° de Expedientes",
            "RIESGO_AGRUPADO": "Riesgo"
        }
    )

    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis_title="Año",
        yaxis_title="N° de Expedientes",
        legend_title="Riesgo"
    )

    fig.update_xaxes(type="category")

    st.plotly_chart(fig, use_container_width=True)


def grafico_recaudacion_riesgo(detalle_df):
    st.subheader("💳 Recaudación por Riesgo")

    riesgo_recaudacion = (
        detalle_df.groupby(["PERIODO", "RIESGO_AGRUPADO"], observed=False)["TOTAL"]
        .sum()
        .reset_index()
    )

    fig = px.bar(
        riesgo_recaudacion,
        x="PERIODO",
        y="TOTAL",
        color="RIESGO_AGRUPADO",
        barmode="group",
        category_orders={"PERIODO": YEAR_ORDER},
        color_discrete_map=RISK_COLORS,
        height=450,
        labels={
            "PERIODO": "Año",
            "TOTAL": "Recaudación (S/)",
            "RIESGO_AGRUPADO": "Riesgo"
        }
    )

    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis_title="Año",
        yaxis_title="Recaudación (S/)",
        legend_title="Riesgo"
    )

    fig.update_xaxes(type="category")

    st.plotly_chart(fig, use_container_width=True)


def tabla_resumen_anual(resumen_df):
    st.subheader("📋 Tabla Resumen Anual")

    tabla_df = resumen_df.copy().rename(columns={
        "PERIODO": "Año",
        "EXPEDIENTES": "N° Expedientes",
        "RECAUDACION": "Recaudación"
    })

    st.dataframe(
        tabla_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Año": st.column_config.TextColumn("Año", width="medium"),
            "N° Expedientes": st.column_config.NumberColumn("N° Expedientes", format="%d"),
            "Recaudación": st.column_config.NumberColumn("Recaudación", format="S/ %.2f"),
        }
    )


def tabla_detallada(detalle_df):
    st.subheader("🧾 Detalle por Riesgo")

    tabla_df = detalle_df.copy().rename(columns={
        "PERIODO": "Año",
        "RIESGO_DETALLE": "Riesgo",
        "EXPEDIENTES": "Expedientes",
        "COSTO": "Costo",
        "TOTAL": "Total"
    })

    tabla_df = tabla_df[["Año", "Riesgo", "Expedientes", "Costo", "Total"]]

    st.dataframe(
        tabla_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Año": st.column_config.TextColumn("Año", width="small"),
            "Riesgo": st.column_config.TextColumn("Riesgo", width="large"),
            "Expedientes": st.column_config.NumberColumn("Expedientes", format="%d"),
            "Costo": st.column_config.NumberColumn("Costo", format="S/ %.2f"),
            "Total": st.column_config.NumberColumn("Total", format="S/ %.2f"),
        }
    )


def observaciones(resumen_df):
    st.subheader("📝 Observaciones")

    periodo_max_exp = resumen_df.loc[resumen_df["EXPEDIENTES"].idxmax(), "PERIODO"]
    periodo_max_rec = resumen_df.loc[resumen_df["RECAUDACION"].idxmax(), "PERIODO"]

    st.info(
        f"""
- El periodo con mayor número de expedientes fue **{periodo_max_exp}**.
- El periodo con mayor recaudación fue **{periodo_max_rec}**.
- El registro **2026 (Ene-Abr)** corresponde a **enero, febrero, marzo y abril**.
- Los totales anuales se han consignado según el cuadro consolidado fuente.
"""
    )


def show_licencias_funcionamiento_module():
    st.header("🏢 Módulo de Licencias de Funcionamiento")
    st.markdown("---")

    detalle_df, resumen_df = load_licencias_funcionamiento_data()

    if resumen_df is None or resumen_df.empty:
        st.error("No se pudieron cargar los datos.")
        return

    estadisticas_generales(resumen_df)
    st.markdown("---")

    grafico_expedientes(resumen_df)
    st.markdown("---")

    grafico_recaudacion(resumen_df)
    st.markdown("---")

    grafico_riesgo_apilado(detalle_df)
    st.markdown("---")

    grafico_recaudacion_riesgo(detalle_df)
    st.markdown("---")

    tabla_resumen_anual(resumen_df)
    st.markdown("---")

    tabla_detallada(detalle_df)
    st.markdown("---")

    observaciones(resumen_df)

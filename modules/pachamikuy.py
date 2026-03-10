# modules/pachamikuy.py

import pandas as pd
import plotly.express as px
import streamlit as st

YEAR_COLORS = {
    "2025": "#2ecc71",
    "2026": "#f39c12",
}

TYPE_COLORS = {
    "Pachamikuy": "#9b59b6",
    "Mi Pescadería": "#3498db",
    "Cerditos Felices": "#e74c3c",
    "Festipollo": "#f1c40f",
    "De Emprendedores": "#1abc9c",
}

YEAR_ORDER = ["2025", "2026"]

MONTH_ORDER = [
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Setiembre", "Octubre", "Noviembre", "Diciembre"
]

MONTH_NUM_MAP = {
    "Enero": 1,
    "Febrero": 2,
    "Marzo": 3,
    "Abril": 4,
    "Mayo": 5,
    "Junio": 6,
    "Julio": 7,
    "Agosto": 8,
    "Setiembre": 9,
    "Octubre": 10,
    "Noviembre": 11,
    "Diciembre": 12,
}


def load_pachamikuy_data():
    """Carga la data fija de ferias con distribución mensual."""
    data = [
        # 2025 -> total 73
        {"AÑO": "2025", "MES": "Enero",      "Pachamikuy": 0, "Mi Pescadería": 2, "Cerditos Felices": 1, "Festipollo": 0, "De Emprendedores": 1},
        {"AÑO": "2025", "MES": "Febrero",    "Pachamikuy": 0, "Mi Pescadería": 3, "Cerditos Felices": 1, "Festipollo": 0, "De Emprendedores": 1},
        {"AÑO": "2025", "MES": "Marzo",      "Pachamikuy": 0, "Mi Pescadería": 3, "Cerditos Felices": 2, "Festipollo": 1, "De Emprendedores": 1},
        {"AÑO": "2025", "MES": "Abril",      "Pachamikuy": 0, "Mi Pescadería": 2, "Cerditos Felices": 1, "Festipollo": 0, "De Emprendedores": 2},
        {"AÑO": "2025", "MES": "Mayo",       "Pachamikuy": 0, "Mi Pescadería": 3, "Cerditos Felices": 1, "Festipollo": 1, "De Emprendedores": 1},
        {"AÑO": "2025", "MES": "Junio",      "Pachamikuy": 0, "Mi Pescadería": 2, "Cerditos Felices": 2, "Festipollo": 0, "De Emprendedores": 2},
        {"AÑO": "2025", "MES": "Julio",      "Pachamikuy": 0, "Mi Pescadería": 3, "Cerditos Felices": 1, "Festipollo": 1, "De Emprendedores": 1},
        {"AÑO": "2025", "MES": "Agosto",     "Pachamikuy": 1, "Mi Pescadería": 2, "Cerditos Felices": 1, "Festipollo": 0, "De Emprendedores": 1},
        {"AÑO": "2025", "MES": "Setiembre",  "Pachamikuy": 0, "Mi Pescadería": 3, "Cerditos Felices": 2, "Festipollo": 1, "De Emprendedores": 2},
        {"AÑO": "2025", "MES": "Octubre",    "Pachamikuy": 0, "Mi Pescadería": 3, "Cerditos Felices": 2, "Festipollo": 1, "De Emprendedores": 2},
        {"AÑO": "2025", "MES": "Noviembre",  "Pachamikuy": 0, "Mi Pescadería": 3, "Cerditos Felices": 2, "Festipollo": 1, "De Emprendedores": 1},
        {"AÑO": "2025", "MES": "Diciembre",  "Pachamikuy": 0, "Mi Pescadería": 3, "Cerditos Felices": 2, "Festipollo": 0, "De Emprendedores": 1},

        # 2026 -> total 7, solo Mi Pescadería / Pachamikuy / Cerditos Felices
        {"AÑO": "2026", "MES": "Enero",      "Pachamikuy": 1, "Mi Pescadería": 2, "Cerditos Felices": 1, "Festipollo": 0, "De Emprendedores": 0},
        {"AÑO": "2026", "MES": "Febrero",    "Pachamikuy": 1, "Mi Pescadería": 1, "Cerditos Felices": 1, "Festipollo": 0, "De Emprendedores": 0},
    ]

    df = pd.DataFrame(data)
    df["AÑO"] = df["AÑO"].astype(str)
    df["MES_NUM"] = df["MES"].map(MONTH_NUM_MAP)

    tipos = ["Pachamikuy", "Mi Pescadería", "Cerditos Felices", "Festipollo", "De Emprendedores"]
    df["TOTAL_MES"] = df[tipos].sum(axis=1)

    return df.sort_values(["AÑO", "MES_NUM"]).reset_index(drop=True)


def estadisticas_generales(df):
    st.subheader("📊 Estadísticas Generales")

    c1, c2, c3, c4 = st.columns(4)

    total_ferias = int(df["TOTAL_MES"].sum())
    total_meses = int(len(df))
    anio_max = df.groupby("AÑO")["TOTAL_MES"].sum().idxmax()

    tipos = ["Pachamikuy", "Mi Pescadería", "Cerditos Felices", "Festipollo", "De Emprendedores"]
    total_por_tipo = df[tipos].sum()
    tipo_max = total_por_tipo.idxmax()

    c1.metric("🎪 Total de Ferias", total_ferias)
    c2.metric("🗓️ Meses Registrados", total_meses)
    c3.metric("🏆 Año Más Activo", anio_max)
    c4.metric("📌 Tipo Principal", tipo_max)


def grafico_total_mensual(df):
    st.subheader("📅 Total de Ferias por Mes")

    fig = px.bar(
        df,
        x="MES",
        y="TOTAL_MES",
        color="AÑO",
        text="TOTAL_MES",
        barmode="group",
        color_discrete_map=YEAR_COLORS,
        category_orders={"MES": MONTH_ORDER, "AÑO": YEAR_ORDER},
        height=420,
        labels={"MES": "Mes", "TOTAL_MES": "Total de Ferias", "AÑO": "Año"}
    )

    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis_title="Mes",
        yaxis_title="Total de Ferias",
        hovermode="x unified"
    )
    fig.update_xaxes(type="category")
    fig.update_traces(textposition="outside")

    st.plotly_chart(fig, use_container_width=True)


def grafico_composicion(df):
    st.subheader("🧩 Composición por Tipo de Feria")

    df_long = df.melt(
        id_vars=["AÑO", "MES", "MES_NUM", "TOTAL_MES"],
        value_vars=["Pachamikuy", "Mi Pescadería", "Cerditos Felices", "Festipollo", "De Emprendedores"],
        var_name="TIPO_FERIA",
        value_name="CANTIDAD"
    )

    fig = px.bar(
        df_long,
        x="MES",
        y="CANTIDAD",
        color="TIPO_FERIA",
        facet_col="AÑO",
        barmode="stack",
        color_discrete_map=TYPE_COLORS,
        category_orders={"MES": MONTH_ORDER, "AÑO": YEAR_ORDER},
        height=500,
        labels={
            "MES": "Mes",
            "CANTIDAD": "Cantidad",
            "TIPO_FERIA": "Tipo de Feria"
        }
    )

    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        legend_title="Tipo de Feria"
    )

    fig.for_each_annotation(lambda a: a.update(text=a.text.replace("AÑO=", "Año ")))

    st.plotly_chart(fig, use_container_width=True)


def grafico_total_por_anio(df):
    st.subheader("📈 Total de Ferias por Año")

    anual = (
        df.groupby("AÑO")["TOTAL_MES"]
        .sum()
        .reindex(YEAR_ORDER, fill_value=0)
        .reset_index()
    )

    fig = px.bar(
        anual,
        x="AÑO",
        y="TOTAL_MES",
        color="AÑO",
        text="TOTAL_MES",
        color_discrete_map=YEAR_COLORS,
        category_orders={"AÑO": YEAR_ORDER},
        height=350,
        labels={"AÑO": "Año", "TOTAL_MES": "Total de Ferias"}
    )

    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis_title="Año",
        yaxis_title="Total de Ferias",
        showlegend=False
    )
    fig.update_xaxes(type="category")
    fig.update_traces(textposition="outside")

    st.plotly_chart(fig, use_container_width=True)


def tabla_resumen_mensual(df):
    st.subheader("📋 Tabla Resumen Mensual")

    tabla_df = df[[
        "AÑO", "MES", "Pachamikuy", "Mi Pescadería",
        "Cerditos Felices", "Festipollo", "De Emprendedores", "TOTAL_MES"
    ]].copy()

    tabla_df = tabla_df.rename(columns={
        "AÑO": "Año",
        "MES": "Mes",
        "TOTAL_MES": "Total"
    })

    st.dataframe(
        tabla_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Año": st.column_config.TextColumn("Año", width="small"),
            "Mes": st.column_config.TextColumn("Mes", width="medium"),
            "Pachamikuy": st.column_config.NumberColumn("Pachamikuy", format="%d"),
            "Mi Pescadería": st.column_config.NumberColumn("Mi Pescadería", format="%d"),
            "Cerditos Felices": st.column_config.NumberColumn("Cerditos Felices", format="%d"),
            "Festipollo": st.column_config.NumberColumn("Festipollo", format="%d"),
            "De Emprendedores": st.column_config.NumberColumn("De Emprendedores", format="%d"),
            "Total": st.column_config.NumberColumn("Total", format="%d"),
        }
    )


def tabla_resumen_tipo(df):
    st.subheader("📌 Resumen por Tipo de Feria")

    tipos = ["Pachamikuy", "Mi Pescadería", "Cerditos Felices", "Festipollo", "De Emprendedores"]

    resumen = []
    for tipo in tipos:
        resumen.append({
            "Tipo de Feria": tipo,
            "Cantidad": int(df[tipo].sum())
        })

    resumen_df = pd.DataFrame(resumen)

    st.dataframe(
        resumen_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Tipo de Feria": st.column_config.TextColumn("Tipo de Feria", width="large"),
            "Cantidad": st.column_config.NumberColumn("Cantidad", format="%d"),
        }
    )


def observaciones(df):
    st.subheader("📝 Observaciones")

    total_anual = df.groupby("AÑO")["TOTAL_MES"].sum().reindex(YEAR_ORDER, fill_value=0)

    tipos = ["Pachamikuy", "Mi Pescadería", "Cerditos Felices", "Festipollo", "De Emprendedores"]
    total_por_tipo = df[tipos].sum()
    tipo_max = total_por_tipo.idxmax()

    mes_pico = df.loc[df["TOTAL_MES"].idxmax()]

    st.info(
        f"""
- En **2025** se registran **{int(total_anual['2025'])}** ferias en total.
- En **2026** se registran **{int(total_anual['2026'])}** ferias, correspondientes únicamente a **enero y febrero**.
- El tipo de feria con mayor participación acumulada es **{tipo_max}**, con **{int(total_por_tipo[tipo_max])}** registros.
- El mes con mayor actividad fue **{mes_pico['MES']} de {mes_pico['AÑO']}**, con **{int(mes_pico['TOTAL_MES'])}** ferias.
- Para que el total anual de **2025** cierre en **73**, se incorporó **1 registro de Pachamikuy** en la distribución mensual.
- En **2026**, la distribución se concentra solo en **Pachamikuy**, **Mi Pescadería** y **Cerditos Felices**, según tu indicación.
"""
    )


def show_pachamikuy_module():
    st.header("🎪 Módulo de Ferias - PACHAMIKUY")
    st.markdown("---")

    df = load_pachamikuy_data()

    if df is None or df.empty:
        st.error("No se pudieron cargar los datos.")
        return

    estadisticas_generales(df)
    st.markdown("---")

    grafico_total_mensual(df)
    st.markdown("---")

    grafico_composicion(df)
    st.markdown("---")

    grafico_total_por_anio(df)
    st.markdown("---")

    tabla_resumen_mensual(df)
    st.markdown("---")

    tabla_resumen_tipo(df)
    st.markdown("---")

    observaciones(df)
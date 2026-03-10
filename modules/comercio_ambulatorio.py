# modules/comercio_ambulatorio.py

import pandas as pd
import plotly.express as px
import streamlit as st
from pathlib import Path

# Paleta de colores por año
YEAR_COLORS = {
    "2023": "#e74c3c",
    "2024": "#3498db",
    "2025": "#2ecc71",
    "2026": "#f39c12",
}

YEAR_ORDER = ["2023", "2024", "2025", "2026"]

MONTH_ORDER = [
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
]

MONTH_MAP = {
    1: "Enero",
    2: "Febrero",
    3: "Marzo",
    4: "Abril",
    5: "Mayo",
    6: "Junio",
    7: "Julio",
    8: "Agosto",
    9: "Septiembre",
    10: "Octubre",
    11: "Noviembre",
    12: "Diciembre"
}


def get_spanish_month(month_num):
    return MONTH_MAP.get(month_num, "")


def load_comercio_ambulatorio_data():
    """Carga y procesa los datos de autorizaciones de comercio ambulatorio."""
    try:
        data_path = Path(__file__).parent.parent / "data" / "comercio_ambulatorio.csv"

        df_raw = pd.read_csv(
            data_path,
            sep=";",
            encoding="utf-8-sig",
            dtype=str
        )

        df_raw.columns = df_raw.columns.str.strip()

        # Caso 1: si el archivo ya viene con FECHA_EMITIDA
        if "FECHA_EMITIDA" in df_raw.columns:
            df = df_raw.copy()

            df["FECHA_EMITIDA"] = pd.to_datetime(
                df["FECHA_EMITIDA"],
                dayfirst=True,
                errors="coerce"
            )

            df = df.dropna(subset=["FECHA_EMITIDA"])
            df["AÑO"] = df["FECHA_EMITIDA"].dt.year.astype(str)

        else:
            # Caso 2: columnas por año: 2023, 2024, 2025, 2026...
            year_cols = [col for col in df_raw.columns if col.strip().isdigit()]

            if not year_cols:
                raise ValueError(
                    "No se encontró la columna 'FECHA_EMITIDA' ni columnas de años como 2023, 2024, 2025, 2026."
                )

            df = df_raw[year_cols].melt(
                var_name="AÑO",
                value_name="FECHA_EMITIDA"
            )

            df["FECHA_EMITIDA"] = df["FECHA_EMITIDA"].astype(str).str.strip()

            df = df[
                df["FECHA_EMITIDA"].notna() &
                (df["FECHA_EMITIDA"] != "") &
                (df["FECHA_EMITIDA"].str.lower() != "nan")
            ]

            df["FECHA_EMITIDA"] = pd.to_datetime(
                df["FECHA_EMITIDA"],
                format="%d/%m/%Y",
                errors="coerce"
            )

            df = df.dropna(subset=["FECHA_EMITIDA"])

        df["AÑO"] = df["AÑO"].astype(str)
        df["MES_NUM"] = df["FECHA_EMITIDA"].dt.month
        df["MES"] = df["MES_NUM"].map(get_spanish_month)

        df = df.sort_values("FECHA_EMITIDA").reset_index(drop=True)

        return df

    except Exception as e:
        st.error(f"🚨 Error al cargar datos: {str(e)}")
        return None


def load_comercio_ambulatorio_recaudacion_data():
    """Carga los datos fijos de recaudación de comercio ambulatorio."""
    data = [
        {"AÑO": "2023", "PERMISOS": 398, "MESES": 12, "COSTO": 30.0, "TOTAL_RECAUDADO": 143280.0},
        {"AÑO": "2024", "PERMISOS": 183, "MESES": 12, "COSTO": 30.0, "TOTAL_RECAUDADO": 65880.0},
        {"AÑO": "2025", "PERMISOS": 125, "MESES": 12, "COSTO": 30.0, "TOTAL_RECAUDADO": 45000.0},
        {"AÑO": "2026", "PERMISOS": 37, "MESES": 3, "COSTO": 30.0, "TOTAL_RECAUDADO": 3330.0},
    ]

    df = pd.DataFrame(data)
    df["AÑO"] = pd.Categorical(df["AÑO"], categories=YEAR_ORDER, ordered=True)
    return df


def grafico_comparativa_meses(df):
    """Gráfico de barras comparativo por meses y años."""
    st.subheader("📊 Comparativa por Meses")

    comparativa = (
        df.groupby(["MES", "MES_NUM", "AÑO"])
        .size()
        .reset_index(name="AUTORIZACIONES")
        .sort_values(["MES_NUM", "AÑO"])
    )

    fig = px.bar(
        comparativa,
        x="MES",
        y="AUTORIZACIONES",
        color="AÑO",
        barmode="group",
        color_discrete_map=YEAR_COLORS,
        category_orders={
            "MES": MONTH_ORDER,
            "AÑO": YEAR_ORDER
        },
        height=450,
        labels={
            "AUTORIZACIONES": "Cantidad de Autorizaciones",
            "MES": "Mes",
            "AÑO": "Año",
        }
    )

    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis_title="Mes",
        yaxis_title="Cantidad de Autorizaciones",
        hovermode="x unified",
        legend_title="Año"
    )

    st.plotly_chart(fig, use_container_width=True)


def grafico_crecimiento_mensual(df):
    """Gráfico de líneas de crecimiento mensual por año."""
    st.subheader("📈 Crecimiento Mensual por Año")

    monthly_data = (
        df.groupby(["MES", "MES_NUM", "AÑO"])
        .size()
        .reset_index(name="AUTORIZACIONES")
        .sort_values(["AÑO", "MES_NUM"])
    )

    fig = px.line(
        monthly_data,
        x="MES",
        y="AUTORIZACIONES",
        color="AÑO",
        markers=True,
        line_shape="spline",
        color_discrete_map=YEAR_COLORS,
        category_orders={
            "MES": MONTH_ORDER,
            "AÑO": YEAR_ORDER
        },
        height=450,
        labels={
            "AUTORIZACIONES": "Cantidad de Autorizaciones",
            "MES": "Mes",
            "AÑO": "Año",
        }
    )

    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis_title="Mes",
        yaxis_title="Cantidad de Autorizaciones",
        hovermode="x unified",
        legend_title="Año"
    )

    fig.update_traces(
        marker=dict(size=8),
        line=dict(width=3)
    )

    st.plotly_chart(fig, use_container_width=True)


def grafico_comparativa_por_ano(df):
    """Gráfico de barras con totales por año."""
    st.subheader("📅 Total de Autorizaciones por Año")

    anual = (
        df.groupby("AÑO")
        .size()
        .reindex(YEAR_ORDER, fill_value=0)
        .reset_index(name="TOTAL_AUTORIZACIONES")
    )

    fig = px.bar(
        anual,
        x="AÑO",
        y="TOTAL_AUTORIZACIONES",
        color="AÑO",
        text="TOTAL_AUTORIZACIONES",
        color_discrete_map=YEAR_COLORS,
        category_orders={"AÑO": YEAR_ORDER},
        height=350,
        labels={
            "TOTAL_AUTORIZACIONES": "Total de Autorizaciones",
            "AÑO": "Año",
        }
    )

    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis_title="Año",
        yaxis_title="Total de Autorizaciones",
        showlegend=False
    )

    fig.update_xaxes(type="category")

    fig.update_traces(
        textposition="outside",
        marker_line_color="rgba(0,0,0,0.3)",
        marker_line_width=2
    )

    st.plotly_chart(fig, use_container_width=True)


def tabla_resumen(df):
    """Tabla resumen por mes y año."""
    st.subheader("📋 Tabla Resumen: Autorizaciones por Mes y Año")

    resumen = (
        df.groupby(["MES_NUM", "MES", "AÑO"])
        .size()
        .reset_index(name="TOTAL")
    )

    tabla_df = (
        resumen.pivot_table(
            index=["MES_NUM", "MES"],
            columns="AÑO",
            values="TOTAL",
            aggfunc="sum",
            fill_value=0
        )
        .reset_index()
        .sort_values("MES_NUM")
    )

    for year in YEAR_ORDER:
        if year not in tabla_df.columns:
            tabla_df[year] = 0

    tabla_df["Total"] = tabla_df[YEAR_ORDER].sum(axis=1)
    tabla_df = tabla_df[["MES", "2023", "2024", "2025", "2026", "Total"]]
    tabla_df = tabla_df.rename(columns={"MES": "Mes"})

    st.dataframe(
        tabla_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Mes": st.column_config.TextColumn("Mes", width="medium"),
            "2023": st.column_config.NumberColumn("2023", format="%d"),
            "2024": st.column_config.NumberColumn("2024", format="%d"),
            "2025": st.column_config.NumberColumn("2025", format="%d"),
            "2026": st.column_config.NumberColumn("2026", format="%d"),
            "Total": st.column_config.NumberColumn("Total", format="%d"),
        }
    )


def estadisticas_generales(df):
    """Muestra KPIs generales de autorizaciones."""
    st.subheader("📊 Estadísticas Generales de Autorizaciones")

    c1, c2, c3, c4 = st.columns(4)

    total_autorizaciones = len(df)
    total_anios = df["AÑO"].nunique()

    mes_max = (
        df.groupby("MES")
        .size()
        .sort_values(ascending=False)
        .index[0]
    )

    promedio_mes = (
        df.groupby(["AÑO", "MES_NUM"])
        .size()
        .mean()
    )

    c1.metric("📜 Total Autorizaciones", total_autorizaciones)
    c2.metric("📅 Años", total_anios)
    c3.metric("🏆 Mes Más Activo", mes_max)
    c4.metric("📈 Promedio/Mes", f"{promedio_mes:.1f}")


def estadisticas_recaudacion(recaud_df):
    """Muestra KPIs generales de recaudación."""
    st.subheader("💰 Estadísticas Generales de Recaudación")

    c1, c2, c3, c4 = st.columns(4)

    total_recaudado = float(recaud_df["TOTAL_RECAUDADO"].sum())
    anio_max_recaudacion = recaud_df.loc[recaud_df["TOTAL_RECAUDADO"].idxmax(), "AÑO"]
    promedio_anual = recaud_df["TOTAL_RECAUDADO"].mean()
    costo_mensual = recaud_df["COSTO"].iloc[0]

    c1.metric("💵 Total Recaudado", f"S/ {total_recaudado:,.2f}")
    c2.metric("🏆 Año con Mayor Recaudación", str(anio_max_recaudacion))
    c3.metric("📈 Promedio Anual", f"S/ {promedio_anual:,.2f}")
    c4.metric("🧾 Costo Mensual", f"S/ {costo_mensual:,.2f}")


def grafico_recaudacion_por_ano(recaud_df):
    """Gráfico de barras de recaudación por año."""
    st.subheader("💰 Recaudación por Año")

    fig = px.bar(
        recaud_df,
        x="AÑO",
        y="TOTAL_RECAUDADO",
        color="AÑO",
        text="TOTAL_RECAUDADO",
        color_discrete_map=YEAR_COLORS,
        category_orders={"AÑO": YEAR_ORDER},
        height=350,
        labels={
            "AÑO": "Año",
            "TOTAL_RECAUDADO": "Recaudación Total (S/)"
        }
    )

    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis_title="Año",
        yaxis_title="Recaudación Total (S/)",
        showlegend=False
    )

    fig.update_xaxes(type="category")

    fig.update_traces(
        texttemplate="S/ %{y:,.2f}",
        textposition="outside",
        marker_line_color="rgba(0,0,0,0.3)",
        marker_line_width=2
    )

    st.plotly_chart(fig, use_container_width=True)


def grafico_permisos_vs_recaudacion(recaud_df):
    """Gráfico comparativo entre permisos y recaudación."""
    st.subheader("📈 Permisos vs Recaudación")

    df_chart = recaud_df.copy()
    df_chart["AÑO"] = df_chart["AÑO"].astype(str)

    fig = px.scatter(
        df_chart,
        x="PERMISOS",
        y="TOTAL_RECAUDADO",
        color="AÑO",
        size="PERMISOS",
        text="AÑO",
        color_discrete_map=YEAR_COLORS,
        category_orders={"AÑO": YEAR_ORDER},
        height=420,
        labels={
            "PERMISOS": "Cantidad de Permisos",
            "TOTAL_RECAUDADO": "Recaudación Total (S/)"
        }
    )

    fig.update_traces(
        textposition="top center",
        marker=dict(line=dict(width=1, color="rgba(0,0,0,0.3)"))
    )

    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis_title="Cantidad de Permisos",
        yaxis_title="Recaudación Total (S/)"
    )

    st.plotly_chart(fig, use_container_width=True)


def tabla_recaudacion(recaud_df):
    """Tabla resumen de recaudación."""
    st.subheader("📋 Tabla Resumen de Recaudación")

    tabla_df = recaud_df.copy().rename(columns={
        "AÑO": "Año",
        "PERMISOS": "Permisos",
        "MESES": "Meses",
        "COSTO": "Costo",
        "TOTAL_RECAUDADO": "Total Recaudado"
    })

    st.dataframe(
        tabla_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Año": st.column_config.TextColumn("Año", width="small"),
            "Permisos": st.column_config.NumberColumn("Permisos", format="%d"),
            "Meses": st.column_config.NumberColumn("Meses", format="%d"),
            "Costo": st.column_config.NumberColumn("Costo", format="S/ %.2f"),
            "Total Recaudado": st.column_config.NumberColumn("Total Recaudado", format="S/ %.2f"),
        }
    )


def observaciones(df):
    """Muestra observaciones automáticas del comportamiento anual y mensual."""
    st.subheader("📝 Observaciones de Autorizaciones")

    total_anual = (
        df.groupby("AÑO")
        .size()
        .reindex(YEAR_ORDER, fill_value=0)
    )

    mes_general = (
        df.groupby(["MES_NUM", "MES"])
        .size()
        .reset_index(name="TOTAL")
        .sort_values(["TOTAL", "MES_NUM"], ascending=[False, True])
        .iloc[0]
    )

    pico_por_anio = (
        df.groupby(["AÑO", "MES_NUM", "MES"])
        .size()
        .reset_index(name="TOTAL")
        .sort_values(["AÑO", "TOTAL", "MES_NUM"], ascending=[True, False, True])
        .drop_duplicates(subset=["AÑO"])
        .sort_values("AÑO")
    )

    def obtener_pico(anio):
        fila = pico_por_anio[pico_por_anio["AÑO"] == anio]
        return fila.iloc[0] if not fila.empty else None

    pico_2023 = obtener_pico("2023")
    pico_2024 = obtener_pico("2024")
    pico_2025 = obtener_pico("2025")
    pico_2026 = obtener_pico("2026")

    def variacion_pct(base, actual):
        if base == 0:
            return None
        return ((actual - base) / base) * 100

    var_23_24 = variacion_pct(total_anual.get("2023", 0), total_anual.get("2024", 0))
    var_24_25 = variacion_pct(total_anual.get("2024", 0), total_anual.get("2025", 0))
    var_25_26 = variacion_pct(total_anual.get("2025", 0), total_anual.get("2026", 0))

    nota_2026 = ""
    df_2026 = df[df["AÑO"] == "2026"]
    if not df_2026.empty:
        ultimo_mes_2026 = int(df_2026["MES_NUM"].max())
        ultimo_mes_nombre = MONTH_MAP.get(ultimo_mes_2026, "")
        if ultimo_mes_2026 < 12:
            nota_2026 = (
                f"- El año **2026** presenta información parcial hasta **{ultimo_mes_nombre}**, "
                "por lo que su comparación con años completos debe interpretarse con cautela.\n"
            )

    texto = (
        f"- En el periodo analizado, el año con mayor número de autorizaciones emitidas fue "
        f"**{total_anual.idxmax()}**, con **{int(total_anual.max())}** registros.\n"
        f"- El mes con mayor concentración de autorizaciones en todo el periodo fue "
        f"**{mes_general['MES']}**, con **{int(mes_general['TOTAL'])}** registros acumulados.\n"
    )

    if pico_2023 is not None:
        texto += (
            f"- En **2023**, el mes con mayor número de autorizaciones fue "
            f"**{pico_2023['MES']}**, con **{int(pico_2023['TOTAL'])}** registros.\n"
        )

    if pico_2024 is not None:
        texto += (
            f"- En **2024**, el mes con mayor número de autorizaciones fue "
            f"**{pico_2024['MES']}**, con **{int(pico_2024['TOTAL'])}** registros.\n"
        )

    if pico_2025 is not None:
        texto += (
            f"- En **2025**, el mes con mayor número de autorizaciones fue "
            f"**{pico_2025['MES']}**, con **{int(pico_2025['TOTAL'])}** registros.\n"
        )

    if pico_2026 is not None:
        texto += (
            f"- En **2026**, el mes con mayor número de autorizaciones fue "
            f"**{pico_2026['MES']}**, con **{int(pico_2026['TOTAL'])}** registros.\n"
        )

    if var_23_24 is not None:
        tendencia = "disminución" if var_23_24 < 0 else "incremento"
        texto += (
            f"- Entre **2023 y 2024** se observa una **{tendencia}** de "
            f"**{abs(var_23_24):.1f}%** en el total de autorizaciones emitidas.\n"
        )

    if var_24_25 is not None:
        tendencia = "disminución" if var_24_25 < 0 else "incremento"
        texto += (
            f"- Entre **2024 y 2025** se observa una **{tendencia}** de "
            f"**{abs(var_24_25):.1f}%** en el total de autorizaciones emitidas.\n"
        )

    if var_25_26 is not None:
        tendencia = "disminución" if var_25_26 < 0 else "incremento"
        texto += (
            f"- Entre **2025 y 2026** se observa una **{tendencia}** de "
            f"**{abs(var_25_26):.1f}%** en el total registrado.\n"
        )

    texto += nota_2026

    st.info(texto)


def observaciones_recaudacion(recaud_df):
    """Muestra observaciones automáticas de la recaudación."""
    st.subheader("📝 Observaciones de Recaudación")

    mayor_recaudacion = recaud_df.loc[recaud_df["TOTAL_RECAUDADO"].idxmax()]
    menor_recaudacion = recaud_df.loc[recaud_df["TOTAL_RECAUDADO"].idxmin()]

    def variacion_pct(base, actual):
        if base == 0:
            return None
        return ((actual - base) / base) * 100

    rec_2023 = recaud_df.loc[recaud_df["AÑO"] == "2023", "TOTAL_RECAUDADO"].iloc[0]
    rec_2024 = recaud_df.loc[recaud_df["AÑO"] == "2024", "TOTAL_RECAUDADO"].iloc[0]
    rec_2025 = recaud_df.loc[recaud_df["AÑO"] == "2025", "TOTAL_RECAUDADO"].iloc[0]
    rec_2026 = recaud_df.loc[recaud_df["AÑO"] == "2026", "TOTAL_RECAUDADO"].iloc[0]

    var_23_24 = variacion_pct(rec_2023, rec_2024)
    var_24_25 = variacion_pct(rec_2024, rec_2025)
    var_25_26 = variacion_pct(rec_2025, rec_2026)

    total_recaudado = recaud_df["TOTAL_RECAUDADO"].sum()

    texto = (
        f"- La recaudación total del periodo asciende a **S/ {total_recaudado:,.2f}**.\n"
        f"- El año con mayor recaudación fue **{mayor_recaudacion['AÑO']}**, con **S/ {mayor_recaudacion['TOTAL_RECAUDADO']:,.2f}**.\n"
        f"- El año con menor recaudación fue **{menor_recaudacion['AÑO']}**, con **S/ {menor_recaudacion['TOTAL_RECAUDADO']:,.2f}**.\n"
    )

    if var_23_24 is not None:
        tendencia = "disminución" if var_23_24 < 0 else "incremento"
        texto += (
            f"- Entre **2023 y 2024** se registra una **{tendencia}** de "
            f"**{abs(var_23_24):.1f}%** en la recaudación.\n"
        )

    if var_24_25 is not None:
        tendencia = "disminución" if var_24_25 < 0 else "incremento"
        texto += (
            f"- Entre **2024 y 2025** se registra una **{tendencia}** de "
            f"**{abs(var_24_25):.1f}%** en la recaudación.\n"
        )

    if var_25_26 is not None:
        tendencia = "disminución" if var_25_26 < 0 else "incremento"
        texto += (
            f"- Entre **2025 y 2026** se registra una **{tendencia}** de "
            f"**{abs(var_25_26):.1f}%** en la recaudación acumulada.\n"
        )

    texto += (
        "- El valor consignado para **2026** corresponde únicamente a **3 meses**, por lo que no resulta directamente comparable con años completos.\n"
        "- La recaudación presentada se basa en el cuadro consolidado proporcionado para permisos, meses, costo y total anual."
    )

    st.info(texto)


def show_comercio_ambulatorio_module():
    """Módulo completo de Comercio Ambulatorio."""
    st.header("📍 Módulo de Autorizaciones de Comercio Ambulatorio")
    st.markdown("---")

    with st.spinner("🔍 Cargando datos..."):
        df = load_comercio_ambulatorio_data()

    recaud_df = load_comercio_ambulatorio_recaudacion_data()

    if df is None or df.empty:
        st.error("No se pudieron cargar los datos.")
        return

    estadisticas_generales(df)
    st.markdown("---")

    grafico_comparativa_meses(df)
    st.markdown("---")

    grafico_crecimiento_mensual(df)
    st.markdown("---")

    grafico_comparativa_por_ano(df)
    st.markdown("---")

    tabla_resumen(df)
    st.markdown("---")

    observaciones(df)
    st.markdown("---")

    estadisticas_recaudacion(recaud_df)
    st.markdown("---")

    grafico_recaudacion_por_ano(recaud_df)
    st.markdown("---")

    grafico_permisos_vs_recaudacion(recaud_df)
    st.markdown("---")

    tabla_recaudacion(recaud_df)
    st.markdown("---")

    observaciones_recaudacion(recaud_df)

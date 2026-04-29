import pandas as pd
import plotly.express as px
import streamlit as st
from utils.google_sheets import get_resoluciones_sheet_or_none, normalize_text, parse_money_series

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
    12: "Diciembre",
}


def refresh_year_order(resumen_df):
    global YEAR_ORDER
    years = sorted(resumen_df["PERIODO"].dropna().astype(str).unique())
    if years:
        YEAR_ORDER = years
        for idx, year in enumerate(YEAR_ORDER):
            YEAR_COLORS.setdefault(year, px.colors.qualitative.Set2[idx % len(px.colors.qualitative.Set2)])


def classify_itse(value):
    text = normalize_text(value)
    if "MUY ALTO" in text:
        return "MUY ALTO", "ALTOS Y MUY ALTOS"
    if "ALTO" in text:
        return "ALTO", "ALTOS Y MUY ALTOS"
    if "MEDIO" in text:
        return "MEDIO", "MEDIO"
    return "SIN ITSE", "IMPROCEDENTES"


def load_licencias_drive_data():
    df_raw = get_resoluciones_sheet_or_none()
    if df_raw is None:
        return None

    required = {"TIPO DE PROCEDIMIENTO", "FECHA RESOLUCION", "TIPO DE ITSE", "COSTO"}
    if not required.issubset(df_raw.columns):
        st.warning("El Sheet no tiene las columnas requeridas para Licencias de Funcionamiento.")
        return None

    df = df_raw.copy()
    df["PROCEDIMIENTO_NORMALIZADO"] = df["TIPO DE PROCEDIMIENTO"].map(normalize_text)
    df = df[
        df["PROCEDIMIENTO_NORMALIZADO"].isin(
            ["LICENCIA TEMPORAL", "LICENCIA INDETERMINADA"]
        )
    ].copy()
    if df.empty:
        return None

    df["FECHA_RESOLUCION"] = pd.to_datetime(
        df["FECHA RESOLUCION"],
        dayfirst=True,
        errors="coerce",
    )
    df = df.dropna(subset=["FECHA_RESOLUCION"])
    if df.empty:
        return None

    df["COSTO_NUM"] = parse_money_series(df["COSTO"])
    risk_data = df["TIPO DE ITSE"].apply(classify_itse)
    df["RIESGO_DETALLE"] = risk_data.apply(lambda item: item[0])
    df["RIESGO_AGRUPADO"] = risk_data.apply(lambda item: item[1])
    df["PERIODO"] = df["FECHA_RESOLUCION"].dt.year.astype(str)
    df["MES_NUM"] = df["FECHA_RESOLUCION"].dt.month
    df["MES"] = df["MES_NUM"].map(MONTH_MAP)

    detalle_df = (
        df.groupby(["PERIODO", "MES_NUM", "MES", "RIESGO_DETALLE", "RIESGO_AGRUPADO"])
        .agg(
            EXPEDIENTES=("FECHA_RESOLUCION", "size"),
            COSTO=("COSTO_NUM", "mean"),
            TOTAL=("COSTO_NUM", "sum"),
        )
        .reset_index()
        .sort_values(["PERIODO", "MES_NUM", "RIESGO_DETALLE"])
    )

    resumen_df = (
        df.groupby("PERIODO")
        .agg(
            EXPEDIENTES=("FECHA_RESOLUCION", "size"),
            RECAUDACION=("COSTO_NUM", "sum"),
        )
        .reset_index()
        .sort_values("PERIODO")
    )

    detalle_df.attrs["source"] = "drive"
    resumen_df.attrs["source"] = "drive"
    refresh_year_order(resumen_df)
    return detalle_df, resumen_df


def load_licencias_funcionamiento_data():
    """Carga los datos fijos de Licencias de Funcionamiento."""
    drive_data = load_licencias_drive_data()

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

    # Resumen anual segun el total consolidado mostrado en tu cuadro
    resumen_data = [
        {"PERIODO": "2023", "EXPEDIENTES": 850, "RECAUDACION": 314165.00},
        {"PERIODO": "2024", "EXPEDIENTES": 900, "RECAUDACION": 276410.00},
        {"PERIODO": "2025", "EXPEDIENTES": 1010, "RECAUDACION": 370209.00},
        {"PERIODO": "2026 (Ene-Abr)", "EXPEDIENTES": 288, "RECAUDACION": 82276.00},
    ]

    detalle_df = pd.DataFrame(detalle_data)
    resumen_df = pd.DataFrame(resumen_data)

    if drive_data is not None:
        drive_detalle_df, drive_resumen_df = drive_data
        active_year = drive_resumen_df["PERIODO"].astype(str).str.extract(r"(\d{4})")[0].astype(int).max()

        detalle_years = detalle_df["PERIODO"].astype(str).str.extract(r"(\d{4})")[0].astype(int)
        resumen_years = resumen_df["PERIODO"].astype(str).str.extract(r"(\d{4})")[0].astype(int)

        detalle_df = pd.concat(
            [detalle_df[detalle_years < active_year], drive_detalle_df],
            ignore_index=True,
        )
        resumen_df = pd.concat(
            [resumen_df[resumen_years < active_year], drive_resumen_df],
            ignore_index=True,
        )
        detalle_df.attrs["source"] = "mixed"
        resumen_df.attrs["source"] = "mixed"
        refresh_year_order(resumen_df)
        return detalle_df, resumen_df

    detalle_df["PERIODO"] = pd.Categorical(detalle_df["PERIODO"], categories=YEAR_ORDER, ordered=True)
    resumen_df["PERIODO"] = pd.Categorical(resumen_df["PERIODO"], categories=YEAR_ORDER, ordered=True)
    detalle_df.attrs["source"] = "local"
    resumen_df.attrs["source"] = "local"

    return detalle_df, resumen_df


def estadisticas_generales(resumen_df):
    st.subheader("Estadisticas Generales")

    c1, c2, c3, c4 = st.columns(4)

    total_expedientes = int(resumen_df["EXPEDIENTES"].sum())
    total_recaudado = float(resumen_df["RECAUDACION"].sum())
    periodo_max = resumen_df.loc[resumen_df["RECAUDACION"].idxmax(), "PERIODO"]
    promedio_expedientes = resumen_df["EXPEDIENTES"].mean()

    c1.metric("Total Expedientes", f"{total_expedientes:,}")
    c2.metric("Recaudacion Total", f"S/ {total_recaudado:,.2f}")
    c3.metric("Mayor Recaudacion", str(periodo_max))
    c4.metric("Promedio Expedientes", f"{promedio_expedientes:.1f}")


def grafico_expedientes(resumen_df):
    st.subheader("Expedientes por Anio")

    fig = px.bar(
        resumen_df,
        x="PERIODO",
        y="EXPEDIENTES",
        color="PERIODO",
        text="EXPEDIENTES",
        color_discrete_map=YEAR_COLORS,
        category_orders={"PERIODO": YEAR_ORDER},
        height=420,
        labels={"PERIODO": "Anio", "EXPEDIENTES": "Nro. de Expedientes"}
    )

    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis_title="Anio",
        yaxis_title="Nro. de Expedientes",
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
    st.subheader("Recaudacion por Anio")

    fig = px.bar(
        resumen_df,
        x="PERIODO",
        y="RECAUDACION",
        color="PERIODO",
        text="RECAUDACION",
        color_discrete_map=YEAR_COLORS,
        category_orders={"PERIODO": YEAR_ORDER},
        height=420,
        labels={"PERIODO": "Anio", "RECAUDACION": "Recaudacion (S/)"}
    )

    fig.update_traces(
        texttemplate="S/ %{y:,.2f}",
        textposition="outside",
        marker_line_color="rgba(0,0,0,0.3)",
        marker_line_width=2
    )

    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis_title="Anio",
        yaxis_title="Recaudacion (S/)",
        showlegend=False
    )

    fig.update_xaxes(type="category")

    st.plotly_chart(fig, use_container_width=True)


def grafico_riesgo_apilado(detalle_df):
    st.subheader("Expedientes por Riesgo")

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
            "PERIODO": "Anio",
            "EXPEDIENTES": "Nro. de Expedientes",
            "RIESGO_AGRUPADO": "Riesgo"
        }
    )

    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis_title="Anio",
        yaxis_title="Nro. de Expedientes",
        legend_title="Riesgo"
    )

    fig.update_xaxes(type="category")

    st.plotly_chart(fig, use_container_width=True)


def grafico_recaudacion_riesgo(detalle_df):
    st.subheader("Recaudacion por Riesgo")

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
            "PERIODO": "Anio",
            "TOTAL": "Recaudacion (S/)",
            "RIESGO_AGRUPADO": "Riesgo"
        }
    )

    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis_title="Anio",
        yaxis_title="Recaudacion (S/)",
        legend_title="Riesgo"
    )

    fig.update_xaxes(type="category")

    st.plotly_chart(fig, use_container_width=True)


def grafico_mensual_licencias(detalle_df):
    if not {"MES", "MES_NUM"}.issubset(detalle_df.columns):
        return

    st.subheader("Recaudacion mensual por Licencias")

    mensual = (
        detalle_df.groupby(["PERIODO", "MES", "MES_NUM"], observed=False)
        .agg(EXPEDIENTES=("EXPEDIENTES", "sum"), RECAUDACION=("TOTAL", "sum"))
        .reset_index()
        .sort_values(["PERIODO", "MES_NUM"])
    )

    fig = px.bar(
        mensual,
        x="MES",
        y="RECAUDACION",
        color="PERIODO",
        barmode="group",
        text="RECAUDACION",
        category_orders={"MES": MONTH_ORDER, "PERIODO": YEAR_ORDER},
        color_discrete_map=YEAR_COLORS,
        height=450,
        labels={
            "MES": "Mes",
            "RECAUDACION": "Recaudacion (S/)",
            "PERIODO": "Anio",
        },
    )
    fig.update_traces(texttemplate="S/ %{y:,.2f}", textposition="outside")
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis_title="Mes",
        yaxis_title="Recaudacion (S/)",
        legend_title="Anio",
    )
    st.plotly_chart(fig, use_container_width=True)

    tabla = mensual.pivot_table(
        index=["MES_NUM", "MES"],
        columns="PERIODO",
        values="RECAUDACION",
        aggfunc="sum",
        fill_value=0,
    ).reset_index()

    for year in YEAR_ORDER:
        if year not in tabla.columns:
            tabla[year] = 0

    tabla["Total"] = tabla[YEAR_ORDER].sum(axis=1)
    tabla = tabla[["MES", *YEAR_ORDER, "Total"]].rename(columns={"MES": "Mes"})

    st.dataframe(
        tabla,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Mes": st.column_config.TextColumn("Mes"),
            **{
                year: st.column_config.NumberColumn(year, format="S/ %.2f")
                for year in YEAR_ORDER
            },
            "Total": st.column_config.NumberColumn("Total", format="S/ %.2f"),
        },
    )


def tabla_resumen_anual(resumen_df):
    st.subheader("Tabla Resumen Anual")

    tabla_df = resumen_df.copy().rename(columns={
        "PERIODO": "Anio",
        "EXPEDIENTES": "Nro. Expedientes",
        "RECAUDACION": "Recaudacion"
    })

    st.dataframe(
        tabla_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Anio": st.column_config.TextColumn("Anio", width="medium"),
            "Nro. Expedientes": st.column_config.NumberColumn("Nro. Expedientes", format="%d"),
            "Recaudacion": st.column_config.NumberColumn("Recaudacion", format="S/ %.2f"),
        }
    )


def tabla_detallada(detalle_df):
    st.subheader("Detalle por Riesgo")

    tabla_df = detalle_df.copy().rename(columns={
        "PERIODO": "Anio",
        "RIESGO_DETALLE": "Riesgo",
        "EXPEDIENTES": "Expedientes",
        "COSTO": "Costo",
        "TOTAL": "Total"
    })

    tabla_df = tabla_df[["Anio", "Riesgo", "Expedientes", "Costo", "Total"]]

    st.dataframe(
        tabla_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Anio": st.column_config.TextColumn("Anio", width="small"),
            "Riesgo": st.column_config.TextColumn("Riesgo", width="large"),
            "Expedientes": st.column_config.NumberColumn("Expedientes", format="%d"),
            "Costo": st.column_config.NumberColumn("Costo", format="S/ %.2f"),
            "Total": st.column_config.NumberColumn("Total", format="S/ %.2f"),
        }
    )


def observaciones(resumen_df):
    st.subheader("Observaciones")

    periodo_max_exp = resumen_df.loc[resumen_df["EXPEDIENTES"].idxmax(), "PERIODO"]
    periodo_max_rec = resumen_df.loc[resumen_df["RECAUDACION"].idxmax(), "PERIODO"]
    fuente = resumen_df.attrs.get("source")
    if fuente == "drive":
        texto_fuente = "- Los datos se actualizan automaticamente desde Google Drive.\n"
    elif fuente == "mixed":
        texto_fuente = "- Se conserva el historico local y el ano actual se actualiza desde Google Drive.\n"
    else:
        texto_fuente = "- Los totales anuales se han consignado segun el cuadro consolidado fuente.\n"

    st.info(
        f"""
- El periodo con mayor numero de expedientes fue **{periodo_max_exp}**.
- El periodo con mayor recaudacion fue **{periodo_max_rec}**.
{texto_fuente}
"""
    )

def show_licencias_funcionamiento_module():
    st.header("Modulo de Licencias de Funcionamiento")
    st.markdown("---")

    detalle_df, resumen_df = load_licencias_funcionamiento_data()

    if resumen_df is None or resumen_df.empty:
        st.error("No se pudieron cargar los datos.")
        return

    if resumen_df.attrs.get("source") == "drive":
        st.success("Datos actualizados desde Google Drive: licencias por fecha de resolucion, tipo de ITSE y costo.")
    elif resumen_df.attrs.get("source") == "mixed":
        st.success("Historico local conservado y ano actual actualizado desde Google Drive.")

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

    grafico_mensual_licencias(detalle_df)
    st.markdown("---")

    tabla_resumen_anual(resumen_df)
    st.markdown("---")

    tabla_detallada(detalle_df)
    st.markdown("---")

    observaciones(resumen_df)

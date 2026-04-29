# modules/anuncios_publicitarios.py

import pandas as pd
import plotly.express as px
import streamlit as st

# Colores por periodo
YEAR_COLORS = {
    "2023": "#e74c3c",
    "2024": "#3498db",
    "2025": "#2ecc71",
    "2026 (E-A)": "#f39c12",
}

YEAR_ORDER = ["2023", "2024", "2025", "2026 (E-A)"]

MESES_2026 = ["enero", "febrero", "marzo", "abril"]

ANUNCIOS_2026_DETALLE = [
    {
        "tipo_panel": "PANEL SIMPLE SENCILLO",
        "costo_unitario": 100.6,
        "enero": {"cantidad": 15, "monto": 1509.00},
        "febrero": {"cantidad": 13, "monto": 1307.80},
        "marzo": {"cantidad": 3, "monto": 301.80},
        "abril": {"cantidad": 10, "monto": 1006.00},
    },
    {
        "tipo_panel": "PANEL SIMPLE LUMINOSO",
        "costo_unitario": 120.7,
        "enero": {"cantidad": 7, "monto": 844.90},
        "febrero": {"cantidad": 11, "monto": 1327.70},
        "marzo": {"cantidad": 7, "monto": 844.90},
        "abril": {"cantidad": 8, "monto": 965.60},
    },
    {
        "tipo_panel": "PANEL SIMPLE ILUMINADO",
        "costo_unitario": 120.7,
        "enero": {"cantidad": 0, "monto": 0.00},
        "febrero": {"cantidad": 0, "monto": 0.00},
        "marzo": {"cantidad": 2, "monto": 241.40},
        "abril": {"cantidad": 1, "monto": 120.70},
    },
    {
        "tipo_panel": "TOTEM ESPECIAL",
        "costo_unitario": 120.7,
        "enero": {"cantidad": 0, "monto": 0.00},
        "febrero": {"cantidad": 0, "monto": 0.00},
        "marzo": {"cantidad": 1, "monto": 120.70},
        "abril": {"cantidad": 0, "monto": 0.00},
    },
    {
        "tipo_panel": "TOTEM LUMINOSO",
        "costo_unitario": 120.7,
        "enero": {"cantidad": 0, "monto": 0.00},
        "febrero": {"cantidad": 0, "monto": 0.00},
        "marzo": {"cantidad": 0, "monto": 0.00},
        "abril": {"cantidad": 0, "monto": 0.00},
    },
]

TOTALES_MENSUALES_2026 = {
    "enero": {"cantidad": 22, "monto": 2353.90},
    "febrero": {"cantidad": 24, "monto": 2635.50},
    "marzo": {"cantidad": 13, "monto": 1508.80},
    "abril": {"cantidad": 19, "monto": 2092.30},
}

TOTAL_GENERAL_2026 = {
    "cantidad_total": 78,
    "recaudacion_total": 8590.50,
}


def load_anuncios_publicitarios_data():
    """Carga datos fijos de anuncios publicitarios."""
    data = [
        {"AÑO": "2023", "N_CERT_EMITIDOS": 360, "RECAUDACION": 25292.20},
        {"AÑO": "2024", "N_CERT_EMITIDOS": 348, "RECAUDACION": 30868.90},
        {"AÑO": "2025", "N_CERT_EMITIDOS": 456, "RECAUDACION": 36344.30},
        {
            "AÑO": "2026 (E-A)",
            "N_CERT_EMITIDOS": TOTAL_GENERAL_2026["cantidad_total"],
            "RECAUDACION": TOTAL_GENERAL_2026["recaudacion_total"],
        },
    ]

    df = pd.DataFrame(data)

    # Forzar a texto para que Plotly no lo trate como numérico
    df["AÑO"] = df["AÑO"].astype(str)

    return df


def load_anuncios_2026_mensual_data():
    """Carga el resumen mensual 2026 de enero a abril."""
    data = [
        {
            "MES": mes.capitalize(),
            "N_CERT_EMITIDOS": TOTALES_MENSUALES_2026[mes]["cantidad"],
            "RECAUDACION": TOTALES_MENSUALES_2026[mes]["monto"],
        }
        for mes in MESES_2026
    ]
    return pd.DataFrame(data)


def load_anuncios_2026_detalle_data():
    """Carga el detalle 2026 por tipo de panel y mes."""
    rows = []
    for item in ANUNCIOS_2026_DETALLE:
        row = {
            "Tipo de panel": item["tipo_panel"],
            "Costo unitario": item["costo_unitario"],
        }
        total_cantidad = 0
        total_monto = 0.0

        for mes in MESES_2026:
            cantidad = item[mes]["cantidad"]
            monto = item[mes]["monto"]
            row[f"{mes.capitalize()} Cant."] = cantidad
            row[f"{mes.capitalize()} Monto"] = monto
            total_cantidad += cantidad
            total_monto += monto

        row["Total Cant."] = total_cantidad
        row["Total Monto"] = total_monto
        rows.append(row)

    return pd.DataFrame(rows)


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


def grafico_mensual_2026(df_mensual):
    """Gráficos mensuales 2026 de certificados y recaudación."""
    st.subheader("📆 Evolución Mensual 2026")

    c1, c2 = st.columns(2)

    fig_cert = px.bar(
        df_mensual,
        x="MES",
        y="N_CERT_EMITIDOS",
        text="N_CERT_EMITIDOS",
        color="MES",
        height=360,
        labels={"MES": "Mes", "N_CERT_EMITIDOS": "N° de Certificados Emitidos"},
    )
    fig_cert.update_layout(plot_bgcolor="rgba(0,0,0,0)", showlegend=False)
    fig_cert.update_traces(textposition="outside")
    c1.plotly_chart(fig_cert, use_container_width=True)

    fig_rec = px.bar(
        df_mensual,
        x="MES",
        y="RECAUDACION",
        text="RECAUDACION",
        color="MES",
        height=360,
        labels={"MES": "Mes", "RECAUDACION": "Recaudación (S/)"},
    )
    fig_rec.update_layout(plot_bgcolor="rgba(0,0,0,0)", showlegend=False)
    fig_rec.update_traces(texttemplate="S/ %{y:,.2f}", textposition="outside")
    c2.plotly_chart(fig_rec, use_container_width=True)


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


def tabla_detalle_2026(df_detalle, df_mensual):
    """Tablas del detalle 2026 por mes y tipo de panel."""
    st.subheader("📋 Detalle 2026 por Tipo de Panel")

    st.dataframe(
        df_detalle,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Costo unitario": st.column_config.NumberColumn("Costo unitario", format="S/ %.2f"),
            "Enero Monto": st.column_config.NumberColumn("Enero Monto", format="S/ %.2f"),
            "Febrero Monto": st.column_config.NumberColumn("Febrero Monto", format="S/ %.2f"),
            "Marzo Monto": st.column_config.NumberColumn("Marzo Monto", format="S/ %.2f"),
            "Abril Monto": st.column_config.NumberColumn("Abril Monto", format="S/ %.2f"),
            "Total Monto": st.column_config.NumberColumn("Total Monto", format="S/ %.2f"),
        },
    )

    st.subheader("📋 Totales Mensuales 2026")
    tabla_mensual = df_mensual.rename(columns={
        "MES": "Mes",
        "N_CERT_EMITIDOS": "N° Cert. Emitidos",
        "RECAUDACION": "Recaudación",
    })
    st.dataframe(
        tabla_mensual,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Mes": st.column_config.TextColumn("Mes"),
            "N° Cert. Emitidos": st.column_config.NumberColumn("N° Cert. Emitidos", format="%d"),
            "Recaudación": st.column_config.NumberColumn("Recaudación", format="S/ %.2f"),
        },
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
- El registro **2026 (E-A)** corresponde a **enero, febrero, marzo y abril**.
- En 2026 se registran **{TOTAL_GENERAL_2026['cantidad_total']} certificados** y **S/ {TOTAL_GENERAL_2026['recaudacion_total']:,.2f}** de recaudación acumulada.
"""
    )


def show_anuncios_publicitarios_module():
    """Módulo completo de Anuncios Publicitarios."""
    st.header("📢 Módulo de Anuncios Publicitarios")
    st.markdown("---")

    df = load_anuncios_publicitarios_data()
    df_mensual_2026 = load_anuncios_2026_mensual_data()
    df_detalle_2026 = load_anuncios_2026_detalle_data()

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

    grafico_mensual_2026(df_mensual_2026)
    st.markdown("---")

    tabla_resumen(df)
    st.markdown("---")

    tabla_detalle_2026(df_detalle_2026, df_mensual_2026)
    st.markdown("---")

    observaciones(df)

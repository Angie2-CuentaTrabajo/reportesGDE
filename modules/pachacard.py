# modules/pachacard.py

import pandas as pd
import plotly.express as px
import streamlit as st

CARD_COLORS = {
    "Estándar": "#3498db",
    "Premium": "#f39c12",
}

def load_pachacard_data():
    """Carga la data fija del programa PACHACARD."""
    emitidas_total = 2500

    categorias_data = [
        {"CATEGORIA": "Estándar", "TARJETAS": 430},
        {"CATEGORIA": "Premium", "TARJETAS": 1350},
    ]

    empresas_afiliadas = [
        "Lo de Juan",
        "D'Carlos",
        "Privilegio",
        "Las Ruedas de Pachacámac",
        "Tikay Cafetería",
        "La Esquina",
        "La Ley",
        "Otros establecimientos afiliados",
    ]

    df_categorias = pd.DataFrame(categorias_data)
    df_categorias["PORCENTAJE"] = (
        df_categorias["TARJETAS"] / df_categorias["TARJETAS"].sum() * 100
    ).round(1)

    resumen_data = [
        {"ESTADO": "Emitidas", "CANTIDAD": emitidas_total},
    ]
    df_resumen = pd.DataFrame(resumen_data)

    df_empresas = pd.DataFrame({"EMPRESA": empresas_afiliadas})

    return df_categorias, df_resumen, df_empresas


def estadisticas_generales(df_categorias, df_resumen, df_empresas):
    """KPIs generales."""
    st.subheader("📊 Estadísticas Generales")

    c1, c2, c3 = st.columns(3)

    emitidas = int(df_resumen.loc[df_resumen["ESTADO"] == "Emitidas", "CANTIDAD"].iloc[0])

    categoria_top = df_categorias.loc[df_categorias["TARJETAS"].idxmax(), "CATEGORIA"]
    n_empresas = len(df_empresas)
    total_categorizadas = int(df_categorias["TARJETAS"].sum())

    c1.metric("💳 Tarjetas Emitidas", f"{emitidas:,}")
    c2.metric("🏷️ Tarjetas categorizadas", f"{total_categorizadas:,}")
    c3.metric("🏪 Empresas Afiliadas", f"{n_empresas}+" if n_empresas >= 8 else n_empresas)

    st.caption(
        f"Categoría predominante: {categoria_top}. No se muestra tarjetas entregadas porque el dato no está confirmado."
    )

def grafico_distribucion_categorias(df_categorias):
    """Gráfico tipo dona de tarjetas por categoría registrada."""
    st.subheader("🥇 Distribución de tarjetas por categoría")

    fig = px.pie(
        df_categorias,
        names="CATEGORIA",
        values="TARJETAS",
        color="CATEGORIA",
        color_discrete_map=CARD_COLORS,
        hole=0.55
    )

    fig.update_traces(
        textinfo="percent+label",
        hovertemplate="<b>%{label}</b><br>Tarjetas: %{value}<br>Porcentaje: %{percent}<extra></extra>"
    )

    fig.update_layout(
        height=420,
        legend_title="Categoría"
    )

    st.plotly_chart(fig, use_container_width=True)


def grafico_comparativo_categorias(df_categorias):
    """Gráfico de barras de tarjetas por categoría registrada."""
    st.subheader("📈 Tarjetas por categoría")

    fig = px.bar(
        df_categorias,
        x="CATEGORIA",
        y="TARJETAS",
        color="CATEGORIA",
        text="TARJETAS",
        color_discrete_map=CARD_COLORS,
        height=380,
        labels={
            "CATEGORIA": "Categoría",
            "TARJETAS": "Cantidad de Tarjetas"
        }
    )

    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis_title="Categoría",
        yaxis_title="Cantidad de Tarjetas",
        showlegend=False
    )

    fig.update_xaxes(type="category")

    fig.update_traces(
        textposition="outside",
        marker_line_color="rgba(0,0,0,0.25)",
        marker_line_width=1.5
    )

    st.plotly_chart(fig, use_container_width=True)


def tabla_resumen(df_categorias, df_resumen):
    """Tabla resumen del programa."""
    st.subheader("📋 Tabla Resumen")

    emitidas = int(df_resumen.loc[df_resumen["ESTADO"] == "Emitidas", "CANTIDAD"].iloc[0])
    categorizadas = int(df_categorias["TARJETAS"].sum())

    tabla_general = pd.DataFrame([
        {"Indicador": "Tarjetas emitidas", "Valor": emitidas},
        {"Indicador": "Tarjetas categorizadas", "Valor": categorizadas},
    ])

    st.markdown("**Resumen general**")
    st.dataframe(
        tabla_general,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Indicador": st.column_config.TextColumn("Indicador", width="large"),
            "Valor": st.column_config.NumberColumn("Valor", format="%.1f"),
        }
    )

    st.markdown("**Distribución por categoría**")
    tabla_cat = df_categorias.copy().rename(columns={
        "CATEGORIA": "Categoría",
        "TARJETAS": "Tarjetas",
        "PORCENTAJE": "Porcentaje (%)"
    })

    st.dataframe(
        tabla_cat,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Categoría": st.column_config.TextColumn("Categoría", width="medium"),
            "Tarjetas": st.column_config.NumberColumn("Tarjetas", format="%d"),
            "Porcentaje (%)": st.column_config.NumberColumn("Porcentaje (%)", format="%.1f"),
        }
    )


def tabla_empresas(df_empresas):
    """Tabla de empresas afiliadas."""
    st.subheader("🏪 Empresas Afiliadas al Programa")

    st.dataframe(
        df_empresas.rename(columns={"EMPRESA": "Empresa afiliada"}),
        use_container_width=True,
        hide_index=True,
        column_config={
            "Empresa afiliada": st.column_config.TextColumn("Empresa afiliada", width="large"),
        }
    )


def observaciones(df_categorias, df_resumen, df_empresas):
    """Observaciones automáticas."""
    st.subheader("📝 Observaciones")

    emitidas = int(df_resumen.loc[df_resumen["ESTADO"] == "Emitidas", "CANTIDAD"].iloc[0])
    categorizadas = int(df_categorias["TARJETAS"].sum())

    categoria_top = df_categorias.loc[df_categorias["TARJETAS"].idxmax()]
    categoria_min = df_categorias.loc[df_categorias["TARJETAS"].idxmin()]

    st.info(
        f"""
- El programa registra un total de **{emitidas:,} tarjetas emitidas**.
- No se presenta el indicador de tarjetas entregadas porque el dato aún no se encuentra confirmado con exactitud.
- Se cuenta con **{categorizadas:,} tarjetas categorizadas** en la base referencial del programa.
- La categoría con mayor participación es **{categoria_top['CATEGORIA']}**, con **{int(categoria_top['TARJETAS'])}** tarjetas, equivalente al **{categoria_top['PORCENTAJE']:.1f}%** del total categorizado.
- La categoría **{categoria_min['CATEGORIA']}** concentra **{int(categoria_min['TARJETAS'])}** tarjetas, equivalente al **{categoria_min['PORCENTAJE']:.1f}%**.
- El programa cuenta con **más de 15 empresas afiliadas**, entre ellas establecimientos gastronómicos y comerciales del distrito.
- La predominancia de la categoría Premium evidencia una alta aceptación del programa y refuerza su rol como herramienta de incentivo al cumplimiento tributario.
"""
    )


def conclusion():
    """Conclusión ejecutiva."""
    st.subheader("✅ Conclusión")

    st.success(
        """
El Programa **PACHACARD** se consolida como una herramienta municipal de reconocimiento al contribuyente puntual, al combinar incentivos concretos con beneficios comerciales dentro del distrito.

El reporte se concentra en las tarjetas emitidas, la distribución registrada por categoría y la red de empresas afiliadas. El indicador de tarjetas entregadas queda excluido hasta contar con una cifra validada.
"""
    )


def show_pachacard_module():
    """Módulo completo de PACHACARD."""
    st.header("💳 Módulo del Programa PACHACARD")
    st.markdown("---")

    df_categorias, df_resumen, df_empresas = load_pachacard_data()

    if df_categorias is None or df_categorias.empty:
        st.error("No se pudieron cargar los datos.")
        return

    estadisticas_generales(df_categorias, df_resumen, df_empresas)
    st.markdown("---")

    grafico_distribucion_categorias(df_categorias)
    st.markdown("---")

    grafico_comparativo_categorias(df_categorias)
    st.markdown("---")

    tabla_resumen(df_categorias, df_resumen)
    st.markdown("---")

    tabla_empresas(df_empresas)
    st.markdown("---")

    observaciones(df_categorias, df_resumen, df_empresas)
    st.markdown("---")

    conclusion()

import pandas as pd
import plotly.express as px
import streamlit as st
from pathlib import Path
from utils.helpers import get_spanish_month
from modules.ferias_plaza import show_ferias_plaza_module

# Paleta de colores
COLOR_MAP = px.colors.qualitative.Set3

FERIAS_MACRO_MANUALES = {
    "2025": [
        {
            "FERIA": "Feria Dominical Noviembre 2025",
            "INGRESO": "2025-11-01",
            "MACRO_CATEGORIA": "ARTESANIA",
            "PARTICIPANTES": 112,
            "MONTO_TOTAL": 2240.0,
        },
        {
            "FERIA": "Feria Dominical Noviembre 2025",
            "INGRESO": "2025-11-01",
            "MACRO_CATEGORIA": "GASTRONOMIA",
            "PARTICIPANTES": 101,
            "MONTO_TOTAL": 3030.0,
        },
        {
            "FERIA": "Navidad 2025",
            "INGRESO": "2025-12-24",
            "MACRO_CATEGORIA": "ARTESANIA",
            "PARTICIPANTES": 405,
            "MONTO_TOTAL": 16200.0,
        },
        {
            "FERIA": "Navidad 2025",
            "INGRESO": "2025-12-24",
            "MACRO_CATEGORIA": "GASTRONOMIA",
            "PARTICIPANTES": 18,
            "MONTO_TOTAL": 1080.0,
        },
        {
            "FERIA": "Año Nuevo 2025",
            "INGRESO": "2025-12-31",
            "MACRO_CATEGORIA": "ARTESANIA",
            "PARTICIPANTES": 279,
            "MONTO_TOTAL": 16740.0,
        },
        {
            "FERIA": "Año Nuevo 2025",
            "INGRESO": "2025-12-31",
            "MACRO_CATEGORIA": "GASTRONOMIA",
            "PARTICIPANTES": 1,
            "MONTO_TOTAL": 30.0,
        },
    ],
}


def agregar_ferias_macro_manuales(df, year):
    registros = FERIAS_MACRO_MANUALES.get(str(year), [])
    if not registros:
        return df

    filas = []
    for registro in registros:
        monto_unitario = registro["MONTO_TOTAL"] / registro["PARTICIPANTES"]
        for _ in range(registro["PARTICIPANTES"]):
            filas.append({
                "FERIA": registro["FERIA"],
                "INGRESO": pd.to_datetime(registro["INGRESO"]),
                "MES": get_spanish_month(pd.to_datetime(registro["INGRESO"]).month),
                "MACRO_CATEGORIA": registro["MACRO_CATEGORIA"],
                "MONTO": monto_unitario,
            })

    return pd.concat([df, pd.DataFrame(filas)], ignore_index=True)


def load_ferias_data(year):
    archivo = Path(__file__).parent.parent / "data" / "ferias" / f"{year}_ferias_macro.csv"
    if not archivo.exists():
        return pd.DataFrame()

    df = pd.read_csv(archivo, sep=';', encoding='utf-8')

    if 'INGRESO' in df.columns:
        df['INGRESO'] = pd.to_datetime(df['INGRESO'], dayfirst=True, errors='coerce')
    elif 'FECHA DE INGRESO' in df.columns:
        df['INGRESO'] = pd.to_datetime(df['FECHA DE INGRESO'], dayfirst=True, errors='coerce')

    df['MES'] = df['INGRESO'].dt.month.map(get_spanish_month)
    return agregar_ferias_macro_manuales(df, year)


def show_ferias_module():
    st.header("📊 Módulo de Ferias Ambulatorias")
    st.markdown("---")

    st.subheader("🏛️ Selecciona la sede")
    sede = st.radio("Sede:", ["3 Marías", "Plaza Cívica"], horizontal=True)

    if sede == "3 Marías":
        show_ferias_tres_marias()
    else:
        show_ferias_plaza_module()


# === 3 MARIAS LOGIC ===
def show_ferias_tres_marias():
    if 'year_sel' not in st.session_state:
        st.session_state.year_sel = '2025'
    cols = st.columns(4)
    if cols[0].button('2023'):
        st.session_state.year_sel = '2023'
    if cols[1].button('2024'):
        st.session_state.year_sel = '2024'
    if cols[2].button('2025'):
        st.session_state.year_sel = '2025'
    if cols[3].button('Histórico'):
        st.session_state.year_sel = 'Histórico'

    year = st.session_state.year_sel
    st.markdown(f'**Año seleccionado:** {year} — Sede: 3 Marías')

    if year == 'Histórico':
        dfs = []
        for y in ['2023', '2024', '2025']:
            d = load_ferias_data(y)
            if not d.empty:
                d['AÑO'] = y
                dfs.append(d)
        df = pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()
    else:
        df = load_ferias_data(year)

    if df.empty:
        st.warning('No se encontraron registros para la opción seleccionada.')
        return

    # KPIs
    c1, c2, c3 = st.columns(3)
    c1.metric('📆 Ferias', df['FERIA'].nunique())
    c2.metric('👥 Participantes', len(df))
    c3.metric('🏷️ Categorías', df['MACRO_CATEGORIA'].nunique())

    st.markdown('---')
    cA, cB = st.columns(2)
    with cA:
        grafico_participantes(df)
    with cB:
        grafico_recaudacion(df)

    st.markdown('---')
    grafico_macro_rubros(df)
    st.markdown('---')
    grafico_trend_mensual(df)

    if year == 'Histórico':
        st.markdown('---')
        st.subheader('👥 Participantes Totales por Año')
        p_df = df['AÑO'].value_counts().reset_index()
        p_df.columns = ['AÑO', 'PARTICIPANTES']
        p_df = p_df.sort_values('AÑO')
        fig = px.bar(
            p_df,
            x='AÑO', y='PARTICIPANTES',
            color='AÑO', color_discrete_sequence=COLOR_MAP,
            text='PARTICIPANTES',
            title='Total de Participantes por Año'
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)


# ==== GRAFICOS TRES MARIAS ====
def grafico_participantes(df):
    st.subheader("👥 Participantes por Feria")
    orden = st.selectbox("Ordenar por:", ["Por Fecha", "Ascendente", "Descendente"], key="orden_part")

    participantes = df['FERIA'].value_counts().reset_index()
    participantes.columns = ['FERIA', 'N_PARTICIPANTES']

    fechas = (
        df[df['INGRESO'].notna()]
        .groupby("FERIA")['INGRESO']
        .agg(lambda x: x.mode().iloc[0] if not x.mode().empty else x.min())
        .reset_index()
    )
    participantes = participantes.merge(fechas, on="FERIA", how="left")

    if orden == "Por Fecha":
        participantes = participantes.sort_values("INGRESO")
    elif orden == "Ascendente":
        participantes = participantes.sort_values("N_PARTICIPANTES")
    elif orden == "Descendente":
        participantes = participantes.sort_values("N_PARTICIPANTES", ascending=False)

    fig = px.bar(
        participantes,
        x='FERIA', y='N_PARTICIPANTES',
        color='FERIA', color_discrete_sequence=COLOR_MAP,
        text='N_PARTICIPANTES'
    )
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)


def grafico_recaudacion(df):
    st.subheader("💰 Recaudación Total por Feria")
    orden = st.selectbox("Ordenar por:", ["Por Fecha", "Ascendente", "Descendente"], key="orden_monto")

    df['MONTO'] = pd.to_numeric(df['MONTO'], errors='coerce')
    recaudacion = df.groupby('FERIA')['MONTO'].sum().reset_index()

    fechas = (
        df[df['INGRESO'].notna()]
        .groupby("FERIA")['INGRESO']
        .agg(lambda x: x.mode().iloc[0] if not x.mode().empty else x.min())
        .reset_index()
    )
    recaudacion = recaudacion.merge(fechas, on="FERIA", how="left")

    if orden == "Por Fecha":
        recaudacion = recaudacion.sort_values("INGRESO")
    elif orden == "Ascendente":
        recaudacion = recaudacion.sort_values("MONTO")
    elif orden == "Descendente":
        recaudacion = recaudacion.sort_values("MONTO", ascending=False)

    fig = px.bar(
        recaudacion,
        x='FERIA', y='MONTO',
        color='FERIA', color_discrete_sequence=COLOR_MAP,
        text='MONTO'
    )
    fig.update_traces(textposition='outside')
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)


def grafico_macro_rubros(df):
    rubros = df['MACRO_CATEGORIA'].value_counts().reset_index()
    rubros.columns = ['MACRO_CATEGORIA', 'CANTIDAD']
    fig = px.bar(
        rubros.head(10), x='MACRO_CATEGORIA', y='CANTIDAD',
        title='🏷️ Top 10 Macro Categorías',
        color='MACRO_CATEGORIA', color_discrete_sequence=COLOR_MAP,
        text='CANTIDAD'
    )
    fig.update_traces(textposition='outside')
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)


def grafico_trend_mensual(df):
    df_valid = df[df['INGRESO'].notna()]
    if df_valid.empty:
        st.info('No hay fechas para mostrar tendencia mensual.')
        return

    monthly = (
        df_valid.groupby(df_valid['INGRESO'].dt.to_period('M'))
        .size()
        .reset_index(name='INSCRIPCIONES')
    )
    monthly['MES_ANIO'] = monthly['INGRESO'].dt.to_timestamp()
    fig = px.line(
        monthly,
        x='MES_ANIO', y='INSCRIPCIONES',
        markers=True,
        line_shape='spline',
        title='📈 Tendencia Mensual de Inscripciones',
        color_discrete_sequence=['#3498db']
    )
    fig.update_xaxes(
        tickformat='%b %Y',
        tickmode='array',
        tickvals=monthly['MES_ANIO'],
        ticktext=monthly['MES_ANIO'].dt.strftime('%b %Y')
    )
    st.plotly_chart(fig, use_container_width=True)

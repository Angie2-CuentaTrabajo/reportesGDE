import pandas as pd
import plotly.express as px
import streamlit as st
import re
import unicodedata
from pathlib import Path
from utils.helpers import get_spanish_month

COLOR_MAP = px.colors.qualitative.Set3
MESES_PLAZA = [
    'ENERO', 'FEBRERO', 'MARZO', 'ABRIL', 'MAYO', 'JUNIO',
    'JULIO', 'AGOSTO', 'SEPTIEMBRE', 'OCTUBRE', 'NOVIEMBRE', 'DICIEMBRE'
]
ARCHIVO_PLAZA_CONSOLIDADO = "COMERCIO AMBULATORIO - BD - FERIANTES DE LA PLAZA CÍVICA (1).csv"


def cargar_ferias_plaza_manuales():
    registros = []
    feria = "Feria Escolar 2026"

    for idx in range(1, 29):
        registros.append({
            "FERIA": feria,
            "MACRO_CATEGORIA": "FERIA ESCOLAR",
            "NOMBRES Y APELLIDOS": f"FERIA ESCOLAR PARTICIPANTE {idx:02d}",
            "MONTO": 720.0,
            "PAGO": "SI",
            "INGRESO": pd.Timestamp(year=2026, month=3, day=1),
        })

    for idx in range(1, 9):
        registros.append({
            "FERIA": feria,
            "MACRO_CATEGORIA": "FERIA ESCOLAR",
            "NOMBRES Y APELLIDOS": f"FERIA ESCOLAR PARTICIPANTE {idx:02d}",
            "MONTO": 140.0,
            "PAGO": "SI",
            "INGRESO": pd.Timestamp(year=2026, month=4, day=15),
        })

    df = pd.DataFrame(registros)
    df["AÑO"] = "2026"
    df["MES"] = df["INGRESO"].dt.month.map(get_spanish_month)
    return df


def normalizar_texto(valor):
    texto = str(valor or "").strip().upper()
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(char for char in texto if not unicodedata.combining(char))
    return texto


def normalizar_mes(valor):
    texto = normalizar_texto(valor).split(".")[0]
    if texto == "SETIEMBRE":
        texto = "SEPTIEMBRE"
    return texto


def sumar_montos(valor):
    texto = str(valor or "").strip()
    numeros = re.findall(r"\d+(?:[.,]\d+)?", texto)
    if not numeros:
        return 0.0
    return sum(float(numero.replace(",", ".")) for numero in numeros)


def cargar_datos_ferias_plaza_consolidado():
    archivo = Path(__file__).parent.parent / "data" / "ferias" / ARCHIVO_PLAZA_CONSOLIDADO
    if not archivo.exists():
        return pd.DataFrame()

    df = pd.read_csv(archivo, sep=",", encoding="utf-8-sig", dtype=str)
    if df.empty:
        return pd.DataFrame()

    registros = []
    anio = 2024
    mes_anterior = 0

    # Despues de las 4 columnas base, el archivo alterna MONTO y N DE RECIBO.
    columnas_monto = list(df.columns[4::2])
    for columna in columnas_monto:
        mes = normalizar_mes(columna)
        if mes not in MESES_PLAZA:
            continue

        mes_num = MESES_PLAZA.index(mes) + 1
        if mes_anterior and mes_num <= mes_anterior:
            anio += 1
        mes_anterior = mes_num

        for _, row in df.iterrows():
            monto = sumar_montos(row.get(columna))
            if monto <= 0:
                continue

            nombre = str(row.get("NOMBRES Y APELLIDOS", "")).strip().upper()
            if not nombre:
                continue

            registros.append({
                "FERIA": f"Plaza Cívica {anio}",
                "MACRO_CATEGORIA": str(row.get("GIRO", "OTROS")).strip().upper(),
                "NOMBRES Y APELLIDOS": nombre,
                "MONTO": monto,
                "PAGO": "SI",
                "INGRESO": pd.Timestamp(year=anio, month=mes_num, day=1),
                "AÑO": str(anio),
            })

    if not registros:
        return pd.DataFrame()

    df_final = pd.DataFrame(registros)
    df_final["MES"] = df_final["INGRESO"].dt.month.map(get_spanish_month)
    return pd.concat([df_final, cargar_ferias_plaza_manuales()], ignore_index=True)

def cargar_datos_ferias_plaza(anio):
    df_consolidado = cargar_datos_ferias_plaza_consolidado()
    if not df_consolidado.empty:
        return df_consolidado[df_consolidado["AÑO"] == str(anio)].copy()

    archivo = Path(__file__).parent.parent / 'data' / 'ferias' / f'{anio}_ferias_manchay.csv'
    if not archivo.exists():
        return pd.DataFrame()

    df = pd.read_csv(archivo, sep=';', encoding='utf-8')

    registros = []
    for _, row in df.iterrows():
        feria = f"Plaza Cívica {anio}"
        macro = str(row.get('GIRO', 'OTROS')).strip().upper()
        nombre = str(row.get('NOMBRES Y APELLIDOS', '')).strip().upper()

        for mes_num, mes in enumerate(MESES_PLAZA, start=1):
            monto = row.get(mes)
            if pd.notna(monto):
                try:
                    monto_num = float(monto)
                    pago = 'SI' if monto_num > 0 else 'NO'
                except:
                    continue

                ingreso = pd.Timestamp(year=int(anio), month=mes_num, day=1)
                registros.append({
                    'FERIA': feria,
                    'MACRO_CATEGORIA': macro,
                    'NOMBRES Y APELLIDOS': nombre,
                    'MONTO': monto_num,
                    'PAGO': pago,
                    'INGRESO': ingreso
                })

    df_final = pd.DataFrame(registros)
    df_final['MES'] = df_final['INGRESO'].dt.month.map(get_spanish_month)
    return df_final

def grafico_participantes(df):
    st.subheader("👥 Participantes por Feria")
    st.caption("Este gráfico muestra la cantidad única de participantes activos por cada feria realizada.")
    orden = st.selectbox("Ordenar por:", ["Por Fecha", "Ascendente", "Descendente"], key="orden_part_plaza")

    participantes_validos = df[df['MONTO'] > 0][['FERIA', 'NOMBRES Y APELLIDOS']].drop_duplicates()
    participantes = participantes_validos.groupby('FERIA').size().reset_index(name='N_PARTICIPANTES')

    fechas = df[df['INGRESO'].notna()].groupby("FERIA")['INGRESO'].agg(lambda x: x.mode().iloc[0] if not x.mode().empty else x.min()).reset_index()
    participantes = participantes.merge(fechas, on="FERIA", how="left")

    if orden == "Por Fecha":
        participantes = participantes.sort_values("INGRESO")
    elif orden == "Ascendente":
        participantes = participantes.sort_values("N_PARTICIPANTES")
    elif orden == "Descendente":
        participantes = participantes.sort_values("N_PARTICIPANTES", ascending=False)

    fig = px.bar(participantes, x='FERIA', y='N_PARTICIPANTES', color='FERIA', text='N_PARTICIPANTES', color_discrete_sequence=COLOR_MAP)
    fig.update_layout(showlegend=False, xaxis_title="Feria", yaxis_title="Participantes")
    st.plotly_chart(fig, use_container_width=True)

def grafico_recaudacion(df):
    st.subheader("💰 Recaudación Total por Feria")
    st.caption("Se muestra el total recaudado por feria según los pagos realizados.")
    orden = st.selectbox("Ordenar por:", ["Por Fecha", "Ascendente", "Descendente"], key="orden_monto_plaza")

    recaudacion = df.groupby('FERIA')['MONTO'].sum().reset_index()
    fechas = df[df['INGRESO'].notna()].groupby("FERIA")['INGRESO'].agg(lambda x: x.mode().iloc[0] if not x.mode().empty else x.min()).reset_index()
    recaudacion = recaudacion.merge(fechas, on="FERIA", how="left")

    if orden == "Por Fecha":
        recaudacion = recaudacion.sort_values("INGRESO")
    elif orden == "Ascendente":
        recaudacion = recaudacion.sort_values("MONTO")
    elif orden == "Descendente":
        recaudacion = recaudacion.sort_values("MONTO", ascending=False)

    fig = px.bar(recaudacion, x='FERIA', y='MONTO', color='FERIA', text='MONTO', color_discrete_sequence=COLOR_MAP)
    fig.update_traces(textposition='outside')
    fig.update_layout(showlegend=False, xaxis_title="Feria", yaxis_title="Monto Recaudado (S/.)")
    st.plotly_chart(fig, use_container_width=True)

def grafico_macro_rubros(df):
    st.subheader("🏷️ Top 5 Macro Categorías")
    st.caption("Se destacan las categorías con mayor número de participantes únicos.")
    rubros = df[df['MONTO'] > 0][['MACRO_CATEGORIA', 'NOMBRES Y APELLIDOS']].drop_duplicates()
    rubros = rubros.groupby('MACRO_CATEGORIA').size().reset_index(name='CANTIDAD').sort_values('CANTIDAD', ascending=False).head(5)

    fig = px.bar(rubros, x='MACRO_CATEGORIA', y='CANTIDAD', color='MACRO_CATEGORIA', text='CANTIDAD', color_discrete_sequence=COLOR_MAP)
    fig.update_traces(textposition='outside')
    fig.update_layout(showlegend=False, xaxis_title="Macro Categoría", yaxis_title="Participantes Únicos")
    st.plotly_chart(fig, use_container_width=True)

def grafico_trend_mensual(df):
    st.subheader("📈 Tendencia Mensual de Inscripciones")
    st.caption("Visualiza cómo evolucionó la participación en las ferias mes a mes.")
    df_valid = df[df['INGRESO'].notna()]
    if df_valid.empty:
        st.info('No hay fechas para mostrar tendencia mensual.')
        return

    monthly = df_valid.groupby(df_valid['INGRESO'].dt.to_period('M')).size().reset_index(name='INSCRIPCIONES')
    monthly['MES_ANIO'] = monthly['INGRESO'].dt.to_timestamp()
    fig = px.line(monthly, x='MES_ANIO', y='INSCRIPCIONES', markers=True, line_shape='spline', color_discrete_sequence=['#3498db'])
    fig.update_xaxes(tickformat='%b %Y', tickvals=monthly['MES_ANIO'], ticktext=monthly['MES_ANIO'].dt.strftime('%b %Y'))
    fig.update_layout(xaxis_title="Mes", yaxis_title="Cantidad de Inscripciones")
    st.plotly_chart(fig, use_container_width=True)

def grafico_recaudacion_mensual_comparada():
    st.subheader("Recaudacion mensual por año")

    path_base = Path(__file__).parent.parent / "data" / "ferias"
    registros = []

    for anio in ["2024", "2025"]:
        archivo = path_base / f"{anio}_ferias_manchay.csv"
        if not archivo.exists():
            continue

        df = pd.read_csv(archivo, sep=";", encoding="utf-8")
        for mes_num, mes in enumerate(MESES_PLAZA, start=1):
            monto = (
                pd.to_numeric(df[mes], errors="coerce").fillna(0).sum()
                if mes in df.columns
                else 0
            )
            registros.append({
                "ANIO": anio,
                "MES": get_spanish_month(mes_num),
                "MES_NUM": mes_num,
                "RECAUDACION": float(monto),
            })

    if not registros:
        st.info("No hay datos de recaudacion mensual para mostrar.")
        return

    resumen = pd.DataFrame(registros)
    meses_orden = [get_spanish_month(i) for i in range(1, 13)]

    fig = px.bar(
        resumen,
        x="MES",
        y="RECAUDACION",
        color="ANIO",
        barmode="group",
        text="RECAUDACION",
        category_orders={"MES": meses_orden},
        color_discrete_sequence=COLOR_MAP,
        labels={"MES": "Mes", "RECAUDACION": "Recaudacion (S/)", "ANIO": "Año"},
    )
    fig.update_traces(texttemplate="S/ %{y:,.0f}", textposition="outside")
    fig.update_layout(xaxis_title="Mes", yaxis_title="Recaudacion (S/)", legend_title="Año")
    st.plotly_chart(fig, use_container_width=True)

    tabla = resumen.pivot(index="MES", columns="ANIO", values="RECAUDACION").reset_index()
    tabla["MES_NUM"] = tabla["MES"].map({mes: idx for idx, mes in enumerate(meses_orden, start=1)})
    tabla = tabla.sort_values("MES_NUM").drop(columns=["MES_NUM"])
    tabla["TOTAL"] = tabla[[col for col in ["2024", "2025"] if col in tabla.columns]].sum(axis=1)

    st.dataframe(
        tabla,
        use_container_width=True,
        hide_index=True,
        column_config={
            "MES": st.column_config.TextColumn("Mes"),
            "2024": st.column_config.NumberColumn("2024", format="S/ %.2f"),
            "2025": st.column_config.NumberColumn("2025", format="S/ %.2f"),
            "TOTAL": st.column_config.NumberColumn("Total", format="S/ %.2f"),
        },
    )
def grafico_recaudacion_mensual_comparada():
    st.subheader("Recaudacion mensual por aÃ±o")

    consolidado = cargar_datos_ferias_plaza_consolidado()
    if consolidado.empty:
        st.info("No hay datos de recaudacion mensual para mostrar.")
        return

    resumen = (
        consolidado.assign(
            ANIO=consolidado["AÑO"].astype(str),
            MES_NUM=consolidado["INGRESO"].dt.month,
        )
        .groupby(["ANIO", "MES_NUM"])["MONTO"]
        .sum()
        .reset_index(name="RECAUDACION")
    )
    resumen["MES"] = resumen["MES_NUM"].map(get_spanish_month)
    meses_orden = [get_spanish_month(i) for i in range(1, 13)]

    fig = px.bar(
        resumen,
        x="MES",
        y="RECAUDACION",
        color="ANIO",
        barmode="group",
        text="RECAUDACION",
        category_orders={"MES": meses_orden},
        color_discrete_sequence=COLOR_MAP,
        labels={"MES": "Mes", "RECAUDACION": "Recaudacion (S/)", "ANIO": "AÃ±o"},
    )
    fig.update_traces(texttemplate="S/ %{y:,.0f}", textposition="outside")
    fig.update_layout(xaxis_title="Mes", yaxis_title="Recaudacion (S/)", legend_title="AÃ±o")
    st.plotly_chart(fig, use_container_width=True)

    tabla = resumen.pivot(index="MES", columns="ANIO", values="RECAUDACION").reset_index()
    tabla["MES_NUM"] = tabla["MES"].map({mes: idx for idx, mes in enumerate(meses_orden, start=1)})
    tabla = tabla.sort_values("MES_NUM").drop(columns=["MES_NUM"])
    anios_tabla = [col for col in ["2024", "2025", "2026"] if col in tabla.columns]
    tabla["TOTAL"] = tabla[anios_tabla].sum(axis=1)

    st.dataframe(
        tabla,
        use_container_width=True,
        hide_index=True,
        column_config={
            "MES": st.column_config.TextColumn("Mes"),
            "2024": st.column_config.NumberColumn("2024", format="S/ %.2f"),
            "2025": st.column_config.NumberColumn("2025", format="S/ %.2f"),
            "2026": st.column_config.NumberColumn("2026", format="S/ %.2f"),
            "TOTAL": st.column_config.NumberColumn("Total", format="S/ %.2f"),
        },
    )


def show_ferias_plaza_module():
    st.header("Ferias de la Plaza Cívica")
    st.markdown('---')

    if 'year_sel_plaza' not in st.session_state:
        st.session_state.year_sel_plaza = '2025'
    cols = st.columns(4)
    if cols[0].button('2024', key="btn_2024_plaza"):
        st.session_state.year_sel_plaza = '2024'
    if cols[1].button('2025', key="btn_2025_plaza"):
        st.session_state.year_sel_plaza = '2025'
    if cols[3].button('2026', key="btn_2026_plaza"):
        st.session_state.year_sel_plaza = '2026'
    if cols[2].button('Ambos Años', key="btn_hist_plaza"):
        st.session_state.year_sel_plaza = 'Histórico'

    year = st.session_state.year_sel_plaza
    st.markdown(f'**Año seleccionado:** {year}')

    if year == 'Histórico':
        dfs = []
        for y in ['2024', '2025', '2026']:
            d = cargar_datos_ferias_plaza(y)
            if not d.empty:
                d['AÑO'] = y
                dfs.append(d)
        df = pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()
    else:
        df = cargar_datos_ferias_plaza(year)

    if df.empty:
        st.warning('No se encontraron registros para la opción seleccionada.')
        return

    participantes_unicos = df[df['MONTO'] > 0][['FERIA', 'NOMBRES Y APELLIDOS']].drop_duplicates()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric('📆 Ferias', df['FERIA'].nunique())
    c2.metric('👥 Participantes', len(participantes_unicos))
    c3.metric('🏷️ Categorías', df['MACRO_CATEGORIA'].nunique())
    c4.metric('Recaudacion', f"S/ {df['MONTO'].sum():,.2f}")

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
    st.markdown('---')
    grafico_recaudacion_mensual_comparada()

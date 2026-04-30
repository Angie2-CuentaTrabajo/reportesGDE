import hashlib
import inspect
from datetime import datetime
from io import BytesIO

import pandas as pd

SPANISH_MONTHS = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
    5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
    9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
}

def get_spanish_month(month_number):
    """Devuelve el nombre del mes en español"""
    return SPANISH_MONTHS.get(month_number, "Mes inválido")

def format_date(date_str):
    """Formatea fecha a texto en español"""
    try:
        date_obj = datetime.strptime(date_str, "%d/%m/%Y")
        return f"{date_obj.day} de {SPANISH_MONTHS[date_obj.month]} de {date_obj.year}"
    except:
        return date_str


def dataframe_to_excel_bytes(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Reporte")
    return output.getvalue()


def install_excel_dataframe_download(st_module):
    if getattr(st_module, "_excel_dataframe_download_installed", False):
        return

    original_dataframe = st_module.dataframe

    def dataframe_with_download(data=None, *args, **kwargs):
        result = original_dataframe(data, *args, **kwargs)
        if isinstance(data, pd.DataFrame):
            excel_bytes = dataframe_to_excel_bytes(data)
            caller = inspect.stack()[1]
            key_source = (
                f"{caller.filename}|{caller.lineno}|"
                f"{hashlib.md5(excel_bytes).hexdigest()}"
            )
            key = f"download_excel_{hashlib.md5(key_source.encode('utf-8')).hexdigest()}"
            st_module.download_button(
                "Descargar Excel",
                data=excel_bytes,
                file_name="reporte.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key=key,
                use_container_width=True,
            )
        return result

    st_module.dataframe = dataframe_with_download
    st_module._excel_dataframe_download_installed = True

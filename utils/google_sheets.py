import io
import re
import unicodedata

import pandas as pd
import streamlit as st


def normalize_column_name(value):
    """Normalize column labels from Google Sheets without depending on exact accents."""
    text = str(value or "").strip().upper()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(char for char in text if not unicodedata.combining(char))
    text = re.sub(r"\s+", " ", text)
    return text


def normalize_text(value):
    text = str(value or "").strip().upper()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(char for char in text if not unicodedata.combining(char))
    text = re.sub(r"\s+", " ", text)
    return text


def parse_money_series(series):
    values = (
        series.astype(str)
        .str.strip()
        .str.replace("S/", "", regex=False)
        .str.replace(" ", "", regex=False)
        .str.replace(",", ".", regex=False)
    )
    return pd.to_numeric(values, errors="coerce").fillna(0.0)


@st.cache_data(ttl=600, show_spinner=False)
def load_resoluciones_sheet():
    """Read the private Google Sheet configured in Streamlit secrets."""
    try:
        import gspread
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaIoBaseDownload
        from google.oauth2.service_account import Credentials
    except ImportError as exc:
        raise RuntimeError(
            "Faltan dependencias para leer Google Drive/Sheets. Instala gspread, google-auth y google-api-python-client."
        ) from exc

    required_scopes = [
        "https://www.googleapis.com/auth/spreadsheets.readonly",
        "https://www.googleapis.com/auth/drive.readonly",
    ]
    credentials = Credentials.from_service_account_info(
        dict(st.secrets["gcp_service_account"]),
        scopes=required_scopes,
    )

    client = gspread.authorize(credentials)
    sheet_id = st.secrets["GOOGLE_SHEET_ID"]
    tab_name = st.secrets["GOOGLE_SHEET_TAB"]
    try:
        worksheet = client.open_by_key(sheet_id).worksheet(tab_name)
        records = worksheet.get_all_records()
        df = pd.DataFrame(records)
    except Exception:
        drive = build("drive", "v3", credentials=credentials)
        metadata = drive.files().get(fileId=sheet_id, fields="mimeType,name").execute()
        mime_type = metadata.get("mimeType", "")
        buffer = io.BytesIO()

        if mime_type == "application/vnd.google-apps.spreadsheet":
            request = drive.files().export_media(
                fileId=sheet_id,
                mimeType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        else:
            request = drive.files().get_media(fileId=sheet_id)

        downloader = MediaIoBaseDownload(buffer, request)
        done = False
        while not done:
            _, done = downloader.next_chunk()

        buffer.seek(0)
        df = pd.read_excel(buffer, sheet_name=tab_name)

    df.columns = [normalize_column_name(col) for col in df.columns]
    return df


def get_resoluciones_sheet_or_none():
    try:
        df = load_resoluciones_sheet()
        return df if df is not None and not df.empty else None
    except Exception as exc:
        st.warning(f"No se pudo leer Drive. Se usaran datos locales. Detalle: {exc}")
        return None

import os
import tempfile
from io import BytesIO
from pathlib import Path

import streamlit as st
from google.api_core.exceptions import GoogleAPIError

st.set_page_config(page_title="DOCX Translator", layout="centered")

_mode = None
try:
    from app.translator_core_patched import translate_docx_buf
    _mode = "buf"
except Exception:
    try:
        from app.translator_core import translate_docx_buf
        _mode = "buf"
    except Exception:
        from app.translator_core import translate_docx
        _mode = "filelike"

def setup_gcp_from_secrets():
    try:
        gcp_cfg = st.secrets["gcp"]
    except Exception:
        return
    with tempfile.NamedTemporaryFile("w", delete=False, suffix=".json") as f:
        f.write(gcp_cfg.get("key", ""))
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = f.name
    if gcp_cfg.get("project"):
        os.environ["GCP_PROJECT_ID"] = gcp_cfg["project"]
        os.environ["GOOGLE_CLOUD_PROJECT"] = gcp_cfg["project"]

setup_gcp_from_secrets()


uploaded = st.file_uploader("Загрузите .docx", type=["docx"])

col1, col2 = st.columns(2)
with col1:
    target_lang = st.selectbox(
        "Язык перевода",
        options=[("kk", "Қазақша"), ("ru", "Русский")],
        index=0,
        format_func=lambda x: x[1],
    )[0]
with col2:
    use_auto_gloss = st.checkbox("глоссарий", value=True)

glossary_path: str | None = None
if use_auto_gloss:
    glossary_path = "glossaries/ru_kk.csv" if target_lang == "kk" else "glossaries/kk_ru.csv"
    if not Path(glossary_path).exists():
        st.warning(f"Глоссарий не найден: {glossary_path}")
        glossary_path = None
else:
    user_csv = st.file_uploader("CSV", type=["csv"], key="gls")
    if user_csv:
        tmp = Path("glossaries/_uploaded_glossary.csv")
        tmp.parent.mkdir(parents=True, exist_ok=True)
        tmp.write_bytes(user_csv.read())
        glossary_path = str(tmp)

gcp_project = os.getenv("GCP_PROJECT_ID") or os.getenv("GOOGLE_CLOUD_PROJECT") or ""

if st.button("Перевести"):
    if not uploaded:
        st.error("Загрузите .docx файл")
        st.stop()
    if not gcp_project:
        st.error("Не найден GCP")
        st.stop()

    try:
        with st.spinner("Перевод"):
            data = uploaded.read()
            if _mode == "buf":
                try:
                    out_buf: BytesIO = translate_docx_buf(
                        data,
                        gcp_project=gcp_project,
                        target_lang=target_lang,
                        glossary_csv=glossary_path,
                    )
                except TypeError:
                    out_buf: BytesIO = translate_docx_buf(
                        data,
                        gcp_project=gcp_project,
                        target_lang=target_lang,
                    )
            else:
                try:
                    out_buf: BytesIO = translate_docx(
                        BytesIO(data),
                        target_lang=target_lang,
                        gcp_project=gcp_project,
                        glossary_csv=glossary_path,
                    )
                except TypeError:
                    out_buf: BytesIO = translate_docx(
                        BytesIO(data),
                        target_lang=target_lang,
                        gcp_project=gcp_project,
                    )

        out_name = Path(uploaded.name).stem + f".{target_lang}.docx"
        st.success("Готово")
        st.download_button(
            "Скачать перевод",
            data=out_buf.getvalue(),
            file_name=out_name,
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )

    except GoogleAPIError as e:
        st.error(f"Ошибка Google API: {getattr(e, 'message', str(e))}")
    except Exception as e:
        st.exception(e)

st.caption("secrets.toml ")

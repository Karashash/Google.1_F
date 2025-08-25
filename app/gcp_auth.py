import os, tempfile, streamlit as st
def setup_gcp():
    gcp = st.secrets["gcp"]
    with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as f:
        f.write(gcp["key"].encode())
        cred_path = f.name
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = cred_path
    os.environ["GOOGLE_CLOUD_PROJECT"] = gcp["project"]
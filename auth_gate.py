"""
auth_gate.py — Document AI Engine PoC access gate
--------------------------------------------------
Drop this file next to app.py (repo root) in BOTH repos:
  - fle-dify-demo-en
  - fle-dify-demo-jp

Integration (3 lines at the very top of app.py, right after `import streamlit as st`
and st.set_page_config):

    from auth_gate import require_access_code
    require_access_code(BRAND)   # place AFTER the BRAND dict is defined

Everything below the call runs only for authenticated sessions.

Secrets (Streamlit Cloud -> App -> Settings -> Secrets):

    ACCESS_CODE = "your-code-here"

Use a DIFFERENT code for the EN app and the JP app, so leaking one
does not expose the other. Rotate by simply editing the secret
(no redeploy needed; active sessions stay logged in until they expire).
"""

import hmac
import time

import streamlit as st

# Fallback labels (English). Each app can override via its BRAND dict —
# add the keys below to BRAND and they will be picked up automatically.
_DEFAULT_LABELS = {
    "gate_title": "Document AI Engine — α ver.",
    "gate_caption": "Internal access — enter the access code provided to you.",
    "gate_input": "Access code",
    "gate_button": "Enter",
    "gate_error": "Invalid access code.",
    "gate_footer": "FLE internal use only. Do not share this URL or code.",
}


def require_access_code(brand: dict | None = None) -> None:
    """Block the app until the correct access code is entered.

    Reads the expected code from st.secrets["ACCESS_CODE"].
    Labels can be overridden by adding gate_* keys to the BRAND dict.
    """
    labels = dict(_DEFAULT_LABELS)
    if brand:
        for k in _DEFAULT_LABELS:
            if k in brand:
                labels[k] = brand[k]

    if st.session_state.get("_authed", False):
        return  # already authenticated in this session

    expected = st.secrets.get("ACCESS_CODE", None)
    if not expected:
        st.error("ACCESS_CODE is not configured in Streamlit secrets.")
        st.stop()

    st.title(labels["gate_title"])
    st.caption(labels["gate_caption"])

    with st.form("auth_gate_form"):
        code = st.text_input(labels["gate_input"], type="password")
        submitted = st.form_submit_button(labels["gate_button"])

    if submitted:
        # constant-time comparison; small delay deters brute-force guessing
        if hmac.compare_digest(code.strip(), str(expected)):
            st.session_state["_authed"] = True
            st.rerun()
        else:
            time.sleep(1.0)
            st.error(labels["gate_error"])

    st.caption(labels["gate_footer"])
    st.stop()  # nothing below this line runs until authenticated

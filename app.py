# app.py
import streamlit as st
from login import mostrar_login
from portal_backup import mostrar_portal   # ← importa a função

st.set_page_config(
    page_title="Portal de Pedidos",
    page_icon="🛒",
    layout="wide"                          # ← muda para wide, que é o que o portal usa
)

if "logado" not in st.session_state:
    st.session_state.logado = False
if "usuario_atual" not in st.session_state:
    st.session_state.usuario_atual = ""
if "erro_login" not in st.session_state:
    st.session_state.erro_login = ""

if st.session_state.logado:
    mostrar_portal()                       # ← chama o portal
    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Sair"):
        st.session_state.logado = False
        st.session_state.usuario_atual = ""
        st.rerun()
else:
    mostrar_login()

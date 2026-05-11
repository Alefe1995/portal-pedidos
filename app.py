# app.py
import streamlit as st
from login import mostrar_login  # ← importa a função, não o módulo solto

st.set_page_config(
    page_title="Portal de Pedidos",
    page_icon="🛒",
    layout="centered"
)

if "logado" not in st.session_state:
    st.session_state.logado = False
if "usuario_atual" not in st.session_state:
    st.session_state.usuario_atual = ""
if "erro_login" not in st.session_state:
    st.session_state.erro_login = ""

if st.session_state.logado:
    st.title("✅ Área Administrativa")
    st.write(f"Bem-vindo, **{st.session_state.usuario_atual}**!")
    st.info("Portal carregado com sucesso.")
    if st.button("🚪 Sair"):
        st.session_state.logado = False
        st.session_state.usuario_atual = ""
        st.rerun()
else:
    mostrar_login()  # ← chama a função

# login.py
import streamlit as st

USUARIOS = {
    "admin": "123456",
    "usuario": "senha123"
}

def mostrar_login():
    st.title("🔐 Portal de Pedidos")
    st.markdown("---")

    with st.form("form_login"):
        usuario = st.text_input("Usuário")
        senha = st.text_input("Senha", type="password")
        botao_login = st.form_submit_button("Entrar", use_container_width=True)

    if botao_login:
        if usuario in USUARIOS and USUARIOS[usuario] == senha:
            st.session_state.logado = True
            st.session_state.usuario_atual = usuario
            st.session_state.erro_login = ""
            st.rerun()
        else:
            st.session_state.erro_login = "❌ Usuário ou senha inválidos."

    if st.session_state.erro_login:
        st.error(st.session_state.erro_login)

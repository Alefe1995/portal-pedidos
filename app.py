# app.py
import streamlit as st

st.set_page_config(
    page_title="Portal de Pedidos",
    page_icon="🛒",
    layout="centered"
)

USUARIOS = {
    "admin": "123456",
    "usuario": "senha123"
}

if "logado" not in st.session_state:
    st.session_state.logado = False
if "usuario_atual" not in st.session_state:
    st.session_state.usuario_atual = ""
if "erro_login" not in st.session_state:
    st.session_state.erro_login = ""

def tela_login():
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

def area_logada():
    st.title("✅ Área Administrativa")
    st.write(f"Bem-vindo, **{st.session_state.usuario_atual}**!")
    st.markdown("---")
    st.info("Portal carregado com sucesso.")

    if st.button("🚪 Sair", use_container_width=True):
        st.session_state.logado = False
        st.session_state.usuario_atual = ""
        st.rerun()

# Roteamento
if st.session_state.logado:
    area_logada()
else:
    tela_login()

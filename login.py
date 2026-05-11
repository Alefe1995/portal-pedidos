# login.py
import streamlit as st
import pandas as pd

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
            st.session_state.tipo_usuario = "MASTER"
            st.session_state.erro_login = ""
            st.rerun()
        else:
            st.session_state.erro_login = "❌ Usuário ou senha inválidos."

    if st.session_state.erro_login:
        st.error(st.session_state.erro_login)

# ====================================
# LOGIN RC
# ====================================

st.markdown("---")

st.subheader("Login RC")

email_rc = st.text_input(
    "Digite seu e-mail"
)

if st.button("Validar E-mail RC"):

    df_rc = pd.read_excel(
        "E-mailsRCs.xlsx"
    )

    rc_encontrado = None

    for _, linha in df_rc.iterrows():

        emails = [
            str(linha.get("Email1", "")).strip().lower(),
            str(linha.get("Email2", "")).strip().lower(),
            str(linha.get("Email3", "")).strip().lower()
        ]

        if email_rc.strip().lower() in emails:

            rc_encontrado = linha["RC"]

            break

    if rc_encontrado:

        st.success(
            f"RC encontrado: {rc_encontrado}"
        )

    else:

        st.error(
            "E-mail não encontrado."
        )

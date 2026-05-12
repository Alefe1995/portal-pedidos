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

    # ====================================
    # LOGIN ADMIN
    # ====================================
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

    email_rc = st.text_input("Digite seu e-mail", key="input_email_rc")  # ← key única

    if st.button("Validar E-mail RC"):
        df_rc = pd.read_excel("E-mailsRCs.xlsx")
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
            st.session_state.logado = True
            st.session_state.tipo_usuario = "RC"
            st.session_state.usuario_atual = email_rc
            st.session_state.rc_usuario = rc_encontrado
            st.rerun()
        else:
            st.error("E-mail não encontrado.")

    # ====================================
    # LOGIN COORDENADOR
    # ====================================
    st.markdown("---")
    st.subheader("Login Coordenador")

    email_coord = st.text_input("Digite o e-mail do coordenador", key="input_email_coord")  # ← key única

    if st.button("Validar E-mail Coordenador"):
        df_coord = pd.read_excel("E-mailsCoordenador.xlsx")
        coord_encontrado = None

        for _, linha in df_coord.iterrows():
            email_planilha = str(linha.get("E-mail", "")).strip().lower()
            if email_coord.strip().lower() == email_planilha:
                coord_encontrado = linha["Coordenador"]
                break

        if coord_encontrado:
            st.session_state.logado = True
            st.session_state.tipo_usuario = "COORDENADOR"
            st.session_state.usuario_atual = email_coord
            st.session_state.coordenador_usuario = coord_encontrado
            st.rerun()
        else:
            st.error("E-mail do coordenador não encontrado.")  # ← else duplicado removido

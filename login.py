# login.py
import streamlit as st
import pandas as pd
import smtplib
import random

from email.mime.text import MIMEText

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

            codigo_otp = str(
                random.randint(100000, 999999)
            )

            st.session_state.codigo_otp = codigo_otp

            st.session_state.rc_temp = rc_encontrado

            st.session_state.email_temp = email_rc

            try:

                remetente = st.secrets["EMAIL_REMETENTE"]

                senha = st.secrets["SENHA_EMAIL"]

                mensagem = MIMEText(
                    f"Seu código de acesso é: {codigo_otp}"
                )

                mensagem["Subject"] = "Código de acesso Portal"

                mensagem["From"] = remetente

                mensagem["To"] = email_rc

                servidor = smtplib.SMTP(
                    "smtp.gmail.com",
                    587
                )

                servidor.starttls()

                servidor.login(
                    remetente,
                    senha
                )

                servidor.sendmail(
                    remetente,
                    email_rc,
                    mensagem.as_string()
                )

                servidor.quit()

                st.success(
                    "Código enviado no e-mail!"
                )

            except Exception as erro:

                st.error(
                    f"Erro ao enviar código: {erro}"
                )
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

    # ====================================
    # TESTE ENVIO E-MAIL
    # ====================================
    
    st.markdown("---")
    
    if st.button("Testar envio de e-mail"):
    
        try:
    
            remetente = st.secrets["EMAIL_REMETENTE"]
    
            senha = st.secrets["SENHA_EMAIL"]
    
            destinatario = "alefef4@gmail.com"
    
            mensagem = MIMEText(
                "Seu teste de envio de e-mail do portal funcionou."
            )
    
            mensagem["Subject"] = "Teste Portal"
    
            mensagem["From"] = remetente
    
            mensagem["To"] = destinatario
    
            servidor = smtplib.SMTP(
                "smtp.gmail.com",
                587
            )
    
            servidor.starttls()
    
            servidor.login(
                remetente,
                senha
            )
    
            servidor.sendmail(
                remetente,
                destinatario,
                mensagem.as_string()
            )
    
            servidor.quit()
    
            st.success(
                "E-mail enviado com sucesso!"
            )
    
        except Exception as erro:
    
            st.error(
                f"Erro ao enviar e-mail: {erro}"
            )

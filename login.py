# login.py
import streamlit as st
import pandas as pd
import smtplib
import random
from email.mime.text import MIMEText


USUARIOS_MASTER = {
    "admin": "123456",
    "usuario": "senha123"
}


def enviar_email_otp(destinatario, codigo):
    remetente = st.secrets["EMAIL_REMETENTE"]
    senha     = st.secrets["SENHA_EMAIL"]
    mensagem             = MIMEText(f"Seu código de acesso ao Portal ADERE é: {codigo}")
    mensagem["Subject"]  = "Código de Acesso — Portal ADERE"
    mensagem["From"]     = remetente
    mensagem["To"]       = destinatario
    servidor = smtplib.SMTP("smtp.gmail.com", 587)
    servidor.starttls()
    servidor.login(remetente, senha)
    servidor.sendmail(remetente, destinatario, mensagem.as_string())
    servidor.quit()


def mostrar_login():

    st.markdown("""
    <style>

    #MainMenu, header, footer,
    [data-testid="stToolbar"],
    [data-testid="stDecoration"],
    [data-testid="stStatusWidget"],
    [data-testid="stFloatingButton"],
    .stDeployButton {
        display: none !important;
        visibility: hidden !important;
    }

    .stApp {
        background-color: #f1f3f6;
    }

    /* Página centralizada e compacta */
    .block-container {
        padding-top: 2.5rem !important;
        padding-bottom: 1rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        max-width: 460px !important;
        margin: 0 auto !important;
    }

    /* CARD */
    div[data-testid="stVerticalBlock"] div[data-testid="stVerticalBlock"]:has(
        div[data-testid="stTabs"]
    ) {
        background: white !important;
        border-radius: 16px !important;
        padding: 28px 32px 24px 32px !important;
        box-shadow: 0 6px 24px rgba(0,0,0,0.09) !important;
        border: 1px solid #e5e7eb !important;
    }

    /* Input label */
    .stTextInput label {
        font-size: 10px !important;
        font-weight: 700 !important;
        color: #374151 !important;
        letter-spacing: 0.07em !important;
        text-transform: uppercase !important;
        margin-bottom: 2px !important;
    }

    /* Input campo */
    .stTextInput input {
        border-radius: 8px !important;
        border: 1.5px solid #e5e7eb !important;
        padding: 8px 12px !important;
        font-size: 13px !important;
        background: #f9fafb !important;
        color: #111827 !important;
    }
    .stTextInput input:focus {
        border-color: #c00000 !important;
        box-shadow: 0 0 0 3px rgba(192,0,0,0.08) !important;
        background: white !important;
    }

    /* Botões */
    div[data-testid="stButton"] > button {
        background-color: #c00000 !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        font-size: 13px !important;
        padding: 9px 0 !important;
        width: 100% !important;
        margin-top: 4px !important;
        letter-spacing: 0.02em !important;
    }
    div[data-testid="stButton"] > button:hover {
        background-color: #a00000 !important;
    }

    /* Abas */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0 !important;
        background: #f3f4f6 !important;
        border-radius: 8px !important;
        padding: 3px !important;
        margin-bottom: 14px !important;
        border-bottom: none !important;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 6px !important;
        font-weight: 600 !important;
        font-size: 12px !important;
        color: #6b7280 !important;
        padding: 5px 14px !important;
        border: none !important;
        background: transparent !important;
    }
    .stTabs [aria-selected="true"] {
        background: white !important;
        color: #c00000 !important;
        box-shadow: 0 1px 4px rgba(0,0,0,0.10) !important;
    }
    .stTabs [data-baseweb="tab-border"],
    .stTabs [data-baseweb="tab-highlight"] {
        display: none !important;
    }

    .stAlert { border-radius: 8px !important; }

    </style>
    """, unsafe_allow_html=True)

    # Inicializa session_state
    for k in ["erro_login", "email_temp", "rc_temp", "email_coord_temp", "coord_temp"]:
        if k not in st.session_state:
            st.session_state[k] = ""
    for k in ["codigo_otp", "codigo_otp_coord"]:
        if k not in st.session_state:
            st.session_state[k] = None

    # =========================
    # CARD
    # =========================
    with st.container():

        # Cabeçalho compacto
        st.markdown("""
        <div style="text-align:center; margin-bottom:20px;">
            <div style="
                background:#fce8e8;
                border-radius:14px;
                width:52px; height:52px;
                display:inline-flex;
                align-items:center; justify-content:center;
                font-size:22px;
                margin-bottom:10px;
                box-shadow: 0 2px 8px rgba(192,0,0,0.12);
            ">✉️</div>
            <div style="font-size:20px; font-weight:800; color:#111827; margin-bottom:5px;">
                Acesse o Portal
            </div>
            <div style="font-size:12px; color:#6b7280; line-height:1.5;">
                Informe seu e-mail cadastrado. Vamos enviar um código de acesso temporário.
            </div>
        </div>
        """, unsafe_allow_html=True)

        aba_rc, aba_coord, aba_admin = st.tabs(["  🧑‍💼 RC  ", "📋 Coordenador", "🔑 Atendimento"])

        # ---- ABA RC ----
        with aba_rc:
            if st.session_state.codigo_otp:
                codigo_digitado = st.text_input(
                    "CÓDIGO RECEBIDO NO E-MAIL",
                    max_chars=6, placeholder="000000",
                    key="otp_rc_input"
                )
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✅ Validar", key="btn_validar_rc", use_container_width=True):
                        if codigo_digitado == str(st.session_state.codigo_otp):
                            st.session_state.logado        = True
                            st.session_state.tipo_usuario  = "RC"
                            st.session_state.usuario_atual = st.session_state.email_temp
                            st.session_state.rc_usuario    = st.session_state.rc_temp
                            st.session_state.codigo_otp    = None
                            st.rerun()
                        else:
                            st.error("❌ Código inválido.")
                with col2:
                    if st.button("↩ Voltar", key="btn_voltar_rc", use_container_width=True):
                        st.session_state.codigo_otp = None
                        st.rerun()
            else:
                email_rc = st.text_input(
                    "E-MAIL", placeholder="seu@email.com",
                    key="input_email_rc"
                )
                if st.button("Enviar Código →", key="btn_enviar_rc", use_container_width=True):
                    if not email_rc.strip():
                        st.warning("Informe seu e-mail.")
                    else:
                        df_rc = pd.read_excel("E-mailsRCs.xlsx")
                        rc_encontrado = None
                        for _, linha in df_rc.iterrows():
                            emails = [
                                str(linha.get("Email1", "")).strip().lower(),
                                str(linha.get("Email2", "")).strip().lower(),
                                str(linha.get("Email3", "")).strip().lower(),
                            ]
                            if email_rc.strip().lower() in emails:
                                rc_encontrado = linha["RC"]
                                break
                        if rc_encontrado:
                            codigo = str(random.randint(100000, 999999))
                            st.session_state.codigo_otp = codigo
                            st.session_state.rc_temp    = rc_encontrado
                            st.session_state.email_temp = email_rc
                            try:
                                enviar_email_otp(email_rc, codigo)
                                st.success("✅ Código enviado! Verifique seu e-mail.")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Erro ao enviar e-mail: {e}")
                        else:
                            st.error("❌ E-mail não encontrado.")

        # ---- ABA COORDENADOR ----
        with aba_coord:
            if st.session_state.codigo_otp_coord:
                codigo_coord_digitado = st.text_input(
                    "CÓDIGO RECEBIDO NO E-MAIL",
                    max_chars=6, placeholder="000000",
                    key="otp_coord_input"
                )
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✅ Validar", key="btn_validar_coord", use_container_width=True):
                        if codigo_coord_digitado == str(st.session_state.codigo_otp_coord):
                            st.session_state.logado              = True
                            st.session_state.tipo_usuario        = "COORDENADOR"
                            st.session_state.usuario_atual       = st.session_state.email_coord_temp
                            st.session_state.coordenador_usuario = st.session_state.coord_temp
                            st.session_state.codigo_otp_coord    = None
                            st.rerun()
                        else:
                            st.error("❌ Código inválido.")
                with col2:
                    if st.button("↩ Voltar", key="btn_voltar_coord", use_container_width=True):
                        st.session_state.codigo_otp_coord = None
                        st.rerun()
            else:
                email_coord = st.text_input(
                    "E-MAIL DO COORDENADOR", placeholder="coordenador@email.com",
                    key="input_email_coord"
                )
                if st.button("Enviar Código →", key="btn_enviar_coord", use_container_width=True):
                    if not email_coord.strip():
                        st.warning("Informe o e-mail.")
                    else:
                        df_coord = pd.read_excel("E-mailsCoordenador.xlsx")
                        coord_encontrado = None
                        for _, linha in df_coord.iterrows():
                            if email_coord.strip().lower() == str(linha.get("E-mail", "")).strip().lower():
                                coord_encontrado = linha["Coordenador"]
                                break
                        if coord_encontrado:
                            codigo_coord = str(random.randint(100000, 999999))
                            st.session_state.codigo_otp_coord = codigo_coord
                            st.session_state.coord_temp       = coord_encontrado
                            st.session_state.email_coord_temp = email_coord
                            try:
                                enviar_email_otp(email_coord, codigo_coord)
                                st.success("✅ Código enviado! Verifique seu e-mail.")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Erro ao enviar e-mail: {e}")
                        else:
                            st.error("❌ E-mail não encontrado.")

        # ---- ABA ADMIN ----
        with aba_admin:
            with st.form("form_login_admin"):
                usuario     = st.text_input("USUÁRIO", placeholder="admin")
                senha_admin = st.text_input("SENHA", type="password", placeholder="••••••")
                botao_login = st.form_submit_button("Entrar →", use_container_width=True)

            if botao_login:
                if usuario in USUARIOS_MASTER and USUARIOS_MASTER[usuario] == senha_admin:
                    st.session_state.logado        = True
                    st.session_state.usuario_atual = usuario
                    st.session_state.tipo_usuario  = "MASTER"
                    st.session_state.erro_login    = ""
                    st.rerun()
                else:
                    st.session_state.erro_login = "❌ Usuário ou senha inválidos."

            if st.session_state.get("erro_login"):
                st.error(st.session_state.erro_login)

    # Rodapé
    st.markdown("""
    <div style="text-align:center; font-size:11px; color:#9ca3af; margin-top:16px;">
        Acesso exclusivo para representantes comerciais ADERE
    </div>
    """, unsafe_allow_html=True)

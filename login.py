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
    """Envia o código OTP por e-mail via Gmail SMTP."""
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


def _css_login():
    st.markdown("""
    <style>
    /* Esconde elementos padrão Streamlit */
    #MainMenu, header, footer,
    [data-testid="stToolbar"],
    [data-testid="stDecoration"],
    [data-testid="stStatusWidget"],
    [data-testid="stFloatingButton"],
    .stDeployButton { display: none !important; visibility: hidden !important; }

    /* Fundo cinza claro */
    .stApp { background-color: #f1f3f6; }
    .block-container { padding-top: 2rem !important; }

    /* Card central */
    .login-card {
        background: white;
        border-radius: 18px;
        padding: 40px 44px 36px 44px;
        max-width: 480px;
        margin: 0 auto;
        box-shadow: 0 4px 24px rgba(0,0,0,0.10);
    }

    /* Ícone topo */
    .login-icon {
        background: #fce8e8;
        border-radius: 16px;
        width: 62px; height: 62px;
        display: flex; align-items: center; justify-content: center;
        font-size: 28px;
        margin: 0 auto 18px auto;
    }

    /* Títulos */
    .login-title {
        font-size: 24px; font-weight: 800;
        color: #111827; text-align: center;
        margin-bottom: 6px;
    }
    .login-sub {
        font-size: 14px; color: #6b7280;
        text-align: center; margin-bottom: 28px;
        line-height: 1.5;
    }

    /* Label dos inputs */
    .login-label {
        font-size: 11px; font-weight: 700;
        color: #374151; letter-spacing: 0.07em;
        text-transform: uppercase; margin-bottom: 6px;
    }

    /* Inputs */
    .stTextInput input {
        border-radius: 10px !important;
        border: 1.5px solid #e5e7eb !important;
        padding: 11px 14px 11px 40px !important;
        font-size: 14px !important;
        background: #f9fafb !important;
        color: #111827 !important;
    }
    .stTextInput input:focus {
        border-color: #c00000 !important;
        box-shadow: 0 0 0 3px rgba(192,0,0,0.08) !important;
    }

    /* Botão principal */
    div[data-testid="stButton"] > button {
        background-color: #c00000 !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
        font-size: 15px !important;
        padding: 12px 0 !important;
        width: 100% !important;
        margin-top: 8px !important;
        letter-spacing: 0.01em;
    }
    div[data-testid="stButton"] > button:hover {
        background-color: #a00000 !important;
    }

    /* Rodapé */
    .login-footer {
        text-align: center; font-size: 12px;
        color: #9ca3af; margin-top: 28px;
    }

    /* Abas tipo segmento */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0; background: #f3f4f6;
        border-radius: 10px; padding: 4px;
        margin-bottom: 20px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px; font-weight: 600;
        font-size: 13px; color: #6b7280;
        padding: 7px 18px; border: none;
        background: transparent;
    }
    .stTabs [aria-selected="true"] {
        background: white !important;
        color: #c00000 !important;
        box-shadow: 0 1px 4px rgba(0,0,0,0.10);
    }
    .stTabs [data-baseweb="tab-border"] { display: none; }
    </style>
    """, unsafe_allow_html=True)


def mostrar_login():
    _css_login()

    # Inicializa estados OTP
    for k in ["codigo_otp", "rc_temp", "email_temp",
              "codigo_otp_coord", "coord_temp", "email_coord_temp",
              "erro_login"]:
        if k not in st.session_state:
            st.session_state[k] = "" if k != "codigo_otp" and k != "codigo_otp_coord" else None

    # ── Card visual ──────────────────────────────────────────────
    st.markdown("<div class='login-card'>", unsafe_allow_html=True)
    st.markdown("<div class='login-icon'>✉️</div>", unsafe_allow_html=True)
    st.markdown("<div class='login-title'>Acesse o Portal</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='login-sub'>Informe seu e-mail cadastrado. Vamos enviar um código "
        "de acesso temporário.</div>",
        unsafe_allow_html=True
    )

    # ── Abas: RC | Coordenador | Admin ──────────────────────────
    aba_rc, aba_coord, aba_admin = st.tabs(["🧑‍💼 RC", "📋 Coordenador", "🔑 Admin"])

    # ============================================================
    # ABA RC
    # ============================================================
    with aba_rc:

        # Se OTP RC já foi enviado → mostrar campo de código
        if st.session_state.codigo_otp:
            st.markdown("<div class='login-label'>CÓDIGO RECEBIDO NO E-MAIL</div>", unsafe_allow_html=True)
            codigo_digitado = st.text_input(
                "Código", max_chars=6,
                placeholder="000000",
                key="otp_rc_input",
                label_visibility="collapsed"
            )
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Validar Código", key="btn_validar_rc", use_container_width=True):
                    if codigo_digitado == str(st.session_state.codigo_otp):
                        st.session_state.logado          = True
                        st.session_state.tipo_usuario    = "RC"
                        st.session_state.usuario_atual   = st.session_state.email_temp
                        st.session_state.rc_usuario      = st.session_state.rc_temp
                        st.session_state.codigo_otp      = None
                        st.rerun()
                    else:
                        st.error("❌ Código inválido. Tente novamente.")
            with col2:
                if st.button("↩ Voltar", key="btn_voltar_rc", use_container_width=True):
                    st.session_state.codigo_otp = None
                    st.rerun()

        else:
            st.markdown("<div class='login-label'>E-MAIL</div>", unsafe_allow_html=True)
            email_rc = st.text_input(
                "E-mail RC", placeholder="seu@email.com",
                key="input_email_rc", label_visibility="collapsed"
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
                        st.session_state.codigo_otp  = codigo
                        st.session_state.rc_temp     = rc_encontrado
                        st.session_state.email_temp  = email_rc
                        try:
                            enviar_email_otp(email_rc, codigo)
                            st.success("✅ Código enviado! Verifique seu e-mail.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro ao enviar e-mail: {e}")
                    else:
                        st.error("❌ E-mail não encontrado.")

    # ============================================================
    # ABA COORDENADOR
    # ============================================================
    with aba_coord:

        if st.session_state.codigo_otp_coord:
            st.markdown("<div class='login-label'>CÓDIGO RECEBIDO NO E-MAIL</div>", unsafe_allow_html=True)
            codigo_coord_digitado = st.text_input(
                "Código coord", max_chars=6,
                placeholder="000000",
                key="otp_coord_input",
                label_visibility="collapsed"
            )
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Validar Código", key="btn_validar_coord", use_container_width=True):
                    if codigo_coord_digitado == str(st.session_state.codigo_otp_coord):
                        st.session_state.logado              = True
                        st.session_state.tipo_usuario        = "COORDENADOR"
                        st.session_state.usuario_atual       = st.session_state.email_coord_temp
                        st.session_state.coordenador_usuario = st.session_state.coord_temp
                        st.session_state.codigo_otp_coord    = None
                        st.rerun()
                    else:
                        st.error("❌ Código inválido. Tente novamente.")
            with col2:
                if st.button("↩ Voltar", key="btn_voltar_coord", use_container_width=True):
                    st.session_state.codigo_otp_coord = None
                    st.rerun()

        else:
            st.markdown("<div class='login-label'>E-MAIL DO COORDENADOR</div>", unsafe_allow_html=True)
            email_coord = st.text_input(
                "E-mail Coordenador", placeholder="coordenador@email.com",
                key="input_email_coord", label_visibility="collapsed"
            )
            if st.button("Enviar Código →", key="btn_enviar_coord", use_container_width=True):
                if not email_coord.strip():
                    st.warning("Informe o e-mail do coordenador.")
                else:
                    df_coord = pd.read_excel("E-mailsCoordenador.xlsx")
                    coord_encontrado = None
                    for _, linha in df_coord.iterrows():
                        if email_coord.strip().lower() == str(linha.get("E-mail", "")).strip().lower():
                            coord_encontrado = linha["Coordenador"]
                            break

                    if coord_encontrado:
                        codigo_coord = str(random.randint(100000, 999999))
                        st.session_state.codigo_otp_coord    = codigo_coord
                        st.session_state.coord_temp          = coord_encontrado
                        st.session_state.email_coord_temp    = email_coord
                        try:
                            enviar_email_otp(email_coord, codigo_coord)
                            st.success("✅ Código enviado! Verifique seu e-mail.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro ao enviar e-mail: {e}")
                    else:
                        st.error("❌ E-mail do coordenador não encontrado.")

    # ============================================================
    # ABA ADMIN
    # ============================================================
    with aba_admin:
        with st.form("form_login_admin"):
            st.markdown("<div class='login-label'>USUÁRIO</div>", unsafe_allow_html=True)
            usuario = st.text_input("Usuário", placeholder="admin", label_visibility="collapsed")
            st.markdown("<div class='login-label'>SENHA</div>", unsafe_allow_html=True)
            senha_admin = st.text_input("Senha", type="password", placeholder="••••••", label_visibility="collapsed")
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

    st.markdown("</div>", unsafe_allow_html=True)  # fecha .login-card
    st.markdown(
        "<div class='login-footer'>Acesso exclusivo para representantes comerciais ADERE</div>",
        unsafe_allow_html=True
    )

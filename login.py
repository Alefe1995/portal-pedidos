import streamlit as st

# ====================================
# CONFIGURAÇÃO DA PÁGINA
# ====================================
st.set_page_config(
    page_title="Portal de Pedidos",
    page_icon="🛒",
    layout="centered"
)

# ====================================
# CREDENCIAIS
# ====================================
USUARIOS = {
    "admin": "1234567",
    "usuario": "senha123"
}

# ====================================
# INICIALIZA SESSION STATE
# ====================================
if "logado" not in st.session_state:
    st.session_state.logado = False
if "usuario_atual" not in st.session_state:
    st.session_state.usuario_atual = ""
if "erro_login" not in st.session_state:
    st.session_state.erro_login = ""

# ====================================
# TELA DE LOGIN
# ====================================
def tela_login():
    st.title("🔐 Portal de Pedidos")
    st.markdown("---")

    with st.form("form_login"):
        usuario = st.text_input("Usuário")
        senha = st.text_input("Senha", type="password")
        botao_login = st.form_submit_button("Entrar", use_container_width=True)

    # ← FORA do with st.form, mas ainda captura os valores
    if botao_login:
        if usuario in USUARIOS and USUARIOS[usuario] == senha:
            st.session_state.logado = True
            st.session_state.usuario_atual = usuario
            st.session_state.erro_login = ""
            st.rerun()  # ← Agora funciona corretamente fora do form
        else:
            st.session_state.erro_login = "❌ Usuário ou senha inválidos."

    if st.session_state.erro_login:
        st.error(st.session_state.erro_login)

# ====================================
# ÁREA LOGADA
# ====================================
def area_logada():
    st.title("✅ Área Administrativa")
    st.write(f"Bem-vindo, **{st.session_state.usuario_atual}**!")
    st.markdown("---")

    st.info("Portal carregado com sucesso.")

    if st.button("🚪 Sair", use_container_width=True):
        st.session_state.logado = False
        st.session_state.usuario_atual = ""
        st.rerun()

# ====================================
# ROTEAMENTO PRINCIPAL
# ====================================
if st.session_state.logado:
    area_logada()
else:
    tela_login()

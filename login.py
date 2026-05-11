import streamlit as st

# ====================================
# CONFIGURAÇÃO DA PÁGINA
# ====================================
st.set_page_config(
    page_title="Portal de Pedidos",
    layout="centered"
)

# ====================================
# CONTROLE DE LOGIN
# ====================================
if "logado" not in st.session_state:
    st.session_state.logado = False

# ====================================
# TELA LOGIN
# ====================================
if not st.session_state.logado:

    st.title("🔐 Portal de Pedidos")

    st.markdown("---")

    with st.form("form_login"):

        usuario = st.text_input("Usuário")

        senha = st.text_input(
            "Senha",
            type="password"
        )

        botao_login = st.form_submit_button("Entrar")

        if botao_login:

            if usuario == "admin" and senha == "123456":

                st.session_state.logado = True

                st.success("Login realizado com sucesso!")

            else:

                st.error("Usuário ou senha inválidos.")

# ====================================
# ÁREA LOGADA
# ====================================
else:

    st.title("✅ Área Administrativa")

    st.write("Você está logado no portal.")

    if st.button("Sair"):

        st.session_state.logado = False

        st.rerun()

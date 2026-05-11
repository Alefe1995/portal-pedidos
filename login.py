import streamlit as st

# =========================
# CONFIGURAÇÃO DA PÁGINA
# =========================
st.set_page_config(
    page_title="Login Portal",
    layout="centered"
)

# =========================
# CONTROLE DE LOGIN
# =========================
if "logado" not in st.session_state:
    st.session_state["logado"] = False

# =========================
# LOGIN
# =========================
if st.session_state["logado"] == False:

    st.title("🔐 Portal de Pedidos")

    st.markdown("---")

    st.subheader("Login Administrador")

    usuario = st.text_input("Usuário")

    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):

        if usuario == "admin" and senha == "123456":

            st.session_state["logado"] = True

            st.rerun()

        else:

            st.error("Usuário ou senha inválidos.")

# =========================
# ÁREA LOGADA
# =========================
else:

    st.success("Login realizado com sucesso!")

    st.write("✅ Área administrativa liberada.")

    if st.button("Sair"):

        st.session_state["logado"] = False

        st.rerun()

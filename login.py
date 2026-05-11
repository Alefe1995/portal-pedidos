import streamlit as st

# =========================
# CONFIGURAÇÃO DA PÁGINA
# =========================
st.set_page_config(
    page_title="Login Portal",
    layout="centered"
)

# =========================
# TÍTULO
# =========================
st.title("🔐 Portal de Pedidos")

st.markdown("---")

# =========================
# LOGIN MASTER
# =========================
st.subheader("Login Administrador")

usuario = st.text_input("Usuário")
senha = st.text_input("Senha", type="password")

if st.button("Entrar"):

    if usuario == "admin" and senha == "123456":

        st.success("Login realizado com sucesso!")

    else:

        st.error("Usuário ou senha inválidos.")

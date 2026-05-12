# app.py
import streamlit as st
from login import mostrar_login
from portal_backup import mostrar_portal

st.set_page_config(
    page_title="Portal de Pedidos",
    page_icon="📊",
    layout="wide"
)

# ── Inicializa session_state ─────────────────────────────────────
defaults = {
    "logado": False,
    "usuario_atual": "",
    "tipo_usuario": "",
    "erro_login": "",
    "rc_usuario": None,
    "coordenador_usuario": None,
    "codigo_otp": None,
    "codigo_otp_coord": None,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── Roteamento ───────────────────────────────────────────────────
if st.session_state.logado:

    tipo = st.session_state.tipo_usuario

    if tipo == "RC":
        # Passa o código RC para o portal filtrar automaticamente
        mostrar_portal(
            filtro_tipo="RC",
            filtro_valor=st.session_state.rc_usuario
        )

    elif tipo == "COORDENADOR":
        # Passa o nome do coordenador para o portal filtrar automaticamente
        mostrar_portal(
            filtro_tipo="COORDENADOR",
            filtro_valor=st.session_state.coordenador_usuario
        )

    else:
        # MASTER: abre o portal normalmente sem filtro
        mostrar_portal(
            filtro_tipo="MASTER",
            filtro_valor=None
        )

    # Botão de sair na sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown(
        f"👤 **{st.session_state.usuario_atual}**  \n"
        f"*{st.session_state.tipo_usuario}*"
    )
    if st.sidebar.button("🚪 Sair"):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()

else:
    mostrar_login()

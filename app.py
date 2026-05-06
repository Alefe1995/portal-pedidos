import pandas as pd
import streamlit as st

st.title("📦 Portal de Pedidos")

# Carregar arquivos
pedidos = pd.read_excel("Pedidos.xlsx")
itens = pd.read_excel("Itens.xlsx")

# Entrada do RC
rc_input = st.text_input("Digite seu código RC:")

if rc_input:
    # Filtrar pedidos do RC
    pedidos_rc = pedidos[pedidos['RC'].astype(str) == rc_input]

    if not pedidos_rc.empty:
        st.subheader("📋 Seus Pedidos")
        st.dataframe(pedidos_rc)
    else:
        st.error("Nenhum pedido encontrado para este RC.")

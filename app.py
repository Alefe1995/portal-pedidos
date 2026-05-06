import pandas as pd
import streamlit as st

st.image("download.png", width=200)
st.title("Portal de Pedidos")

# Carregar arquivos
pedidos = pd.read_excel("Pedidos.xlsx")
itens = pd.read_excel("Itens.xlsx")

# Entrada do RC
rc_input = st.text_input("Digite seu código RC:")

if rc_input:
    pedidos_rc = pedidos[pedidos['RC'].astype(str) == rc_input]

    if not pedidos_rc.empty:
        st.subheader("📋 Seus Pedidos")
        st.dataframe(pedidos_rc)

        # Selecionar pedido
        lista_pedidos = pedidos_rc['Pedido'].astype(str).unique()
        pedido_selecionado = st.selectbox(
            "Selecione um pedido para ver os itens:",
            lista_pedidos
        )

        # Mostrar itens
        if pedido_selecionado:
            st.subheader("📦 Itens do Pedido")
            itens_pedido = itens[itens['Pedido'].astype(str) == pedido_selecionado]
            st.dataframe(itens_pedido)

    else:
        st.error("Nenhum pedido encontrado para este RC.")

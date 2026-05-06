import pandas as pd
import streamlit as st

st.title("📦 Portal de Pedidos")

# Carregar arquivos
pedidos = pd.read_excel("Pedidos.xlsx")
itens = pd.read_excel("Itens.xlsx")

# Campo de busca
pedido_input = st.text_input("Digite o número do pedido:")

if pedido_input:
    pedido = pedidos[pedidos['Pedido'].astype(str) == pedido_input]

    if not pedido.empty:
        st.subheader("📋 Dados do Pedido")
        st.dataframe(pedido)

        st.subheader("📦 Itens do Pedido")
        itens_pedido = itens[itens['Pedido'].astype(str) == pedido_input]
        st.dataframe(itens_pedido)
    else:
        st.error("Pedido não encontrado.")

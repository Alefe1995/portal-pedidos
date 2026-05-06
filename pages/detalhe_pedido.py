import pandas as pd
import streamlit as st

st.title("📦 Detalhe do Pedido")

# Carregar arquivos
itens = pd.read_excel("Itens.xlsx")

# Recuperar pedido selecionado
pedido = st.query_params.get("pedido")

if pedido:
    st.subheader(f"Itens do Pedido {pedido}")
    itens_pedido = itens[itens['Pedido'].astype(str) == pedido]
    st.dataframe(itens_pedido)
else:
    st.warning("Nenhum pedido selecionado.")

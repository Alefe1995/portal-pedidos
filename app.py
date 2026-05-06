import pandas as pd
import streamlit as st

st.title("📦 Portal de Pedidos")

# Carregar arquivos
pedidos = pd.read_excel("Pedidos.xlsx")

# Entrada do RC
rc_input = st.text_input("Digite seu código RC:")

if rc_input:
    pedidos_rc = pedidos[pedidos['RC'].astype(str) == rc_input]

    if not pedidos_rc.empty:
        st.subheader("📋 Seus Pedidos")

        for _, row in pedidos_rc.iterrows():
            st.write(f"Pedido: {row['Pedido']} | Cliente: {row['Cliente']} | Status: {row['Status']}")

            # Botão para acessar detalhes
            if st.button(f"Ver itens do pedido {row['Pedido']}"):
                st.query_params["pedido"] = str(row['Pedido'])
                st.switch_page("pages/detalhe_pedido.py")
    else:
        st.error("Nenhum pedido encontrado para este RC.")

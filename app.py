import pandas as pd
import streamlit as st

# CONFIGURAÇÃO DA PÁGINA
st.set_page_config(layout="wide")

# LOGO + TÍTULO
st.image("download.png", width=80)
st.title("Portal de Pedidos")

# =========================
# FUNÇÃO FORMATAÇÃO MOEDA
# =========================
def formatar_moeda(valor):
    try:
        if pd.isna(valor):
            return ""

        if isinstance(valor, (int, float)):
            valor_float = float(valor)
        else:
            valor_str = str(valor)
            valor_str = valor_str.replace("R$", "").strip()

            if "," in valor_str:
                valor_str = valor_str.replace(".", "").replace(",", ".")

            valor_float = float(valor_str)

        return f"R$ {valor_float:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    except:
        return valor

# =========================
# FUNÇÃO FORMATAÇÃO DATA
# =========================
def formatar_data(valor):
    try:
        data = pd.to_datetime(valor, errors="coerce")
        if pd.notna(data):
            return data.strftime("%d/%m/%Y")
        else:
            return valor
    except:
        return valor

# =========================
# CARREGAR DADOS
# =========================
pedidos = pd.read_excel("Pedidos.xlsx")
itens = pd.read_excel("Itens.xlsx")

# =========================
# ENTRADA RC
# =========================
rc_input = st.text_input("Digite seu código RC:")

if rc_input:
    pedidos_rc = pedidos[pedidos['RC'].astype(str) == rc_input]

    if not pedidos_rc.empty:

        pedidos_view = pedidos_rc.copy()

        # Remover RC
        if "RC" in pedidos_view.columns:
            pedidos_view = pedidos_view.drop(columns=["RC"])

        # Formatar moedas (Pedidos)
        for col in ["Valor (R$)", "Soma de Valor", "Soma de Valores"]:
            if col in pedidos_view.columns:
                pedidos_view[col] = pedidos_view[col].apply(formatar_moeda)

        # Formatar data
        if "Previsão" in pedidos_view.columns:
            pedidos_view["Previsão"] = pedidos_view["Previsão"].apply(formatar_data)

        st.subheader("📋 Seus Pedidos")

        st.dataframe(
            pedidos_view,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Pedido": st.column_config.TextColumn("Pedido", width="small"),
                "Cliente": st.column_config.TextColumn("Cliente", width="large"),
                "UF": st.column_config.TextColumn("UF", width=50),  # 👈 AJUSTADO
                "Status": st.column_config.TextColumn("Status", width="medium"),
                "Motivo": st.column_config.TextColumn("Motivo", width="medium"),
                "Previsão": st.column_config.TextColumn("Previsão", width="medium"),
                "Valor (R$)": st.column_config.TextColumn("Valor (R$)", width="medium"),
                "Soma de Valor": st.column_config.TextColumn("Valor Total", width="medium"),
                "Soma de Valores": st.column_config.TextColumn("Valor Total", width="medium"),
            }
        )

        # =========================
        # SELEÇÃO DE PEDIDO
        # =========================
        lista_pedidos = pedidos_rc['Pedido'].astype(str).unique()

        pedido_selecionado = st.selectbox(
            "Selecione um pedido para ver os itens:",
            lista_pedidos
        )

        # =========================
        # ITENS
        # =========================
        if pedido_selecionado:
            itens_pedido = itens[itens['Pedido'].astype(str) == pedido_selecionado].copy()

            # Remover RC
            if "RC" in itens_pedido.columns:
                itens_pedido = itens_pedido.drop(columns=["RC"])

            # Formatar moedas (Itens)
            for col in ["Soma de Valor", "Soma de Valores"]:
                if col in itens_pedido.columns:
                    itens_pedido[col] = itens_pedido[col].apply(formatar_moeda)

            # Formatar data
            if "Previsão Final" in itens_pedido.columns:
                itens_pedido["Previsão Final"] = itens_pedido["Previsão Final"].apply(formatar_data)

            st.subheader("📦 Itens do Pedido")

            st.dataframe(
                itens_pedido,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Pedido": st.column_config.TextColumn("Pedido", width="small"),
                    "Produto": st.column_config.TextColumn("Produto", width="large"),
                    "Status Reserva": st.column_config.TextColumn("Status Reserva", width="medium"),
                    "Pedido2": st.column_config.TextColumn("Qtde", width=60),  # 👈 AJUSTADO
                    "Soma de Valor": st.column_config.TextColumn("Valor (R$)", width="medium"),
                    "Soma de Valores": st.column_config.TextColumn("Valor (R$)", width="medium"),
                    "Previsão Final": st.column_config.TextColumn("Previsão Final", width="medium"),
                }
            )

    else:
        st.error("Nenhum pedido encontrado para este RC.")

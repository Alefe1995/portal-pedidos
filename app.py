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
        return valor
    except:
        return valor


# =========================
# FUNÇÃO LIMPAR TEXTO AÇÃO (CORRIGIDA)
# =========================
def limpar_texto(texto):
    if pd.isna(texto):
        return ""

    texto = str(texto)

    # Corrigir quebras vindas do Excel/SharePoint
    texto = (
        texto.replace("_x000D_", "\n")
             .replace("\r\n", "\n")
             .replace("\r", "\n")
    )

    # Remover múltiplas quebras exageradas
    while "\n\n\n" in texto:
        texto = texto.replace("\n\n\n", "\n\n")

    return texto.strip()


# =========================
# CARREGAR DADOS
# =========================
pedidos = pd.read_excel("Pedidos.xlsx")
itens = pd.read_excel("Itens.xlsx")
acoes = pd.read_excel("Ação.xlsx")


# =========================
# ENTRADA RC
# =========================
rc_input = st.text_input("🔎 Digite seu código RC:")

if rc_input:
    pedidos_rc = pedidos[pedidos['RC'].astype(str) == rc_input]

    if not pedidos_rc.empty:

        pedidos_view = pedidos_rc.copy()

        if "RC" in pedidos_view.columns:
            pedidos_view = pedidos_view.drop(columns=["RC"])

        for col in ["Valor (R$)", "Soma de Valor", "Soma de Valores"]:
            if col in pedidos_view.columns:
                pedidos_view[col] = pedidos_view[col].apply(formatar_moeda)

        if "Previsão" in pedidos_view.columns:
            pedidos_view["Previsão"] = pedidos_view["Previsão"].apply(formatar_data)

        st.subheader("🧾 Seus Pedidos")

        st.dataframe(
            pedidos_view,
            use_container_width=True,
            hide_index=True
        )

        lista_pedidos = pedidos_rc['Pedido'].astype(str).unique()

        pedido_selecionado = st.selectbox(
            "📌 Selecione um pedido para ver os itens:",
            lista_pedidos
        )

        if pedido_selecionado:
            itens_pedido = itens[itens['Pedido'].astype(str) == pedido_selecionado].copy()

            if "RC" in itens_pedido.columns:
                itens_pedido = itens_pedido.drop(columns=["RC"])

            for col in ["Soma de Valor", "Soma de Valores"]:
                if col in itens_pedido.columns:
                    itens_pedido[col] = itens_pedido[col].apply(formatar_moeda)

            if "Previsão Final" in itens_pedido.columns:
                itens_pedido["Previsão Final"] = itens_pedido["Previsão Final"].apply(formatar_data)

            st.subheader("📦 Itens do Pedido")

            st.dataframe(
                itens_pedido,
                use_container_width=True,
                hide_index=True
            )

            # =========================
            # AÇÃO RECOMENDADA (CORRIGIDA)
            # =========================
            acoes_pedido = acoes[
                (acoes['Pedido'].astype(str) == pedido_selecionado) &
                (acoes['RC'].astype(str) == rc_input)
            ]

            if not acoes_pedido.empty:

                texto = limpar_texto(acoes_pedido.iloc[0]["Texto"])

                st.subheader("📌 Ação Recomendada")

                st.markdown(
                    f"""
                    <div style="
                        background-color:#f0f8ff;
                        padding:15px;
                        border-radius:10px;
                        border:1px solid #d0e7ff;
                        white-space:pre-wrap;
                        font-family:inherit;
                    ">
                    {texto}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            else:
                st.info("Nenhuma ação cadastrada para este pedido.")

    else:
        st.error("Nenhum pedido encontrado para este RC.")

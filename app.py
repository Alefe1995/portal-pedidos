import pandas as pd
import streamlit as st

# =========================
# CONFIGURAÇÃO
# =========================
st.set_page_config(layout="wide")

# =========================
# 🎨 FAIXA SUPERIOR (BRANDING)
# =========================
st.markdown(
    """
    <div style="
        background-color:#c00000;
        height:45px;
        width:100%;
        margin-bottom:10px;
        border-radius:5px;
    "></div>
    """,
    unsafe_allow_html=True
)

st.title("Portal de Pedidos")


# =========================
# CONVERSÕES
# =========================
def para_float(valor):
    try:
        if pd.isna(valor):
            return 0

        if isinstance(valor, (int, float)):
            return float(valor)

        valor = str(valor).replace("R$", "").strip()
        valor = valor.replace(".", "").replace(",", ".")

        return float(valor)
    except:
        return 0


def formatar_moeda(valor):
    try:
        if pd.isna(valor):
            return ""

        if isinstance(valor, (int, float)):
            valor_float = float(valor)
        else:
            valor_str = str(valor).replace("R$", "").strip()

            if "," in valor_str:
                valor_str = valor_str.replace(".", "").replace(",", ".")

            valor_float = float(valor_str)

        return f"R$ {valor_float:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return valor


def formatar_data(valor):
    try:
        data = pd.to_datetime(valor, errors="coerce")
        if pd.notna(data):
            return data.strftime("%d/%m/%Y")
        return valor
    except:
        return valor


def limpar_texto(texto):
    if pd.isna(texto):
        return ""

    texto = str(texto)
    texto = texto.replace("_x000D_", "\n").replace("\r\n", "\n").replace("\r", "\n")

    linhas = [l.strip() for l in texto.split("\n") if l.strip() != ""]
    return "\n".join(linhas)


# =========================
# DADOS
# =========================
pedidos = pd.read_excel("Pedidos.xlsx")
itens = pd.read_excel("Itens.xlsx")
acoes = pd.read_excel("Ação.xlsx")


# =========================
# RC
# =========================
rc_input = st.text_input("🔎 Digite seu código RC:")

if rc_input:

    base = pedidos[pedidos["RC"].astype(str) == rc_input].copy()

    if not base.empty:

        if "RC" in base.columns:
            base = base.drop(columns=["RC"])

        base = base.rename(columns={
            "Pedido2": "Qtde",
            "Soma de Valor": "Valor (R$)"
        })

        # =========================
        # FORMATAÇÃO
        # =========================
        for col in ["Valor (R$)", "Soma de Valores"]:
            if col in base.columns:
                base[col] = base[col].apply(formatar_moeda)

        if "Previsão" in base.columns:
            base["Previsão"] = base["Previsão"].apply(formatar_data)

        # =========================
        # SIDEBAR (AGORA COM IMAGEM NO TOPO)
        # =========================
        st.sidebar.image("download.png", width=90)

        st.sidebar.header("🔎 Filtros")

        # ---- STATUS ----
        status_list = sorted(base["Status"].dropna().unique()) if "Status" in base.columns else []
        status = st.sidebar.selectbox("Status", ["Todos"] + status_list)

        df1 = base.copy()
        if status != "Todos":
            df1 = df1[df1["Status"] == status]

        # ---- MOTIVO ----
        motivo_list = sorted(df1["Motivo"].dropna().unique()) if "Motivo" in df1.columns else []
        motivo = st.sidebar.selectbox("Motivo", ["Todos"] + motivo_list)

        df2 = df1.copy()
        if motivo != "Todos":
            df2 = df2[df2["Motivo"] == motivo]

        # ---- CLIENTE ----
        cliente = st.sidebar.text_input("Cliente (buscar)")

        df3 = df2.copy()
        if cliente:
            df3 = df3[df3["Cliente"].str.contains(cliente, case=False, na=False)]

        pedidos_view = df3

        # =========================
        # VALOR TOTAL
        # =========================
        pedidos_view["Valor_num"] = pedidos_view["Valor (R$)"].apply(para_float)

        valor_total = pedidos_view["Valor_num"].sum()

        st.sidebar.markdown("---")
        st.sidebar.subheader("💰 Valor Total")

        st.sidebar.markdown(
            f"""
            <div style="
                background-color:#e8f4ff;
                padding:15px;
                border-radius:10px;
                text-align:center;
                font-size:20px;
                font-weight:bold;
                border:1px solid #b3daff;
            ">
                R$ {valor_total:,.2f}
            </div>
            """,
            unsafe_allow_html=True
        )

        # =========================
        # TABELA
        # =========================
        st.subheader("🧾 Seus Pedidos")

        st.dataframe(
            pedidos_view.drop(columns=["Valor_num"]),
            use_container_width=True,
            hide_index=True
        )

        # =========================
        # PEDIDOS
        # =========================
        lista_pedidos = pedidos_view["Pedido"].astype(str).unique()

        pedido_selecionado = st.selectbox("📌 Selecione um pedido:", lista_pedidos)

        if pedido_selecionado:

            itens_pedido = itens[itens["Pedido"].astype(str) == pedido_selecionado].copy()

            if "RC" in itens_pedido.columns:
                itens_pedido = itens_pedido.drop(columns=["RC"])

            itens_pedido = itens_pedido.rename(columns={
                "Pedido2": "Qtde",
                "Soma de Valor": "Valor (R$)"
            })

            for col in ["Valor (R$)", "Soma de Valores"]:
                if col in itens_pedido.columns:
                    itens_pedido[col] = itens_pedido[col].apply(formatar_moeda)

            if "Previsão Final" in itens_pedido.columns:
                itens_pedido["Previsão Final"] = itens_pedido["Previsão Final"].apply(formatar_data)

            st.subheader("📦 Itens do Pedido")

            st.dataframe(itens_pedido, use_container_width=True, hide_index=True)

            # =========================
            # AÇÃO
            # =========================
            acoes_pedido = acoes[
                (acoes["Pedido"].astype(str) == pedido_selecionado) &
                (acoes["RC"].astype(str) == rc_input)
            ]

            if not acoes_pedido.empty:

                texto = limpar_texto(acoes_pedido.iloc[0]["Texto"])

                st.subheader("🚨 Ação Recomendada")

                st.markdown(
                    f"""
                    <div style="
                        background-color:#e8f4ff;
                        border:1px solid #b3daff;
                        padding:16px;
                        border-radius:10px;
                        white-space:pre-line;
                        line-height:1.5;
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

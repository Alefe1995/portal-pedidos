import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

# =========================
# CONFIGURAÇÃO
# =========================
st.set_page_config(
    page_title="Portal de Pedidos",
    layout="wide"
)

# =========================
# CSS GLOBAL
# =========================
st.markdown("""
<style>

/* FUNDO */
.stApp {
    background-color: #f5f7fb;
}

/* HEADER */
.top-header {
    background-color:#c00000;
    padding:16px 24px;
    border-radius:12px;
    margin-bottom:25px;
    color:white;
    font-size:30px;
    font-weight:700;
    box-shadow:0 3px 10px rgba(0,0,0,0.10);
}

/* SIDEBAR */
section[data-testid="stSidebar"] {
    background:#ffffff;
    border-right:1px solid #e5e7eb;
}

/* TITULOS */
.section-title {
    font-size:22px;
    font-weight:700;
    color:#111827;
    margin-bottom:15px;
    margin-top:10px;
}

/* INPUT */
.stTextInput input {
    border-radius:10px !important;
    border:1px solid #cbd5e1 !important;
    padding:10px !important;
    background:white !important;
}

/* SELECT */
div[data-baseweb="select"] > div {
    border-radius:10px !important;
    border:1px solid #cbd5e1 !important;
    background:white !important;
    min-height:42px;
}

/* ALERTAS */
.stAlert {
    border-radius:12px;
}

</style>
""", unsafe_allow_html=True)

# =========================
# HEADER
# =========================
st.markdown("""
<div class='top-header'>
    Portal de Pedidos
</div>
""", unsafe_allow_html=True)

# =========================
# FUNÇÕES
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

    texto = texto.replace("_x000D_", "\n")
    texto = texto.replace("\r\n", "\n")
    texto = texto.replace("\r", "\n")

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

# =========================
# PROCESSAMENTO
# =========================
if rc_input:

    base = pedidos[pedidos["RC"].astype(str) == rc_input].copy()

    if not base.empty:

        # REMOVE RC
        if "RC" in base.columns:
            base = base.drop(columns=["RC"])

        # RENOMEIA
        base = base.rename(columns={
            "Pedido2": "Qtde",
            "Soma de Valor": "Valor (R$)"
        })

        # =========================
        # FORMATAÇÕES
        # =========================
        for col in ["Valor (R$)", "Soma de Valores"]:

            if col in base.columns:
                base[col] = base[col].apply(formatar_moeda)

        if "Previsão" in base.columns:
            base["Previsão"] = base["Previsão"].apply(formatar_data)

        # =========================
        # SIDEBAR
        # =========================
        st.sidebar.image("download.png", width=150)

        st.sidebar.markdown("## 🔎 Filtros")

        # STATUS
        status_list = (
            sorted(base["Status"].dropna().unique())
            if "Status" in base.columns
            else []
        )

        status = st.sidebar.selectbox(
            "Status",
            ["Todos"] + status_list
        )

        df1 = base.copy()

        if status != "Todos":
            df1 = df1[df1["Status"] == status]

        # MOTIVO
        motivo_list = (
            sorted(df1["Motivo"].dropna().unique())
            if "Motivo" in df1.columns
            else []
        )

        motivo = st.sidebar.selectbox(
            "Motivo",
            ["Todos"] + motivo_list
        )

        df2 = df1.copy()

        if motivo != "Todos":
            df2 = df2[df2["Motivo"] == motivo]

        # CLIENTE
        cliente = st.sidebar.text_input("Cliente")

        df3 = df2.copy()

        if cliente:

            df3 = df3[
                df3["Cliente"].str.contains(
                    cliente,
                    case=False,
                    na=False
                )
            ]

        pedidos_view = df3

        # =========================
        # VALOR TOTAL
        # =========================
        pedidos_view["Valor_num"] = pedidos_view["Valor (R$)"].apply(para_float)

        valor_total = pedidos_view["Valor_num"].sum()

        st.sidebar.markdown("---")
        st.sidebar.markdown("### 💰 Valor Total")

        st.sidebar.success(
            formatar_moeda(valor_total)
        )

        # =========================
        # TITULO
        # =========================
        st.markdown(
            "<div class='section-title'>🧾 Seus Pedidos</div>",
            unsafe_allow_html=True
        )

        # =========================
        # HTML TABELA
        # =========================
        html = """
        <html>

        <head>

        <style>

        body{
            font-family:Arial;
            background:white;
            margin:0;
            padding:0;
        }

        .table-box{
            border:1px solid #e5e7eb;
            border-radius:14px;
            overflow:hidden;
        }

        table{
            width:100%;
            border-collapse:collapse;
        }

        thead{
            background:#f8fafc;
        }

        th{
            padding:14px;
            text-align:left;
            font-size:12px;
            text-transform:uppercase;
            color:#6b7280;
            border-bottom:1px solid #e5e7eb;
        }

        td{
            padding:14px;
            border-bottom:1px solid #f1f5f9;
            font-size:14px;
            color:#111827;
        }

        tr:hover{
            background:#f9fafb;
        }

        .pedido{
            color:#dc2626;
            font-weight:700;
        }

        .motivo{
            font-weight:600;
        }

        .valor{
            font-weight:700;
        }

        .liberado{
            background:#dcfce7;
            color:#166534;
            padding:5px 12px;
            border-radius:999px;
            font-size:12px;
            font-weight:600;
        }

        .conferido{
            background:#dbeafe;
            color:#1d4ed8;
            padding:5px 12px;
            border-radius:999px;
            font-size:12px;
            font-weight:600;
        }

        .pendente{
            background:#fef3c7;
            color:#92400e;
            padding:5px 12px;
            border-radius:999px;
            font-size:12px;
            font-weight:600;
        }

        </style>

        </head>

        <body>

        <div class="table-box">

        <table>

        <thead>
        <tr>
            <th>Pedido</th>
            <th>Cliente</th>
            <th>UF</th>
            <th>Status</th>
            <th>Motivo</th>
            <th>Previsão</th>
            <th>Valor (R$)</th>
        </tr>
        </thead>

        <tbody>
        """

        for _, row in pedidos_view.iterrows():

            status = str(row["Status"]).lower()

            if "liberado" in status:
                badge = f"<span class='liberado'>{row['Status']}</span>"

            elif "conferido" in status:
                badge = f"<span class='conferido'>{row['Status']}</span>"

            else:
                badge = f"<span class='pendente'>{row['Status']}</span>"

            html += f"""
            <tr>

                <td class="pedido">
                    {row['Pedido']}
                </td>

                <td>
                    {row['Cliente']}
                </td>

                <td>
                    {row['UF']}
                </td>

                <td>
                    {badge}
                </td>

                <td class="motivo">
                    {row['Motivo']}
                </td>

                <td>
                    {row['Previsão']}
                </td>

                <td class="valor">
                    {row['Valor (R$)']}
                </td>

            </tr>
            """

        html += """
        </tbody>

        </table>

        </div>

        </body>

        </html>
        """

        components.html(
            html,
            height=500,
            scrolling=True
        )

        # =========================
        # SELECT PEDIDO
        # =========================
        pedidos_view["Pedido_Exibicao"] = (
            pedidos_view["Pedido"].astype(str)
            + " - "
            + pedidos_view["Cliente"].astype(str)
        )

        lista_pedidos = pedidos_view["Pedido_Exibicao"].unique()

        pedido_selecionado = st.selectbox(
            "📌 Selecione um pedido:",
            lista_pedidos
        )

        # =========================
        # PEDIDO SELECIONADO
        # =========================
        if pedido_selecionado:

            pedido_numero = pedido_selecionado.split(" - ")[0]

            pedido_info = pedidos_view[
                pedidos_view["Pedido"].astype(str) == pedido_numero
            ].iloc[0]

            st.markdown(f"""
<div style="
background:white;
border:1px solid #dfe3eb;
border-radius:14px;
padding:20px;
margin-top:15px;
margin-bottom:25px;
box-shadow:0 2px 8px rgba(0,0,0,0.05);
">

<div style="
font-size:12px;
color:#6b7280;
font-weight:600;
text-transform:uppercase;
margin-bottom:8px;
">
Pedido Selecionado
</div>

<div style="
font-size:30px;
font-weight:700;
color:#111827;
">
#{pedido_numero}
</div>

<div style="
font-size:15px;
color:#6b7280;
margin-top:6px;
">
{pedido_info['Cliente']}
</div>

</div>
""", unsafe_allow_html=True)

            # =========================
            # ITENS
            # =========================
            itens_pedido = itens[
                itens["Pedido"].astype(str) == pedido_numero
            ].copy()

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

            st.markdown(
                "<div class='section-title'>📦 Itens do Pedido</div>",
                unsafe_allow_html=True
            )

            st.dataframe(
                itens_pedido,
                use_container_width=True,
                hide_index=True
            )

            # =========================
            # AÇÃO
            # =========================
            acoes_pedido = acoes[
                (acoes["Pedido"].astype(str) == pedido_numero)
                &
                (acoes["RC"].astype(str) == rc_input)
            ]

            st.markdown(
                "<div class='section-title'>🚨 Ação Recomendada</div>",
                unsafe_allow_html=True
            )

            if not acoes_pedido.empty:

                texto = limpar_texto(
                    acoes_pedido.iloc[0]["Texto"]
                )

                st.info(texto)

            else:

                st.info(
                    "Nenhuma ação cadastrada para este pedido."
                )

    else:

        st.error(
            "Nenhum pedido encontrado para este RC."
        )

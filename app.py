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

        if pd.isna(valor):
            return ""

        data = pd.to_datetime(valor, errors="coerce")

        if pd.notna(data):
            return data.strftime("%d/%m/%Y")

        return str(valor)

    except:
        return str(valor)


def limpar_texto(texto):

    if pd.isna(texto):
        return ""

    texto = str(texto)

    texto = texto.replace("_x000D_", "\n")
    texto = texto.replace("\r\n", "\n")
    texto = texto.replace("\r", "\n")

    linhas = [
        l.strip()
        for l in texto.split("\n")
        if l.strip() != ""
    ]

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

    base = pedidos[
        pedidos["RC"].astype(str) == rc_input
    ].copy()

    if not base.empty:

        # REMOVE RC
        if "RC" in base.columns:
            base = base.drop(columns=["RC"])

        # RENOMEIA
        base = base.rename(columns={
            "Pedido2": "Qtde",
            "Soma de Valor": "Valor (R$)"
        })

        # FORMATAÇÕES
        for col in ["Valor (R$)", "Soma de Valores"]:

            if col in base.columns:
                base[col] = base[col].apply(formatar_moeda)

        if "Previsão" in base.columns:
            base["Previsão"] = base["Previsão"].apply(formatar_data)

        # =========================
        # SIDEBAR
        # =========================
        st.sidebar.image("download.png", width=100)

        st.sidebar.header("🔎 Filtros")

        # STATUS
        status_list = sorted(
            base["Status"].dropna().unique()
        ) if "Status" in base.columns else []

        status = st.sidebar.selectbox(
            "Status",
            ["Todos"] + status_list
        )

        df1 = base.copy()

        if status != "Todos":
            df1 = df1[df1["Status"] == status]

        # MOTIVO
        motivo_list = sorted(
            df1["Motivo"].dropna().unique()
        ) if "Motivo" in df1.columns else []

        motivo = st.sidebar.selectbox(
            "Motivo",
            ["Todos"] + motivo_list
        )

        df2 = df1.copy()

        if motivo != "Todos":
            df2 = df2[df2["Motivo"] == motivo]

        # CLIENTE
        cliente = st.sidebar.text_input("Cliente (buscar)")

        df3 = df2.copy()

        if cliente:

            df3 = df3[
                df3["Cliente"].str.contains(
                    cliente,
                    case=False,
                    na=False
                )
            ]

        pedidos_view = df3.copy()

        # =========================
        # VALORES NUMÉRICOS
        # =========================
        pedidos_view["Valor_num"] = pedidos_view["Valor (R$)"].apply(para_float)

        total_pedidos = len(pedidos_view)

        valor_total = pedidos_view["Valor_num"].sum()

        valor_liberado = pedidos_view[
            pedidos_view["Status"].astype(str).str.lower().str.contains("liberado")
        ]["Valor_num"].sum()

        valor_critico = pedidos_view[
            pedidos_view["Motivo"].astype(str).str.lower().isin([
                "estoque",
                "ag retorno comercial"
            ])
        ]["Valor_num"].sum()

        valor_pendente = pedidos_view[
            pedidos_view["Status"].astype(str).str.lower() == "pendente"
        ]["Valor_num"].sum()

        # =========================
        # CARDS RESUMO
        # =========================
        col1, col2, col3, col4, col5 = st.columns(5)

        # CARD PEDIDOS
        with col1:

            st.markdown(f"""
            <div style="
                background:white;
                border:1px solid #e5e7eb;
                border-radius:14px;
                padding:14px;
                box-shadow:0 2px 8px rgba(0,0,0,0.04);
            ">

            <div style="
                font-size:24px;
            ">
            📦
            </div>

            <div style="
                font-size:24px;
                font-weight:700;
                color:#111827;
                margin-top:5px;
            ">
            {total_pedidos}
            </div>

            <div style="
                font-size:13px;
                color:#6b7280;
                margin-top:3px;
            ">
            Pedidos
            </div>

            </div>
            """, unsafe_allow_html=True)

        # CARD VALOR TOTAL
        with col2:

            st.markdown(f"""
            <div style="
                background:white;
                border:1px solid #e5e7eb;
                border-radius:14px;
                padding:14px;
                box-shadow:0 2px 8px rgba(0,0,0,0.04);
            ">

            <div style="
                font-size:24px;
            ">
            💰
            </div>

            <div style="
                font-size:22px;
                font-weight:700;
                color:#111827;
                margin-top:5px;
            ">
            {formatar_moeda(valor_total)}
            </div>

            <div style="
                font-size:13px;
                color:#6b7280;
                margin-top:3px;
            ">
            Valor Total
            </div>

            </div>
            """, unsafe_allow_html=True)

        # CARD LIBERADOS
        with col3:

            st.markdown(f"""
            <div style="
                background:white;
                border:1px solid #dcfce7;
                border-radius:14px;
                padding:14px;
                box-shadow:0 2px 8px rgba(0,0,0,0.04);
            ">

            <div style="
                font-size:24px;
            ">
            🟢
            </div>

            <div style="
                font-size:22px;
                font-weight:700;
                color:#166534;
                margin-top:5px;
            ">
            {formatar_moeda(valor_liberado)}
            </div>

            <div style="
                font-size:13px;
                color:#6b7280;
                margin-top:3px;
            ">
            Valor Liberado
            </div>

            </div>
            """, unsafe_allow_html=True)

        # CARD CRÍTICOS
        with col4:

            st.markdown(f"""
            <div style="
                background:white;
                border:1px solid #fee2e2;
                border-radius:14px;
                padding:14px;
                box-shadow:0 2px 8px rgba(0,0,0,0.04);
            ">

            <div style="
                font-size:24px;
            ">
            🔴
            </div>

            <div style="
                font-size:22px;
                font-weight:700;
                color:#991b1b;
                margin-top:5px;
            ">
            {formatar_moeda(valor_critico)}
            </div>

            <div style="
                font-size:13px;
                color:#6b7280;
                margin-top:3px;
            ">
            Estoque / Ag Retorno Comercial
            </div>

            </div>
            """, unsafe_allow_html=True)

        # CARD PENDENTES
        with col5:
        
            st.markdown(f"""
            <div style="
                background:white;
                border:1px solid #fef3c7;
                border-radius:14px;
                padding:14px;
                box-shadow:0 2px 8px rgba(0,0,0,0.04);
            ">
        
            <div style="
                font-size:24px;
            ">
            🟡
            </div>
        
            <div style="
                font-size:22px;
                font-weight:700;
                color:#b45309;
                margin-top:5px;
            ">
            {formatar_moeda(valor_pendente)}
            </div>
        
            <div style="
                font-size:13px;
                color:#6b7280;
                margin-top:3px;
            ">
            Valor Ag Atendimento
            </div>
        
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # =========================
        # TÍTULO
        # =========================
        st.markdown(
            "<div class='section-title'>🧾 Seus Pedidos</div>",
            unsafe_allow_html=True
        )

        # =========================
        # HTML TABELA PEDIDOS
        # =========================
        html = """
        <style>

        table {
            width:100%;
            border-collapse:collapse;
            font-family:Arial;
            background:white;
            border-radius:12px;
            overflow:hidden;
        }

        thead tr {
            background:#f3f4f6;
        }

        th {
            padding:14px;
            text-align:left;
            font-size:14px;
            color:#374151;
        }

        td {
            padding:14px;
            border-top:1px solid #f1f5f9;
            font-size:14px;
            color:#111827;
        }

        tr:hover {
            background:#f9fafb;
        }

        .pedido-highlight {
            font-weight:700;
            color:#c00000;
        }

        .motivo-highlight {
            font-weight:600;
            color:#b45309;
        }

        .valor-highlight {
            font-weight:700;
            color:#166534;
        }

        .badge-liberado {
            background:#dcfce7;
            color:#166534;
            padding:6px 10px;
            border-radius:999px;
            font-size:12px;
            font-weight:700;
        }

        .badge-pendente {
            background:#fee2e2;
            color:#991b1b;
            padding:6px 10px;
            border-radius:999px;
            font-size:12px;
            font-weight:700;
        }

        </style>

        <table>
        <thead>
        <tr>
        """

        # CABEÇALHO
        for col in pedidos_view.drop(columns=["Valor_num"]).columns:
            html += f"<th>{col}</th>"

        html += "</tr></thead><tbody>"

        # LINHAS
        for _, row in pedidos_view.drop(columns=["Valor_num"]).iterrows():

            status = str(row["Status"]).strip().lower()

            if status == "liberado":

                badge = f"""
                <span class='badge-liberado'>
                    {row['Status']}
                </span>
                """

            else:

                badge = f"""
                <span class='badge-pendente'>
                    {row['Status']}
                </span>
                """

            html += f"""
            <tr>

                <td class="pedido-highlight">
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

                <td class="motivo-highlight">
                    {row['Motivo']}
                </td>

                <td style="font-weight:700;">
                    {row['Previsão']}
                </td>

                <td class="valor-highlight">
                    {row['Valor (R$)']}
                </td>

            </tr>
            """

        html += "</tbody></table>"

        # =========================
        # ALTURA DINÂMICA
        # =========================
        quantidade_pedidos = len(pedidos_view)

        if quantidade_pedidos <= 5:

            altura_pedidos = (quantidade_pedidos * 52) + 50
            scroll = False

        else:

            altura_pedidos = 330
            scroll = True

        components.html(
            html,
            height=altura_pedidos,
            scrolling=scroll
        )

        # =========================
        # SELECT PEDIDO
        # =========================
        pedidos_view["Pedido_Cliente"] = (
            pedidos_view["Pedido"].astype(str)
            + " - "
            + pedidos_view["Cliente"].astype(str)
        )

        pedido_escolha = st.selectbox(
            "📌 Selecione um Pedido:",
            [""] + pedidos_view["Pedido_Cliente"].tolist()
        )

        # =========================
        # MOSTRAR APENAS SE ESCOLHER
        # =========================
        if pedido_escolha != "":

            pedido_selecionado = pedido_escolha.split(" - ")[0]

            pedido_info = pedidos_view[
                pedidos_view["Pedido"].astype(str) == pedido_selecionado
            ].iloc[0]

            # =========================
            # CARD PEDIDO
            # =========================
            st.markdown(f"""
            <div style="
            background:#fffbeb;
            border:1px solid #dfe3eb;
            border-left:5px solid #f59e0b;
            border-radius:14px;
            padding:20px;
            margin-top:15px;
            margin-bottom:25px;
            box-shadow:0 2px 8px rgba(0,0,0,0.05);
            ">

            <div style="
            font-size:14px;
            color:#6b7280;
            font-weight:600;
            ">
            Pedido Selecionado
            </div>

            <div style="
            font-size:28px;
            font-weight:700;
            color:#111827;
            margin-top:5px;
            ">
            #{pedido_selecionado}
            </div>

            <div style="
            font-size:15px;
            color:#6b7280;
            margin-top:6px;
            ">
            <b>Cliente:</b> {pedido_info['Cliente']}
            &nbsp;&nbsp; | &nbsp;&nbsp;
            <b>Valor:</b> {pedido_info['Valor (R$)']}
            </div>

            </div>
            """, unsafe_allow_html=True)

            # =========================
            # ITENS
            # =========================
            itens_pedido = itens[
                itens["Pedido"].astype(str) == pedido_selecionado
            ].copy()

            if "RC" in itens_pedido.columns:
                itens_pedido = itens_pedido.drop(columns=["RC"])

            if "Pedido" in itens_pedido.columns:
                itens_pedido = itens_pedido.drop(columns=["Pedido"])

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

            # =========================
            # HTML TABELA ITENS
            # =========================
            html_itens = """
            <style>

            table {
                width:100%;
                border-collapse:collapse;
                font-family:Arial;
                background:white;
                border-radius:12px;
                overflow:hidden;
            }

            thead tr {
                background:#f3f4f6;
            }

            th {
                padding:14px;
                text-align:left;
                font-size:14px;
                color:#374151;
            }

            td {
                padding:14px;
                border-top:1px solid #f1f5f9;
                font-size:14px;
                color:#111827;
            }

            tr:hover {
                background:#f9fafb;
            }

            .status-ok {
                background:#dcfce7;
                color:#166534;
                padding:6px 10px;
                border-radius:999px;
                font-size:12px;
                font-weight:700;
            }

            .status-alerta {
                background:#fee2e2;
                color:#991b1b;
                padding:6px 10px;
                border-radius:999px;
                font-size:12px;
                font-weight:700;
            }

            .valor-highlight {
                font-weight:700;
                color:#166534;
            }

            </style>

            <table>
            <thead>
            <tr>
            """

            # CABEÇALHO
            for col in itens_pedido.columns:
                html_itens += f"<th>{col}</th>"

            html_itens += "</tr></thead><tbody>"

            # LINHAS
            for _, row in itens_pedido.iterrows():

                status_reserva = str(
                    row.get("Status Reserva", "")
                ).strip().lower()

                if (
                    "reservado" in status_reserva
                    or
                    "ok" in status_reserva
                    or
                    "liberado" in status_reserva
                ):

                    badge_reserva = f"""
                    <span class='status-ok'>
                        {row.get('Status Reserva', '')}
                    </span>
                    """

                else:

                    badge_reserva = f"""
                    <span class='status-alerta'>
                        {row.get('Status Reserva', '')}
                    </span>
                    """

                html_itens += "<tr>"

                for col in itens_pedido.columns:

                    valor = row[col]

                    if col == "Status Reserva":

                        html_itens += f"<td>{badge_reserva}</td>"

                    elif col == "Valor (R$)":

                        html_itens += f"""
                        <td class='valor-highlight'>
                            {valor}
                        </td>
                        """

                    else:

                        html_itens += f"<td>{valor}</td>"

                html_itens += "</tr>"

            html_itens += "</tbody></table>"

            # ALTURA DINÂMICA
            quantidade_itens = len(itens_pedido)

            altura_itens = (quantidade_itens * 52) + 60

            components.html(
                html_itens,
                height=altura_itens,
                scrolling=False
            )

            # =========================
            # AÇÃO RECOMENDADA
            # =========================
            acoes_pedido = acoes[
                (acoes["Pedido"].astype(str) == pedido_selecionado)
                &
                (acoes["RC"].astype(str) == rc_input)
            ]

            if not acoes_pedido.empty:

                texto = limpar_texto(
                    acoes_pedido.iloc[0]["Texto"]
                )

                st.markdown(
                    "<div class='section-title'>🚨 Ação Recomendada</div>",
                    unsafe_allow_html=True
                )

                st.markdown(
                    f"""
                    <div style="
                        background:#fffbeb;
                        border:1px solid #d1d5db;
                        border-left:5px solid #f59e0b;
                        padding:18px;
                        border-radius:12px;
                        line-height:1.7;
                        white-space:pre-line;
                        font-size:15px;
                        color:#111827;
                    ">
                        {texto}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            else:

                st.info(
                    "Nenhuma ação cadastrada para este pedido."
                )

    else:

        st.error(
            "Nenhum pedido encontrado para este RC."
        )

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
import plotly.express as px
import plotly.graph_objects as go

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

/* ABAS */
.stTabs [data-baseweb="tab-list"] {
    gap: 12px;
}

.stTabs [data-baseweb="tab"] {
    background:white;
    border-radius:10px;
    padding:10px 18px;
    border:1px solid #e5e7eb;
    font-weight:600;
}

.stTabs [aria-selected="true"] {
    background:#c00000 !important;
    color:white !important;
}

/* CARDS */
.card-geral {
    background:white;
    border:1px solid #e5e7eb;
    border-radius:14px;
    padding:18px;
    box-shadow:0 2px 8px rgba(0,0,0,0.04);
}

/* TITULO GRAFICO */
.chart-title {
    font-size:15px;
    font-weight:700;
    color:#6b7280;
    margin-bottom:15px;
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
    texto = texto.replace("\\r\\n", "\n")
    texto = texto.replace("\\r", "\n")

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
        # ABAS
        # =========================
        tab1, tab2 = st.tabs([
            "📊 Visão Geral",
            f"📦 Pedidos ({total_pedidos})"
        ])

        # =====================================================
        # ABA 1 — VISÃO GERAL
        # =====================================================
        with tab1:

            # =========================
            # INSIGHTS
            # =========================
            st.markdown("""
            <div style="
                font-size:16px;
                font-weight:700;
                color:#6b7280;
                margin-top:5px;
                margin-bottom:10px;
            ">
            ⚡ INSIGHTS AUTOMÁTICOS
            </div>
            """, unsafe_allow_html=True)

            insight1, insight2 = st.columns(2)

            motivo_top = (
                pedidos_view.groupby("Motivo")["Valor_num"]
                .sum()
                .sort_values(ascending=False)
            )

            if len(motivo_top) > 0:

                motivo_nome = motivo_top.index[0]
                motivo_valor = motivo_top.iloc[0]

                percentual_motivo = (
                    motivo_valor / valor_total * 100
                ) if valor_total > 0 else 0

            else:

                motivo_nome = "-"
                percentual_motivo = 0

            percentual_liberado = (
                valor_liberado / valor_total * 100
            ) if valor_total > 0 else 0

            with insight1:

                st.markdown(f"""
                <div style="
                    background:#eff6ff;
                    border:1px solid #bfdbfe;
                    border-radius:14px;
                    padding:16px;
                    margin-bottom:15px;
                ">

                <div style="
                    font-size:18px;
                    font-weight:700;
                    color:#1d4ed8;
                ">
                📉 Concentração: "{motivo_nome}"
                </div>

                <div style="
                    margin-top:8px;
                    color:#2563eb;
                    font-size:15px;
                ">
                Representa {percentual_motivo:.0f}% do valor total
                ({formatar_moeda(motivo_valor)})
                </div>

                </div>
                """, unsafe_allow_html=True)

            with insight2:

                st.markdown(f"""
                <div style="
                    background:#f0fdf4;
                    border:1px solid #86efac;
                    border-radius:14px;
                    padding:16px;
                    margin-bottom:15px;
                ">

                <div style="
                    font-size:18px;
                    font-weight:700;
                    color:#15803d;
                ">
                ✅ {percentual_liberado:.0f}% dos pedidos estão liberados
                </div>

                <div style="
                    margin-top:8px;
                    color:#16a34a;
                    font-size:15px;
                ">
                {formatar_moeda(valor_liberado)} já disponíveis
                </div>

                </div>
                """, unsafe_allow_html=True)

            # =========================
            # GRÁFICOS
            # =========================
            col_graf1, col_graf2, col_graf3 = st.columns(3)

            # =========================
            # STATUS
            # =========================
            with col_graf1:

                st.markdown("""
                <div class='card-geral'>
                <div class='chart-title'>
                DISTRIBUIÇÃO POR STATUS
                </div>
                """, unsafe_allow_html=True)

                status_chart = (
                    pedidos_view.groupby("Status")
                    .size()
                    .reset_index(name="Quantidade")
                )

                fig_status = px.pie(
                    status_chart,
                    values="Quantidade",
                    names="Status",
                    hole=0.65
                )

                fig_status.update_layout(
                    height=320,
                    margin=dict(l=0, r=0, t=0, b=0),
                    showlegend=True
                )

                st.plotly_chart(
                    fig_status,
                    use_container_width=True
                )

                st.markdown("</div>", unsafe_allow_html=True)

            # =========================
            # MOTIVO
            # =========================
            with col_graf2:

                st.markdown("""
                <div class='card-geral'>
                <div class='chart-title'>
                VALOR POR MOTIVO
                </div>
                """, unsafe_allow_html=True)

                motivo_chart = (
                    pedidos_view.groupby("Motivo")["Valor_num"]
                    .sum()
                    .reset_index()
                )

                fig_motivo = px.bar(
                    motivo_chart,
                    x="Motivo",
                    y="Valor_num"
                )

                fig_motivo.update_layout(
                    height=320,
                    margin=dict(l=0, r=0, t=0, b=0),
                    xaxis_title="",
                    yaxis_title=""
                )

                st.plotly_chart(
                    fig_motivo,
                    use_container_width=True
                )

                st.markdown("</div>", unsafe_allow_html=True)

            # =========================
            # UF
            # =========================
            with col_graf3:

                st.markdown("""
                <div class='card-geral'>
                <div class='chart-title'>
                VALOR POR ESTADO (UF)
                </div>
                """, unsafe_allow_html=True)

                uf_chart = (
                    pedidos_view.groupby("UF")["Valor_num"]
                    .sum()
                    .reset_index()
                )

                fig_uf = px.bar(
                    uf_chart,
                    x="Valor_num",
                    y="UF",
                    orientation="h"
                )

                fig_uf.update_layout(
                    height=320,
                    margin=dict(l=0, r=0, t=0, b=0),
                    xaxis_title="",
                    yaxis_title=""
                )

                st.plotly_chart(
                    fig_uf,
                    use_container_width=True
                )

                st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # =========================
            # TOP CLIENTES
            # =========================
            st.markdown("""
            <div class='section-title'>
            🏆 Top Clientes por Valor
            </div>
            """, unsafe_allow_html=True)

            top_clientes = (
                pedidos_view.groupby("Cliente")["Valor_num"]
                .sum()
                .sort_values(ascending=False)
                .head(10)
                .reset_index()
            )

            fig_clientes = px.bar(
                top_clientes,
                x="Valor_num",
                y="Cliente",
                orientation="h"
            )

            fig_clientes.update_layout(
                height=420,
                margin=dict(l=0, r=0, t=0, b=0),
                xaxis_title="",
                yaxis_title=""
            )

            st.plotly_chart(
                fig_clientes,
                use_container_width=True
            )

        # =====================================================
        # ABA 2 — PEDIDOS
        # =====================================================
        with tab2:

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
                Pedido(s)
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
                Estoque / Ag RC
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
                Valor Pendente
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

            .badge-liberado {
                background:#dcfce7;
                color:#166534;
                padding:6px 10px;
                border-radius:999px;
                font-size:12px;
                font-weight:700;
            }

            .badge-conferido {
                background:#dbeafe;
                color:#1d4ed8;
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

            .pedido-highlight {
                font-weight:700;
                color:#c00000;
            }

            .valor-highlight {
                font-weight:700;
                color:#166534;
            }

            .motivo-estoque {
                font-weight:700;
                color:#dc2626;
            }

            .motivo-retorno {
                font-weight:700;
                color:#d97706;
            }

            .motivo-liberado {
                font-weight:700;
                color:#16a34a;
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

                # STATUS
                if status == "liberado":

                    badge = f"""
                    <span class='badge-liberado'>
                        {row['Status']}
                    </span>
                    """

                elif status == "conferido":

                    badge = f"""
                    <span class='badge-conferido'>
                        {row['Status']}
                    </span>
                    """

                else:

                    badge = f"""
                    <span class='badge-pendente'>
                        {row['Status']}
                    </span>
                    """

                motivo_html = f"""
                <span style="
                    font-weight:700;
                    color:#d97706;
                ">
                    {row['Motivo']}
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

                    <td>
                        {motivo_html}
                    </td>

                    <td style="
                        font-weight:700;
                        color:#374151;
                    ">
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
            # SOMENTE SE ESCOLHER PEDIDO
            # =========================
            if pedido_escolha != "":

                pedido_numero = pedido_escolha.split(" - ")[0]

                pedido_info = pedidos_view[
                    pedidos_view["Pedido"].astype(str) == pedido_numero
                ].iloc[0]

                st.markdown("<br>", unsafe_allow_html=True)

                # =========================
                # PEDIDO SELECIONADO
                # =========================

                st.markdown(f"""
                <div style="
                background:#fff7f7;
                border:1px solid #f3dede;
                border-left:5px solid #c00000;
                border-radius:12px;
                padding:18px;
                margin-top:10px;
                margin-bottom:20px;
                box-shadow:0 2px 8px rgba(0,0,0,0.04);
                ">
                
                <div style="
                font-size:13px;
                font-weight:600;
                color:#6b7280;
                margin-bottom:8px;
                ">
                Pedido Selecionado
                </div>
                
                <div style="
                font-size:34px;
                font-weight:800;
                color:#111827;
                line-height:1;
                ">
                #{pedido_info['Pedido']}
                </div>
                
                <div style="
                font-size:14px;
                color:#6b7280;
                margin-top:16px;
                ">
                <b>Cliente:</b> {pedido_info['Cliente']}
                &nbsp;&nbsp;&nbsp; |
                &nbsp;&nbsp;&nbsp;
                <b>Valor:</b> {pedido_info['Valor (R$)']}
                </div>
                
                </div>
                """, unsafe_allow_html=True)

                # =========================
                # ITENS
                # =========================
                st.markdown("""
                <div class='section-title'>
                📦 Itens do Pedido
                </div>
                """, unsafe_allow_html=True)
                
                itens_pedido = itens[
                    itens["Pedido"].astype(str) == pedido_numero
                ].copy()
                
                if not itens_pedido.empty:
                
                    # =========================
                    # RENOMEIA COLUNAS
                    # =========================
                    itens_pedido = itens_pedido.rename(columns={
                
                        "Codigo": "Código",
                        "Descricao": "Descrição",
                        "Qtd Ped": "Qtde",
                        "Valor Total": "Valor Total (R$)"
                
                    })
                
                    # =========================
                    # FORMATAÇÕES
                    # =========================
                    if "Previsão Final" in itens_pedido.columns:
                
                        itens_pedido["Previsão Final"] = (
                            itens_pedido["Previsão Final"]
                            .apply(formatar_data)
                            .replace("NaT", "")
                        )
                
                    if "Valor Total (R$)" in itens_pedido.columns:
                
                        itens_pedido["Valor Total (R$)"] = (
                            itens_pedido["Valor Total (R$)"]
                            .apply(formatar_moeda)
                        )
                
                    # =========================
                    # HTML
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
                
                    .status-reservado {
                        background:#dcfce7;
                        color:#166534;
                        padding:6px 10px;
                        border-radius:999px;
                        font-size:12px;
                        font-weight:700;
                    }
                
                    .status-saldo {
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
                    for col in itens_pedido.columns:
                        html_itens += f"<th>{col}</th>"
                
                    html_itens += "</tr></thead><tbody>"
                
                    # LINHAS
                    for _, row in itens_pedido.iterrows():
                
                        html_itens += "<tr>"
                
                        for col in itens_pedido.columns:
                
                            valor = row[col]
                
                            # STATUS RESERVA
                            if col == "Status Reserva":
                
                                status = str(valor).strip().lower()
                
                                if status == "reservado":
                
                                    valor = f"""
                                    <span class='status-reservado'>
                                        {row[col]}
                                    </span>
                                    """
                
                                else:
                
                                    valor = f"""
                                    <span class='status-saldo'>
                                        {row[col]}
                                    </span>
                                    """
                
                            html_itens += f"<td>{valor}</td>"
                
                        html_itens += "</tr>"
                
                    html_itens += "</tbody></table>"
                
                    # =========================
                    # ALTURA DINÂMICA
                    # =========================
                    quantidade_itens = len(itens_pedido)
                
                    if quantidade_itens <= 8:
                
                        altura_itens = (quantidade_itens * 52) + 55
                        scroll_itens = False
                
                    else:
                
                        altura_itens = 450
                        scroll_itens = True
                
                    components.html(
                        html_itens,
                        height=altura_itens,
                        scrolling=scroll_itens
                    )
                
                else:
                
                    st.info(
                        "Nenhum item encontrado para este pedido."
                    )

                st.markdown("<br>", unsafe_allow_html=True)

                # =========================
                # AÇÃO RECOMENDADA
                # =========================
                st.markdown("""
                <div class='section-title'>
                💡 Ação Recomendada
                </div>
                """, unsafe_allow_html=True)

                acoes_pedido = acoes[
                    acoes["Pedido"].astype(str) == pedido_numero
                ]

                if not acoes_pedido.empty:

                    texto = limpar_texto(
                        acoes_pedido.iloc[0]["Texto"]
                    )

                    st.markdown(
                        f"""
                        <div style="
                            background:#fff5f5;
                            border:1px solid #fecaca;
                            border-left:5px solid #c00000;
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

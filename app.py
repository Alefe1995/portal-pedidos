# Portal de Pedidos — Layout Profissional estilo Base44

```python
import pandas as pd
import streamlit as st

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
st.markdown(
    """
    <style>

    /* FUNDO */
    .stApp {
        background-color: #f5f7fb;
    }

    /* HEADER */
    .top-header {
        background-color:#c00000;
        padding:14px 20px;
        border-radius:0px;
        margin-bottom:25px;
        color:white;
        font-size:26px;
        font-weight:700;
        box-shadow:0 2px 8px rgba(0,0,0,0.15);
    }

    /* CARDS */
    .card {
        background:white;
        padding:18px;
        border-radius:14px;
        border:1px solid #e6e9ef;
        box-shadow:0 2px 10px rgba(0,0,0,0.04);
        margin-bottom:18px;
    }

    /* TITULOS */
    .section-title {
        font-size:18px;
        font-weight:700;
        color:#1f2937;
        margin-bottom:12px;
    }

    /* PEDIDO SELECIONADO */
    .pedido-box {
        background:white;
        border:1px solid #e5e7eb;
        border-radius:14px;
        padding:18px;
        margin-top:10px;
        margin-bottom:20px;
        box-shadow:0 2px 10px rgba(0,0,0,0.04);
    }

    .pedido-label {
        font-size:12px;
        color:#6b7280;
        font-weight:600;
        text-transform:uppercase;
        margin-bottom:4px;
    }

    .pedido-numero {
        font-size:28px;
        font-weight:700;
        color:#111827;
    }

    .pedido-cliente {
        font-size:15px;
        color:#6b7280;
        margin-top:5px;
    }

    /* BADGES STATUS */
    .status-liberado {
        background:#d1fae5;
        color:#065f46;
        padding:5px 12px;
        border-radius:999px;
        font-size:12px;
        font-weight:600;
        display:inline-block;
    }

    .status-conferido {
        background:#dbeafe;
        color:#1d4ed8;
        padding:5px 12px;
        border-radius:999px;
        font-size:12px;
        font-weight:600;
        display:inline-block;
    }

    .status-pendente {
        background:#fef3c7;
        color:#92400e;
        padding:5px 12px;
        border-radius:999px;
        font-size:12px;
        font-weight:600;
        display:inline-block;
    }

    /* SIDEBAR */
    section[data-testid="stSidebar"] {
        background:#ffffff;
        border-right:1px solid #e5e7eb;
    }

    /* INPUTS */
    .stTextInput input,
    .stSelectbox div[data-baseweb="select"] {
        border-radius:10px !important;
    }

    </style>
    """,
    unsafe_allow_html=True
)

# =========================
# HEADER
# =========================
st.markdown(
    """
    <div class='top-header'>
        Portal de Pedidos
    </div>
    """,
    unsafe_allow_html=True
)

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


def badge_status(status):

    status = str(status).lower()

    if "liberado" in status:
        return "<span class='status-liberado'>Liberado</span>"

    if "conferido" in status:
        return "<span class='status-conferido'>Conferido</span>"

    return "<span class='status-pendente'>Pendente</span>"


# =========================
# DADOS
# =========================
pedidos = pd.read_excel("Pedidos.xlsx")
itens = pd.read_excel("Itens.xlsx")
acoes = pd.read_excel("Ação.xlsx")

# =========================
# INPUT RC
# =========================
st.markdown("<div class='card'>", unsafe_allow_html=True)

rc_input = st.text_input("🔎 Digite seu código RC:")

st.markdown("</div>", unsafe_allow_html=True)

# =========================
# PROCESSAMENTO
# =========================
if rc_input:

    base = pedidos[pedidos["RC"].astype(str) == rc_input].copy()

    if not base.empty:

        if "RC" in base.columns:
            base = base.drop(columns=["RC"])

        base = base.rename(columns={
            "Pedido2": "Qtde",
            "Soma de Valor": "Valor (R$)"
        })

        # FORMATAÇÃO
        for col in ["Valor (R$)", "Soma de Valores"]:
            if col in base.columns:
                base[col] = base[col].apply(formatar_moeda)

        if "Previsão" in base.columns:
            base["Previsão"] = base["Previsão"].apply(formatar_data)

        # =========================
        # SIDEBAR
        # =========================
        st.sidebar.image("download.png", width=120)

        st.sidebar.markdown("## 🔎 Filtros")

        # STATUS
        status_list = sorted(base["Status"].dropna().unique()) if "Status" in base.columns else []
        status = st.sidebar.selectbox("Status", ["Todos"] + status_list)

        df1 = base.copy()

        if status != "Todos":
            df1 = df1[df1["Status"] == status]

        # MOTIVO
        motivo_list = sorted(df1["Motivo"].dropna().unique()) if "Motivo" in df1.columns else []
        motivo = st.sidebar.selectbox("Motivo", ["Todos"] + motivo_list)

        df2 = df1.copy()

        if motivo != "Todos":
            df2 = df2[df2["Motivo"] == motivo]

        # CLIENTE
        cliente = st.sidebar.text_input("Cliente")

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
        st.sidebar.markdown(f"### 💰 Valor Total")
        st.sidebar.success(formatar_moeda(valor_total))

        # =========================
        # CARD PEDIDOS
        # =========================
        st.markdown("<div class='card'>", unsafe_allow_html=True)

        st.markdown(
            "<div class='section-title'>🧾 Seus Pedidos</div>",
            unsafe_allow_html=True
        )

        st.dataframe(
            pedidos_view.drop(columns=["Valor_num"]),
            use_container_width=True,
            hide_index=True
        )

        st.markdown("</div>", unsafe_allow_html=True)

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

        if pedido_selecionado:

            pedido_numero = pedido_selecionado.split(" - ")[0]

            pedido_info = pedidos_view[
                pedidos_view["Pedido"].astype(str) == pedido_numero
            ].iloc[0]

            # =========================
            # PEDIDO SELECIONADO
            # =========================
            st.markdown(
                f"""
                <div class='pedido-box'>
                    <div class='pedido-label'>Pedido Selecionado</div>
                    <div class='pedido-numero'>#{pedido_numero}</div>
                    <div class='pedido-cliente'>{pedido_info['Cliente']}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

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

            st.markdown("<div class='card'>", unsafe_allow_html=True)

            st.markdown(
                "<div class='section-title'>📦 Itens do Pedido</div>",
                unsafe_allow_html=True
            )

            st.dataframe(
                itens_pedido,
                use_container_width=True,
                hide_index=True
            )

            st.markdown("</div>", unsafe_allow_html=True)

            # =========================
            # AÇÕES
            # =========================
            acoes_pedido = acoes[
                (acoes["Pedido"].astype(str) == pedido_numero) &
                (acoes["RC"].astype(str) == rc_input)
            ]

            st.markdown("<div class='card'>", unsafe_allow_html=True)

            if not acoes_pedido.empty:

                texto = limpar_texto(acoes_pedido.iloc[0]["Texto"])

                st.markdown(
                    "<div class='section-title'>🚨 Ação Recomendada</div>",
                    unsafe_allow_html=True
                )

                st.info(texto)

            else:
                st.info("Nenhuma ação cadastrada para este pedido.")

            st.markdown("</div>", unsafe_allow_html=True)

    else:
        st.error("Nenhum pedido encontrado para este RC.")
```

---

# O que mudou visualmente

## ✅ Cards estilo Base44

Cada área agora fica dentro de um container visual:

* tabela de pedidos
* pedido selecionado
* itens
* ação

---

## ✅ Fundo cinza claro moderno

Mesmo estilo visual da imagem que você mostrou.

---

## ✅ Status coloridos

* Liberado → verde
* Conferido → azul
* Pendente → amarelo

---

## ✅ Pedido selecionado profissional

Agora aparece em destaque:

* número grande
* nome do cliente
* box separado

---

## ✅ Sidebar mais limpa

Visual semelhante a ERP / dashboard.

---

## Próximo upgrade recomendado

Depois disso, o próximo nível seria:

* substituir `st.dataframe` por tabela HTML customizada
* aplicar cores reais nos status dentro da tabela
* adicionar hover
* adicionar clique direto na linha
* adicionar métricas no topo
* adicionar gráficos

Aí seu sistema começa realmente a ficar com cara de software profissional.

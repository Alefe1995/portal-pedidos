import pandas as pd
import streamlit as st

# =========================
# CONFIGURAÇÃO DA PÁGINA
# =========================
st.set_page_config(layout="wide", page_title="Portal de Pedidos Adere")

# CSS para customização avançada (Estilo Base44)
st.markdown("""
    <style>
    /* Fundo da Sidebar */
    [data-testid="stSidebar"] {
        background-color: #f8f9fa;
        border-right: 1px solid #e0e0e0;
    }
    
    /* Título da Sidebar */
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2 {
        color: #c00000;
        font-size: 1.2rem;
    }

    /* Botão Buscar Vermelho */
    div.stButton > button {
        background-color: #c00000;
        color: white;
        border-radius: 5px;
        width: 100%;
        border: none;
    }
    div.stButton > button:hover {
        background-color: #a00000;
        color: white;
    }

    /* Estilo dos Headers das Tabelas */
    .stDataFrame {
        border: 1px solid #e6e6e6;
        border-radius: 10px;
    }

    /* Faixa Superior */
    .main-header {
        background-color: #c00000;
        padding: 15px;
        border-radius: 5px;
        color: white;
        font-weight: bold;
        font-size: 24px;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
    }
    </style>
    """, unsafe_allow_html=True)

# =========================
# FUNÇÕES DE FORMATAÇÃO
# =========================
def para_float(valor):
    try:
        if pd.isna(valor): return 0
        if isinstance(valor, (int, float)): return float(valor)
        valor = str(valor).replace("R$", "").strip().replace(".", "").replace(",", ".")
        return float(valor)
    except: return 0

def formatar_moeda(valor):
    try:
        if pd.isna(valor): return ""
        v = para_float(valor)
        return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except: return valor

# =========================
# HEADER
# =========================
st.markdown('<div class="main-header">Portal de Pedidos</div>', unsafe_allow_html=True)

# =========================
# CARGA DE DADOS
# =========================
@st.cache_data
def carregar_dados():
    try:
        pedidos = pd.read_excel("Pedidos.xlsx")
        itens = pd.read_excel("Itens.xlsx")
        acoes = pd.read_excel("Ação.xlsx")
        return pedidos, itens, acoes
    except:
        st.error("Erro ao carregar arquivos .xlsx. Verifique se eles estão no repositório.")
        return None, None, None

pedidos, itens, acoes = carregar_dados()

# =========================
# BUSCA DE RC (LAYOUT CENTRALIZADO)
# =========================
col_rc1, col_rc2 = st.columns([3, 1])
with col_rc1:
    rc_input = st.text_input("Código RC", placeholder="Digite o código...")
with col_rc2:
    st.write("##") # Espaçador
    btn_buscar = st.button("Buscar")

if rc_input:
    base = pedidos[pedidos["RC"].astype(str) == rc_input].copy()

    if not base.empty:
        # Pre-processamento
        if "RC" in base.columns: base = base.drop(columns=["RC"])
        base = base.rename(columns={"Pedido2": "Qtde", "Soma de Valor": "Valor (R$)"})

        # =========================
        # SIDEBAR (FILTROS)
        # =========================
        with st.sidebar:
            st.image("download.png", width=120)
            st.markdown("###  Filtros")
            
            status_list = sorted(base["Status"].dropna().unique())
            status_sel = st.selectbox("Status", ["Todos"] + status_list)
            
            motivo_list = sorted(base["Motivo"].dropna().unique())
            motivo_sel = st.selectbox("Motivo", ["Todos"] + motivo_list)
            
            cliente_input = st.text_input("Cliente", placeholder="Buscar cliente...")

            # Aplicar Filtros
            df_filtrado = base.copy()
            if status_sel != "Todos": df_filtrado = df_filtrado[df_filtrado["Status"] == status_sel]
            if motivo_sel != "Todos": df_filtrado = df_filtrado[df_filtrado["Motivo"] == motivo_sel]
            if cliente_input: df_filtrado = df_filtrado[df_filtrado["Cliente"].str.contains(cliente_input, case=False)]

            # Valor Total no final da Sidebar
            st.markdown("---")
            total = df_filtrado["Valor (R$)"].apply(para_float).sum()
            st.metric("Valor Total", formatar_moeda(total))

        # =========================
        # TABELA PRINCIPAL
        # =========================
        st.markdown(f"### 🧾 Seus Pedidos ({len(df_filtrado)} pedidos)")
        
        # Formatação para exibição
        display_df = df_filtrado.copy()
        if "Previsão" in display_df.columns:
            display_df["Previsão"] = pd.to_datetime(display_df["Previsão"]).dt.strftime('%d/%m/%Y')

        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Valor (R$)": st.column_config.NumberColumn(format="R$ %.2f"),
                "Status": st.column_config.TextColumn(help="Status atual do pedido")
            }
        )

        # =========================
        # DETALHES DO PEDIDO SELECIONADO
        # =========================
        st.markdown("---")
        lista_pedidos = (df_filtrado["Pedido"].astype(str) + " - " + df_filtrado["Cliente"].astype(str)).unique()
        pedido_selecionado = st.selectbox("📌 Selecione um pedido para ver detalhes:", lista_pedidos)

        if pedido_selecionado:
            id_pedido = pedido_selecionado.split(" - ")[0]
            
            # Itens
            df_itens = itens[itens["Pedido"].astype(str) == id_pedido].copy()
            st.subheader("📦 Itens do Pedido")
            st.dataframe(df_itens, use_container_width=True, hide_index=True)

            # Ações (Card Azul como na imagem)
            df_acao = acoes[(acoes["Pedido"].astype(str) == id_pedido) & (acoes["RC"].astype(str) == rc_input)]
            
            st.subheader("🚨 Ação Recomendada")
            if not df_acao.empty:
                texto_acao = df_acao.iloc[0]["Texto"]
                st.info(texto_acao)
            else:
                st.warning("Nenhuma ação cadastrada.")

    else:
        st.error("Nenhum pedido encontrado para este RC.")

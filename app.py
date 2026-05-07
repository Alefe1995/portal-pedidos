import pandas as pd
import streamlit as st

# =========================
# 1. CONFIGURAÇÃO DA PÁGINA
# =========================
st.set_page_config(layout="wide", page_title="Portal de Pedidos Adere")

# CSS para customização avançada (Estilo Base44 / Adere)
st.markdown("""
    <style>
    /* Fundo da Sidebar cinza claro */
    [data-testid="stSidebar"] {
        background-color: #f8f9fa;
        border-right: 1px solid #e0e0e0;
    }
    
    /* Títulos da Sidebar em vermelho Adere */
    [data-testid="stSidebar"] h3 {
        color: #c00000 !important;
        font-size: 1.1rem;
        font-weight: bold;
    }

    /* Botão Buscar Vermelho */
    div.stButton > button {
        background-color: #c00000;
        color: white;
        border-radius: 5px;
        width: 100%;
        border: none;
        height: 45px;
        font-weight: bold;
    }
    div.stButton > button:hover {
        background-color: #a00000;
        color: white;
    }

    /* Faixa Superior (Header) */
    .main-header {
        background-color: #c00000;
        padding: 15px 25px;
        border-radius: 8px;
        color: white;
        font-weight: bold;
        font-size: 22px;
        margin-bottom: 25px;
    }
    </style>
    """, unsafe_allow_html=True)

# =========================
# 2. FUNÇÕES DE SUPORTE
# =========================
def para_float(valor):
    try:
        if pd.isna(valor): return 0.0
        if isinstance(valor, (int, float)): return float(valor)
        valor = str(valor).replace("R$", "").strip().replace(".", "").replace(",", ".")
        return float(valor)
    except: return 0.0

def formatar_moeda(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# =========================
# 3. CARGA DE DADOS
# =========================
@st.cache_data
def carregar_dados():
    try:
        ped_df = pd.read_excel("Pedidos.xlsx")
        ite_df = pd.read_excel("Itens.xlsx")
        aco_df = pd.read_excel("Ação.xlsx")
        return ped_df, ite_df, aco_df
    except Exception as e:
        st.error(f"Erro ao carregar arquivos Excel: {e}")
        return None, None, None

pedidos_raw, itens_raw, acoes_raw = carregar_dados()

# =========================
# 4. HEADER E BUSCA INICIAL
# =========================
st.markdown('<div class="main-header">Portal de Pedidos</div>', unsafe_allow_html=True)

# Layout de busca superior (Correção da linha que deu erro)
col_rc1, col_rc2 = st.columns([4, 1])
with col_rc1:
    rc_input = st.text_input("Código RC", placeholder="Digite o código RC...", label_visibility="collapsed")
with col_rc2:
    btn_buscar = st.button("BUSCAR")

# =========================
# 5. LÓGICA PRINCIPAL
# =========================
if rc_input:
    # Filtrar base pelo RC
    base = pedidos_raw[pedidos_raw["RC"].astype(str) == rc_input].copy()

    if not base.empty:
        # --- SIDEBAR (FILTROS) ---
        with st.sidebar:
            st.image("download.png", width=150)
            st.markdown("### 🔎 Filtros")
            
            status_list = sorted(base["Status"].dropna().unique()) if "Status" in base.columns else []
            status_sel = st.selectbox("Status", ["Todos"] + status_list)
            
            motivo_list = sorted(base["Motivo"].dropna().unique()) if "Motivo" in base.columns else []
            motivo_sel = st.selectbox("Motivo", ["Todos"] + motivo_list)
            
            cliente_input = st.text_input("Buscar Cliente")

            # Aplicar Filtros
            df_view = base.copy()
            if status_sel != "Todos":
                df_view = df_view[df_view["Status"] == status_sel]
            if motivo_sel != "Todos":
                df_view = df_view[df_view["Motivo"] == motivo_sel]
            if cliente_input:
                df_view = df_view[df_view["Cliente"].str.contains(cliente_input, case=False, na=False)]

            # Resumo Financeiro
            st.markdown("---")
            st.markdown("### 💰 Resumo Financeiro")
            # Ajuste dinâmico da coluna de valor
            col_valor = "Soma de Valor" if "Soma de Valor" in df_view.columns else df_view.columns[-1]
            valor_total_num = df_view[col_valor].apply(para_float).sum()
            st.metric("Total Filtrado", formatar_moeda(valor_total_num))

        # --- TABELA PRINCIPAL ---
        st.markdown(f"### 🧾 Seus Pedidos ({len(df_view)})")
        
        display_df = df_view.copy()
        # Tratamento de Data Seguro
        if "Previsão" in display_df.columns:
            display_df["Previsão"] = pd.to_datetime(display_df["Previsão"], errors='coerce')
            display_df["Previsão"] = display_df["Previsão"].apply(lambda x: x.strftime('%d/%m/%Y') if pd.notnull(x) else "")

        st.dataframe(
            display_df.drop(columns=["RC"], errors='ignore'),
            use_container_width=True,
            hide_index=True
        )

        # --- SELEÇÃO E DETALHES ---
        st.markdown("---")
        if "Pedido" in display_df.columns and "Cliente" in display_df.columns:
            display_df["Label"] = display_df["Pedido"].astype(str) + " - " + display_df["Cliente"].astype(str)
            pedido_selecionado = st.selectbox("📌 Selecione um pedido para detalhes:", display_df["Label"].unique())

            if pedido_selecionado:
                id_pedido = pedido_selecionado.split(" - ")[0]
                
                # Itens
                df_itens = itens_raw[itens_raw["Pedido"].astype(str) == id_pedido].copy()
                st.markdown("#### 📦 Itens do Pedido")
                if "Previsão Final" in df_itens.columns:
                    df_itens["Previsão Final"] = pd.to_datetime(df_itens["Previsão Final"], errors='coerce').apply(lambda x: x.strftime('%d/%m/%Y') if pd.notnull(x) else "")
                
                st.dataframe(df_itens.drop(columns=["RC"], errors='ignore'), use_container_width=True, hide_index=True)

                # Ação
                st.markdown("#### 🚨 Ação Recomendada")
                df_acao = acoes_raw[(acoes_raw["Pedido"].astype(str) == id_pedido) & (acoes_raw["RC"].astype(str) == rc_input)]
                if not df_acao.empty:
                    st.info(df_acao.iloc[0]["Texto"])
                else:
                    st.warning("Nenhuma ação cadastrada.")
    else:
        st.error("Nenhum pedido encontrado para este RC.")

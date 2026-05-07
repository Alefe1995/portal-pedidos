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
        color: #c00000;
        font-size: 1.1rem;
        font-weight: bold;
        margin-bottom: 10px;
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
        border: none;
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
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    /* Estilização dos inputs */
    .stTextInput input {
        border-radius: 5px;
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
        st.error(f"Erro ao carregar arquivos: {e}")
        return None, None, None

pedidos_raw, itens_raw, acoes_raw = carregar_dados()

# =========================
# 4. HEADER E BUSCA INICIAL
# =========================
st.markdown('<div class="main-header">Portal de Pedidos</div>', unsafe_allow_html=True)

# Layout de busca superior
col_rc1, col_rc2 = st.columns([4, 1])
with col_rc1:
    rc_input = st.text_input("Código RC", placeholder="Digite o código RC para buscar seus pedidos...", label

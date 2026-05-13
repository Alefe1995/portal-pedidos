import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
import plotly.express as px
import plotly.graph_objects as go


def mostrar_portal(filtro_tipo="MASTER", filtro_valor=None):

    # =========================
    # CSS GLOBAL
    # =========================
    st.markdown("""
    <style>

    header { visibility:hidden; }
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    [data-testid="stToolbar"]      { display: none !important; }
    .stDeployButton                { display: none !important; }
    [data-testid="stDecoration"]   { display: none !important; }
    [data-testid="stStatusWidget"] { display: none !important; }
    [data-testid="stFloatingButton"]{ display: none !important; }
    button[kind="secondary"]       { display: none !important; }
    div[style*="position: fixed"]  { display: none !important; }

    /* Remove botão << da sidebar */
    [data-testid="stSidebarCollapseButton"],
    [data-testid="collapsedControl"] {
        display: none !important;
    }

    .stApp { background-color: #f4f5f7; }

    .block-container {
        padding-top: 0rem !important;
        padding-bottom: 2rem !important;
    }

    /* ── HEADER ── */
    .top-header {
        background-color: #c00000;
        padding: 14px 24px;
        margin-bottom: 20px;
        color: white;
        font-size: 18px;
        font-weight: 700;
        display: flex;
        align-items: center;
        gap: 10px;
        margin-left: -1rem;
        margin-right: -1rem;
    }
    .top-header .subtitle { font-size:12px; font-weight:400; opacity:0.85; }

    /* ══════════════════════════════════════════════════
       SIDEBAR — ícone quando retraída, expande no hover
       ══════════════════════════════════════════════════ */
    section[data-testid="stSidebar"] {
        background: #ffffff;
        border-right: 1px solid #e5e7eb;
        transition: width 0.3s ease, min-width 0.3s ease !important;
        overflow: hidden !important;
        min-width: 52px !important;
        width:     52px !important;
    }
    section[data-testid="stSidebar"]:hover {
        width:     280px !important;
        min-width: 280px !important;
        box-shadow: 4px 0 16px rgba(0,0,0,0.10);
    }

    /* Ícone de filtro quando retraída */
    section[data-testid="stSidebar"] > div:first-child::before {
        content: "⚙️";
        font-size: 22px;
        display: flex;
        align-items: center;
        justify-content: center;
        height: 52px;
        width: 52px;
    }
    section[data-testid="stSidebar"]:hover > div:first-child::before {
        display: none;
    }

    /* Esconde conteúdo quando retraída */
    section[data-testid="stSidebar"] [data-testid="stSidebarContent"] {
        opacity: 0;
        transition: opacity 0.15s ease;
        overflow: hidden;
    }
    section[data-testid="stSidebar"]:hover [data-testid="stSidebarContent"] {
        opacity: 1;
        transition: opacity 0.2s ease 0.1s;
    }

    /* ── Inputs e selects ── */
    .stTextInput input {
        border-radius: 8px !important;
        border: 1px solid #d1d5db !important;
        padding: 8px 12px !important;
        background: white !important;
        font-size: 14px !important;
    }
    div[data-baseweb="select"] > div {
        border-radius: 8px !important;
        border: 1px solid #d1d5db !important;
        background: white !important;
        min-height: 38px;
    }

    /* ── Abas ── */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px; background: transparent;
        border-bottom: 1px solid #e5e7eb !important; padding-bottom: 0;
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent; border-radius: 6px 6px 0 0;
        padding: 8px 18px; border: none;
        font-weight: 600; font-size: 14px; color: #6b7280;
    }
    .stTabs [aria-selected="true"] {
        background: #c00000 !important; color: white !important;
        border-radius: 6px 6px 0 0;
    }
    .stTabs [data-baseweb="tab-border"] { display: none; }

    /* ── KPI cards ── */
    .kpi-card {
        background: white; border: 1px solid #e5e7eb;
        border-radius: 12px; padding: 16px 18px;
        box-shadow: 0 1px 4px rgba(0,0,0,0.05);
    }

    .stAlert { border-radius: 10px; }

    div[data-testid="stRadio"] > label { font-weight:600 !important; font-size:13px !important; }

    div[data-testid="stButton"] button {
        background-color: #c00000 !important; color: white !important;
        border: none !important; border-radius: 8px !important;
        font-weight: 600 !important; font-size: 14px !important; padding: 8px 20px !important;
    }
    div[data-testid="stButton"] button:hover { background-color: #a00000 !important; }

    </style>
    """, unsafe_allow_html=True)

    # =========================
    # FUNÇÕES AUXILIARES
    # =========================
    def para_float(valor):
        try:
            if pd.isna(valor): return 0
            if isinstance(valor, (int, float)): return float(valor)
            valor = str(valor).replace("R$","").strip().replace(".","").replace(",",".")
            return float(valor)
        except: return 0

    def formatar_moeda(valor):
        try:
            if pd.isna(valor): return ""
            v = float(str(valor).replace("R$","").strip().replace(".","").replace(",",".")) if not isinstance(valor,(int,float)) else float(valor)
            return f"R$ {v:,.2f}".replace(",","X").replace(".",",").replace("X",".")
        except: return valor

    def formatar_moeda_curto(valor):
        try:
            v = float(valor)
            if v >= 1_000_000: return f"R$ {v/1_000_000:.1f}M"
            elif v >= 1_000:   return f"R$ {v/1_000:.1f}k"
            else:              return f"R$ {v:.0f}"
        except: return "R$ 0"

    def formatar_data(valor):
        try:
            if pd.isna(valor): return ""
            data = pd.to_datetime(valor, errors="coerce")
            return data.strftime("%d/%m/%Y") if pd.notna(data) else str(valor)
        except: return str(valor)

    def formatar_cnpj(valor):
        try:
            if pd.isna(valor): return ""
            digits = str(int(float(str(valor).replace(".","").replace("/","").replace("-","")))).zfill(14)
            return f"{digits[:2]}.{digits[2:5]}.{digits[5:8]}/{digits[8:12]}-{digits[12:14]}"
        except: return str(valor)

    def limpar_texto(texto):
        if pd.isna(texto): return ""
        texto = str(texto).replace("_x000D_","\n").replace("\\r\\n","\n").replace("\\r","\n")
        return "\n".join([l.strip() for l in texto.split("\n") if l.strip()])

    def badge_status(status_val):
        s = str(status_val).strip().lower()
        if s == "liberado":
            return f"<span style='background:#dcfce7;color:#166534;padding:3px 10px;border-radius:999px;font-size:12px;font-weight:600;'>{status_val}</span>"
        elif s == "conferido":
            return f"<span style='background:#dbeafe;color:#1d4ed8;padding:3px 10px;border-radius:999px;font-size:12px;font-weight:600;'>{status_val}</span>"
        elif s == "batch":
            return f"<span style='background:#f3e8ff;color:#7c3aed;padding:3px 10px;border-radius:999px;font-size:12px;font-weight:600;'>{status_val}</span>"
        else:
            return f"<span style='background:#fef9c3;color:#92400e;padding:3px 10px;border-radius:999px;font-size:12px;font-weight:600;'>{status_val}</span>"

    # =========================
    # HEADER
    # =========================
    usuario_logado = st.session_state.get("usuario_atual", "")
    st.markdown(f"""
    <div class='top-header'>
        <div>
            <div>📋 Portal de Pedidos</div>
            <div class='subtitle'>ADERE Produto Auto Adesivos</div>
        </div>
        <div style="margin-left:auto;font-size:13px;opacity:0.8;">Olá, {usuario_logado}</div>
    </div>
    """, unsafe_allow_html=True)

    # =========================
    # DADOS
    # =========================
    pedidos = pd.read_excel("Pedidos.xlsx")
    itens   = pd.read_excel("Itens.xlsx")
    acoes   = pd.read_excel("Ação.xlsx")

    if "CNPJ" in pedidos.columns:
        pedidos["CNPJ"] = pedidos["CNPJ"].apply(formatar_cnpj)

    # =========================
    # FILTRO TIPO USUÁRIO
    # =========================
    base = pd.DataFrame()
    identificador = ""

    if filtro_tipo == "RC":
        base = pedidos[pedidos["RC"].astype(str) == str(filtro_valor)].copy()
        identificador = f"RC {filtro_valor}"

    elif filtro_tipo == "COORDENADOR":
        if "Coordenador" in pedidos.columns:
            base = pedidos[pedidos["Coordenador"].astype(str) == str(filtro_valor)].copy()
        identificador = f"Coordenador: {filtro_valor}"

    else:
        st.markdown("<div style='margin-bottom:8px;font-size:13px;font-weight:600;color:#374151;'>🔍 Buscar por:</div>", unsafe_allow_html=True)
        tipo_busca = st.radio("Tipo de Busca", ["Código RC","Coordenador de Vendas"], horizontal=True, label_visibility="collapsed")

        if tipo_busca == "Código RC":
            col_rc, col_btn, _ = st.columns([2,1,5])
            with col_rc:
                rc_input = st.text_input("CÓDIGO RC", placeholder="Ex: 614", max_chars=5)
            with col_btn:
                st.markdown("<div style='margin-top:28px;'></div>", unsafe_allow_html=True)
                st.button("Buscar", use_container_width=True)
            if rc_input:
                base = pedidos[pedidos["RC"].astype(str) == rc_input].copy()
                identificador = f"RC {rc_input}"
        else:
            coordenadores_lista = sorted(pedidos["Coordenador"].dropna().astype(str).unique().tolist()) if "Coordenador" in pedidos.columns else []
            col_coord, col_btn, _ = st.columns([3,1,4])
            with col_coord:
                if coordenadores_lista:
                    coord_input = st.selectbox("COORDENADOR DE VENDAS", options=[""] + coordenadores_lista)
                else:
                    coord_input = st.text_input("COORDENADOR DE VENDAS", placeholder="Digite o nome")
            with col_btn:
                st.markdown("<div style='margin-top:28px;'></div>", unsafe_allow_html=True)
                st.button("Buscar", use_container_width=True, key="btn_buscar_coord")
            if coord_input and coord_input != "" and "Coordenador" in pedidos.columns:
                base = pedidos[pedidos["Coordenador"].astype(str) == coord_input].copy()
                identificador = f"Coordenador: {coord_input}"

    # =========================
    # PROCESSAMENTO
    # =========================
    if not base.empty:

        if "RC" in base.columns:
            base = base.drop(columns=["RC"])

        base = base.rename(columns={"Pedido2": "Qtde", "Soma de Valor": "Valor (R$)"})

        for col in ["Valor (R$)", "Soma de Valores"]:
            if col in base.columns:
                base[col] = base[col].apply(formatar_moeda)

        if "Previsão" in base.columns:
            base["Previsão"] = base["Previsão"].apply(formatar_data)

        # ══════════════════════════════════════════
        # SIDEBAR — FILTROS
        # FIX 1: logo e info do usuário sem repetição
        # FIX 2: filtro CNPJ com máscara via components.html
        # ══════════════════════════════════════════
        st.sidebar.image("download.png", width=170)
        st.sidebar.header("🔎 Filtros")

        # Status
        status_list = sorted(base["Status"].dropna().unique()) if "Status" in base.columns else []
        status = st.sidebar.selectbox("Status", ["Todos"] + status_list)
        df1 = base[base["Status"] == status].copy() if status != "Todos" else base.copy()

        # Motivo
        motivo_list = sorted(df1["Motivo"].dropna().unique()) if "Motivo" in df1.columns else []
        motivo = st.sidebar.selectbox("Motivo", ["Todos"] + motivo_list)
        df2 = df1[df1["Motivo"] == motivo].copy() if motivo != "Todos" else df1.copy()

        # Cliente
        cliente = st.sidebar.text_input("Cliente (buscar)", key="sb_cliente")
        df3 = df2[df2["Cliente"].str.contains(cliente, case=False, na=False)].copy() if cliente else df2.copy()

        # CNPJ com máscara automática via JS embutido em components.html
        # Usamos session_state para guardar o valor formatado
        if "cnpj_filtro" not in st.session_state:
            st.session_state.cnpj_filtro = ""

        cnpj_html = f"""
        <style>
        #cnpj_input {{
            width: 100%;
            padding: 8px 12px;
            border: 1px solid #d1d5db;
            border-radius: 8px;
            font-size: 14px;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            box-sizing: border-box;
            outline: none;
        }}
        #cnpj_input:focus {{ border-color: #c00000; box-shadow: 0 0 0 2px rgba(192,0,0,0.1); }}
        label {{ font-size:14px; font-weight:600; color:#374151; display:block; margin-bottom:6px; }}
        </style>
        <label>CNPJ (buscar)</label>
        <input id="cnpj_input" type="text" maxlength="18" placeholder="00.000.000/0000-00"
               value="{st.session_state.cnpj_filtro}" />
        <script>
        const input = document.getElementById('cnpj_input');

        function mask(v) {{
            v = v.replace(/\\D/g,'');
            if (v.length > 14) v = v.slice(0,14);
            let r = '';
            if (v.length > 0)  r += v.slice(0,2);
            if (v.length > 2)  r += '.' + v.slice(2,5);
            if (v.length > 5)  r += '.' + v.slice(5,8);
            if (v.length > 8)  r += '/' + v.slice(8,12);
            if (v.length > 12) r += '-' + v.slice(12,14);
            return r;
        }}
        
        input.addEventListener('change', function() {
            this.value = mask(this.value);
        
            const url = new URL(window.location.href);
            url.searchParams.set('cnpj_filtro', this.value);
        
            window.location.href = url.toString();
        }});
        </script>
        """
        st.sidebar.components_placeholder = st.sidebar.empty()
        with st.sidebar:
            components.html(cnpj_html, height=70)

        # Lê CNPJ digitado via query params (fallback: session_state)
        cnpj_raw = st.query_params.get("cnpj_filtro", "")
        if cnpj_raw:
            st.session_state.cnpj_filtro = cnpj_raw

        # Aplica filtro CNPJ
        df4 = df3.copy()
        if cnpj_raw.strip() and "CNPJ" in df4.columns:
            digits_busca = cnpj_raw.replace(".","").replace("/","").replace("-","").strip()
            df4 = df4[df4["CNPJ"].str.replace(".","",regex=False).str.replace("/","",regex=False).str.replace("-","",regex=False).str.contains(digits_busca, na=False)]

        pedidos_view = df4.copy()

        # FIX: info do usuário aparece apenas UMA vez, no final da sidebar
        st.sidebar.markdown("---")
        st.sidebar.markdown(f"👤 **{usuario_logado}**  \n*{st.session_state.get('tipo_usuario','')}*")

        # FIX: aviso se filtros não retornaram resultados
        if pedidos_view.empty:
            st.warning("⚠️ Nenhum pedido encontrado com os filtros aplicados. Tente outros critérios.")
            return

        # =========================
        # VALORES NUMÉRICOS
        # =========================
        pedidos_view["Valor_num"] = pedidos_view["Valor (R$)"].apply(para_float)

        total_pedidos  = len(pedidos_view)
        valor_total    = pedidos_view["Valor_num"].sum()
        valor_liberado = pedidos_view[pedidos_view["Status"].astype(str).str.lower().str.contains("liberado")]["Valor_num"].sum()
        valor_critico  = pedidos_view[pedidos_view["Motivo"].astype(str).str.lower().isin(["estoque","ag retorno comercial"])]["Valor_num"].sum()
        valor_pendente = pedidos_view[pedidos_view["Status"].astype(str).str.lower() == "pendente"]["Valor_num"].sum()
        valor_batch    = pedidos_view[pedidos_view["Status"].astype(str).str.lower() == "batch"]["Valor_num"].sum()

        # =========================
        # KPI CARDS
        # =========================
        k1,k2,k3,k4,k5,k6 = st.columns(6)
        with k1: st.markdown(f"<div class='kpi-card'><div style='font-size:18px;margin-bottom:4px;'>📦</div><div style='font-size:20px;font-weight:700;color:#111827;line-height:1;'>{total_pedidos}</div><div style='font-size:12px;color:#6b7280;margin-top:6px;'>Pedido(s)</div></div>", unsafe_allow_html=True)
        with k2: st.markdown(f"<div class='kpi-card'><div style='font-size:18px;margin-bottom:4px;'>🏅</div><div style='font-size:20px;font-weight:700;color:#111827;line-height:1;'>{formatar_moeda(valor_total)}</div><div style='font-size:12px;color:#6b7280;margin-top:6px;'>Valor Total</div></div>", unsafe_allow_html=True)
        with k3: st.markdown(f"<div class='kpi-card'><div style='font-size:18px;margin-bottom:4px;'><span style='color:#16a34a;'>●</span></div><div style='font-size:20px;font-weight:700;color:#16a34a;line-height:1;'>{formatar_moeda(valor_liberado)}</div><div style='font-size:12px;color:#6b7280;margin-top:6px;'>Valor Liberado</div></div>", unsafe_allow_html=True)
        with k4: st.markdown(f"<div class='kpi-card'><div style='font-size:18px;margin-bottom:4px;'><span style='color:#dc2626;'>●</span></div><div style='font-size:20px;font-weight:700;color:#dc2626;line-height:1;'>{formatar_moeda(valor_critico)}</div><div style='font-size:12px;color:#6b7280;margin-top:6px;'>Estoque / Ag. Retorno Comercial</div></div>", unsafe_allow_html=True)
        with k5: st.markdown(f"<div class='kpi-card'><div style='font-size:18px;margin-bottom:4px;'><span style='color:#d97706;'>●</span></div><div style='font-size:20px;font-weight:700;color:#d97706;line-height:1;'>{formatar_moeda(valor_pendente)}</div><div style='font-size:12px;color:#6b7280;margin-top:6px;'>Aguardando Atendimento</div></div>", unsafe_allow_html=True)
        with k6: st.markdown(f"<div class='kpi-card'><div style='font-size:18px;margin-bottom:4px;'><span style='color:#7c3aed;'>●</span></div><div style='font-size:20px;font-weight:700;color:#7c3aed;line-height:1;'>{formatar_moeda(valor_batch)}</div><div style='font-size:12px;color:#6b7280;margin-top:6px;'>Batch</div></div>", unsafe_allow_html=True)

        st.markdown("<div style='margin-top:20px;'></div>", unsafe_allow_html=True)

        # =========================
        # ABAS PRINCIPAIS
        # =========================
        tab1, tab2 = st.tabs(["📊 Visão Geral", f"📦 Pedidos  {total_pedidos}"])

        # ─────────────────────────────────────────
        # ABA 1 — VISÃO GERAL
        # ─────────────────────────────────────────
        with tab1:
            motivo_top   = pedidos_view.groupby("Motivo")["Valor_num"].sum().sort_values(ascending=False)
            motivo_nome  = motivo_top.index[0] if len(motivo_top) > 0 else "-"
            motivo_valor = motivo_top.iloc[0]  if len(motivo_top) > 0 else 0
            pct_motivo   = (motivo_valor/valor_total*100) if valor_total > 0 else 0
            pct_liberado = (valor_liberado/valor_total*100) if valor_total > 0 else 0
            n_lib        = len(pedidos_view[pedidos_view["Status"].astype(str).str.lower().str.contains("liberado")])

            ins1,ins2 = st.columns(2)
            with ins1:
                st.markdown(f"""<div style="background:#eff6ff;border:1px solid #bfdbfe;border-radius:12px;padding:14px 18px;margin-bottom:16px;">
                    <div style="font-size:13px;font-weight:700;color:#1d4ed8;margin-bottom:4px;">📉 Concentração: "{motivo_nome}"</div>
                    <div style="font-size:13px;color:#2563eb;">Representa {pct_motivo:.0f}% do valor total ({formatar_moeda(motivo_valor)})</div>
                </div>""", unsafe_allow_html=True)
            with ins2:
                st.markdown(f"""<div style="background:#f0fdf4;border:1px solid #86efac;border-radius:12px;padding:14px 18px;margin-bottom:16px;">
                    <div style="font-size:13px;font-weight:700;color:#15803d;margin-bottom:4px;">✅ {pct_liberado:.0f}% dos pedidos estão liberados</div>
                    <div style="font-size:13px;color:#16a34a;">{n_lib} de {total_pedidos} pedidos prontos</div>
                </div>""", unsafe_allow_html=True)

            st.markdown("""<style>
            [data-testid="stVerticalBlock"] div[data-testid="stVerticalBlock"]:has(> [data-testid="stPlotlyChart"]) {
                background:white;border:1px solid #e5e7eb;border-radius:30px;
                padding:16px;box-shadow:0 1px 4px rgba(0,0,0,0.05);margin-bottom:16px;
            }</style>""", unsafe_allow_html=True)

            g1,g2 = st.columns(2)
            with g1:
                with st.container():
                    sc = pedidos_view.groupby("Status").size().reset_index(name="Quantidade")
                    cm = {"Pendente":"#f59e0b","Conferido":"#3b82f6","Liberado":"#22c55e","Batch":"#7c3aed"}
                    fig = go.Figure(go.Pie(labels=sc["Status"],values=sc["Quantidade"],hole=0.6,
                        marker_colors=[cm.get(s,"#9ca3af") for s in sc["Status"]],
                        marker=dict(line=dict(color="white",width=2)),textinfo="percent",textfont_size=12))
                    fig.update_layout(title=dict(text="DISTRIBUIÇÃO POR STATUS",font=dict(size=11,color="#9ca3af"),x=0.01,xanchor="left"),
                        height=320,margin=dict(l=10,r=10,t=40,b=10),showlegend=True,
                        legend=dict(orientation="h",yanchor="top",y=-0.05,xanchor="center",x=0.5,font=dict(size=11)),
                        paper_bgcolor="white",plot_bgcolor="white")
                    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})

            with g2:
                with st.container():
                    mc = pedidos_view.groupby("Motivo")["Valor_num"].sum().reset_index().sort_values("Valor_num",ascending=False)
                    pal = ["#ef4444","#f97316","#eab308","#22c55e","#3b82f6","#8b5cf6","#ec4899","#14b8a6"]
                    fig2 = go.Figure()
                    for i,row in mc.iterrows():
                        fig2.add_trace(go.Bar(x=[row["Motivo"]],y=[row["Valor_num"]],name=row["Motivo"],
                            marker=dict(color=pal[i%len(pal)],cornerradius=8,line=dict(width=0)),showlegend=False))
                    fig2.update_layout(title=dict(text="VALOR POR MOTIVO",font=dict(size=11,color="#9ca3af"),x=0.01,xanchor="left"),
                        height=320,margin=dict(l=10,r=10,t=40,b=80),xaxis_title="",yaxis_title="",
                        paper_bgcolor="white",plot_bgcolor="white",bargap=0.4,
                        xaxis=dict(tickfont=dict(size=10),tickangle=-30,showgrid=False,zeroline=False,showline=False),
                        yaxis=dict(tickfont=dict(size=10),gridcolor="#f3f4f6",showline=False,zeroline=False),shapes=[])
                    st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar":False})

            g3,g4 = st.columns(2)
            with g3:
                with st.container():
                    uf = pedidos_view.groupby("UF")["Valor_num"].sum().reset_index().sort_values("Valor_num",ascending=True)
                    mx = uf["Valor_num"].max() if len(uf)>0 else 1
                    cores_uf = ["#dc2626" if v/mx>0.66 else "#f87171" if v/mx>0.33 else "#fca5a5" for v in uf["Valor_num"]]
                    fig3 = go.Figure()
                    for i,row in uf.iterrows():
                        fig3.add_trace(go.Bar(y=[row["UF"]],x=[row["Valor_num"]],orientation="h",name=row["UF"],
                            marker=dict(color=cores_uf[list(uf.index).index(i)],cornerradius=8,line=dict(width=0)),showlegend=False))
                    fig3.update_layout(title=dict(text="VALOR POR ESTADO (UF)",font=dict(size=11,color="#9ca3af"),x=0.01,xanchor="left"),
                        height=320,margin=dict(l=10,r=10,t=40,b=10),paper_bgcolor="white",plot_bgcolor="white",bargap=0.4,
                        xaxis=dict(tickfont=dict(size=10),gridcolor="#f3f4f6",showline=False,zeroline=False),
                        yaxis=dict(tickfont=dict(size=11),showgrid=False,showline=False,zeroline=False),shapes=[])
                    st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar":False})

            with g4:
                with st.container():
                    est = pedidos_view[pedidos_view["Motivo"].astype(str).str.strip().str.lower()=="estoque"].copy()
                    if not est.empty and "Previsão" in est.columns:
                        def classifica(prev):
                            v = str(prev).strip()
                            if v.lower()=="futuro": return "Futuro"
                            try:
                                if pd.notna(pd.to_datetime(v,dayfirst=True,errors="raise")): return "Mês Atual"
                            except: pass
                            return "Outros"
                        est["Tipo"] = est["Previsão"].apply(classifica)
                        eg = est.groupby("Tipo").size().reset_index(name="Qtde")
                        ordem = ["Mês Atual","Futuro","Outros"]
                        eg["Tipo"] = pd.Categorical(eg["Tipo"],categories=ordem,ordered=True)
                        eg = eg.sort_values("Tipo")
                        ce = {"Mês Atual":"#f9a8d4","Futuro":"#dc2626","Outros":"#d1d5db"}
                        fig4 = go.Figure()
                        for _,row in eg.iterrows():
                            fig4.add_trace(go.Bar(x=[str(row["Tipo"])],y=[row["Qtde"]],name=str(row["Tipo"]),
                                text=[str(int(row["Qtde"]))],textposition="outside",textfont=dict(size=13,color="#374151"),
                                marker=dict(color=ce.get(str(row["Tipo"]),"#d1d5db"),cornerradius=8,line=dict(width=0)),showlegend=False))
                        fig4.update_layout(title=dict(text="ESTOQUE - PREVISÃO POR MÊS",font=dict(size=11,color="#9ca3af"),x=0.01,xanchor="left"),
                            height=320,margin=dict(l=10,r=10,t=40,b=10),paper_bgcolor="white",plot_bgcolor="white",bargap=0.5,
                            xaxis=dict(tickfont=dict(size=12),showgrid=False,showline=False,zeroline=False),
                            yaxis=dict(tickfont=dict(size=10),gridcolor="#f3f4f6",showline=False,zeroline=False),shapes=[])
                        st.plotly_chart(fig4, use_container_width=True, config={"displayModeBar":False})
                    else:
                        st.info("Nenhum pedido com Motivo 'Estoque' encontrado.")

            # Top clientes
            tc = pedidos_view.groupby("Cliente").agg(Valor=("Valor_num","sum"),Pedidos=("Pedido","count")).sort_values("Valor",ascending=False).head(8).reset_index()
            if not tc.empty:
                mx2 = tc["Valor"].max()
                rows_top = ""
                for idx,row in tc.reset_index(drop=True).iterrows():
                    pct = int((row["Valor"]/mx2)*100) if mx2>0 else 0
                    nc  = str(row["Cliente"])[:45]+("..." if len(str(row["Cliente"]))>45 else "")
                    rows_top += (
                        f'<div style="display:flex;align-items:center;gap:12px;padding:9px 0;border-bottom:1px solid #f3f4f6;">'
                        f'<div style="font-size:12px;font-weight:700;color:#9ca3af;width:20px;text-align:right;">{idx+1}</div>'
                        f'<div style="flex:1;min-width:0;"><div style="font-size:13px;color:#111827;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{nc}</div>'
                        f'<div style="margin-top:4px;background:#fee2e2;border-radius:999px;height:5px;">'
                        f'<div style="background:#dc2626;border-radius:999px;height:5px;width:{pct}%;"></div></div></div>'
                        f'<div style="text-align:right;min-width:90px;"><div style="font-size:12px;color:#6b7280;">{int(row["Pedidos"])} ped.</div>'
                        f'<div style="font-size:13px;font-weight:700;color:#111827;">{formatar_moeda_curto(row["Valor"])}</div></div></div>'
                    )
                st.markdown(f'<div style="background:white;border:1px solid #e5e7eb;border-radius:12px;padding:16px 20px;box-shadow:0 1px 4px rgba(0,0,0,0.05);margin-bottom:16px;"><div style="font-size:11px;font-weight:700;color:#9ca3af;letter-spacing:0.08em;text-transform:uppercase;margin-bottom:8px;">👤 Top Clientes por Valor</div>{rows_top}</div>', unsafe_allow_html=True)
            else:
                st.info("Sem dados de clientes.")

        # ─────────────────────────────────────────
        # ABA 2 — PEDIDOS
        # ─────────────────────────────────────────
        with tab2:
            st.markdown("<div style='margin-top:12px;'></div>", unsafe_allow_html=True)

            n_todos      = len(pedidos_view)
            n_pendentes  = len(pedidos_view[pedidos_view["Status"].str.lower()=="pendente"])
            n_liberados  = len(pedidos_view[pedidos_view["Status"].str.lower()=="liberado"])
            n_conferidos = len(pedidos_view[pedidos_view["Status"].str.lower()=="conferido"])
            n_batch      = len(pedidos_view[pedidos_view["Status"].str.lower()=="batch"])

            ft1,ft2,ft3,ft4,ft5 = st.tabs([
                f"Todos  {n_todos}", f"Pendentes  {n_pendentes}",
                f"Liberados  {n_liberados}", f"Conferidos  {n_conferidos}", f"Batch  {n_batch}",
            ])

            def renderizar_tabela(df_filtrado):
                df_show   = df_filtrado.drop(columns=["Valor_num","Pedido_Cliente"], errors="ignore")
                tem_cnpj  = "CNPJ" in df_show.columns
                html = """
                <style>
                *{box-sizing:border-box;}
                body{margin:0;padding:0;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;}
                table{width:100%;border-collapse:collapse;background:white;}
                thead tr{background:#f9fafb;border-bottom:2px solid #e5e7eb;}
                th{padding:10px 14px;text-align:left;font-size:11px;font-weight:700;color:#6b7280;text-transform:uppercase;letter-spacing:0.05em;white-space:nowrap;}
                td{padding:10px 14px;border-bottom:1px solid #f3f4f6;font-size:13px;color:#111827;vertical-align:middle;}
                tr:hover td{background:#f9fafb;}
                .ped{font-weight:700;color:#c00000;} .val{font-weight:600;color:#166534;}
                .mot{font-weight:600;color:#d97706;} .prev{font-weight:700;color:#374151;}
                .cnpj{font-size:12px;color:#6b7280;white-space:nowrap;}
                .badge-lib  {background:#dcfce7;color:#166534;padding:3px 10px;border-radius:999px;font-size:11px;font-weight:600;white-space:nowrap;}
                .badge-conf {background:#dbeafe;color:#1d4ed8;padding:3px 10px;border-radius:999px;font-size:11px;font-weight:600;white-space:nowrap;}
                .badge-pend {background:#fef9c3;color:#92400e;padding:3px 10px;border-radius:999px;font-size:11px;font-weight:600;white-space:nowrap;}
                .badge-batch{background:#f3e8ff;color:#7c3aed;padding:3px 10px;border-radius:999px;font-size:11px;font-weight:600;white-space:nowrap;}
                </style>
                <table><thead><tr>
                <th>Pedido</th><th>Cliente</th>"""
                if tem_cnpj: html += "<th>CNPJ</th>"
                html += "<th>UF</th><th>Status</th><th>Motivo</th><th>Previsão</th><th>Valor (R$)</th></tr></thead><tbody>"

                for _,row in df_show.iterrows():
                    s = str(row.get("Status","")).strip().lower()
                    badge = (f"<span class='badge-lib'>{row['Status']}</span>"   if s=="liberado"  else
                             f"<span class='badge-conf'>{row['Status']}</span>"  if s=="conferido" else
                             f"<span class='badge-batch'>{row['Status']}</span>" if s=="batch"     else
                             f"<span class='badge-pend'>{row['Status']}</span>")
                    html += f"<tr><td class='ped'>{row.get('Pedido','')}</td><td>{row.get('Cliente','')}</td>"
                    if tem_cnpj: html += f"<td class='cnpj'>{row.get('CNPJ','')}</td>"
                    html += f"<td>{row.get('UF','')}</td><td>{badge}</td><td class='mot'>{row.get('Motivo','')}</td><td class='prev'>{row.get('Previsão','')}</td><td class='val'>{row.get('Valor (R$)','')}</td></tr>"

                html += "</tbody></table>"
                qtd = len(df_filtrado)
                components.html(html, height=min((qtd*46)+52,420), scrolling=qtd>8)

            with ft1: renderizar_tabela(pedidos_view)
            with ft2: renderizar_tabela(pedidos_view[pedidos_view["Status"].str.lower()=="pendente"])
            with ft3: renderizar_tabela(pedidos_view[pedidos_view["Status"].str.lower()=="liberado"])
            with ft4: renderizar_tabela(pedidos_view[pedidos_view["Status"].str.lower()=="conferido"])
            with ft5: renderizar_tabela(pedidos_view[pedidos_view["Status"].str.lower()=="batch"])

            st.markdown("<div style='margin-top:16px;'></div>", unsafe_allow_html=True)

            # ── Detalhe pedido ──
            pedidos_view["Pedido_Cliente"] = pedidos_view["Pedido"].astype(str) + " - " + pedidos_view["Cliente"].astype(str)
            pedido_escolha = st.selectbox("📌 Selecione um pedido para ver detalhes:", [""] + pedidos_view["Pedido_Cliente"].tolist())

            if pedido_escolha != "":
                pedido_numero = pedido_escolha.split(" - ")[0]
                pedido_info   = pedidos_view[pedidos_view["Pedido"].astype(str)==pedido_numero].iloc[0]
                badge_ped     = badge_status(pedido_info.get("Status",""))
                cnpj_fmt      = pedido_info.get("CNPJ","") if "CNPJ" in pedido_info.index else ""

                st.markdown("<div style='margin-top:12px;'></div>", unsafe_allow_html=True)
                st.markdown(f"""
                <div style="background:white;border:1px solid #e5e7eb;border-left:5px solid #c00000;
                    border-radius:12px;padding:18px 22px;margin-bottom:18px;box-shadow:0 1px 4px rgba(0,0,0,0.05);">
                    <div style="font-size:11px;font-weight:700;color:#9ca3af;letter-spacing:0.08em;text-transform:uppercase;margin-bottom:6px;">Pedido Selecionado</div>
                    <div style="display:flex;align-items:center;gap:12px;flex-wrap:wrap;">
                        <div style="font-size:32px;font-weight:800;color:#111827;">#{pedido_info['Pedido']}</div>
                        <div>{badge_ped}</div>
                    </div>
                    <div style="font-size:13px;color:#6b7280;margin-top:10px;display:flex;gap:24px;flex-wrap:wrap;">
                        <span><b style="color:#374151;">Cliente:</b> {pedido_info['Cliente']}</span>
                        {"<span><b style='color:#374151;'>CNPJ:</b> "+str(cnpj_fmt)+"</span>" if cnpj_fmt else ""}
                        <span><b style="color:#374151;">Valor:</b> {pedido_info['Valor (R$)']}</span>
                        <span><b style="color:#374151;">Previsão:</b> {pedido_info.get('Previsão','')}</span>
                        <span><b style="color:#374151;">Motivo:</b> {pedido_info.get('Motivo','')}</span>
                    </div>
                </div>""", unsafe_allow_html=True)

                # Itens
                st.markdown("<div style='font-size:14px;font-weight:700;color:#111827;margin-bottom:10px;'>📦 Itens do Pedido</div>", unsafe_allow_html=True)
                itens_pedido = itens[itens["Pedido"].astype(str)==pedido_numero].copy()
                itens_pedido = itens_pedido.drop(columns=[c for c in ["RC","Pedido"] if c in itens_pedido.columns])

                if not itens_pedido.empty:
                    itens_pedido = itens_pedido.rename(columns={"Codigo":"Código","Descricao":"Descrição","Pedido2":"Qtde","Soma de Valor":"Valor (R$)"})
                    if "Previsão Final" in itens_pedido.columns:
                        itens_pedido["Previsão Final"] = itens_pedido["Previsão Final"].apply(formatar_data).replace("NaT","")
                    if "Valor (R$)" in itens_pedido.columns:
                        itens_pedido["Valor (R$)"] = itens_pedido["Valor (R$)"].apply(formatar_moeda)

                    hi = """<style>*{box-sizing:border-box;}body{margin:0;padding:0;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;}
                    table{width:100%;border-collapse:collapse;background:white;}thead tr{background:#f9fafb;border-bottom:2px solid #e5e7eb;}
                    th{padding:10px 14px;text-align:left;font-size:11px;font-weight:700;color:#6b7280;text-transform:uppercase;letter-spacing:0.05em;}
                    td{padding:10px 14px;border-bottom:1px solid #f3f4f6;font-size:13px;color:#111827;vertical-align:middle;}tr:hover td{background:#f9fafb;}
                    .badge-res{background:#dcfce7;color:#166534;padding:3px 10px;border-radius:999px;font-size:11px;font-weight:600;}
                    .badge-sal{background:#fee2e2;color:#991b1b;padding:3px 10px;border-radius:999px;font-size:11px;font-weight:600;}
                    </style><table><thead><tr>"""
                    for col in itens_pedido.columns: hi += f"<th>{col}</th>"
                    hi += "</tr></thead><tbody>"
                    for _,row in itens_pedido.iterrows():
                        hi += "<tr>"
                        for col in itens_pedido.columns:
                            val = row[col]
                            if col=="Status Reserva":
                                val = f"<span class='badge-res'>{val}</span>" if str(val).strip().lower()=="reservado" else f"<span class='badge-sal'>{val}</span>"
                            hi += f"<td>{val}</td>"
                        hi += "</tr>"
                    hi += "</tbody></table>"
                    qtd_i = len(itens_pedido)
                    components.html(hi, height=min((qtd_i*46)+52,420), scrolling=qtd_i>8)
                else:
                    st.info("Nenhum item encontrado para este pedido.")

                st.markdown("<div style='margin-top:16px;'></div>", unsafe_allow_html=True)

                # Ação recomendada
                st.markdown("<div style='font-size:14px;font-weight:700;color:#111827;margin-bottom:10px;'>💡 Ação Recomendada</div>", unsafe_allow_html=True)
                acoes_pedido = acoes[acoes["Pedido"].astype(str)==pedido_numero]
                if not acoes_pedido.empty:
                    texto = limpar_texto(acoes_pedido.iloc[0]["Texto"])
                    st.markdown(f"""<div style="background:#fffbeb;border:1px solid #fde68a;border-left:5px solid #f59e0b;
                        padding:14px 18px;border-radius:10px;line-height:1.7;white-space:pre-line;font-size:14px;color:#111827;">
                        {texto}</div>""", unsafe_allow_html=True)
                else:
                    st.info("Nenhuma ação cadastrada para este pedido.")

    else:
        if filtro_tipo == "RC":
            st.warning(f"Nenhum pedido encontrado para o RC {filtro_valor}.")
        elif filtro_tipo == "COORDENADOR":
            st.warning(f"Nenhum pedido encontrado para o Coordenador {filtro_valor}.")

# ─────────────────────────────────────────
            # ITENS EM RUPTURA E PREVISÕES
            # ─────────────────────────────────────────

            # Filtra pedidos com motivo "Estoque" (ruptura de estoque)
            ruptura_df = pedidos_view[
                pedidos_view["Motivo"].astype(str).str.strip().str.lower() == "estoque"
            ].copy()

            if not ruptura_df.empty:

                # Cruza com itens para pegar os produtos em ruptura
                ruptura_itens = itens[
                    itens["Pedido"].astype(str).isin(ruptura_df["Pedido"].astype(str))
                ].copy()

                if not ruptura_itens.empty:

                    # Agrupa por código/descrição e previsão
                    col_cod  = "Codigo"    if "Codigo"    in ruptura_itens.columns else None
                    col_desc = "Descricao" if "Descricao" in ruptura_itens.columns else None
                    col_prev = "Previsão Final" if "Previsão Final" in ruptura_itens.columns else (
                               "Previsão"      if "Previsão"       in ruptura_itens.columns else None)
                    col_qtd  = "Pedido2"   if "Pedido2"   in ruptura_itens.columns else None
                    col_val  = "Soma de Valor" if "Soma de Valor" in ruptura_itens.columns else None

                    # Formata previsão
                    if col_prev:
                        ruptura_itens["_prev_fmt"] = ruptura_itens[col_prev].apply(formatar_data).replace("", "Sem previsão")
                        ruptura_itens["_prev_fmt"] = ruptura_itens["_prev_fmt"].replace("NaT", "Sem previsão").fillna("Sem previsão")
                    else:
                        ruptura_itens["_prev_fmt"] = "Sem previsão"

                    # Classifica por urgência de previsão
                    hoje = pd.Timestamp.today().normalize()
                    def urgencia(prev_str):
                        try:
                            d = pd.to_datetime(prev_str, dayfirst=True, errors="coerce")
                            if pd.isna(d): return "Sem Previsão"
                            diff = (d - hoje).days
                            if diff < 0:   return "Atrasado"
                            elif diff <= 7: return "Urgente (≤7 dias)"
                            elif diff <= 30: return "Próximo (≤30 dias)"
                            else:           return "Futuro (>30 dias)"
                        except:
                            return "Sem Previsão"

                    ruptura_itens["_urgencia"] = ruptura_itens["_prev_fmt"].apply(urgencia)

                    # ── Gráfico de barras: Top itens em ruptura por qtde de pedidos ──
                    if col_cod and col_desc:
                        ruptura_itens["_label"] = (
                            ruptura_itens[col_cod].astype(str).str.strip() + " – " +
                            ruptura_itens[col_desc].astype(str).str[:30]
                        )
                    elif col_desc:
                        ruptura_itens["_label"] = ruptura_itens[col_desc].astype(str).str[:40]
                    else:
                        ruptura_itens["_label"] = ruptura_itens[col_cod].astype(str) if col_cod else "Item"

                    # Agrupa para o gráfico (Top 10 itens mais bloqueados)
                    agg_item = ruptura_itens.groupby("_label").agg(
                        Pedidos=("Pedido", "nunique"),
                        Valor=(col_val, "sum") if col_val else ("_label", "count"),
                    ).sort_values("Pedidos", ascending=False).head(10).reset_index()

                    # Agrupa por urgência para o gráfico de pizza
                    agg_urg = ruptura_itens.groupby("_urgencia").agg(
                        Qtde=("_label", "count")
                    ).reset_index()

                    # ── Layout: dois gráficos lado a lado ──
                    gr1, gr2 = st.columns(2)

                    with gr1:
                        with st.container():
                            cores_rup = ["#dc2626","#f97316","#eab308","#6b7280","#ef4444",
                                         "#f87171","#fca5a5","#fcd34d","#9ca3af","#374151"]
                            fig_rup = go.Figure()
                            for i, row in agg_item.iterrows():
                                fig_rup.add_trace(go.Bar(
                                    y=[row["_label"]], x=[row["Pedidos"]],
                                    orientation="h", name=row["_label"],
                                    text=[str(int(row["Pedidos"]))], textposition="outside",
                                    textfont=dict(size=11, color="#374151"),
                                    marker=dict(color=cores_rup[i % len(cores_rup)], cornerradius=6, line=dict(width=0)),
                                    showlegend=False,
                                ))
                            fig_rup.update_layout(
                                title=dict(text="🔴 TOP ITENS EM RUPTURA (por pedidos bloqueados)",
                                           font=dict(size=11, color="#9ca3af"), x=0.01, xanchor="left"),
                                height=340, margin=dict(l=10, r=30, t=40, b=10),
                                paper_bgcolor="white", plot_bgcolor="white", bargap=0.35,
                                xaxis=dict(tickfont=dict(size=10), gridcolor="#f3f4f6",
                                           showline=False, zeroline=False),
                                yaxis=dict(tickfont=dict(size=10), showgrid=False,
                                           showline=False, zeroline=False, automargin=True),
                            )
                            st.plotly_chart(fig_rup, use_container_width=True, config={"displayModeBar": False})

                    with gr2:
                        with st.container():
                            cor_urg = {
                                "Atrasado":         "#dc2626",
                                "Urgente (≤7 dias)": "#f97316",
                                "Próximo (≤30 dias)":"#eab308",
                                "Futuro (>30 dias)": "#22c55e",
                                "Sem Previsão":      "#9ca3af",
                            }
                            fig_urg = go.Figure(go.Pie(
                                labels=agg_urg["_urgencia"],
                                values=agg_urg["Qtde"],
                                hole=0.58,
                                marker_colors=[cor_urg.get(u, "#d1d5db") for u in agg_urg["_urgencia"]],
                                marker=dict(line=dict(color="white", width=2)),
                                textinfo="percent+label",
                                textfont_size=11,
                            ))
                            fig_urg.update_layout(
                                title=dict(text="📅 PREVISÃO DE RETORNO — RUPTURA",
                                           font=dict(size=11, color="#9ca3af"), x=0.01, xanchor="left"),
                                height=340, margin=dict(l=10, r=10, t=40, b=10),
                                showlegend=True,
                                legend=dict(orientation="h", yanchor="top", y=-0.08,
                                            xanchor="center", x=0.5, font=dict(size=10)),
                                paper_bgcolor="white", plot_bgcolor="white",
                            )
                            st.plotly_chart(fig_urg, use_container_width=True, config={"displayModeBar": False})

                    # ── Tabela resumo: itens em ruptura com previsão ──
                    cols_show = ["_label", "_prev_fmt", "_urgencia"]
                    if col_qtd: cols_show.insert(2, col_qtd)

                    tabela_rup = ruptura_itens[cols_show].copy()
                    tabela_rup.columns = (
                        ["Item", "Qtde Pedida", "Previsão", "Urgência"] if col_qtd
                        else ["Item", "Previsão", "Urgência"]
                    )

                    # Ordena: Atrasado > Urgente > Próximo > Futuro > Sem Previsão
                    ordem_urg = {"Atrasado": 0, "Urgente (≤7 dias)": 1,
                                 "Próximo (≤30 dias)": 2, "Futuro (>30 dias)": 3, "Sem Previsão": 4}
                    tabela_rup["_ord"] = tabela_rup["Urgência"].map(ordem_urg).fillna(5)
                    tabela_rup = tabela_rup.sort_values("_ord").drop(columns=["_ord"]).head(30)

                    badge_urg = {
                        "Atrasado":          ("background:#fee2e2;color:#991b1b", "Atrasado"),
                        "Urgente (≤7 dias)": ("background:#fff7ed;color:#c2410c", "Urgente ≤7d"),
                        "Próximo (≤30 dias)":("background:#fefce8;color:#92400e", "Próximo ≤30d"),
                        "Futuro (>30 dias)": ("background:#f0fdf4;color:#166534", "Futuro"),
                        "Sem Previsão":      ("background:#f3f4f6;color:#6b7280", "Sem Previsão"),
                    }

                    html_rup = """
                    <style>
                    *{box-sizing:border-box;}
                    body{margin:0;padding:0;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;}
                    table{width:100%;border-collapse:collapse;background:white;}
                    thead tr{background:#f9fafb;border-bottom:2px solid #e5e7eb;position:sticky;top:0;z-index:10;}
                    th{padding:10px 14px;text-align:left;font-size:11px;font-weight:700;color:#6b7280;text-transform:uppercase;letter-spacing:0.05em;}
                    td{padding:9px 14px;border-bottom:1px solid #f3f4f6;font-size:13px;color:#111827;vertical-align:middle;}
                    tr:hover td{background:#fafafa;}
                    .bdg{padding:3px 10px;border-radius:999px;font-size:11px;font-weight:600;white-space:nowrap;}
                    </style>
                    <table><thead><tr>"""

                    for col in tabela_rup.columns:
                        html_rup += f"<th>{col}</th>"
                    html_rup += "</tr></thead><tbody>"

                    for _, row in tabela_rup.iterrows():
                        html_rup += "<tr>"
                        for col in tabela_rup.columns:
                            val = row[col]
                            if col == "Urgência":
                                style, label = badge_urg.get(str(val), ("background:#f3f4f6;color:#6b7280", str(val)))
                                html_rup += f"<td><span class='bdg' style='{style}'>{label}</span></td>"
                            else:
                                html_rup += f"<td>{val}</td>"
                        html_rup += "</tr>"

                    html_rup += "</tbody></table>"

                    n_rup = len(tabela_rup)
                    st.markdown("""
                    <div style='font-size:11px;font-weight:700;color:#9ca3af;letter-spacing:0.08em;
                        text-transform:uppercase;margin:8px 0 6px;'>
                        📋 Itens em Ruptura — Detalhe por Previsão
                    </div>""", unsafe_allow_html=True)
                    components.html(html_rup, height=min((n_rup * 44) + 52, 400), scrolling=n_rup > 8)

                else:
                    st.info("Nenhum item de ruptura encontrado na base de itens.")
            else:
                st.info("Não há pedidos bloqueados por 'Estoque' (ruptura) no momento.")

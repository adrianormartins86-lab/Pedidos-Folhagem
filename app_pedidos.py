import streamlit as st
import pandas as pd
import io
from streamlit_gsheets import GSheetsConnection

# ─────────────────────────────────────────────
# CONFIGURAÇÃO DA PÁGINA
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Gestão de Pedidos - Folhagem",
    page_icon="🥬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
# INICIALIZAÇÃO DE VARIÁVEIS DE SESSÃO
# ─────────────────────────────────────────────
if 'reset_counter_folhagem' not in st.session_state:
    st.session_state['reset_counter_folhagem'] = 0

if 'usuario_logado_folhagem' not in st.session_state:
    st.session_state['usuario_logado_folhagem'] = None

# ─────────────────────────────────────────────
# CSS GLOBAL
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@400;500;700&display=swap');

:root {
    --bg-main:        #0d1117;
    --bg-card:        #161b22;
    --bg-sidebar:     #0d1117;
    --green-dark:     #1a3a2a;
    --green-mid:      #1f4d35;
    --green-accent:   #2ea043;
    --green-bright:   #3fb950;
    --green-glow:     rgba(46,160,67,.25);
    --text-primary:   #e6edf3;
    --text-muted:     #7d8590;
    --text-header:    #cae8cb;
    --border:         #21262d;
    --border-active:  #2ea043;
    --row-hover:      rgba(46,160,67,.08);
    --row-selected:   rgba(46,160,67,.18);
}

.stApp, .main { background-color: var(--bg-main) !important; color: var(--text-primary) !important; }
html, body, [class*="css"] { font-family: 'IBM Plex Sans', sans-serif !important; }
section[data-testid="stSidebar"] { background-color: var(--bg-sidebar) !important; border-right: 1px solid var(--border); }
section[data-testid="stSidebar"] * { color: var(--text-primary) !important; }
section[data-testid="stSidebar"] .stRadio label { font-size: 14px; }

.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, var(--green-mid) 0%, var(--green-accent) 100%) !important;
    color: #fff !important;
    border: 1px solid var(--green-accent) !important;
    border-radius: 8px !important;
    font-weight: 700 !important;
    letter-spacing: .3px;
    transition: all .2s ease !important;
}
.stButton > button[kind="primary"]:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 4px 18px var(--green-glow) !important;
}
.stButton > button {
    background: var(--bg-card) !important;
    color: var(--text-primary) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    transition: all .2s ease !important;
}
.stButton > button:hover {
    border-color: var(--green-accent) !important;
    color: var(--green-bright) !important;
    transform: translateY(-1px) !important;
}
.stTextInput input, .stSelectbox > div > div {
    background-color: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--text-primary) !important;
}
.stTextInput input:focus, .stSelectbox > div > div:focus-within {
    border-color: var(--green-accent) !important;
    box-shadow: 0 0 0 3px var(--green-glow) !important;
}
.title-input input {
    font-weight: 700 !important;
    font-size: 16px !important;
    color: var(--green-bright) !important;
    padding: 2px 8px !important;
    background: transparent !important;
    border: 1px dashed #21262d !important;
}
.title-input input:focus { border: 1px dashed #2ea043 !important; }

[data-testid="stDataEditor"] {
    border-radius: 10px !important;
    overflow: hidden;
    border: 1px solid var(--green-mid) !important;
    box-shadow: 0 4px 20px rgba(0,0,0,.4);
    font-size: 12px !important;
}
div[data-testid="stVerticalBlockBorderWrapper"] {
    background-color: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    transition: box-shadow .25s ease, border-color .25s ease;
}
div[data-testid="stVerticalBlockBorderWrapper"]:hover {
    border-color: var(--green-mid) !important;
    box-shadow: 0 6px 24px rgba(0,0,0,.35) !important;
}
[data-testid="stMetric"] {
    background-color: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 10px 10px;
}
[data-testid="stMetricValue"] { color: var(--green-bright) !important; font-weight: 700; font-size: 1.8rem !important; }
[data-testid="stMetricLabel"] { color: var(--text-muted) !important; }

.topbar-loja {
    background: linear-gradient(90deg, var(--green-dark) 0%, #0d2018 100%);
    border: 1px solid var(--green-mid);
    border-radius: 10px;
    padding: 10px 18px;
    margin-bottom: 18px;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.topbar-left { display: flex; align-items: center; gap: 12px; }
.topbar-title { font-size: 18px; font-weight: 700; color: var(--text-header); }
.topbar-sub { font-size: 11px; color: var(--text-muted); margin-top: 2px; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# CONSTANTES
# ─────────────────────────────────────────────
LOJAS = ["Loja 01", ""Loja 02"", ""Loja 03"", ""Loja 04"", ""Loja 05"", ""Loja 06"", ""Loja 07"", ""Loja 08""]"
MAPA_LOJAS = {l: l for l in LOJAS}

# ─────────────────────────────────────────────
# CONEXÃO GOOGLE SHEETS & FUNÇÕES DE DADOS
# ─────────────────────────────────────────────
conn = st.connection("gsheets", type=GSheetsConnection)

@st.cache_data(ttl=15)
def carregar_catalogo_folhagem():
    df = conn.read(worksheet="Produtos_Folhagem", ttl=0, usecols=list(range(20)))
    
    if df.empty:
        return pd.DataFrame(columns=["Código", "Descrição", "Fornecedor"] + LOJAS)
    
    # Limpeza de cabeçalhos
    novas_colunas = {}
    for col in df.columns:
        col_str = str(col).strip()
        for loja in LOJAS:
            if loja.lower() in col_str.lower():
                novas_colunas[col] = loja
    df = df.rename(columns=novas_colunas)
    
    # 🔥 PARSER CORRIGIDO — trata NaN, bool nativo e string
    for loja in LOJAS:
        if loja not in df.columns:
            df[loja] = False
        else:
            def parse_bool(x):
                if isinstance(x, bool):
                    return x
                if isinstance(x, (int, float)):
                    return bool(x) and not pd.isna(x)
                return str(x).strip().upper() in ['TRUE', 'VERDADEIRO', '1', 'V', 'SIM', 'YES', 'T', 'X']
            df[loja] = df[loja].apply(parse_bool)
            
    if "Código" in df.columns:
        df["Código"] = pd.to_numeric(df["Código"], errors='coerce').fillna(0).astype(int)
        
    return df

@st.cache_data(ttl=15)
def carregar_pedidos():
    df_pedidos = conn.read(worksheet="Folhagem", ttl=0)
    df_cat = carregar_catalogo_folhagem()
    
    # Aplica a mesma limpeza agressiva na aba de pedidos
    if not df_pedidos.empty:
        novas_colunas_ped = {}
        for col in df_pedidos.columns:
            col_str = str(col).strip()
            for loja in LOJAS:
                if loja.lower() in col_str.lower():
                    novas_colunas_ped[col] = loja
        df_pedidos = df_pedidos.rename(columns=novas_colunas_ped)
    
    if df_pedidos.empty or "Fornecedor" not in df_pedidos.columns:
        df_init = df_cat[["Código", "Descrição", "Fornecedor"]].copy()
        for loja in LOJAS:
            df_init[loja] = 0
        if not df_init.empty:
            conn.update(worksheet="Folhagem", data=df_init)
        return df_init
    
    if "Código" in df_pedidos.columns:
        df_pedidos["Código"] = pd.to_numeric(df_pedidos["Código"], errors='coerce').fillna(0).astype(int)
        
    for loja in LOJAS:
        if loja in df_pedidos.columns:
            df_pedidos[loja] = pd.to_numeric(df_pedidos[loja], errors='coerce').fillna(0).astype(int)
            
    return df_pedidos

def salvar_pedidos(df_to_save):
    conn.update(worksheet="Folhagem", data=df_to_save)
    st.cache_data.clear()

def salvar_catalogo(df_to_save):
    conn.update(worksheet="Produtos_Folhagem", data=df_to_save)
    st.cache_data.clear()

# ─────────────────────────────────────────────
# SISTEMA DE LOGIN
# ─────────────────────────────────────────────
if st.session_state['usuario_logado_folhagem'] is None:
    st.write("<br><br>", unsafe_allow_html=True)
    _, col2, _ = st.columns([1, 1.4, 1])
    with col2:
        with st.container(border=True):
            h1, h2 = st.columns([4, 1])
            with h1:
                st.markdown("""
                    <h2 style='margin-bottom:0'>Portal de Pedidos</h2>
                    <p style='color:#7d8590;font-size:14px;margin-top:4px'>Folhagem — Molicenter</p>
                """, unsafe_allow_html=True)
            with h2:
                st.write("")
                try:
                    st.image("passaro_logo.png", width=60)
                except Exception:
                    st.markdown("🥬", unsafe_allow_html=True)

            st.divider()
            usuarios_permitidos = ["Selecione..."] + ["Administrador"] + LOJAS
            usuario_selecionado = st.selectbox("👤 Usuário de acesso:", usuarios_permitidos)
            
            senha_digitada = st.text_input("🔑 Senha de acesso:", type="password", autocomplete="off")
            
            st.write("<br>", unsafe_allow_html=True)

            if st.button("Entrar no Sistema", type="primary", use_container_width=True):
                if usuario_selecionado == "Selecione...":
                    st.error("⚠️ Por favor, selecione um usuário.")
                elif usuario_selecionado == "Administrador" and senha_digitada == "moli0000":
                    st.session_state['usuario_logado_folhagem'] = usuario_selecionado
                    st.rerun()
                elif usuario_selecionado in LOJAS and senha_digitada == "moli1234":
                    st.session_state['usuario_logado_folhagem'] = usuario_selecionado
                    st.rerun()
                elif senha_digitada:
                    st.error("⚠️ Senha incorreta. Tente novamente.")

            st.markdown('<p style="font-size: 11px; color: #7d8590; text-align: center; margin-top: 10px;">🔒 Acesso restrito — Molicenter © 2026</p>', unsafe_allow_html=True)
    st.stop()

# ─────────────────────────────────────────────
# PÓS-LOGIN
# ─────────────────────────────────────────────
usuario_atual = st.session_state['usuario_logado_folhagem']
acesso_total  = usuario_atual == "Administrador"

if not acesso_total:
    st.markdown("""
    <style>
        section[data-testid="stSidebar"] { display: none !important; }
        [data-testid="collapsedControl"]  { display: none !important; }
        .main .block-container { max-width: 100% !important; padding-left: 2.5rem !important; padding-right: 2.5rem !important; }
    </style>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    try:
        st.image("passaro_logo.png", width=72)
    except Exception:
        st.markdown("🥬")

    st.markdown(f"### Olá, *{usuario_atual}*")
    st.caption("Sistema de Pedidos — Folhagem")
    st.divider()

    if acesso_total:
        perfil_navegacao = st.radio("📍 Navegação:", [
            "Separação e Fechamento",
            "Visão das Lojas",
            "Visão Fornecedores (Resumo)",
            "Catálogo de Produtos" 
        ])
    else:
        perfil_navegacao = "Visão das Lojas"

    st.divider()
    
    df_ped = carregar_pedidos()
    if not df_ped.empty and set(LOJAS).issubset(df_ped.columns):
        total_preenchidos = (df_ped[LOJAS] > 0).any(axis=1).sum()
    else:
        total_preenchidos = 0
        
    st.metric("Itens c/ pedido", total_preenchidos, help="Itens com ao menos 1 quantidade preenchida")
    
    st.divider()
    
    if st.button("🔄 Sincronizar Dados", use_container_width=True):
        st.cache_data.clear()
        st.session_state['reset_counter_folhagem'] += 1
        st.rerun()
        
    st.write("<br>", unsafe_allow_html=True)

    if st.button("🚪 Sair / Logout", use_container_width=True):
        st.session_state['usuario_logado_folhagem'] = None
        st.rerun()

# ─────────────────────────────────────────────
# FUNÇÃO MODAL DE CONFIRMAÇÃO PARA ZERAR
# ─────────────────────────────────────────────
@st.dialog("🚨 Confirmação Necessária")
def modal_zerar_pedidos():
    st.markdown("Tem certeza que deseja **zerar todos os pedidos** de todas as lojas?")
    st.markdown("⚠️ *Esta ação irá zerar as quantidades diretamente no Google Sheets.*")
    
    st.write("<br>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        if st.button("❌ Não, cancelar", use_container_width=True):
            st.rerun()
    with c2:
        if st.button("✔️ Sim, zerar tudo", type="primary", use_container_width=True):
            st.session_state['reset_counter_folhagem'] += 1
            df_main = carregar_pedidos()
            for loja in LOJAS:
                if loja in df_main.columns:
                    df_main[loja] = 0
            salvar_pedidos(df_main)
            st.rerun()

# ─────────────────────────────────────────────
# ROTA 1 — SEPARAÇÃO E FECHAMENTO (Admin)
# ─────────────────────────────────────────────
if perfil_navegacao == "Separação e Fechamento":
    st.markdown("""
    <div style="background: linear-gradient(90deg, var(--green-dark) 0%, #0d2018 100%); padding: 14px 20px; border-radius: 10px; margin-bottom: 22px;">
        <span style="font-size: 26px; margin-right: 12px;">📊</span>
        <div style="display: inline-block; vertical-align: top;">
            <div style="font-size: 20px; font-weight: 700; color: var(--text-header);">Separação e Fechamento — Folhagem</div>
            <div style="font-size: 12px; color: var(--text-muted); margin-top: 2px;">Consolidado geral de quantidades por fornecedor</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    with st.container(border=True):
        df_base = carregar_pedidos()
        
        if df_base.empty:
            st.warning("A base de pedidos está vazia. Cadastre produtos no Catálogo primeiro.")
            st.stop()
            
        df_base["TOTAL GERAL"] = df_base[LOJAS].sum(axis=1)

        col_cfg = {
            "Fornecedor":  st.column_config.TextColumn("Fornecedor", disabled=True),
            "Código":      st.column_config.NumberColumn("Cód", width=80, format="%d", disabled=True),
            "Descrição":   st.column_config.TextColumn("Produto", disabled=True),
            "TOTAL GERAL": st.column_config.NumberColumn("TOTAL ▶️", width=90, format="%d", disabled=True),
        }
        for loja, novo_nome in MAPA_LOJAS.items():
            col_cfg[loja] = st.column_config.NumberColumn(novo_nome, format="%d", min_value=0, step=1)

        cols_order = ["Fornecedor", "Código", "Descrição"] + LOJAS + ["TOTAL GERAL"]
        df_exibir = df_base[cols_order]

        df_editado = st.data_editor(
            df_exibir,
            hide_index=True,
            use_container_width=True,
            height=600,
            column_config=col_cfg,
            key=f"sep_editor_{st.session_state['reset_counter_folhagem']}"
        )

        st.divider()
        col_salvar, col_csv, col_excel, col_zerar, _ = st.columns([2.5, 1.5, 1.5, 2, 2.5])

        with col_salvar:
            if st.button("💾 Salvar Alterações", type="primary", use_container_width=True):
                df_to_save = df_editado.drop(columns=["TOTAL GERAL"])
                salvar_pedidos(df_to_save)
                st.success("✅ Pedidos salvos na nuvem com sucesso!")
                st.rerun()

        with col_csv:
            df_csv = df_editado.copy().rename(columns=MAPA_LOJAS)
            csv = df_csv.to_csv(index=False).encode("utf-8")
            st.download_button("⬇️ CSV", data=csv, file_name="separacao_folhagem.csv", mime="text/csv", use_container_width=True)

        with col_excel:
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df_exp = df_editado.copy().rename(columns=MAPA_LOJAS)
                df_exp.to_excel(writer, index=False, sheet_name='Pedidos Folhagem')
            st.download_button("⬇️ Excel", data=buffer.getvalue(), file_name="separacao_folhagem.xlsx",
                               mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                               use_container_width=True)

        with col_zerar:
            if st.button("🚨 Zerar Todos os Pedidos", use_container_width=True):
                modal_zerar_pedidos()

# ─────────────────────────────────────────────
# ROTA 2 — VISÃO DAS LOJAS
# ─────────────────────────────────────────────
elif perfil_navegacao == "Visão das Lojas":
    if acesso_total:
        loja_selecionada = st.selectbox("👁️ Visualizar como:", LOJAS)
    else:
        loja_selecionada = usuario_atual

    col_info, col_logout = st.columns([8, 2])
    with col_info:
        id_loja = MAPA_LOJAS.get(loja_selecionada, loja_selecionada)
        st.markdown(f"""
        <div class="topbar-loja">
            <div class="topbar-left">
                <span style="font-size:22px">🥬</span>
                <div>
                    <div class="topbar-title">{loja_selecionada} — Folhagem</div>
                    <div class="topbar-sub">Preencha a quantidade de cada produto por fornecedor</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col_logout:
        st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
        if st.button("🚪 Sair / Logout", use_container_width=True):
            st.session_state['usuario_logado_folhagem'] = None
            st.rerun()

    df_cat = carregar_catalogo_folhagem()
    df_cat_loja = df_cat[df_cat[loja_selecionada] == True].copy()
    
    if df_cat_loja.empty:
        st.warning(f"Nenhum produto habilitado para a {loja_selecionada} no momento.")
        st.stop()

    df_all = carregar_pedidos()
    df_loja_view = pd.merge(
        df_cat_loja[["Fornecedor", "Código", "Descrição"]],
        df_all[["Código", "Descrição", "Fornecedor", loja_selecionada]],
        on=["Código", "Descrição", "Fornecedor"],
        how="left"
    )
    df_loja_view[loja_selecionada] = df_loja_view[loja_selecionada].fillna(0).astype(int)
    df_loja_view = df_loja_view.rename(columns={loja_selecionada: "Qtde"})

    with st.container(border=True):
        st.info("💡 Preencha a *Qtde* desejada para cada produto. Apenas os fornecedores e itens atrelados a esta loja são exibidos.")

        col_cfg_loja = {
            "Fornecedor": st.column_config.TextColumn("Fornecedor", width=150, disabled=True),
            "Código":     st.column_config.NumberColumn("Cód", width=65, format="%d", disabled=True),
            "Descrição":  st.column_config.TextColumn("Produto", width=220, disabled=True),
            "Qtde":       st.column_config.NumberColumn("🛒 Qtde", width=90, min_value=0, step=1),
        }

        with st.container():
            df_editado = st.data_editor(
                df_loja_view,
                column_config=col_cfg_loja,
                hide_index=True,
                use_container_width=True,
                height=520,
                key=f"loja_folhagem_{st.session_state['reset_counter_folhagem']}"
            )

        itens_com_pedido = int((df_editado["Qtde"] > 0).sum())
        total_itens      = len(df_editado)
        total_unidades   = int(df_editado["Qtde"].sum())
        pct              = round(itens_com_pedido / total_itens * 100) if total_itens else 0

        st.divider()
        m1, m2, m3, _, col_btn = st.columns([2.5, 2.2, 1.8, 0.5, 3])
        with m1: st.metric("Itens preenchidos", f"{itens_com_pedido} / {total_itens}")
        with m2: st.metric("Total de unidades", total_unidades)
        with m3: st.metric("Cobertura", f"{pct}%")
        with col_btn:
            st.write("<br>", unsafe_allow_html=True)
            if st.button("💾 Salvar Pedido da Semana", type="primary", use_container_width=True):
                df_main = carregar_pedidos()
                
                for _, row in df_editado.iterrows():
                    mask = (
                        (df_main["Fornecedor"] == row["Fornecedor"]) &
                        (df_main["Código"] == row["Código"])
                    )
                    if mask.any():
                        df_main.loc[mask, loja_selecionada] = row["Qtde"]
                    else:
                        nova_linha = {"Fornecedor": row["Fornecedor"], "Código": row["Código"], "Descrição": row["Descrição"]}
                        for l in LOJAS: nova_linha[l] = 0
                        nova_linha[loja_selecionada] = row["Qtde"]
                        df_main = pd.concat([df_main, pd.DataFrame([nova_linha])], ignore_index=True)
                
                salvar_pedidos(df_main)
                st.success(f"✅ Pedido da {loja_selecionada} enviado para a nuvem com sucesso!")

# ─────────────────────────────────────────────
# ROTA 3 — VISÃO FORNECEDORES / RESUMO (Admin)
# ─────────────────────────────────────────────
elif perfil_navegacao == "Visão Fornecedores (Resumo)":
    st.markdown("""
    <div style="background: linear-gradient(90deg, var(--green-dark) 0%, #0d2018 100%); padding: 14px 20px; border-radius: 10px; margin-bottom: 22px;">
        <span style="font-size: 26px; margin-right: 12px;">🚚</span>
        <div style="display: inline-block; vertical-align: top;">
            <div style="font-size: 20px; font-weight: 700; color: var(--text-header);">Visão por Fornecedor — Folhagem</div>
            <div style="font-size: 12px; color: var(--text-muted); margin-top: 2px;">Resumo consolidado: totais por loja e geral para cada fornecedor</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    df_all = carregar_pedidos()
    df_cat = carregar_catalogo_folhagem()
    
    if df_all.empty or df_cat.empty:
        st.warning("Não há dados de pedidos ou catálogo preenchidos.")
        st.stop()

    nomes_fornecedores = df_cat["Fornecedor"].dropna().unique().tolist()

    for i in range(0, len(nomes_fornecedores), 1):
        cols = st.columns(1, gap="small")
        for j, fornecedor in enumerate(nomes_fornecedores[i:i+1]):
            
            df_cat_forn = df_cat[df_cat["Fornecedor"] == fornecedor]
            lojas_forn = [l for l in LOJAS if df_cat_forn[l].any()]
            
            if not lojas_forn:
                continue 

            lojas_renomeadas = {l: MAPA_LOJAS[l] for l in lojas_forn}

            df_forn = df_all[df_all["Fornecedor"] == fornecedor].copy()
            
            colunas_presentes = [c for c in lojas_forn if c in df_forn.columns]
            df_forn = df_forn[["Código", "Descrição"] + colunas_presentes].copy()
            df_forn["TOTAL"] = df_forn[colunas_presentes].sum(axis=1)
            df_forn = df_forn.rename(columns=lojas_renomeadas)

            lojas_cols_renomeadas = [MAPA_LOJAS[l] for l in colunas_presentes]

            col_cfg_forn = {
                "Código":    st.column_config.NumberColumn("Cód", format="%d", disabled=False),
                "Descrição": st.column_config.TextColumn("Produto", disabled=False),
                "TOTAL":     st.column_config.NumberColumn("TOTAL", format="%d", disabled=True),
            }
            for c in lojas_cols_renomeadas:
                col_cfg_forn[c] = st.column_config.NumberColumn(c, format="%d", disabled=False, min_value=0)

            # 🔥 AJUSTE APLICADO AQUI: Altura exata sem sobrar linha em branco 🔥
            altura = (len(df_forn) * 35) + 42 

            with cols[j]:
                with st.container(border=True):
                    st.markdown('<div class="title-input">', unsafe_allow_html=True)
                    st.text_input(
                        "Fornecedor",
                        value=f"🥬 {fornecedor}",
                        label_visibility="collapsed",
                        key=f"title_forn_{fornecedor}_{st.session_state['reset_counter_folhagem']}"
                    )
                    st.markdown('</div>', unsafe_allow_html=True)

                    lojas_str = " · ".join([MAPA_LOJAS[l] for l in colunas_presentes])
                    st.caption(f"Atende: {lojas_str}")

                    cols_order_forn = ["Código", "Descrição"] + lojas_cols_renomeadas + ["TOTAL"]
                    df_forn_edit = st.data_editor(
                        df_forn[cols_order_forn],
                        hide_index=True,
                        use_container_width=True,
                        column_config=col_cfg_forn,
                        height=altura,
                        num_rows="fixed",
                        key=f"forn_folhagem_{fornecedor}_{st.session_state['reset_counter_folhagem']}"
                    )

                    total_geral = int(df_forn_edit["TOTAL"].sum()) if "TOTAL" in df_forn_edit.columns else 0
                    st.markdown(f"""
                        <div style="text-align:right; font-weight:700; margin-top:6px; color:var(--green-bright); font-size:15px;">
                            Total Geral: {total_geral} unidades
                        </div>
                    """, unsafe_allow_html=True)

        st.write("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# ROTA 4 — CATÁLOGO DE PRODUTOS
# ─────────────────────────────────────────────
elif perfil_navegacao == "Catálogo de Produtos":
    st.markdown("""
    <div style="background: linear-gradient(90deg, var(--green-dark) 0%, #0d2018 100%); padding: 14px 20px; border-radius: 10px; margin-bottom: 22px;">
        <span style="font-size: 26px; margin-right: 12px;">🗂️</span>
        <div style="display: inline-block; vertical-align: top;">
            <div style="font-size: 20px; font-weight: 700; color: var(--text-header);">Catálogo de Folhagem</div>
            <div style="font-size: 12px; color: var(--text-muted); margin-top: 2px;">Gerencie itens e controle a visibilidade por loja através das caixas de seleção</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    df_catalogo = carregar_catalogo_folhagem()
    
    with st.container(border=True):
        
        col_cfg_cat = {
            "Código":     st.column_config.NumberColumn("Cód.", width=80, format="%d"),
            "Descrição":  st.column_config.TextColumn("Descrição do Item", width=300),
            "Fornecedor": st.column_config.TextColumn("Fornecedor", width=180),
        }
        for loja in LOJAS:
            col_cfg_cat[loja] = st.column_config.CheckboxColumn(loja, default=False)
            
        edited_cat = st.data_editor(
            df_catalogo,
            use_container_width=True,
            hide_index=True,
            height=600,
            num_rows="dynamic",
            column_config=col_cfg_cat,
            key=f"editor_catalogo_folhagem_{st.session_state['reset_counter_folhagem']}"
        )
        
        st.divider()
        if st.button("💾 Salvar Catálogo no Google Sheets", type="primary", use_container_width=True):
            salvar_catalogo(edited_cat)
            st.session_state['reset_counter_folhagem'] += 1
            st.success("✅ Catálogo atualizado com sucesso! As alterações já refletem na visão das lojas.")
            st.rerun()

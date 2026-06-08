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
# CSS GLOBAL (mesmo padrão visual do FLV Normal)
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
LOJAS = ["Loja 01", "Loja 02", "Loja 03", "Loja 04", "Loja 05", "Loja 06", "Loja 07", "Loja 08"]
MAPA_LOJAS = {l: l for l in LOJAS}

FORNECEDORES_CONFIG = {
    "Sidnei / Evanilde": {
        "lojas": ["Loja 01", "Loja 02", "Loja 03", "Loja 04", "Loja 05", "Loja 06"],
        "produtos": [
            {"Código": 9250,  "Descrição": "Cebolinha"},
            {"Código": 9311,  "Descrição": "Couve Manteiga"},
        ]
    },
    "Sidnei Gudelumes": {
        "lojas": ["Loja 01", "Loja 02", "Loja 03", "Loja 04", "Loja 05", "Loja 06"],
        "produtos": [
            {"Código": 14144, "Descrição": "Brocólis Maço"},
        ]
    },
    "Ricardo Morakami": {
        "lojas": ["Loja 05", "Loja 06"],
        "produtos": [
            {"Código": 253295, "Descrição": "Alface Hidropônica"},
            {"Código": 346151, "Descrição": "Rucula Hidropônica"},
        ]
    },
    "Paulo Fukunaga": {
        "lojas": ["Loja 01", "Loja 02", "Loja 03", "Loja 04"],
        "produtos": [
            {"Código": 16902,  "Descrição": "Alface Hidropônica"},
            {"Código": 452115, "Descrição": "Rucula Hidropônica"},
        ]
    },
    "Perola Verde": {
        "lojas": ["Loja 01", "Loja 02", "Loja 03", "Loja 04", "Loja 07", "Loja 08"],
        "produtos": [
            {"Código": 637062, "Descrição": "Alface Crespa Roxa"},
            {"Código": 457916, "Descrição": "Alface Hidropônica"},
            {"Código": 637071, "Descrição": "Alface Lisa"},
            {"Código": 637088, "Descrição": "Alface Mimosa Verde"},
            {"Código": 0,      "Descrição": "Alface Mista"},
            {"Código": 1,      "Descrição": "Almeirão Hidropônico"},
            {"Código": 457925, "Descrição": "Rucula Hidropônica"},
        ]
    },
    "Fenato": {
        "lojas": ["Loja 01", "Loja 02", "Loja 03", "Loja 04", "Loja 05", "Loja 06"],
        "produtos": [
            {"Código": 513063, "Descrição": "Alface Americana"},
            {"Código": 513744, "Descrição": "Alface Crespa"},
            {"Código": 513045, "Descrição": "Alface Roxa"},
            {"Código": 453363, "Descrição": "Almeirão"},
            {"Código": 9205,   "Descrição": "Chicória"},
            {"Código": 44493,  "Descrição": "Coentro Maço"},
            {"Código": 0,      "Descrição": "Rúcula"},
            {"Código": 9269,   "Descrição": "Salsinha"},
        ]
    },
    "Suzuki": {
        "lojas": ["Loja 05", "Loja 06"],
        "produtos": [
            {"Código": 459154, "Descrição": "Alface Hidropônica"},
            {"Código": 459163, "Descrição": "Rucula Hidropônica"},
        ]
    },
    "Anderson Assaí": {
        "lojas": ["Loja 07"],
        "produtos": [
            {"Código": 34159, "Descrição": "Alface Americana"},
            {"Código": 9241,  "Descrição": "Alface Crespa"},
            {"Código": 9214,  "Descrição": "Almeirão"},
            {"Código": 9250,  "Descrição": "Cebolinha"},
            {"Código": 44493, "Descrição": "Coentro"},
            {"Código": 9269,  "Descrição": "Salsinha"},
            {"Código": 9311,  "Descrição": "Couve Manteiga Maço"},
        ]
    },
}

# ─────────────────────────────────────────────
# CONEXÃO GOOGLE SHEETS & FUNÇÕES DE DADOS
# ─────────────────────────────────────────────
conn = st.connection("gsheets", type=GSheetsConnection)

@st.cache_data(ttl=15) # O Cache atualiza a cada 15 segundos para sincronizar as lojas
def carregar_pedidos():
    df = conn.read(worksheet="Folhagem")
    
    # Se a planilha estiver vazia, cria a estrutura inicial e joga pro Sheets
    if df.empty or "Fornecedor" not in df.columns:
        linhas = []
        for forn, cfg in FORNECEDORES_CONFIG.items():
            for prod in cfg["produtos"]:
                linha = {
                    "Fornecedor": forn,
                    "Código": prod["Código"],
                    "Descrição": prod["Descrição"],
                }
                for loja in LOJAS:
                    linha[loja] = 0
                linhas.append(linha)
        df_init = pd.DataFrame(linhas)
        conn.update(worksheet="Folhagem", data=df_init)
        return df_init
    
    # Tratamento de segurança: Garante que quantidades são inteiros e não nulos
    for loja in LOJAS:
        if loja in df.columns:
            df[loja] = pd.to_numeric(df[loja], errors='coerce').fillna(0).astype(int)
            
    return df

def salvar_pedidos(df_to_save):
    # Atualiza o Google Sheets e limpa o cache para forçar leitura nova
    conn.update(worksheet="Folhagem", data=df_to_save)
    st.cache_data.clear()

if 'reset_counter_folhagem' not in st.session_state:
    st.session_state['reset_counter_folhagem'] = 0

# ─────────────────────────────────────────────
# SISTEMA DE LOGIN
# ─────────────────────────────────────────────
if 'usuario_logado_folhagem' not in st.session_state:
    st.session_state['usuario_logado_folhagem'] = None

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
            
            # Bloqueio de autocomplete adicionado aqui
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
        ])
    else:
        perfil_navegacao = "Visão das Lojas"

    st.divider()
    
    # Indicador de Preenchimento (Lê do Sheets)
    df_ped = carregar_pedidos()
    total_preenchidos = (df_ped[LOJAS] > 0).any(axis=1).sum()
    st.metric("Itens c/ pedido", total_preenchidos, help="Itens com ao menos 1 quantidade preenchida")
    
    st.divider()
    if st.button("🚪 Sair / Logout", use_container_width=True):
        st.session_state['usuario_logado_folhagem'] = None
        st.rerun()

# ─────────────────────────────────────────────
# FUNÇÃO MODAL DE CONFIRMAÇÃO PARA ZERAR (VIA GOOGLE SHEETS)
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
                # Remove a coluna calculada 'TOTAL GERAL' antes de enviar para o Sheets
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

    fornecedores_da_loja = [
        forn for forn, cfg in FORNECEDORES_CONFIG.items()
        if loja_selecionada in cfg["lojas"]
    ]

    df_all = carregar_pedidos()
    df_loja_view = df_all[df_all["Fornecedor"].isin(fornecedores_da_loja)][
        ["Fornecedor", "Código", "Descrição", loja_selecionada]
    ].copy().rename(columns={loja_selecionada: "Qtde"})

    with st.container(border=True):
        st.info("💡 Preencha a *Qtde* desejada para cada produto. Apenas os fornecedores que atendem esta loja são exibidos.")

        # Otimização visual da tabela para não esticar demais
        col_cfg_loja = {
            "Fornecedor": st.column_config.TextColumn("Fornecedor", width=200, disabled=True),
            "Código":     st.column_config.NumberColumn("Cód", width=80, format="%d", disabled=True),
            "Descrição":  st.column_config.TextColumn("Produto", width=400, disabled=True),
            "Qtde":       st.column_config.NumberColumn("🛒 Qtde", width=120, min_value=0, step=1),
        }

        # Criação de margens com colunas vazias
        _, col_tabela, _ = st.columns([1, 4, 1])

        with col_tabela:
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
                # Carrega o DF principal para não sobrescrever o que outras lojas fizeram
                df_main = carregar_pedidos()
                for _, row in df_editado.iterrows():
                    mask = (
                        (df_main["Fornecedor"] == row["Fornecedor"]) &
                        (df_main["Descrição"] == row["Descrição"])
                    )
                    df_main.loc[mask, loja_selecionada] = row["Qtde"]
                
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
    nomes_fornecedores = list(FORNECEDORES_CONFIG.keys())

    for i in range(0, len(nomes_fornecedores), 1):
        cols = st.columns(1, gap="small")
        for j, fornecedor in enumerate(nomes_fornecedores[i:i+1]):
            cfg = FORNECEDORES_CONFIG[fornecedor]
            lojas_forn = cfg["lojas"]
            lojas_renomeadas = {l: MAPA_LOJAS[l] for l in lojas_forn}

            df_forn = df_all[df_all["Fornecedor"] == fornecedor].copy()
            df_forn = df_forn[["Código", "Descrição"] + lojas_forn].copy()
            df_forn["TOTAL"] = df_forn[lojas_forn].sum(axis=1)
            df_forn = df_forn.rename(columns=lojas_renomeadas)

            lojas_cols_renomeadas = list(lojas_renomeadas.values())

            col_cfg_forn = {
                "Código":    st.column_config.NumberColumn("Cód", format="%d", disabled=False),
                "Descrição": st.column_config.TextColumn("Produto", disabled=False),
                "TOTAL":     st.column_config.NumberColumn("TOTAL", format="%d", disabled=True),
            }
            for c in lojas_cols_renomeadas:
                col_cfg_forn[c] = st.column_config.NumberColumn(c, format="%d", disabled=False, min_value=0)

            altura = int((len(df_forn) + 2) * 36) + 5

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

                    lojas_str = " · ".join([MAPA_LOJAS[l] for l in lojas_forn])
                    st.caption(f"Atende: {lojas_str}")

                    cols_order_forn = ["Código", "Descrição"] + lojas_cols_renomeadas + ["TOTAL"]
                    df_forn_edit = st.data_editor(
                        df_forn[cols_order_forn],
                        hide_index=True,
                        use_container_width=True,
                        column_config=col_cfg_forn,
                        height=altura,
                        num_rows="dynamic",
                        key=f"forn_folhagem_{fornecedor}_{st.session_state['reset_counter_folhagem']}"
                    )

                    total_geral = int(df_forn_edit["TOTAL"].sum()) if "TOTAL" in df_forn_edit.columns else 0
                    st.markdown(f"""
                        <div style="text-align:right; font-weight:700; margin-top:6px; color:var(--green-bright); font-size:15px;">
                            Total Geral: {total_geral} unidades
                        </div>
                    """, unsafe_allow_html=True)

        st.write("<br>", unsafe_allow_html=True)

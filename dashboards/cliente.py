import streamlit as st
from utils.auth import verificar_autenticacao
from database.db import (
    buscar_docas,
    buscar_alocacoes_docas,
    buscar_agendamentos_por_usuario,
    criar_agendamento,
    buscar_encomendas,
    alocar_encomenda_agendamento,
)

def render():
    if not verificar_autenticacao("cliente"):
        st.stop()

    # Fundo escuro e estilos globais para contraste e fontes
    st.markdown("""
    <style>
    body, .stApp {
        background: linear-gradient(120deg, #232946 0%, #394867 100%) !important;
    }
    label, .stTextInput > label, .stSelectbox > label, .stMultiSelect > label, .stSlider > label, .stRadio > label, .stCheckbox > label {
        color: #f5f7fa !important;
        font-weight: 700 !important;
        font-size: 1.08rem !important;
        letter-spacing: 0.5px;
    }
    input, textarea, select {
        background-color: #232946 !important;
        color: #f5f7fa !important;
        border-radius: 7px !important;
        border: 1.5px solid #90caf9 !important;
    }
    .stTextInput input:focus, .stSelectbox select:focus, .stMultiSelect input:focus, .stSlider input:focus, .stRadio input:focus, .stCheckbox input:focus {
        border: 2px solid #1976d2 !important;
        background-color: #232946 !important;
        color: #fff !important;
    }
    </style>
    """, unsafe_allow_html=True)

    usuario = st.session_state.usuario
    usuario_id = st.session_state.usuario_id

    # Cabeçalho em formato de card
    st.markdown(f"""
    <div style="
        max-width: 520px;
        margin: 32px auto 18px auto;
        padding: 28px 24px 18px 24px;
        background: linear-gradient(120deg, #e3f2fd 60%, #90caf9 100%);
        border-radius: 18px;
        box-shadow: 0 4px 24px #0004;
        border-left: 8px solid #1976d2;
        text-align: center;
    ">
        <div style="font-size:2.5rem; margin-bottom:8px;">👤</div>
        <h2 style="color:#1976d2; font-weight:800; letter-spacing:1px; margin-bottom:10px;">Dashboard do Cliente</h2>
        <span style="color:#333; font-size:1.1rem;">Bem-vindo, <b>{st.session_state.nome}</b>!<br></span>
    </div>
    """, unsafe_allow_html=True)

    # Buscar docas do banco e alocações do banco
    docas = buscar_docas()
    alocacoes = buscar_alocacoes_docas()

    # Filtra docas alocadas para este cliente
    docas_cliente = [
        d["doca_nome"] for d in alocacoes if d["usuario_id"] == usuario_id
    ]

    # Inicializa toggles na sessão
    if "show_agendamentos" not in st.session_state:
        st.session_state.show_agendamentos = False
    if "show_docas" not in st.session_state:
        st.session_state.show_docas = False
    if "show_form_agendamento" not in st.session_state:
        st.session_state.show_form_agendamento = False
    if "show_encomendas" not in st.session_state:
        st.session_state.show_encomendas = False

    st.divider()

    # Botão toggle para agendamentos
    if st.button("📅 Ver Agendamentos", key="btn_agendamentos"):
        st.session_state.show_agendamentos = not st.session_state.show_agendamentos

    if st.session_state.show_agendamentos:
        ags = buscar_agendamentos_por_usuario(usuario_id)
        st.markdown(
            '<h3 style="color:#d0e4f7; font-weight:800; letter-spacing:0.5px; margin-bottom:12px;">Meus Agendamentos</h3>',
            unsafe_allow_html=True
        )
        if ags:
            for ag in ags:
                cor_borda, cor_grad1, cor_grad2, cor_status, icone, status_legenda = {
                    "Pendente":   ("#b28704", "#fff9e1", "#ffe082", "#b28704", "⏳", "Pendente"),
                    "Em Processamento": ("#1976d2", "#e3f2fd", "#90caf9", "#1976d2", "🔄", "Em Processamento"),
                    "Confirmado": ("#0097a7", "#e0f7fa", "#80deea", "#0097a7", "📅", "Confirmado"),
                    "Concluído": ("#388e3c", "#e8f5e9", "#a5d6a7", "#388e3c", "✅", "Concluído"),
                    "Cancelado":  ("#d32f2f", "#ffebee", "#ffcdd2", "#d32f2f", "❌", "Cancelado"),
                }.get(ag["status"], ("#b0bec5", "#eceff1", "#b0bec5", "#78909c", "❔", ag["status"]))
                st.markdown(f"""
<div style="
    background: linear-gradient(90deg, {cor_grad1} 60%, {cor_grad2} 100%);
    padding: 18px 24px;
    border-radius: 12px;
    margin-bottom: 18px;
    box-shadow: 0 2px 12px #0002;
    border-left: 6px solid {cor_borda};
    display: flex;
    align-items: center;
    justify-content: space-between;
">
  <div>
    <div style="font-size: 1.1rem; color: {cor_status}; font-weight: 700; letter-spacing: 1px; margin-bottom: 2px;">
        <span style="vertical-align: middle;">{icone} Agendamento {status_legenda}</span>
    </div>
    <div style="color: #222; font-size: 1.05rem; margin-bottom: 2px;">
        <b>Data:</b> {ag['data']} &nbsp; <b>Hora:</b> {ag['hora']} &nbsp; <b>Doca:</b> {ag['doca_nome']}
    </div>
    <div style="color: #444; font-size: 0.98rem;">
        <b>Status:</b> <span style="color:{cor_status};">{ag['status']}</span>
    </div>
  </div>
  <div style="text-align: right;">
    <span style="background:{cor_status}22; color:{cor_status}; padding:6px 14px; border-radius:8px; font-weight:700; font-size:0.95rem;">
        ● {status_legenda}
    </span>
  </div>
</div>
""", unsafe_allow_html=True)
        else:
            st.markdown(
                '<h3 style="color:#d0e4f7; font-weight:200; letter-spacing:0.5px; margin-bottom:12px; font-size:1.02rem;">⚠️Nenhum Agendamento Encontrado.⚠️</h3>',
                unsafe_allow_html=True
            )

    # Botão toggle para docas
    if len(docas_cliente) == 1:
        if st.button("🔎 Status da Doca", key="btn_docas"):
            st.session_state.show_docas = not st.session_state.show_docas
        if st.session_state.show_docas:
            doca_nome = docas_cliente[0]
            doca_status = next((d["status"] for d in docas if d["nome"] == doca_nome), "Desconhecido")
            cor_borda, cor_grad1, cor_grad2, cor_status, icone, status_legenda = {
                "Livre": ("#388e3c", "#e8f5e9", "#a5d6a7", "#388e3c", "🟢", "Livre"),
                "Ocupada": ("#1976d2", "#e3f2fd", "#90caf9", "#1976d2", "🔵", "Ocupada"),
                "Em preparação": ("#b28704", "#fff9e1", "#ffe082", "#b28704", "🟡", "Em preparação"),
            }.get(doca_status, ("#b0bec5", "#eceff1", "#b0bec5", "#78909c", "❔", doca_status))
            st.markdown(f"""
<div style="
    background: linear-gradient(90deg, {cor_grad1} 60%, {cor_grad2} 100%);
    padding: 16px 20px;
    border-radius: 10px;
    margin-bottom: 14px;
    box-shadow: 0 2px 8px #0001;
    border-left: 6px solid {cor_borda};
    display: flex;
    align-items: center;
    justify-content: space-between;
">
  <div>
    <div style="font-size: 1.08rem; color: {cor_status}; font-weight: 700; margin-bottom: 2px;">
        <span style="vertical-align: middle;">{icone} Doca {doca_nome}</span>
    </div>
    <div style="color: #444; font-size: 0.98rem;">
        <b>Status:</b> <span style="color:{cor_status};">{status_legenda}</span>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)
    elif len(docas_cliente) > 1:
        if st.button("🔎 Ver Docas", key="btn_docas"):
            st.session_state.show_docas = not st.session_state.show_docas
        if st.session_state.show_docas:
            for doca_nome in docas_cliente:
                doca_status = next((d["status"] for d in docas if d["nome"] == doca_nome), "Desconhecido")
                cor_borda, cor_grad1, cor_grad2, cor_status, icone, status_legenda = {
                    "Livre": ("#388e3c", "#e8f5e9", "#a5d6a7", "#388e3c", "🟢", "Livre"),
                    "Ocupada": ("#1976d2", "#e3f2fd", "#90caf9", "#1976d2", "🔵", "Ocupada"),
                    "Em preparação": ("#b28704", "#fff9e1", "#ffe082", "#b28704", "🟡", "Em preparação"),
                }.get(doca_status, ("#b0bec5", "#eceff1", "#b0bec5", "#78909c", "❔", doca_status))
                st.markdown(f"""
<div style="
    background: linear-gradient(90deg, {cor_grad1} 60%, {cor_grad2} 100%);
    padding: 16px 20px;
    border-radius: 10px;
    margin-bottom: 14px;
    box-shadow: 0 2px 8px #0001;
    border-left: 6px solid {cor_borda};
    display: flex;
    align-items: center;
    justify-content: space-between;
">
  <div>
    <div style="font-size: 1.08rem; color: {cor_status}; font-weight: 700; margin-bottom: 2px;">
        <span style="vertical-align: middle;">{icone} Doca {doca_nome}</span>
    </div>
    <div style="color: #444; font-size: 0.98rem;">
        <b>Status:</b> <span style="color:{cor_status};">{status_legenda}</span>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

    # Botão toggle para solicitar agendamento
    if st.button("➕ Solicitar Agendamento", key="btn_form_agendamento"):
        st.session_state.show_form_agendamento = not st.session_state.show_form_agendamento

    if st.session_state.show_form_agendamento:
        st.markdown(
            '<h3 style="color:#d0e4f7; font-weight:800; letter-spacing:0.5px; margin-bottom:12px;">Solicitar Novo Agendamento</h3>',
            unsafe_allow_html=True
        )
        with st.form("form_solicitar_agendamento"):
            doca_escolhida = st.selectbox("Escolha a doca", docas_cliente)
            data = st.date_input("Data")
            hora = st.time_input("Hora")
            enviar = st.form_submit_button("Solicitar")
            if enviar:
                doca_id = next((d["id"] for d in docas if d["nome"] == doca_escolhida), None)
                criar_agendamento(usuario_id, doca_id, data, hora)
                st.markdown(
                    '<div style="color:#388e3c; font-weight:700; background:#e8f5e9; padding:16px 18px; border-radius:8px; border-left:5px solid #388e3c;">Solicitação de agendamento enviada!</div>',
                    unsafe_allow_html=True
                )
                st.session_state.show_form_agendamento = False
                st.session_state.show_agendamentos = True  # Mostra agendamentos após solicitar

    # Seção de Encomendas (agora usa dados do banco)
    if st.button("📦 Ver Encomendas", key="btn_encomendas"):
        st.session_state.show_encomendas = not st.session_state.show_encomendas

    if st.session_state.show_encomendas:
        st.markdown(
            '<h3 style="color:#d0e4f7; font-weight:800; letter-spacing:0.5px; margin-bottom:12px;">Minhas Encomendas</h3>',
            unsafe_allow_html=True
        )
        # Busca encomendas do banco e filtra pelo usuario_id
        encomendas_cliente = [e for e in buscar_encomendas() if e["usuario_id"] == usuario_id]
        ags_disponiveis = [
            ag for ag in buscar_agendamentos_por_usuario(usuario_id)
            if ag["status"] in ("Pendente", "Em Processamento", "Confirmado")
        ]
        if not encomendas_cliente:
            st.markdown(
                '<h3 style="color:#d0e4f7; font-weight:200; letter-spacing:0.5px; margin-bottom:12px; font-size:1.02rem;">⚠️Nenhuma Encomenda Registada.⚠️</h3>',
                unsafe_allow_html=True)
        else:
            for idx, encomenda in enumerate(encomendas_cliente):
                cor_borda, cor_grad1, cor_grad2, cor_status, icone, status_legenda = {
                    "Pendente":   ("#b28704", "#fff9e1", "#ffe082", "#b28704", "📦", "Pendente"),
                    "Em Processamento": ("#1976d2", "#e3f2fd", "#90caf9", "#1976d2", "🔄", "Em Processamento"),
                    "Processada": ("#388e3c", "#e8f5e9", "#a5d6a7", "#388e3c", "✅", "Processada"),
                    "Cancelada":  ("#d32f2f", "#ffebee", "#ffcdd2", "#d32f2f", "❌", "Cancelada"),
                }[encomenda["status"]]

                st.markdown(f"""
<div style="
    background: linear-gradient(90deg, {cor_grad1} 60%, {cor_grad2} 100%);
    padding: 18px 24px;
    border-radius: 12px;
    margin-bottom: 18px;
    box-shadow: 0 2px 12px #0002;
    border-left: 6px solid {cor_borda};
    display: flex;
    align-items: center;
    justify-content: space-between;
">
  <div>
    <div style="font-size: 1.1rem; color: {cor_status}; font-weight: 700; letter-spacing: 1px; margin-bottom: 2px;">
        <span style="vertical-align: middle;">{icone} Encomenda {status_legenda}</span>
    </div>
    <div style="color: #222; font-size: 1.05rem; margin-bottom: 2px;">
        <b>Descrição:</b> {encomenda['descricao']}
    </div>
    <div style="color: #444; font-size: 0.98rem;">
        <b>Status:</b> <span style="color:{cor_status};">{encomenda['status']}</span>
    </div>
  </div>
  <div style="text-align: right;">
    <span style="background:{cor_status}22; color:{cor_status}; padding:6px 14px; border-radius:8px; font-weight:700; font-size:0.95rem;">
        ● {status_legenda}
    </span>
  </div>
</div>
""", unsafe_allow_html=True)

                # Botão para alocar encomenda em agendamento (apenas se pendente e não alocada)
                if encomenda["status"] == "Pendente" and not encomenda.get("agendamento_id"):
                    if st.button("Alocar em Agendamento", key=f"alocar_{encomenda['id']}"):
                        st.session_state[f"show_alocar_{encomenda['id']}"] = not st.session_state.get(f"show_alocar_{encomenda['id']}", False)
                if st.session_state.get(f"show_alocar_{encomenda['id']}", False):
                    with st.form(f"form_alocar_{encomenda['id']}"):
                        if not ags_disponiveis:
                            st.warning("Você não possui agendamentos disponíveis para alocar esta encomenda.")
                            st.form_submit_button("OK")  # <-- Adicione esta linha
                        else:
                            ag_options = [
                                f"Agendamento: {ag['id']} - Data: {ag['data']} - Hora: {ag['hora']} - Doca: {ag['doca_nome']}" for ag in ags_disponiveis
                            ]
                            ag_id_map = {ag_options[i]: ags_disponiveis[i]["id"] for i in range(len(ags_disponiveis))}
                            ag_select = st.selectbox("Escolha o agendamento para alocar esta encomenda:", ag_options)
                            submit = st.form_submit_button("Alocar")
                            if submit:
                                agendamento_id = ag_id_map[ag_select]
                                alocar_encomenda_agendamento(encomenda["id"], agendamento_id)
                                st.success("Encomenda alocada ao agendamento com sucesso!")
                                st.session_state[f"show_alocar_{encomenda['id']}"] = False
                                st.rerun()
    st.divider()
    st.markdown(
        f'<div style="color:#90caf9; font-size:0.98rem; margin-top:24px; text-align:right;">Utilizador: <b>ID:</b> {st.session_state.nome} &nbsp;|&nbsp; <b>Email:</b> {usuario}</div>',
        unsafe_allow_html=True
    )

    if st.button("🔓 Sair"):
        st.session_state.logado = False
        st.rerun()

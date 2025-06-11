import streamlit as st
from utils.auth import verificar_autenticacao
from datetime import datetime, timedelta
import pandas as pd
from streamlit_option_menu import option_menu
from database.db import (
    buscar_agendamentos,
    buscar_docas,
    buscar_clientes,
    buscar_alocacoes_docas,
    alocar_doca_cliente,
    desalocar_doca_cliente,
    atualizar_agendamento_status,
    atualizar_agendamento_doca_data_hora,
    buscar_alertas,
    resolver_alerta,
    buscar_encomendas,
    cancelar_encomenda,
    atualizar_status_doca,
)

def render():

    st.markdown("""
<style>
label, .stSelectbox > label {
    color: #d0e4f7 !important;
    font-weight: 700 !important;
    font-size: 1.08rem !important;
    letter-spacing: 0.5px;
}
</style>
""", unsafe_allow_html=True)

    if not verificar_autenticacao("gestor"):
        st.stop()

    st.markdown("""
    <style>
    body, .stApp {
        background: linear-gradient(120deg, #232946 0%, #394867 100%) !important;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="
        max-width: 900px;
        margin: 0 auto 28px auto;
        padding: 32px 28px 24px 28px;
        background: linear-gradient(120deg, #e3f2fd 60%, #90caf9 100%);
        border-radius: 18px;
        box-shadow: 0 4px 24px #0004;
        border-left: 8px solid #1976d2;
        text-align: left;
        display: flex;
        align-items: center;
        gap: 24px;
    ">
        <div style="font-size:2.5rem;">🚚</div>
        <div>
            <h1 style="color:#1976d2; font-weight:800; letter-spacing:1px; margin-bottom:8px; margin-top:0;">Dashboard do Gestor</h1>
            <span style="color:#222; font-size:1.13rem;">Bem-vindo, <b>{st.session_state.nome}</b>!</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    usuario = st.session_state.usuario

    # --- ALERTAS: busca do banco ---
    alertas = buscar_alertas()

    # --- Lógica de conflito: gerar alerta ao detectar conflito em pendentes ---
    ags_db = buscar_agendamentos()  # Busca todos os agendamentos do banco

    for ag in ags_db:
        if ag["status"] == "Pendente":
            conflito = any(
                a for a in ags_db
                if a is not ag and
                   a["doca_nome"] == ag["doca_nome"] and
                   a["data"] == ag["data"] and
                   a["hora"] == ag["hora"] and
                   a["status"] in ["Pendente", "Em Processamento", "Confirmado"]
            )
            alerta_existente = any(
                a for a in alertas
                if a.get("tipo") == "Conflito" and a.get("agendamento_id") == ag["id"] and a.get("status", "Ativo") == "Ativo"
            )
            if conflito and not alerta_existente:
                # Cria alerta no banco usando doca_id
                from database.db import criar_alerta
                criar_alerta(
                    mensagem=f"Conflito de agendamento para doca {ag['doca_nome']} em {ag['data']} {ag['hora']}",
                    doca_id=ag["doca_id"],
                    tipo="Conflito",
                    agendamento_id=ag["id"]
                )

    # Inicializa toggles na sessão
    if "show_agendamentos_gestor" not in st.session_state:
        st.session_state.show_agendamentos_gestor = False
    if "show_alertas_gestor" not in st.session_state:
        st.session_state.show_alertas_gestor = False
    if "show_docas_gestor" not in st.session_state:
        st.session_state.show_docas_gestor = False
    if "show_encomendas_gestor" not in st.session_state:
        st.session_state.show_encomendas_gestor = False
    if "filtro_encomenda_status" not in st.session_state:
        st.session_state.filtro_encomenda_status = "Todas"
    if "show_ag_pendentes" not in st.session_state:
        st.session_state.show_ag_pendentes = False
    if "show_ag_processando" not in st.session_state:
        st.session_state.show_ag_processando = False
    if "show_ag_confirmados" not in st.session_state:
        st.session_state.show_ag_confirmados = False
    if "show_ag_cancelados" not in st.session_state:
        st.session_state.show_ag_cancelados = False
    if "show_ag_concluidos" not in st.session_state:
        st.session_state.show_ag_concluidos = False

    st.divider()

    # Botão toggle para agendamentos
    if st.button("📅 Ver Agendamentos", key="btn_agendamentos_gestor"):
        st.session_state.show_agendamentos_gestor = not st.session_state.show_agendamentos_gestor

    if st.session_state.show_agendamentos_gestor:
        ags_db = buscar_agendamentos()  # Busca todos os agendamentos do banco

        # Buscar docas alocadas ao cliente de cada agendamento
        alocacoes = buscar_alocacoes_docas()

        # Pendentes
        if st.button("Agendamentos Pendentes", key="btn_ag_pendentes"):
            st.session_state.show_ag_pendentes = not st.session_state.show_ag_pendentes
        if st.session_state.show_ag_pendentes:
            for idx, ag in enumerate([a for a in ags_db if a["status"] == "Pendente"]):
                st.markdown(f"""
<div style="
    background: linear-gradient(90deg, #fff9e1 60%, #ffe082 100%);
    padding: 18px 24px;
    border-radius: 12px;
    margin-bottom: 18px;
    box-shadow: 0 2px 12px #0002;
    border-left: 6px solid #ffb300;
    display: flex;
    align-items: center;
    justify-content: space-between;
">
  <div>
    <div style="font-size: 1.1rem; color: #b28704; font-weight: 700; letter-spacing: 1px; margin-bottom: 2px;">
        <span style="vertical-align: middle;">⏳ Agendamento Pendente</span>
    </div>
    <div style="color: #222; font-size: 1.05rem; margin-bottom: 2px;">
        <b>Cliente:</b> {ag['usuario_nome']} &nbsp; | &nbsp;
        <b>Doca:</b> {ag['doca_nome']}
    </div>
    <div style="color: #444; font-size: 0.98rem;">
        <b>Data:</b> {ag['data']} {ag['hora']} &nbsp; | &nbsp;
        <b>Status:</b> <span style="color:#b28704;">{ag['status']}</span>
    </div>
  </div>
  <div style="text-align: right;">
    <span style="background:#b2870422; color:#b28704; padding:6px 14px; border-radius:8px; font-weight:700; font-size:0.95rem;">
        ● Pendente
    </span>
  </div>
</div>
""", unsafe_allow_html=True)
                col1, col2, col3 = st.columns(3)
                with col1:
                    conflito = any(
                        a for a in ags_db
                        if a is not ag and
                           a["doca_nome"] == ag["doca_nome"] and
                           a["data"] == ag["data"] and
                           a["hora"] == ag["hora"] and
                           a["status"] in ["Pendente", "Em Processamento", "Confirmado"]
                    )
                    if st.button("Aprovar", key=f"aprovar_{idx}"):
                        if conflito:
                            st.error("Não é possível aprovar: existe conflito de agendamento para esta doca, data e hora!")
                        else:
                            # Quando aprovar (Em Processamento)
                            atualizar_agendamento_status(ag["id"], "Em Processamento")
                            atualizar_status_doca(ag["doca_id"], "Em preparação")
                            st.success("Agendamento aprovado! Doca em preparação.")
                            st.rerun()
                with col2:
                    if st.button("Cancelar", key=f"cancelar_p_{idx}"):
                        atualizar_agendamento_status(ag["id"], "Cancelado")
                        st.warning("Agendamento cancelado!")
                        st.rerun()
                with col3:
                    if st.button("Reagendar", key=f"reagendar_p_{idx}"):
                        st.session_state[f"show_reagendar_{idx}"] = not st.session_state.get(f"show_reagendar_{idx}", False)
                if st.session_state.get(f"show_reagendar_{idx}", False):
                    with st.form(f"form_reagendar_{idx}"):
                        import datetime as dt
                        data_val = ag["data"]
                        if isinstance(data_val, str):
                            try:
                                data_val = dt.datetime.strptime(data_val, "%d/%m/%Y").date()
                            except Exception:
                                data_val = dt.date.today()
                        elif isinstance(data_val, dt.datetime):
                            data_val = data_val.date()
                        elif not isinstance(data_val, dt.date):
                            data_val = dt.date.today()
                        hora_val = ag["hora"]
                        if isinstance(hora_val, str):
                            try:
                                hora_val = dt.datetime.strptime(hora_val, "%H:%M").time()
                            except Exception:
                                hora_val = dt.datetime.now().time()
                        elif isinstance(hora_val, dt.datetime):
                            hora_val = hora_val.time()
                        elif not isinstance(hora_val, dt.time):
                            hora_val = dt.datetime.now().time()
                        # Docas alocadas ao cliente deste agendamento
                        docas_cliente = [d["doca_nome"] for d in alocacoes if d["usuario_id"] == ag["usuario_id"]]
                        if not docas_cliente:
                            st.warning("Este cliente não possui docas alocadas.")
                        else:
                            nova_data = st.date_input("Nova data", value=data_val)
                            nova_hora = st.time_input("Nova hora", value=hora_val)
                            nova_doca = st.selectbox("Nova doca", options=docas_cliente, index=docas_cliente.index(ag["doca_nome"]))
                            submit = st.form_submit_button("Salvar Reagendamento")
                            if submit:
                                docas_db = buscar_docas()
                                doca_id = next((d["id"] for d in docas_db if d["nome"] == nova_doca), None)
                                atualizar_agendamento_doca_data_hora(ag["id"], doca_id, nova_data, nova_hora)
                                st.success("Agendamento reagendado!")
                                st.session_state[f"show_reagendar_{idx}"] = False
                                st.rerun()

        # Em Processamento
        if st.button("Agendamentos em Processamento", key="btn_ag_processando"):
            st.session_state.show_ag_processando = not st.session_state.show_ag_processando
        if st.session_state.show_ag_processando:
            for idx, ag in enumerate([a for a in ags_db if a["status"] == "Em Processamento"]):
                st.markdown(f"""
<div style="
    background: linear-gradient(90deg, #e3f2fd 60%, #90caf9 100%);
    padding: 18px 24px;
    border-radius: 12px;
    margin-bottom: 18px;
    box-shadow: 0 2px 12px #0002;
    border-left: 6px solid #1976d2;
    display: flex;
    align-items: center;
    justify-content: space-between;
">
  <div>
    <div style="font-size: 1.1rem; color: #1976d2; font-weight: 600, letter-spacing: 1px; margin-bottom: 2px;">
        <span style="vertical-align: middle;">🔄 Em Processamento</span>
    </div>
    <div style="color: #222; font-size: 1.05rem; margin-bottom: 2px;">
        <b>Cliente:</b> {ag['usuario_nome']} &nbsp; | &nbsp;
        <b>Doca:</b> {ag['doca_nome']}
    </div>
    <div style="color: #444; font-size: 0.98rem;">
        <b>Data:</b> {ag['data']} {ag['hora']} &nbsp; | &nbsp;
        <b>Status:</b> <span style="color:#1976d2;">{ag['status']}</span>
    </div>
  </div>
  <div style="text-align: right;">
    <span style="background:#1976d222; color:#1976d2; padding:6px 14px; border-radius:8px; font-weight:600; font-size:0.95rem;">
        ● Em Processamento
    </span>
  </div>
</div>
""", unsafe_allow_html=True)
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("Confirmar", key=f"confirmar_{idx}"):
                        # Quando confirmar
                        atualizar_agendamento_status(ag["id"], "Confirmado")
                        atualizar_status_doca(ag["doca_id"], "Ocupada")
                        st.success("Agendamento confirmado! Doca ocupada.")
                        st.rerun()
                with col2:
                    if st.button("Cancelar", key=f"cancelar_e_{idx}"):
                        atualizar_agendamento_status(ag["id"], "Cancelado")
                        st.warning("Agendamento cancelado!")
                        st.rerun()
                with col3:
                    if st.button("Reagendar", key=f"reagendar_e_{idx}"):
                        st.session_state[f"show_reagendar_e_{idx}"] = not st.session_state.get(f"show_reagendar_e_{idx}", False)
                if st.session_state.get(f"show_reagendar_e_{idx}", False):
                    with st.form(f"form_reagendar_e_{idx}"):
                        import datetime as dt
                        data_val = ag["data"]
                        if isinstance(data_val, str):
                            try:
                                data_val = dt.datetime.strptime(data_val, "%d/%m/%Y").date()
                            except Exception:
                                data_val = dt.date.today()
                        elif isinstance(data_val, dt.datetime):
                            data_val = data_val.date()
                        elif not isinstance(data_val, dt.date):
                            data_val = dt.date.today()
                        hora_val = ag["hora"]
                        if isinstance(hora_val, str):
                            try:
                                hora_val = dt.datetime.strptime(hora_val, "%H:%M").time()
                            except Exception:
                                hora_val = dt.datetime.now().time()
                        elif isinstance(hora_val, dt.datetime):
                            hora_val = hora_val.time()
                        elif not isinstance(hora_val, dt.time):
                            hora_val = dt.datetime.now().time()
                        # Docas alocadas ao cliente deste agendamento
                        docas_cliente = [d["doca_nome"] for d in alocacoes if d["usuario_id"] == ag["usuario_id"]]
                        if not docas_cliente:
                            st.warning("Este cliente não possui docas alocadas.")
                        else:
                            nova_data = st.date_input("Nova data", value=data_val)
                            nova_hora = st.time_input("Nova hora", value=hora_val)
                            nova_doca = st.selectbox("Nova doca", options=docas_cliente, index=docas_cliente.index(ag["doca_nome"]))
                            submit = st.form_submit_button("Salvar Reagendamento")
                            if submit:
                                docas_db = buscar_docas()
                                doca_id = next((d["id"] for d in docas_db if d["nome"] == nova_doca), None)
                                atualizar_agendamento_doca_data_hora(ag["id"], doca_id, nova_data, nova_hora)
                                st.success("Agendamento reagendado!")
                                st.session_state[f"show_reagendar_e_{idx}"] = False
                                st.rerun()

        # Confirmados
        if st.button("Agendamentos Confirmados", key="btn_ag_confirmados"):
            st.session_state.show_ag_confirmados = not st.session_state.show_ag_confirmados
        if st.session_state.show_ag_confirmados:
            for idx, ag in enumerate([a for a in ags_db if a["status"] == "Confirmado"]):
                st.markdown(f"""
<div style="
    background: linear-gradient(90deg, #e0f7fa 60%, #80deea 100%);
    padding: 18px 24px;
    border-radius: 12px;
    margin-bottom: 18px;
    box-shadow: 0 2px 12px #0002;
    border-left: 6px solid #0097a7;
    display: flex;
    align-items: center;
    justify-content: space-between;
">
  <div>
    <div style="font-size: 1.1rem; color: #0097a7; font-weight: 700; letter-spacing: 1px; margin-bottom: 2px;">
        <span style="vertical-align: middle;">📅 Agendamento Confirmado</span>
    </div>
    <div style="color: #222; font-size: 1.05rem; margin-bottom: 2px;">
        <b>Cliente:</b> {ag['usuario_nome']} &nbsp; | &nbsp;
        <b>Doca:</b> {ag['doca_nome']}
    </div>
    <div style="color: #444; font-size: 0.98rem;">
        <b>Data:</b> {ag['data']} {ag['hora']} &nbsp; | &nbsp;
        <b>Status:</b> <span style="color:#0097a7;">{ag['status']}</span>
    </div>
  </div>
  <div style="text-align: right;">
    <span style="background:#0097a722; color:#0097a7; padding:6px 14px; border-radius:8px; font-weight:700; font-size:0.95rem;">
        ● Confirmado
    </span>
  </div>
</div>
""", unsafe_allow_html=True)
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Concluir", key=f"concluir_{idx}"):
                        # Quando concluir
                        atualizar_agendamento_status(ag["id"], "Concluído")
                        atualizar_status_doca(ag["doca_id"], "Livre")
                        st.success("Agendamento concluído e doca liberada!")
                        st.rerun()
                with col2:
                    pass

        # Concluídos
        if st.button("Agendamentos Concluídos", key="btn_ag_concluidos"):
            st.session_state.show_ag_concluidos = not st.session_state.show_ag_concluidos
        if st.session_state.show_ag_concluidos:
            for ag in [a for a in ags_db if a["status"] == "Concluído"]:
                st.markdown(f"""
<div style="
    background: linear-gradient(90deg, #e8f5e9 60%, #a5d6a7 100%);
    padding: 18px 24px;
    border-radius: 12px;
    margin-bottom: 18px;
    box-shadow: 0 2px 12px #0002;
    border-left: 6px solid #388e3c;
    display: flex;
    align-items: center;
    justify-content: space-between;
">
  <div>
    <div style="font-size: 1.1rem; color: #388e3c; font-weight: 600; letter-spacing: 1px; margin-bottom: 2px;">
        <span style="vertical-align: middle;">✅ Agendamento Concluído</span>
    </div>
    <div style="color: #222; font-size: 1.05rem; margin-bottom: 2px;">
        <b>Cliente:</b> {ag['usuario_nome']} &nbsp; | &nbsp;
        <b>Doca:</b> {ag['doca_nome']}
    </div>
    <div style="color: #444; font-size: 0.98rem;">
        <b>Data:</b> {ag['data']} {ag['hora']} &nbsp; | &nbsp;
        <b>Status:</b> <span style="color:#388e3c;">{ag['status']}</span>
    </div>
  </div>
  <div style="text-align: right;">
    <span style="background:#388e3c22; color:#388e3c; padding:6px 14px; border-radius:8px; font-weight:600; font-size:0.95rem;">
        ● Concluído
    </span>
  </div>
</div>
""", unsafe_allow_html=True)

        # Cancelados
        if st.button("Agendamentos Cancelados", key="btn_ag_cancelados"):
            st.session_state.show_ag_cancelados = not st.session_state.show_ag_cancelados
        if st.session_state.show_ag_cancelados:
            for ag in [a for a in ags_db if a["status"] == "Cancelado"]:
                st.markdown(f"""
<div style="
    background: linear-gradient(90deg, #ffebee 60%, #ffcdd2 100%);
    padding: 18px 24px;
    border-radius: 12px;
    margin-bottom: 18px;
    box-shadow: 0 2px 12px #0002;
    border-left: 6px solid #d32f2f;
    display: flex;
    align-items: center;
    justify-content: space-between;
">
  <div>
    <div style="font-size: 1.1rem; color: #d32f2f; font-weight: 600; letter-spacing: 1px; margin-bottom: 2px;">
        <span style="vertical-align: middle;">❌ Agendamento Cancelado</span>
    </div>
    <div style="color: #222; font-size: 1.05rem; margin-bottom: 2px;">
        <b>Cliente:</b> {ag['usuario_nome']} &nbsp; | &nbsp;
        <b>Doca:</b> {ag['doca_nome']}
    </div>
    <div style="color: #444; font-size: 0.98rem;">
        <b>Data:</b> {ag['data']} {ag['hora']} &nbsp; | &nbsp;
        <b>Status:</b> <span style="color:#d32f2f;">{ag['status']}</span>
    </div>
  </div>
  <div style="text-align: right;">
    <span style="background:#d32f2f22; color:#d32f2f; padding:6px 14px; border-radius:8px; font-weight:600; font-size:0.95rem;">
        ● Cancelado
    </span>
  </div>
</div>
""", unsafe_allow_html=True)

    # Botão toggle para gestão de docas
    if st.button("🛠️ Gestão de Docas", key="btn_gestao_docas"):
        st.session_state.show_gestao_docas = not st.session_state.get("show_gestao_docas", False)

    if st.session_state.get("show_gestao_docas", False):
        st.markdown(
            '<h3 style="color:#d0e4f7; font-weight:800; letter-spacing:0.5px; margin-bottom:12px;">Gestão de Docas: Status e Alocação de Clientes</h3>',
            unsafe_allow_html=True
        )

        docas = buscar_docas()
        clientes = buscar_clientes()
        alocacoes = buscar_alocacoes_docas()

        doca_id_para_clientes = {}
        for doca in docas:
            doca_id_para_clientes[doca["id"]] = [
                a["usuario_nome"] for a in alocacoes if a["doca_id"] == doca["id"]
            ]

        for doca in docas:
            cor_borda, cor_grad1, cor_grad2, cor_status, icone, status_legenda = {
                "Livre": ("#388e3c", "#e8f5e9", "#a5d6a7", "#388e3c", "🟢", "Livre"),
                "Ocupada": ("#1976d2", "#e3f2fd", "#90caf9", "#1976d2", "🔵", "Ocupada"),
                "Em preparação": ("#b28704", "#fff9e1", "#ffe082", "#b28704", "🟡", "Em preparação"),
            }.get(doca["status"], ("#b0bec5", "#eceff1", "#b0bec5", "#78909c", "❔", doca["status"]))
            clientes_alocados = doca_id_para_clientes.get(doca["id"], [])
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
                    <span style="vertical-align: middle;">{icone} Doca {doca['nome']}</span>
                </div>
                <div style="color: #444; font-size: 0.98rem;">
                    <b>Status:</b> <span style="color:{cor_status};">{status_legenda}</span>
                </div>
                <div style="color: #444; font-size: 0.98rem;">
                    <b>Clientes alocados:</b> {', '.join(clientes_alocados) if clientes_alocados else 'Nenhum'}
                </div>
              </div>
            </div>
            """, unsafe_allow_html=True)

            clientes_disponiveis = [c for c in clientes if c["nome"] not in clientes_alocados]
            col1, col2 = st.columns(2)
            with col1:
                cliente_sel = st.selectbox(
                    f"Selecionar cliente para alocar na doca {doca['nome']}",
                    options=[""] + [c["nome"] for c in clientes_disponiveis],
                    key=f"select_cliente_{doca['id']}"
                )
                if cliente_sel:
                    usuario_id = next((c["id"] for c in clientes if c["nome"] == cliente_sel), None)
                    if usuario_id and st.button(f"Alocar {cliente_sel} em {doca['nome']}", key=f"alocar_{cliente_sel}_{doca['id']}"):
                        alocar_doca_cliente(doca["id"], usuario_id)
                        st.success(f"Cliente {cliente_sel} alocado em {doca['nome']}.")
                        st.rerun()
            with col2:
                if clientes_alocados:
                    cliente_remover = st.selectbox(
                        f"Remover cliente da doca {doca['nome']}",
                        options=[""] + clientes_alocados,
                        key=f"remover_cliente_{doca['id']}"
                    )
                    if cliente_remover:
                        usuario_id = next((c["id"] for c in clientes if c["nome"] == cliente_remover), None)
                        if usuario_id and st.button(f"Remover {cliente_remover} de {doca['nome']}", key=f"remover_{cliente_remover}_{doca['id']}"):
                            desalocar_doca_cliente(doca["id"], usuario_id)
                            st.warning(f"Cliente {cliente_remover} removido de {doca['nome']}.")
                            st.rerun()
            st.divider()

    # Botão toggle para encomendas
    if st.button("📦 Ver Encomendas", key="btn_encomendas_gestor"):
        st.session_state.show_encomendas_gestor = not st.session_state.show_encomendas_gestor

    if st.session_state.show_encomendas_gestor:
        st.markdown(
        '<h3 style="color:#d0e4f7; font-weight:800; letter-spacing:0.5px; margin-bottom:12px;">Todas as Encomendas:</h3>',
        unsafe_allow_html=True
    )
        status_options = ["Todas", "Pendente", "Em Processamento", "Processada", "Cancelada"]
        st.session_state.filtro_encomenda_status = st.selectbox(
            "Filtrar por status:",
            status_options,
            index=status_options.index(st.session_state.filtro_encomenda_status),
            key="filtro_encomenda_status_select"
        )
        encomendas_db = buscar_encomendas()
        # Buscar nomes dos clientes para cada encomenda
        usuarios = {u["id"]: u["nome"] for u in buscar_clientes()}
        if st.session_state.filtro_encomenda_status == "Todas":
            encomendas_filtradas = encomendas_db
        else:
            encomendas_filtradas = [e for e in encomendas_db if e["status"] == st.session_state.filtro_encomenda_status]

        if not encomendas_filtradas:
            st.info("Nenhuma encomenda encontrada para o filtro selecionado.")
        else:
            for encomenda in encomendas_filtradas:
                cor_borda, cor_grad1, cor_grad2, cor_status, icone, status_legenda = {
                    "Pendente":   ("#b28704", "#fff9e1", "#ffe082", "#b28704", "📦", "Pendente"),
                    "Em Processamento": ("#1976d2", "#e3f2fd", "#90caf9", "#1976d2", "🔄", "Em Processamento"),
                    "Processada": ("#388e3c", "#e8f5e9", "#a5d6a7", "#388e3c", "✅", "Processada"),
                    "Cancelada":  ("#d32f2f", "#ffebee", "#ffcdd2", "#d32f2f", "❌", "Cancelada"),
                }[encomenda["status"]]

                cancelar_key = f"cancelar_gestor_{encomenda['id']}"

                cliente_nome = usuarios.get(encomenda["usuario_id"], "Desconhecido")

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
                        <b>ID:</b> {encomenda['id']} &nbsp; | &nbsp;
                        <b>Cliente:</b> {cliente_nome}
                    </div>
                    <div style="color: #444; font-size: 0.98rem;">
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

                # Botão funcional de cancelar encomenda (apenas se Pendente ou Em Processamento)
                if encomenda["status"] in ["Pendente", "Em Processamento"]:
                    if st.button("Cancelar", key=cancelar_key):
                        cancelar_encomenda(encomenda["id"])
                        st.warning("Encomenda cancelada!")
                        st.rerun()

    # Painel de alertas
    if st.button("⚠️ Ver Alertas", key="btn_alertas_gestor"):
        st.session_state.show_alertas_gestor = not st.session_state.show_alertas_gestor
    if "show_alertas_resolvidos" not in st.session_state:
        st.session_state.show_alertas_resolvidos = False

    if st.session_state.show_alertas_gestor:
        st.markdown(
        '<h3 style="color:#d0e4f7; font-weight:800; letter-spacing:0.5px; margin-bottom:12px;">Painel de Alertas Gerais</h3>',
        unsafe_allow_html=True
    )
        for idx, alerta in enumerate([a for a in alertas if a.get("status", "Ativo") == "Ativo"]):
            cor_borda = "#d32f2f"
            cor_grad1 = "#ffebee"
            cor_grad2 = "#ffcdd2"
            icone = "⏰" if alerta.get("tipo") == "Atraso" else "⚠️"
            resolver_key = f"resolver_alerta_{idx}"

            col1, col2 = st.columns([8, 1])
            with col1:
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
                    <div style="font-size: 1.05rem; color: {cor_borda}; font-weight: 700; margin-bottom: 2px;">
                        <span style="vertical-align: middle;">{icone} {alerta['mensagem']}</span>
                    </div>
                    <div style="color: #555; font-size: 0.97rem;">
                        <b>Doca:</b> {alerta.get('doca_nome', 'N/A')} &nbsp; | &nbsp; <b>Data:</b> {alerta['timestamp']}
                    </div>
                  </div>
                  <div style="text-align: right;">
                    <span style="background:{cor_borda}22; color:{cor_borda}; padding:5px 12px; border-radius:7px; font-weight:600; font-size:0.93rem;">
                        {alerta['tipo']}
                    </span>
                  </div>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                if st.button("Resolver", key=resolver_key):
                    resolver_alerta(alerta["id"], usuario)
                    st.success("Alerta resolvido!")
                    st.rerun()

        # Sub-botão para mostrar alertas resolvidos
        if st.button("🔽 Alertas Resolvidos", key="btn_alertas_resolvidos"):
            st.session_state.show_alertas_resolvidos = not st.session_state.show_alertas_resolvidos

        if st.session_state.show_alertas_resolvidos:
            st.markdown(
        '<h3 style="color:#d0e4f7; font-weight:800; letter-spacing:0.5px; margin-bottom:12px;">Alertas Resolvidos</h3>',
        unsafe_allow_html=True
    )
            for alerta in [a for a in alertas if a.get("status", "Ativo") == "Resolvido"]:
                resolvido_por = alerta.get("resolvido_por", "Desconhecido")
                resolvido_em = alerta.get("resolvido_em", "Data desconhecida")
                st.markdown(
                    f"""
                    <div style="background-color:#e1f5fe;padding:10px;border-radius:5px;margin-bottom:8px;">
                        <b>{alerta['mensagem']}</b> (Doca {alerta.get('doca_nome', 'N/A')}) - {alerta['timestamp']}<br>
                        <small>Resolvido por: {resolvido_por} em {resolvido_em}</small>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    if "show_metricas_gestor" not in st.session_state:
        st.session_state.show_metricas_gestor = False

    if st.button("📈 Ver Painel de Métricas", key="btn_metricas_gestor"):
        st.session_state.show_metricas_gestor = not st.session_state.show_metricas_gestor

    if st.session_state.show_metricas_gestor:
        painel_metricas()

    st.divider()
    st.markdown(
    f'<div style="color:#90caf9; font-size:0.98rem; margin-top:24px; text-align:right;">Utilizador: <b>ID:</b> {st.session_state.nome} &nbsp;|&nbsp; <b>Email:</b> {usuario}</div>',
    unsafe_allow_html=True
)

    if st.button("🔓 Sair"):
        st.session_state.logado = False
        st.rerun()

def painel_metricas():
    st.markdown(
        '<h3 style="color:#d0e4f7; font-weight:800; letter-spacing:0.5px; margin-bottom:12px;">📈 Painel de Métricas / KPIs:</h3>',
        unsafe_allow_html=True
    )

    ags = buscar_agendamentos()
    df = pd.DataFrame(ags)

    if not df.empty and "confirmado_em" in df.columns and "finalizado_em" in df.columns:
        df_concluidos = df[(df["status"] == "Concluído") & df["confirmado_em"].notnull() & df["finalizado_em"].notnull()].copy()
        if not df_concluidos.empty:
            df_concluidos["confirmado_em"] = pd.to_datetime(df_concluidos["confirmado_em"])
            df_concluidos["finalizado_em"] = pd.to_datetime(df_concluidos["finalizado_em"])
            df_concluidos["duracao"] = (df_concluidos["finalizado_em"] - df_concluidos["confirmado_em"]).dt.total_seconds() / 3600
            tempo_medio = df_concluidos["duracao"].mean()
            st.metric("Tempo médio de ocupação (h)", f"{tempo_medio:.2f}" if tempo_medio else "N/A")
        else:
            st.metric("Tempo médio de ocupação (h)", "N/A")
    else:
        st.metric("Tempo médio de ocupação (h)", "N/A")

    if not df.empty and "status" in df.columns:
        status_counts = df["status"].value_counts()
        st.markdown(
        '<h3 style="color:#d0e4f7; font-weight:200; letter-spacing:0.5px; margin-bottom:2px;">Quantidade de Agendamento por Status:</h3>',
        unsafe_allow_html=True
    )
        st.dataframe(status_counts.rename_axis('Status').reset_index(name='Quantidade'))
    else:
        st.write("Nenhum agendamento cadastrado.")

    # Corrigido: buscar alertas do banco, não de ALERTAS em memória
    alertas = buscar_alertas()
    atrasos = [a for a in alertas if a.get("tipo") == "Atraso" and a.get("status") == "Ativo"]
    st.metric("Agendamentos em atraso", len(atrasos))

    if not df.empty and "doca_nome" in df.columns:
        doca_counts = df["doca_nome"].value_counts()
        st.markdown(
        '<h3 style="color:#d0e4f7; font-weight:200; letter-spacing:0.5px; margin-bottom:2px;">Utilização de cada doca:</h3>',
        unsafe_allow_html=True
    )
        st.dataframe(doca_counts.rename_axis('Doca').reset_index(name='Quantidade'))

    st.markdown(
        '<h3 style="color:#d0e4f7; font-weight:800; letter-spacing:0.5px; margin-bottom:12px;">Exportar Relatório de Agendamentos</h3>',
        unsafe_allow_html=True
    )
    export_df = df.copy()
    if st.button("Exportar para Excel"):
        export_df.to_excel("relatorio_agendamentos.xlsx", index=False)
        st.success("Relatório exportado como relatorio_agendamentos.xlsx")
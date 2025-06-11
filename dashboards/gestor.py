import streamlit as st
from utils.auth import verificar_autenticacao
from utils.dados import AGENDAMENTOS, ALERTAS, DOCAS, ENCOMENDAS, CLIENTES
from datetime import datetime, timedelta
import pandas as pd
from streamlit_option_menu import option_menu

def render():

    st.markdown("""
<style>
/* Altera cor e estilo dos labels dos campos de seleção */
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

    # Aplica fundo escuro e agradável ao dashboard do gestor
    st.markdown("""
    <style>
    body, .stApp {
        background: linear-gradient(120deg, #232946 0%, #394867 100%) !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # Cabeçalho visual padronizado do dashboard gestor
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
            <span style="color:#222; font-size:1.13rem;">Bem-vindo, <b>{st.session_state.usuario}</b>!</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    usuario = st.session_state.usuario

    # --- Lógica temporal para atrasos em agendamentos confirmados ---
    for ag in AGENDAMENTOS:
        if ag.get("status") == "Confirmado" and ag.get("confirmado_em"):
            confirmado_em = datetime.strptime(ag["confirmado_em"], "%d/%m/%Y %H:%M")
            if datetime.now() - confirmado_em > timedelta(hours=2):
                # Verifica se já existe alerta para esse agendamento
                alerta_existente = any(
                    a for a in ALERTAS
                    if a.get("tipo") == "Atraso" and a.get("agendamento_id") == id(ag) and a.get("status", "Ativo") == "Ativo"
                )
                if not alerta_existente:
                    ALERTAS.append({
                        "mensagem": f"Atraso na conclusão do agendamento do cliente {ag['cliente']} na doca {ag['doca']}",
                        "doca": ag["doca"],
                        "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M"),
                        "status": "Ativo",
                        "tipo": "Atraso",
                        "agendamento_id": id(ag)
                    })

    # --- Lógica de conflito: gerar alerta ao detectar conflito em pendentes ---
    for ag in AGENDAMENTOS:
        if ag["status"] == "Pendente":
            conflito = any(
                a for a in AGENDAMENTOS
                if a is not ag and
                   a["doca"] == ag["doca"] and
                   a["data"] == ag["data"] and
                   a["hora"] == ag["hora"] and
                   a["status"] in ["Pendente", "Em Processamento", "Confirmado"]
            )
            alerta_existente = any(
                a for a in ALERTAS
                if a.get("tipo") == "Conflito" and a.get("agendamento_id") == id(ag) and a.get("status", "Ativo") == "Ativo"
            )
            if conflito and not alerta_existente:
                ALERTAS.append({
                    "mensagem": f"Conflito de agendamento para doca {ag['doca']} em {ag['data']} {ag['hora']}",
                    "doca": ag["doca"],
                    "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M"),
                    "status": "Ativo",
                    "tipo": "Conflito",
                    "agendamento_id": id(ag)
                })

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

    # Inicializa toggles para cada estado de agendamento
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
        # Pendentes
        if st.button("Agendamentos Pendentes", key="btn_ag_pendentes"):
            st.session_state.show_ag_pendentes = not st.session_state.show_ag_pendentes
        if st.session_state.show_ag_pendentes:
            for idx, ag in enumerate([a for a in AGENDAMENTOS if a["status"] == "Pendente"]):
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
        <b>Cliente:</b> {ag['cliente']} &nbsp; | &nbsp;
        <b>Doca:</b> {ag['doca']}
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
                    # Aprovar só se não houver conflito
                    conflito = any(
                        a for a in AGENDAMENTOS
                        if a is not ag and
                           a["doca"] == ag["doca"] and
                           a["data"] == ag["data"] and
                           a["hora"] == ag["hora"] and
                           a["status"] in ["Pendente", "Em Processamento", "Confirmado"]
                    )
                    if st.button("Aprovar", key=f"aprovar_{idx}"):
                        if conflito:
                            st.error("Não é possível aprovar: existe conflito de agendamento para esta doca, data e hora!")
                        else:
                            ag["status"] = "Em Processamento"
                            DOCAS[ag["doca"]]["status"] = "Em preparação"
                            st.success("Agendamento aprovado! Doca em preparação.")
                            st.rerun()
                with col2:
                    if st.button("Cancelar", key=f"cancelar_p_{idx}"):
                        ag["status"] = "Cancelado"
                        st.warning("Agendamento cancelado!")
                        st.rerun()
                with col3:
                    if st.button("Reagendar", key=f"reagendar_p_{idx}"):
                        st.session_state[f"show_reagendar_{idx}"] = not st.session_state.get(f"show_reagendar_{idx}", False)
                if st.session_state.get(f"show_reagendar_{idx}", False):
                    with st.form(f"form_reagendar_{idx}"):
                        nova_data = st.date_input("Nova data", value=datetime.strptime(ag["data"], "%d/%m/%Y"))
                        nova_hora = st.time_input("Nova hora", value=datetime.strptime(ag["hora"], "%H:%M").time())
                        nova_doca = st.selectbox("Nova doca", options=list(DOCAS.keys()), index=list(DOCAS.keys()).index(ag["doca"]))
                        submit = st.form_submit_button("Salvar Reagendamento")
                        if submit:
                            ag["data"] = nova_data.strftime("%d/%m/%Y")
                            ag["hora"] = nova_hora.strftime("%H:%M")
                            ag["doca"] = nova_doca
                            st.success("Agendamento reagendado!")
                            st.session_state[f"show_reagendar_{idx}"] = False
                            st.rerun()

        # Em Processamento
        if st.button("Agendamentos em Processamento", key="btn_ag_processando"):
            st.session_state.show_ag_processando = not st.session_state.show_ag_processando
        if st.session_state.show_ag_processando:
            for idx, ag in enumerate([a for a in AGENDAMENTOS if a["status"] == "Em Processamento"]):
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
        <b>Cliente:</b> {ag['cliente']} &nbsp; | &nbsp;
        <b>Doca:</b> {ag['doca']}
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
                    # Confirmar
                    if st.button("Confirmar", key=f"confirmar_{idx}"):
                        ag["status"] = "Confirmado"
                        ag["confirmado_em"] = datetime.now().strftime("%d/%m/%Y %H:%M")
                        DOCAS[ag["doca"]]["status"] = "Ocupada"
                        st.success("Agendamento confirmado! Doca ocupada.")
                        st.rerun()
                with col2:
                    # Cancelar
                    if st.button("Cancelar", key=f"cancelar_e_{idx}"):
                        ag["status"] = "Cancelado"
                        # Atualiza encomendas relacionadas
                        for encomenda in ENCOMENDAS:
                            if encomenda.get("agendamento_idx") == idx and encomenda["status"] == "Em Processamento":
                                encomenda["status"] = "Pendente"
                                encomenda["agendamento_idx"] = None
                                if "historico" not in encomenda:
                                    encomenda["historico"] = []
                                encomenda["historico"].append({
                                    "acao": "Desalocada automaticamente ao cancelar agendamento",
                                    "data": datetime.now().strftime("%d/%m/%Y %H:%M")
                                })
                        st.warning("Agendamento cancelado!")
                        st.rerun()
                with col3:
                    # Reagendar
                    if st.button("Reagendar", key=f"reagendar_e_{idx}"):
                        st.session_state[f"show_reagendar_e_{idx}"] = not st.session_state.get(f"show_reagendar_e_{idx}", False)
                if st.session_state.get(f"show_reagendar_e_{idx}", False):
                    with st.form(f"form_reagendar_e_{idx}"):
                        nova_data = st.date_input("Nova data", value=datetime.strptime(ag["data"], "%d/%m/%Y"))
                        nova_hora = st.time_input("Nova hora", value=datetime.strptime(ag["hora"], "%H:%M").time())
                        nova_doca = st.selectbox("Nova doca", options=list(DOCAS.keys()), index=list(DOCAS.keys()).index(ag["doca"]))
                        submit = st.form_submit_button("Salvar Reagendamento")
                        if submit:
                            ag["data"] = nova_data.strftime("%d/%m/%Y")
                            ag["hora"] = nova_hora.strftime("%H:%M")
                            ag["doca"] = nova_doca
                            ag["status"] = "Pendente"
                            st.success("Agendamento reagendado e voltou para Pendente!")
                            st.session_state[f"show_reagendar_e_{idx}"] = False
                            st.rerun()

        # Confirmados
        if st.button("Agendamentos Confirmados", key="btn_ag_confirmados"):
            st.session_state.show_ag_confirmados = not st.session_state.show_ag_confirmados
        if st.session_state.show_ag_confirmados:
            for idx, ag in enumerate([a for a in AGENDAMENTOS if a["status"] == "Confirmado"]):
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
        <b>Cliente:</b> {ag['cliente']} &nbsp; | &nbsp;
        <b>Doca:</b> {ag['doca']}
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
                        ag["status"] = "Concluído"
                        ag["finalizado_em"] = datetime.now().strftime("%d/%m/%Y %H:%M")
                        # Atualiza encomendas relacionadas
                        for encomenda in ENCOMENDAS:
                            if encomenda.get("agendamento_idx") == idx and encomenda["status"] == "Em Processamento":
                                encomenda["status"] = "Processada"
                                if "historico" not in encomenda:
                                    encomenda["historico"] = []
                                encomenda["historico"].append({
                                    "acao": "Processada ao concluir agendamento pelo gestor",
                                    "data": datetime.now().strftime("%d/%m/%Y %H:%M")
                                })
                        # Libera a doca se não houver outro agendamento confirmado ou em processamento para ela
                        doca_id = ag["doca"]
                        outros_agendamentos = [
                            a for a in AGENDAMENTOS
                            if a["doca"] == doca_id and a["status"] in ["Confirmado", "Em Processamento"] and a is not ag
                        ]
                        if not outros_agendamentos:
                            DOCAS[doca_id]["status"] = "Livre"
                        st.success("Agendamento concluído e doca liberada!")
                        st.rerun()
                with col2:
                    # (Opcional: mostrar detalhes, histórico, etc.)
                    pass

        # Concluídos
        if st.button("Agendamentos Concluídos", key="btn_ag_concluidos"):
            st.session_state.show_ag_concluidos = not st.session_state.get("show_ag_concluidos", False)
        if st.session_state.get("show_ag_concluidos", False):
            for ag in [a for a in AGENDAMENTOS if a["status"] == "Concluído"]:
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
        <b>Cliente:</b> {ag['cliente']} &nbsp; | &nbsp;
        <b>Doca:</b> {ag['doca']}
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
            for ag in [a for a in AGENDAMENTOS if a["status"] == "Cancelado"]:
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
        <b>Cliente:</b> {ag['cliente']} &nbsp; | &nbsp;
        <b>Doca:</b> {ag['doca']}
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

    # Botão toggle para gestão de docas (substitui o antigo "Ver Docas")
    if st.button("🛠️ Gestão de Docas", key="btn_gestao_docas"):
        st.session_state.show_gestao_docas = not st.session_state.get("show_gestao_docas", False)

    if st.session_state.get("show_gestao_docas", False):
        st.markdown(
        '<h3 style="color:#d0e4f7; font-weight:800; letter-spacing:0.5px; margin-bottom:12px;">Gestão de Docas: Status e Alocação de Clientes</h3>',
        unsafe_allow_html=True
    )

        # Inicializa estrutura de alocação se não existir
        if "alocacoes_docas" not in st.session_state:
            st.session_state.alocacoes_docas = {doca: [] for doca in DOCAS}
            for cliente, info in CLIENTES.items():
                for doca in info["docas"]:
                    if doca in st.session_state.alocacoes_docas:
                        st.session_state.alocacoes_docas[doca].append(cliente)

        st.markdown(
        '<h3 style="color:#d0e4f7; font-weight:50; letter-spacing:0.5px; margin-bottom:0.5px;">Altere as alocações conforme necessário:</h3>',
        unsafe_allow_html=True
    )

        for doca, info in DOCAS.items():
            cor_borda, cor_grad1, cor_grad2, cor_status, icone, status_legenda = {
                "Livre": ("#388e3c", "#e8f5e9", "#a5d6a7", "#388e3c", "🟢", "Livre"),
                "Ocupada": ("#1976d2", "#e3f2fd", "#90caf9", "#1976d2", "🔵", "Ocupada"),
                "Em preparação": ("#b28704", "#fff9e1", "#ffe082", "#b28704", "🟡", "Em preparação"),
            }[info["status"]]
            clientes_alocados = st.session_state.alocacoes_docas.get(doca, [])
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
                    <span style="vertical-align: middle;">{icone} Doca {doca}</span>
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

            # Selecionar cliente para alocar
            clientes_disponiveis = [c for c in CLIENTES if c not in clientes_alocados]
            col1, col2 = st.columns(2)
            with col1:
                cliente_sel = st.selectbox(
                    f"Selecionar cliente para alocar na doca {doca}",
                    options=[""] + clientes_disponiveis,
                    key=f"select_cliente_{doca}"
                )
                if cliente_sel:
                    if st.button(f"Alocar {cliente_sel} em {doca}", key=f"alocar_{cliente_sel}_{doca}"):
                        st.session_state.alocacoes_docas[doca].append(cliente_sel)
                        st.success(f"Cliente {cliente_sel} alocado em {doca}.")
                        st.rerun()
            with col2:
                if clientes_alocados:
                    cliente_remover = st.selectbox(
                        f"Remover cliente da doca {doca}",
                        options=[""] + clientes_alocados,
                        key=f"remover_cliente_{doca}"
                    )
                    if cliente_remover:
                        if st.button(f"Remover {cliente_remover} de {doca}", key=f"remover_{cliente_remover}_{doca}"):
                            st.session_state.alocacoes_docas[doca].remove(cliente_remover)
                            st.warning(f"Cliente {cliente_remover} removido de {doca}.")
                            st.rerun()
            st.divider()

    # Sincroniza status das docas com os agendamentos mais recentes
    for doca_id in DOCAS.keys():
        ags_doca = [a for a in AGENDAMENTOS if a["doca"] == doca_id]
        ags_doca.sort(key=lambda x: (x["data"], x["hora"]), reverse=True)
        for ag in ags_doca:
            if ag["status"] == "Confirmado":
                DOCAS[doca_id]["status"] = "Ocupada"
                break
            elif ag["status"] == "Em Processamento":
                DOCAS[doca_id]["status"] = "Em preparação"
                break
        else:
            DOCAS[doca_id]["status"] = "Livre"  # Sempre define como Livre se não houver agendamento relevant

    # Botão toggle para encomendas (coloque antes do rodapé e botão sair)
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
        if st.session_state.filtro_encomenda_status == "Todas":
            encomendas_filtradas = ENCOMENDAS
        else:
            encomendas_filtradas = [e for e in ENCOMENDAS if e["status"] == st.session_state.filtro_encomenda_status]

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
                        <b>Cliente:</b> {encomenda['cliente']}
                    </div>
                    <div style="color: #444; font-size: 0.98rem;">
                        <b>Descrição:</b> {encomenda['descricao']}
                    </div>
                    <div style="color: #444; font-size: 0.98rem;">
                        <b>Status:</b> <span style="color:{cor_status};">{encomenda['status']}</span>
                    </div>
                    {"<div style='color:#444;font-size:0.98rem;'><b>Agendamento:</b> " +
                        f"{AGENDAMENTOS[encomenda['agendamento_idx']]['data']} {AGENDAMENTOS[encomenda['agendamento_idx']]['hora']} | Doca {AGENDAMENTOS[encomenda['agendamento_idx']]['doca']} | Status: {AGENDAMENTOS[encomenda['agendamento_idx']]['status']}" +
                        "</div>" if encomenda.get("agendamento_idx") is not None else ""}
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
                        encomenda["status"] = "Cancelada"
                        encomenda["agendamento_idx"] = None
                        if "historico" not in encomenda:
                            encomenda["historico"] = []
                        encomenda["historico"].append({
                            "acao": "Cancelada pelo gestor",
                            "data": datetime.now().strftime("%d/%m/%Y %H:%M")
                        })
                        st.warning("Encomenda cancelada!")
                        st.rerun()

                # Histórico da encomenda
                if "historico" in encomenda and encomenda["historico"]:
                    with st.expander("Histórico da Encomenda"):
                        for h in encomenda["historico"]:
                            st.markdown(f"- {h['acao']} em {h['data']}")

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
        for idx, alerta in enumerate([a for a in ALERTAS if a.get("status", "Ativo") == "Ativo"]):
            cor_borda = "#d32f2f"  # Vermelho forte para todos os alertas
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
                        <b>Doca:</b> {alerta['doca']} &nbsp; | &nbsp; <b>Data:</b> {alerta['timestamp']}
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
                    alerta["status"] = "Resolvido"
                    alerta["resolvido_por"] = f"Gestor ({usuario})"
                    alerta["resolvido_em"] = datetime.now().strftime("%d/%m/%Y %H:%M")
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
            for alerta in [a for a in ALERTAS if a.get("status", "Ativo") == "Resolvido"]:
                resolvido_por = alerta.get("resolvido_por", "Desconhecido")
                resolvido_em = alerta.get("resolvido_em", "Data desconhecida")
                st.markdown(
                    f"""
                    <div style="background-color:#e1f5fe;padding:10px;border-radius:5px;margin-bottom:8px;">
                        <b>{alerta['mensagem']}</b> (Doca {alerta['doca']}) - {alerta['timestamp']}<br>
                        <small>Resolvido por: {resolvido_por} em {resolvido_em}</small>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

# Painel de Métricas/KPIs
    if "show_metricas_gestor" not in st.session_state:
        st.session_state.show_metricas_gestor = False

    if st.button("📈 Ver Painel de Métricas", key="btn_metricas_gestor"):
        st.session_state.show_metricas_gestor = not st.session_state.show_metricas_gestor

    if st.session_state.show_metricas_gestor:
        painel_metricas()

    st.divider()
    st.markdown(
    f'<div style="color:#90caf9; font-size:0.98rem; margin-top:24px; text-align:right;">Utilizador: <b>ID:</b> {usuario} &nbsp;|&nbsp; <b>Email:</b> {usuario}@cliente.smid</div>',
    unsafe_allow_html=True
)

    if st.button("🔓 Sair"):
        st.session_state.logado = False
        st.rerun()

# Painel de Métricas/KPIs
def painel_metricas():
    st.markdown(
        '<h3 style="color:#d0e4f7; font-weight:800; letter-spacing:0.5px; margin-bottom:12px;">📈 Painel de Métricas / KPIs:</h3>',
        unsafe_allow_html=True
    )

    # DataFrame dos agendamentos
    df = pd.DataFrame(AGENDAMENTOS)

    # Tempo médio de ocupação das docas (apenas agendamentos concluídos)
    if not df.empty and "confirmado_em" in df.columns and "finalizado_em" in df.columns:
        df_concluidos = df[(df["status"] == "Concluído") & df["confirmado_em"].notnull() & df["finalizado_em"].notnull()].copy()
        if not df_concluidos.empty:
            df_concluidos["confirmado_em"] = pd.to_datetime(df_concluidos["confirmado_em"], format="%d/%m/%Y %H:%M")
            df_concluidos["finalizado_em"] = pd.to_datetime(df_concluidos["finalizado_em"], format="%d/%m/%Y %H:%M")
            df_concluidos["duracao"] = (df_concluidos["finalizado_em"] - df_concluidos["confirmado_em"]).dt.total_seconds() / 3600
            tempo_medio = df_concluidos["duracao"].mean()
            st.metric("Tempo médio de ocupação (h)", f"{tempo_medio:.2f}" if tempo_medio else "N/A")
        else:
            st.metric("Tempo médio de ocupação (h)", "N/A")
    else:
        st.metric("Tempo médio de ocupação (h)", "N/A")

    # Número de agendamentos por status
    if not df.empty and "status" in df.columns:
        status_counts = df["status"].value_counts()
        st.markdown(
        '<h3 style="color:#d0e4f7; font-weight:200; letter-spacing:0.5px; margin-bottom:2px;">Quantidade de Agendamento por Status:</h3>',
        unsafe_allow_html=True
    )
        st.dataframe(status_counts.rename_axis('Status').reset_index(name='Quantidade'))
    else:
        st.write("Nenhum agendamento cadastrado.")

    # Quantidade de atrasos
    atrasos = [a for a in ALERTAS if a.get("tipo") == "Atraso" and a.get("status") == "Ativo"]
    st.metric("Agendamentos em atraso", len(atrasos))

    # Utilização de cada doca
    if not df.empty and "doca" in df.columns:
        doca_counts = df["doca"].value_counts()
        st.markdown(
        '<h3 style="color:#d0e4f7; font-weight:200; letter-spacing:0.5px; margin-bottom:2px;">Utilização de cada doca:</h3>',
        unsafe_allow_html=True
    )
        st.dataframe(doca_counts.rename_axis('Doca').reset_index(name='Quantidade'))

    # Exportar relatório
    st.markdown(
        '<h3 style="color:#d0e4f7; font-weight:800; letter-spacing:0.5px; margin-bottom:12px;">Exportar Relatório de Agendamentos</h3>',
        unsafe_allow_html=True
    )
    export_df = df.copy()
    if st.button("Exportar para Excel"):
        export_df.to_excel("relatorio_agendamentos.xlsx", index=False)
        st.success("Relatório exportado como relatorio_agendamentos.xlsx")
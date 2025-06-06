import streamlit as st
from utils.auth import verificar_autenticacao
from utils.dados import AGENDAMENTOS, ALERTAS, DOCAS, ENCOMENDAS
from datetime import datetime

def render():
    if not verificar_autenticacao("gestor"):
        st.stop()

    st.title("📊 Dashboard do Gestor")
    usuario = st.session_state.usuario

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

    # Botão toggle para agendamentos
    if st.button("📅 Ver Agendamentos", key="btn_agendamentos_gestor"):
        st.session_state.show_agendamentos_gestor = not st.session_state.show_agendamentos_gestor

    if st.session_state.show_agendamentos_gestor:
        # Pendentes
        st.subheader("Agendamentos Pendentes")
        for idx, ag in enumerate([a for a in AGENDAMENTOS if a["status"] == "Pendente"]):
            st.write(f"Cliente: {ag['cliente']} | Doca: {ag['doca']} | {ag['data']} {ag['hora']} | Status: {ag['status']}")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Aprovar", key=f"aprovar_{idx}"):
                    ag["status"] = "Em Processamento"
                    DOCAS[ag["doca"]]["status"] = "Em preparação"
                    st.success("Agendamento aprovado! Doca em preparação.")
                    st.rerun()
            with col2:
                if st.button("Cancelar", key=f"cancelar_p_{idx}"):
                    ag["status"] = "Cancelado"
                    st.warning("Agendamento cancelado!")
                    st.rerun()

        # Em Processamento
        st.subheader("Agendamentos em Processamento")
        for idx, ag in enumerate([a for a in AGENDAMENTOS if a["status"] == "Em Processamento"]):
            st.write(f"Cliente: {ag['cliente']} | Doca: {ag['doca']} | {ag['data']} {ag['hora']} | Status: {ag['status']}")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Confirmar", key=f"confirmar_{idx}"):
                    ag["status"] = "Confirmado"
                    DOCAS[ag["doca"]]["status"] = "Ocupada"
                    # Atualiza encomendas relacionadas
                    for encomenda in ENCOMENDAS:
                        if encomenda.get("agendamento_idx") == idx and encomenda["status"] == "Em Processamento":
                            encomenda["status"] = "Processada"
                            if "historico" not in encomenda:
                                encomenda["historico"] = []
                            encomenda["historico"].append({
                                "acao": "Processada automaticamente ao confirmar agendamento",
                                "data": datetime.now().strftime("%d/%m/%Y %H:%M")
                            })
                    st.success("Agendamento confirmado! Doca ocupada.")
                    st.rerun()
            with col2:
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

        # Confirmados
        st.subheader("Agendamentos Confirmados")
        for ag in [a for a in AGENDAMENTOS if a["status"] == "Confirmado"]:
            st.write(f"Cliente: {ag['cliente']} | Doca: {ag['doca']} | {ag['data']} {ag['hora']} | Status: {ag['status']}")

        # Cancelados
        st.subheader("Agendamentos Cancelados")
        for ag in [a for a in AGENDAMENTOS if a["status"] == "Cancelado"]:
            st.write(f"Cliente: {ag['cliente']} | Doca: {ag['doca']} | {ag['data']} {ag['hora']} | Status: {ag['status']}")

    # Botão toggle para alertas
    if st.button("⚠️ Ver Alertas", key="btn_alertas_gestor"):
        st.session_state.show_alertas_gestor = not st.session_state.show_alertas_gestor
    if "show_alertas_resolvidos" not in st.session_state:
        st.session_state.show_alertas_resolvidos = False

    if st.session_state.show_alertas_gestor:
        st.subheader("Painel de Alertas Gerais")
        for idx, alerta in enumerate([a for a in ALERTAS if a.get("status", "Ativo") == "Ativo"]):
            cols = st.columns([6, 1])
            with cols[0]:
                st.error(f"{alerta['mensagem']} (Doca {alerta['doca']}) - {alerta['timestamp']}")
            with cols[1]:
                if st.button("Resolver", key=f"resolver_alerta_{idx}"):
                    alerta["status"] = "Resolvido"
                    alerta["resolvido_por"] = f"Gestor ({usuario})"
                    alerta["resolvido_em"] = datetime.now().strftime("%d/%m/%Y %H:%M")
                    st.success("Alerta resolvido!")
                    st.rerun()

        # Sub-botão para mostrar alertas resolvidos
        if st.button("🔽 Alertas Resolvidos", key="btn_alertas_resolvidos"):
            st.session_state.show_alertas_resolvidos = not st.session_state.show_alertas_resolvidos

        if st.session_state.show_alertas_resolvidos:
            st.subheader("Alertas Resolvidos")
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

    # Botão toggle para docas
    if st.button("🔎 Ver Docas", key="btn_docas_gestor"):
        st.session_state.show_docas_gestor = not st.session_state.show_docas_gestor

    if st.session_state.show_docas_gestor:
        st.subheader("Status das Docas")
        for doca_id, doca in DOCAS.items():
            st.info(f"Doca {doca_id}: {doca['status']}")

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
            DOCAS[doca_id]["status"] = "Livre"  # Sempre define como Livre se não houver agendamento relevante

    # Botão toggle para encomendas (coloque antes do rodapé e botão sair)
    if st.button("📦 Ver Encomendas", key="btn_encomendas_gestor"):
        st.session_state.show_encomendas_gestor = not st.session_state.show_encomendas_gestor

    if st.session_state.show_encomendas_gestor:
        st.subheader("Todas as Encomendas")
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
                st.markdown(f"**ID:** {encomenda['id']}")
                st.markdown(f"**Descrição:** {encomenda['descricao']}")
                st.markdown(f"**Cliente:** {encomenda['cliente']}")
                st.markdown(f"**Status atual:** {encomenda['status']}")
                # Mostrar agendamento associado, se houver
                if encomenda["agendamento_idx"] is not None:
                    ag = AGENDAMENTOS[encomenda["agendamento_idx"]]
                    st.markdown(
                        f"**Agendamento:** {ag['data']} {ag['hora']} | Doca {ag['doca']} | Status: {ag['status']}"
                    )
                # Cancelar encomenda (apenas se Pendente ou Em Processamento)
                if encomenda["status"] in ["Pendente", "Em Processamento"]:
                    if st.button("Cancelar Encomenda", key=f"cancelar_gestor_{encomenda['id']}"):
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
                st.divider()

    st.divider()
    st.caption(f"Utilizador: ID: {usuario} | Email: {usuario}@manager.smid")

    if st.button("🔓 Sair"):
        st.session_state.logado = False
        st.rerun()
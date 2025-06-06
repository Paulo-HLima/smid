import streamlit as st
from utils.auth import verificar_autenticacao
from utils.dados import DOCAS, CLIENTES, AGENDAMENTOS, ENCOMENDAS

def render():
    if not verificar_autenticacao("cliente"):
        st.stop()

    st.title("📦 Dashboard do Cliente")
    usuario = st.session_state.usuario
    cliente_info = CLIENTES.get(usuario, {})
    docas_cliente = cliente_info.get("docas", [])

    # Inicializa toggles na sessão
    if "show_agendamentos" not in st.session_state:
        st.session_state.show_agendamentos = False
    if "show_docas" not in st.session_state:
        st.session_state.show_docas = False
    if "show_form_agendamento" not in st.session_state:
        st.session_state.show_form_agendamento = False
    if "show_encomendas" not in st.session_state:
        st.session_state.show_encomendas = False

    # Botão toggle para agendamentos
    if st.button("📅 Ver Agendamentos", key="btn_agendamentos"):
        st.session_state.show_agendamentos = not st.session_state.show_agendamentos

    if st.session_state.show_agendamentos:
        ags = [a for a in AGENDAMENTOS if a["cliente"] == usuario]
        if ags:
            for ag in ags:
                st.write(
                    f"📆 {ag['data']} às {ag['hora']} | Doca {ag['doca']} | Status: {ag.get('status', 'Desconhecido')}"
                )
        else:
            st.info("Nenhum agendamento encontrado.")

    # Botão toggle para docas
    if len(docas_cliente) == 1:
        if st.button("🔎 Status da Doca", key="btn_docas"):
            st.session_state.show_docas = not st.session_state.show_docas
        if st.session_state.show_docas:
            doca_id = docas_cliente[0]
            doca_status = DOCAS.get(doca_id, {}).get("status", "Desconhecido")
            st.success(f"Status da Doca {doca_id}: {doca_status}")
    elif len(docas_cliente) > 1:
        if st.button("🔎 Ver Docas", key="btn_docas"):
            st.session_state.show_docas = not st.session_state.show_docas
        if st.session_state.show_docas:
            for doca_id in docas_cliente:
                doca_status = DOCAS.get(doca_id, {}).get("status", "Desconhecido")
                st.info(f"Doca {doca_id}: {doca_status}")

    # Botão toggle para solicitar agendamento
    if st.button("➕ Solicitar Agendamento", key="btn_form_agendamento"):
        st.session_state.show_form_agendamento = not st.session_state.show_form_agendamento

    if st.session_state.show_form_agendamento:
        with st.form("form_solicitar_agendamento"):
            doca_escolhida = st.selectbox("Escolha a doca", docas_cliente)
            data = st.date_input("Data")
            hora = st.time_input("Hora")
            enviar = st.form_submit_button("Solicitar")
            if enviar:
                novo_agendamento = {
                    "cliente": usuario,
                    "doca": doca_escolhida,
                    "data": data.strftime("%d/%m/%Y"),
                    "hora": hora.strftime("%H:%M"),
                    "status": "Pendente"
                }
                AGENDAMENTOS.append(novo_agendamento)
                st.success("Solicitação de agendamento enviada!")
                st.session_state.show_form_agendamento = False
                st.session_state.show_agendamentos = True  # Mostra agendamentos após solicitar

    # Seção de Encomendas
    if st.button("📦 Ver Encomendas", key="btn_encomendas"):
        st.session_state.show_encomendas = not st.session_state.show_encomendas

    if st.session_state.show_encomendas:
        st.subheader("Minhas Encomendas")
        encomendas_cliente = [e for e in ENCOMENDAS if e["cliente"] == usuario]
        if not encomendas_cliente:
            st.info("Nenhuma encomenda registrada.")
        else:
            for encomenda in encomendas_cliente:
                st.markdown(f"**Descrição:** {encomenda['descricao']}")
                st.markdown(f"**Status:** {encomenda['status']}")
                # Mostrar agendamento associado, se houver
                if encomenda["agendamento_idx"] is not None:
                    ag = AGENDAMENTOS[encomenda["agendamento_idx"]]
                    st.markdown(
                        f"**Agendamento:** {ag['data']} {ag['hora']} | Doca {ag['doca']} | Status: {ag['status']}"
                    )
                # Alocar encomenda pendente
                if encomenda["status"] == "Pendente":
                    ags_disp = [
                        (idx, ag)
                        for idx, ag in enumerate(AGENDAMENTOS)
                        if ag["cliente"] == usuario and ag["status"] == "Em Processamento"
                    ]
                    if ags_disp:
                        options = [
                            (str(idx), f"{ag['data']} {ag['hora']} | Doca {ag['doca']}")
                            for idx, ag in ags_disp
                        ]
                        with st.form(f"form_alocar_{encomenda['id']}"):
                            escolha = st.selectbox(
                                "Alocar em agendamento:",
                                options=options,
                                format_func=lambda x: x[1] if isinstance(x, tuple) else x
                            )
                            submit = st.form_submit_button("Alocar")
                            if submit:
                                encomenda["agendamento_idx"] = int(escolha[0])
                                encomenda["status"] = "Em Processamento"
                                st.success("Encomenda alocada com sucesso!")
                                st.rerun()
                    else:
                        st.info("Nenhum agendamento disponível para alocação.")
                # Cancelar encomenda (Pendente ou Em Processamento)
                if encomenda["status"] in ["Pendente", "Em Processamento"]:
                    if st.button("Cancelar Encomenda", key=f"cancelar_{encomenda['id']}"):
                        encomenda["status"] = "Cancelada"
                        encomenda["agendamento_idx"] = None
                        st.warning("Encomenda cancelada!")
                        st.rerun()
                st.divider()

    st.divider()
    st.caption(f"Utilizador: ID: {usuario} | Email: {usuario}@cliente.smid")

    if st.button("🔓 Sair"):
        st.session_state.logado = False
        st.rerun()

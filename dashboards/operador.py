import streamlit as st
from utils.auth import verificar_autenticacao
from utils.dados import DOCAS, AGENDAMENTOS, ENCOMENDAS

def render():
    if not verificar_autenticacao("operador"):
        st.stop()

    st.title("🛠️ Dashboard do Operador")
    usuario = st.session_state.usuario

    # Inicializa toggles na sessão
    if "show_docas_operador" not in st.session_state:
        st.session_state.show_docas_operador = False
    if "show_alertas_operador" not in st.session_state:
        st.session_state.show_alertas_operador = False
    if "show_alertas_resolvidos_operador" not in st.session_state:
        st.session_state.show_alertas_resolvidos_operador = False
    if "show_encomendas_operador" not in st.session_state:
        st.session_state.show_encomendas_operador = False

    # Botão toggle para docas
    if st.button("🔎 Monitorar Docas", key="btn_docas_operador"):
        st.session_state.show_docas_operador = not st.session_state.show_docas_operador

    if st.session_state.show_docas_operador:
        st.subheader("Status das Docas")
        for doca_id, doca in DOCAS.items():
            st.info(f"Doca {doca_id}: {doca['status']}")

    # Botão toggle para encomendas
    if st.button("📦 Ver Encomendas", key="btn_encomendas_operador"):
        st.session_state.show_encomendas_operador = not st.session_state.show_encomendas_operador

    if st.session_state.show_encomendas_operador:
        st.subheader("Encomendas em Agendamentos Ativos")
        encomendas_ativas = [
            e for e in ENCOMENDAS
            if e["agendamento_idx"] is not None and
               AGENDAMENTOS[e["agendamento_idx"]]["status"] in ["Em Processamento", "Confirmado"]
        ]
        if not encomendas_ativas:
            st.info("Nenhuma encomenda ativa para exibir.")
        else:
            for encomenda in encomendas_ativas:
                ag = AGENDAMENTOS[encomenda["agendamento_idx"]]
                st.markdown(f"**ID:** {encomenda['id']}")
                st.markdown(f"**Descrição:** {encomenda['descricao']}")
                st.markdown(f"**Cliente:** {encomenda['cliente']}")
                st.markdown(f"**Status da Encomenda:** {encomenda['status']}")
                st.markdown(
                    f"**Agendamento:** {ag['data']} {ag['hora']} | Doca {ag['doca']} | Status: {ag['status']}"
                )
                # Histórico da encomenda
                if "historico" in encomenda and encomenda["historico"]:
                    with st.expander("Histórico da Encomenda"):
                        for h in encomenda["historico"]:
                            st.markdown(f"- {h['acao']} em {h['data']}")
                st.divider()

    # Botão toggle para alertas técnicos
    if st.button("⚠️ Visualizar Alertas Técnicos", key="btn_alertas_operador"):
        st.session_state.show_alertas_operador = not st.session_state.show_alertas_operador

    if st.session_state.show_alertas_operador:
        from utils.dados import ALERTAS
        st.subheader("Alertas Técnicos Ativos")
        for idx, alerta in enumerate([a for a in ALERTAS if a.get("status", "Ativo") == "Ativo"]):
            cols = st.columns([6, 1])
            with cols[0]:
                st.error(f"{alerta['mensagem']} (Doca {alerta['doca']}) - {alerta['timestamp']}")
            with cols[1]:
                if st.button("Resolver", key=f"resolver_alerta_op_{idx}"):
                    from datetime import datetime
                    alerta["status"] = "Resolvido"
                    alerta["resolvido_por"] = f"Operador ({usuario})"
                    alerta["resolvido_em"] = datetime.now().strftime("%d/%m/%Y %H:%M")
                    st.success("Alerta resolvido!")
                    st.rerun()

        # Sub-botão para mostrar alertas resolvidos
        if st.button("🔽 Alertas Resolvidos", key="btn_alertas_resolvidos_operador"):
            st.session_state.show_alertas_resolvidos_operador = not st.session_state.show_alertas_resolvidos_operador

        if st.session_state.show_alertas_resolvidos_operador:
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

    st.divider()
    st.caption(f"Utilizador: ID: {usuario} | Email: {usuario}@operator.smid")

    if st.button("🔓 Sair"):
        st.session_state.logado = False
        st.rerun()
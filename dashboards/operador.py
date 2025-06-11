import streamlit as st
from utils.auth import verificar_autenticacao
from database.db import (
    buscar_docas,
    buscar_encomendas,
    buscar_agendamentos,
    buscar_clientes,
    buscar_alertas,
    resolver_alerta,
    atualizar_agendamento_status,
    atualizar_encomenda_status,
    atualizar_status_doca,  # <-- Adicione este import
)
from datetime import datetime

def render():
    if not verificar_autenticacao("operador"):
        st.stop()

    # Estilo global sofisticado
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

    # Cabeçalho sofisticado
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
        <div style="font-size:2.5rem;">🛠️</div>
        <div>
            <h1 style="color:#1976d2; font-weight:800; letter-spacing:1px; margin-bottom:8px; margin-top:0;">Dashboard do Operador</h1>
            <span style="color:#222; font-size:1.13rem;">Bem-vindo, <b>{st.session_state.nome}</b>!</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Inicializa toggles na sessão
    if "show_docas_operador" not in st.session_state:
        st.session_state.show_docas_operador = False
    if "show_alertas_operador" not in st.session_state:
        st.session_state.show_alertas_operador = False
    if "show_alertas_resolvidos_operador" not in st.session_state:
        st.session_state.show_alertas_resolvidos_operador = False
    if "show_encomendas_operador" not in st.session_state:
        st.session_state.show_encomendas_operador = False

    st.divider()

    # Botão toggle para encomendas
    if st.button("📦 Ver Encomendas", key="btn_encomendas_operador"):
        st.session_state.show_encomendas_operador = not st.session_state.show_encomendas_operador

    if st.session_state.show_encomendas_operador:
        st.markdown(
            '<h3 style="color:#d0e4f7; font-weight:800; letter-spacing:0.5px; margin-bottom:12px;">Encomendas em Agendamentos Ativos</h3>',
            unsafe_allow_html=True
        )
        encomendas_db = buscar_encomendas()
        agendamentos_db = buscar_agendamentos()
        clientes_db = {c["id"]: c["nome"] for c in buscar_clientes()}
        # Filtra encomendas vinculadas a agendamentos ativos
        encomendas_ativas = [
            e for e in encomendas_db
            if e.get("agendamento_id") is not None and
               next((ag for ag in agendamentos_db if ag["id"] == e["agendamento_id"] and ag["status"] in ["Em Processamento", "Confirmado"]), None)
        ]
        if not encomendas_ativas:
            st.markdown(
                '<div style="color:#d32f2f; font-weight:700; background:#fff3cd; padding:16px 18px; border-radius:8px; border-left:5px solid #d32f2f;">Nenhuma encomenda ativa para exibir.</div>',
                unsafe_allow_html=True
            )
            st.divider()       
        else:
            for encomenda in encomendas_ativas:
                ag = next(ag for ag in agendamentos_db if ag["id"] == encomenda["agendamento_id"])
                cliente_nome = clientes_db.get(encomenda["usuario_id"], "Desconhecido")
                cor_borda, cor_grad1, cor_grad2, cor_status, icone, status_legenda = {
                    "Pendente":   ("#b28704", "#fff9e1", "#ffe082", "#b28704", "📦", "Pendente"),
                    "Em Processamento": ("#1976d2", "#e3f2fd", "#90caf9", "#1976d2", "🔄", "Em Processamento"),
                    "Processada": ("#388e3c", "#e8f5e9", "#a5d6a7", "#388e3c", "✅", "Processada"),
                    "Cancelada":  ("#d32f2f", "#ffebee", "#ffcdd2", "#d32f2f", "❌", "Cancelada"),
                    "Confirmado": ("#0097a7", "#e0f7fa", "#80deea", "#0097a7", "📅", "Confirmado"),
                }.get(encomenda["status"], ("#b0bec5", "#eceff1", "#b0bec5", "#78909c", "❔", encomenda["status"]))
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
        <b>ID:</b> {encomenda['id']} &nbsp; <b>Cliente:</b> {cliente_nome}
    </div>
    <div style="color: #444; font-size: 0.98rem;">
        <b>Descrição:</b> {encomenda['descricao']}
    </div>
    <div style="color: #444; font-size: 0.98rem;">
        <b>Status:</b> <span style="color:{cor_status};">{encomenda['status']}</span>
    </div>
    <div style="color: #444; font-size: 0.98rem;">
        <b>Agendamento:</b> {ag['data']} {ag['hora']} | Doca {ag['doca_nome']} | Status: {ag['status']}
    </div>
  </div>
  <div style="text-align: right;">
    <span style="background:{cor_status}22; color:{cor_status}; padding:6px 14px; border-radius:8px; font-weight:700; font-size:0.95rem;">
        ● {status_legenda}
    </span>
  </div>
</div>
""", unsafe_allow_html=True)

                # Botão "Concluir" para encomendas em processamento com agendamento confirmado
                if (
                    encomenda["status"] == "Em Processamento"
                    and ag["status"] == "Confirmado"
                ):
                    if st.button("Concluir", key=f"concluir_{encomenda['id']}"):
                        atualizar_agendamento_status(ag["id"], "Concluído")
                        atualizar_encomenda_status(encomenda["id"], "Processada")
                        atualizar_status_doca(ag["doca_id"], "Livre")  # <-- Atualiza doca para Livre
                        st.success("Encomenda e agendamento concluídos!")
                        st.rerun()
                st.divider()

    # Botão toggle para docas
    if st.button("🔎 Monitorar Docas", key="btn_docas_operador"):
        st.session_state.show_docas_operador = not st.session_state.show_docas_operador

    if st.session_state.show_docas_operador:
        st.markdown(
            '<h3 style="color:#d0e4f7; font-weight:800; letter-spacing:0.5px; margin-bottom:12px;">Status das Docas</h3>',
            unsafe_allow_html=True
        )
        docas = buscar_docas()
        for doca in docas:
            cor_borda, cor_grad1, cor_grad2, cor_status, icone, status_legenda = {
                "Livre": ("#388e3c", "#e8f5e9", "#a5d6a7", "#388e3c", "🟢", "Livre"),
                "Ocupada": ("#1976d2", "#e3f2fd", "#90caf9", "#1976d2", "🔵", "Ocupada"),
                "Em preparação": ("#b28704", "#fff9e1", "#ffe082", "#b28704", "🟡", "Em preparação"),
            }.get(doca["status"], ("#b0bec5", "#eceff1", "#b0bec5", "#78909c", "❔", doca["status"]))
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
  </div>
</div>
""", unsafe_allow_html=True)

    # Painel de alertas
    if st.button("⚠️ Ver Alertas", key="btn_alertas_operador"):
        st.session_state.show_alertas_operador = not st.session_state.show_alertas_operador
    if "show_alertas_resolvidos_operador" not in st.session_state:
        st.session_state.show_alertas_resolvidos_operador = False

    if st.session_state.show_alertas_operador:
        st.markdown(
            '<h3 style="color:#d0e4f7; font-weight:800; letter-spacing:0.5px; margin-bottom:12px;">Painel de Alertas Gerais</h3>',
            unsafe_allow_html=True
        )
        alertas = buscar_alertas()
        for idx, alerta in enumerate([a for a in alertas if a.get("status", "Ativo") == "Ativo"]):
            cor_borda = "#d32f2f"
            st.markdown(f"""
<div style="
    background: linear-gradient(90deg, #ffebee 60%, #ffcdd2 100%);
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
    <div style="font-size: 1.08rem; color: {cor_borda}; font-weight: 700; margin-bottom: 2px;">
        ⚠️ {alerta['mensagem']} (Doca {alerta.get('doca_nome', 'N/A')}) - {alerta['timestamp']}
    </div>
  </div>
  <div>
    {"<span style='color:#d32f2f; font-weight:700;'>Conflito</span>" if alerta.get("tipo") == "Conflito" else ""}
  </div>
</div>
""", unsafe_allow_html=True)
            # Botão real para resolver alerta (fora do HTML)
            if alerta.get("tipo") != "Conflito":
                if st.button("Resolver", key=f"resolver_alerta_op_{idx}"):
                    resolver_alerta(alerta["id"], usuario)
                    st.success("Alerta resolvido!")
                    st.rerun()
        st.divider()
        # Sub-botão para mostrar alertas resolvidos
        if st.button("🔽 Alertas Resolvidos", key="btn_alertas_resolvidos_operador"):
            st.session_state.show_alertas_resolvidos_operador = not st.session_state.show_alertas_resolvidos_operador

        if st.session_state.show_alertas_resolvidos_operador:
            st.markdown(
                '<h3 style="color:#d0e4f7; font-weight:800; letter-spacing:0.5px; margin-bottom:12px;">Alertas Resolvidos</h3>',
                unsafe_allow_html=True
            )
            for alerta in [a for a in alertas if a.get("status", "Ativo") == "Resolvido"]:
                resolvido_por = alerta.get("resolvido_por", "Desconhecido")
                resolvido_em = alerta.get("resolvido_em", "Data desconhecida")
                st.markdown(
                    f"""
<div style="background: linear-gradient(90deg, #e1f5fe 60%, #b3e5fc 100%);padding:10px 18px;border-radius:8px;margin-bottom:8px;border-left:5px solid #1976d2;">
    <b>{alerta['mensagem']}</b> (Doca {alerta.get('doca_nome', 'N/A')}) - {alerta['timestamp']}<br>
    <small>Resolvido por: {resolvido_por} em {resolvido_em}</small>
</div>
""",
                    unsafe_allow_html=True
                )

    st.divider()
    st.markdown(
        f'<div style="color:#90caf9; font-size:0.98rem; margin-top:24px; text-align:right;">Utilizador: <b>ID:</b> {st.session_state.nome} &nbsp;|&nbsp; <b>Email:</b> {usuario}</div>',
        unsafe_allow_html=True
    )

    if st.button("🔓 Sair"):
        st.session_state.logado = False
        st.rerun()
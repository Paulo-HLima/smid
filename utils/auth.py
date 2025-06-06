# utils/auth.py
import streamlit as st

def verificar_autenticacao(tipo_esperado):
    """Verifica se o usuário está logado e se o tipo está correto"""
    if not st.session_state.get("logado"):
        st.warning("Você precisa estar logado para acessar esta página.")
        return False

    if st.session_state.get("tipo") != tipo_esperado:
        st.error("Acesso negado: perfil sem permissões para esta página.")
        return False

    if "usuario" not in st.session_state or "tipo" not in st.session_state:
        st.error("Sessão corrompida ou inválida.")
        return False

    return True
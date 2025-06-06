import streamlit as st

# Inicialize as chaves necessárias se não existirem
if "usuario" not in st.session_state:
    st.session_state["usuario"] = ""
if "tipo" not in st.session_state:
    st.session_state["tipo"] = ""
if "logado" not in st.session_state:
    st.session_state["logado"] = False

st.set_page_config(
    page_title="SMID - Sistema de Monitorização Inteligente de Docas",
    page_icon="🚚",
    layout="centered",
    initial_sidebar_state="collapsed"
)

hide_menu = """
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        section[data-testid="stSidebar"] {display: none;}
    </style>
"""
st.markdown(hide_menu, unsafe_allow_html=True)

import pandas as pd
from pathlib import Path
from dashboards import cliente, gestor, operador

USERS_FILE = Path("data/seed_usuarios.csv")

def autenticar(username, senha):
    if USERS_FILE.exists():
        df = pd.read_csv(USERS_FILE)
        user = df[(df["username"] == username) & (df["senha"] == senha)]
        if not user.empty:
            info = user.iloc[0]
            st.session_state.logado = True
            st.session_state.usuario = info["username"]
            st.session_state.tipo = info["tipo"]
            return True
    return False

# Só mostra dashboard se estiver logado e com usuário/tipo válidos
if (
    st.session_state.get("logado") is True
    and st.session_state.get("usuario")
    and st.session_state.get("tipo")
):
    tipo = st.session_state.tipo
    if tipo == "cliente":
        cliente.render()
    elif tipo == "gestor":
        gestor.render()
    elif tipo == "operador":
        operador.render()
    else:
        st.error("Tipo de utilizador inválido.")
    st.stop()

# Página de login (só aparece se NÃO estiver logado)
st.title("🏠 Home - Login SMID")

with st.form("login_form"):
    username = st.text_input("Utilizador (ID)")
    senha = st.text_input("Palavra-passe", type="password")
    login_btn = st.form_submit_button("Entrar")

    if login_btn:
        if autenticar(username, senha):
            st.success("Login efetuado com sucesso!")
            st.rerun()
        else:
            st.error("Credenciais inválidas. Tente novamente.")
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

# Aplica um fundo escuro suave à tela toda
st.markdown("""
<style>
body, .stApp {
    background: linear-gradient(120deg, #232946 0%, #394867 100%) !important;
}
</style>
""", unsafe_allow_html=True)

# Página de login (só aparece se NÃO estiver logado)
st.markdown("""
<div style="
    max-width: 420px;
    margin: 60px auto 0 auto;
    padding: 32px 28px 24px 28px;
    background: linear-gradient(120deg, #e3f2fd 60%, #90caf9 100%);
    border-radius: 18px;
    box-shadow: 0 4px 24px #0004;
    border-left: 8px solid #1976d2;
    text-align: center;
">
    <div style="font-size:2.5rem; margin-bottom:8px;">🚚</div>
    <h2 style="color:#1976d2; font-weight:800; letter-spacing:1px; margin-bottom:10px;">SMID - Login</h2>
    <span style="color:#333; font-size:1.1rem;">Acesse o sistema com seu utilizador e palavra-passe.</span>
</div>
""", unsafe_allow_html=True)

# Melhora contraste dos labels e campos de texto para fundo escuro
st.markdown("""
<style>
label, .stTextInput > label {
    color: #f5f7fa !important;
    font-weight: 700 !important;
    font-size: 1.12rem !important;
    letter-spacing: 0.5px;
}
input {
    background-color: #232946 !important;
    color: #f5f7fa !important;
    border-radius: 7px !important;
    border: 1.5px solid #90caf9 !important;
}
.stTextInput input:focus {
    border: 2px solid #1976d2 !important;
    background-color: #232946 !important;
    color: #fff !important;
}
</style>
""", unsafe_allow_html=True)

with st.form("login_form"):
    st.markdown('<div style="height: 16px"></div>', unsafe_allow_html=True)
    username = st.text_input("Utilizador (ID)")
    senha = st.text_input("Palavra-passe", type="password")
    login_btn = st.form_submit_button("Entrar")

    if login_btn:
        if autenticar(username, senha):
            st.success("Login efetuado com sucesso!")
            st.rerun()
        else:
            st.error("Credenciais inválidas. Tente novamente.")
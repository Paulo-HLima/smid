import streamlit as st
from utils.dados import ALERTAS

def mostrar_alertas():
    st.subheader("⚠️ Painel de Alertas Gerais")
    for alerta in ALERTAS:
        st.error(f"{alerta['mensagem']} (Doca {alerta['doca']}) - {alerta['timestamp']}")
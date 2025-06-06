import streamlit as st
from utils.dados import AGENDAMENTOS

def mostrar_agendamentos(cliente_id=None):
    st.subheader("📅 Painel de Consulta de Agendamentos")
    ags = AGENDAMENTOS
    if cliente_id:
        ags = [a for a in AGENDAMENTOS if a["cliente"] == cliente_id]
    for ag in ags:
        st.write(f"{ag['cliente']} | Doca {ag['doca']} | {ag['data']} - {ag['hora']}")
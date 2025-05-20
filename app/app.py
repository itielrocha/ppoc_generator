import streamlit as st
import pandas as pd
import io
from generator import generate_schedule_csv  # Tu función principal

st.set_page_config(page_title="Asignador Semanal PPOC", layout="centered")
st.title("📅 Generador de Asignaciones Semanales PPOC")

st.markdown("""
Sube tu archivo de **preferencias.csv**, elige el **mes** y el **año**, y genera automáticamente las asignaciones.
""")

uploaded_file = st.file_uploader("Selecciona tu archivo preferencias.csv", type=["csv"])
col1, col2 = st.columns(2)
with col1:
    month = st.number_input("Mes", min_value=1, max_value=12, value=5, step=1)
with col2:
    year = st.number_input("Año", min_value=2024, value=2025, step=1)

if uploaded_file and st.button("Generar asignaciones"):
    try:
        csv_bytes = generate_schedule_csv(uploaded_file, month, year)
        st.success("Asignaciones generadas correctamente.")
        st.download_button(
            label="📥 Descargar respuesta.csv",
            data=csv_bytes,
            file_name="respuesta.csv",
            mime="text/csv"
        )
    except Exception as e:
        st.error(f"Ocurrió un error: {e}")

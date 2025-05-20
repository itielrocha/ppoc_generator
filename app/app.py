import streamlit as st
from datetime import datetime
from io import BytesIO
import pandas as pd
from main import generate_schedule_csv  # asegúrate de que el script principal se llama main.py

st.set_page_config(page_title="Asignador de ppoc", page_icon="📅")

st.title("📅 Asignador de ppoc semanal")
st.write("Carga tus preferencias y elige el mes y año para generar las asignaciones.")

uploaded_file = st.file_uploader("Sube tu archivo de preferencias (.csv)", type="csv")
col1, col2 = st.columns(2)
with col1:
    year = st.number_input("Año", min_value=2023, max_value=2100, step=1, value=datetime.now().year)
with col2:
    month = st.selectbox("Mes", options=list(range(1, 13)), format_func=lambda x: datetime(1900, x, 1).strftime('%B'))

if uploaded_file and st.button("Generar asignaciones"):
    try:
        csv_bytes = generate_schedule_csv(uploaded_file, month, year)
        st.success("Asignaciones generadas correctamente.")
        st.download_button(
            label="📥 Descargar archivo de asignaciones",
            data=csv_bytes,
            file_name=f"asignaciones_{month:02d}_{year}.csv",
            mime="text/csv"
        )
    except Exception as e:
        st.error(f"Error al generar las asignaciones: {e}")
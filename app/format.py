import pandas as pd

# Diccionario para mapear columnas originales a nombres estándar
COLUMN_MAPPING = {
    'Lunes a las 18h en Alcúdia': 'Lunes 18h Alcúdia',
    'Miércoles a las 10h en Puerto Pollensa': 'Miércoles 10h Pt. Pollensa',
    'Miércoles a las 18h en Sa Pobla': 'Miércoles 18h Sa Pobla',
    'Sábado a las 10h en Pollensa': 'Sábado 10h Pollensa',
    'Sábado a las 10h en Alcúdia': 'Sábado 10h Alcudia',
    'Sábado a las 10h en Sa Pobla (Calle Mayor)': 'Sábado 10h Sa Pobla (Calle Mayor)',
    'Sábado a las 10h en Sa Pobla (Plaza ayuntamiento)': 'Sábado 10h Sa Pobla (Plaza ayunt)',
}

def transform_response(valor):
    if pd.isna(valor):
        return '0'
    val = valor.strip().lower()
    if 'ninguna' in val:
        return '0'
    elif 'una vez' in val:
        return '1'
    else:
        return 'x'

def transform_csv_form(file) -> bytes:
    df = pd.read_csv(file)

    df_limpio = pd.DataFrame()
    df_limpio['Hermanos/as'] = df['Nombre y apellido (ej: Javier Vicente)'].str.strip().str.title()
    df_limpio['Superintendente'] = 0  # O puedes inferirlo si tienes lógica para ello
    df_limpio['Activo'] = 1  # Todos activos por defecto

    for original, nuevo in COLUMN_MAPPING.items():
        if original in df.columns:
            df_limpio[nuevo] = df[original].apply(transform_response)
        else:
            df_limpio[nuevo] = '0'  # Si no está la columna, poner 0

    output = df_limpio.to_csv(index=False)
    return output.encode('utf-8')

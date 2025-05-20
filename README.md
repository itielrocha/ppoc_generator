# 📅 Generador de Asignaciones Semanales PPOC

Este script en Python genera asignaciones semanales entre hermanos y salidas de ppoc tomando en cuenta sus preferencias y restricciones mensuales.

---

## ✅ Funcionalidades

- Lee un archivo `preferencias.csv` con:
  - Hermanos.
  - Días y horarios posibles.
  - Restricciones mensuales de participación.
  - Información sobre quiénes son superintendentes.
- Genera asignaciones para **cada semana** de un **mes específico**.
- Asegura que en **cada salida haya al menos un superintendente**.
- Evita repeticiones semanales **salvo si no hay otra opción**.
- Marca como `repetido` e `incompleto` los casos donde:
  - Faltan personas.
  - Alguien se repite en la misma semana.

---

## 📄 Formato de entrada: `preferencias.csv`

El archivo debe tener la siguiente estructura:

| Hermanos/as | Superintendente | Activo | Lunes 10h Pollensa | Sábado 19h Alcúdia | ... |
|----------|------------------|--------|------------------|----------------------|-----|
| juan     | 1                | 1      | x                | 2                    |
| laura    | 0                | 1      | 1                | 0                    |
| pablo    | 1                | 0      | x                | x                    |

- `"x"`: Puede asistir todas las veces que se repita ese evento en el mes.
- `"0"`: No puede asistir a ese evento en todo el mes.
- Número: Máximo número de veces que puede asistir a ese evento en el mes.
- `"Superintendente"`: 1 si lo es, 0 si no.
- `"Activo"`: 1 si debe asignarse, 0 si se ignora.

---

## 📤 Salida: `respuesta.csv`

El script genera un archivo con el siguiente formato:

| ppoc                     | persona1 | persona2 | persona3 | nota          |
|----------------------------|----------|----------|----------|---------------|
| lunes 5 10h palma          | juan     | laura    | pedro    |               |
| viernes 9 19h alcúdia      | [vacío]  | juan     | carlos   | incompleto  |
| martes 13 18h pollensa     | juan     | juan     | sofía    | repetido    |

---

## ▶️ Ejecución

### Requisitos
- Python 3.7 o superior
- Librerías estándar (`csv`, `datetime`, `random`, `calendar`, etc.)

### Comando

```bash
python asignador.py --month 5 --year 2025 --input preferencias.csv --output respuesta.csv
```

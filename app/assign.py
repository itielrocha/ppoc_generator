import pandas as pd
import numpy as np
import calendar
import re
import argparse
import io

# Load preferences from a CSV file and extract event metadata

def load_preferences_with_event_structure(filepath):
    df = pd.read_csv(filepath)
    df = df[df['Activo'] == 1].reset_index(drop=True)
    people = df['Nombre'].tolist()
    event_columns = df.columns[4:]  # Skip nombre, hermana, superintendente, activo 

    # Parse event columns into metadata (weekday, hour, place)
    event_infos = []
    for col in event_columns:
        match = re.match(r"(\w+)\s+(\d{1,2}(?::\d{2})?h)\s+(.+)", col)
        if match:
            weekday_str, hour, place = match.groups()
            event_infos.append({
                "original": col,
                "weekday": weekday_str,
                "hour": hour,
                "place": place,
            })
        else:
            raise ValueError(f"Formato de evento inválido: {col}")

    limits = {}
    for i, person in enumerate(people):
        person_limits = {}
        for event in event_columns:
            value = df.loc[i, event]
            if pd.isna(value):
                person_limits[event] = 0
            elif str(value).strip().lower() == 'x':
                person_limits[event] = float('inf')
            else:
                person_limits[event] = int(value)
        limits[person] = person_limits

    supervisors = df[df['Superintendente'] == 1]['Nombre'].tolist()
    sisters = df[df['Hermana'] == 1]['Nombre'].tolist()

    return people, event_infos, limits, supervisors, sisters


# Return list of weeks with date objects from a given month and year

def get_weeks_with_dates(month, year):
    cal = calendar.Calendar(firstweekday=0)  # 0 = monday
    all_weeks = cal.monthdatescalendar(year, month)

    # Filter out the first week if it does not start in the current month (i.e., if Monday is not from the month)
    if all_weeks[0][0].month != month:
        all_weeks = all_weeks[1:]

    # The last week is already complete (Monday to Sunday) and is included even if it ends in the next month
    return all_weeks

# Map abstract event names to actual dates based on weekday

def map_event_names_to_real_dates(event_infos, weeks, month):
    day_name_map = {
        'Lunes': 0, 'Martes': 1, 'Miércoles': 2,
        'Jueves': 3, 'Viernes': 4, 'Sábado': 5, 'Domingo': 6
    }
    result = []

    for week in weeks:
        week_events = []
        for event in event_infos:
            weekday_num = day_name_map[event['weekday']]
            for day in week:
                if day.weekday() == weekday_num:
                    real_event = f"{event['weekday']} {day.day} {event['hour']} {event['place']}"
                    week_events.append((event['original'], real_event))
                    break
        result.append(week_events)
    return result


# Select 3 people including one supervisor from a pool

def select_people_with_supervisor(available, supervisors, sisters):
    available_supervisors = [p for p in available if p in supervisors]
    if not available_supervisors or len(available) < 3:
        return None

    for _ in range(100):  # 100 tries to find a valid group
        chosen_supervisor = np.random.choice(available_supervisors)
        rest = [p for p in available if p != chosen_supervisor]
        if len(rest) < 2:
            continue
        others = list(np.random.choice(rest, 2, replace=False))
        group = [chosen_supervisor] + others

        # rule: a sister must be present if there are 2 or more sisters in the group
        sister_count = sum(1 for p in group if p in sisters)
        if sister_count not in [0, 2, 3]:
            continue

        return group

    return None


# Main logic to assign people to events per week

def assign_events_real_dates(weeks, event_weeks, limits, supervisors, sisters):
    assignments = []
    monthly_count = {p: {e: 0 for e in limits[p]} for p in limits}

    for week_idx, week_events in enumerate(event_weeks):
        assigned_this_week = set()

        for original_event, real_event in week_events:
            possible = [p for p in limits if monthly_count[p][original_event] < limits[p][original_event]]
            available = [p for p in possible if p not in assigned_this_week]
            note = ""

            selected = select_people_with_supervisor(available, supervisors, sisters)

            if not selected:
                available = possible
                selected = select_people_with_supervisor(available, supervisors, sisters)
                if selected:
                    repetidos = [p for p in selected if p in assigned_this_week]
                    if repetidos:
                        note = "repetido: " + ", ".join(repetidos)
                else:
                    selected = []
                    sups = [p for p in available if p in supervisors]
                    if sups:
                        selected.append(np.random.choice(sups))
                    while len(selected) < 3:
                        selected.append("[vacío]")
                    note = "incompleto"

            for person in selected:
                if person != "[vacío]":
                    monthly_count[person][original_event] += 1
                    assigned_this_week.add(person)

            assignments.append([real_event] + selected + [note])

    return assignments


# Save result to CSV file

def save_assignments(assignments, output_path):
    df = pd.DataFrame(assignments, columns=["ppoc", "persona1", "persona2", "persona3", "nota"])
    df.to_csv(output_path, index=False)
    return output_path


# Function for use in web app (e.g. Streamlit)

def generate_schedule_csv(file, month: int, year: int) -> bytes:
    preferences_df = pd.read_csv(file)
    tmp_path = "__tmp_preferences.csv"
    preferences_df.to_csv(tmp_path, index=False)
    people, event_infos, limits, supervisors, sisters = load_preferences_with_event_structure(tmp_path)
    weeks = get_weeks_with_dates(month, year)
    event_weeks = map_event_names_to_real_dates(event_infos, weeks, month)
    assignments = assign_events_real_dates(weeks, event_weeks, limits, supervisors, sisters)

    output = io.StringIO()
    df = pd.DataFrame(assignments, columns=["ppoc", "persona1", "persona2", "persona3", "nota"])
    df.to_csv(output, index=False)
    return output.getvalue().encode('utf-8')


# Entry point for CLI usage

def main():
    parser = argparse.ArgumentParser(description="Asignador semanal de salidas ppoc con preferencias")
    parser.add_argument("--month", type=int, required=True, help="Mes (1-12)")
    parser.add_argument("--year", type=int, required=True, help="Año (ej. 2025)")
    parser.add_argument("--input", type=str, required=True, help="Ruta al CSV de preferencias")
    parser.add_argument("--output", type=str, required=True, help="Ruta para guardar el CSV de resultado")
    args = parser.parse_args()

    people, event_infos, limits, supervisors, sisters = load_preferences_with_event_structure(args.input)
    weeks = get_weeks_with_dates(args.month, args.year)
    event_weeks = map_event_names_to_real_dates(event_infos, weeks, args.month)
    assignments = assign_events_real_dates(weeks, event_weeks, limits, supervisors, sisters)
    save_assignments(assignments, args.output)

if __name__ == "__main__":
    main()

import pandas as pd
import numpy as np
import calendar
import re
import argparse

def load_preferences_with_event_structure(filepath):
    df = pd.read_csv(filepath)
    df = df[df['activo'] == 1].reset_index(drop=True)
    people = df['personas'].tolist()
    event_columns = df.columns[3:]
    
    # Parse event info
    event_infos = []
    for col in event_columns:
        match = re.match(r"(\w+)\s+(\d{1,2}(?::\d{2})?h)\s+(.+)", col)
        if match:
            weekday_str, hour, place = match.groups()
            event_infos.append({
                "original": col,
                "weekday": weekday_str.lower(),
                "hour": hour,
                "place": place,
            })
        else:
            raise ValueError(f"Invalid event column format: {col}")
    
    limits = {
        person: {
            event: (float('inf') if df.loc[i, event] == 'x' else int(df.loc[i, event]))
            for event in event_columns
        }
        for i, person in enumerate(people)
    }
    
    supervisors = df[df['superintendente'] == 1]['personas'].tolist()
    
    return people, event_infos, limits, supervisors

def get_weeks_with_dates(month, year):
    cal = calendar.Calendar()
    return cal.monthdatescalendar(year, month)

def map_event_names_to_real_dates(event_infos, weeks, month):
    day_name_map = {
        'lunes': 0, 'martes': 1, 'miércoles': 2,
        'jueves': 3, 'viernes': 4, 'sábado': 5, 'domingo': 6
    }
    result = []
    
    for week in weeks:
        week_events = []
        for event in event_infos:
            weekday_num = day_name_map[event['weekday']]
            for day in week:
                if day.weekday() == weekday_num and day.month == month:
                    new_event_name = f"{event['weekday']} {day.day} {event['hour']} {event['place']}"
                    week_events.append((event['original'], new_event_name))
                    break
        result.append(week_events)
    return result

def select_people_with_supervisor(available, supervisors):
    available_supervisors = [p for p in available if p in supervisors]
    if not available_supervisors or len(available) < 3:
        return None
    chosen_supervisor = np.random.choice(available_supervisors)
    rest = [p for p in available if p != chosen_supervisor]
    chosen = [chosen_supervisor] + list(np.random.choice(rest, 2, replace=False))
    return chosen

def assign_events_real_dates(weeks, event_weeks, limits, supervisors):
    assignments = []
    monthly_count = {p: {e: 0 for e in limits[p]} for p in limits}
    
    for week_idx, week_events in enumerate(event_weeks):
        assigned_this_week = set()
        
        for original_event, real_event in week_events:
            possible = [p for p in limits if monthly_count[p][original_event] < limits[p][original_event]]
            available = [p for p in possible if p not in assigned_this_week]
            note = ""
            
            selected = select_people_with_supervisor(available, supervisors)
            
            if not selected:
                available = possible
                selected = select_people_with_supervisor(available, supervisors)
                if selected:
                    note = "repetido"
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

def save_assignments(assignments, output_path):
    df = pd.DataFrame(assignments, columns=["ppoc", "persona1", "persona2", "persona3", "nota"])
    df.to_csv(output_path, index=False)
    return output_path

def main():
    parser = argparse.ArgumentParser(description="Asignador de ppoc semanal con preferencias.")
    parser.add_argument("--month", type=int, required=True, help="Mes numérico (1-12)")
    parser.add_argument("--year", type=int, required=True, help="Año numérico (ej. 2025)")
    parser.add_argument("--input", type=str, required=True, help="Ruta al archivo de preferencias .csv")
    parser.add_argument("--output", type=str, required=True, help="Ruta de salida para el archivo de respuesta .csv")
    args = parser.parse_args()

    people, event_infos, limits, supervisors = load_preferences_with_event_structure(args.input)
    weeks = get_weeks_with_dates(args.month, args.year)
    event_weeks = map_event_names_to_real_dates(event_infos, weeks, args.month)
    assignments = assign_events_real_dates(weeks, event_weeks, limits, supervisors)
    save_assignments(assignments, args.output)

if __name__ == "__main__":
    main()

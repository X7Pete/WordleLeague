from google_sheets.sheets_client import get_spreadsheet


def add_result(players, date, wordle, results):
    ss = get_spreadsheet()
    ws = ss.worksheet("Results")

    row = [date, wordle]
    for player in players:
        row.append(results.get(player, ""))

    ws.append_row(row)
    print(f"✅ Resultat tillagt: {date} #{wordle}")


def clear_results():
    ss = get_spreadsheet()
    ws = ss.worksheet("Results")

    # Behåll rubrikraden, radera resten
    headers = ws.row_values(1)
    ws.clear()
    ws.append_row(headers)
    print("✅ Results rensad!")
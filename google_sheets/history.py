from google_sheets.sheets_client import get_spreadsheet


def update_history():
    ss = get_spreadsheet()
    results_ws = ss.worksheet("Results")
    history_ws = ss.worksheet("History")

    all_rows = results_ws.get_all_values()
    if not all_rows:
        return

    headers = all_rows[0]
    player_names = headers[2:]
    data_rows = sorted(all_rows[1:], key=lambda x: (x[0], x[1]), reverse=True)

    history_ws.clear()
    rows = [["Date", "Wordle", "1st", "2nd", "3rd", "4th", "5th", "6th"]]

    for row in data_rows:
        date = row[0]
        wordle = row[1]
        scores = {}
        for i, name in enumerate(player_names):
            val = row[2 + i] if 2 + i < len(row) else ""
            if val != "":
                scores[name] = int(val)

        if not scores:
            continue

        sorted_players = sorted(scores.items(), key=lambda x: x[1])
        history_row = [date, wordle]
        for name, score in sorted_players:
            history_row.append(f"{name} ({score})")
        while len(history_row) < 8:
            history_row.append("")

        rows.append(history_row)

    history_ws.update("A1", rows)
    print("✅ History uppdaterad!")
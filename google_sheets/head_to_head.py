from google_sheets.sheets_client import get_spreadsheet


def update_head_to_head():
    ss = get_spreadsheet()
    results_ws = ss.worksheet("Results")
    h2h_ws = ss.worksheet("Head-to-Head")

    all_rows = results_ws.get_all_values()
    if not all_rows:
        return

    headers = all_rows[0]
    player_names = headers[2:]
    data_rows = all_rows[1:]

    h2h = {a: {b: [0, 0, 0] for b in player_names if b != a} for a in player_names}

    for row in data_rows:
        scores = {}
        for i, name in enumerate(player_names):
            val = row[2 + i] if 2 + i < len(row) else ""
            if val != "":
                scores[name] = int(val)

        if not scores:
            continue

        players_today = list(scores.keys())
        for i in range(len(players_today)):
            for j in range(len(players_today)):
                if i == j:
                    continue
                a = players_today[i]
                b = players_today[j]
                if scores[a] < scores[b]:
                    h2h[a][b][0] += 1
                elif scores[a] > scores[b]:
                    h2h[a][b][1] += 1
                else:
                    h2h[a][b][2] += 1

    h2h_ws.clear()
    rows = [[""] + player_names]

    for a in player_names:
        row = [a]
        for b in player_names:
            if a == b:
                row.append("-")
            else:
                wins, losses, draws = h2h[a][b]
                row.append(f"{wins}-{losses}-{draws}")
        rows.append(row)

    h2h_ws.update("A1", rows)
    print("✅ Head-to-Head uppdaterad!")
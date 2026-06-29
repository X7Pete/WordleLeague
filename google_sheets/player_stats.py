from google_sheets.sheets_client import get_spreadsheet


def update_player_stats():
    ss = get_spreadsheet()
    results_ws = ss.worksheet("Results")
    stats_ws = ss.worksheet("Player Stats")

    all_rows = results_ws.get_all_values()
    if not all_rows:
        return

    headers = all_rows[0]
    player_names = headers[2:]
    data_rows = all_rows[1:]

    history = {name: [] for name in player_names}

    for row in data_rows:
        date = row[0]
        wordle = row[1]
        for i, name in enumerate(player_names):
            val = row[2 + i] if 2 + i < len(row) else ""
            if val != "":
                history[name].append((date, wordle, int(val)))

    stats_ws.clear()
    output = []

    for name in player_names:
        games = history[name]
        output.append([name])
        output.append(["Date", "Wordle", "Score"])

        for date, wordle, score in games:
            output.append([date, wordle, score])

        scores = [s for _, _, s in games]
        if scores:
            total_games = len(scores)
            average = round(sum(scores) / total_games, 2)
            best = min(scores)
            worst = max(scores)

            wins = 0
            for row in data_rows:
                day_scores = {}
                for i, n in enumerate(player_names):
                    val = row[2 + i] if 2 + i < len(row) else ""
                    if val != "":
                        day_scores[n] = int(val)
                if day_scores and name in day_scores:
                    if day_scores[name] == min(day_scores.values()):
                        wins += 1

            output.append([])
            output.append([f"Games: {total_games}", f"Wins: {wins}", f"Average: {average}", f"Best: {best}", f"Worst: {worst}"])

        output.append([])
        output.append([])

    stats_ws.update("A1", output)
    print("✅ Player Stats uppdaterad!")
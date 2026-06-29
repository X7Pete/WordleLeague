from google_sheets.sheets_client import get_spreadsheet


def update_streaks():
    ss = get_spreadsheet()
    results_ws = ss.worksheet("Results")
    streaks_ws = ss.worksheet("Streaks")

    all_rows = results_ws.get_all_values()
    if not all_rows:
        return

    headers = all_rows[0]
    player_names = headers[2:]
    data_rows = sorted(all_rows[1:], key=lambda x: (x[0], x[1]))

    history = {name: [] for name in player_names}

    for row in data_rows:
        scores = {}
        for i, name in enumerate(player_names):
            val = row[2 + i] if 2 + i < len(row) else ""
            if val != "":
                scores[name] = int(val)

        if not scores:
            continue

        best_score = min(scores.values())
        for name, score in scores.items():
            won = score == best_score
            history[name].append((row[0], score, won))

    results = {}
    for name in player_names:
        games = history[name]
        if not games:
            results[name] = {"current_streak": 0, "best_streak": 0, "current_win_streak": 0, "best_win_streak": 0}
            continue

        current_streak = 0
        for _, score, _ in reversed(games):
            if score is not None:
                current_streak += 1
            else:
                break

        best_streak = running = 0
        for _, score, _ in games:
            if score is not None:
                running += 1
                best_streak = max(best_streak, running)
            else:
                running = 0

        current_win_streak = 0
        for _, _, won in reversed(games):
            if won:
                current_win_streak += 1
            else:
                break

        best_win_streak = running = 0
        for _, _, won in games:
            if won:
                running += 1
                best_win_streak = max(best_win_streak, running)
            else:
                running = 0

        results[name] = {
            "current_streak": current_streak,
            "best_streak": best_streak,
            "current_win_streak": current_win_streak,
            "best_win_streak": best_win_streak,
        }

    sorted_results = sorted(results.items(), key=lambda x: (-x[1]["current_streak"], -x[1]["best_streak"]))

    streaks_ws.clear()
    rows = [["Name", "Current Streak", "Best Streak", "Current Win Streak", "Best Win Streak"]]
    for name, s in sorted_results:
        rows.append([name, s["current_streak"], s["best_streak"], s["current_win_streak"], s["best_win_streak"]])

    streaks_ws.update("A1", rows)
    print("✅ Streaks uppdaterad!")
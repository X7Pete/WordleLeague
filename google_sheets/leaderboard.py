from google_sheets.sheets_client import get_spreadsheet


def update_leaderboard():
    ss = get_spreadsheet()
    results_ws = ss.worksheet("Results")
    leaderboard_ws = ss.worksheet("Leaderboard")

    # Läs all data
    all_rows = results_ws.get_all_values()
    if not all_rows:
        return

    headers = all_rows[0]
    player_names = headers[2:]
    data_rows = all_rows[1:]

    # Samla statistik
    stats = {
        name: {
            "points": 0,
            "total": 0,
            "games": 0,
            "wins": 0,
            "podiums": 0,
            "best": None,
            "worst": None,
        }
        for name in player_names
    }

    for row in data_rows:
        scores = {}
        for i, name in enumerate(player_names):
            val = row[2 + i] if 2 + i < len(row) else ""
            if val != "":
                scores[name] = int(val)

        if not scores:
            continue

        # Points med tie-hantering
        sorted_players = sorted(scores.items(), key=lambda x: x[1])
        point_map = [10, 7, 5, 3, 2, 1]
        prev_score = None
        rank = 0
        for i, (name, score) in enumerate(sorted_players):
            if score != prev_score:
                rank = i
                prev_score = score
            if rank < len(point_map):
                stats[name]["points"] += point_map[rank]

        # Wins
        best_score = min(scores.values())
        for name, score in scores.items():
            if score == best_score:
                stats[name]["wins"] += 1

        # Podiums
        unique_scores = sorted(set(scores.values()))
        top3_scores = set(unique_scores[:3])
        for name, score in scores.items():
            if score in top3_scores:
                stats[name]["podiums"] += 1

        # Average, Best, Worst
        for name, score in scores.items():
            stats[name]["total"] += score
            stats[name]["games"] += 1
            if stats[name]["best"] is None or score < stats[name]["best"]:
                stats[name]["best"] = score
            if stats[name]["worst"] is None or score > stats[name]["worst"]:
                stats[name]["worst"] = score

    # Sortera
    sorted_stats = sorted(
        stats.items(),
        key=lambda x: (
            -x[1]["points"],
            x[1]["total"] / x[1]["games"] if x[1]["games"] > 0 else 999
        )
    )

    # Skriv till Google Sheets
    leaderboard_ws.clear()
    rows = [["Rank", "Name", "Points", "Games", "Wins", "Podiums", "Best", "Worst", "Average"]]

    for rank, (name, s) in enumerate(sorted_stats, start=1):
        avg = round(s["total"] / s["games"], 2) if s["games"] > 0 else "-"
        rows.append([rank, name, s["points"], s["games"], s["wins"], s["podiums"], s["best"], s["worst"], avg])

    leaderboard_ws.update("A1", rows)
    print("✅ Leaderboard uppdaterad!")
from google_sheets.sheets_client import get_spreadsheet

SHEETS = [
    "Dashboard",
    "Results",
    "Leaderboard",
    "Player Stats",
    "Streaks",
    "Head-to-Head",
    "History",
    "Settings"
]

def setup_sheets(players):
    ss = get_spreadsheet()
    existing = [ws.title for ws in ss.worksheets()]

    # Skapa blad som saknas
    for sheet_name in SHEETS:
        if sheet_name not in existing:
            ss.add_worksheet(title=sheet_name, rows=1000, cols=26)
            print(f"✅ Skapade blad: {sheet_name}")

    # Sätt rubriker i Results om det är tomt
    results_ws = ss.worksheet("Results")
    if not results_ws.get_all_values():
        headers = ["Date", "Wordle"] + players
        results_ws.append_row(headers)
        print("✅ Rubriker satta i Results")

    # Sätt rubriker i Leaderboard om det är tomt
    leaderboard_ws = ss.worksheet("Leaderboard")
    if not leaderboard_ws.get_all_values():
        leaderboard_ws.append_row(["Rank", "Name", "Points", "Games", "Wins", "Podiums", "Best", "Worst", "Average"])
        print("✅ Rubriker satta i Leaderboard")

    print("✅ Google Sheets setup klar!")
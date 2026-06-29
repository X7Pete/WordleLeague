from data.player_manager import load_players
from google_sheets.setup_sheets import setup_sheets
from google_sheets.results import add_result, clear_results
from google_sheets.leaderboard import update_leaderboard
from google_sheets.player_stats import update_player_stats
from google_sheets.streaks import update_streaks
from google_sheets.history import update_history
from google_sheets.head_to_head import update_head_to_head


def input_result(players):
    from datetime import date

    print("\n📅 Vilket datum? (YYYY-MM-DD, tryck Enter för idag)")
    date_input = input("> ").strip()
    result_date = str(date.today()) if date_input == "" else date_input

    print("\n🔢 Vilket Wordle-nummer?")
    wordle = int(input("> ").strip())

    print("\nAnge resultat per spelare (1-6, eller 0 om ej spelat):")
    results = {}
    for player in players:
        while True:
            raw = input(f"  {player}: ").strip()
            if raw in {"1", "2", "3", "4", "5", "6", "0"}:
                if raw != "0":
                    results[player] = int(raw)
                break
            else:
                print("    ⚠️  Ange ett tal mellan 1-6, eller 0 om ej spelat.")

    print("\n💾 Sparar resultat...")
    add_result(players, result_date, wordle, results)

    print("📊 Uppdaterar statistik...")
    update_leaderboard()
    update_player_stats()
    update_streaks()
    update_history()
    update_head_to_head()

    print("\n✅ Klart!")


def main():
    players = load_players()
    setup_sheets(players)
    input_result(players)


if __name__ == "__main__":
    main()
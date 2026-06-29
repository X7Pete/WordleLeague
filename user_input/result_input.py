from datetime import date
from excel.results import add_result
from stats.leaderboard import update_leaderboard
from stats.player_stats import update_player_stats
from stats.streaks import update_streaks
from stats.history import update_history
from stats.head_to_head import update_head_to_head
from excel.dashboard import update_dashboard


def input_result(players):
    print("\n📅 Vilket datum? (YYYY-MM-DD, tryck Enter för idag)")
    date_input = input("> ").strip()

    if date_input == "":
        result_date = str(date.today())
    else:
        result_date = date_input

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
    update_dashboard()

    print("\n✅ Klart!")
import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(
    page_title="WordleLeague",
    page_icon="🟩",
    layout="wide"
)

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

def get_spreadsheet():
    creds = Credentials.from_service_account_file(
        "credentials.json",
        scopes=SCOPES
    )
    client = gspread.authorize(creds)
    return client.open("WordleLeague")

def load_sheet(ss, name):
    ws = ss.worksheet(name)
    data = ws.get_all_values()
    if not data:
        return pd.DataFrame()
    df = pd.DataFrame(data[1:], columns=data[0])
    return df

def load_data():
    ss = get_spreadsheet()
    leaderboard = load_sheet(ss, "Leaderboard")
    results = load_sheet(ss, "Results")
    history = load_sheet(ss, "History")
    streaks = load_sheet(ss, "Streaks")
    return leaderboard, results, history, streaks

leaderboard, results, history, streaks = load_data()

# --- Titel ---
st.title("🟩 WordleLeague")
st.caption("Tryck R för att ladda om senaste datan.")
st.divider()

# --- Leaderboard ---
st.header("🏆 Leaderboard")
st.dataframe(leaderboard, use_container_width=True, hide_index=True)
st.divider()

# --- Poängutveckling ---
st.header("📈 Poängutveckling")

player_names = [col for col in results.columns if col not in ["Date", "Wordle"]]
point_map = [10, 7, 5, 3, 2, 1]
cumulative = {name: [] for name in player_names}
dates = []

for _, row in results.iterrows():
    scores = {}
    for name in player_names:
        val = row[name]
        if val != "":
            scores[name] = int(val)

    if not scores:
        continue

    dates.append(f"{row['Date']} #{row['Wordle']}")
    sorted_players = sorted(scores.items(), key=lambda x: x[1])

    points_today = {name: 0 for name in player_names}
    prev_score = None
    rank = 0
    for i, (name, score) in enumerate(sorted_players):
        if score != prev_score:
            rank = i
            prev_score = score
        if rank < len(point_map):
            points_today[name] = point_map[rank]

    for name in player_names:
        prev = cumulative[name][-1] if cumulative[name] else 0
        cumulative[name].append(prev + points_today.get(name, 0))

chart_data = pd.DataFrame(cumulative, index=dates)
st.line_chart(chart_data, use_container_width=True)
st.divider()

# --- Streaks ---
st.header("🔥 Streaks")
st.dataframe(streaks, use_container_width=True, hide_index=True)
st.divider()

# --- Historik ---
st.header("📅 Historik")
st.dataframe(history, use_container_width=True, hide_index=True)

st.divider()

# --- Player Stats ---
st.header("👤 Player Stats")

ss = get_spreadsheet()
player_stats_ws = ss.worksheet("Player Stats")
player_stats_data = player_stats_ws.get_all_values()

# Visa rådata som text eftersom formatet är annorlunda
current_player = None
for row in player_stats_data:
    if not any(row):
        continue
    if row[0] and not row[1]:  # Spelarnamn-rad
        st.subheader(row[0])
    elif row[0] == "Date":  # Rubrikrad
        st.markdown("**Date | Wordle | Score**")
    elif row[0].startswith("Games:"):  # Sammanfattningsrad
        st.markdown(f"`{' | '.join([r for r in row if r])}`")
    else:
        st.markdown(f"{row[0]} | {row[1]} | {row[2]}")

st.divider()

# --- Head-to-Head ---
st.header("⚔️ Head-to-Head")
h2h = load_sheet(ss, "Head-to-Head")
st.dataframe(h2h, use_container_width=True, hide_index=True)
import streamlit as st
import pandas as pd
import gspread
import requests
from datetime import date
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
@st.cache_resource
def get_spreadsheet():
    creds_dict = dict(st.secrets["gcp_service_account"])
    creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
    creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    client = gspread.authorize(creds)
    return client.open("WordleLeague")
@st.cache_data(ttl=30)
def load_sheet(_ss, name):
    ws = _ss.worksheet(name)
    data = ws.get_all_values()
    if not data:
        return pd.DataFrame()
    return pd.DataFrame(data[1:], columns=data[0])

def get_todays_wordle_number():
    try:
        today = date.today().strftime("%Y-%m-%d")
        url = f"https://www.nytimes.com/svc/wordle/v2/{today}.json"
        response = requests.get(url, timeout=5)
        data = response.json()
        return data["days_since_launch"]
    except:
        return None
@st.cache_data(ttl=60)
def get_players(_ss):
    ws = _ss.worksheet("Results")
    headers = ws.row_values(1)
    return headers[2:]
@st.cache_data(ttl=10)
def has_submitted_today(_ss, player_name):
    ws = _ss.worksheet("Results")
    today = date.today().strftime("%Y-%m-%d")
    records = ws.get_all_values()
    for row in records[1:]:
        if row[0] == today:
            headers = records[0]
            if player_name in headers:
                idx = headers.index(player_name)
                if idx < len(row) and row[idx] != "":
                    return True
    return False

def save_result(ss, player_name, wordle_number, score):
    ws = ss.worksheet("Results")
    today = date.today().strftime("%Y-%m-%d")
    records = ws.get_all_values()
    headers = records[0]
    player_idx = headers.index(player_name)

    # Kolla om det redan finns en rad för dagens datum och Wordle-nummer
    for i, row in enumerate(records[1:], start=2):
        if row[0] == today and row[1] == str(wordle_number):
            # Uppdatera spelarens cell i befintlig rad
            ws.update_cell(i, player_idx + 1, score)
            return

    # Skapa ny rad
    new_row = [""] * len(headers)
    new_row[0] = today
    new_row[1] = wordle_number
    new_row[player_idx] = score
    ws.append_row(new_row)

def update_all_stats(ss):
    import time
    from google_sheets.leaderboard import update_leaderboard
    from google_sheets.player_stats import update_player_stats
    from google_sheets.streaks import update_streaks
    from google_sheets.history import update_history
    from google_sheets.head_to_head import update_head_to_head

    steps = [
        ("Leaderboard", update_leaderboard),
        ("Player Stats", update_player_stats),
        ("Streaks", update_streaks),
        ("History", update_history),
        ("Head-to-Head", update_head_to_head),
    ]

    for name, func in steps:
        try:
            func()
            time.sleep(2)
        except Exception as e:
            st.warning(f"⚠️ Kunde inte uppdatera {name}: {e}")

# --- Anslut till Google Sheets ---
try:
    ss = get_spreadsheet()
except Exception as e:
    st.error("⚠️ Kunde inte ansluta till Google Sheets just nu. Prova att ladda om sidan om en liten stund.")
    st.stop()

# --- Titel ---
st.title("🟩 WordleLeague")
st.caption("Tryck R för att ladda om senaste datan.")

# --- Inmatningsformulär ---
st.divider()
st.header("📝 Mata in ditt resultat")

players = get_players(ss)
wordle_number = get_todays_wordle_number()
today = date.today().strftime("%Y-%m-%d")

col1, col2 = st.columns([2, 1])

with col1:
    selected_player = st.selectbox("Vem är du?", ["Välj namn..."] + players)

with col2:
    if wordle_number:
        st.metric("Dagens Wordle", f"#{wordle_number}")
    else:
        wordle_number = st.number_input("Wordle-nummer", min_value=1, step=1)

if selected_player != "Välj namn...":
    if has_submitted_today(ss, selected_player):
        st.success(f"✅ {selected_player} har redan matat in sitt resultat idag!")
    else:
        score = st.radio(
        "Antal gissningar",
        options=[1, 2, 3, 4, 5, 6],
        index=3,
        horizontal=True
        )

        if st.button("💾 Spara resultat", type="primary"):
            with st.spinner("Sparar..."):
                save_result(ss, selected_player, wordle_number, score)
                update_all_stats(ss)
            load_sheet.clear()
            get_players.clear()
            has_submitted_today.clear()
            st.success(f"✅ {selected_player}s resultat sparat!")
            st.balloons()
            st.rerun()

# --- Leaderboard ---
st.divider()
st.header("🏆 Leaderboard")
leaderboard = load_sheet(ss, "Leaderboard")
st.dataframe(leaderboard, use_container_width=True, hide_index=True)

# --- Poängutveckling ---
st.divider()
st.header("📈 Poängutveckling")

results = load_sheet(ss, "Results")
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

if dates:
    chart_data = pd.DataFrame(cumulative, index=dates)
    st.line_chart(chart_data, use_container_width=True)

# --- Streaks ---
st.divider()
st.header("🔥 Streaks")
streaks = load_sheet(ss, "Streaks")
st.dataframe(streaks, use_container_width=True, hide_index=True)

# --- Historik ---
st.divider()
st.header("📅 Historik")
history = load_sheet(ss, "History")
st.dataframe(history, use_container_width=True, hide_index=True)

# --- Head-to-Head ---
st.divider()
st.header("⚔️ Head-to-Head")
h2h = load_sheet(ss, "Head-to-Head")
st.dataframe(h2h, use_container_width=True, hide_index=True)
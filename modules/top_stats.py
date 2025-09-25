import streamlit as st
import requests
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
RAPIDAPI_HOST = os.getenv("RAPIDAPI_HOST")

PLAYER_PROFILE_URL = "https://cricbuzz-cricket.p.rapidapi.com/stats/v1/player"

HEADERS = {
    "X-RapidAPI-Key": RAPIDAPI_KEY,
    "X-RapidAPI-Host": RAPIDAPI_HOST
}

# ✅ Verified working IDs
KNOWN_PLAYERS = {
    "Virat Kohli": 1413,
    "Rohit Sharma": 576,
    "Babar Azam": 8359,
    "Kane Williamson": 6326,
    "Joe Root": 8019,
    "David Warner": 1739,
    "MS Dhoni": 265,
    "Jasprit Bumrah": 9311,   # candidate from profile link
    "Hardik Pandya": 9647     # candidate from profile link
}

@st.cache_data(ttl=21600)
def fetch_player_profile(player_id):
    """Fetch player profile (basic info, rankings, recent matches)."""
    url = f"{PLAYER_PROFILE_URL}/{player_id}"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        st.error(f"❌ Could not fetch profile for ID {player_id}: {e}")
        return None

def parse_recent(data, key):
    """Extract recent batting/bowling records into a DataFrame."""
    records = []
    section = data.get(key, {})
    if "rows" in section:
        for row in section["rows"]:
            vals = row.get("values", [])
            if len(vals) >= 5:
                records.append({
                    "Match ID": vals[0],
                    "Opposition": vals[1],
                    "Stat": vals[2],
                    "Format": vals[3],
                    "Date": vals[4]
                })
    return pd.DataFrame(records)

def show():
    st.title("📊 Player Stats (Predefined Players)")
    st.markdown("Select a player to view their profile, rankings, and recent performance.")

    player_name = st.selectbox("Select Player", list(KNOWN_PLAYERS.keys()))
    player_id = KNOWN_PLAYERS[player_name]

    with st.spinner(f"Fetching stats for {player_name} (ID: {player_id})..."):
        profile = fetch_player_profile(player_id)

    if not profile:
        st.error("❌ Unable to fetch profile data.")
        return

    # Display basic profile
    if "image" in profile and profile["image"]:
        st.image(profile["image"], width=120)
    st.subheader(profile.get("name", "Unknown"))
    st.markdown(
        f"**Role:** {profile.get('role','')} | **Bat:** {profile.get('bat','')} | **Bowl:** {profile.get('bowl','')}"
    )
    st.markdown(f"**Teams:** {profile.get('teams','')}")

    # Rankings (if available)
    if "rankings" in profile:
        st.subheader("🌍 Rankings")
        st.json(profile["rankings"])

    # Recent performance
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🏏 Recent Batting")
        bat_df = parse_recent(profile, "recentBatting")
        if not bat_df.empty:
            st.dataframe(bat_df, use_container_width=True)
        else:
            st.info("No recent batting data.")
    with col2:
        st.subheader("🎯 Recent Bowling")
        bowl_df = parse_recent(profile, "recentBowling")
        if not bowl_df.empty:
            st.dataframe(bowl_df, use_container_width=True)
        else:
            st.info("No recent bowling data.")

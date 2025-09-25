import streamlit as st
import requests
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
RAPIDAPI_HOST = os.getenv("RAPIDAPI_HOST")
LIVE_URL = os.getenv("CRICBUZZ_LIVE_URL")
SCORECARD_URL = os.getenv("CRICBUZZ_SCORECARD_URL")

HEADERS = {
    "x-rapidapi-key": RAPIDAPI_KEY,
    "x-rapidapi-host": RAPIDAPI_HOST
}

@st.cache_data(ttl=60)  # cache live matches for 1 min
def fetch_live_matches():
    """Fetch live matches (cached)"""
    try:
        resp = requests.get(LIVE_URL, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        matches = []
        for series in data.get("typeMatches", []):
            for match in series.get("seriesMatches", []):
                if "seriesAdWrapper" in match:
                    for m in match["seriesAdWrapper"].get("matches", []):
                        info = m.get("matchInfo", {})
                        score = m.get("matchScore", {})

                        matches.append({
                            "match_id": info.get("matchId"),
                            "series_name": info.get("seriesName"),
                            "match_desc": info.get("matchDesc"),
                            "team1": info.get("team1", {}).get("teamName"),
                            "team2": info.get("team2", {}).get("teamName"),
                            "venue": info.get("venueInfo", {}).get("ground"),
                            "status": info.get("status"),
                            "score": f"{score.get('team1', {}).get('score', '')}/{score.get('team1', {}).get('wickets', '')} ({score.get('team1', {}).get('overs', '')})",
                        })
        return matches
    except Exception as e:
        st.error(f"Error fetching live matches: {e}")
        return []


def fetch_scorecard(match_id):
    """Fetch detailed scorecard (only when needed)"""
    try:
        url = f"{SCORECARD_URL}?matchId={match_id}"
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        st.error(f"Error fetching scorecard: {e}")
        return None


def show():
    st.title("⚡ Live Matches")
    st.markdown("Real-time cricket match updates with minimal API calls (trial safe).")

    if st.button("🔄 Refresh Live Data"):
        st.cache_data.clear()  # clear cache manually on refresh
        st.rerun()

    matches = fetch_live_matches()

    if not matches:
        st.warning("No live matches currently available.")
        return

    for match in matches:
        with st.container():
            st.markdown(f"### {match['match_desc']}")

            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                st.write(f"**Series**: {match['series_name']}")
                st.write(f"**Venue**: {match['venue']}")
                st.write(f"**Status**: 🟢 {match['status']}")

            with col2:
                st.write(f"**{match['team1']}** vs **{match['team2']}**")

            with col3:
                st.write("📊 **Score**")
                st.write(match['score'])

            # Expandable scorecard - only fetch when opened
            with st.expander("📑 View Detailed Scorecard"):
                score_data = fetch_scorecard(match["match_id"])
                if score_data and "scoreCard" in score_data:
                    for innings in score_data["scoreCard"]:
                        st.subheader(f"{innings.get('batTeam', {}).get('teamName', 'Unknown')} Innings")

                        # Batting Table
                        if "batTeamDetails" in innings:
                            batters = innings["batTeamDetails"].get("batsmenData", {}).values()
                            if batters:
                                bat_df = pd.DataFrame([
                                    {
                                        "Batsman": b.get("batName"),
                                        "Runs": b.get("runs"),
                                        "Balls": b.get("balls"),
                                        "4s": b.get("fours"),
                                        "6s": b.get("sixes"),
                                        "SR": b.get("strikeRate")
                                    }
                                    for b in batters
                                ])
                                st.write("**Batting**")
                                st.dataframe(bat_df)

                        # Bowling Table
                        if "bowlTeamDetails" in innings:
                            bowlers = innings["bowlTeamDetails"].get("bowlersData", {}).values()
                            if bowlers:
                                bowl_df = pd.DataFrame([
                                    {
                                        "Bowler": bw.get("bowlName"),
                                        "Overs": bw.get("overs"),
                                        "Runs": bw.get("runs"),
                                        "Wickets": bw.get("wickets"),
                                        "Economy": bw.get("economy")
                                    }
                                    for bw in bowlers
                                ])
                                st.write("**Bowling**")
                                st.dataframe(bowl_df)

            st.markdown("---")

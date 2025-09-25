import streamlit as st
import pandas as pd
from utils.db_connection import execute_query

def show():
    st.title("🛠️ CRUD Operations")
    
    # CRUD implementation with parameterized queries
    operation = st.selectbox("Operation", ["View Data", "Add Player", "Update Player", "Delete Player"])
    
    if operation == "View Data":
        table = st.selectbox("Select Table", ["players", "matches", "batting_stats", "bowling_stats"])
        if st.button("Load Data"):
            result = execute_query(f"SELECT * FROM {table} LIMIT 100")
            if result:
                df = pd.DataFrame(result[0], columns=result[1])
                st.dataframe(df)
    
    elif operation == "Add Player":
        with st.form("Add Form"):
            name = st.text_input("Player Name")
            country = st.selectbox("Country", ["India", "Australia", "England"])
            role = st.selectbox("Role", ["Batsman", "Bowler"])
            if st.form_submit_button("Add"):
                execute_query(
                    "INSERT INTO players (player_name, country, playing_role) VALUES (?, ?, ?)",
                    (name, country, role),
                    fetch=False
                )
                st.success("Player added!")
    
    elif operation == "Update Player":
        players = execute_query("SELECT player_id, player_name FROM players LIMIT 50")
        if players:
            player_map = {f"{name} (ID: {id})": id for id, name in players[0]}
            selected = st.selectbox("Select Player", list(player_map.keys()))
            new_name = st.text_input("New Name")
            if st.button("Update"):
                execute_query(
                    "UPDATE players SET player_name = ? WHERE player_id = ?",
                    (new_name, player_map[selected]),
                    fetch=False
                )
                st.success("Updated!")
    
    elif operation == "Delete Player":
        players = execute_query("SELECT player_id, player_name FROM players LIMIT 50")
        if players:
            player_map = {f"{name} (ID: {id})": id for id, name in players[0]}
            selected = st.selectbox("Select Player", list(player_map.keys()))
            if st.button("Delete"):
                execute_query(
                    "DELETE FROM players WHERE player_id = ?",
                    (player_map[selected],),
                    fetch=False
                )
                st.success("Deleted!")
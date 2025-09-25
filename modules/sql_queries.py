import streamlit as st
import pandas as pd
from utils.db_connection import execute_query

# Predefined SQL queries adapted to your schema
SQL_QUERIES = {
    "Beginner": {
        "Question 1: Indian Players": """
            SELECT player_name, playing_role, batting_style, bowling_style 
            FROM players 
            WHERE country = 'India';
        """,
        "Question 2: Recent Matches": """
            SELECT match_description, team1, team2, venue, match_date 
            FROM matches 
            WHERE match_date >= DATE('now','-7 day')
            ORDER BY match_date DESC;
        """,
        "Question 3: Top Run Scorers (ODI)": """
            SELECT player_name, total_runs, batting_avg, centuries 
            FROM batting_stats 
            WHERE format = 'ODI' 
            ORDER BY total_runs DESC 
            LIMIT 10;
        """,
        "Question 4: Large Venues": """
            SELECT venue_name, city, country, capacity 
            FROM venues 
            WHERE capacity > 30000 
            ORDER BY capacity DESC;
        """,
        "Question 5: Team Wins": """
            SELECT winner AS team_name, COUNT(*) AS total_wins
            FROM matches
            WHERE winner IS NOT NULL
            GROUP BY winner
            ORDER BY total_wins DESC;
        """,
        "Question 6: Players by Role": """
            SELECT playing_role, COUNT(*) AS player_count
            FROM players
            GROUP BY playing_role;
        """,
        "Question 7: Highest Individual Scores by Format": """
            SELECT format, MAX(highest_score) AS max_score
            FROM batting_stats
            GROUP BY format;
        """,
        "Question 8: Series in 2024 (Matches)": """
            SELECT match_description, team1, team2, match_date, venue
            FROM matches
            WHERE strftime('%Y', match_date) = '2024';
        """
    },

    "Intermediate": {
        "Question 9: All-rounders": """
            SELECT p.player_name, b.total_runs, bw.total_wickets, b.format
            FROM players p
            JOIN batting_stats b ON p.player_id = b.player_id
            JOIN bowling_stats bw ON p.player_id = bw.player_id
            WHERE b.total_runs > 1000 AND bw.total_wickets > 50
              AND p.playing_role LIKE '%All-rounder%';
        """,
        "Question 10: Recent Completed Matches": """
            SELECT match_description, team1, team2, winner, victory_margin, victory_type, venue
            FROM matches 
            WHERE status = 'Completed'
            ORDER BY match_date DESC 
            LIMIT 20;
        """,
        "Question 11: Player Format Comparison": """
            SELECT p.player_name,
                   SUM(CASE WHEN b.format = 'Test' THEN b.total_runs ELSE 0 END) AS TestRuns,
                   SUM(CASE WHEN b.format = 'ODI' THEN b.total_runs ELSE 0 END) AS ODIRuns,
                   SUM(CASE WHEN b.format = 'T20I' THEN b.total_runs ELSE 0 END) AS T20Runs,
                   AVG(b.batting_avg) AS overall_batting_avg
            FROM players p
            JOIN batting_stats b ON p.player_id = b.player_id
            GROUP BY p.player_name
            HAVING COUNT(DISTINCT b.format) >= 2;
        """,
        "Question 12: Home vs Away Performance": """
            SELECT team1 AS team,
                   SUM(CASE WHEN venue LIKE '%' || team1 || '%' THEN 1 ELSE 0 END) AS home_matches,
                   SUM(CASE WHEN venue NOT LIKE '%' || team1 || '%' THEN 1 ELSE 0 END) AS away_matches,
                   SUM(CASE WHEN venue LIKE '%' || team1 || '%' AND winner=team1 THEN 1 ELSE 0 END) AS home_wins,
                   SUM(CASE WHEN venue NOT LIKE '%' || team1 || '%' AND winner=team1 THEN 1 ELSE 0 END) AS away_wins
            FROM matches
            GROUP BY team1;
        """,
        "Question 13: 100+ Partnerships (Simplified)": """
            SELECT match_id, team1, team2, match_description,
                   'Partnerships > 100 runs (details need partnerships table)' AS note
            FROM matches
            LIMIT 5;
        """,
        "Question 14: Bowling at Venues": """
            SELECT p.player_name, m.venue,
                   AVG(bw.economy) AS avg_economy,
                   SUM(bw.wickets) AS total_wickets,
                   COUNT(bw.match_id) AS matches_played
            FROM bowling_stats bw
            JOIN players p ON bw.player_id = p.player_id
            JOIN matches m ON bw.match_id = m.match_id
            GROUP BY p.player_name, m.venue
            HAVING COUNT(bw.match_id) >= 3;
        """,
        "Question 15: Performance in Close Matches": """
            SELECT p.player_name, AVG(b.runs) AS avg_runs,
                   COUNT(m.match_id) AS total_close_matches,
                   SUM(CASE WHEN m.winner = b.team THEN 1 ELSE 0 END) AS wins
            FROM batting_stats b
            JOIN players p ON b.player_id = p.player_id
            JOIN matches m ON b.match_id = m.match_id
            WHERE (m.victory_type = 'Runs' AND m.victory_margin < 50)
               OR (m.victory_type = 'Wickets' AND m.victory_margin < 5)
            GROUP BY p.player_name;
        """,
        "Question 16: Yearly Batting Performance": """
            SELECT p.player_name, strftime('%Y', m.match_date) AS year,
                   AVG(b.runs) AS avg_runs,
                   AVG(b.strike_rate) AS avg_sr
            FROM batting_stats b
            JOIN players p ON b.player_id = p.player_id
            JOIN matches m ON b.match_id = m.match_id
            WHERE strftime('%Y', m.match_date) >= '2020'
            GROUP BY p.player_name, strftime('%Y', m.match_date)
            HAVING COUNT(b.match_id) >= 5;
        """
    },

    "Advanced": {
        "Question 17: Toss Advantage": """
            SELECT toss_decision,
                   COUNT(*) AS total_matches,
                   SUM(CASE WHEN toss_winner = winner THEN 1 ELSE 0 END) AS wins_after_toss,
                   ROUND(SUM(CASE WHEN toss_winner = winner THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS win_percentage
            FROM matches
            WHERE winner IS NOT NULL
            GROUP BY toss_decision;
        """,
        "Question 18: Economical Bowlers": """
            SELECT p.player_name, AVG(bw.economy) AS economy, SUM(bw.wickets) AS wickets
            FROM bowling_stats bw
            JOIN players p ON bw.player_id = p.player_id
            WHERE bw.format IN ('ODI','T20I')
            GROUP BY p.player_name
            HAVING COUNT(DISTINCT bw.match_id) >= 10
            ORDER BY economy ASC;
        """,
        "Question 19: Consistent Batsmen": """
            SELECT p.player_name,
                   AVG(b.runs) AS avg_runs,
                   (AVG(b.runs * b.runs) - AVG(b.runs) * AVG(b.runs)) AS run_variability
            FROM batting_stats b
            JOIN players p ON b.player_id = p.player_id
            JOIN matches m ON b.match_id = m.match_id
            WHERE m.match_date >= '2022-01-01' AND b.balls >= 10
            GROUP BY p.player_name;
        """,
        "Question 20: Matches by Format": """
            SELECT p.player_name,
                   SUM(CASE WHEN b.format='Test' THEN 1 ELSE 0 END) AS test_matches,
                   SUM(CASE WHEN b.format='ODI' THEN 1 ELSE 0 END) AS odi_matches,
                   SUM(CASE WHEN b.format='T20I' THEN 1 ELSE 0 END) AS t20_matches,
                   AVG(CASE WHEN b.format='Test' THEN b.batting_avg END) AS test_avg,
                   AVG(CASE WHEN b.format='ODI' THEN b.batting_avg END) AS odi_avg,
                   AVG(CASE WHEN b.format='T20I' THEN b.batting_avg END) AS t20_avg
            FROM batting_stats b
            JOIN players p ON b.player_id = p.player_id
            GROUP BY p.player_name
            HAVING (test_matches + odi_matches + t20_matches) >= 20;
        """,
        "Question 21: Player Ranking": """
            SELECT p.player_name, b.format,
                   (b.total_runs * 0.01) + (b.batting_avg * 0.5) + (b.strike_rate * 0.3) AS batting_points,
                   (bw.wickets * 2) + ((50 - bw.bowling_avg) * 0.5) + ((6 - bw.economy) * 2) AS bowling_points,
                   ((b.total_runs * 0.01) + (b.batting_avg * 0.5) + (b.strike_rate * 0.3) +
                   (bw.wickets * 2) + ((50 - bw.bowling_avg) * 0.5) + ((6 - bw.economy) * 2)) AS total_points
            FROM players p
            LEFT JOIN batting_stats b ON p.player_id = b.player_id
            LEFT JOIN bowling_stats bw ON p.player_id = bw.player_id AND b.format = bw.format
            WHERE b.total_runs > 0 OR bw.wickets > 0
            ORDER BY total_points DESC;
        """,
        "Question 22: Head-to-Head Analysis": """
            SELECT team1, team2,
                   COUNT(*) AS matches_played,
                   SUM(CASE WHEN winner=team1 THEN 1 ELSE 0 END) AS team1_wins,
                   SUM(CASE WHEN winner=team2 THEN 1 ELSE 0 END) AS team2_wins
            FROM matches
            WHERE match_date >= DATE('now','-3 year')
            GROUP BY team1, team2
            HAVING matches_played >= 5;
        """,
        "Question 23: Recent Player Form": """
            SELECT p.player_name,
                   AVG(b.runs) AS avg_runs,
                   AVG(b.strike_rate) AS avg_sr,
                   SUM(CASE WHEN b.runs >= 50 THEN 1 ELSE 0 END) AS fifties
            FROM batting_stats b
            JOIN players p ON b.player_id = p.player_id
            JOIN matches m ON b.match_id = m.match_id
            WHERE m.match_date >= DATE('now','-1 year')
            GROUP BY p.player_name;
        """,
        "Question 24: Batting Partnerships (Simplified)": """
            SELECT 'Partnership analysis requires partnerships table' AS note;
        """,
        "Question 25: Player Career Trajectory": """
            SELECT p.player_name, strftime('%Y', m.match_date) AS year,
                   AVG(b.runs) AS avg_runs, AVG(b.strike_rate) AS avg_sr
            FROM batting_stats b
            JOIN players p ON b.player_id = p.player_id
            JOIN matches m ON b.match_id = m.match_id
            GROUP BY p.player_name, strftime('%Y', m.match_date)
            HAVING COUNT(b.match_id) >= 3;
        """
    }
}


def show():
    st.title("🔍 SQL Analytics")
    
    st.markdown("""
    Execute pre-built SQL queries for advanced cricket analytics. 
    Select a query from the dropdown below to see the results.
    """)
    
    difficulty = st.selectbox("Select Difficulty Level", list(SQL_QUERIES.keys()))
    
    if difficulty:
        query_name = st.selectbox("Select Query", list(SQL_QUERIES[difficulty].keys()))
        
        if query_name:
            query = SQL_QUERIES[difficulty][query_name]
            
            st.subheader("SQL Query")
            st.code(query, language="sql")
            
            if st.button("Execute Query"):
                with st.spinner("Executing query..."):
                    result = execute_query(query)
                    
                    if result:
                        data, columns = result
                        if data:
                            df = pd.DataFrame(data, columns=columns)
                            st.subheader("Query Results")
                            st.dataframe(df)
                        else:
                            st.info("Query executed successfully but returned no results.")
                    else:
                        st.error("Error executing query. Please check your database connection.")
    
    # Custom query
    st.markdown("---")
    st.subheader("Custom SQL Query")
    custom_query = st.text_area("Enter your own SQL query:", height=150)
    
    if st.button("Execute Custom Query") and custom_query:
        with st.spinner("Executing custom query..."):
            result = execute_query(custom_query)
            
            if result:
                data, columns = result
                if data:
                    df = pd.DataFrame(data, columns=columns)
                    st.dataframe(df)
                else:
                    st.success("Query executed successfully.")
            else:
                st.error("Error executing custom query.")

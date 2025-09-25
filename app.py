import streamlit as st

st.set_page_config(
    page_title="Cricbuzz LiveStats",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    st.sidebar.title("🏏 Cricbuzz LiveStats")
    page = st.sidebar.radio(
        "Navigation",
        [
            "Home",
            "Live Matches",
            "Top Player Stats",
            "SQL Analytics",
            "CRUD Operations"
        ]
    )

    if page == "Home":
        from modules import home
        home.show()
    elif page == "Live Matches":
        from modules import live_matches
        live_matches.show()
    elif page == "Top Player Stats":
        from modules import top_stats
        top_stats.show()
    elif page == "SQL Analytics":
        from modules import sql_queries
        sql_queries.show()
    elif page == "CRUD Operations":
        from modules import crud_operations
        crud_operations.show()

if __name__ == "__main__":
    main()

import streamlit as st

def show():
    st.title("🏏 Cricbuzz LiveStats: Real-Time Cricket Insights")
    
    st.markdown("""
    ## Welcome to Cricket Analytics Dashboard
    
    This comprehensive platform delivers real-time cricket statistics and advanced analytics 
    powered by SQL-based data processing.
    """)
    
    # Project Overview
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("**Real-time Updates** ⚡")
        st.write("Live match data from Cricbuzz API")
    
    with col2:
        st.info("**Advanced Analytics** 📊")
        st.write("SQL-driven insights and visualizations")
    
    with col3:
        st.info("**Data Management** 🛠️")
        st.write("Full CRUD operations for database management")
    
    # Features Section
    st.markdown("---")
    st.header("📋 Features")
    
    features = {
        "Live Match Tracking": "Real-time scorecards and match updates",
        "Player Statistics": "Detailed batting, bowling, and fielding stats",
        "SQL Analytics": "25+ pre-built analytical queries",
        "Data Management": "Add, update, and delete records",
        "Multi-format Support": "Test, ODI, and T20I cricket data"
    }
    
    for feature, description in features.items():
        st.write(f"✅ **{feature}**: {description}")
    
    # Technology Stack
    st.markdown("---")
    st.header("🛠️ Technology Stack")
    
    tech_col1, tech_col2, tech_col3 = st.columns(3)
    
    with tech_col1:
        st.write("**Backend**")
        st.write("- Python 3.8+")
        st.write("- Streamlit")
        st.write("- REST API Integration")
    
    with tech_col2:
        st.write("**Database**")
        st.write("- MySQL/PostgreSQL")
        st.write("- SQLite (Development)")
        st.write("- Advanced SQL Queries")
    
    with tech_col3:
        st.write("**Frontend**")
        st.write("- Streamlit UI")
        st.write("- Real-time Updates")
        st.write("- Interactive Charts")
    
    # Getting Started
    st.markdown("---")
    st.header("🚀 Getting Started")
    
    st.markdown("""
    1. **Configure Database**: Set up your database connection in `.env` file
    2. **Install Dependencies**: Run `pip install -r requirements.txt`
    3. **Run Application**: Execute `streamlit run app.py`
    4. **Explore Features**: Navigate through different sections using the sidebar
    """)
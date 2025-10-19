import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os
import sys
from psycopg2 import sql
import plotly.express as px
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from ai_assistant_project.app.db.connection import db_connection

def get_data():
    try:
        conn = db_connection()
        cur = conn.cursor()
        sql_insert = f'SELECT "Machine_ID","Temperature_C","Vibration_mms","Sound_dB","Oil_Level_pct","Coolant_Level_pct" FROM sensor_readings WHERE "Vibration_mms" > (SELECT AVG("Vibration_mms") * 1.25 FROM sensor_readings) or "Coolant_Level_pct" < (SELECT AVG("Coolant_Level_pct") * 0.25 FROM sensor_readings) limit 5;'
        cur.execute(sql_insert)
        machine_data = cur.fetchall()
        if machine_data:
            print("there are machines found!")
            return machine_data
        print(f"there are no machines found in db!")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if conn:
            cur.close()
            conn.close()

def main():
    # Custom CSS for elegant dashboard design
    css = """
    <style>
    /* Hide Streamlit's default navigation */
    [data-testid="stSidebarNav"] {
        display: none;
    }

    /* Global styles */
    body {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        background-color: #1E1E1E;
        color: #FFFFFF;
    }

    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #2A2A2A 0%, #1E1E1E 100%);
        border-right: 1px solid #3A3A3A;
        padding: 20px;
    }
    .stButton > button {
        background-color: #FF6F61;
        color: white;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        background-color: #E55A50;
        transform: translateY(-2px);
    }

    /* Title styling */
    h1 {
        text-align: center;
        font-size: 2.5rem;
        font-weight: 600;
        margin-bottom: 20px;
        color: #FFFFFF;
        text-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }

    /* Metric card styling */
    .stMetric {
        background: linear-gradient(135deg, #2A2A2A 0%, #252525 100%);
        border: 1px solid #3A3A3A;
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.2);
        transition: transform 0.2s ease;
    }
    .stMetric:hover {
        transform: translateY(-3px);
    }
    .stMetric label {
        font-size: 1.1rem;
        font-weight: 500;
        color: #F7CAC9;
        animation: colorChange 10s infinite linear;
    }
    .stMetric > div > div > div > div {
        font-size: 1.5rem;
        font-weight: 600;
        animation: colorChange 10s infinite linear;
    }
    @keyframes colorChange {
        0% { color: #FF6F61; }
        20% { color: #6B5B95; }
        40% { color: #88B04B; }
        60% { color: #F7CAC9; }
        80% { color: #92A8D1; }
        100% { color: #FF6F61; }
    }

    /* Table styling */
    .stDataFrame {
        background-color: #252525;
        border-radius: 8px;
        overflow: hidden;
    }
    .stDataFrame table {
        width: 100%;
        border-collapse: collapse;
    }
    .stDataFrame th {
        background-color: #3A3A3A;
        color: #FFFFFF;
        font-weight: 500;
        padding: 12px;
        text-align: left;
    }
    .stDataFrame td {
        padding: 12px;
        border-bottom: 1px solid #3A3A3A;
        color: #D3D3D3;
    }
    .stDataFrame tr:nth-child(even) {
        background-color: #2E2E2E;
    }
    .stDataFrame tr:hover {
        background-color: #353535;
    }

    /* Gauge styling */
    .stPlotlyChart {
        background: linear-gradient(135deg, #2A2A2A 0%, #252525 100%);
        border: 1px solid #3A3A3A;
        border-radius: 12px;
        padding: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.2);
    }

    /* Alert panel card styling */
    .alert-card {
        background: linear-gradient(135deg, #2A2A2A 0%, #252525 100%);
        border: 1px solid #3A3A3A;
        border-radius: 12px;
        padding: 20px;
        margin-left: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.2);
        transition: transform 0.2s ease;
    }
    .alert-card:hover {
        transform: translateY(-3px);
    }
    .alert-card h3 {
        font-size: 1.3rem;
        font-weight: 600;
        color: #F7CAC9;
        margin-bottom: 15px;
        animation: colorChange 10s infinite linear;
    }
    .alert-card p {
        font-size: 1rem;
        color: #D3D3D3;
        margin-bottom: 10px;
        line-height: 1.5;
    }
    .alert-card p strong {
        color: #FFFFFF;
        font-weight: 600;
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

    # Center-aligned title
    st.markdown("<h1>⭕ Operator Dashboard</h1>", unsafe_allow_html=True)

    # Sidebar with Back button
    with st.sidebar:
        if st.button("Back to Main Page"):
            st.switch_page("app.py")

    col1, col2, col3 = st.columns([2, 1, 1])

    columns = ["Temperature_C", "Vibration_mms", "Sound_dB", "Oil_Level_pct", "Coolant_Level_pct"]

    with col1:
        st.markdown("**Machine Sensors**")
        data_completed = get_data()
        data_without_machine_id = [row[1:] for row in data_completed]
        data = pd.DataFrame(data_without_machine_id, columns=columns)
        st.table(data)

        # Alert panel card
        data = pd.DataFrame(data_completed, columns=["Machine_ID"] + columns)
        most_machine_vibration = data[data["Vibration_mms"] == data["Vibration_mms"].max()]["Machine_ID"].values[0]
        least_machine_coolant = data[data["Coolant_Level_pct"] == data["Coolant_Level_pct"].min()]["Machine_ID"].values[0]
        st.markdown(
            f"""
            <div class="alert-card">
                <h3>Alert Panel</h3>
                <p><strong>Machine {most_machine_vibration}</strong> → Vibration is the most above threshold</p>
                <p><strong>Machine {least_machine_coolant}</strong> → Coolant is the least under threshold</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        data_completed = pd.DataFrame(data_completed, columns=["Machine_ID"] + columns)
        value = data_completed[data_completed["Machine_ID"] == most_machine_vibration]["Vibration_mms"].values[0]
        end = int(value * 1.25)
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=value,
            number={'suffix': f"/{end}"},
            title={'text': "Vibration (mm/s)", 'font': {'color': '#FFFFFF'}},
            gauge={
                'axis': {'range': [0, end], 'tickcolor': '#FFFFFF', 'tickfont': {'color': '#FFFFFF'}},
                'bar': {'color': "#FF6F61"},
                'steps': [
                    {'range': [0, value], 'color': "#3A3A3A"},
                    {'range': [value, end], 'color': "#2E2E2E"}
                ],
                'bgcolor': "#252525"
            }
        ))
        fig.update_layout(
            plot_bgcolor="#252525",
            paper_bgcolor="#252525",
            font=dict(color="#FFFFFF"),
            margin=dict(l=20, r=20, t=50, b=20)
        )
        st.plotly_chart(fig, use_container_width=True)

    with col3:
        value = data_completed[data_completed["Machine_ID"] == least_machine_coolant]["Coolant_Level_pct"].values[0]
        end = int(value * 1.75)
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=value,
            number={'suffix': f"/{end}"},
            title={'text': "Coolant Level (%)", 'font': {'color': '#FFFFFF'}},
            gauge={
                'axis': {'range': [0, end], 'dtick': 30, 'tickcolor': '#FFFFFF', 'tickfont': {'color': '#FFFFFF'}},
                'bar': {'color': "#92A8D1"},
                'steps': [
                    {'range': [0, value], 'color': "#3A3A3A"},
                    {'range': [value, end], 'color': "#2E2E2E"}
                ],
                'bgcolor': "#252525"
            }
        ))
        fig.update_layout(
            plot_bgcolor="#252525",
            paper_bgcolor="#252525",
            font=dict(color="#FFFFFF"),
            margin=dict(l=20, r=20, t=50, b=20)
        )
        st.plotly_chart(fig, use_container_width=True)

if __name__ == '__main__':
    main()
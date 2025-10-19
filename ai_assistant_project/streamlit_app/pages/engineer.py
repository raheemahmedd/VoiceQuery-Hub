import re
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import os
import sys
from psycopg2 import sql

# Adjust sys.path for module import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))
from ai_assistant_project.app.db.connection import db_connection

# Cache query results to avoid repeated database calls
@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_data(query):
    """Fetch data from the database using the provided SQL query."""
    conn = None
    cur = None
    try:
        conn = db_connection()
        cur = conn.cursor()
        cur.execute(query)
        sensor_readings = cur.fetchall()
        if sensor_readings:
            print(f"Machines found for query: {query[:50]}...")
            return sensor_readings[:100]  # Limit to 100 rows
        print(f"No machines found for query: {query[:50]}...")
        return []
    except Exception as e:
        print(f"Error executing query: {e}")
        return []
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

def extract_columns(query):
    """Extract column names from an SQL SELECT query."""
    pattern = r'SELECT\s+(.+?)\s+FROM'
    match = re.search(pattern, query, re.IGNORECASE)
    if match:
        columns_str = match.group(1)
        columns = [col.strip().strip('"').split(' AS ')[-1].strip() for col in columns_str.split(',')]
        return columns
    print("No columns found in query!")
    return []

@st.cache_data
def create_visualization(df, columns, idx):
    """Create a Plotly visualization based on the query index and DataFrame."""
    try:
        # Limit DataFrame to 100 rows for plotting
        df = df.head(100)
        if idx == 0:  # Machine_Type, Operational_Hours, Temperature_C
            fig = px.scatter(
                df,
                x=columns[1],
                y=columns[2],
                color=columns[0],
                title="Temperature vs. Operational Hours",
                labels={columns[1]: "Operational Hours", columns[2]: "Temperature (°C)"}
            )
        elif idx == 1:  # Machine_Type, Remaining_Useful_Life_days
            fig = px.histogram(
                df,
                x=columns[1],
                color=columns[0],
                title="Remaining Useful Life",
                labels={columns[1]: "Remaining Useful Life (days)"}
            )
        elif idx == 2:  # month_year, failure_count
            fig = px.line(
                df,
                x=columns[0],
                y=columns[1],
                title="Monthly Failure Count",
                labels={columns[0]: "Month", columns[1]: "Failure Count"}
            )
        elif idx == 3:  # Machine_ID, Vibration_mms, Sound_dB
            fig = px.scatter(
                df,
                x=columns[1],
                y=columns[2],
                title="Vibration vs. Sound",
                labels={columns[1]: "Vibration (mm/s)", columns[2]: "Sound (dB)"}
            )
        elif idx == 4:  # Installation_Year, avg_power
            fig = px.bar(
                df,
                x=columns[0],
                y=columns[1],
                title="Avg Power by Installation Year",
                labels={columns[0]: "Installation Year", columns[1]: "Avg Power (kW)"}
            )
        elif idx == 5:  # Maintenance_History_Count, avg_error_codes
            fig = px.bar(
                df,
                x=columns[0],
                y=columns[1],
                title="Avg Error Codes by Maintenance",
                labels={columns[0]: "Maintenance Count", columns[1]: "Avg Error Codes"}
            )
        elif idx == 6:  # AI_Supervision, Heat_Index, Coolant_Flow_L_min
            fig = px.scatter(
                df,
                x=columns[1],
                y=columns[2],
                color=columns[0],
                title="Heat Index vs. Coolant Flow",
                labels={columns[1]: "Heat Index", columns[2]: "Coolant Flow (L/min)"}
            )
        else:
            return None
        # Simplify layout to reduce rendering time
        fig.update_layout(
            plot_bgcolor="#252525",
            paper_bgcolor="#252525",
            font=dict(color="#FFFFFF", size=10),
            margin=dict(l=10, r=10, t=30, b=10),
            showlegend=False  # Disable legend to reduce complexity
        )
        return fig
    except Exception as e:
        print(f"Error creating visualization for query {idx}: {e}")
        return None

def main():
    # Simplified CSS without animations to reduce browser load
    css = """
    <style>
    /* Hide Streamlit's default navigation */
    [data-testid="stSidebarNav"] {
        display: none;
    }

    /* Global styles */
    body {
        font-family: 'Inter', sans-serif;
        background-color: #1E1E1E;
        color: #FFFFFF;
    }

    /* Sidebar styling */
    .stSidebar {
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
        font-size: 2rem;
        font-weight: 600;
        margin-bottom: 20px;
        color: #FFFFFF;
    }

    /* Metric card styling */
    .stMetric {
        background: #2A2A2A;
        border: 1px solid #3A3A3A;
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.2);
    }
    .stMetric label {
        font-size: 1rem;
        font-weight: 500;
        color: #F7CAC9;
    }
    .stMetric > div > div > div > div {
        font-size: 1.2rem;
        font-weight: 600;
        color: #FFFFFF;
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
        padding: 10px;
    }
    .stDataFrame td {
        padding: 10px;
        border-bottom: 1px solid #3A3A3A;
        color: #D3D3D3;
    }
    .stDataFrame tr:nth-child(even) {
        background-color: #2E2E2E;
    }
    .stDataFrame tr:hover {
        background-color: #353535;
    }

    /* Plotly chart styling */
    .stPlotlyChart {
        background: #2A2A2A;
        border: 1px solid #3A3A3A;
        border-radius: 12px;
        padding: 10px;
    }

    /* Alert panel card styling */
    .alert-card {
        background: #2A2A2A;
        border: 1px solid #3A3A3A;
        border-radius: 12px;
        padding: 15px;
        margin-left: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.2);
    }
    .alert-card h3 {
        font-size: 1.2rem;
        font-weight: 600;
        color: #F7CAC9;
        margin-bottom: 10px;
    }
    .alert-card p {
        font-size: 0.9rem;
        color: #D3D3D3;
        margin-bottom: 8px;
    }
    .alert-card p strong {
        color: #FFFFFF;
        font-weight: 600;
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

    # Center-aligned title
    st.markdown("<h1>👷🏻 Engineer Dashboard</h1>", unsafe_allow_html=True)

    # Sidebar with Back button and visualization selector
    with st.sidebar:
        if st.button("Back to Main Page"):
            st.switch_page("app.py")
        # Allow user to select which visualization to display
        viz_options = [
            "Temperature vs. Operational Hours",
            "Remaining Useful Life",
            "Monthly Failure Count",
            "Vibration vs. Sound",
            "Avg Power by Installation Year",
            "Avg Error Codes by Maintenance",
            "Heat Index vs. Coolant Flow"
        ]
        selected_viz = st.selectbox("Select Visualization", ["None"] + viz_options)

    # Define queries
    queries = [
        """SELECT "Machine_Type", "Operational_Hours", "Temperature_C"
        FROM sensor_readings
        WHERE "Operational_Hours" IS NOT NULL AND "Temperature_C" IS NOT NULL
        LIMIT 100;""",
        """SELECT "Machine_Type", "Remaining_Useful_Life_days"
        FROM sensor_readings
        WHERE "Remaining_Useful_Life_days" IS NOT NULL
        LIMIT 100;""",
        """SELECT DATE_TRUNC('month', created_at) AS month_year, COUNT(*) AS failure_count
        FROM sensor_readings
        WHERE "Failure_Within_7_Days" = TRUE
        GROUP BY DATE_TRUNC('month', created_at)
        ORDER BY month_year
        LIMIT 100;""",
        """SELECT "Machine_ID", "Vibration_mms", "Sound_dB"
        FROM sensor_readings
        WHERE "Vibration_mms" IS NOT NULL AND "Sound_dB" IS NOT NULL
        LIMIT 100;""",
        """SELECT "Installation_Year", AVG("Power_Consumption_kW") AS avg_power
        FROM sensor_readings
        WHERE "Installation_Year" IS NOT NULL AND "Power_Consumption_kW" IS NOT NULL
        GROUP BY "Installation_Year"
        ORDER BY "Installation_Year"
        LIMIT 100;""",
        """SELECT "Maintenance_History_Count", AVG("Error_Codes_Last_30_Days") AS avg_error_codes
        FROM sensor_readings
        WHERE "Maintenance_History_Count" IS NOT NULL AND "Error_Codes_Last_30_Days" IS NOT NULL
        GROUP BY "Maintenance_History_Count"
        ORDER BY "Maintenance_History_Count"
        LIMIT 100;""",
        """SELECT "AI_Supervision", "Heat_Index", "Coolant_Flow_L_min"
        FROM sensor_readings
        WHERE "Heat_Index" IS NOT NULL AND "Coolant_Flow_L_min" IS NOT NULL
        LIMIT 100;"""
    ]

    # Display selected visualization
    if selected_viz != "None":
        idx = viz_options.index(selected_viz)
        query = queries[idx]
        with st.spinner(f"Loading {selected_viz}..."):
            columns = extract_columns(query)
            if not columns:
                st.error(f"Failed to extract columns for {selected_viz}")
            else:
                data = get_data(query)
                if not data:
                    st.warning(f"No data returned for {selected_viz}")
                else:
                    df = pd.DataFrame(data, columns=columns)
                    st.markdown(f"**{selected_viz} Data**")
                    st.table(df.head(50))  # Limit table to 50 rows
                    fig = create_visualization(df, columns, idx)
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)

    # Machine sensors and gauges
    sensor_query = """SELECT "Machine_ID", "Temperature_C", "Vibration_mms", "Sound_dB", "Oil_Level_pct", "Coolant_Level_pct"
    FROM sensor_readings
    WHERE "Vibration_mms" > (SELECT AVG("Vibration_mms") * 1.25 FROM sensor_readings)
    OR "Coolant_Level_pct" < (SELECT AVG("Coolant_Level_pct") * 0.25 FROM sensor_readings)
    LIMIT 5;"""
    columns = ["Machine_ID", "Temperature_C", "Vibration_mms", "Sound_dB", "Oil_Level_pct", "Coolant_Level_pct"]

    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        st.markdown("**Machine Sensors**")
        with st.spinner("Loading machine sensor data..."):
            data_completed = get_data(sensor_query)
            if not data_completed:
                st.warning("No machine sensor data available")
            else:
                data_without_machine_id = [row[1:] for row in data_completed]
                data = pd.DataFrame(data_without_machine_id, columns=columns[1:])
                st.table(data)

                # Alert panel card
                data = pd.DataFrame(data_completed, columns=columns)
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
        if data_completed:
            data = pd.DataFrame(data_completed, columns=columns)
            value = data[data["Machine_ID"] == most_machine_vibration]["Vibration_mms"].values[0]
            end = int(value * 1.25)
            with st.spinner("Loading vibration gauge..."):
                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=value,
                    number={'suffix': f"/{end}"},
                    title={'text': "Vibration (mm/s)", 'font': {'color': '#FFFFFF', 'size': 12}},
                    gauge={
                        'axis': {'range': [0, end], 'tickcolor': '#FFFFFF', 'tickfont': {'color': '#FFFFFF', 'size': 10}},
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
                    font=dict(color="#FFFFFF", size=10),
                    margin=dict(l=10, r=10, t=30, b=10)
                )
                st.plotly_chart(fig, use_container_width=True)

    with col3:
        if data_completed:
            data = pd.DataFrame(data_completed, columns=columns)
            value = data[data["Machine_ID"] == least_machine_coolant]["Coolant_Level_pct"].values[0]
            end = int(value * 1.75)
            with st.spinner("Loading coolant gauge..."):
                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=value,
                    number={'suffix': f"/{end}"},
                    title={'text': "Coolant Level (%)", 'font': {'color': '#FFFFFF', 'size': 12}},
                    gauge={
                        'axis': {'range': [0, end], 'dtick': 30, 'tickcolor': '#FFFFFF', 'tickfont': {'color': '#FFFFFF', 'size': 10}},
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
                    font=dict(color="#FFFFFF", size=10),
                    margin=dict(l=10, r=10, t=30, b=10)
                )
                st.plotly_chart(fig, use_container_width=True)

if __name__ == '__main__':
    main()
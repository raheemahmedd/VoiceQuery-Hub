import streamlit as st
import pandas as pd

import os
import  sys
from psycopg2 import sql
import plotly.express as px
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from ai_assistant_project.app.db.connection import db_connection


columns=["installation year","operational hours","temperature","vibration in mms","sound db","oil Level pct","coolant level pct","power consumption","maintenance history count","failture history count","remaining useful days","laster intensity","hydraulic pressure bar","coolant flow","heat index"]
def get_total_machine_numbers():

     try:
          conn=db_connection()
          cur = conn.cursor()
          sql_insert = f'select count("Machine_ID") from sensor_readings;'
          cur.execute(sql_insert)
            # Fetch all results
          machine_numbers = cur.fetchall()
          if machine_numbers:
            print("there are machines found!")
            return machine_numbers
          print(f"there are no machines found in db!")
     except Exception as e:
            print(f"An unexpected error occurred: {e}")
     finally:
             if conn:
                  cur.close()
                  conn.close()

def machines_failed_within_7():

     try:
          conn=db_connection()
          cur = conn.cursor()
          sql_insert = f'SELECT 100. * COUNT(CASE WHEN "Failure_Within_7_Days" = TRUE THEN 1 END) / COUNT(*) AS failure_percentage FROM sensor_readings;'
          cur.execute(sql_insert)
            # Fetch all results
          fail_perecnt = cur.fetchall()
          if fail_perecnt:
            print("there are machines found!")
            return fail_perecnt
          print(f"there are no machines found in db!")
     except Exception as e:
            print(f"An unexpected error occurred: {e}")
     finally:
             if conn:
                  cur.close()
                  conn.close()


def get_similar_column(column_name):
     try:
          conn=db_connection()
          cur = conn.cursor()
           # Enable pg_trgm extension first (outside query)
          cur.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm;")
          conn.commit()
          sql_insert = f"""
     
        -- Example: find closest match to a typo 'Failur_Within_7day'
         SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'sensor_readings'
            ORDER BY similarity(column_name, %s) DESC
            LIMIT 1; 
        """
          cur.execute(sql_insert,(column_name,))
          correct_column_name = cur.fetchone()
          if correct_column_name:
            print("the corrected column name found")
            return correct_column_name[0]
          print(f"there is no column similar found in db!")
     except Exception as e:
            print(f"An unexpected error occurred: {e}")
     finally:
             if conn:
                  cur.close()
                  conn.close()

def build_query(col_name,aggregate):
     try:
          conn=db_connection()
          cur = conn.cursor()
          query = sql.SQL("SELECT {func}({col}) FROM public.sensor_readings").format(
            func=sql.SQL(aggregate),  # aggregate function (AVG, COUNT, etc.)
            col=sql.Identifier(col_name)  # column name safely quoted
        )
          cur.execute(query)
          query_result = cur.fetchone()
          if query_result:
                    print("the corrected column name found")
                    return query_result[0]
          print(f"there is no column similar found in db!")
     except Exception as e:
            print(f"An unexpected error occurred: {e}")
     finally:
            if conn:
                cur.close()
                conn.close()

def main_plot_query(col_name):
     try:
          conn=db_connection()
          cur = conn.cursor()
          query = sql.SQL(
            'SELECT "Machine_ID" ,{col} FROM public.sensor_readings ORDER BY {col} DESC LIMIT 5'
        ).format(
            col=sql.Identifier(col_name)  # safely inject column name
        )

          cur.execute(query)
          query_result = cur.fetchall()
          if query_result:
                    print("main_plot_query done successfully")
                    return query_result
          print(f"main_plot_query not successfully done")
     except Exception as e:
            print(f"An unexpected error occurred: {e}")
     finally:
            if conn:
                cur.close()
                conn.close()    


def sub_plot_query():
     try:
          conn=db_connection()
          cur = conn.cursor()
          query =""" 
                
                SELECT
                    COUNT(CASE WHEN "Remaining_Useful_Life_days" > 452 THEN 1 END) AS healthy,
                    COUNT(CASE WHEN "Remaining_Useful_Life_days" < 225 THEN 1 END) AS critical,
                    COUNT(CASE WHEN "Remaining_Useful_Life_days" >= 225 AND "Remaining_Useful_Life_days" <= 452 THEN 1 END) AS warning
                FROM sensor_readings;

                """
        

          cur.execute(query)
          query_result = cur.fetchall()
          if query_result:
                    print("sub plot query done successfully")
                    return query_result
          print(f"sub plot query not successfully done")
     except Exception as e:
            print(f"An unexpected error occurred: {e}")
     finally:
            if conn:
                cur.close()
                conn.close()    

def main():
    # Custom CSS to style the selectbox container and hide default navigation
    css = """
    <style>
    /* Hide Streamlit's default multi-page navigation in the sidebar */
    [data-testid="stSidebarNav"] {
        display: none;
    }
    
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

    # Center-aligned title in main content area
    st.markdown("<h1 style='text-align: center;'> 🎯 Admin Dashboard 🎯 </h1>", unsafe_allow_html=True)

    # Sidebar with selectbox and Back button
    with st.sidebar:
        # Back button to main page
        if st.button("Back to Main Page"):
            st.switch_page("app.py")  # Adjust to your main page file, e.g., "pages/main.py"

        # Selectbox with DataFrame column names, wrapped in styled div
        st.markdown('<div class="Testing">', unsafe_allow_html=True)
        selected_column = st.selectbox(
            "**Select Column :**",  # Updated label for clarity
            columns  # Use DataFrame column names as options
        )
        st.markdown('</div>', unsafe_allow_html=True)
        selected_metric = st.selectbox(
            "**Select metric :**",  # Updated label for clarity
            ["average","maximum","minimum"]  # Use DataFrame column names as options
        )
        st.markdown('</div>', unsafe_allow_html=True)
        map_selected_metric={
             "average":"AVG",
             "maximum":"max",
             "minimum":"min",
        }
        pre_map=selected_metric
        selected_metric=map_selected_metric[pre_map]
  
    st.markdown("""
        <style>
        .stMetric {
            border: 3px solid white;
            border-radius: 15px;
            padding: 10px;
            background-color: #1E1E1E;
            color: white;
        }
        @keyframes colorChange {
        0% { color: #FF6F61; }  /* Coral */
        20% { color: #6B5B95; } /* Purple */
        40% { color: #88B04B; } /* Green */
        60% { color: #F7CAC9; } /* Light Pink */
        80% { color: #92A8D1; } /* Light Blue */
        100% { color: #FF6F61; } /* Back to Coral */
    }
        .stMetric > div > div > div > div {
            animation: colorChange 10s infinite linear !important;
        }
        .stMetric label {
            animation: colorChange 10s infinite linear !important;
        }
        </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            label="Total Machines",
            value=int(get_total_machine_numbers()[0][0])
        )

    with col2:
        st.metric(
            label="Machines Failed Within 7",
            value=f"{float(round(machines_failed_within_7()[0][0], 1))} %"
        )

    with col3:
        st.metric(
            label=f"{pre_map} {selected_column}",
            value=float(round(build_query(aggregate=selected_metric, col_name=get_similar_column(selected_column)), 2))
        )

    st.markdown("""
    <style>
   
    .stPlotlyChart {
        background-color: transparent !important;
        border: 2px solid white;
            border-radius: 8px;
    }
    </style>
""", unsafe_allow_html=True)

    correct_column_name = get_similar_column(selected_column)
    data = main_plot_query(col_name=correct_column_name)
    
    df = pd.DataFrame(data, columns=["Machine_ID", f"{correct_column_name}"])

    # Create bar chart
    fig_bar = px.bar(df, 
                    x=df.index, 
                    y=f"{correct_column_name}", 
                    title=f"Top Machines by {correct_column_name}",
                    text=f"{correct_column_name}")

    y_min = df[f"{correct_column_name}"].min()
    y_max = df[f"{correct_column_name}"].max()
    padding = (y_max - y_min) * 0.12
    y_start = y_min - padding

    fig_bar.update_traces(textposition="outside")  # show labels on bars

    # Set machine IDs as tick labels
    fig_bar.update_layout(
        xaxis=dict(
            tickmode="array",
            tickvals=df.index,
            ticktext=df["Machine_ID"],  # show Machine_ID under each bar
            title="Machine ID"  # start from min index
        ),
        yaxis=dict(
            title=correct_column_name,
            range=[y_start, y_max]  # start slightly before min
        ),
        plot_bgcolor="#1E1E1E",
        paper_bgcolor="#1E1E1E",
        font=dict(color="white"),
        title_font=dict(color="white"),
        xaxis_title_font=dict(color="white"),
        yaxis_title_font=dict(color="white"),
        xaxis_tickfont=dict(color="white"),
        yaxis_tickfont=dict(color="white")
    )

    data = sub_plot_query()
    df = pd.DataFrame(data, columns=["healthy", "critical", "warning"])
    df_melted = df.melt(var_name="Condition", value_name="Count")

    # Create Pie Chart
    fig_pie = px.pie(
        df_melted,
        names="Condition",
        values="Count",
        title="Machine Health Status Distribution",
        color="Condition",
        color_discrete_map={
            "critical": "red",
            "warning": "yellow",
            "healthy": "aquamarine"
        }
    )

    fig_pie.update_layout(
        plot_bgcolor="#1E1E1E",
        paper_bgcolor="#1E1E1E",
        font=dict(color="white"),
        title_font=dict(color="white")
    )

    # Arrange plots side by side in columns for dashboard view
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="plot-container">', unsafe_allow_html=True)
        st.plotly_chart(fig_bar, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="plot-container">', unsafe_allow_html=True)
        st.plotly_chart(fig_pie, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == '__main__':
    main()
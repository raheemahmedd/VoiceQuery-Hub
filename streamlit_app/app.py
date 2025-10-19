import streamlit as st
import requests
import pandas as pd
from pydantic import BaseModel ,Field
from typing import Optional
from datetime import datetime
from typing import Literal
class MachineData(BaseModel):
    """Always use this tool to structure your response to the user.
    the keys should be all have the same with sql_db_query values.
    """
    Machine_ID: str
    Machine_Type: str
    Installation_Year: int
    Operational_Hours: Optional[float] = None
    Temperature_C: Optional[float] = None
    Vibration_mms: Optional[float] = None
    Sound_dB: Optional[float] = None
    Oil_Level_pct: Optional[float] = None
    Coolant_Level_pct: Optional[float] = None
    Power_Consumption_kW: Optional[float] = None
    Last_Maintenance_Days_Ago: Optional[int] = None
    Maintenance_History_Count: Optional[int] = None
    Failure_History_Count: Optional[int] = None
    AI_Supervision: Optional[bool] = None
    Error_Codes_Last_30_Days: Optional[int] = None
    Remaining_Useful_Life_days: Optional[int] = None
    Failure_Within_7_Days: Optional[bool] = None
    Laser_Intensity: Optional[float] = None
    Hydraulic_Pressure_bar: Optional[float] = None
    Coolant_Flow_L_min: Optional[float] = None
    Heat_Index: Optional[float] = None
    AI_Override_Events: Optional[int] = None
    created_at: Optional[datetime] = None
    overall_llm_opinion_response:str
    combined_prediction: Optional[str] = None  # New field for concatenated 

# from ..app.schemas.db_agent_schema import MachineData
from typing import Optional, List, Dict, Any
# from app.schemas.db_agent_schema import MachineData

def process_final_response(final_response: List[Any]) -> List[Dict]:
    """
    Process the final_response array to combine MachineData and predictions into a table-friendly structure.
    Args:
        final_response: List containing MachineData instances and/or a prediction dictionary.
    Returns:
        List of dictionaries, each containing MachineData fields and a combined_prediction field.
    """
    tables_data = []
    
    # Process each MachineData instance
    for item in final_response:

        if isinstance(item, dict):
            param_value_pairs = [(key, value) for key, value in item.items()]
            # Create a DataFrame with 'Parameters' and 'Values' columns
            df = pd.DataFrame(param_value_pairs, columns=["Parameters", "Values"])
            tables_data.append(df)
            

    return tables_data


def main():
    css = """
    <style>
    /* Hide Streamlit's default multi-page navigation in the sidebar */
    [data-testid="stSidebarNav"] {
        display: none;
    }
    
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
    st.set_page_config(page_title="Predictive Maintenance App", layout="wide")
    st.title(":brain: Intelligence Predictive Maintenance App")
    st.markdown('<p style="font-size: 24px;">Let’s just make sure the machines are doing fine!</p>', unsafe_allow_html=True)
    # Apply custom CSS to style the audio input widget
    
    st.markdown(
        """
        <style>
        /* Target the audio input widget container */
        div[data-testid="stAudioInput"] {
            width: 20% !important;  /* Set desired width (e.g., 75%, 300px, etc.) */
            margin: left;  /* Center the widget */
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Initialize session state variables
    if 'recorded_audio' not in st.session_state:
        st.session_state.recorded_audio = None
    if 'api_response' not in st.session_state:
        st.session_state.api_response = None
    if 'admin_options' not in st.session_state:
        st.session_state.admin_options = None
    if 'new_user_name' not in st.session_state:
        st.session_state.new_user_name = ""
    if 'new_user_role' not in st.session_state:
        st.session_state.new_user_role = ""
    if 'new_user_audio' not in st.session_state:
        st.session_state.new_user_audio = None
    if 'delete_user_id' not in st.session_state:
        st.session_state.delete_user_id = ""
    if 'action_response' not in st.session_state:
        st.session_state.action_response = None

    # Render the audio input widget on the main page
    st.audio_input(
        label="how can I help you?",
        key="audio_input",
        help=None,
        on_change=None,
        args=None,
        kwargs=None,
        disabled=False,
        label_visibility="visible"
    )

    # Update recorded_audio in session state when new audio is provided
    if st.session_state.audio_input:
        st.session_state.recorded_audio = st.session_state.audio_input
    
    if st.button('submit') and st.session_state.recorded_audio:
        files = {"file": ("recording.wav", st.session_state.recorded_audio, "audio/wav")}
        response = requests.post("http://127.0.0.1:8000/api/v1/speech/upload_audio", files=files)

        if response.status_code == 200:
            st.session_state.api_response = response.json()
        else:
            st.error(f"Error: {response.text}")

    # Display API response if available
    if st.session_state.api_response:
        data = st.session_state.api_response
        st.markdown(
            f"<p style='font-size: 14px;'>transcribed_text: {data['transcribed_text']['text']}</p>",
            unsafe_allow_html=True
        )
        if data["verification"]["verified"]:
            st.markdown(
                f"<p style='font-size: 14px;'>speaker name: {data['verification']['speaker_name']}</p>",
                unsafe_allow_html=True
            )
            st.markdown(
                f"<p style='font-size: 14px;'>speaker role: {data['verification']['speaker_role']}</p>",
                unsafe_allow_html=True
            )
            st.markdown(
                f"<p style='font-size: 14px;'>confidence score: {data['verification']['similarity_score']}%</p>",
                unsafe_allow_html=True
            )
            pages_path="dashboards"
            if st.button("Display Dashboard"):
                st.switch_page(f"pages/{data['verification']['speaker_role']}.py") 

           

           
                     # st.switch_page("page1") # Switches to page1.py
          
            print(data["verification"]['final_response'])
            if data["verification"]['final_response']:
                tables_data=process_final_response(data["verification"]['final_response'])
               
                for table in tables_data:
                    st.table(table)
                
        else:
            st.markdown(
                f"<p style='font-size: 14px;'>Un-Verified user to reply!</p>",
                unsafe_allow_html=True
            )

    # Sidebar content
    with st.sidebar:
        add_selectbox = st.selectbox(
            "**Provide Services :**",
            ("Proved Answers", "Failture Prediction", "Dashboard Analysis")
        )

        # Admin-only radio button and add/delete logic
        if st.session_state.api_response and st.session_state.api_response["verification"]["verified"] and st.session_state.api_response['verification']['speaker_role'] == 'admin':
            st.session_state.admin_options = st.radio(
                "You have access to add or delete user!",
                ["Add", "Delete"],
                index=None,
                key="genre_radio"
            )
            if st.session_state.admin_options == "Add":
                st.session_state.new_user_name = st.text_input("New User Name", value=st.session_state.new_user_name, key="new_user_name_input")
                st.session_state.new_user_role = st.text_input("New User Role", value=st.session_state.new_user_role, key="new_user_role_input")
                st.audio_input(
                    label="Record voice for new user",
                    key="new_user_audio_input",
                    help=None,
                    on_change=None,
                    args=None,
                    kwargs=None,
                    disabled=False,
                    label_visibility="visible"
                )
                if st.session_state.new_user_audio_input:
                    st.session_state.new_user_audio = st.session_state.new_user_audio_input
                if st.session_state.new_user_audio:
                    st.write("Voice recorded for new user.")
            elif st.session_state.admin_options == "Delete":
                st.session_state.delete_user_id = st.text_input("User ID to Delete", value=st.session_state.delete_user_id, key="delete_user_id_input")

            # Submit button for both Add and Delete
            if st.button("Submit Action"):
                if st.session_state.admin_options == "Add":
                    if st.session_state.new_user_name and st.session_state.new_user_role and st.session_state.new_user_audio:
                      
                        # st.write(st.session_state.new_user_audio)
                        files = {"file": ("new_user.wav", st.session_state.new_user_audio, "audio/wav")}
                        # data = {"name": st.session_state.new_user_name, "role": st.session_state.new_user_role}
                        url = f"http://127.0.0.1:8000/api/v1/users/add_user?name={st.session_state.new_user_name}&role={st.session_state.new_user_role}"
                        response = requests.post(url, files=files)  # Send file as multipart/form-data, name and role as query params
                        # response = requests.post("http://127.0.0.1:8000/api/v1/users/add_user", files=files, data=data)
                        if response.status_code == 200:
                            st.session_state.action_response = response.json()
                            st.success("User added successfully!")
                            # Clear fields after success
                            st.session_state.new_user_name = ""
                            st.session_state.new_user_role = ""
                            st.session_state.new_user_audio = None
                        else:
                            st.error(f"Error adding user: {response.text}")
                    else:
                        st.warning("Please fill all fields and record voice for the new user.")
                elif st.session_state.admin_options == "Delete":
                        
                        if st.session_state.delete_user_id and st.session_state.delete_user_id.strip():
                            url = f"http://127.0.0.1:8000/api/v1/users/delete_user?user_id={st.session_state.delete_user_id}"
                            response = requests.post(url)  # No payload needed for delete
                            if response.status_code == 200:
                                st.session_state.action_response = response.json()
                                st.success("User deleted successfully!")
                                st.session_state.delete_user_id = ""
                            else:
                                st.error(f"Error deleting user: {response.text}")
                        else:
                            st.warning("Please enter a valid User ID to delete.")
                       

if __name__ == "__main__":
    main()
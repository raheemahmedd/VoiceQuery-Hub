

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
            
            machine_df=pd.DataFrame(item,index=[0])
            tables_data.append(machine_df)
            

    return tables_data


if __name__ =='__main__':
    
    final_response = [{'Machine_ID': '1', 'Machine_Type': '17', 'Installation_Year': 2032, 'Operational_Hours': 74966.0, 'Temperature_C': 58.32, 'Vibration_mms': 14.99, 'Sound_dB': 77.04, 'Oil_Level_pct': 100.0, 'Coolant_Level_pct': 62.13, 'Power_Consumption_kW': 154.61, 'Last_Maintenance_Days_Ago': 136, 'Maintenance_History_Count': 5, 'Failure_History_Count': 2, 'AI_Supervision': True, 'Error_Codes_Last_30_Days': 4, 'Remaining_Useful_Life_days': 147, 'Failure_Within_7_Days': False, 'Laser_Intensity': 74.9955133280549, 'Hydraulic_Pressure_bar': 119.91751351351351, 'Coolant_Flow_L_min': 
40.92, 'Heat_Index': 499.7609662936258, 'AI_Override_Events': 2, 'created_at': '2025-01-01T00:01:00', 'overall_llm_opinion_response': 'OK'}, {'classifcation prediction': 'False', 'regression prediction': 871.832763671875}]
    data=process_final_response(final_response)
    print(data[1])
    
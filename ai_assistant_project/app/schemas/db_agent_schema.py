from pydantic import BaseModel ,Field
from typing import Optional
from datetime import datetime
from typing import Literal

class MachineData(BaseModel):
    """Always use this tool to structure your response to the user.
    the keys should be all have the same with sql_db_query values.
    """
    Machine_ID: int
    Machine_Type: int
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
    overall_llm_opinion_response:str =Field(description="10 words maximum that describe the state of machine now based on another fields data.")


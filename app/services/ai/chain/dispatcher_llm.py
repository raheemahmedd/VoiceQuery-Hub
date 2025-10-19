import joblib
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from ....core.config import GEMINI_API_KEY
from langchain_core.prompts import PromptTemplate
from ..graph.db_agent import llm_initialization as db_agent_initialization
from ..graph.db_agent import *
from ..graph.db_agent import llm_run as db_agent_run
import json
import os
import pandas as pd
from ....schemas.speech_schema import SpeechResponse
from ....db.users import update_user_query,add_user_query
def load_prompt(file_name="dispatcher.txt") -> str:
    """Load a prompt text from the prompts folder"""
  
    path=r"E:\projects-in-army\1\Voice-Enabled Agentic Predictive Maintenance with Biometric Alerts\ai_assistant_project\app\services\ai"
 
    file_path = os.path.join(path,"prompts",file_name )
    
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()
    

@tool
def prediction(user_question):
        """if the user query is prediction"""
        print("user query classified as : prediction! ")
        llm,prompt=db_agent_initialization(query_type="prediction")
        
        agent_executor=SQLDatabaseToolkit_initialization(llm,prompt)
        response=db_agent_run(user_question,agent_executor)
        print("⚠️ The DB query is ⚠️")
        
        query = response['messages'][1].tool_calls[0]['args']['query']
        print(query)

      
        # Get raw SQL result
        sql_result = response['messages'][2].content
        print(sql_result)

        
        # # print(response)
        # print(response['messages'][1]['tool_calls'][0]['args']['query']
# )
        machine_data=response['structured_response']
        df = pd.DataFrame([machine_data.model_dump()]) # Use data.dict() for Pydantic v1
        
        # Define the columns to drop
        columns_to_drop = ['Failure_Within_7_Days', 'created_at','overall_llm_opinion_response']
        X_pred=df.drop(columns=columns_to_drop)
        
        ## save df sample ############
        df.to_csv("sample-data.csv",encoding='utf-8-sig')      
    
        loaded_dt = joblib.load(r"E:\projects-in-army\1\Voice-Enabled Agentic Predictive Maintenance with Biometric Alerts\ai_assistant_project\app\services\ai\ml-models\decision_tree_model.pkl")
        y_pred_dt = loaded_dt.predict([X_pred.iloc[0]])
        print("classifaction model finished predicting!")
        
        columns_to_drop = ['Remaining_Useful_Life_days', 'created_at','overall_llm_opinion_response']
        X_pred=df.drop(columns=columns_to_drop)
        
       
        # # Later, load the model
        loaded_xgb = joblib.load(r"E:\projects-in-army\1\Voice-Enabled Agentic Predictive Maintenance with Biometric Alerts\ai_assistant_project\app\services\ai\ml-models\xgb_regressor_model.pkl")
        y_pred_xgb = loaded_xgb.predict([X_pred.iloc[0]])
        print("regression model finished predicting!")
       
        return {"classifcation prediction":str(y_pred_dt[0]),"regression prediction":float(y_pred_xgb[0])}
@tool
def query(user_question):
        """if the user query is query"""
        print("user query classified as : query! ")
                
        llm,prompt=db_agent_initialization(query_type="query")
        # print(llm)
        agent_executor=SQLDatabaseToolkit_initialization(llm,prompt)
        response=db_agent_run(user_question,agent_executor)
        
        return response['structured_response']



def llm_initialization():
    
    llm = ChatGoogleGenerativeAI(temperature=0,model="gemini-2.0-flash", api_key=GEMINI_API_KEY)
    
    # Define the prompt template
    query_prompt =load_prompt("dispatcher.txt")
    prompt_template = PromptTemplate.from_template(query_prompt
    )
    # Bind the tools to the LLM
    llm_with_tools = llm.bind_tools([ query, prediction])
    return llm_with_tools, prompt_template

def llm_run(llm_with_tools, prompt_template, user_query,user_id):
    
    formatted_prompt = prompt_template.format(input=user_query)
    llm_response = llm_with_tools.invoke(formatted_prompt)
    
    tool_results=[]
    tool_names=[]

     # Handle tool calls if present
    if llm_response.tool_calls:
        
        for tool_call in llm_response.tool_calls:
            add_user_query(user_id,tool_call['name'],user_query.text)
            
                    

            # return f"The result is {result}"
            if tool_call['name'] == 'prediction':
                    tool_names.append(tool_call['name'])
                    tool_result = prediction.invoke(tool_call['args'])
                    update_user_query(user_id,float(tool_result["regression prediction"]),str(tool_result['classifcation prediction']))
                    tool_results.append(tool_result)

            elif tool_call['name'] == 'query':
                    tool_names.append(tool_call['name'])
                    tool_result = query.invoke(tool_call['args'])
                    
                    update_user_query(user_id,llm_response=str(tool_result))
                    tool_results.append(tool_result)

           
       
                
    return tool_results ,llm_response,tool_names
    
   

if __name__ =='__main__':
    
    llm_with_tools,prompt_template=llm_initialization()
    user_query=SpeechResponse(text="ايه حاله مكنه 2  تتوقع مكنه 15 فيها عطل")
    # user_query=SpeechResponse(text='إيه حالة الماكينة دلوقتي؟')
    tool_result,llm_response,_=llm_run(llm_with_tools,prompt_template,user_query,19)
    
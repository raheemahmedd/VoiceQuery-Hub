from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.utilities import SQLDatabase
from ....core.config import host, database, user, password, port,GEMINI_API_KEY
from langchain_community.agent_toolkits import SQLDatabaseToolkit
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langgraph.prebuilt import create_react_agent
from ....schemas.db_agent_schema import MachineData


def load_prompt(file_name: str) -> str:
    """Load a prompt text from the prompts folder"""
    
    path=r"E:\projects-in-army\1\Voice-Enabled Agentic Predictive Maintenance with Biometric Alerts\ai_assistant_project\app\services\ai"
  
    file_path = os.path.join(path,"prompts",file_name )
    
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def llm_initialization(query_type=None):

    # Initialize the model
    llm = ChatGoogleGenerativeAI(temperature=0,model="gemini-2.0-flash", api_key='AIzaSyAeaNwAmo1Dp6utQpZQKWOys2TOI-U_75Y')
    
    # Define the prompt template
    query_prompt =load_prompt("db_agent.txt")
    prompt_template = PromptTemplate.from_template(query_prompt
    ).format(
    dialect="postgresql",
    top_k=1,query_type=query_type)
   
    return llm, prompt_template

def SQLDatabaseToolkit_initialization(llm,system_message):


    # Database connection details
    DB_HOST = host
    DB_NAME = database
    DB_USER = user
    DB_PASSWORD = password
    DB_PORT = port

    # Create PostgreSQL URI
    postgres_uri = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

    # Initialize SQLDatabase with PostgreSQL
    db = SQLDatabase.from_uri(postgres_uri)

    # Test the connection by listing tables
    print("Tables in the database:", db.get_usable_table_names())
    
    toolkit = SQLDatabaseToolkit(db=db, llm=llm)

    tools = toolkit.get_tools()

    agent_executor = create_react_agent(llm, tools, prompt=system_message,response_format=MachineData)
    return agent_executor

def llm_run(question,agent_executor):

    result=agent_executor.invoke(
        {"messages": [{"role": "user", "content": question}]})
    return result

if __name__=="__main__":

    llm,prompt=llm_initialization()
    # print(llm)
    agent_executor=SQLDatabaseToolkit_initialization(llm,prompt)
    response=llm_run("ايه حالة machine id 0",agent_executor)
    print(response['structured_response'])
    
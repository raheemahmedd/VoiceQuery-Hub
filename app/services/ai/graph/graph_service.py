from typing import Dict , TypedDict
# from ...speech_service import SpeechService
from langgraph.graph import StateGraph,START, END
from ..chain.dispatcher_llm import *
## create an agentstate which is the shared data structure the keeps track of inf. as my app runs
class AgentState(TypedDict):
    audio_path:str
    speach_service:object
    speaker_verfication_service:object
    verified: bool
    transcribed_text:str
    user_id: int
    llm_response: any
    tool_result:any
    query_type:any

def speaker_verfication_node(state:AgentState)->AgentState:


        transcribed_text=state["speach_service"].transcribe(audio_path=state["audio_path"])
       
        print(transcribed_text)
        state["transcribed_text"]=transcribed_text
        state["speaker_verfication_service"].audio_resample()
        verified,user_id=state["speaker_verfication_service"].verfication_similarity()
        state["verified"]=verified
        state["user_id"]=user_id
        return state


def continue_node(state:AgentState) -> AgentState:
    """This node will select the next node of the graph"""

    if state["verified"] == True:
        ## return edge name
        return "working"
    
    else:
        ## return edge name
        return END


def dispatcher_node(state:AgentState)->AgentState:

        
        llm_with_tools,prompt_template=llm_initialization()
        user_query=state["transcribed_text"]
        tool_result,llm_response,query_type=llm_run(llm_with_tools,prompt_template,user_query,state['user_id'])
        
        state["llm_response"]=llm_response
        state["tool_result"]=tool_result
        state["query_type"]=query_type

        return state

def build_graph(AgentState):
    graph=StateGraph(AgentState)
    ## construct nodes
    graph.add_node("verfication",speaker_verfication_node)
    graph.add_node("continue",lambda state:state)
    graph.add_node("dispatcher",dispatcher_node)
    
   
    ## construct edges
    graph.add_edge(START,"verfication")
    graph.add_edge("verfication", "continue")

    graph.add_conditional_edges(
        'continue',
        continue_node,
        {
            ## Edge : Node
            "working": "dispatcher",  # if verified → working
            END:END,
        }

    )
    
    app = graph.compile()

    return app

def save_graph_img(app):
        png_bytes = app.get_graph().draw_mermaid_png()
        with open(r"ai_assistant_project\app\services\ai\graph\my_graph.png", "wb") as f:
            f.write(png_bytes)



if __name__ =='__main__':
     print("graph starting..")
     app=build_graph(AgentState)
     save_graph_img(app)
    #  initial_state = AgentState(command = "إيه حالة الماكينة دلوقتي", perform="")
    #  result=app.invoke(initial_state)
    #  print(result)

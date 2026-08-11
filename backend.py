import os
from dotenv import load_dotenv
load_dotenv()

from typing import TypedDict,Annotated
import operator
import uuid

import psycopg #help to connect python with postgres database
from psycopg.rows import dict_row # help to convert the result of a query into a dictionary

from langgraph.graph import StateGraph,END,START
from langgraph.checkpoint.postgres import PostgresSaver #help to save the state of the graph into a postgres database

from langchain_core.messages import AnyMessage,HumanMessage,AIMessage,SystemMessage

from langchain_groq import ChatGroq
from tools.tavily_tool import tavily_search
from tools.flight_tool import search_flights



def get_database_url():
    database_url=os.getenv("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL environment variable is not set")
    if "sslmode" not in database_url:
        separator = '&' if '?' in database_url else '?'
        database_url += f"{separator}sslmode=require"
    return database_url


llm=ChatGroq(model="llama-3.1-8b-instant",api_key=os.getenv("GROQ_API_KEY"))

class TravelState(TypedDict):
    messages:Annotated[list[AnyMessage],operator.add]
    user_query:str
    flight_result:str
    hotel_result:str
    itinerary:str
    llm_calls:int

def flight_agent(state:TravelState):
    query=state['user_query']
    result=search_flights(query)

    return {
        "flight_result":result,
        "messages":[
            AIMessage(content="flight result fetched")
        ],
        "llm_calls": state.get("llm_calls",0)+1
    }

def hotel_agent(state:TravelState):
    query=f"best hotel for {state['user_query']}"
    result=tavily_search(query)

    return {
        "hotel_result":result,
        "messages":[
            AIMessage(content="hotel result fetched")
        ],
        "llm_calls": state.get("llm_calls",0)+1
    }

def itinerary_agent(state:TravelState):
    prompt=f"""create a complete itinerary for the trip 

user_query:{state['user_query']}

hotel_results:{state['hotel_result']}

flight_results:{state['flight_result']}

make the itineray practical, budget friendly and easy to follow

    """
    result=llm.invoke([
        SystemMessage(content="You are an expert Travel Agent"),
        HumanMessage(content=prompt)
    ])

    return {
        "itinerary":result.content,
        "messages":[result],
        "llm_calls": state.get("llm_calls",0)+1
    
    }

def summary_agent(state: TravelState):
    prompt = f"""
Create a final trip summary for the user based on all the details gathered so far.

user_query: {state['user_query']}

flight_results: {state['flight_result']}

hotel_results: {state['hotel_result']}

itinerary: {state['itinerary']}

Structure your response with these exact sections:
1. Trip Summary
2. Flight Information
3. Hotel Suggestions
4. Day-by-Day Itinerary
5. Estimated Budget
6. Final Recommendations

Important:
- Be clear and practical.
- Mention that live flight API may not provide ticket prices if pricing is unavailable.
- Keep the response useful for real travel planning.
"""

    result = llm.invoke([
        SystemMessage(content="You are an expert Travel Summary Agent"),
        HumanMessage(content=prompt)
    ])

    return {  
        "messages": [result],
        "llm_calls": state.get("llm_calls", 0) + 1
    }


graph=StateGraph(TravelState)

graph.add_node("flight_agent",flight_agent)
graph.add_node("hotel_agent",hotel_agent)
graph.add_node("itinerary_agent",itinerary_agent)
graph.add_node("summary_agent",summary_agent)

graph.add_edge(START,"flight_agent")
graph.add_edge("flight_agent","hotel_agent")
graph.add_edge("hotel_agent","itinerary_agent")
graph.add_edge("itinerary_agent","summary_agent")
graph.add_edge("summary_agent",END)

DATABASE_URL=get_database_url()
cunn=psycopg.connect(
    DATABASE_URL,
    autocommit=True,
    row_factory=dict_row
)

checkpointer=PostgresSaver(cunn)
checkpointer.setup()

travel_graph=graph.compile(checkpointer=checkpointer)



# fast api frunction


def run_travel_agent(user_query:str,thread_id:str|None=None):
    if not thread_id:
        thread_id=f"user{uuid.uuid4()}.hex"

    config={
        "configurable":{
            "thread_id":thread_id

        }
    }

    
    
    result=travel_graph.invoke(
        {
       
            "messages":[
                HumanMessage(content=user_query)
            ],
            "user_query":user_query,
            "flight_result":"",
            "hotel_result":"",
            "itinerary":"",
            "llm_calls":0
        },
        config=config
    )
    

    final_result=result['messages'][-1].content

    return {
        "thread_id":thread_id,
        "final_result":final_result,
        "flight_result":result.get('flight_result', ''),
        "hotel_result":result.get('hotel_result', ''),
        "itinerary":result.get('itinerary', ''),
        "llm_calls":result['llm_calls']

    }
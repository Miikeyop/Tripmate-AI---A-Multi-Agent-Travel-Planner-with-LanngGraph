import os
from dotenv import load_dotenv
load_dotenv()

from typing import TypedDict,Annotated
import operator
import uuid
import asyncio

import psycopg #help to connect python with postgres database
from psycopg.rows import dict_row # help to convert the result of a query into a dictionary

from langgraph.graph import StateGraph,END,START
from langgraph.checkpoint.postgres import PostgresSaver #help to save the state of the graph into a postgres database

from langchain_core.messages import AnyMessage,HumanMessage,AIMessage,SystemMessage

from langchain_groq import ChatGroq
# from tools.tavily_tool import tavily_search
from mcp_client import run_tavily_search,aviation_mcp_call,weather_mcp_call

#from tools.flight_tool import search_flights



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
    weather_result: str
    itinerary:str
    llm_calls:int

# manual flight agent

#def flight_agent(state:TravelState):
#    query=state['user_query']
#    result=search_flights(query)

 #   return {
  #      "flight_result":result,
   #     "messages":[
    #        AIMessage(content="flight result fetched")
     #   ],
      #  "llm_calls": state.get("llm_calls",0)+1
    #}
FLIGHT_AGENT_PROMPT = """
User Query:
{query}

Airport Information:
{airport_data}

Airline Information:
{airline_data}

Generate:

1. Likely departure airport
2. Likely arrival airport
3. Airlines serving this route
4. Typical flight duration
5. Estimated airfare range
6. Peak season pricing warning
7. Booking advice

Return concise travel guidance.
"""
# mcp server flight agent
def flight_agent(state: TravelState):

    query = state["user_query"]

    airports = asyncio.run(aviation_mcp_call("list_airports"))
    airlines = asyncio.run(aviation_mcp_call("list_airlines"))

    prompt = FLIGHT_AGENT_PROMPT.format(
        query=query,
        airport_data=str(airports)[:3000],
        airline_data=str(airlines)[:3000]
    )

    response =  llm.invoke([
        SystemMessage(
            content="You are an expert travel flight planner."
        ),
        HumanMessage(content=prompt)
    ])

    return {
        "flight_result": response.content,
        "messages": [
            AIMessage(content=response.content)
        ],
        "llm_calls": state.get("llm_calls", 0) + 1
    }

# using mcp server as well as manually but using mcp server currently
def hotel_agent(state:TravelState):
    query=f"best hotel for {state['user_query']}"
   # result=tavily_search(query)

    result=asyncio.run(run_tavily_search(query))

    return {
        "hotel_result":result,
        "messages":[
            AIMessage(content="hotel result fetched")
        ],
        "llm_calls": state.get("llm_calls",0)+1
    }
def weather_agent(state: TravelState):

    query = state["user_query"]

    # Get weather information from MCP
    weather_data = asyncio.run(
        weather_mcp_call(
            "get_hourly_weather",
            {
                "location": query
            }
        )
    )

    weather_prompt = f"""
You are an expert travel weather assistant.

User travel query:
{query}

Weather information retrieved from the weather service:
{weather_data}

Create a clear weather section for the travel plan.

Use exactly this style:

## 🌤️ Weather Information

Start with a short paragraph describing the overall weather
conditions at the destination.

Then provide the forecast information using bullet points.

For example:

## 🌤️ Weather Information

Japan's weather can be quite varied. Currently, the temperature
is around XX°C with [condition] and humidity of XX%.

The forecast includes:

- [Weather condition] with a temperature of XX°C
- [Weather condition] with a temperature of XX°C
- [Weather condition] with a temperature of XX°C

Then provide a short practical travel recommendation such as
clothing, hydration, umbrella/rain protection, or planning
outdoor activities, but ONLY when supported by the weather data.

Important rules:

1. Use ONLY the weather information provided.
2. Do not invent temperatures or weather conditions.
3. Do not invent humidity, wind, rainfall, or forecasts.
4. If some information is unavailable, simply don't mention it.
5. Do not mention MCP, APIs, tools, or internal implementation.
6. Keep the weather section informative but not unnecessarily long.
7. Use bullet points for forecast information.
8. Return ONLY the weather section.
"""

    response = llm.invoke([
        SystemMessage(
            content="You are an expert travel weather assistant."
        ),
        HumanMessage(content=weather_prompt)
    ])

    return {
        "weather_result": response.content,
        "messages": [
            AIMessage(content=response.content)
        ],
        "llm_calls": state.get("llm_calls", 0) + 1
    }

def itinerary_agent(state: TravelState):

    prompt = f"""
You are an expert travel planner.

Create a complete and practical day-by-day itinerary based on
the information below.

USER QUERY:
{state["user_query"]}

FLIGHT INFORMATION:
{state["flight_result"]}

HOTEL INFORMATION:
{state["hotel_result"]}

WEATHER INFORMATION:
{state["weather_result"]}

Create a practical, budget-friendly and easy-to-follow itinerary.

Requirements:

1. Create a day-by-day itinerary.
2. Consider the available flight information.
3. Consider the selected/recommended hotel information.
4. Consider the weather conditions when planning outdoor activities.
5. Avoid scheduling outdoor activities during unfavorable weather
   when the weather information clearly indicates a problem.
6. Group nearby attractions together to reduce unnecessary travel.
7. Mention the city/location for each day.
8. Include important attractions and activities.
9. Keep the itinerary realistic rather than overcrowded.
10. Include arrival and departure considerations.
11. Do not invent flight details that are not provided.
12. Do not invent weather information.
13. Do not mention internal agents, MCP, APIs, or LangGraph.

Format the result like this:

## 📅 Day-by-Day Itinerary

- **Day 1: [Location]** - ...
- **Day 2: [Location]** - ...
- **Day 3: [Location]** - ...
- **Day 4: [Location]** - ...

Make the itinerary easy to read and follow.
"""

    result = llm.invoke([
        SystemMessage(
            content="You are an expert travel itinerary planner."
        ),
        HumanMessage(content=prompt)
    ])

    return {
        "itinerary": result.content,
        "messages": [
            result
        ],
        "llm_calls": state.get("llm_calls", 0) + 1
    }

def summary_agent(state: TravelState):

    summary_prompt = f"""
You are the final travel assistant.

Create ONE polished and detailed travel plan for the user.

USER QUERY:
{state["user_query"]}

================ FLIGHT INFORMATION ================
{state.get("flight_result", "No flight information available.")}

================ HOTEL INFORMATION =================
{state.get("hotel_result", "No hotel information available.")}

================ WEATHER INFORMATION ===============
{state.get("weather_result", "No weather information available.")}

================ ITINERARY ==========================
{state.get("itinerary", "No itinerary information available.")}


IMPORTANT:
The final response must begin with a short "Trip Summary".

The Trip Summary should give the user a quick overview of the
entire trip before showing the detailed information.

Use the following structure:

## 📝 Trip Summary

Write ONE short paragraph summarizing:

- destination
- trip duration if available
- major cities/places covered
- overall travel experience
- important highlights

Do NOT simply repeat the complete itinerary here.
Keep the summary concise.

---

## ✈️ Flights

Present the useful flight information clearly.

Include when available:

- Departure airport
- Arrival airport
- Airlines
- Typical flight duration
- Estimated airfare
- Peak season pricing
- Booking advice

Do not invent information.

---

## 🏨 Hotels

Present the useful hotel recommendations clearly.

Include:

- Hotel/property name
- Location
- Price information if available
- Important facilities/features
- Why it may be suitable

Do not invent hotel information.

---

## 🌤️ Weather Information

Present the weather information clearly.

Include:

- Current/general weather
- Temperature
- Weather conditions
- Forecast
- Rain/precipitation
- Humidity
- Wind
- Practical weather advice

Only include information that exists in the weather result.

---

## 📅 Day-by-Day Itinerary

Use the itinerary generated by the itinerary planner.

Present each day clearly:

- Day 1
- Day 2
- Day 3
- etc.

Do not unnecessarily rewrite or duplicate the itinerary.

---

## 📋 Overall Travel Plan

End with a short practical conclusion.

Mention:

- Best way to organize the trip
- Important things to keep in mind
- Weather considerations
- Flight/hotel considerations
- General travel advice

IMPORTANT RULES:

1. Start with "## 📝 Trip Summary".
2. Include only sections for which useful information exists.
3. Use the itinerary result instead of activity_result.
4. Do NOT include restaurant or activity sections because there are
   no separate restaurant/activity agents.
5. Do not mention internal agent names.
6. Do not mention LangGraph, MCP, APIs, prompts, or state.
7. Do not invent information.
8. Do not repeat the same information unnecessarily.
9. Keep the Trip Summary short.
10. Keep the detailed sections informative.
11. Use headings and bullet points for readability.
12. Preserve important factual information from the agents.
13. The final response should feel like ONE complete professional
    travel plan rather than separate agent responses.

Return ONLY the final travel plan.
"""

    response = llm.invoke([
        SystemMessage(
            content="You are an expert final travel planning assistant."
        ),
        HumanMessage(content=summary_prompt)
    ])

    return {
        "messages": [
            AIMessage(content=response.content)
        ],
        "llm_calls": state.get("llm_calls", 0) + 1
    }

graph=StateGraph(TravelState)

graph.add_node("flight_agent",flight_agent)
graph.add_node("hotel_agent",hotel_agent)
graph.add_node("weather_agent",weather_agent)
graph.add_node("itinerary_agent",itinerary_agent)
graph.add_node("summary_agent",summary_agent)

graph.add_edge(START,"flight_agent")
graph.add_edge("flight_agent","hotel_agent")
graph.add_edge("hotel_agent","weather_agent")
graph.add_edge("weather_agent","itinerary_agent")
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
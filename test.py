from tools.tavily_tool import tavily_search

from tools.flight_tool import search_flights
from backend import run_travel_agent

from rich import print
#res=tavily_search("best hostel in goa")

#print(res)


#res=search_flights("5 day trip to spain")



#print(res)


user_input=input("enter travel request:")

res=run_travel_agent(user_input)

print("-----------result------------------------")

print(res)
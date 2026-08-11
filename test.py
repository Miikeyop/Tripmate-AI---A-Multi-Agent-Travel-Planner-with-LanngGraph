from tools.tavily_tool import tavily_search

from tools.flight_tool import search_flights
#res=tavily_search("best hostel in goa")

#print(res)


res=search_flights("5 day trip to spain")

print(res)
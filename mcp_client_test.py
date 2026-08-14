from langchain_mcp_adapters.client import MultiServerMCPClient
import asyncio
import os
from dotenv import load_dotenv
load_dotenv()

import certifi



os.environ["SSL_CERT_FILE"] = certifi.where()
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()


TAVILY_API_KEY=os.getenv("TAVILY_API_KEY")
AVIATIONSTACK_API_KEY=os.getenv("AVIATIONSTACK_API_KEY")

client=MultiServerMCPClient(
    {    # remote server
        "tavily":{
            "transport":"streamable_http",
            "url":f"https://mcp.tavily.com/mcp/?tavilyApiKey={TAVILY_API_KEY}"
        },
    })

async def get_tools():
    tools=await client.get_tools()

    for tool in tools:
        print(tool.name)

TAVILY_SEARCH_TOOL= None

async def  get_tavily_seaarch_tool():
    global TAVILY_SEARCH_TOOL
    if TAVILY_SEARCH_TOOL is None:
        tools=await client.get_tools()
        for tool in tools:
            if tool.name=="tavily_search":
                TAVILY_SEARCH_TOOL=tool
                break
    return TAVILY_SEARCH_TOOL

async def run_tavily_search(query):
    await get_tavily_seaarch_tool()

    result= await TAVILY_SEARCH_TOOL.ainvoke(
        {
            "query":query
        }
    )
    return result


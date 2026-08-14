from langchain_mcp_adapters.client import MultiServerMCPClient
import asyncio
import os
from dotenv import load_dotenv
import certifi

load_dotenv()

os.environ["SSL_CERT_FILE"] = certifi.where()
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
AVIATIONSTACK_API_KEY = os.getenv("AVIATIONSTACK_API_KEY")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")


client = MultiServerMCPClient(
    {
        # Remote MCP server
        "tavily": {
            "transport": "streamable_http",
            "url": f"https://mcp.tavily.com/mcp/?tavilyApiKey={TAVILY_API_KEY}"
        },

        # Local MCP server - AviationStack
        "aviationstack": {
            "transport": "stdio",
            "command": "uvx",
            "args": [
                "--python", "3.13",
                "--with", "mcp==1.12.4",
                "--with", "aviationstack-mcp",
                "aviationstack-mcp"
            ],
            "env": {
                "AVIATION_STACK_API_KEY": AVIATIONSTACK_API_KEY
            }
        },

        # Local MCP server - Weather
        "weather": {
            "transport": "stdio",
            "command": "uvx",
            "args": [
                "--from",
                "git+https://github.com/adhikasp/mcp-weather.git",
                "mcp-weather"
            ],
            "env": {
                "ACCUWEATHER_API_KEY": OPENWEATHER_API_KEY
            }
        }
    }
)


async def get_tools():

    tools = await client.get_tools()

    for tool in tools:
        print(tool.name)


# Store selected tools
TAVILY_SEARCH_TOOL = None
aviation_tools = []
weather_tools = []


async def initialize_mcp():

    global TAVILY_SEARCH_TOOL
    global aviation_tools
    global weather_tools

    if (
        TAVILY_SEARCH_TOOL is not None
        and aviation_tools
        and weather_tools
    ):
        return

    tools = await client.get_tools()

    print("Available MCP tools:")

    for tool in tools:

        print(tool.name)

        # Tavily
        if tool.name == "tavily_search":
            TAVILY_SEARCH_TOOL = tool

        # AviationStack
        elif tool.name in ["list_airports", "list_airlines"]:
            aviation_tools.append(tool)

        # Weather
        elif tool.name == "get_hourly_weather":
            weather_tools.append(tool)


async def run_tavily_search(query):

    await initialize_mcp()

    result = await TAVILY_SEARCH_TOOL.ainvoke(
        {
            "query": query
        }
    )

    return result


async def aviation_mcp_call(
    tool_name: str,
    tool_args: dict = None
):

    await initialize_mcp()

    tool = None

    for t in aviation_tools:

        if t.name == tool_name:
            tool = t
            break

    if tool is None:
        raise ValueError(
            f"Aviation tool '{tool_name}' not found"
        )

    result = await tool.ainvoke(
        tool_args or {}
    )

    return result


async def weather_mcp_call(
    tool_name: str,
    tool_args: dict = None
):

    await initialize_mcp()

    tool = None

    for t in weather_tools:

        if t.name == tool_name:
            tool = t
            break

    if tool is None:
        raise ValueError(
            f"Weather tool '{tool_name}' not found"
        )

    result = await tool.ainvoke(
        tool_args or {}
    )

    return result
from langchain_mcp_adapters.client import MultiServerMCPClient

import asyncio
import os
from dotenv import load_dotenv
import certifi


# --------------------------------------------------
# Load environment variables
# --------------------------------------------------

load_dotenv()

os.environ["SSL_CERT_FILE"] = certifi.where()
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()


TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
AVIATIONSTACK_API_KEY = os.getenv("AVIATIONSTACK_API_KEY")


# --------------------------------------------------
# MCP Client
# --------------------------------------------------

client = MultiServerMCPClient(
    {

        # ==========================================
        # 1. TAVILY MCP SERVER
        # ==========================================

        "tavily": {
            "transport": "streamable_http",
            "url": f"https://mcp.tavily.com/mcp/?tavilyApiKey={TAVILY_API_KEY}"
        },


        # ==========================================
        # 2. AVIATIONSTACK MCP SERVER
        # ==========================================

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


        # ==========================================
        # 3. WEATHER MCP SERVER
        # ==========================================

        "weather": {
            "transport": "stdio",

            "command": "npx",

            "args": [
                "-y",
                "@open-mcp/open-weather"
            ]
        }

    }
)


# --------------------------------------------------
# Store selected tools
# --------------------------------------------------

TAVILY_SEARCH_TOOL = None

aviation_tools = []

weather_tools = []


# --------------------------------------------------
# Initialize MCP
# --------------------------------------------------

async def initialize_mcp():

    global TAVILY_SEARCH_TOOL
    global aviation_tools
    global weather_tools


    # Already initialized
    if (
        TAVILY_SEARCH_TOOL is not None
        and aviation_tools
        and weather_tools
    ):
        return


    # Get tools from all MCP servers
    tools = await client.get_tools()


    print("\nAvailable MCP tools:\n")


    for tool in tools:

        print(tool.name)


        # ------------------------------------------
        # Tavily
        # ------------------------------------------

        if tool.name == "tavily_search":

            TAVILY_SEARCH_TOOL = tool


        # ------------------------------------------
        # AviationStack
        # ------------------------------------------

        elif tool.name in [
            "list_airports",
            "list_airlines"
        ]:

            aviation_tools.append(tool)


        # ------------------------------------------
        # Weather
        # ------------------------------------------

        elif tool.name == "getweatherdata":

            weather_tools.append(tool)


# --------------------------------------------------
# Tavily Search
# --------------------------------------------------

async def run_tavily_search(query):

    await initialize_mcp()


    if TAVILY_SEARCH_TOOL is None:

        raise ValueError(
            "Tavily search tool not found."
        )


    result = await TAVILY_SEARCH_TOOL.ainvoke(
        {
            "query": query
        }
    )


    return result


# --------------------------------------------------
# Aviation MCP Call
# --------------------------------------------------

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
            f"Aviation tool '{tool_name}' not found."
        )


    result = await tool.ainvoke(
        tool_args or {}
    )


    return result


# --------------------------------------------------
# Weather MCP Call
# --------------------------------------------------

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
            f"Weather tool '{tool_name}' not found."
        )


    result = await tool.ainvoke(
        tool_args or {}
    )


    return result


# --------------------------------------------------
# Test MCP Tools
# --------------------------------------------------

async def get_tools():

    tools = await client.get_tools()


    print("\n==============================")
    print("AVAILABLE MCP TOOLS")
    print("==============================\n")


    for tool in tools:

        print(f"Tool: {tool.name}")
        print(f"Description: {tool.description}")
        print(f"Schema: {tool.args_schema}")
        print()


# --------------------------------------------------
# Run directly
# --------------------------------------------------

if __name__ == "__main__":

    asyncio.run(get_tools())
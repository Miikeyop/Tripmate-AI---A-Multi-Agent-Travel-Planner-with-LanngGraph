
import asyncio
import os
import traceback

import certifi
from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient

# =====================================================
# ENVIRONMENT
# =====================================================

load_dotenv()

os.environ["SSL_CERT_FILE"] = certifi.where()
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")


# =====================================================
# MCP CLIENT
# AviationStack MCP removed because its connection
# closes during initialization.
# =====================================================

client = MultiServerMCPClient(
    {
        "tavily": {
            "transport": "streamable_http",
            "url": (
                "https://mcp.tavily.com/mcp/"
                f"?tavilyApiKey={TAVILY_API_KEY}"
            ),
        },

        "weather": {
            "transport": "stdio",
            "command": "npx",
            "args": [
                "-y",
                "@open-mcp/open-weather",
            ],
        },
    }
)


# =====================================================
# AVIATION REFERENCE DATA (FALLBACK)
# Static reference data; not live flight information.
# =====================================================

AIRPORTS = [
    {"city": "Delhi", "iata": "DEL",
     "airport": "Indira Gandhi International Airport"},
    {"city": "Mumbai", "iata": "BOM",
     "airport": "Chhatrapati Shivaji Maharaj International Airport"},
    {"city": "Bengaluru", "iata": "BLR",
     "airport": "Kempegowda International Airport"},
    {"city": "Dubai", "iata": "DXB",
     "airport": "Dubai International Airport"},
    {"city": "Tokyo", "iata": "HND",
     "airport": "Haneda Airport"},
    {"city": "Tokyo", "iata": "NRT",
     "airport": "Narita International Airport"},
    {"city": "Bangkok", "iata": "BKK",
     "airport": "Suvarnabhumi Airport"},
    {"city": "Singapore", "iata": "SIN",
     "airport": "Singapore Changi Airport"},
    {"city": "London", "iata": "LHR",
     "airport": "Heathrow Airport"},
    {"city": "Paris", "iata": "CDG",
     "airport": "Charles de Gaulle Airport"},
    {"city": "New York", "iata": "JFK",
     "airport": "John F. Kennedy International Airport"},
    {"city": "Doha", "iata": "DOH",
     "airport": "Hamad International Airport"},
]

AIRLINES = [
    "Air India",
    "IndiGo",
    "Emirates",
    "Qatar Airways",
    "Singapore Airlines",
    "Japan Airlines",
    "All Nippon Airways",
    "Thai Airways",
    "British Airways",
    "Lufthansa",
    "Air France",
    "Turkish Airlines",
]


# =====================================================
# MCP TOOL INITIALIZATION
# =====================================================

async def initialize_mcp(server_name=None):
    """
    Discover tools from a server independently.
    Avoid requiring unrelated MCP servers to initialize.
    """

    if server_name is not None:
        return await client.get_tools(
            server_name=server_name
        )

    all_tools = []

    for name in ["tavily", "weather"]:
        tools = await client.get_tools(
            server_name=name
        )
        all_tools.extend(tools)

    return all_tools


# =====================================================
# TAVILY SEARCH
# =====================================================

async def run_tavily_search(query):
    tools = await initialize_mcp("tavily")

    search_tool = next(
        (
            tool for tool in tools
            if tool.name == "tavily_search"
        ),
        None,
    )

    if search_tool is None:
        raise RuntimeError(
            "Tavily search tool not found."
        )

    return await search_tool.ainvoke(
        {"query": query}
    )


# =====================================================
# AVIATION FALLBACK
# Keeps the original backend.py function interface.
# =====================================================

async def aviation_mcp_call(
    tool_name: str,
    tool_args: dict = None,
):
    if tool_name == "list_airports":
        return {
            "source": "Static airport reference",
            "airports": AIRPORTS,
            "note": (
                "This is a limited reference list. "
                "It does not contain live availability."
            ),
        }

    if tool_name == "list_airlines":
        return {
            "source": "Static airline reference",
            "airlines": AIRLINES,
            "note": (
                "These are examples of major airlines. "
                "Routes, schedules and fares are not verified."
            ),
        }

    raise ValueError(
        f"Unsupported aviation tool: {tool_name}"
    )


# =====================================================
# WEATHER MCP
# =====================================================

async def weather_mcp_call(
    tool_name: str,
    tool_args: dict = None,
):
    tools = await initialize_mcp("weather")

    weather_tool = next(
        (
            tool for tool in tools
            if tool.name == tool_name
        ),
        None,
    )

    if weather_tool is None:
        raise ValueError(
            f"Weather tool '{tool_name}' not found."
        )

    return await weather_tool.ainvoke(
        tool_args or {}
    )


# =====================================================
# DIAGNOSTIC TESTS
# =====================================================

async def test_servers():
    print("\n========== MCP SERVER TEST ==========")

    for name in ["tavily", "weather"]:
        print(f"\nTesting {name}...", flush=True)

        try:
            tools = await asyncio.wait_for(
                initialize_mcp(name),
                timeout=60,
            )

            print(f"SUCCESS: {name}")

            for tool in tools:
                print(f" - {tool.name}")

        except Exception as error:
            print(f"FAILED: {name}")
            traceback.print_exception(error)

    print("\nTesting Aviation fallback...")

    try:
        airports = await aviation_mcp_call(
            "list_airports"
        )

        airlines = await aviation_mcp_call(
            "list_airlines"
        )

        print(
            "SUCCESS: Aviation reference data"
        )
        print(
            "Airports:",
            len(airports["airports"])
        )
        print(
            "Airlines:",
            len(airlines["airlines"])
        )

    except Exception as error:
        print("FAILED: Aviation fallback")
        traceback.print_exception(error)

    print("\n========== TEST FINISHED ==========")


async def get_tools():
    return await initialize_mcp()


# =====================================================
# MAIN
# =====================================================

if __name__ == "__main__":
    asyncio.run(test_servers())

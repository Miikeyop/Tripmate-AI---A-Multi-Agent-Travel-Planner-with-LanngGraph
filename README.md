# Tripmate-AI---A-Multi-Agent-Travel-Planner-with-LanngGraph# 


✈️ TripMate AI — Multi-Agent Travel Planner

> AI travel planner built with **LangGraph, MCP, Groq, FastAPI and PostgreSQL**.

## 🌍 Overview

TripMate converts a natural-language travel request into a structured plan using specialized agents for **flights, hotels, weather and itinerary generation**.

## ✨ Features

* 🤖 Multi-agent workflow with **LangGraph**
* 🔌 **MCP** integration for external travel tools
* 🛡️ Input and output **guardrails**
* ✈️ Flight information via AviationStack MCP
* 🏨 Hotel search via Tavily MCP
* 🌤️ Weather information via Weather MCP
* 📅 AI-generated day-by-day itinerary
* 🗄️ PostgreSQL-backed LangGraph checkpoints
* 🚀 FastAPI backend with web UI

## 🧠 Workflow

```text
User Query
    ↓
Input Guardrail
    ↓
Flight Agent → AviationStack MCP
    ↓
Hotel Agent → Tavily MCP
    ↓
Weather Agent → Weather MCP
    ↓
Itinerary Agent
    ↓
Summary Agent
    ↓
Output Guardrail
    ↓
Final Travel Plan
```

## 🔌 MCP Integrations

| MCP                   | Purpose                         |
| --------------------- | ------------------------------- |
| **Tavily MCP**        | Hotel/travel web search         |
| **AviationStack MCP** | Airport and airline information |
| **Weather MCP**       | Destination weather data        |

## 🔐 Guardrails

* **Input guardrail:** validates that requests are relevant and safe.
* **Output guardrail:** validates the generated travel response.
* **Fail-closed behavior:** failed validation is rejected.

## 🧩 LangGraph

The workflow uses a shared `TravelState` for user, flight, hotel, weather and itinerary data. Conditional routing handles the guardrails, while PostgreSQL checkpointing persists conversation state.

## 🤖 LLM

Uses **Groq `llama-3.1-8b-instant`** through `langchain-groq` for validation, travel planning, itinerary generation and summarization.

## ✈️ Travel Planning

Specialized agents combine flight, hotel and weather information to create a practical **day-by-day itinerary**. The final Summary Agent combines the results into one travel plan.

## 🌐 API

* `GET /` — web interface
* `POST /api/travel` — generate a travel plan
* `GET /health` — health check

## 🗂️ Structure

| File                   | Purpose                                   |
| ---------------------- | ----------------------------------------- |
| `app.py`               | FastAPI app and endpoints                 |
| `backend.py`           | LangGraph workflow, agents and guardrails |
| `mcp_client.py`        | MCP configuration and tools               |
| `templates/index.html` | Web UI                                    |
| `static/`              | Frontend assets                           |
| `requirements.txt`     | Dependencies                              |

## 🚀 Setup

```bash
git clone https://github.com/Miikeyop/Tripmate-AI---A-Multi-Agent-Travel-Planner-with-LanngGraph.git
cd Tripmate-AI---A-Multi-Agent-Travel-Planner-with-LanngGraph
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Create `.env`:

```env
GROQ_API_KEY=your_groq_api_key
TAVILY_API_KEY=your_tavily_api_key
AVIATIONSTACK_API_KEY=your_aviationstack_api_key
DATABASE_URL=your_postgresql_connection_string
```

Run:

```bash
python app.py
```

Open `http://127.0.0.1:8000`.

## 🛠️ Tech Stack

**Python · LangGraph · LangChain · MCP · Groq · FastAPI · PostgreSQL · Jinja2**

## 🧪 Testing

The repository includes `test.py` and `mcp_client_test.py` for application and MCP testing.

## 📌 Future Improvements

* Parallel execution of independent agents
* More travel APIs
* Real-time availability
* Budget and route optimization
* User preference memory
* Authentication
* Production monitoring

## 👨‍💻 Author

**Miikeyop** · [GitHub](https://github.com/Miikeyop)

**Built with Python, LangGraph, MCP, FastAPI, Groq and PostgreSQL.**

---

## ✨ Key Features

### 🤖 Multi-Agent Architecture

TripMate separates travel planning into specialized agents instead of relying on one large prompt.

| Agent                | Responsibility                                           |
| -------------------- | -------------------------------------------------------- |
| 🛡️ Input Guardrail  | Validates whether the request is relevant and safe       |
| ✈️ Flight Agent      | Provides airport, airline, duration and airfare guidance |
| 🏨 Hotel Agent       | Searches for relevant hotel information                  |
| 🌤️ Weather Agent    | Retrieves and summarizes destination weather             |
| 📅 Itinerary Agent   | Creates a practical day-by-day itinerary                 |
| 📝 Summary Agent     | Combines all results into one final travel plan          |
| 🛡️ Output Guardrail | Validates the generated response before returning it     |

---

## 🧠 Architecture

```text
                         ┌─────────────────────┐
                         │     User Query      │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │   Input Guardrail   │
                         └──────────┬──────────┘
                                    │
                           Accept / Reject
                              │         │
                         Accept         └──────────────► Rejection
                              │
                              ▼
                    ┌──────────────────────┐
                    │     Flight Agent     │
                    │    AviationStack     │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │      Hotel Agent     │
                    │       Tavily MCP     │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │     Weather Agent    │
                    │    Weather MCP       │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │   Itinerary Agent    │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │     Summary Agent    │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │   Output Guardrail   │
                    └──────────┬───────────┘
                               │
                         Approved / Rejected
                          │             │
                       Approved         └──────► Rejection
                          │
                          ▼
                  ┌─────────────────────┐
                  │   Final Travel Plan │
                  └─────────────────────┘
```

The workflow is implemented as a LangGraph `StateGraph` with conditional routing at the input and output guardrails.

---

## 🔐 Guardrail System

A major component of TripMate AI is its **two-stage guardrail architecture**.

### 1. Input Guardrail

Before the travel workflow begins, the user's request is checked for relevance and safety.

The system rejects requests that:

* Are unrelated to travel
* Request illegal activities
* Request harmful or dangerous activities
* Attempt to manipulate system instructions
* Attempt to reveal hidden prompts
* Request API keys, credentials or environment variables
* Attempt prompt injection
* Fall clearly outside the application's purpose

Valid travel requests are allowed to continue to the travel agents.

### 2. Output Guardrail

After the final travel plan has been generated, another guardrail validates the response.

It checks that the output:

* Is relevant to the travel request
* Does not contain dangerous or illegal instructions
* Does not expose system prompts
* Does not expose credentials or secrets
* Does not contain obvious prompt injection content
* Does not make clearly unsafe claims
* Does not falsely guarantee unavailable information

If validation fails, the generated response is rejected instead of being returned to the user.

### Fail-Closed Design

The guardrails are designed to **fail closed**. If the guardrail cannot properly validate a request or response, it rejects it rather than allowing potentially unsafe content to continue.

---

## 🔌 MCP Integration

TripMate uses the **Model Context Protocol (MCP)** to connect the application with external tools.

The MCP client manages three external MCP integrations:

### 🔎 Tavily MCP

Used for travel-related web search, particularly hotel information.

```text
TripMate
   │
   ▼
Tavily MCP
   │
   ▼
Search Results
   │
   ▼
Hotel Agent
```

### ✈️ AviationStack MCP

Used by the Flight Agent to access airport and airline information.

The project uses MCP tools including:

* `list_airports`
* `list_airlines`

### 🌤️ Weather MCP

Used by the Weather Agent to retrieve weather information for the destination.

The MCP client uses the `getweatherdata` tool for weather retrieval.

### MCP Architecture

```text
                  MCP Client
                      │
          ┌───────────┼───────────┐
          │           │           │
          ▼           ▼           ▼
       Tavily     AviationStack   Weather
         MCP          MCP           MCP
          │           │             │
          ▼           ▼             ▼
       Search      Airports       Weather
       Results     Airlines         Data
```

The project uses `MultiServerMCPClient` to initialize and discover tools from the configured MCP servers.

---

## 🧩 LangGraph Workflow

The application uses a shared `TravelState` to pass information between the different stages.

The state contains:

```text
messages
user_query
flight_result
hotel_result
weather_result
itinerary
llm_calls
guardrail_accept
guardrail_reason
```

The main workflow is:

```text
START
  │
  ▼
Input Guardrail
  │
  ├── Reject ──► Rejection ──► END
  │
  ▼
Flight Agent
  │
  ▼
Hotel Agent
  │
  ▼
Weather Agent
  │
  ▼
Itinerary Agent
  │
  ▼
Summary Agent
  │
  ▼
Output Guardrail
  │
  ├── Reject ──► Output Rejection ──► END
  │
  └── Approve ──► END
```

This workflow is compiled with a PostgreSQL checkpointer, allowing LangGraph state to be associated with a conversation thread.

---

## 🤖 LLM

TripMate uses **Groq's `llama-3.1-8b-instant` model** through `langchain-groq`.

```python
llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.getenv("GROQ_API_KEY")
)
```

The LLM is used across different stages, including:

* Input validation
* Flight planning
* Destination extraction
* Weather summarization
* Itinerary generation
* Final travel-plan summarization
* Output validation

---

## ✈️ Flight Planning

The Flight Agent retrieves airport and airline information through the AviationStack MCP integration.

It generates guidance covering:

* Likely departure airport
* Likely arrival airport
* Airlines serving the route
* Typical flight duration
* Estimated airfare range
* Peak-season pricing considerations
* Booking advice

The implementation explicitly instructs the model not to invent exact schedules, prices or availability.

---

## 🏨 Hotel Search

The Hotel Agent builds a hotel-search query from the user's travel request and sends it through the Tavily MCP search tool.

The resulting information is passed into the later itinerary and summary stages.

---

## 🌤️ Weather Planning

The Weather Agent first extracts the destination city from the user's request.

It then calls the weather MCP tool and generates a weather report containing available information such as:

* Temperature
* Weather condition
* Humidity
* Feels-like temperature
* Wind speed
* Forecast
* Rain/precipitation
* Practical travel advice

The itinerary agent then uses the weather information when deciding how to structure outdoor activities.

---

## 📅 Intelligent Itinerary Generation

The Itinerary Agent combines:

* User requirements
* Flight information
* Hotel information
* Weather information

It then generates a realistic day-by-day travel plan.

The system is instructed to:

* Group nearby attractions
* Consider weather conditions
* Avoid unfavorable outdoor activities when appropriate
* Include locations
* Include important attractions and activities
* Consider arrival and departure
* Avoid inventing unavailable flight or weather information

---

## 📝 Final Travel Plan

The Summary Agent combines the outputs from the different stages into one user-facing travel plan.

The final response can contain:

```text
📝 Trip Summary

✈️ Flights

🏨 Hotels

🌤️ Weather Information

📅 Day-by-Day Itinerary

📋 Overall Travel Plan
```

The system is designed to only include information that is actually available and avoid unnecessarily repeating information.

---

## 💾 Persistent Conversation State

TripMate uses **PostgreSQL** together with `PostgresSaver` from LangGraph's checkpoint package.

A unique thread ID is generated for each conversation when one is not supplied:

```text
User
 │
 ▼
Travel Request
 │
 ▼
Thread ID
 │
 ▼
LangGraph
 │
 ▼
PostgreSQL Checkpointer
```

This allows the LangGraph workflow to associate state with a specific conversation thread.

---

## 🌐 FastAPI Backend

The application exposes a FastAPI backend.

### Main Endpoints

#### `GET /`

Serves the TripMate web interface.

#### `POST /api/travel`

Accepts a travel request containing:

```json
{
  "message": "Plan a 7 day trip to Japan",
  "thread_id": "optional-thread-id"
}
```

The endpoint returns:

```json
{
  "success": true,
  "thread_id": "...",
  "answer": "...",
  "flight_results": "...",
  "hotel_results": "...",
  "itinerary": "...",
  "llm_calls": 0
}
```

#### `GET /health`

Returns the application health status.

```json
{
  "status": "ok",
  "message": "AI Travel Planner API is running"
}
```

---

## 🖥️ User Interface

The frontend provides a simple travel-planning interface where users can:

* Enter a natural-language travel request
* Use example travel prompts
* Generate an AI travel plan
* View the generated plan
* Copy the result
* Download the travel plan as a PDF

The frontend is served through FastAPI using Jinja2 templates and static assets.

---

## 🗂️ Project Structure

```text
Tripmate-AI---A-Multi-Agent-Travel-Planner-with-LanngGraph/
│
├── app.py
├── backend.py
├── mcp_client.py
├── mcp_client_test.py
├── test.py
├── requirements.txt
├── runtime.txt
├── .python-version
│
├── static/
│   └── ...
│
└── templates/
    └── index.html
```

### Important Files

| File                   | Purpose                                                             |
| ---------------------- | ------------------------------------------------------------------- |
| `app.py`               | FastAPI application and API endpoints                               |
| `backend.py`           | LangGraph workflow, agents, guardrails and PostgreSQL checkpointing |
| `mcp_client.py`        | MCP server configuration and tool invocation                        |
| `mcp_client_test.py`   | MCP-related testing                                                 |
| `test.py`              | Project testing                                                     |
| `templates/index.html` | Web interface                                                       |
| `static/`              | Frontend assets                                                     |
| `requirements.txt`     | Python dependencies                                                 |
| `.python-version`      | Python version configuration                                        |

The repository currently specifies **Python 3.13.5**.

---

# 🚀 Getting Started

## 1. Clone the Repository

```bash
git clone https://github.com/Miikeyop/Tripmate-AI---A-Multi-Agent-Travel-Planner-with-LanngGraph.git

cd Tripmate-AI---A-Multi-Agent-Travel-Planner-with-LanngGraph
```

## 2. Create a Virtual Environment

```bash
python -m venv .venv
```

### Windows

```bash
.venv\Scripts\activate
```

### Linux / macOS

```bash
source .venv/bin/activate
```

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

The repository includes dependencies for FastAPI, LangChain, LangGraph, Groq, MCP adapters, PostgreSQL checkpointing, Tavily and related components.

---

# 🔑 Environment Variables

Create a `.env` file in the project root.

```env
GROQ_API_KEY=your_groq_api_key
TAVILY_API_KEY=your_tavily_api_key
AVIATIONSTACK_API_KEY=your_aviationstack_api_key
DATABASE_URL=your_postgresql_connection_string
```

These variables are used by the current implementation for:

* Groq LLM access
* Tavily MCP
* AviationStack MCP
* PostgreSQL persistence

> **Never commit your `.env` file or API keys to GitHub.**

---

# ▶️ Run the Application

Start the FastAPI application with:

```bash
python app.py
```

The application starts Uvicorn on:

```text
http://127.0.0.1:8000
```

Then open the address in your browser.

---

# 💬 Example Queries

Try requests such as:

```text
Plan a complete 7 day Japan trip including flights, hotels and sightseeing under 2 lakhs.
```

```text
Plan a 5 days Dubai trip with flights, hotels and sightseeing.
```

```text
Plan a 7 days Thailand trip with budget hotels and sightseeing.
```

The web interface already includes example prompts for Japan, Dubai, Thailand and global flight information.

---

# 🔄 End-to-End Example

A request such as:

```text
Plan a 7 day trip to Japan including flights,
hotels, weather and sightseeing.
```

moves through the system as:

```text
                 USER
                   │
                   ▼
          "Plan a Japan trip"
                   │
                   ▼
          ┌────────────────┐
          │ Input Guardrail│
          └───────┬────────┘
                  │
                  ▼
          ┌────────────────┐
          │  Flight Agent  │──────► AviationStack MCP
          └───────┬────────┘
                  │
                  ▼
          ┌────────────────┐
          │  Hotel Agent   │──────► Tavily MCP
          └───────┬────────┘
                  │
                  ▼
          ┌────────────────┐
          │ Weather Agent  │──────► Weather MCP
          └───────┬────────┘
                  │
                  ▼
          ┌────────────────┐
          │Itinerary Agent │
          └───────┬────────┘
                  │
                  ▼
          ┌────────────────┐
          │ Summary Agent  │
          └───────┬────────┘
                  │
                  ▼
          ┌────────────────┐
          │Output Guardrail│
          └───────┬────────┘
                  │
                  ▼
          📝 FINAL TRAVEL PLAN
```

---

# 🛠️ Technology Stack

### Backend

* **Python 3.13.5**
* **FastAPI**
* **Uvicorn**
* **Jinja2**

### AI / LLM

* **Groq**
* **Llama 3.1 8B Instant**
* **LangChain**
* **LangChain Core**

### Agent Orchestration

* **LangGraph**
* **StateGraph**
* Conditional routing
* PostgreSQL checkpointing

### Tool Integration

* **Model Context Protocol (MCP)**
* **LangChain MCP Adapters**
* Tavily MCP
* AviationStack MCP
* Weather MCP

### Database

* **PostgreSQL**
* **Psycopg**
* **LangGraph Postgres Checkpointer**

### Frontend

* HTML
* CSS
* JavaScript
* Jinja2 templates
* Marked.js
* html2pdf.js

The current dependency configuration confirms the major framework and integration versions used by the project.

---

# 🧪 Testing

The repository includes:

```text
mcp_client_test.py
test.py
```

The MCP client also includes a utility for discovering and printing the available MCP tools, their descriptions and schemas.

Run the available test files according to your local Python environment, for example:

```bash
python test.py
```

and:

```bash
python mcp_client_test.py
```

---

# 🔒 Safety & Reliability

TripMate incorporates several defensive mechanisms:

### Input Validation

Requests are checked before entering the main travel workflow.

### Output Validation

Generated travel plans are checked before being returned.

### Fail-Closed Guardrails

If guardrail validation fails, the request or response is rejected.

### No Fabricated Travel Details

The flight and weather prompts explicitly instruct the LLM not to invent unavailable information.

### Secret Protection

The guardrails explicitly check for attempts to expose API keys, credentials, environment variables and internal implementation details.

---

# 🎯 Why This Project?

TripMate demonstrates how a modern AI application can combine:

```text
LLM
 │
 ├── Multi-Agent Architecture
 │
 ├── Workflow Orchestration
 │
 ├── External Tool Integration
 │
 ├── MCP
 │
 ├── Guardrails
 │
 ├── Persistent State
 │
 └── API + Web Application
```

Rather than treating an LLM as a standalone chatbot, the project demonstrates a structured AI workflow where specialized components cooperate to solve a broader problem.

---

# 📌 Future Improvements

Potential improvements for future versions include:

* Parallel execution of independent travel agents
* More travel APIs
* Real-time flight availability and booking integrations
* Real-time hotel availability
* Budget optimization
* Route optimization
* User preference memory
* Authentication and user accounts
* More granular tool-level permissions
* Improved automated test coverage
* Production deployment and monitoring

---

# 👨‍💻 Author

**Miikeyop**

GitHub:
https://github.com/Miikeyop

Project:
https://github.com/Miikeyop/Tripmate-AI---A-Multi-Agent-Travel-Planner-with-LanngGraph

---

## ⭐ Project Highlights

```text
🤖 Multi-Agent AI
🧠 LangGraph
🔌 Model Context Protocol (MCP)
🛡️ Input & Output Guardrails
⚡ Groq / Llama 3.1
✈️ AviationStack MCP
🔎 Tavily MCP
🌤️ Weather MCP
🗄️ PostgreSQL Checkpointing
🚀 FastAPI
🌐 Web Interface
```

---

**Built with Python, LangGraph, MCP, FastAPI, Groq and PostgreSQL.**

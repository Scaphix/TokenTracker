# TokenTracker: AI Cost Calculator Agent

A helper agent that estimates the cost of running AI agents, tools, and servers — before production.

## Installation

- Create & Activate Python venv in root directory
- `pip install -r ./requirements.txt`
- Create `.env` in my_agent/
- Add to .env the following values
```
GOOGLE_GENAI_USE_VERTEXAI=0
GOOGLE_API_KEY=<your-api-key>
```
- Run `adk run my_agent` in root directory for cli version
- Run `adk web --port <port>` in root directory for web version

## Agent Purpose & Scope

###  Background & Motivation:

I wanted to build an AI Agent for real-world use, but I realized I had no clear way to estimate how much it would cost a user — especially if multiple agents, tools, hosting platforms, or LLM models were involved.
Because of this uncertainty, I had an idea:

➡️ Build an AI Agent that can calculate the cost of running any AI agent or full AI project.
This tool could help me — and other developers — plan projects, control budget, optimize models, and compare platforms before launching to production.


### Agent Purpose

The Cost Calculator AI Agent is designed to:

- Estimate the cost of AI models.
- Calculate server and hosting costs.
- Simulate multi-agent workflows and their total cost
- Compare pricing options across LLM models and platforms.
- Help developers predict production cost before deployment.
- Support decision making: Recommend cheaper or optimized alternative.

### Core Functions:

1. Collect information

The agent needs to know what the AI is buid of before being able to calculate the cost of production:

- Detect missing inputs:	“We can’t calculate cost yet — data is missing.”
- Offer defaults: “Would you like industry averages?”
- Ask smart questions	: “Do you expect few or many tasks per day?”
- Show the formula:	Build trust & transparency
- Refine over time : Make estimates more accurate

2. calculate production costs

- LLM Cost Estimation: Calculates cost based on tokens & model pricing
- Server Cost Estimation: Estimates hosting cost for websites or agents
- Tool Cost Estimation: Costs of APIs (e.g., web search, vector DB)
- Multi-Agent Workflow Cost: Simulates team of agents with multiple steps
- Cost Comparison: Compare platforms/models to find cheapest option
- Recommendation: Suggest cheaper alternatives or cost optimizations


### Scope & Limitations

1. Core Features :

- LLM Cost Estimation	: Calculates token-based cost for GPT / Claude models
- Server Cost Estimation: 	Estimates monthly cost for hosting providers
- Tool Cost Estimation: Cost of APIs (e.g., web search, vector DB)
- Multi-Agent Simulation: Calculates cost of workflows with multiple agents
- Cost Comparison	: Compares platforms and model providers
- Recommendations	: Optimizes for lowest-cost setups

2. Future Expansion

In later versions, the agent could:

- Use real pricing APIs (AWS Pricing API, OpenAI tools API, etc.)
- Track real token usage of agents
- Store history and learn typical usage patterns
- Run as a service with a web interface


# Architecture Overview: 

## Multi-Agent Flow:


1️⃣ Overview of the Workflow

### User Input:

User specifies project details:

Number/type of AI agents

Expected API calls per agent (tokens, calls per day)

Hosting requirements (Vertex AI resources, storage, traffic)

Whether live pricing is needed

### Planner Agent :

- Interprets the input
- Decides which tasks are needed (LLM cost, server cost, live pricing)
- Generates a task list for the Dispatcher

### Dispatcher Agent:

Sends each task to the appropriate agent:
- LLM Cost Agent → calculates token usage cost based on model choice
- Server Cost Agent → calculates Vertex AI resource cost
- Pricing API Agent → fetches live pricing using Google API key
- Workflow Agent → aggregates multiple agents’ costs

### Pricing API Agent:

Uses Google Cloud APIs (or Vertex AI pricing endpoints) to fetch:
- Vertex AI managed instance costs
- Storage costs (Cloud Storage buckets)
- Traffic / egress fees
- LLM pricing if using Vertex-hosted models
- Stores results in JSON format for other agents

### LLM Cost Agent:

Uses static or live model pricing
- Calculates total tokens per month × cost per 1M tokens

### Server Cost Agent:

Calculates Vertex AI compute costs:

- Instance type (CPU/GPU) × hours per month × region pricing
- Storage and network usage


### Workflow Agent:

Aggregates all costs:

- Multi-agent LLM usage
- Hosting + storage + bandwidth


### Formatter Agent:

Creates human-readable report and JSON output:



✅ Result:

- Understand the project
- Collect pricing data (live + static)
- Compute LLM + server + workflow costs
- Output clear, actionable reports

Answer always includes:

- 🧾 Source of prices

- 📅 Date of retrieval

- 📊 Confidence level

User Input → Planner Agent 
               │
               ▼
         Dispatcher Agent
   ┌─────────┬─────────┐
   ▼         ▼         ▼
LLM Cost  Server Cost  Pricing API
 Agent      Agent        Agent
   │         │         │
   └─────────┴─────────┘
               │
               ▼
        Workflow Agent
               │
               ▼
        Formatter Agent → Output




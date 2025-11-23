from google.adk.runners import InMemoryRunner
from google.adk.agents import Agent, SequentialAgent
from google.adk.tools import google_search


information_collector = Agent(
    name="InformationCollector",
    model="gemini-2.5-flash-lite",
    instruction="""You are a specialized research agent,
    who collect information about AI cost estimation. Your job is to:
    1. Analyze the user's request and identify what information is needed
    2. Detect missing inputs (model type, token counts, server specs, etc.)
    3. Offer sensible defaults when data is missing
    4. Ask clarifying questions: "Do you expect few or many tasks per day?"
    5. Present the calculation formula for transparency

    Return a structured dictionary with all necessary parameters for
    cost calculation.""",
    tools=[google_search],
    output_key="collected_information",
)

print("✅ research_agent created.")
# cost_calculation_agent.py
cost_calculator = Agent(
    name="CostCalculator",
    model="gemini-2.5-flash-lite",
    instruction="""You are a cost calculation specialist.
    Using the collected information: {collected_information}

    Calculate:
    1. LLM costs (tokens by model pricing)
    2. Server/hosting costs
    3. Tool/API costs
    4. Multi-agent workflow costs if applicable
    5. Total monthly and daily costs

    Then provide:
    - Cost breakdown by category
    - Cost comparisons (if alternatives exist)
    - Recommendations for optimization
    (e.g., "Switch to gpt-4o-mini to save 60%")

    Return detailed cost analysis with formulas shown.""",
    tools=[google_search],
    output_key="cost_analysis"
)

print("✅ summarizer_agent created.")


root_agent = SequentialAgent(
    name="CostCalculatorCoordinator",
    model="gemini-2.5-flash-lite",
    instruction="""You are a cost calculator coordinator.
    Your goal is to answer the user's query by orchestrating
    a workflow of agents. You have two agents at your disposal:
    - InformationCollector: to gather information about the user's query
    - CostCalculator: to calculate the cost of the user's query

    Your workflow:
    1. FIRST, call the `InformationCollector` tool to gather all inputs
    2. NEXT, call the `CostCalculator` tool with the collected information
    3. FINALLY, present the complete cost analysis to the user with:
       - Clear breakdown
       - Assumptions made
       - Recommendations
       - Formulas used""",
    sub_agents=[information_collector, cost_calculator]
)

print("✅ root_agent created.")

runner = InMemoryRunner(agent=root_agent)
response = runner.run_debug("How much will my AI agent cost? ")

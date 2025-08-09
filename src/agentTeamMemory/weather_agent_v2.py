
from google.adk.agents import Agent
import tools
from dotenv import load_dotenv
import os
import subAgents
# @title Define the Root Agent with Sub-Agents

# Ensure sub-agents were created successfully before defining the root agent.
# Also ensure the original 'get_weather' tool is defined.

load_dotenv()
root_agent_model = os.getenv("MODEL_GEMINI_2_0_FLASH")
# Let's use a capable Gemini model for the root agent to handle orchestration

weather_agent_team = Agent(
  name="weather_agent_v2",
  model=root_agent_model,
  description="The main coordinator agent. Handles weather requests and delegates greeting/farewell to specialist.",
  instruction="You are the main Weather Agent coordinating a team. Your primary responsibility is to provide weather information."
                "Use the 'get_weather' tool ONLY for specific weather requests (e.g., 'weather in London'). "
                "You have specialized sub-agents: "
                "1. 'greeting_agent': Handles simple greetings like 'Hi', 'Hello'. Delegate to it for these. "
                "2. 'farewell_agent': Handles simple farewells like 'Bye', 'See you'. Delegate to it for these. "
                "Analyze the user's query. If it's a greeting, delegate to 'greeting_agent'. If it's a farewell, delegate to 'farewell_agent'. "
                "If it's a weather request, handle it yourself using 'get_weather'. "
                "For anything else, respond appropriately or state you cannot handle it."
                "If the user asks for a city you don't know, tell him: cities you know are: " + ", ".join(tools.getCities()),
  tools=[tools.get_weather],
  sub_agents=[subAgents.greeting_agent, subAgents.farewell_agent],
)

print(f"✅ Root Agent '{weather_agent_team.name}' created using model '{root_agent_model}' with sub-agents: {[sa.name for sa in weather_agent_team.sub_agents]}")

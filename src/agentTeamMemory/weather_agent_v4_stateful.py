
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

weather_agent_stateful = Agent(
  name="weather_agent_v4_stateful",
  model=root_agent_model,
  description="Main agent: Provides weather (state-aware unit), delegates greetings/farewells, saves report to state.",
  instruction="You are the main Weather Agent. Your job is to provide weather using 'get_weather_stateful'. "
                    "The tool will format the temperature based on user preference stored in state. "
                    "Delegate simple greetings to 'greeting_agent' and farewells to 'farewell_agent'. "
                    "Handle only weather requests, greetings, and farewells."
                    "If the user asks for a city you don't know, tell him: cities you know are: " + ", ".join(tools.getCities()),
  tools=[tools.get_weather_stateful], # Use the state-aware tool
  sub_agents=[subAgents.greeting_agent, subAgents.farewell_agent],
  output_key="last_weather_report" # <<< Auto-save agent's final weather response

)

print(f"✅ Root Agent '{weather_agent_stateful.name}' created using model '{root_agent_model}' with sub-agents: {[sa.name for sa in weather_agent_team.sub_agents]}")

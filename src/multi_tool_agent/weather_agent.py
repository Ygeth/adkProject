
from google.adk.agents import Agent
import tools
from dotenv import load_dotenv
import os

load_dotenv()

AGENT_MODEL = os.getenv("AGENT_MODEL")

weather_agent = Agent(
  name="weather_agent_v1",
  model=AGENT_MODEL,
  description="Provides weather information for specific cities.",
  instruction="You are a helpful weather assistant. "
                "When the user asks for the weather in a specific city,"
                "use the 'get_weather' tool to find the information. "
                "If the tool returns an error, inform the user politely. "
                "If the tool is successful, present the weather report clearly."
                "If the user asks for a city you don't know, tell him: cities you know are: " + ", ".join(tools.getCities()),
  tools=[tools.get_weather],
)
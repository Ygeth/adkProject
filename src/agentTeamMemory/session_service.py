import asyncio
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types # For creating message Content/Parts
from agentTeamMemory.weather_agent_v4_stateful import weather_agent_stateful

from google.genai import types # For creating message Content/Parts
import asyncio

# Define constants for identifying the interaction context
APP_NAME = "weather_tutorial_app"
USER_ID_STATEFUL = "user_state_demo"
SESSION_ID_STATEFUL = "session_state_demo_001" # Using a fixed ID for simplicity

# @title Define Agent Interaction Function
async def call_agent_async(query: str, runner, user_id, session_id):
  """Sends a query to the agent and prints the final response."""
  print(f"\n>>> User Query: {query}")

  # Prepare the user's message in ADK format
  content = types.Content(role='user', parts=[types.Part(text=query)])

  final_response_text = "Agent did not produce a final response." # Default

  # Key Concept: run_async executes the agent logic and yields Events.
  # We iterate through events to find the final answer.
  async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=content):
      # You can uncomment the line below to see *all* events during execution
      # print(f"  [Event] Author: {event.author}, Type: {type(event).__name__}, Final: {event.is_final_response()}, Content: {event.content}")

      # Key Concept: is_final_response() marks the concluding message for the turn.
      if event.is_final_response():
          if event.content and event.content.parts:
             # Assuming text response in the first part
             final_response_text = event.content.parts[0].text
          elif event.actions and event.actions.escalate: # Handle potential errors/escalations
             final_response_text = f"Agent escalated: {event.error_message or 'No specific message.'}"
          # Add more checks here if needed (e.g., specific error codes)
          break # Stop processing events once the final response is found

  print(f"<<< Agent Response: {final_response_text}")
  
  
# @title Run the Initial Conversation

# We need an async function to await our interaction helper
async def run_conversation():
    # Define initial state data - user prefers Celsius initially
    initial_state = {
        "user_preference_temperature_unit": "Celsius"
    }

    # @title Setup Session Service and Runner

    # --- Session Management ---
    # Key Concept: SessionService stores conversation history & state.
    # InMemorySessionService is simple, non-persistent storage for this tutorial.
    # Create a NEW session service instance for this state demonstration
    session_service_stateful = InMemorySessionService()

    session_stateful = await session_service_stateful.create_session(
        app_name=APP_NAME,
        user_id=USER_ID_STATEFUL,
        session_id=SESSION_ID_STATEFUL,
        state = initial_state # Pass initial state data
    )
    print(f"✅ Session created: App='{APP_NAME}', User='{USER_ID_STATEFUL}', Session='{SESSION_ID_STATEFUL}'")

    # Verify the initial state was set correctly
    retrieved_session = await session_service_stateful.get_session(app_name=APP_NAME,
                                                            user_id=USER_ID_STATEFUL,
                                                            session_id = SESSION_ID_STATEFUL)
    print("\n--- Initial Session State ---")
    if retrieved_session:
        print(retrieved_session.state)
    else:
        print("Error: Could not retrieve session.")

    # --- Runner ---
    # Key Concept: Runner orchestrates the agent execution loop.
    runner_root_stateful = Runner(
        agent=weather_agent_stateful, # The agent we want to run
        app_name=APP_NAME,   # Associates runs with our app
        session_service=session_service_stateful # Uses our session manager
    )
    print(f"Runner created for agent '{runner_root_stateful.agent.name}'.")

    # 1. Check weather (Uses initial state: Celsius)
    print("--- Turn 1: Requesting weather in London (expect Celsius) ---")
    await call_agent_async(query= "What's the weather in London?",
                            runner=runner_root_stateful,
                            user_id=USER_ID_STATEFUL,
                            session_id=SESSION_ID_STATEFUL
                            )

    # 2. Manually update state preference to Fahrenheit - DIRECTLY MODIFY STORAGE
    print("\n--- Manually Updating State: Setting unit to Fahrenheit ---")
    try:
        # Access the internal storage directly - THIS IS SPECIFIC TO InMemorySessionService for testing
        # NOTE: In production with persistent services (Database, VertexAI), you would
        # typically update state via agent actions or specific service APIs if available,
        # not by direct manipulation of internal storage.
        stored_session = session_service_stateful.sessions[APP_NAME][USER_ID_STATEFUL][SESSION_ID_STATEFUL]
        stored_session.state["user_preference_temperature_unit"] = "Fahrenheit"
        # Optional: You might want to update the timestamp as well if any logic depends on it
        # import time
        # stored_session.last_update_time = time.time()
        print(f"--- Stored session state updated. Current 'user_preference_temperature_unit': {stored_session.state.get('user_preference_temperature_unit', 'Not Set')} ---") # Added .get for safety
    except KeyError:
        print(f"--- Error: Could not retrieve session '{SESSION_ID_STATEFUL}' from internal storage for user '{USER_ID_STATEFUL}' in app '{APP_NAME}' to update state. Check IDs and if session was created. ---")
    except Exception as e:
            print(f"--- Error updating internal session state: {e} ---")

    # 3. Check weather again (Tool should now use Fahrenheit)
    # This will also update 'last_weather_report' via output_key
    print("\n--- Turn 2: Requesting weather in New York (expect Fahrenheit) ---")
    await call_agent_async(query= "Tell me the weather in New York.",
                            runner=runner_root_stateful,
                            user_id=USER_ID_STATEFUL,
                            session_id=SESSION_ID_STATEFUL
                            )
    
    # 4. Test basic delegation (should still work)
    # This will update 'last_weather_report' again, overwriting the NY weather report
    print("\n--- Turn 3: Sending a greeting ---")
    await call_agent_async(query= "Hi!",
                            runner=runner_root_stateful,
                            user_id=USER_ID_STATEFUL,
                            session_id=SESSION_ID_STATEFUL
                            )

    await call_agent_async("Tell me the weather in New York",
                            runner=runner_root_stateful,
                            user_id=USER_ID_STATEFUL,
                            session_id=SESSION_ID_STATEFUL)
    
# Uncomment the following lines if running as a standard Python script (.py file):
if __name__ == "__main__":
    try:
        asyncio.run(run_conversation())
    except Exception as e:
        print(f"An error occurred: {e}")
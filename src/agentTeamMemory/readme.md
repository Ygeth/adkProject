# Step 4: Adding Memory and Personalization with Session State

## What is Session State?

* It's a Python dictionary (`session.state`) tied to a specific user session (identified by `APP_NAME`, `USER_ID`, `SESSION_ID`).
* It persists information across multiple conversational turns within that session.
* Agents and Tools can read from and write to this state, allowing them to remember details, adapt behavior, and personalize responses.

## How Agents Interact with State:

* **ToolContext (Primary Method)**: Tools can accept a `ToolContext` object (automatically provided by ADK if declared as the last argument). This object gives direct access to the session state via `tool_context.state`, allowing tools to read preferences or save results during execution.
* **output_key (Auto-Save Agent Response)**: An Agent can be configured with an `output_key="your_key"`. ADK will then automatically save the agent's final textual response for a turn into `session.state["your_key"]`.

In this step, we will enhance our Weather Bot team by:

1. Using a new `InMemorySessionService` to demonstrate state in isolation.
2. Initializing session state with a user preference for `temperature_unit`.
3. Creating a state-aware version of the weather tool (`get_weather_stateful`) that reads this preference via `ToolContext` and adjusts its output format (Celsius/Fahrenheit).
4. Updating the root agent to use this stateful tool and configuring it with an `output_key` to automatically save its final weather report to the session state.
5. Running a conversation to observe how the initial state affects the tool, how manual state changes alter subsequent behavior, and how `output_key` persists the agent's response.

## 1. Initialize New Session Service and State

To clearly demonstrate state management without interference from prior steps, we'll instantiate a new `InMemorySessionService`. We'll also create a session with an initial state defining the user's preferred temperature unit.

```python
# Import necessary session components
from google.adk.sessions import InMemorySessionService

# Create a NEW session service instance for this state demonstration
session_service_stateful = InMemorySessionService()
print("✅ New InMemorySessionService created for state demonstration.")

# Define a NEW session ID for this part of the tutorial
SESSION_ID_STATEFUL = "session_state_demo_001"
USER_ID_STATEFUL = "user_state_demo"

# Define initial state data - user prefers Celsius initially
initial_state = {
    "user_preference_temperature_unit": "Celsius"
}

# Create the session, providing the initial state
session_stateful = await session_service_stateful.create_session(
    app_name=APP_NAME, # Use the consistent app name
    user_id=USER_ID_STATEFUL,
    session_id=SESSION_ID_STATEFUL,
    state=initial_state # <<< Initialize state during creation
)
print(f"✅ Session '{SESSION_ID_STATEFUL}' created for user '{USER_ID_STATEFUL}'.")

# Verify the initial state was set correctly
retrieved_session = await session_service_stateful.get_session(app_name=APP_NAME,
                                                         user_id=USER_ID_STATEFUL,
                                                         session_id = SESSION_ID_STATEFUL)
print("\n--- Initial Session State ---")
if retrieved_session:
    print(retrieved_session.state)
else:
    print("Error: Could not retrieve session.")
```

## 2. Create State-Aware Weather Tool (get_weather_stateful)

Now, we create a new version of the weather tool. Its key feature is accepting `tool_context: ToolContext` which allows it to access `tool_context.state`. It will read the `user_preference_temperature_unit` and format the temperature accordingly.

### Key Concept: ToolContext
This object is the bridge allowing your tool logic to interact with the session's context, including reading and writing state variables. ADK injects it automatically if defined as the last parameter of your tool function.

### Best Practice
When reading from state, use `dictionary.get('key', default_value)` to handle cases where the key might not exist yet, ensuring your tool doesn't crash.

```python
from google.adk.tools.tool_context import ToolContext

def get_weather_stateful(city: str, tool_context: ToolContext) -> dict:
    """Retrieves weather, converts temp unit based on session state."""
    print(f"--- Tool: get_weather_stateful called for {city} ---")

    # --- Read preference from state ---
    preferred_unit = tool_context.state.get("user_preference_temperature_unit", "Celsius") # Default to Celsius
    print(f"--- Tool: Reading state 'user_preference_temperature_unit': {preferred_unit} ---")

    city_normalized = city.lower().replace(" ", "")

    # Mock weather data (always stored in Celsius internally)
    mock_weather_db = {
        "newyork": {"temp_c": 25, "condition": "sunny"},
        "london": {"temp_c": 15, "condition": "cloudy"},
        "tokyo": {"temp_c": 18, "condition": "light rain"},
    }

    if city_normalized in mock_weather_db:
        data = mock_weather_db[city_normalized]
        temp_c = data["temp_c"]
        condition = data["condition"]

        # Format temperature based on state preference
        if preferred_unit == "Fahrenheit":
            temp_value = (temp_c * 9/5) + 32 # Calculate Fahrenheit
            temp_unit = "°F"
        else: # Default to Celsius
            temp_value = temp_c
            temp_unit = "°C"

        report = f"The weather in {city.capitalize()} is {condition} with a temperature of {temp_value:.0f}{temp_unit}."
        result = {"status": "success", "report": report}
        print(f"--- Tool: Generated report in {preferred_unit}. Result: {result} ---")

        # Example of writing back to state (optional for this tool)
        tool_context.state["last_city_checked_stateful"] = city
        print(f"--- Tool: Updated state 'last_city_checked_stateful': {city} ---")

        return result
    else:
        # Handle city not found
        error_msg = f"Sorry, I don't have weather information for '{city}'."
        print(f"--- Tool: City '{city}' not found. ---")
        return {"status": "error", "error_message": error_msg}

print("✅ State-aware 'get_weather_stateful' tool defined.")
```

## 3. Redefine Sub-Agents and Update Root Agent

To ensure this step is self-contained and builds correctly, we first redefine the `greeting_agent` and `farewell_agent` exactly as they were in Step 3. Then, we define our new root agent (`weather_agent_v4_stateful`):

* It uses the new `get_weather_stateful` tool.
* It includes the greeting and farewell sub-agents for delegation.
* Crucially, it sets `output_key="last_weather_report"` which automatically saves its final weather response to the session state.

```python
# Ensure necessary imports: Agent, LiteLlm, Runner
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import Runner
# Ensure tools 'say_hello', 'say_goodbye' are defined (from Step 3)
# Ensure model constants MODEL_GPT_4O, MODEL_GEMINI_2_0_FLASH etc. are defined

# --- Redefine Greeting Agent (from Step 3) ---
greeting_agent = None
try:
    greeting_agent = Agent(
        model=MODEL_GEMINI_2_0_FLASH,
        name="greeting_agent",
        instruction="You are the Greeting Agent. Your ONLY task is to provide a friendly greeting using the 'say_hello' tool. Do nothing else.",
        description="Handles simple greetings and hellos using the 'say_hello' tool.",
        tools=[say_hello],
    )
    print(f"✅ Agent '{greeting_agent.name}' redefined.")
except Exception as e:
    print(f"❌ Could not redefine Greeting agent. Error: {e}")

# --- Redefine Farewell Agent (from Step 3) ---
farewell_agent = None
try:
    farewell_agent = Agent(
        model=MODEL_GEMINI_2_0_FLASH,
        name="farewell_agent",
        instruction="You are the Farewell Agent. Your ONLY task is to provide a polite goodbye message using the 'say_goodbye' tool. Do not perform any other actions.",
        description="Handles simple farewells and goodbyes using the 'say_goodbye' tool.",
        tools=[say_goodbye],
    )
    print(f"✅ Agent '{farewell_agent.name}' redefined.")
except Exception as e:
    print(f"❌ Could not redefine Farewell agent. Error: {e}")

# --- Define the Updated Root Agent ---
root_agent_stateful = None
runner_root_stateful = None # Initialize runner

# Check prerequisites before creating the root agent
if greeting_agent and farewell_agent and 'get_weather_stateful' in globals():

    root_agent_model = MODEL_GEMINI_2_0_FLASH # Choose orchestration model

    root_agent_stateful = Agent(
        name="weather_agent_v4_stateful", # New version name
        model=root_agent_model,
        description="Main agent: Provides weather (state-aware unit), delegates greetings/farewells, saves report to state.",
        instruction="You are the main Weather Agent. Your job is to provide weather using 'get_weather_stateful'. "
                    "The tool will format the temperature based on user preference stored in state. "
                    "Delegate simple greetings to 'greeting_agent' and farewells to 'farewell_agent'. "
                    "Handle only weather requests, greetings, and farewells.",
        tools=[get_weather_stateful], # Use the state-aware tool
        sub_agents=[greeting_agent, farewell_agent], # Include sub-agents
        output_key="last_weather_report" # <<< Auto-save agent's final weather response
    )
    print(f"✅ Root Agent '{root_agent_stateful.name}' created using stateful tool and output_key.")

    # --- Create Runner for this Root Agent & NEW Session Service ---
    runner_root_stateful = Runner(
        agent=root_agent_stateful,
        app_name=APP_NAME,
        session_service=session_service_stateful # Use the NEW stateful session service
    )
    print(f"✅ Runner created for stateful root agent '{runner_root_stateful.agent.name}' using stateful session service.")

else:
    print("❌ Cannot create stateful root agent. Prerequisites missing.")
    if not greeting_agent: print(" - greeting_agent definition missing.")
    if not farewell_agent: print(" - farewell_agent definition missing.")
    if 'get_weather_stateful' not in globals(): print(" - get_weather_stateful tool missing.")
```

## 4. Interact and Test State Flow

Now, let's execute a conversation designed to test the state interactions using the `runner_root_stateful` (associated with our stateful agent and the `session_service_stateful`). We'll use the `call_agent_async` function defined earlier, ensuring we pass the correct runner, user ID (`USER_ID_STATEFUL`), and session ID (`SESSION_ID_STATEFUL`).

The conversation flow will be:

1. **Check weather (London)**: The `get_weather_stateful` tool should read the initial "Celsius" preference from the session state initialized in Section 1. The root agent's final response (the weather report in Celsius) should get saved to `state['last_weather_report']` via the `output_key` configuration.

2. **Manually update state**: We will directly modify the state stored within the `InMemorySessionService` instance (`session_service_stateful`).
   * Why direct modification? The `session_service.get_session()` method returns a copy of the session. Modifying that copy wouldn't affect the state used in subsequent agent runs. For this testing scenario with `InMemorySessionService`, we access the internal sessions dictionary to change the actual stored state value for `user_preference_temperature_unit` to "Fahrenheit". Note: In real applications, state changes are typically triggered by tools or agent logic returning `EventActions(state_delta=...)`, not direct manual updates.

3. **Check weather again (New York)**: The `get_weather_stateful` tool should now read the updated "Fahrenheit" preference from the state and convert the temperature accordingly. The root agent's new response (weather in Fahrenheit) will overwrite the previous value in `state['last_weather_report']` due to the `output_key`.

4. **Greet the agent**: Verify that delegation to the `greeting_agent` still works correctly alongside the stateful operations. This interaction will become the last response saved by `output_key` in this specific sequence.

5. **Inspect final state**: After the conversation, we retrieve the session one last time (getting a copy) and print its state to confirm the `user_preference_temperature_unit` is indeed "Fahrenheit", observe the final value saved by `output_key` (which will be the greeting in this run), and see the `last_city_checked_stateful` value written by the tool.

```python
# Ensure asyncio is imported
import asyncio

# Ensure the stateful runner (runner_root_stateful) is available from the previous cell
# Ensure call_agent_async, USER_ID_STATEFUL, SESSION_ID_STATEFUL, APP_NAME are defined

if 'runner_root_stateful' in globals() and runner_root_stateful:
    # Define the main async function for the stateful conversation logic.
    # The 'await' keywords INSIDE this function are necessary for async operations.
    async def run_stateful_conversation():
        print("\n--- Testing State: Temp Unit Conversion & output_key ---")

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

    # --- Execute the `run_stateful_conversation` async function ---
    # Choose ONE of the methods below based on your environment.

    # METHOD 1: Direct await (Default for Notebooks/Async REPLs)
    # If your environment supports top-level await (like Colab/Jupyter notebooks),
    # it means an event loop is already running, so you can directly await the function.
    print("Attempting execution using 'await' (default for notebooks)...")
    await run_stateful_conversation()

    # METHOD 2: asyncio.run (For Standard Python Scripts [.py])
    # If running this code as a standard Python script from your terminal,
    # the script context is synchronous. `asyncio.run()` is needed to
    # create and manage an event loop to execute your async function.
    # To use this method:
    # 1. Comment out the `await run_stateful_conversation()` line above.
    # 2. Uncomment the following block:
    """
    import asyncio
    if __name__ == "__main__": # Ensures this runs only when script is executed directly
        print("Executing using 'asyncio.run()' (for standard Python scripts)...")
        try:
            # This creates an event loop, runs your async function, and closes the loop.
            asyncio.run(run_stateful_conversation())
        except Exception as e:
            print(f"An error occurred: {e}")
    """

    # --- Inspect final session state after the conversation ---
    # This block runs after either execution method completes.
    print("\n--- Inspecting Final Session State ---")
    final_session = await session_service_stateful.get_session(app_name=APP_NAME,
                                                         user_id= USER_ID_STATEFUL,
                                                         session_id=SESSION_ID_STATEFUL)
    if final_session:
        # Use .get() for safer access to potentially missing keys
        print(f"Final Preference: {final_session.state.get('user_preference_temperature_unit', 'Not Set')}")
        print(f"Final Last Weather Report (from output_key): {final_session.state.get('last_weather_report', 'Not Set')}")
        print(f"Final Last City Checked (by tool): {final_session.state.get('last_city_checked_stateful', 'Not Set')}")
        # Print full state for detailed view
        # print(f"Full State Dict: {final_session.state}") # For detailed view
    else:
        print("\n❌ Error: Could not retrieve final session state.")

else:
    print("\n⚠️ Skipping state test conversation. Stateful root agent runner ('runner_root_stateful') is not available.")
```

By reviewing the conversation flow and the final session state printout, you can confirm:

1. **State Read**: The weather tool (`get_weather_stateful`) correctly read `user_preference_temperature_unit` from state, initially using "Celsius" for London.
2. **State Update**: The direct modification successfully changed the stored preference to "Fahrenheit".
3. **State Read (Updated)**: The tool subsequently read "Fahrenheit" when asked for New York's weather and performed the conversion.
4. **Tool State Write**: The tool successfully wrote the `last_city_checked_stateful` ("New York" after the second weather check) into the state via `tool_context.state`.
5. **Delegation**: The delegation to the `greeting_agent` for "Hi!" functioned correctly even after state modifications.
6. **output_key**: The `output_key="last_weather_report"` successfully saved the root agent's final response for each turn where the root agent was the one ultimately responding. In this sequence, the last response was the greeting ("Hello, there!"), so that overwrote the weather report in the state key.
7. **Final State**: The final check confirms the preference persisted as "Fahrenheit".

You've now successfully integrated session state to personalize agent behavior using `ToolContext`, manually manipulated state for testing `InMemorySessionService`, and observed how `output_key` provides a simple mechanism for saving the agent's last response to state. This foundational understanding of state management is key as we proceed to implement safety guardrails using callbacks in the next steps.

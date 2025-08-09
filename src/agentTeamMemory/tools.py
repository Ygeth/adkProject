import datetime
from zoneinfo import ZoneInfo
from typing import Optional
from google.adk.tools.tool_context import ToolContext

# Mock weather data
mock_weather_db = {
    "newyork": {"status": "success", "report": "The weather in New York is sunny with a temperature of 25°C."},
    "london": {"status": "success", "report": "It's cloudy in London with a temperature of 15°C."},
    "tokyo": {"status": "success", "report": "Tokyo is experiencing light rain and a temperature of 18°C."},
}

# @title Define the getCities Function
def getCities():
    """Returns a list of cities for which weather information is available."""
    return list(mock_weather_db.keys())

# @title Define the get_weather_stateful Tool
# This tool retrieves weather information and respects user preferences stored in session state.
def get_weather_stateful(city:str, tool_context: ToolContext) -> dict:
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

    
# @title Basic get_weather Tool
def get_weather(city: str) -> dict:
    """Retrieves the current weather report for a specified city.

    Args:
        city (str): The name of the city (e.g., "New York", "London", "Tokyo").

    Returns:
        dict: A dictionary containing the weather information.
            Includes a 'status' key ('success' or 'error').
            If 'success', includes a 'report' key with weather details.
            If 'error', includes an 'error_message' key.
    """
    print(f"--- Tool: get_weather called for city: {city} ---") # Log tool execution
    city_normalized = city.lower().replace(" ", "") # Basic normalization



    if city_normalized in mock_weather_db:
        return mock_weather_db[city_normalized]
    else:
        return {"status": "error", "error_message": f"Sorry, I don't have weather information for '{city}'."}

# @title Define the get_current_time Tool
def get_current_time(city: str) -> dict:
    """ Get the current time for a given city.
    Args:
        city (str): The name of the city to get the current time for.
    Returns: 
        dict: status and result or error message.
    """
    if city.lower() == "paris":
        tz_identifier = "Europe/Paris"
    else:
        return {
            "status": "error",
            "error_message": (f"Sorry, I don't have timezone information for {city}.")
        }

    tz = ZoneInfo(tz_identifier)
    now = datetime.datetime.now(tz)
    report = (
        f'The current time in {city} is {now.strftime("%Y-%m-%d %H:%M:%S %Z%z")}'
    )
    return {"status": "success", "report": report}


# @title Define Tools for Greetin and Farewell Agents
def say_hello(name: Optional[str] = None) -> str:
    """Returns a greeting message. If a name is provided, it personalizes the greeting.
    Args:
        name (Optional[str]): The name to include in the greeting. Defaults to None.
    Returns:
        str: A grateful greeting message.
    """
    if name:
        gretting = f"Hello, {name}!"
        print(f"--- Tool: say_hello called with name: {name} ---")  # Log tool execution
    else:
        gretting = "Ey SinNombre!" # Default greeting if no name is provided
        print("--- Tool: say_hello called without name ---") 
    return gretting

def say_goodbye(name: Optional[str] = None) -> str:
    """Returns a farewell message. If a name is provided, it personalizes the farewell.
    Args:
        name (Optional[str]): The name to include in the farewell. Defaults to None.
    Returns:
        str: A farewell message.
    """
    if name:
        farewell = f"Goodbye, {name}!"
        print(f"--- Tool: say_goodbye called with name: {name} ---")  # Log tool execution
    else:
        farewell = "Adios SinNombre!"  # Default farewell if no name is provided
        print("--- Tool: say_goodbye called without name ---")
    return farewell
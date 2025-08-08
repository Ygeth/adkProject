import datetime
from zoneinfo import ZoneInfo
from typing import Optional

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

# @title Define the get_weather Tool
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
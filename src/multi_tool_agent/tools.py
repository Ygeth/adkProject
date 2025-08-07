import datetime
from zoneinfo import ZoneInfo

# Mock weather data
mock_weather_db = {
      "newyork": {"status": "success", "report": "The weather in New York is sunny with a temperature of 25°C."},
      "london": {"status": "success", "report": "It's cloudy in London with a temperature of 15°C."},
      "tokyo": {"status": "success", "report": "Tokyo is experiencing light rain and a temperature of 18°C."},
  }

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
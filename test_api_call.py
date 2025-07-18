import requests
import json

def test_zone_api():
    """Calls the zone API and prints the response."""
    url = "http://localhost:5001/api/v1/zones"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes
        data = response.json()
        print(json.dumps(data, indent=4))
    except requests.exceptions.RequestException as e:
        print(f"Error calling the API: {e}")

if __name__ == "__main__":
    test_zone_api()

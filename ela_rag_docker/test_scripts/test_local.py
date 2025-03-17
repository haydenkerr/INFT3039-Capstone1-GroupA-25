import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

def test_query_endpoint(query_text: str, api_key: str = None):
    """
    Tests the /query endpoint of the FastAPI application.

    Args:
        query_text: The text to query the system with.
        api_key: The API key for authentication. If None, it will try to get it from environment variable.

    Returns:
        The response from the API, or None if an error occurred.
    """
    url = 'http://localhost:8001/query'  # Assuming the app is running locally on port 8000
    headers = {}
    if api_key:
        headers["x-api-key"] = api_key
    else:
        # api_key = os.getenv("API_KEY")
        api_key = "1234abcd"
        if api_key:
            headers["x-api-key"] = api_key
        else:
            print("Error: API_KEY not provided and not found in environment variables.")
            return None

    data = {
        "query_text": query_text
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error during request: {e}")
        if response is not None:
            print(f"Response content: {response.text}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON response: {e}")
        if response is not None:
            print(f"Response content: {response.text}")
        return None


# Example usage:
if __name__ == "__main__":
    # Example 1: Using API key from environment variable
    query = "Explain the project scope?"
    result = test_query_endpoint(query)
    if result:
        print("Response (using env var API_KEY):")
        print(json.dumps(result, indent=2))
        

    # # Example 2: Providing API key directly
    # query = "Tell me about water treatment."
    # api_key_to_use = os.getenv("API_KEY") # or replace with your actual key
    # result = test_query_endpoint(query, api_key=api_key_to_use)
    # if result:
    #     print("\nResponse (using provided API key):")
    #     print(json.dumps(result, indent=2))
    
    # # Example 3: No API key provided
    # query = "Tell me about water treatment."
    # result = test_query_endpoint(query, api_key=None)
    # if result:
    #     print("\nResponse (using provided API key):")
    #     print(json.dumps(result, indent=2))

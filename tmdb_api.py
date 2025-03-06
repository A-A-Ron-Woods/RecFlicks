# Import necessary libraries
import requests  # Used to make HTTP requests to the TMDB API
import os  # Used to handle environment variables
from dotenv import load_dotenv  # Used to load environment variables from a .env file

# Load environment variables from a .env file
load_dotenv()

# Retrieve the API key from the .env file
API_KEY = os.getenv("IMDB_API_KEY")

# Debugging check to ensure the API key is loaded
if not API_KEY:
    print("⚠️ Warning: API Key not loaded. Check .env file!")  # Warning message if API key is missing

def fetch_movie_data(title):
    """
    Fetches movie details (poster and overview) from The Movie Database (TMDB) API.

    Parameters:
        title (str): The title of the movie to search for.

    Returns:
        dict: A dictionary containing the movie poster URL and overview if found, otherwise None.
    """
    # Check if the API key is available before making the request
    if not API_KEY:
        print("⚠️ Error: No API Key. Unable to fetch movie data.")  # Error message if API key is missing
        return None

    # Construct the API request URL for searching movies by title
    url = f"https://api.themoviedb.org/3/search/movie?api_key={API_KEY}&query={title}"

    try:
        # Make a GET request to the TMDB API
        response = requests.get(url)
        response.raise_for_status()  # Raise an HTTP error if the response status is not 200

        # Parse the JSON response
        data = response.json()

        # Check if the response contains movie results
        if 'results' in data and data['results']:
            movie = data['results'][0]  # Select the first movie from the search results

            # Return a dictionary with the movie poster URL and overview
            return {
                "poster": f"https://image.tmdb.org/t/p/w500{movie.get('poster_path', '')}",  # Construct the poster URL
                "overview": movie.get('overview', 'No description available.')  # Get the movie overview
            }
    
    except requests.exceptions.RequestException as e:
        # Handle potential request errors (e.g., network issues, invalid API key, etc.)
        print(f"API Request Error: {e}")

    # Return None if no movie data is found
    return None

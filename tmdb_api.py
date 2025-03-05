import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
API_KEY = os.getenv("IMDB_API_KEY")

# Debugging check
if not API_KEY:
    print("⚠️ Warning: API Key not loaded. Check .env file!")

def fetch_movie_data(title):
    if not API_KEY:
        print("⚠️ Error: No API Key. Unable to fetch movie data.")
        return None

    url = f"https://api.themoviedb.org/3/search/movie?api_key={API_KEY}&query={title}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        if 'results' in data and data['results']:
            movie = data['results'][0]
            return {
                "poster": f"https://image.tmdb.org/t/p/w500{movie.get('poster_path', '')}",
                "overview": movie.get('overview', 'No description available.')
            }
    except requests.exceptions.RequestException as e:
        print(f"API Request Error: {e}")
    
    return None

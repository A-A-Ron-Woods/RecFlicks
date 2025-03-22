import requests
import os
from dotenv import load_dotenv

# Load API key from environment variables
load_dotenv()
API_KEY = os.getenv("IMDB_API_KEY")

def fetch_movie_data(title, release_year=None, local_overview=None):
    """
    Fetches movie details (poster & overview) from the TMDB API.
    Falls back to local overview if necessary.

    Parameters:
        title: The movie title to search for.
        release_year: (Optional) Release year to improve matching accuracy.
        local_overview: (Optional) Fallback text to use if API overview is missing.

    Returns:
        Dictionary with 'poster' and 'overview'.
    """
    if not API_KEY:
        print("⚠️ No API Key. Using fallback data.")
        return {
            "poster": None,
            "overview": local_overview or "No description available."
        }

    params = {
        "api_key": API_KEY,
        "query": title,
    }
    if release_year:
        params["year"] = release_year

    url = "https://api.themoviedb.org/3/search/movie"
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        if data.get('results'):
            # Try to match title and year closely
            exact_matches = [
                movie for movie in data['results']
                if movie['title'].lower() == title.lower() and
                   (not release_year or str(movie.get('release_date', '')).startswith(str(release_year)))
            ]
            movie = exact_matches[0] if exact_matches else data['results'][0]

            poster_url = f"https://image.tmdb.org/t/p/w500{movie.get('poster_path', '')}" if movie.get('poster_path') else None
            overview_text = movie.get('overview', '').strip()

            return {
                "poster": poster_url,
                "overview": overview_text if overview_text else (local_overview or "No description available.")
            }

    except requests.exceptions.RequestException as e:
        print(f"API Request Error: {e}")

    return {
        "poster": None,
        "overview": local_overview or "No description available."
    }

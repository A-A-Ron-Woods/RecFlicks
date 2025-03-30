import requests
import random
import streamlit as st

# Load API from config.toml file
API_KEY = st.secrets["api"]["tmdb_key"]

def fetch_movie_data(title, release_year=None, local_overview=None):
    """
    Fetches movie details (poster & overview and trailer) from the TMDB API.
    Falls back to local overview if necessary.
    """
    if not API_KEY:
        print("⚠️ No API Key. Using fallback data.")
        return {
            "poster": None,
            "overview": local_overview or "No description available.",
            "trailer": None,
            "reviews_link": None
        }

    params = {
        "api_key": API_KEY,
        "query": title,
        "include_adult": "false",
    }
    if release_year:
        params["year"] = release_year

    url = "https://api.themoviedb.org/3/search/movie"
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        if data.get('results'):
            exact_matches = [
                movie for movie in data['results']
                if movie['title'].lower() == title.lower() and
                   (not release_year or str(movie.get('release_date', '')).startswith(str(release_year)))
            ]
            movie = exact_matches[0] if exact_matches else data['results'][0]
            movie_id = movie['id']

            poster_url = f"https://image.tmdb.org/t/p/w500{movie.get('poster_path', '')}" if movie.get('poster_path') else None
            overview_text = movie.get('overview', '').strip()

            # Fetch movie trailer
            trailer_url = fetch_movie_trailer(movie_id)

            #Create link to movie reviews
            reviews_link = f"https://www.themoviedb.org/movie/{movie_id}/reviews"

            return {
                "poster": poster_url,
                "overview": overview_text if overview_text else (local_overview or "No description available."),
                "trailer": trailer_url,
                "reviews_link": reviews_link
            }

    except requests.exceptions.RequestException as e:
        print(f"API Request Error: {e}")

    return {
        "poster": None,
        "overview": local_overview or "No description available.",
        "trailer": None,
        "reviews_link": None
    }

def fetch_movie_trailer(movie_id):
    """
    Fetches official trailer from TMDb API
    """
    url = f"https://api.themoviedb.org/3/movie/{movie_id}/videos"
    params = {
        "api_key": API_KEY,
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        videos = response.json().get("results", [])

        for video in videos:
            if video['type'] == 'Trailer' and video['site'] == 'YouTube':
                return f"https://www.youtube.com/watch?v={video['key']}"
    except requests.exceptions.RequestException as e:
        print(f"Error fetching trailer: {e}")

    return None

def fetch_random_movie_by_year(year):
    """
    Fetch a random movie's poster and title from TMDb for a specific year.
    """
    if not API_KEY:
        return {"title": None, "poster": None}

    url = "https://api.themoviedb.org/3/discover/movie"
    params = {
        "api_key": API_KEY,
        "primary_release_year": year,
        "sort_by": "popularity.desc",
        "include_adult": "false",
        "page": random.randint(1, 5)  # Randomize the page to get variation
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        results = response.json().get("results", [])

        if results:
            movie = random.choice(results)
            poster_url = f"https://image.tmdb.org/t/p/w500{movie.get('poster_path')}" if movie.get('poster_path') else None
            return {
                "title": movie.get('title', 'Unknown'),
                "poster": poster_url
            }

    except requests.RequestException as e:
        print(f"Error fetching random movie: {e}")
    
    return {"title": None, "poster": None}
import pandas as pd  # Pandas for handling tabular data
from sklearn.feature_extraction.text import TfidfVectorizer  # TF-IDF Vectorizer for text processing
from sklearn.metrics.pairwise import cosine_similarity  # Cosine similarity for measuring movie similarity
import os  # OS module for handling file paths

# Load dataset globally to avoid reloading it multiple times (improves efficiency)
csv_path = os.path.join(os.path.dirname(__file__), "tmdb_movies_data.csv")  # Construct the absolute path to the CSV file
movies = pd.read_csv(csv_path)  # Load the dataset into a DataFrame

# Rename columns for consistency and better readability
movies.rename(columns={
    'original_title': 'title',  # Renaming original_title to title
    'release_year': 'year',  # Renaming release_year to year
    'vote_average': 'rating',  # Renaming vote_average to rating
    'genres': 'genre'  # Renaming genres to genre
}, inplace=True)

# Handle missing values to prevent errors in data processing
movies['overview'] = movies['overview'].fillna('')  # Fill missing overviews with an empty string
movies = movies.dropna(subset=['title', 'year', 'rating', 'genre'])  # Remove rows with missing critical values

def get_recommendations(genre, year_range):
    """
    Returns movie recommendations based on genre and year range.

    Parameters:
        genre (str): The selected movie genre (or "Any" for all genres).
        year_range (tuple): A tuple containing (start_year, end_year) to filter movies by release year.

    Returns:
        pd.DataFrame: A DataFrame containing the top 10 movies based on rating.
    """
    start_year, end_year = year_range  # Unpack the year range tuple

    # Make a copy of the dataset to avoid modifying the original
    filtered_movies = movies.copy()

    # Map "Sci-Fi" to "Science Fiction" to match the dataset
    genre_mapping = {
        "Sci-Fi": "Science Fiction"
    }
    genre = genre_mapping.get(genre, genre)  # Replace genre if mapped

    # If a specific genre is selected, filter movies that contain the genre (case-insensitive)
    if genre != "Any":
        filtered_movies = filtered_movies[filtered_movies['genre'].str.contains(genre, case=False, na=False)]

    # Filter movies based on the selected release year range
    filtered_movies = filtered_movies[(filtered_movies['year'] >= start_year) & (filtered_movies['year'] <= end_year)]

    # If no movies match the filters, print a message and return an empty DataFrame
    if filtered_movies.empty:
        print(f"No movies found for genre '{genre}' between {start_year} and {end_year}.")
        return pd.DataFrame()

    # Return the top 10 highest-rated movies sorted in descending order
    return filtered_movies.sort_values(by='rating', ascending=False).head(10)

def recommend_similar_movies(movie_title):
    """
    Returns movie recommendations similar to the given title using machine learning.

    Parameters:
        movie_title (str): The title of the movie for which similar movies should be recommended.

    Returns:
        pd.DataFrame: A DataFrame containing the top 10 most similar movies based on the overview text.
    """
    # Check if the given movie title exists in the dataset
    if movie_title not in movies['title'].values:
        print(f"Movie '{movie_title}' not found in dataset.")
        return pd.DataFrame()

    # Use TF-IDF Vectorization on movie overviews to transform text into numerical data
    tfidf = TfidfVectorizer(stop_words='english')  # Remove common English stopwords
    tfidf_matrix = tfidf.fit_transform(movies['overview'])  # Convert the 'overview' text into TF-IDF vectors

    # Compute cosine similarity between all movies in the dataset
    similarity_matrix = cosine_similarity(tfidf_matrix, tfidf_matrix)

    # Get the index of the movie that matches the given title
    movie_idx = movies[movies['title'] == movie_title].index[0]

    # Get the similarity scores for all movies compared to the given movie
    similarity_scores = list(enumerate(similarity_matrix[movie_idx]))

    # Sort the movies by similarity score in descending order (higher similarity first)
    similarity_scores = sorted(similarity_scores, key=lambda x: x[1], reverse=True)

    # Get the indices of the top 10 most similar movies (excluding the selected movie itself)
    similar_movie_indices = [i[0] for i in similarity_scores[1:11]]  # Skip the first one (itself)

    # Return the top 10 most similar movies with title, year, rating, and overview
    return movies.iloc[similar_movie_indices][['title', 'year', 'rating', 'overview']]

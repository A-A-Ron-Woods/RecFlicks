import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os

# Load and clean the movie dataset
movies = pd.read_csv(os.path.join(os.path.dirname(__file__), "tmdb_movies_data.csv"))
movies.rename(columns={'original_title': 'title', 'release_year': 'year', 'vote_average': 'rating'}, inplace=True)
movies['overview'].fillna('', inplace=True)
movies.dropna(subset=['title', 'year', 'rating', 'genres'], inplace=True)

def get_recommendations(genre, year_range):
    """
    Filters and returns top-rated movies based on the selected genre and release year range.
    
    Parameters:
        genre (str): Selected genre (or "Any" for all genres).
        year_range (tuple): Range of release years (start, end).

    Returns:
        pd.DataFrame: Top 10 highest-rated movies matching the criteria.
    """
    start_year, end_year = year_range
    filtered_movies = movies[movies['year'].between(start_year, end_year)]

    if genre != "Any":
        filtered_movies = filtered_movies[filtered_movies['genres'].str.contains(genre, case=False, na=False)]

    return filtered_movies.sort_values(by='rating', ascending=False).head(10)

def recommend_similar_movies(movie_title):
    """
    Finds movies similar to a given title based on text similarity of movie overviews.

    Parameters:
        movie_title (str): The title of the movie to find similar recommendations.

    Returns:
        pd.DataFrame: Top 10 most similar movies.
    """
    if movie_title not in movies['title'].values:
        return pd.DataFrame()

    # Convert movie descriptions into numerical feature vectors
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(movies['overview'])

    # Compute similarity scores between all movies
    similarity_matrix = cosine_similarity(tfidf_matrix, tfidf_matrix)

    # Find the index of the selected movie
    movie_idx = movies[movies['title'] == movie_title].index[0]
    similarity_scores = sorted(enumerate(similarity_matrix[movie_idx]), key=lambda x: x[1], reverse=True)

    # Retrieve the most similar movies (excluding the selected movie itself)
    similar_movie_indices = [i[0] for i in similarity_scores[1:11]]

    return movies.iloc[similar_movie_indices][['title', 'year', 'rating', 'overview']]

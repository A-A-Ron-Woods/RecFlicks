import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os

# Load dataset globally (to avoid loading it multiple times)
csv_path = os.path.join(os.path.dirname(__file__), "tmdb_movies_data.csv")
movies = pd.read_csv(csv_path)

# Rename columns for consistency
movies.rename(columns={
    'original_title': 'title',
    'release_year': 'year',
    'vote_average': 'rating',
    'genres': 'genre'
}, inplace=True)

# Handle missing values
movies['overview'] = movies['overview'].fillna('')
movies = movies.dropna(subset=['title', 'year', 'rating', 'genre'])

def get_recommendations(genre, year_range):
    """ Returns movie recommendations based on genre and year range. """
    start_year, end_year = year_range  # Unpack tuple

    filtered_movies = movies.copy()
    if genre != "Any":
        filtered_movies = filtered_movies[filtered_movies['genre'].str.contains(genre, case=False, na=False)]
    
    filtered_movies = filtered_movies[(filtered_movies['year'] >= start_year) & (filtered_movies['year'] <= end_year)]

    if filtered_movies.empty:
        print(f"No movies found for genre '{genre}' between {start_year} and {end_year}.")
        return pd.DataFrame()

    return filtered_movies.sort_values(by='rating', ascending=False).head(10)

def recommend_similar_movies(movie_title):
    """ Returns movie recommendations similar to the given title using ML. """
    if movie_title not in movies['title'].values:
        print(f"Movie '{movie_title}' not found in dataset.")
        return pd.DataFrame()

    # Use TF-IDF Vectorization on movie overviews
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(movies['overview'])

    # Compute cosine similarity between all movies
    similarity_matrix = cosine_similarity(tfidf_matrix, tfidf_matrix)

    # Get the index of the given movie
    movie_idx = movies[movies['title'] == movie_title].index[0]

    # Get similarity scores and sort them
    similarity_scores = list(enumerate(similarity_matrix[movie_idx]))
    similarity_scores = sorted(similarity_scores, key=lambda x: x[1], reverse=True)

    # Get indices of top 10 most similar movies (excluding itself)
    similar_movie_indices = [i[0] for i in similarity_scores[1:11]]

    return movies.iloc[similar_movie_indices][['title', 'year', 'rating', 'overview']]

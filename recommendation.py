import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler
import os

# Load and clean the dataset
movies = pd.read_csv(os.path.join(os.path.dirname(__file__), "tmdb_movies_data.csv"))
movies = movies[['original_title', 'release_year', 'cast', 'keywords', 'overview', 'genres', 'vote_count', 'vote_average']]
movies.dropna(inplace=True)
movies['release_year'] = pd.to_numeric(movies['release_year'], errors='coerce')

# Normalize vote count to give weight to more popular movies
scaler = MinMaxScaler()
movies['votes_scaled'] = scaler.fit_transform(movies[['vote_count']])
movies['weighted_rating'] = movies['vote_average'] * movies['votes_scaled']

# Ensure lists are properly split from '|' separator
for feature in ['genres', 'keywords', 'cast']:
    movies[feature] = movies[feature].apply(lambda x: x.split('|') if isinstance(x, str) else [])

def get_recommendations(genre, year_range):
    """
    Filters and returns top-rated movies based on the selected genre and release year range.
    """
    start_year, end_year = year_range
    filtered_movies = movies[movies['release_year'].between(start_year, end_year, inclusive='both')]
    
    if genre != "Any":
        filtered_movies = filtered_movies[filtered_movies['genres'].apply(lambda x: genre in x)]
    
    if 'weighted_rating' not in filtered_movies.columns:
        filtered_movies['weighted_rating'] = 0
    
    return filtered_movies.sort_values(by='weighted_rating', ascending=False).head(10)

def recommend_similar_movies(movie_title):
    """
    Finds movies similar to a given title based on genre, keywords, and overview similarity.
    """
    if movie_title not in movies['original_title'].values:
        return pd.DataFrame(columns=['original_title', 'release_year', 'vote_average', 'vote_count', 'overview', 'reason_for_recommendation'])
    
    # Get the target movie data
    target_movie = movies[movies['original_title'] == movie_title].iloc[0]
    target_genres = set(target_movie['genres'])
    
    # Filter movies to ensure at least one genre matches
    filtered_movies = movies[movies['genres'].apply(lambda x: bool(set(x) & target_genres))].reset_index(drop=True)
    
    # TF-IDF Vectorization for overview and keywords
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(filtered_movies['overview'] + filtered_movies['keywords'].apply(lambda x: ' '.join(x)))
    
    # Compute similarity
    similarity_matrix = cosine_similarity(tfidf_matrix, tfidf_matrix)
    movie_idx = filtered_movies[filtered_movies['original_title'] == movie_title].index[0]
    similarity_scores = list(enumerate(similarity_matrix[movie_idx]))
    similarity_scores = sorted(similarity_scores, key=lambda x: x[1], reverse=True)
    
    # Select 10 top similar movies (Excludes movie itself)
    similar_movie_indices = [i[0] for i in similarity_scores[1:11] if i[0] < len(filtered_movies)]
    recommended_movies = filtered_movies.iloc[similar_movie_indices].reset_index(drop=True)
    
    # Generate reason for recommendation
    reasons = []
    for _, rec_movie in recommended_movies.iterrows():
        shared_features = []
        
        # Ensure lists are properly formatted
        rec_keywords = set(rec_movie['keywords']) if isinstance(rec_movie['keywords'], list) else set()
        rec_cast = set(rec_movie['cast']) if isinstance(rec_movie['cast'], list) else set()
        target_keywords = set(target_movie['keywords']) if isinstance(target_movie['keywords'], list) else set()
        target_cast = set(target_movie['cast']) if isinstance(target_movie['cast'], list) else set()
        
        # Compare shared features
        shared_keywords = target_keywords & rec_keywords
        shared_cast = target_cast & rec_cast
        
        if shared_keywords:
            shared_features.append(f"Shared keywords: {', '.join(shared_keywords)}")
        if shared_cast:
            shared_features.append(f"Shared cast: {', '.join(shared_cast)}")
        
        reasons.append("; ".join(shared_features) if shared_features else "Similar themes and genres")
    
    # Add reasons and return results sorted by weighted rating
    recommended_movies['reason_for_recommendation'] = reasons
    return recommended_movies.sort_values(by='weighted_rating', ascending=False).head(10)[['original_title', 'release_year', 'vote_average', 'vote_count', 'overview', 'reason_for_recommendation']]

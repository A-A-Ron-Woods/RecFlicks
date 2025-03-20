import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler
from sklearn.decomposition import TruncatedSVD
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

def jaccard_similarity(set1, set2):
    """Compute Jaccard similarity between two sets."""
    if not set1 or not set2:
        return 0
    return len(set1 & set2) / len(set1 | set2)

def recommend_similar_movies(movie_title, tfidf_weight=0.7, cast_weight=0.3):
    """
    Finds movies similar to a given title using SVD on TF-IDF vectors and cast similarity.
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
    
    # Apply Truncated SVD to reduce dimensions
    svd = TruncatedSVD(n_components=100)  # Experiment with different values
    reduced_matrix = svd.fit_transform(tfidf_matrix)
    
    # Compute TF-IDF similarity in reduced space
    similarity_matrix = cosine_similarity(reduced_matrix, reduced_matrix)
    
    # Find movie index in filtered dataset
    movie_idx = filtered_movies[filtered_movies['original_title'] == movie_title].index[0]
    similarity_scores = list(enumerate(similarity_matrix[movie_idx]))
    
    # Compute cast similarity for all filtered movies
    target_cast = set(target_movie['cast']) if isinstance(target_movie['cast'], list) else set()
    cast_similarities = []
    
    for idx, rec_movie in filtered_movies.iterrows():
        rec_cast = set(rec_movie['cast']) if isinstance(rec_movie['cast'], list) else set()
        cast_similarities.append((idx, jaccard_similarity(target_cast, rec_cast)))
    
    # Normalize cast similarities to the same scale as cosine similarity
    max_cast_sim = max([sim[1] for sim in cast_similarities]) if cast_similarities else 1
    cast_similarities = [(idx, sim / max_cast_sim) for idx, sim in cast_similarities]

    # Merge TF-IDF and cast similarities into a final score
    cast_sim_dict = dict(cast_similarities)
    final_scores = [(idx, tfidf_weight * tfidf_sim + cast_weight * cast_sim_dict.get(idx, 0)) 
                    for idx, tfidf_sim in similarity_scores]
    
    # Sort by final similarity score
    final_scores = sorted(final_scores, key=lambda x: x[1], reverse=True)
    
    # Select top 10 similar movies (Excludes movie itself)
    similar_movie_indices = [i[0] for i in final_scores[1:11] if i[0] < len(filtered_movies)]
    recommended_movies = filtered_movies.iloc[similar_movie_indices].reset_index(drop=True)
    
    # Generate reason for recommendation
    reasons = []
    for _, rec_movie in recommended_movies.iterrows():
        shared_features = []
        
        rec_keywords = set(rec_movie['keywords']) if isinstance(rec_movie['keywords'], list) else set()
        rec_cast = set(rec_movie['cast']) if isinstance(rec_movie['cast'], list) else set()
        target_keywords = set(target_movie['keywords']) if isinstance(target_movie['keywords'], list) else set()
        
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
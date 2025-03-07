import streamlit as st
import pandas as pd
from recommendation import get_recommendations, recommend_similar_movies
from tmdb_api import fetch_movie_data

# Load movie dataset and extract unique genres
movies_df = pd.read_csv("tmdb_movies_data.csv")
genre_options = ["Any"] + sorted(set(g for genres in movies_df['genres'].dropna() for g in genres.split('|')))

def main():
    """Runs the Streamlit app for movie recommendations."""
    st.title("RecFlicks")
    
    # Select recommendation method
    recommendation_type = st.radio("Choose a recommendation type:", ("Recommend by Genre & Year", "Recommend Similar Movies"))

    if recommendation_type == "Recommend by Genre & Year":
        # Sidebar filters for genre and release year
        st.sidebar.header("Filter Movies")
        genre = st.sidebar.selectbox("Choose Genre", genre_options)
        year_range = st.sidebar.slider("Release Year Range", 1980, 2025, (2000, 2015))

        # Fetch and display movie recommendations
        if st.button("Get Recommendations"):
            recommendations = get_recommendations(genre, year_range)
            if recommendations.empty:
                st.warning("No recommendations found. Try different filters.")
            else:
                st.subheader("Recommended Movies:")
                for _, row in recommendations.iterrows():
                    movie_details = fetch_movie_data(row['title'])
                    st.subheader(f"{row['title']} ({row['year']})")
                    if movie_details:
                        st.image(movie_details['poster'], width=200)
                        st.write(movie_details['overview'])
                    else:
                        st.write("No additional info available.")

    elif recommendation_type == "Recommend Similar Movies":
        # Input field for entering a movie title
        movie_input = st.text_input("Enter a favorite movie to get similar recommendations")
        
        # Fetch and display similar movie recommendations
        if st.button("Get Similar Movies") and movie_input:
            similar_movies = recommend_similar_movies(movie_input)
            if similar_movies.empty:
                st.warning("No similar movies found. Try another title.")
            else:
                st.subheader(f"Movies similar to: {movie_input}")
                for _, row in similar_movies.iterrows():
                    movie_details = fetch_movie_data(row['title'])
                    st.subheader(f"{row['title']} ({row['year']})")
                    if movie_details:
                        st.image(movie_details['poster'], width=200)
                        st.write(movie_details['overview'])
                    else:
                        st.write("No additional info available.")

if __name__ == "__main__":
    main()

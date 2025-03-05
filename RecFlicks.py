import streamlit as st
import pandas as pd
from recommendation import get_recommendations, recommend_similar_movies
from tmdb_api import fetch_movie_data

def main():
    st.title("RecFlicks")

    # User selects recommendation type
    recommendation_type = st.radio(
        "Choose a recommendation type:",
        ("Recommend by Genre & Year", "Recommend Similar Movies")
    )

    if recommendation_type == "Recommend by Genre & Year":
        # Show inputs for genre and year range
        st.sidebar.header("Filter Movies")
        genre = st.sidebar.selectbox("Choose Genre", ["Any", "Action", "Comedy", "Drama", "Sci-Fi", "Horror"])
        year_range = st.sidebar.slider("Release Year Range", 1980, 2025, (2000, 2015))

        if st.button("Get Recommendations"):
            recommendations = get_recommendations(genre, year_range)

            if recommendations.empty:
                st.warning("No recommendations found. Try different filters.")
            else:
                st.subheader("Recommended Movies:")
                for index, row in recommendations.iterrows():
                    movie_details = fetch_movie_data(row['title'])

                    if movie_details:
                        st.subheader(f"{row['title']} ({row['year']})")
                        st.image(movie_details['poster'], width=200)
                        st.write(movie_details['overview'])
                    else:
                        st.write(f"{row['title']} ({row['year']}) - No additional info available.")

    elif recommendation_type == "Recommend Similar Movies":
        # Show input for movie title
        movie_input = st.text_input("Enter a favorite movie to get similar recommendations")

        if st.button("Get Similar Movies"):
            if not movie_input:
                st.warning("Please enter a movie name to get recommendations.")
            else:
                similar_movies = recommend_similar_movies(movie_input)

                if similar_movies.empty:
                    st.warning("No similar movies found. Try another title.")
                else:
                    st.subheader(f"Movies similar to: {movie_input}")
                    for index, row in similar_movies.iterrows():
                        movie_details = fetch_movie_data(row['title'])

                        if movie_details:
                            st.subheader(f"{row['title']} ({row['year']})")
                            st.image(movie_details['poster'], width=200)
                            st.write(movie_details['overview'])
                        else:
                            st.write(f"{row['title']} ({row['year']}) - No additional info available.")

if __name__ == "__main__":
    main()

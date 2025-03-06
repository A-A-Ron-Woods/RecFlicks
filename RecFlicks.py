# Import necessary libraries
import streamlit as st  # Streamlit for creating the web app UI
import pandas as pd  # Pandas for handling tabular data
from recommendation import get_recommendations, recommend_similar_movies  # Importing custom recommendation functions
from tmdb_api import fetch_movie_data  # Function to fetch movie details from TMDB API

# Define the main function that runs the Streamlit app
def main():
    # Set the title of the app
    st.title("RecFlicks")

    # Create a radio button for selecting the recommendation type
    recommendation_type = st.radio(
        "Choose a recommendation type:",  # Label for the radio button
        ("Recommend by Genre & Year", "Recommend Similar Movies")  # Options to choose from
    )

    # If the user selects "Recommend by Genre & Year"
    if recommendation_type == "Recommend by Genre & Year":
        # Create a sidebar section for filtering movies
        st.sidebar.header("Filter Movies")
        
        # Dropdown to select movie genre
        genre = st.sidebar.selectbox(
            "Choose Genre",  # Label for the dropdown
            ["Any", "Action", "Comedy", "Drama", "Sci-Fi", "Horror"]  # List of genres to choose from
        )
        
        # Slider to select the release year range (default 2000-2015)
        year_range = st.sidebar.slider(
            "Release Year Range",  # Label for the slider
            1980,  # Minimum year
            2025,  # Maximum year
            (2000, 2015)  # Default range
        )

        # Button to fetch recommendations based on selected filters
        if st.button("Get Recommendations"):
            # Call function to get movie recommendations
            recommendations = get_recommendations(genre, year_range)

            # If no recommendations are found, display a warning message
            if recommendations.empty:
                st.warning("No recommendations found. Try different filters.")
            else:
                # Display recommendations
                st.subheader("Recommended Movies:")
                
                # Iterate through the DataFrame and display each movie
                for index, row in recommendations.iterrows():
                    # Fetch additional movie details (poster, overview) from TMDB API
                    movie_details = fetch_movie_data(row['title'])

                    # If details are available, display them
                    if movie_details:
                        st.subheader(f"{row['title']} ({row['year']})")  # Movie title and year
                        st.image(movie_details['poster'], width=200)  # Movie poster
                        st.write(movie_details['overview'])  # Movie description
                    else:
                        # If no additional info is available, display title and year only
                        st.write(f"{row['title']} ({row['year']}) - No additional info available.")

    # If the user selects "Recommend Similar Movies"
    elif recommendation_type == "Recommend Similar Movies":
        # Text input for user to enter a favorite movie title
        movie_input = st.text_input("Enter a favorite movie to get similar recommendations")

        # Button to get similar movie recommendations
        if st.button("Get Similar Movies"):
            # If no movie title is entered, show a warning message
            if not movie_input:
                st.warning("Please enter a movie name to get recommendations.")
            else:
                # Call function to fetch similar movies
                similar_movies = recommend_similar_movies(movie_input)

                # If no similar movies are found, display a warning
                if similar_movies.empty:
                    st.warning("No similar movies found. Try another title.")
                else:
                    # Display recommendations
                    st.subheader(f"Movies similar to: {movie_input}")
                    
                    # Iterate through the DataFrame and display each movie
                    for index, row in similar_movies.iterrows():
                        # Fetch additional movie details (poster, overview) from TMDB API
                        movie_details = fetch_movie_data(row['title'])

                        # If details are available, display them
                        if movie_details:
                            st.subheader(f"{row['title']} ({row['year']})")  # Movie title and year
                            st.image(movie_details['poster'], width=200)  # Movie poster
                            st.write(movie_details['overview'])  # Movie description
                        else:
                            # If no additional info is available, display title and year only
                            st.write(f"{row['title']} ({row['year']}) - No additional info available.")

# Ensure the main function runs when the script is executed directly
if __name__ == "__main__":
    main()

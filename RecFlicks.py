# Import necessary libraries
import streamlit as st  # Streamlit for creating the web app UI
import pandas as pd  # Pandas for handling tabular data
from recommendation import get_recommendations, recommend_similar_movies  # Importing recommendation functions
from tmdb_api import fetch_movie_data  # Function to fetch movie details from TMDB API

# Load dataset to extract valid genres
csv_path = "tmdb_movies_data.csv"  # Ensure the correct relative path to the dataset
movies_df = pd.read_csv(csv_path)  # Load the movie dataset into a DataFrame

# Extract unique individual genres from the dataset
unique_genres_set = set()  # Create an empty set to store unique genres
for genre_entry in movies_df['genres'].dropna():  # Drop missing values and iterate over genres
    genres = genre_entry.split('|')  # Split multi-genre strings into individual genres
    unique_genres_set.update(genres)  # Add each genre to the set

# Convert the genre set to a sorted list and add "Any" as the first option
sorted_unique_genres = sorted(unique_genres_set)  # Sort genres alphabetically
genre_options = ["Any"] + sorted_unique_genres  # Add "Any" as a default selection option

def main():
    """
    Main function that runs the Streamlit app.
    Allows users to select between two recommendation modes:
    1. "Recommend by Genre & Year" - Filters movies by genre and release year.
    2. "Recommend Similar Movies" - Uses ML to find similar movies based on an input title.
    """
    
    # Set the title of the app
    st.title("RecFlicks")

    # Radio button selection for recommendation type
    recommendation_type = st.radio(
        "Choose a recommendation type:",  # Label for the radio button
        ("Recommend by Genre & Year", "Recommend Similar Movies")  # Options to choose from
    )

    # If the user selects "Recommend by Genre & Year"
    if recommendation_type == "Recommend by Genre & Year":
        # Create a sidebar for movie filters
        st.sidebar.header("Filter Movies")
        
        # Dropdown to select movie genre (now dynamically generated from dataset)
        genre = st.sidebar.selectbox("Choose Genre", genre_options)

        # Slider to select the release year range (default 2000-2015)
        year_range = st.sidebar.slider(
            "Release Year Range",  # Label for the slider
            1980,  # Minimum year
            2025,  # Maximum year
            (2000, 2015)  # Default range
        )

        # Button to fetch recommendations based on selected filters
        if st.button("Get Recommendations"):
            recommendations = get_recommendations(genre, year_range)  # Call the function to get movie recommendations

            # If no recommendations are found, display a warning message
            if recommendations.empty:
                st.warning("No recommendations found. Try different filters.")
            else:
                # Display recommendations
                st.subheader("Recommended Movies:")
                
                # Iterate through the DataFrame and display each recommended movie
                for index, row in recommendations.iterrows():
                    movie_details = fetch_movie_data(row['title'])  # Fetch additional movie details from TMDB API

                    # If movie details are found, display them
                    if movie_details:
                        st.subheader(f"{row['title']} ({row['year']})")  # Movie title and release year
                        st.image(movie_details['poster'], width=200)  # Movie poster
                        st.write(movie_details['overview'])  # Movie description
                    else:
                        # If no additional info is available, display title and year only
                        st.write(f"{row['title']} ({row['year']}) - No additional info available.")

    # If the user selects "Recommend Similar Movies"
    elif recommendation_type == "Recommend Similar Movies":
        # Text input for user to enter a favorite movie title
        movie_input = st.text_input("Enter a favorite movie to get similar recommendations")

        # Button to fetch similar movie recommendations
        if st.button("Get Similar Movies"):
            # If no movie title is entered, show a warning message
            if not movie_input:
                st.warning("Please enter a movie name to get recommendations.")
            else:
                similar_movies = recommend_similar_movies(movie_input)  # Call the function to get similar movies

                # If no similar movies are found, display a warning
                if similar_movies.empty:
                    st.warning("No similar movies found. Try another title.")
                else:
                    # Display recommendations
                    st.subheader(f"Movies similar to: {movie_input}")
                    
                    # Iterate through the DataFrame and display each recommended movie
                    for index, row in similar_movies.iterrows():
                        movie_details = fetch_movie_data(row['title'])  # Fetch additional movie details from TMDB API

                        # If movie details are found, display them
                        if movie_details:
                            st.subheader(f"{row['title']} ({row['year']})")  # Movie title and release year
                            st.image(movie_details['poster'], width=200)  # Movie poster
                            st.write(movie_details['overview'])  # Movie description
                        else:
                            # If no additional info is available, display title and year only
                            st.write(f"{row['title']} ({row['year']}) - No additional info available.")

# Ensure the main function runs when the script is executed directly
if __name__ == "__main__":
    main()

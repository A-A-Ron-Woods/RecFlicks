import streamlit as st
import pandas as pd
from recommendation import get_recommendations, recommend_similar_movies
from tmdb_api import fetch_movie_data

# Initialize session state for navigation & recommendations
if "current_page" not in st.session_state:
    st.session_state["current_page"] = "home"
if "last_page" not in st.session_state:
    st.session_state["last_page"] = "home"
if "recommendations" not in st.session_state:
    st.session_state["recommendations"] = []
if "carousel_index" not in st.session_state:
    st.session_state["carousel_index"] = 0
if "recommend_triggered" not in st.session_state:
    st.session_state["recommend_triggered"] = False
if "selected_input" not in st.session_state:
    st.session_state["selected_input"] = "" 
if "selected_years" not in st.session_state:
    st.session_state["selected_years"] = ""

# Load movie dataset
movies_df = pd.read_csv("tmdb_movies_data.csv")
movie_titles = sorted(movies_df['original_title'].dropna().unique().tolist())

# Custom CSS - changing Font style, size, removing visual clutter
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Jolly+Lodger&display=swap');

    /* Apply font to all titles */
    h1 { 
        font-family: 'Jolly Lodger', cursive !important; 
        font-size: 80px !important;  /* Large font size */
        text-align: center !important; 
    }

    /* Reduce size of explanation text */
    .custom-text { 
        font-family: 'Jolly Lodger', cursive !important; 
        font-size: 30px !important;  /* Smaller than title */
        text-align: center !important; 
    }

    /* Remove Streamlit's automatic hover link icons */
    header a, h1 a, h2 a, h3 a, h4 a {
        text-decoration: none !important;
        pointer-events: none !important;
        display: none !important;
    }

    /* Ensure no underline or hover effects */
    a:hover, button:hover { text-decoration: none !important; }
    .stButton>button { border-radius: 8px !important; }
    </style>
    """,
    unsafe_allow_html=True
)

def navigate_to(page):
    """
    Update session state to move between pages of the app.
    Resets the recommendation trigger each time navigation occurs.
    """
    st.session_state["last_page"] = st.session_state["current_page"]
    st.session_state["current_page"] = page
    st.session_state["recommend_triggered"] = False

# Main function
def main():
    
    #--------------- Home Page
    if st.session_state["current_page"] == "home":
        st.title("RecFlicks 🎬")

        st.markdown(
            '<p class="custom-text">Welcome to RecFlicks – your movie recommendation buddy! '
            'Whether you know what kind of movie you like or want something similar to a favorite, '
            'we’ve got your next watch covered. *Uses TMDb dataset/API*</p>',
            unsafe_allow_html=True
        )
        
        st.write("Choose how you'd like to get movie recommendations.")
        
        col1, col2 = st.columns(2)
        with col1:
            st.button("🔍 Recommend by Genre & Year", on_click=lambda: navigate_to("recommend_genre"))
        with col2:
            st.button("🎥 Recommend by Similar Movie", on_click=lambda: navigate_to("recommend_similar"))

    # -----------------------Recommend by Genre & Year Page
    elif st.session_state["current_page"] == "recommend_genre":
        col1, col2 = st.columns([1, 5])
        with col1:
            st.button("🏠 Home", on_click=lambda: navigate_to("home"))
        with col2:
            st.button("🔙 Back", on_click=lambda: navigate_to("home"))

        st.title("🎭 Pick a Genre & Year Range")
        genre_options = ["Any"] + sorted(set(g for genres in movies_df['genres'].dropna() for g in genres.split('|')))
        genre = st.selectbox("Choose Genre", genre_options)
        year_range = st.slider("Release Year Range", 1980, 2025, (2000, 2015))

        if st.button("Get Recommendations") and not st.session_state["recommend_triggered"]:
            st.session_state["recommend_triggered"] = True
            st.session_state["recommendations"] = get_recommendations(genre, year_range).to_dict(orient="records")
            st.session_state["carousel_index"] = 0
            st.session_state["selected_input"] = f"{genre} genre" if genre != "Any" else "various genres"
            st.session_state["selected_years"] = f"{year_range[0]} - {year_range[1]}"
            navigate_to("results")
            st.rerun()

    # ------------------------------Recommend by Similar Movie Page
    elif st.session_state["current_page"] == "recommend_similar":
        col1, col2 = st.columns([1, 5])
        with col1:
            st.button("🏠 Home", on_click=lambda: navigate_to("home"))
        with col2:
            st.button("🔙 Back", on_click=lambda: navigate_to("home"))

        st.title("🔍 Find Similar Movies")
        movie_input = st.selectbox("Start typing a movie name...", movie_titles, index=None, placeholder="Type here...")

        if movie_input and st.button("Get Recommendations") and not st.session_state["recommend_triggered"]:
            st.session_state["recommend_triggered"] = True
            st.session_state["recommendations"] = recommend_similar_movies(movie_input).to_dict(orient="records")
            st.session_state["carousel_index"] = 0
            st.session_state["selected_input"] = movie_input
            st.session_state["selected_years"] = ""
            navigate_to("results")
            st.rerun()

    # ------------------------------Results Page
    elif st.session_state["current_page"] == "results":
        col1, col2 = st.columns([1, 5])
        with col1:
            st.button("🏠 Home", on_click=lambda: navigate_to("home"))
        with col2:
            st.button("🔙 Back", on_click=lambda: navigate_to(st.session_state["last_page"]))

        st.title("🎞️ Recommended Movies")

        # Safety check
        if not st.session_state["recommendations"]:
            st.warning("No recommendations available. Please go back and try again.")
            return

        # Context text above results
        if st.session_state["selected_years"]:
            st.markdown(f'<p class="custom-text"> Here\'s a list of movies in the {st.session_state["selected_input"]}, from the years {st.session_state["selected_years"]}.</p>', unsafe_allow_html=True)
        else:
            st.markdown(f'<p class="custom-text"> Here\'s a list of movies similar to {st.session_state["selected_input"]}.</p>', unsafe_allow_html=True)

        # Recommendation results display controls
        current_index = st.session_state["carousel_index"]
        movie = st.session_state["recommendations"][current_index]

        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            st.button("⬅️ Previous", disabled=(current_index == 0), on_click=lambda: st.session_state.update(carousel_index=max(0, current_index - 1)))
        with col2:
            st.write(f"    **{current_index + 1} / {len(st.session_state['recommendations'])}**")
        with col3:
            st.button("➡️ Next", disabled=(current_index == len(st.session_state["recommendations"]) - 1), on_click=lambda: st.session_state.update(carousel_index=min(len(st.session_state["recommendations"]) - 1, current_index + 1)))

        # Display movie details
        st.subheader(f" {movie['original_title']} ({movie['release_year']})")
        movie_details = fetch_movie_data(
            movie['original_title'],
            movie.get('release_year'),
            movie.get('overview')  # Fallback to local overview (if no API data)
        )
        
        col_img, col_info = st.columns([1, 2])

        with col_img:
            if movie_details and movie_details['poster']:
                st.image(movie_details['poster'], width=200)
            else:
                st.write("No poster available.")

        with col_info:
            if movie_details and movie_details['overview']:
                st.write(movie_details['overview'])

            st.markdown(f"**⭐ Average Rating:** {movie.get('vote_average', 'N/A')}")
            st.markdown(f"**🗳️ Vote Count:** {movie.get('vote_count', 'N/A')}")

        # Display reason for recommendation (if available)
        if "reason_for_recommendation" in movie and movie["reason_for_recommendation"]:
            st.write(f"**Reason for Recommendation:** {movie['reason_for_recommendation']}")

if __name__ == "__main__":
    main()

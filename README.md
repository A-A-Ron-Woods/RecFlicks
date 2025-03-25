# 🎬 RecFlicks – Movie Recommendation App

**RecFlicks** is a fun and user-friendly movie recommendation system built with Streamlit.  
It helps users discover new movies based on:
- 🎭 **Genre & Year Range**
- 🎥 **Movies similar to their favorites** (using ML & NLP techniques)

It also fetches **posters** and **descriptions** via the TMDB API to enhance the experience.

---

## 🚀 Try It Live

🌐 Deployed on Streamlit Cloud:  
👉 https://recflicks.streamlit.app/

---

## 🔧 Features

- ✅ Smart movie recommendations using Scikit-Learn & NLP
- 🎯 Filter by genres and custom year ranges
- 🤖 Similarity-based suggestions using TF-IDF + SVD + cast matching
- 🖼️ Movie posters and details from the TMDB API
- ✨ Stylish dark mode UI with custom fonts

---

## 🛠️ Local Installation (For Developers)

1. **Clone the repository**:
```bash
git clone https://github.com/A-A-Ron-Woods/RecFlicks.git
cd RecFlicks
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Add TMDB API Key**:
Create a file at `.streamlit/secrets.toml` with the following contents:
```toml
[api]
tmdb_key = "your_tmdb_api_key_here"
```

4. **Run the app**:
```bash
streamlit run RecFlicks.py
```

Then open `http://localhost:8501` in your browser if it doesn’t launch automatically.

---

## 📁 Project Structure

```
RecFlicks/
├── RecFlicks.py             # Main app
├── recommendation.py        # ML recommendation logic
├── tmdb_api.py              # TMDB API handling
├── tmdb_movies_data.csv     # Local movie dataset
├── requirements.txt
├── .streamlit/
│   ├── config.toml          # Theme and style settings
│   └── secrets.toml         # TMDB API key (not tracked in Git)
└── README.md
```

---

## 📜 License

This project is for educational/demo purposes.  
Movie data and posters are provided via [TMDB API](https://www.themoviedb.org/documentation/api).  
All trademarks belong to their respective owners.

---

## 👨‍💻 Author

Developed by **Aaron Woods**  
*Bachelor’s of Computer Science – AI Focus*

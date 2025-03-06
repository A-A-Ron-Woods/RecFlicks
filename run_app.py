import os
import webbrowser

# Define the Streamlit app file
streamlit_app = "RecFlicks.py"  # Change this if your main app file has a different name

# Automatically open the browser when Streamlit runs
webbrowser.open("http://localhost:8501")

# Run the Streamlit app
os.system(f"streamlit run {streamlit_app}")

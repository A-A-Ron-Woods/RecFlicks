import os
import webbrowser

# Get the absolute path of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Define the Streamlit app file
streamlit_app = "RecFlicks.py"

# Full path to the Streamlit app
app_path = os.path.join(script_dir, streamlit_app)

# Check if the file exists before running it
if not os.path.exists(app_path):
    print(f"❌ Error: File '{streamlit_app}' not found in {script_dir}")
    exit(1)

# Change the working directory to the script's directory
os.chdir(script_dir)

# Automatically open the browser when Streamlit runs
webbrowser.open("http://localhost:8501")

# Run the Streamlit app
os.system(f"streamlit run {app_path}")

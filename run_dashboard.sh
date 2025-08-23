#!/bin/bash
# --- Job Search Dashboard Launcher ---

# Path to your project
PROJECT_DIR="/Users/stevejose/Steve/Projects/pythonProj/autoapply"

# Move into project directory
cd "$PROJECT_DIR" || exit

# Activate virtual environment
source .venv/bin/activate

# Run Streamlit app
python app_wrapper.py

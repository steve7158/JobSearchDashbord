import webview
import subprocess
import time

# Start Streamlit server
process = subprocess.Popen(["streamlit", "run", "dashboard.py", 
                            "--server.port", "2187",
                            "--server.headless", "true",
                            "--browser.gatherUsageStats", "false"])

# Wait a bit for Streamlit to start
time.sleep(3)

# Open it inside a native window
webview.create_window("Job Search Dashboard", "http://localhost:2187")
webview.start()

# When window closes, stop Streamlit
process.terminate()

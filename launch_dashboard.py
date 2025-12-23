"""
Launch Streamlit Dashboard

Simple launcher script for the Streamlit UI.
"""

import subprocess
import sys
from pathlib import Path

# Get the path to streamlit_app.py
app_path = Path(__file__).parent / "src" / "ui" / "streamlit_app.py"

print("="*60)
print("🚀 Launching GPU-Accelerated Data Science Agents Dashboard")
print("="*60)
print(f"\nStarting Streamlit at: {app_path}")
print("\nThe dashboard will open in your browser automatically.")
print("Press Ctrl+C to stop the server.\n")
print("="*60)

# Launch Streamlit
try:
    subprocess.run([
        sys.executable, "-m", "streamlit", "run",
        str(app_path),
        "--server.headless=false"
    ])
except KeyboardInterrupt:
    print("\n\n👋 Dashboard stopped. Goodbye!")
except Exception as e:
    print(f"\n❌ Error launching dashboard: {e}")
    print("\nTry running manually:")
    print(f"  streamlit run {app_path}")

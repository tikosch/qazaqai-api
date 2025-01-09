# run.py

import os
from dotenv import load_dotenv
import uvicorn
from app.main import app  # Ensure this path is correct based on your project structure

# Load environment variables from .env file
load_dotenv()

if __name__ == "__main__":
    # Retrieve the PORT environment variable, defaulting to 8000 if not set
    port = int(os.getenv("PORT", 8000))
    host = "0.0.0.0"  # Ensure the server is accessible externally

    print(f"Starting server on host {host} and port {port}")

    # Run the Uvicorn server
    uvicorn.run(app, host=host, port=port)

"""
This is probably a non standard way of doing things but it seems to work. 
"""

from ukrdc_cupid.api.main import app, get_session
from sqlalchemy import text
import uvicorn


for session in get_session():
    if session.bind:
        print(f"Trying to connect to database at: {session.bind.url}")
        print(session.execute(text("SELECT version();")).all())

    else:
        print(":(")

# Start the API server
uvicorn.run(app, host="0.0.0.0", port=8000)
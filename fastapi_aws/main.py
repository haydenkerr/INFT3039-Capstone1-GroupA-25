import fastapi as app
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Welcome to the URL shortener!"}

@app.get("/{short_url}")
def redirect_to_long_url(short_url: str):
    # Implement the logic to retrieve and redirect to the long URL corresponding to the short URL
    # For simplicity, we will return a placeholder message here.
    return {"message": f"Redirecting to the long URL for '{short_url}'."}

# This is required for AWS Lambda to work
import mangum

handler = mangum.Mangum(app)



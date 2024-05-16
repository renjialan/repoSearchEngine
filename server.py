# server.py

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import requests
from dotenv import load_dotenv, find_dotenv
import os
from ml_integration import generate_text

from github_api import get_repository_content

app = FastAPI()

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

@app.get("/repositories/{owner}/{repo}/contents")
async def get_repository_contents(owner: str, repo: str):
    try:
        # Fetch repository contents from GitHub API
        url = f"https://api.github.com/repos/{owner}/{repo}/contents"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as err:
        raise HTTPException(status_code=500, detail="Failed to fetch repository contents") from err

@app.get("/search")
async def search_repository(query: str):
    try:
        # Use GitHub API to perform search
        url = f"https://api.github.com/search/code?q={query}"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as err:
        raise HTTPException(status_code=500, detail="Failed to perform search") from err

@app.post('/search')
async def search(query: str):
    # Generate text using Gemini API
    generated_text = generate_text(query)
    return {'generatedText': generated_text}

owner = "llvm"
repo = "torch-mlir"
path = "projects/pt1/e2e_testing/main.py"
content = get_repository_content(owner, repo, path)
if content:
    print(content)
else:
    print("Failed to fetch repository content.")

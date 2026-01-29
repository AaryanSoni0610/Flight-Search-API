from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import httpx
import os

app = FastAPI()

templates = Jinja2Templates(directory="templates")
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/search_proxy")
async def search_proxy(origin: str, destination: str, date: str):
    async with httpx.AsyncClient() as client:
        try:
            # Forward the request to the backend service
            resp = await client.get(
                f"{BACKEND_URL}/api/search",
                params={"origin": origin, "destination": destination, "date": date},
                timeout=10.0
            )
            # Return JSON directly
            if resp.status_code == 200:
                return resp.json()
            else:
                return JSONResponse(status_code=resp.status_code, content=resp.json())
        except Exception as e:
            return JSONResponse(status_code=500, content={"detail": f"Frontend proxy error: {str(e)}"})

@app.get("/health")
async def health():
    return {"status": "healthy"}

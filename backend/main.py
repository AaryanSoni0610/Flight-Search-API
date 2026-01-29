import json
from contextlib import asynccontextmanager
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Query
from models import FlightData, Itinerary
from search_engine import FlightSearchEngine

# Global state
search_engine: Optional[FlightSearchEngine] = None

def load_data(file_path: str = "flights.json") -> FlightData:
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    print(f"Loading raw data from {file_path}...")
    return FlightData(**data)

@asynccontextmanager
async def lifespan(app: FastAPI):
    global search_engine
    print("Loading data...")
    try:
        data = load_data()
        search_engine = FlightSearchEngine(data.airports, data.flights)
        print(f"Search Engine Initialized: {len(data.airports)} airports, {len(data.flights)} flights.")
    except Exception as e:
        print(f"Error loading data: {e}")
    yield

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def root():
    return {"message": "SkyPath Backend Service"}

@app.get("/health")
async def health():
    if search_engine:
        return {
            "status": "healthy", 
            "airports_count": len(search_engine.airports), 
            "flights_count": len(search_engine.flights_map)
        }
    return {"status": "uninitialized"}

@app.get("/api/airports")
async def get_airports():
    if not search_engine:
        raise HTTPException(status_code=503, detail="Search engine not initialized")
    
    return list(search_engine.airports.values())

@app.get("/api/search", response_model=List[Itinerary])
async def search_flights(
    origin: str = Query(..., min_length=3, max_length=3, pattern="^[A-Z]{3}$"),
    destination: str = Query(..., min_length=3, max_length=3, pattern="^[A-Z]{3}$"),
    date: str = Query(..., pattern=r"^\d{4}-\d{2}-\d{2}$")
):
    if not search_engine:
        raise HTTPException(status_code=503, detail="Search engine not initialized")
    
    return search_engine.find_routes(origin, destination, date)

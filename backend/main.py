import json
from datetime import datetime
from typing import List, Dict, Union, Annotated
from fastapi import FastAPI
from pydantic import BaseModel, Field, field_validator, BeforeValidator

app = FastAPI()

# --- Pydantic Models ---

class Airport(BaseModel):
    code: str
    name: str
    city: str
    country: str
    timezone: str

def parse_price(v: Union[str, float, int]) -> float:
    if isinstance(v, str):
        return float(v)
    return float(v)

class Flight(BaseModel):
    flightNumber: str
    airline: str
    origin: str
    destination: str
    departureTime: datetime
    arrivalTime: datetime
    price: Annotated[float, BeforeValidator(parse_price)]
    aircraft: str

class FlightData(BaseModel):
    airports: List[Airport]
    flights: List[Flight]

# --- Data Loader ---

def load_data(file_path: str = "flights.json") -> FlightData:
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # Validation and Parsing happens here via Pydantic
    return FlightData(**data)

# Global data storage
db: Dict[str, Union[List[Airport], List[Flight]]] = {"airports": [], "flights": []}

@app.on_event("startup")
async def startup_event():
    print("Loading data...")
    try:
        loaded_data = load_data()
        db["airports"] = loaded_data.airports
        db["flights"] = loaded_data.flights
        print(f"Loaded {len(db['airports'])} airports and {len(db['flights'])} flights.")
    except Exception as e:
        print(f"Error loading data: {e}")

@app.get("/")
async def root():
    return {"message": "SkyPath Backend Service"}

@app.get("/health")
async def health():
    return {
        "status": "healthy", 
        "airports_count": len(db["airports"]), 
        "flights_count": len(db["flights"])
    }

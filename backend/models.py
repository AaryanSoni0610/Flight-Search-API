from datetime import datetime
from typing import List, Union, Annotated
from pydantic import BaseModel, BeforeValidator

def parse_price(v: Union[str, float, int]) -> float:
    if isinstance(v, str):
        try:
            return float(v)
        except ValueError:
            return 0.0
    return float(v)

class Airport(BaseModel):
    code: str
    name: str
    city: str
    country: str
    timezone: str

class Flight(BaseModel):
    flightNumber: str
    airline: str
    origin: str
    destination: str
    departureTime: datetime
    arrivalTime: datetime
    departureTimeUTC: Union[datetime, None] = None
    arrivalTimeUTC: Union[datetime, None] = None
    price: Annotated[float, BeforeValidator(parse_price)]
    aircraft: str
    duration: float = 0.0

class FlightData(BaseModel):
    airports: List[Airport]
    flights: List[Flight]

class ItinerarySegment(BaseModel):
    flight: Flight
    duration: float  # In minutes or string, let's keep it simple for now as per reqs (time string maybe?)
    # actually requirement 4 says "flight segments with flight numbers, times, airports"
    # We will reuse Flight or a similar structure

class Itinerary(BaseModel):
    segments: List[Flight]
    total_price: float
    total_duration_minutes: float
    layovers: List[float]  # Duration in minutes

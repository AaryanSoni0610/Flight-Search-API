from datetime import datetime, timedelta
import pytz
from typing import List, Dict, Optional
from models import Airport, Flight, Itinerary

class FlightSearchEngine:
    def __init__(self, airports: List[Airport], flights: List[Flight]):
        self.airports = {a.code: a for a in airports}
        self.flights_map: Dict[str, List[Flight]] = {}
        for f in flights:
            # Calculate duration
            if f.duration == 0.0:
                 # Note: we need _get_utc_time which relies on self.airports being set
                 # Since this is inside __init__, we already set self.airports above.
                 # But we can't call instance method easily if we are just refactoring or we can.
                 # Actually, we can call self._get_utc_time
                 pass

            if f.origin not in self.flights_map:
                self.flights_map[f.origin] = []
            self.flights_map[f.origin].append(f)
        
        # Second pass to calculate duration properly using the helper method
        for f in flights:
             try:
                dep_utc = self._get_utc_time(f.departureTime, f.origin)
                arr_utc = self._get_utc_time(f.arrivalTime, f.destination)
                f.duration = (arr_utc - dep_utc).total_seconds() / 60
             except Exception as e:
                print(f"Error calculating duration for {f.flightNumber}: {e}")

    def _get_utc_time(self, local_dt: datetime, airport_code: str) -> datetime:
        airport = self.airports.get(airport_code)
        if not airport:
            # Fallback or error? For now assume valid airport
            return local_dt
        
        local_tz = pytz.timezone(airport.timezone)
        # The datetime from JSON might be naive, assume it matches the airport timezone
        if local_dt.tzinfo is None:
            local_dt_aware = local_tz.localize(local_dt)
        else:
            local_dt_aware = local_dt.astimezone(local_tz)
            
        return local_dt_aware.astimezone(pytz.UTC)

    def _is_domestic_flight(self, flight: Flight) -> bool:
        origin = self.airports[flight.origin]
        dest = self.airports[flight.destination]
        return origin.country == dest.country

    def find_routes(self, origin: str, destination: str, date_str: str) -> List[Itinerary]:
        results: List[Itinerary] = []
        
        # Start flights
        possible_starts = self.flights_map.get(origin, [])
        
        # Filter for start date
        # date_str is YYYY-MM-DD
        # flight.departureTime is datetime
        start_flights = []
        for f in possible_starts:
            # Simple string match on date part
            if f.departureTime.date().isoformat() == date_str:
                start_flights.append(f)

        for f in start_flights:
            self._dfs(f, destination, [f], results)
            
        # Sort results: Primary = Number of stops (0, 1, 2), Secondary = Total Duration
        # Stops = len(segments) - 1
        results.sort(key=lambda x: (len(x.segments) - 1, x.total_duration_minutes))
        return results

    def _dfs(self, current_flight: Flight, target_dest: str, current_path: List[Flight], results: List[Itinerary]):
        # Check if we reached destination
        if current_flight.destination == target_dest:
            self._build_itinerary(current_path, results)
            return

        # Max depth check (max 2 stops = 3 segments)
        if len(current_path) >= 3:
            return

        # Find next flights
        next_flights = self.flights_map.get(current_flight.destination, [])
        current_arrival_utc = self._get_utc_time(current_flight.arrivalTime, current_flight.destination)

        for next_f in next_flights:
            # Validate connection constraints
            next_departure_utc = self._get_utc_time(next_f.departureTime, next_f.origin)
            
            # Layover calculation
            layover_delta = next_departure_utc - current_arrival_utc
            layover_minutes = layover_delta.total_seconds() / 60
            
            # Constraint: Max layover 6 hours
            if layover_minutes > 6 * 60:
                continue
                
            # Constraint: Min layover
            # Logic: If both arriving (current) and departing (next) are domestic -> 45m
            # Else -> 90m
            is_domestic_seq = self._is_domestic_flight(current_flight) and self._is_domestic_flight(next_f)
            min_layover = 45 if is_domestic_seq else 90
            
            if layover_minutes < min_layover:
                continue

            # Recursive step
            self._dfs(next_f, target_dest, current_path + [next_f], results)

    def _build_itinerary(self, path: List[Flight], results: List[Itinerary]):
        total_price = sum(f.price for f in path)
        
        # Calculate layovers
        layovers = []
        for i in range(len(path) - 1):
            curr = path[i]
            next_f = path[i+1]
            arr_utc = self._get_utc_time(curr.arrivalTime, curr.destination)
            dep_utc = self._get_utc_time(next_f.departureTime, next_f.origin)
            diff = (dep_utc - arr_utc).total_seconds() / 60
            layovers.append(diff)
            
        # Total Duration: Departure of first to Arrival of last
        start_utc = self._get_utc_time(path[0].departureTime, path[0].origin)
        end_utc = self._get_utc_time(path[-1].arrivalTime, path[-1].destination)
        total_duration = (end_utc - start_utc).total_seconds() / 60
        
        itinerary = Itinerary(
            segments=path,
            total_price=total_price,
            total_duration_minutes=total_duration,
            layovers=layovers
        )
        results.append(itinerary)

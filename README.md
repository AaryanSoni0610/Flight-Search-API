# ✈️ SkyPath Flight Search Engine

A full-stack flight search engine built with **FastAPI** (backend & frontend) and a clean, responsive **Tailwind CSS** UI. Search for direct and connecting flights across a rich dataset of global routes.

---

## 🚀 Features

- 🔍 **Smart Flight Search** — Search by origin, destination, and date
- 🔗 **Multi-Segment Itineraries** — Finds direct and connecting flights (up to 2 stops)
- 🏙️ **Airport Autocomplete** — Live dropdown with airport name, city, and code
- 🔽 **Filtering & Sorting** — Filter by stops; sort by price, duration, or departure time
- 📋 **Detailed Flight View** — Modal with full itinerary breakdown, layover times, and per-segment info
- 🐳 **Dockerized** — One-command startup with Docker Compose

---

## 🗂️ Project Structure

```
FlightSearchEngine/
├── docker-compose.yml
├── backend/
│   ├── Dockerfile
│   ├── main.py                   # FastAPI backend app & API routes
│   ├── models.py                 # Pydantic data models
│   ├── search_engine.py          # Core flight search & pathfinding logic
│   ├── flights.json              # Local flight & airport data
│   └── requirements.txt
└── frontend/
    ├── Dockerfile
    ├── main.py                   # FastAPI frontend app (proxy to backend)
    ├── requirements.txt
    └── templates/
        └── index.html            # Full UI (Tailwind CSS + Vanilla JS)
```

---

## 🛠️ Tech Stack

| Layer     | Technology                          |
|-----------|--------------------------------------|
| Backend   | Python 3.11, FastAPI, Uvicorn        |
| Frontend  | Python 3.11, FastAPI, Jinja2, HTTPX  |
| UI        | Tailwind CSS (CDN), Day.js, Vanilla JS |
| Data      | JSON (airports + flights dataset)    |
| DevOps    | Docker, Docker Compose               |

---

## ⚡ Quick Start

### Prerequisites
- [Docker](https://www.docker.com/) & [Docker Compose](https://docs.docker.com/compose/)

### Run with Docker

```bash
# Clone the repository
git clone https://github.com/AaryanSoni0610/Flight-Search-API
cd FlightSearchEngine

# Start all services
docker-compose up --build
```

Then open your browser:
- **Frontend UI:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

---

## 🖥️ Running Locally (Without Docker)

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend

```bash
cd frontend
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 3000 --reload
```

---

## 🔌 API Endpoints

### Backend (`http://localhost:8000`)

| Method | Endpoint          | Description                              |
|--------|-------------------|------------------------------------------|
| GET    | `/health`         | Health check & stats                     |
| GET    | `/api/airports`   | List all airports                        |
| GET    | `/api/search`     | Search flights by origin, destination, date |

#### Search Example

```
GET /api/search?origin=JFK&destination=LAX&date=2024-03-15
```

#### Sample Response

```json
[
  {
    "segments": [...],
    "total_price": 299.00,
    "total_duration": 375,
    "layovers": []
  }
]
```

---

## ✈️ Flight Data

The dataset (`flights.json`) includes:

- **30+ global airports** across the US, Europe, Asia, Canada, and Mexico
- **400+ flight routes** covering short-haul and long-haul connections
- Airlines, aircraft types, departure/arrival times, and pricing

### Sample Airports

| Code | City             |
|------|-----------------|
| JFK  | New York         |
| LAX  | Los Angeles      |
| LHR  | London           |
| NRT  | Tokyo            |
| DXB  | Dubai            |
| SYD  | Sydney           |

---

## 🧩 How It Works

1. **User** enters origin, destination, and date in the UI.
2. **Frontend** proxies the request to the backend via `/search_proxy`.
3. **Backend Search Engine** finds all valid direct and connecting itineraries using a graph traversal over the flight map.
4. **Results** are returned as itineraries with full segment details, layover durations, and total price.
5. **Frontend** renders flight cards with filtering and sorting applied client-side.

---

## 🐳 Docker Architecture

```
┌─────────────────┐        ┌─────────────────────┐
│   Browser       │        │  skypath_frontend    │
│  :3000          │◄──────►│  FastAPI + Jinja2    │
└─────────────────┘        │  port 3000           │
                           └────────┬────────────┘
                                    │ HTTP proxy
                           ┌────────▼────────────┐
                           │  skypath_backend     │
                           │  FastAPI             │
                           │  port 8000           │
                           └─────────────────────┘
```

---

## 📄 License

This project is for educational and portfolio purposes.
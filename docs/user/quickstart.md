# User Quickstart Guide

## Step 1: Environment Setup
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Step 2: Run FastAPI Server
```bash
python -m src.api.app
```
Access Swagger UI documentation at `http://localhost:8000/docs`.

## Step 3: Run Clinical Dashboard Frontend
Open `frontend/index.html` in Chrome/Edge or serve via:
```bash
python -m http.server 5173 --directory frontend
```
Navigate to `http://localhost:5173`.

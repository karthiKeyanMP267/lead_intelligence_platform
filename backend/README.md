# Lead Intelligence Platform

All project content now lives inside this `backend` folder.

## Structure

- `backend/` API and DB code
- `ml/` data generation, consolidation, and training scripts
- `data/` raw and processed CSV files
- `models/` trained model and metrics artifacts
- `requirements.txt` Python dependencies

## Setup

From inside this `backend` folder:

```powershell
python -m venv venv
.\venv\Scripts\activate
python -m pip install -r requirements.txt
```

## ML Pipeline

Run these from inside `backend`:

```powershell
python ml/generate_data.py
python ml/consolidate.py
python ml/train.py
python load_data.py
```

## Run API

From inside `backend`, run:

```powershell
python -m uvicorn main:app --reload
```

Using `python -m uvicorn` avoids broken `.exe` launcher paths after folder moves.

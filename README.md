# FitPlanner Recomposition Engine

Production-ready MVP scaffold for an iOS + FastAPI adaptive body recomposition planner.

## Backend Architecture

`backend/app` is split into pure service modules:

- `services/physiology.py`: body composition, BMR (Mifflin-St Jeor 1990), TDEE, safe deficit, macro targets
- `services/projection.py`: weeks-to-goal + weekly/monthly weight projections
- `services/meal_engine.py`: algorithmic weekly meal generation with macro targeting and protein distribution
- `services/grocery_engine.py`: exact gram aggregation, package rounding, leftovers
- `services/adaptive.py`: weekly calorie adaptation engine
- `api/routes/recomp.py`: public endpoints

## Scientific Logic Included

- Mifflin-St Jeor (1990) for BMR
- Helms et al. (2014) protein ranges for dieting athletes
- Hall (2008) practical 7700 kcal/kg fat-energy conversion
- Safe weekly weight-loss bounds based on body-fat level

## API Endpoints

- `POST /calculate-plan`
- `POST /generate-meals`
- `POST /weekly-checkin`
- `GET /projection`
- `GET /health`

See: `docs/API_CONTRACT.md`

## Local Run

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

## Tests

```bash
cd backend
source .venv/bin/activate
pytest -q
```

## iOS App Notes

The iOS app is wired to `POST /generate-meals` and now displays:

- Current/target body fat
- Weeks to goal
- Fat mass remaining
- Training vs rest day macro toggle
- Weekly check-in modal
- Macro compliance tracker

Generate/open iOS project:

```bash
cd ios
xcodegen generate
open FitPlanner.xcodeproj
```

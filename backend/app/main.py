from fastapi import FastAPI
from app.api.routes.health import router as health_router
from app.api.routes.recomp import router as recomp_router

app = FastAPI(title="FitPlanner Recomposition API", version="2.0.0")

app.include_router(health_router)
app.include_router(recomp_router)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend import models
from backend.database.database import Base, engine
from backend.api.jobs import router as jobs_router
from backend.api.users import router as users_router
from backend.api.bot import router as bot_router

app = FastAPI(title="Jobs API")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


Base.metadata.create_all(bind=engine)


app.include_router(bot_router)
app.include_router(users_router)
app.include_router(jobs_router)

import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import your routers and database setup here
from database import create_db_and_tables
from routers import (
    dispenser,
    medications,
    prescriptions,
    reports,
    senior,
    symptoms,
    users,
)
from routers.auth import router as auth_router
from routers.compartment import router as compartment_router
from routers.device import router as device_router

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(title="Serena API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(prescriptions, prefix="/prescriptions", tags=["prescriptions"])
app.include_router(medications, prefix="/medications", tags=["medications"])
app.include_router(symptoms, prefix="/symptoms", tags=["symptoms"])
app.include_router(reports, prefix="/reports", tags=["reports"])
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(users, prefix="/users", tags=["users"])
app.include_router(senior, prefix="/senior", tags=["senior"])
app.include_router(device_router, prefix="/device", tags=["device"])
app.include_router(dispenser, prefix="/dispenser", tags=["dispenser"])
app.include_router(compartment_router, prefix="/compartment", tags=["compartment"])

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

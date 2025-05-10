import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import your routers and database setup here
from database import create_db_and_tables
from routers import medications, prescriptions, reports, symptoms
from routers.auth import router as auth_router

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

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

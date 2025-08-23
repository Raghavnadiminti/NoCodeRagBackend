# app/main.py
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv 
import uvicorn
from routes.userroute import router
from dbconfig.database import engine, Base
from models.Knowledge_model import Knowledge 
from models.User_model import User 
from models.Workflow_model import Workflow
from routes.workflow import workflowrouter

load_dotenv()

app = FastAPI()

# CORS settings
origins = [
    "http://localhost:3000",             # Local dev
    "http://localhost:5173",             # Vite dev
    "http://localhost:5175",
    "http://localhost:5174", 
]  

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600  # Cache preflight requests for 1 hour
)


app.include_router(router)
app.include_router(workflowrouter)
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
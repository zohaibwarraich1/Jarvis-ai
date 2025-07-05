from fastapi import FastAPI
from pydantic import BaseModel
from logic import handle_command, takeCommand

app = FastAPI()

class Query(BaseModel):
    query: str

@app.post("/command")
def process_query(data: Query):
    return {"response": handle_command(data.query)}

@app.get("/listen")
def listen():
    return {"response": takeCommand()}
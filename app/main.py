from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from routers import questions, submit
from database_setup import init_db

app = FastAPI(title="Mountain Coder 🏔️")

# Mount Static Files (UI + Monaco Editor)
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(questions.router)
app.include_router(submit.router)

@app.on_event("startup")
def on_startup():
    init_db()

@app.get("/")
def read_root():
    return FileResponse("static/index.html")
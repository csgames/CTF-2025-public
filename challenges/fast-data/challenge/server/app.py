from fastapi import FastAPI, Request, Cookie
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

import sqlite3
import uvicorn
import os

FLAG = os.environ.get("FLAG", "FLAG")
SECRET = os.environ.get("SECRET", "SECRET").strip()
PORT = 8888

class LoginRequest(BaseModel):
    username: str
    password: str

con = sqlite3.connect("data.db")
app = FastAPI(docs_url=None)

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/pages", StaticFiles(directory="pages", html=True), name="static")

@app.get("/")
async def redirect():
    return RedirectResponse("/pages/")

@app.get("/api/data")
async def query(s: str, request: Request):
    cursor = con.cursor()
    result = cursor.execute("SELECT * FROM data WHERE color LIKE ?", (f"%{s}%",))
    data = result.fetchall()
    return {"data": data, "search": s}

@app.get("/api/admin")
async def get_flag(request: Request):
    if request.cookies.get("token") == SECRET:
        return {"msg": FLAG}
    else:
        return {"msg": "HEY, YOU ARE NOT THE ADMIN, GET OUT OF HERE!"}

@app.post("/api/login")
async def login(login: LoginRequest):
    return {"msg": "Invalid Credentials"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT)

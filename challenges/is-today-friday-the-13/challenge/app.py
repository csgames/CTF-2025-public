from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
import subprocess
from pydantic import BaseModel
import os

app = FastAPI(docs_url=None)
FLAG = os.getenv("FLAG")
templates = Jinja2Templates(directory="templates")

@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

class Body(BaseModel):
    format: str

@app.post("/is-today-friday-the-13th")
async def is_today_friday_the_13(body: Body):
    if body.format == "":
        return {"msg": "Come on, tell me the format you need"}
    if not body.format.replace("%","").replace("-","").replace(" ","").replace("\t","").isalnum():
        return {"msg":"Invalid input detected! You don't need it to know if it's friday the 13th"}
    date = subprocess.getoutput("date +" + body.format)
    if date != "Friday\t13" and date != "Friday 13":
        return {"msg":"No, it's " + str(date) }
    return {"msg": FLAG}

from fastapi import FastAPI
from pydantic import BaseModel
import hashlib
from fastapi.responses import JSONResponse
from typing import Optional
from datetime import timedelta, datetime, date


app = FastAPI()
app.counter = 0
app.patcounter = 0


class HelloResp(BaseModel):
    msg: str


class Patient(BaseModel):
    name: str = ''
    surname: str = ''


class PatientResp(BaseModel):
    id: int
    name: str = ''
    surname: str = ''
    register_date: date
    vaccination_date: date


@app.get("/")
def root():
    return {"message": "Hello world!"}


@app.get('/counter')
def counter():
    app.counter += 1
    return str(app.counter)


@app.get("/hello/{name}", response_model=HelloResp)
async def read_item(name: str):
    return HelloResp(msg=f"Hello {name}")


@app.get("/method", status_code=200)
def give_method():
    return {"method": "GET"}


@app.put("/method", status_code=200)
def give_method():
    return {"method": "PUT"}


@app.options("/method", status_code=200)
def give_method():
    return {"method": "OPTIONS"}


@app.delete("/method", status_code=200)
def give_method():
    return {"method": "DELETE"}


@app.post("/method", status_code=201)
def give_method():
    return {"method": "POST"}


@app.get("/auth", status_code=401)
async def auth(password: Optional[str] = '', password_hash: Optional[str] = ''):
    if password and password_hash:
        password = password.encode('utf-8')
        h = hashlib.sha512(password)

        if h.hexdigest() == password_hash:
            return JSONResponse(status_code=204)
        else:
            return JSONResponse(status_code=401)
    return JSONResponse(status_code=401)


@app.post("/register", response_model=PatientResp, status_code=201)
async def pat_reg(patient: Patient):
    app.patcounter += 1
    today = datetime.now().strftime("%Y-%m-%d")
    delta = len(patient.surname) + len(patient.name)
    vac_day = (datetime.now() + timedelta(days=delta)).strftime('%Y-%m-%d')
    return PatientResp(
        id=app.patcounter,
        name=patient.name,
        surname=patient.surname,
        register_date=today,
        vaccination_date=vac_day,
    )

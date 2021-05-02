from fastapi import FastAPI, Request, status, HTTPException, Depends, Cookie
from pydantic import BaseModel
import hashlib
from fastapi.responses import JSONResponse, HTMLResponse, Response, PlainTextResponse
from typing import Optional
from datetime import timedelta, datetime, date
from fastapi.templating import Jinja2Templates
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets


app = FastAPI()
app.counter = 0
app.patients = dict()
templates = Jinja2Templates(directory="templates")
app.secret_key = "OMGitshouldbesomethinguniqueandlongatakwlasciwietoczemuinEnglish"
app.token = ""
app.session = ""

security = HTTPBasic()


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


@app.api_route(
    path="/method", methods=["GET", "POST", "DELETE", "PUT", "OPTIONS"], status_code=200
)
def read_request(request: Request, response: Response):
    request_method = request.method

    if request_method == "POST":
        response.status_code = status.HTTP_201_CREATED

    return {"method": request_method}


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
    idd = len(app.patients)+1
    today = datetime.now().astimezone().strftime("%Y-%m-%d")
    al_name = ''.join(c for c in patient.name if c.isalpha())
    al_surname = ''.join(c for c in patient.surname if c.isalpha())
    delta = len(al_name) + len(al_surname)
    vac_day = (datetime.now().astimezone() + timedelta(days=delta)).strftime('%Y-%m-%d')
    pat1 = PatientResp(
        id=idd,
        name=patient.name,
        surname=patient.surname,
        register_date=today,
        vaccination_date=vac_day,
    )
    app.patients[idd] = pat1
    return pat1


@app.get("/patient/{id}", status_code=200)
async def get_patient(idd: int):
    if idd < 1:
        return JSONResponse(status_code=400)
    elif idd > len(app.patients):
        return JSONResponse(status_code=404)
    return app.patients[idd]


@app.get("/request_query_string_discovery/")
def read_item(request: Request):
    print(f"{request.query_params=}")
    return request.query_params


@app.get("/hello", response_class=HTMLResponse)
def hello_html(request: Request):
    today = datetime.now().astimezone().strftime("%Y-%m-%d")
    return templates.TemplateResponse("index.html.j2", {
        "request": request, "curr_date": today})


@app.post("/login_session")
def login_session(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, "4dm1n")
    correct_password = secrets.compare_digest(credentials.password, "NotSoSecurePa$$")
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    else:
        session_token = hashlib.sha256(f"{credentials.username}{credentials.password}{app.secret_key}".encode()).hexdigest()
        app.session = session_token
        response = JSONResponse(status_code=status.HTTP_201_CREATED)
        response.set_cookie(key="session_token", value=session_token)
        return response


@app.post("/login_token")
def login_token(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, "4dm1n")
    correct_password = secrets.compare_digest(credentials.password, "NotSoSecurePa$$")
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
        )
    else:
        token_value = hashlib.sha256(f"{credentials.username}{credentials.password}{app.secret_key}".encode()).hexdigest()
        app.token = token_value
        return JSONResponse(status_code=status.HTTP_201_CREATED, content={"token": token_value})


@app.get("/welcome_session")
def welcome_session(request: Request, format: Optional[str] = None):
    session_token = request.cookies.get("session_token")
    if not session_token or session_token != app.session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED
        )
    else:
        if format == "json":
            return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "Welcome!"})
        elif format == "html":
            response = HTMLResponse(status_code=status.HTTP_200_OK, content="""
        <html>
            <head>
                <title>Some HTML in here</title>
            </head>
            <body>
                <h1>Welcome!</h1>
            </body>
        </html>
        """)
            return response
        else:
            return PlainTextResponse(status_code=status.HTTP_200_OK, content='Welcome!')


@app.get("/welcome_token")
def welcome_token(token: Optional[str] = None, format: Optional[str] = None):
    if not token or token != app.token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED
        )
    else:
        if format == "json":
            return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "Welcome!"})
        elif format == "html":
            response = HTMLResponse(status_code=status.HTTP_200_OK, content="""
        <html>
            <head>
                <title>Some HTML in here</title>
            </head>
            <body>
                <h1>Welcome!</h1>
            </body>
        </html>
        """)
            return response
        else:
            return PlainTextResponse(status_code=status.HTTP_200_OK, content='Welcome!')

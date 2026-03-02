from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette.status import HTTP_303_SEE_OTHER

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def handle_login(request: Request, username: str = Form(...), password: str = Form(...)):

    if username == "admin" and password == "admin":
        response = RedirectResponse(url="/", status_code=HTTP_303_SEE_OTHER)
        response.set_cookie(key="user", value=username)
        return response

    return templates.TemplateResponse("login.html", {
        "request": request,
        "error": "Credenciales incorrectas"
    })


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    user = request.cookies.get("user")

    if not user:
        return RedirectResponse(url="/login", status_code=HTTP_303_SEE_OTHER)

    return templates.TemplateResponse("index.html", {
        "request": request,
        "usuario": user,
        "titulo": "Inicio"
    })
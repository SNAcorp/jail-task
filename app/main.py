from fastapi import FastAPI, Request, Form, Cookie, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.templating import Jinja2Templates
from itsdangerous import URLSafeSerializer

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Защищенные данные для админа
security = HTTPBasic()
admin_email = "stepanov.iop@gmail.com"
admin_password = "12345"
secret_key = "SECRET_KEY"
serializer = URLSafeSerializer(secret_key)

# Временное хранилище для голосов
votes = {"betray": 0, "cooperate": 0}


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    # Проверка на наличие куки, чтобы избежать повторного голосования
    voted = request.cookies.get("voted")
    if voted:
        return templates.TemplateResponse("voted.html", {"request": request, "message": "Вы уже проголосовали!"})
    return templates.TemplateResponse("index.html", {"request": request, "message": "Проголосуйте"})

@app.get("/suka", response_class=HTMLResponse)
async def suka(request: Request):
    return templates.TemplateResponse("suka.html", {"request": request})


@app.post("/vote", response_class=RedirectResponse)
async def vote(choice: str = Form(...)):
    # Обновляем результаты голосования
    if choice in votes.keys():
        votes[choice] += 1
    else:
        return RedirectResponse("/suka", status_code=303)
    response = RedirectResponse("/", status_code=303)
    # Устанавливаем куку после голосования
    response.set_cookie(key="voted", value=serializer.dumps("voted"), max_age=86400)
    return response


@app.get("/admin", response_class=HTMLResponse)
async def admin_panel(request: Request, credentials: HTTPBasicCredentials = Depends(security)):
    # Проверка учетных данных администратора
    if credentials.username != admin_email or credentials.password != admin_password:
        raise HTTPException(status_code=401, detail="Неправильные учетные данные")

    return templates.TemplateResponse("admin.html", {"request": request, "votes": votes})

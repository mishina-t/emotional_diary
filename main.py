from fastapi import FastAPI, Request, Form, Depends, HTTPException, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import sqlite3, os, datetime
from analyzer import analyze_text
from contextlib import asynccontextmanager

# --- New Imports for Security ---
from passlib.context import CryptContext
from jose import JWTError, jwt
from typing import Optional

# --- Configuration ---
DB_PATH = "app.db"
# Secret key for signing JWT tokens. In a real app, use a long, random string from your environment.
SECRET_KEY = "a_very_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# --- Password Hashing Setup ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- FastAPI App Setup ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

#DBを作る
def init_db():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    #ユーザーの管理。Id, username, passwordの管理
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      username TEXT NOT NULL UNIQUE,
      password_hash TEXT NOT NULL
    )""")
    #全ての日記の管理
    cur.execute("""
    CREATE TABLE IF NOT EXISTS entries(
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      date TEXT NOT NULL,
      text TEXT NOT NULL,
      emojis TEXT,
      mood INTEGER,
      sentiment_score REAL,
      sentiment_magnitude REAL,
      created_at TEXT NOT NULL,
      user_id INTEGER NOT NULL,
      FOREIGN KEY(user_id) REFERENCES users(id)
    )""")
    #一人のユーザーにつき、一つの日程に日記は一つ
    cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_user_date ON entries (user_id, date)")
    con.commit()
    con.close()

#セキュリティ
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[datetime.timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.datetime.utcnow() + expires_delta
    else:
        expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Dependency to get the current user from the session token
async def get_current_user(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        return None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
        return {"username": username}
    except JWTError:
        return None

#ログイン画面
@app.get("/login", response_class=HTMLResponse)
def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
def login(response: Response, username: str = Form(...), password: str = Form(...)):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("SELECT password_hash FROM users WHERE username = ?", (username,))
    user_row = cur.fetchone()
    con.close()
    if not user_row or not verify_password(password, user_row[0]):
        return RedirectResponse("/login?error=1", status_code=303)
    
    access_token_expires = datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": username}, expires_delta=access_token_expires
    )
    response = RedirectResponse(url="/", status_code=303)
    response.set_cookie(key="access_token", value=access_token, httponly=True)
    return response

#新規登録画面
@app.get("/register", response_class=HTMLResponse)
def register_form(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register")
def register(username: str = Form(...), password: str = Form(...)):
    password_hash = get_password_hash(password)
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    try:
        cur.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, password_hash))
        con.commit()
    except sqlite3.IntegrityError:
        return RedirectResponse("/register?error=1", status_code=303)
    finally:
        con.close()
    return RedirectResponse("/login", status_code=303)

@app.get("/logout")
def logout():
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie("access_token")
    return response

#ホーム画面。
#ユーザーがログインしていなければ、/loginに送らせる
@app.get("/", response_class=HTMLResponse)
def home(request: Request, user: dict = Depends(get_current_user)):
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("SELECT id FROM users WHERE username = ?", (user['username'],))
    user_id_row = cur.fetchone()
    if not user_id_row:
        # Should not happen if token is valid, but good practice to check
        return RedirectResponse(url="/login", status_code=303)
    user_id = user_id_row[0]
    
    cur.execute("SELECT date, mood, sentiment_score FROM entries WHERE user_id = ? ORDER BY date DESC LIMIT 30", (user_id,))
    rows = cur.fetchall()
    con.close()
    
    rows = rows[::-1]
    dates = [r[0] for r in rows]
    moods = [r[1] or 0 for r in rows]
    scores = [r[2] if r[2] is not None else 0 for r in rows]

    suggestion = ""
    if len(scores) >= 3:
        last3 = scores[-3:]
        avg3 = sum(last3)/3
        if avg3 < -0.5:
            suggestion = "パーッと遊びに出かけませんか？"
        elif avg3 < -0.2:
            suggestion = "💡最近少し低調です。近所を5分散歩してみませんか？🌿"
        elif avg3 > 0.3:
            suggestion = "むっちゃ元気！"
        elif avg3 > 0:
            suggestion = "はっぴーはっぴーはっぴー"

    return templates.TemplateResponse(
        "home.html",
        {"request": request, "dates": dates, "moods": moods, "scores": scores, "suggestion": suggestion, "username": user['username']}
    )


@app.get("/entry", response_class=HTMLResponse)
def entry_form(request: Request, user: dict = Depends(get_current_user)):
    if not user:
        return RedirectResponse(url="/login")
    today = datetime.date.today().isoformat()
    return templates.TemplateResponse("entry.html", {"request": request, "today": today})

@app.post("/entry")
def create_or_update_entry(
    date: str = Form(...),
    text: str = Form(...),
    emojis: str = Form(""),
    mood: int = Form(3),
    user: dict = Depends(get_current_user)
):
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    s = analyze_text(text=text, emojis=emojis, mood=mood)
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("SELECT id FROM users WHERE username = ?", (user['username'],))
    user_id = cur.fetchone()[0]

    cur.execute("""
      INSERT OR REPLACE INTO entries(user_id, date, text, emojis, mood, sentiment_score, sentiment_magnitude, created_at)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (user_id, date, text, emojis, mood, s["score"], s["magnitude"], datetime.datetime.utcnow().isoformat()))
    con.commit()
    con.close()
    return RedirectResponse("/", status_code=303)

@app.get("/delete", response_class=HTMLResponse)
def delete_form(request: Request, user: dict = Depends(get_current_user)):
    if not user:
        return RedirectResponse(url="/login")
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("SELECT id FROM users WHERE username = ?", (user['username'],))
    user_id = cur.fetchone()[0]
    cur.execute("SELECT date FROM entries WHERE user_id = ? ORDER BY date DESC", (user_id,))
    dates = [d[0] for d in cur.fetchall()]
    con.close()
    return templates.TemplateResponse("delete.html", {"request": request, "dates": dates})

@app.post("/delete")
def delete_entry(date: str = Form(...), user: dict = Depends(get_current_user)):
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("SELECT id FROM users WHERE username = ?", (user['username'],))
    user_id = cur.fetchone[0]
    cur.execute("DELETE FROM entries WHERE date = ? AND user_id = ?", (date, user_id))
    con.commit()
    con.close()
    return RedirectResponse("/", status_code=303)

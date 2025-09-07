from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import sqlite3, os, datetime
from analyzer import analyze_text

DB_PATH = "app.db"
app = FastAPI()
#app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

def init_db():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS entries(
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      date TEXT NOT NULL,
      text TEXT NOT NULL,
      emojis TEXT,
      mood INTEGER,
      sentiment_score REAL,
      sentiment_magnitude REAL,
      created_at TEXT NOT NULL
    )""")
    con.commit()
    con.close()

@app.on_event("startup")
def on_startup():
    os.makedirs("templates", exist_ok=True)
    os.makedirs("static", exist_ok=True)
    init_db()

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    # 直近30日を取得
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("SELECT date, mood, sentiment_score FROM entries ORDER BY date DESC LIMIT 30")
    rows = cur.fetchall()
    con.close()
    rows = rows[::-1]  # 昇順描画
    dates = [r[0] for r in rows]
    moods = [r[1] or 0 for r in rows]
    scores = [r[2] if r[2] is not None else 0 for r in rows]

    suggestion = ""
    if len(scores) >= 3:
        last3 = scores[-3:]
        avg3 = sum(last3)/3
        if avg3 < -0.2:
            suggestion = "💡最近少し低調です。近所を5分散歩してみませんか？🌿"

    return templates.TemplateResponse(
        "home.html",
        {"request": request, "dates": dates, "moods": moods, "scores": scores, "suggestion": suggestion}
    )

@app.get("/entry", response_class=HTMLResponse)
def entry_form(request: Request):
    today = datetime.date.today().isoformat()
    return templates.TemplateResponse("entry.html", {"request": request, "today": today})

@app.post("/entry")
def create_entry(
    date: str = Form(...),
    text: str = Form(...),
    emojis: str = Form(""),
    mood: int = Form(3),
):
    # Google NL API で分析（失敗時はローカル簡易解析）
    s = analyze_text(text=text, emojis=emojis, mood=mood)

    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("""
      INSERT INTO entries(date, text, emojis, mood, sentiment_score, sentiment_magnitude, created_at)
      VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (date, text, emojis, mood, s["score"], s["magnitude"], datetime.datetime.utcnow().isoformat()))
    con.commit()
    con.close()
    return RedirectResponse("/", status_code=303)


@app.get("/delete", response_class=HTMLResponse)
def delete_form(request: Request):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("SELECT date FROM entries ORDER BY date DESC")
    dates = [d[0] for d in cur.fetchall()]
    con.close()
    return templates.TemplateResponse("delete.html", {"request": request, "dates": dates})

@app.post("/delete")
def delete_entry(date: str = Form(...)):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("DELETE FROM entries WHERE date = ?", (date,))
    con.commit()
    con.close()
    return RedirectResponse("/", status_code=303)

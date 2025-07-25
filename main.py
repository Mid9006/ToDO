import sqlite3
from fastapi import FastAPI
from typing import Optional

app = FastAPI()
DB_NAME = 'todos.db'

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS todos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            description TEXT,
            is_done INTEGER
        )
    ''')
    conn.commit()
    conn.close()

init_db()

def todo_dict(row):
    return {"id": row[0], "title": row[1], "description": row[2], "is_done": bool(row[3])}

@app.get("/")
def root():
    return {"message": "http://127.0.0.1:8000/docs"}

@app.post("/todos")
def add_todo(title: str, description: str = "", is_done: bool = False):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO todos (title, description, is_done) VALUES (?, ?, ?)",
        (title, description, int(is_done))
    )
    conn.commit()
    todo_id = cur.lastrowid
    conn.close()
    return {"id": todo_id, "title": title, "description": description, "is_done": is_done}

@app.get("/todos")
def get_todos(is_done: Optional[bool] = None, search: Optional[str] = None):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    query = "SELECT * FROM todos WHERE 1=1"
    params = []
    if is_done is not None:
        query += " AND is_done = ?"
        params.append(int(is_done))
    if search:
        query += " AND (title LIKE ? OR description LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%"])
    cur.execute(query, params)
    rows = cur.fetchall()
    conn.close()
    return [todo_dict(row) for row in rows]

@app.get("/todos/{todo_id}")
def get_todo(todo_id: int):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT * FROM todos WHERE id = ?", (todo_id,))
    row = cur.fetchone()
    conn.close()
    if row:
        return todo_dict(row)
    return {"error": "Not found"}

@app.put("/todos/{todo_id}")
def update_todo(todo_id: int, title: Optional[str] = None, description: Optional[str] = None, is_done: Optional[bool] = None):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT * FROM todos WHERE id = ?", (todo_id,))
    row = cur.fetchone()
    if not row:
        conn.close()
        return {"error": "Not found"}
    new_title = title if title is not None else row[1]
    new_description = description if description is not None else row[2]
    new_is_done = int(is_done) if is_done is not None else row[3]
    cur.execute(
        "UPDATE todos SET title = ?, description = ?, is_done = ? WHERE id = ?",
        (new_title, new_description, new_is_done, todo_id)
    )
    conn.commit()
    conn.close()
    return {"id": todo_id, "title": new_title, "description": new_description, "is_done": bool(new_is_done)}

@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: int):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
    conn.commit()
    deleted = cur.rowcount
    conn.close()
    return {"deleted": bool(deleted)}

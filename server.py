from flask import Flask, request, jsonify, redirect, session, render_template_string
import sqlite3
import uuid
import os

app = Flask(__name__)
app.secret_key = "supersecret"

ADMIN_LOGIN = "admin"
ADMIN_PASSWORD = "admin123"

DB = "database.db"


def db():
    return sqlite3.connect(DB)


def init_db():
    conn = db()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        login TEXT UNIQUE,
        password TEXT,
        token TEXT,
        attempts INTEGER
    )
    """)

    conn.commit()
    conn.close()


init_db()


def get_user(login):
    conn = db()
    cur = conn.cursor()

    cur.execute("SELECT login,password,token,attempts FROM users WHERE login=?", (login,))
    u = cur.fetchone()

    conn.close()
    return u


def get_user_by_token(token):
    conn = db()
    cur = conn.cursor()

    cur.execute("SELECT login,attempts FROM users WHERE token=?", (token,))
    u = cur.fetchone()

    conn.close()
    return u


@app.route("/api/login", methods=["POST"])
def api_login():

    data = request.json
    user = get_user(data["login"])

    if user and user[1] == data["password"]:
        return jsonify({"token": user[2], "attempts": user[3]})

    return "error", 401


@app.route("/api/scan", methods=["POST"])
def scan():

    token = request.headers.get("Authorization")
    user = get_user_by_token(token)

    if not user:
        return "invalid token"

    if user[1] <= 0:
        return "no attempts"

    file = request.files["file"]

    conn = db()
    cur = conn.cursor()

    cur.execute(
        "UPDATE users SET attempts = attempts - 1 WHERE login=?",
        (user[0],)
    )

    conn.commit()
    conn.close()

    return "File scanned (demo)"


login_html = """
<h2>Admin Login</h2>
<form method="post">
<input name="login" placeholder="login"><br><br>
<input type="password" name="password" placeholder="password"><br><br>
<button>Login</button>
</form>
"""


@app.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        if request.form["login"] == ADMIN_LOGIN and request.form["password"] == ADMIN_PASSWORD:
            session["admin"] = True
            return redirect("/panel")

    return render_template_string(login_html)


panel_html = """
<h1>Admin Panel</h1>

<h2>Create User</h2>

<form action="/create" method="post">
<input name="login" placeholder="login">
<input name="password" placeholder="password">
<input name="attempts" placeholder="attempts">
<button>Create</button>
</form>

<hr>

<h2>Users</h2>

<table border="1">
<tr>
<th>Login</th>
<th>Attempts</th>
<th>Change</th>
</tr>

{% for u in users %}
<tr>
<td>{{u[0]}}</td>
<td>{{u[1]}}</td>
<td>
<form action="/update" method="post">
<input type="hidden" name="login" value="{{u[0]}}">
<input name="attempts">
<button>Update</button>
</form>
</td>
</tr>
{% endfor %}
</table>
"""


@app.route("/panel")
def panel():

    if not session.get("admin"):
        return redirect("/")

    conn = db()
    cur = conn.cursor()

    cur.execute("SELECT login,attempts FROM users")
    users = cur.fetchall()

    conn.close()

    return render_template_string(panel_html, users=users)


@app.route("/create", methods=["POST"])
def create():

    if not session.get("admin"):
        return redirect("/")

    token = str(uuid.uuid4())

    conn = db()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO users(login,password,token,attempts) VALUES(?,?,?,?)",
        (
            request.form["login"],
            request.form["password"],
            token,
            int(request.form["attempts"])
        )
    )

    conn.commit()
    conn.close()

    return redirect("/panel")


@app.route("/update", methods=["POST"])
def update():

    if not session.get("admin"):
        return redirect("/")

    conn = db()
    cur = conn.cursor()

    cur.execute(
        "UPDATE users SET attempts=? WHERE login=?",
        (int(request.form["attempts"]), request.form["login"])
    )

    conn.commit()
    conn.close()

    return redirect("/panel")


port = int(os.environ.get("PORT", 10000))
app.run(host="0.0.0.0", port=port)
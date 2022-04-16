#!/usr/bin/python3

from flask import Flask, request
from waitress import serve
from time import time
import sqlite3

app = Flask(__name__)

def check_request(data):
    db = sqlite3.connect("/path/to/cabalbot.db")
    c = db.cursor()

    account = data.args.get("account")
    key = data.args.get("key")
    secret = data.args.get("secret")
    now = time()

    check = c.execute("""SELECT * FROM auth WHERE account=?;""", (account,)).fetchone()

    if check is not None:
        c.execute("""DELETE FROM auth WHERE account=?;""", (account,))
        db.commit()

    c.execute("""INSERT INTO auth VALUES(?, ?, ?, ?);""", (account, key, secret, now))
    db.commit()

    db.close()
    return True


@app.route("/webhook", methods=["GET"])
def index():
    if request.method == "GET":
        if check_request(request):
            return "OK"


if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=3333)
"""Return names from the Lab 5 SQLite users table on port 3000."""
from pathlib import Path
import sqlite3
from flask import Flask, jsonify

app = Flask(__name__)
DATABASE = Path(__file__).with_name("database.db")

@app.get("/get_users")
def get_users():
    with sqlite3.connect(DATABASE) as connection:
        rows = connection.execute("SELECT name FROM users ORDER BY user_id").fetchall()
    return jsonify([row[0] for row in rows])

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000, debug=False)

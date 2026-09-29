from flask import Flask
from datetime import datetime

app = Flask(__name__)

@app.route("/")
def home():
    return "Sample Time App"

@app.route("/time")
def time():
    return f"Current time: {datetime.now()}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
from flask import Flask
import redis
import os

app = Flask(__name__)

redis_host = os.environ.get("REDIS_HOST", "localhost")
redis_port = int(os.environ.get("REDIS_PORT", 6379))

r = redis.Redis(host=redis_host, port=redis_port)

@app.route("/")
def hello():
    count = r.incr("visits")
    return f"Hello from Zynex Solutions! Visits: {count}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

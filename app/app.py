
from flask import Flask, jsonify
import time

app = Flask(__name__)

START_TIME = time.time()

# Used to simulate an application failure
FAILURE_MODE = False


@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "application": "AutoHeal",
        "status": "running",
        "message": "Self-Healing Platform Application"
    })


@app.route("/health", methods=["GET"])
def health():
    if FAILURE_MODE:
        return jsonify({
            "status": "unhealthy",
            "message": "Application failure is active"
        }), 503

    return jsonify({
        "status": "healthy"
    }), 200


@app.route("/metrics", methods=["GET"])
def metrics():
    uptime = round(time.time() - START_TIME, 2)

    return jsonify({
        "application": "AutoHeal",
        "uptime_seconds": uptime,
        "failure_mode": FAILURE_MODE
    }), 200


@app.route("/simulate-failure", methods=["POST"])
def simulate_failure():
    global FAILURE_MODE

    FAILURE_MODE = True

    return jsonify({
        "status": "failure",
        "message": "Application failure simulated"
    }), 200


@app.route("/restore", methods=["POST"])
def restore():
    global FAILURE_MODE

    FAILURE_MODE = False

    return jsonify({
        "status": "healthy",
        "message": "Application restored"
    }), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)


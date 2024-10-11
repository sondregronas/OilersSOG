import os

from flask import Flask, jsonify, render_template
from flask_socketio import SocketIO

app = Flask(__name__)
sio = SocketIO(app, cors_allowed_origins="*")

# Same structure as the WiseHockey API for easy integration
tally = {
    "home": 0,
    "away": 0,
    "homeTeamStatistics": {"totalStatistics": {"shotStatistics": {"shotsOnGoal": 0}}},
    "awayTeamStatistics": {"totalStatistics": {"shotStatistics": {"shotsOnGoal": 0}}},
}


def modify_tally(team, amount):
    tally[team]["totalStatistics"]["shotStatistics"]["shotsOnGoal"] += amount
    current_tally = tally[team]["totalStatistics"]["shotStatistics"]["shotsOnGoal"]
    if current_tally < 0:
        tally[team]["totalStatistics"]["shotStatistics"]["shotsOnGoal"] = 0
        current_tally = 0
    sio.emit("tally", tally)
    return jsonify(current_tally)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api")
def api():
    tally["home"] = tally["homeTeamStatistics"]["totalStatistics"]["shotStatistics"][
        "shotsOnGoal"
    ]
    tally["away"] = tally["awayTeamStatistics"]["totalStatistics"]["shotStatistics"][
        "shotsOnGoal"
    ]
    return jsonify(tally)


@app.route("/api/<team>")
def api_team(team):
    if team.lower() not in ["home", "away"]:
        return jsonify({"error": "Invalid team"})
    if team.lower() == "home":
        team = "homeTeamStatistics"
    else:
        team = "awayTeamStatistics"
    return jsonify(tally[team]["totalStatistics"]["shotStatistics"]["shotsOnGoal"])


@app.route("/api/<add_or_remove>/<team>")
def add_api(add_or_remove, team):
    if add_or_remove.lower() not in ["add", "remove"]:
        return jsonify({"error": "Invalid operation"})
    if team.lower() not in ["home", "away"]:
        return jsonify({"error": "Invalid team"})
    if team.lower() == "home":
        team = "homeTeamStatistics"
    else:
        team = "awayTeamStatistics"
    modify_tally(team, 1 if add_or_remove.lower() == "add" else -1)
    return jsonify(tally[team]["totalStatistics"]["shotStatistics"]["shotsOnGoal"])


@sio.on("connect")
def connect():
    sio.emit("tally", tally)


@sio.on("add")
def add(data):
    modify_tally(data["team"], 1)


@sio.on("remove")
def remove(data):
    modify_tally(data["team"], -1)


@sio.on("reset")
def reset():
    tally["homeTeamStatistics"]["totalStatistics"]["shotStatistics"]["shotsOnGoal"] = 0
    tally["awayTeamStatistics"]["totalStatistics"]["shotStatistics"]["shotsOnGoal"] = 0
    sio.emit("tally", tally)


if __name__ == "__main__":
    host = os.environ.get("HOST", "http://localhost:5000")
    data = open("templates/index.html", "r").read()
    data = data.replace("http://localhost:5000", host)
    with open("templates/index.html", "w") as file:
        file.write(data)

    sio.run(app, host="0.0.0.0", allow_unsafe_werkzeug=True)

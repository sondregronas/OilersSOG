from flask import Flask, jsonify, render_template
from flask_socketio import SocketIO

app = Flask(__name__)
sio = SocketIO(app, cors_allowed_origins='*')

# Same structure as the WiseHockey API for easy integration
tally = {
    "homeTeamStatistics": {
        "totalStatistics": {
            "shotStatistics": {
                "shotsOnGoal": 0
            }}},
    "awayTeamStatistics": {
        "totalStatistics": {
            "shotStatistics": {
                "shotsOnGoal": 0
            }}}
}


def modify_tally(team, amount):
    tally[team]['totalStatistics']['shotStatistics']['shotsOnGoal'] += amount
    current_tally = tally[team]['totalStatistics']['shotStatistics']['shotsOnGoal']
    if current_tally < 0:
        tally[team]['totalStatistics']['shotStatistics']['shotsOnGoal'] = 0
        current_tally = 0
    sio.emit('tally', tally)
    return jsonify(current_tally)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api')
def api():
    return jsonify(tally)


@sio.on('connect')
def connect():
    sio.emit('tally', tally)


@sio.on('add')
def add(data):
    modify_tally(data['team'], 1)


@sio.on('remove')
def remove(data):
    modify_tally(data['team'], -1)


@sio.on('reset')
def reset():
    tally['homeTeamStatistics']['totalStatistics']['shotStatistics']['shotsOnGoal'] = 0
    tally['awayTeamStatistics']['totalStatistics']['shotStatistics']['shotsOnGoal'] = 0
    sio.emit('tally', tally)


if __name__ == '__main__':
    sio.run(app, host='0.0.0.0', allow_unsafe_werkzeug=True)

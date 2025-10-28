from flask import Flask, render_template, request, jsonify, send_from_directory
from stockfish import Stockfish
import requests
import os

app = Flask(__name__)
stockfish = Stockfish(path="stockfish/stockfish_win.exe")

def fetch_chess_games(username, year=None, month=None):
    headers = {
    'User-Agent': 'Chess Game Analyzer/1.0 Contact: your-email@example.com'
    }
    url = f"https://api.chess.com/pub/player/{username}/games"
    if year and month:
        url += f"/{year}/{month:02d}"
    else:
        url += "/2025/10"
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    return resp.json()["games"]

def analyze_move(fen, move):
    stockfish.set_fen_position(fen)
    stockfish.make_moves_from_current_position([move])
    eval_ = stockfish.get_evaluation()
    return eval_

def categorize_move(eval_diff):
    if eval_diff == 0:
        return "best"
    elif eval_diff < 50:
        return "excellent"
    elif eval_diff < 150:
        return "good"
    elif eval_diff < 300:
        return "inaccuracy"
    elif eval_diff < 700:
        return "mistake"
    else:
        return "blunder"

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/api/games/<username>")
def api_games(username):
    games = fetch_chess_games(username)
    return jsonify(games)

@app.route("/api/analyze", methods=["POST"])
def api_analyze():
    data = request.json
    if not data or "fen" not in data or "move" not in data:
        return jsonify({"error": "Invalid input"}), 400
    fen = data["fen"]
    move = data["move"]
    prev_eval = data.get("prev_eval")
    result = analyze_move(fen, move)
    eval_cp = result.get("value", 0) if result["type"] == "cp" else 0
    if prev_eval is not None:
        diff = abs(eval_cp - prev_eval)
        category = categorize_move(diff)
    else:
        category = "best"
    return jsonify({"eval": eval_cp, "category": category})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

@app.route('/img/<path:filename>')
def custom_static(filename):
    return send_from_directory('img', filename)
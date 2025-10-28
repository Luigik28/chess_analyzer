from flask import Flask, render_template, request, jsonify
from stockfish import Stockfish
import requests
import os

app = Flask(__name__)
stockfish = Stockfish(path="stockfish/stockfish_ubuntu_x86-64-avx2")

def fetch_chess_games(username, year=None, month=None):
    url = f"https://api.chess.com/pub/player/{username}/games"
    if year and month:
        url += f"/{year}/{month:02d}"
    resp = requests.get(url)
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

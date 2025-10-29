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
    # Analizza la posizione prima della mossa
    stockfish.set_fen_position(fen)
    eval_before_data = stockfish.get_evaluation()
    eval_before = eval_before_data["value"] if eval_before_data["type"] == "cp" else 0

    # Analizza la posizione dopo la mossa
    stockfish.set_fen_position(fen)
    stockfish.make_moves_from_current_position([move])
    eval_after_data = stockfish.get_evaluation()
    eval_after = eval_after_data["value"] if eval_after_data["type"] == "cp" else 0

    diff = abs(eval_after - eval_before)
    return eval_after, diff

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
    move = data["move"]
    eval_after, diff = analyze_move(fen, move)
    category = categorize_move(diff)
    return jsonify({"eval": eval_after, "category": category})

# Aggiungi route per favicon se serve
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)), debug=True)

@app.route('/img/<path:filename>')
def custom_static(filename):
    return send_from_directory('img', filename)
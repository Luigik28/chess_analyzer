let board = null;
let game = null;
let moves = [];
let fenList = [];
let analysisList = [];
let currentMove = 0;

function loadGames() {
    const username = document.getElementById('username').value;
    fetch(`/api/games/${username}`)
        .then(resp => resp.json())
        .then(games => {
            let html = '<select id="gameSelect">';
            games.forEach((g, i) => {
                html += `<option value="${i}">VS ${g.white.username} - ${g.black.username} (${g.end_time})</option>`;
            });
            html += '</select><button onclick="startGame()">Apri</button>';
            document.getElementById('games').innerHTML = html;
        });
}

function startGame() {
    const select = document.getElementById('gameSelect');
    const idx = select.value;
    fetch(`/api/games/${document.getElementById('username').value}`)
        .then(resp => resp.json())
        .then(games => {
            const pgn = games[idx].pgn;
            game = new Chess();
            game.load_pgn(pgn);
            moves = game.history({ verbose: true });
            fenList = [];
            let g = new Chess();
            fenList.push(g.fen());
            moves.forEach(m => {
                g.move(m);
                fenList.push(g.fen());
            });
            currentMove = 0;
            board.position(fenList[currentMove]);
            showAnalysis();
        });
}

function prevMove() {
    if (currentMove > 0) currentMove--;
    board.position(fenList[currentMove]);
    showAnalysis();
}

function nextMove() {
    if (currentMove < fenList.length - 1) currentMove++;
    board.position(fenList[currentMove]);
    showAnalysis();
}

function showAnalysis() {
    if (currentMove == 0) {
        document.getElementById('analysis').innerText = "Partita Iniziata";
        document.getElementById('move-icons').innerHTML = "";
    } else {
        const fen = fenList[currentMove - 1];
        const move = moves[currentMove - 1].san;
        fetch('/api/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json'},
            body: JSON.stringify({ fen: fen, move: move })
        })
        .then(resp => resp.json())
        .then(data => {
            document.getElementById('analysis').innerText =
                'Mossa: ' + move + ' - Valutazione: ' + data.eval + ' (' + data.category + ')';
            document.getElementById('move-icons').innerHTML = '';
        });
    }
}

document.addEventListener("DOMContentLoaded", () => {
    board = Chessboard('board', {
        pieceTheme: '/static/img/chesspieces/wikipedia/{piece}.png'
    });
});

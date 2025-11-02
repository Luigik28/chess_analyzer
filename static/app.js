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

function showLoading(show) {
    document.getElementById('loadingBox').style.display = show ? 'block' : 'none';
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
            showLoading(true); // Mostra loading
            batchAnalyze()
                .then(analyses => {
                    analysisList = analyses;
                    board.position(fenList[currentMove]);
                    showAnalysis();
                    showLoading(false); // Nasconde loading
                });
        });
}

function batchAnalyze() {
    // Prepara la lista di FEN prima di ogni mossa e la lista dei SAN move
    let batchFens = fenList.slice(0, moves.length);
    let batchMoves = moves.map(m => m.san);
    return fetch('/api/analyze_batch', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json'},
        body: JSON.stringify({ fen_list: batchFens, move_list: batchMoves })
    })
    .then(resp => resp.json());
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
        // Informazioni già precalcolate
        const moveIdx = currentMove - 1;
        const move = moves[moveIdx].san;
        const data = analysisList[moveIdx];
        document.getElementById('analysis').innerText =
            'Mossa: ' + move + ' - Valutazione: ' + data.bar + ' (' + data.category + ')';
        document.getElementById('move-icons').innerHTML = '';
    }
}

document.addEventListener("DOMContentLoaded", () => {
    board = Chessboard('board', {
        pieceTheme: '/static/img/chesspieces/wikipedia/{piece}.png'
    });
    // Aggiungi box loading in pagina!
    const loadingBox = document.createElement('div');
    loadingBox.id = 'loadingBox';
    loadingBox.innerText = 'Analisi partita in corso...';
    loadingBox.style = 'display:none; position:fixed; left:0; top:0; width:100vw; height:100vh; background:#fffd; color:#333; font-size:2em; text-align:center; padding-top:25vh; z-index:1000;';
    document.body.appendChild(loadingBox);
});

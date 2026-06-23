HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Game Replay</title>
    <style>
        body {
            font-family: 'Inter', sans-serif; background: #121212;
            color: #fff; text-align: center;
        }
        #grid {
            display: grid; grid-template-columns: repeat({cols}, 50px);
            grid-template-rows: repeat({rows}, 50px); gap: 2px;
            margin: 20px auto; width: max-content;
        }
        .cell {
            width: 50px; height: 50px; background: #2a2a2a; display: flex; align-items: center;
            justify-content: center; font-size: 24px; border-radius: 4px;
        }
        .cell.barrier { background: #444; }
        .controls {
            margin: 20px; display: flex; gap: 10px;
            justify-content: center; align-items: center;
        }
        button, select, input {
            padding: 8px 16px; background: #333; color: white; border: none;
            border-radius: 4px; cursor: pointer;
        }
        button:hover { background: #555; }
        .dialogue-box {
            background: #222; padding: 20px; border-radius: 8px; max-width: 600px;
            margin: 0 auto; min-height: 80px;
        }
        .agent-name {
            font-weight: bold; margin-bottom: 8px; color: #aaa; text-transform: uppercase;
        }
        .dialogue-text { font-style: italic; }
        .info-panel {
            display: flex; justify-content: center; gap: 40px; margin: 20px; font-size: 1.2rem;
        }
    </style>
</head>
<body>
    <h1>Cop vs Thief Replay</h1>
    <div class="info-panel">
        <div>Sub-game: <span id="sg-display">1</span></div>
        <div>Turn: <span id="turn-display">0</span></div>
        <div>
            Score - Cop: <span id="score-cop">0</span> | Thief: <span id="score-thief">0</span>
        </div>
    </div>

    <div class="controls">
        <select id="sg-select"></select>
        <button id="btn-back">⏮ Back</button>
        <button id="btn-play">▶ Play/Pause</button>
        <button id="btn-forward">⏭ Forward</button>
        <label>Speed: <input type="range" id="speed" min="1" max="3" value="2"></label>
    </div>

    <div id="grid"></div>

    <div class="dialogue-box">
        <div class="agent-name" id="agent-label">System</div>
        <div class="dialogue-text" id="dialogue-display">Ready to replay.</div>
    </div>

    <script>
        const frames = {frames_json};
        const rows = {rows};
        const cols = {cols};
        let currentFrameIdx = 0;
        let isPlaying = false;
        let playInterval = null;

        let copScore = 0;
        let thiefScore = 0;
        let processedSubgames = new Set();

        const subgames = [...new Set(frames.map(f => f.sub_game))];
        const sgSelect = document.getElementById('sg-select');
        subgames.forEach(sg => {
            const opt = document.createElement('option');
            opt.value = sg; opt.textContent = 'Sub-game ' + sg;
            sgSelect.appendChild(opt);
        });

        const grid = document.getElementById('grid');
        for (let i = 0; i < rows * cols; i++) {
            const cell = document.createElement('div');
            cell.className = 'cell';
            cell.id = 'cell-' + i;
            grid.appendChild(cell);
        }

        function calculateScoresUpTo(frameIdx) {
            copScore = 0;
            thiefScore = 0;
            let currentSg = 1;
            let isCaptured = false;

            for (let i = 0; i <= frameIdx; i++) {
                const f = frames[i];
                if (f.sub_game !== currentSg) {
                    if (isCaptured) {
                        copScore += 20; thiefScore += 5;
                    } else {
                        copScore += 5; thiefScore += 10;
                    }
                    currentSg = f.sub_game;
                    isCaptured = false;
                }

                if (f.cop_pos[0] === f.thief_pos[0] && f.cop_pos[1] === f.thief_pos[1]) {
                    isCaptured = true;
                }
            }
        }

        function renderFrame(idx) {
            if (idx < 0 || idx >= frames.length) return;
            currentFrameIdx = idx;
            const f = frames[idx];

            sgSelect.value = f.sub_game;
            calculateScoresUpTo(idx);

            for (let i = 0; i < rows * cols; i++) {
                const cell = document.getElementById('cell-' + i);
                cell.className = 'cell';
                cell.textContent = '';
            }

            f.barriers.forEach(b => {
                const c = document.getElementById('cell-' + (b[0]*cols + b[1]));
                if (c) { c.className = 'cell barrier'; c.textContent = '🧱'; }
            });

            const tc = document.getElementById('cell-' + (f.thief_pos[0]*cols + f.thief_pos[1]));
            if (tc) tc.textContent = '🦹';

            const cc = document.getElementById('cell-' + (f.cop_pos[0]*cols + f.cop_pos[1]));
            if (cc) cc.textContent = '🚔';

            document.getElementById('sg-display').textContent = f.sub_game;
            document.getElementById('turn-display').textContent = f.turn;
            document.getElementById('agent-label').textContent = f.agent || 'System';
            document.getElementById('dialogue-display').textContent = f.dialogue || '...';
            document.getElementById('score-cop').textContent = copScore;
            document.getElementById('score-thief').textContent = thiefScore;
        }

        function nextFrame() {
            if (currentFrameIdx < frames.length - 1) {
                renderFrame(currentFrameIdx + 1);
            } else {
                pause();
            }
        }

        function prevFrame() {
            if (currentFrameIdx > 0) renderFrame(currentFrameIdx - 1);
        }

        function play() {
            if (isPlaying) return pause();
            isPlaying = true;
            document.getElementById('btn-play').textContent = '⏸ Pause';
            const speedMap = {1: 1000, 2: 500, 3: 200};
            const ms = speedMap[document.getElementById('speed').value] || 500;
            playInterval = setInterval(nextFrame, ms);
        }

        function pause() {
            isPlaying = false;
            document.getElementById('btn-play').textContent = '▶ Play';
            clearInterval(playInterval);
        }

        document.getElementById('btn-play').addEventListener('click', play);
        document.getElementById('btn-forward').addEventListener('click', () => {
            pause(); nextFrame();
        });
        document.getElementById('btn-back').addEventListener('click', () => {
            pause(); prevFrame();
        });

        sgSelect.addEventListener('change', (e) => {
            pause();
            const targetSg = parseInt(e.target.value);
            const idx = frames.findIndex(f => f.sub_game === targetSg);
            if (idx !== -1) renderFrame(idx);
        });

        document.getElementById('speed').addEventListener('change', () => {
            if (isPlaying) { pause(); play(); }
        });

        if (frames.length > 0) renderFrame(0);
    </script>
</body>
</html>
"""

import json
import os
import subprocess


def update_config(use_sweep_cop):
    with open('config/config.json') as f:
        data = json.load(f)
    data['num_games'] = 6
    data['use_sweep_cop'] = use_sweep_cop
    with open('config/config.json', 'w') as f:
        json.dump(data, f, indent=2)

print("Starting full pipeline (2 Cops, 1 Thief, 6 games each)...")

print("=> Running Cop 1 (ManhattanHeuristic)...")
update_config(False)
env = {**os.environ, "PYTHONUNBUFFERED": "1"}
subprocess.run(["uv", "run", "python", "main.py"], check=True, env=env)
os.rename("results/replay.html", "results/replay_cop1.html")

print("=> Running Cop 2 (Wall-Builder without cheating)...")
update_config(True)
subprocess.run(["uv", "run", "python", "main.py"], check=True, env=env)
os.rename("results/replay.html", "results/replay_cop2.html")

print("Pipeline complete! Replays saved to results/replay_cop1.html and results/replay_cop2.html")

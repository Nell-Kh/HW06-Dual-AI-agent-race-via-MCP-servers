from unittest.mock import MagicMock, patch

from cop_thief.services.orchestrator import Orchestrator


def mock_dependencies():
    config = MagicMock()
    config.get_num_games.return_value = 6
    config.get_max_moves.return_value = 5
    config.get_max_barriers.return_value = 5

    llm = MagicMock()
    ret_dict = {
        "action": "up",
        "dialogue": "hi",
        "prompt_tokens": 10,
        "completion_tokens": 10,
        "model": "gpt",
    }
    llm.generate_move.return_value = ret_dict
    llm.generate_barrier_decision.return_value = ret_dict

    cop_server = MagicMock()
    thief_server = MagicMock()

    score_mgr = MagicMock()
    score_mgr.get_scores.return_value = {"cop": 0, "thief": 0}

    q_table = MagicMock()
    partial_obs = MagicMock()
    cost_tracker = MagicMock()
    transcript_writer = MagicMock()

    return (
        config,
        llm,
        cop_server,
        thief_server,
        score_mgr,
        q_table,
        partial_obs,
        cost_tracker,
        transcript_writer,
    )


@patch("cop_thief.services.orchestrator.TrainingEngine")
@patch("cop_thief.services.orchestrator.GameState")
def test_run_game_runs_6_subgames(mock_gs, mock_te):
    deps = mock_dependencies()
    game_instance = MagicMock()
    game_instance.cop.row = 2
    game_instance.cop.col = 2
    game_instance.thief.row = 0
    game_instance.thief.col = 0
    game_instance.grid.rows = 5
    game_instance.grid.cols = 5
    mock_gs.return_value = game_instance
    orch = Orchestrator(*deps)
    res = orch.run_game()
    assert len(res["sub_games"]) == 6


@patch("cop_thief.services.orchestrator.TrainingEngine")
@patch("cop_thief.services.orchestrator.GameState")
def test_thief_moves_first_each_turn(mock_gs, mock_te):
    deps = mock_dependencies()
    game_instance = MagicMock()
    game_instance.cop.row = 2
    game_instance.cop.col = 2
    game_instance.thief.row = 0
    game_instance.thief.col = 0
    game_instance.grid.rows = 5
    game_instance.grid.cols = 5
    mock_gs.return_value = game_instance
    orch = Orchestrator(*deps)
    orch.execute_turn = MagicMock(return_value="up")
    orch.run_sub_game(1)
    calls = orch.execute_turn.call_args_list
    assert calls[0][0][0] == "thief"


@patch("cop_thief.services.orchestrator.TrainingEngine")
@patch("cop_thief.services.orchestrator.GameState")
def test_cop_wins_updates_score_correctly(mock_gs, mock_te):
    deps = mock_dependencies()
    score_mgr = deps[4]

    game_instance = MagicMock()
    game_instance.cop.row = 2
    game_instance.cop.col = 2
    game_instance.thief.row = 2
    game_instance.thief.col = 2
    game_instance.grid.rows = 5
    game_instance.grid.cols = 5
    mock_gs.return_value = game_instance

    orch = Orchestrator(*deps)
    res = orch.run_sub_game(1)

    score_mgr.update_scores.assert_called_with("cop")
    assert res["winner"] == "cop"


@patch("cop_thief.services.orchestrator.TrainingEngine")
@patch("cop_thief.services.orchestrator.GameState")
def test_thief_wins_updates_score_correctly(mock_gs, mock_te):
    deps = mock_dependencies()
    score_mgr = deps[4]

    game_instance = MagicMock()
    game_instance.cop.row = 0
    game_instance.cop.col = 0
    game_instance.thief.row = 4
    game_instance.thief.col = 4
    game_instance.grid.rows = 5
    game_instance.grid.cols = 5
    mock_gs.return_value = game_instance

    orch = Orchestrator(*deps)
    orch.execute_turn = MagicMock(return_value="up")
    res = orch.run_sub_game(1)

    score_mgr.update_scores.assert_called_with("thief")
    assert res["winner"] == "thief"


@patch("cop_thief.services.orchestrator.GameState")
def test_transcript_recorded_each_move(mock_gs):
    deps = mock_dependencies()
    transcript_writer = deps[8]

    game_instance = MagicMock()
    game_instance.cop.row = 0
    game_instance.cop.col = 0
    game_instance.thief.row = 4
    game_instance.thief.col = 4
    game_instance.grid.rows = 5
    game_instance.grid.cols = 5

    orch = Orchestrator(*deps)
    orch.execute_turn(
        "thief", game_instance.thief, game_instance.cop, None, game_instance, MagicMock(), 1, 1
    )

    assert transcript_writer.record_move.called


@patch("cop_thief.services.orchestrator.GameState")
def test_cost_tracked_each_llm_call(mock_gs):
    deps = mock_dependencies()
    cost_tracker = deps[7]

    game_instance = MagicMock()
    game_instance.cop.row = 0
    game_instance.cop.col = 0
    game_instance.thief.row = 4
    game_instance.thief.col = 4
    game_instance.grid.rows = 5
    game_instance.grid.cols = 5

    orch = Orchestrator(*deps)
    orch.execute_turn(
        "thief", game_instance.thief, game_instance.cop, None, game_instance, MagicMock(), 1, 1
    )

    cost_tracker.record_call.assert_called_with(10, 10, "gpt")


@patch("cop_thief.services.orchestrator.GameState")
def test_partial_observer_used_not_full_board(mock_gs):
    deps = mock_dependencies()
    partial_obs = deps[6]

    game_instance = MagicMock()
    game_instance.cop.row = 0
    game_instance.cop.col = 0
    game_instance.thief.row = 4
    game_instance.thief.col = 4
    game_instance.grid.rows = 5
    game_instance.grid.cols = 5

    orch = Orchestrator(*deps)
    orch.execute_turn(
        "thief", game_instance.thief, game_instance.cop, None, game_instance, MagicMock(), 1, 1
    )

    assert partial_obs.generate_description.called


@patch("cop_thief.services.orchestrator.GameState")
def test_sub_game_result_has_required_keys(mock_gs):
    deps = mock_dependencies()
    orch = Orchestrator(*deps)
    res = orch._build_sub_game_result(1, "cop", 5)

    assert "sub_game_number" in res
    assert "winner" in res
    assert "num_moves" in res
    assert "cop_score" in res
    assert "thief_score" in res

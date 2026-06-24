from unittest.mock import MagicMock

from cop_thief.services.turn_executor import TurnExecutor


def mock_dependencies():
    llm = MagicMock()
    q_table = MagicMock()
    partial_obs = MagicMock()
    cost_tracker = MagicMock()
    transcript_writer = MagicMock()
    html_replay = MagicMock()
    config = MagicMock()
    config.get_max_barriers.return_value = 5
    return llm, q_table, partial_obs, cost_tracker, transcript_writer, html_replay, config


def test_update_belief_state():
    deps = mock_dependencies()
    executor = TurnExecutor(*deps)

    # Initially None
    assert executor.last_seen["cop"] is None

    # Test sighting
    executor._update_belief_state(
        "cop", "You are at center. You see the opponent 3 steps north-east from you."
    )
    assert executor.last_seen["cop"] == {"direction": "north-east", "steps": 3, "turns_since": 0}

    # Test 'No sign' increments turns_since
    executor._update_belief_state(
        "cop", "You are at center. No sign of the opponent within your view."
    )
    assert executor.last_seen["cop"] == {"direction": "north-east", "steps": 3, "turns_since": 1}

    # Test another 'No sign'
    executor._update_belief_state(
        "cop", "You are at center. No sign of the opponent within your view."
    )
    assert executor.last_seen["cop"] == {"direction": "north-east", "steps": 3, "turns_since": 2}

    # Test new sighting resets turns_since and updates info
    executor._update_belief_state(
        "cop", "You are at center. You see the opponent 1 steps west from you."
    )
    assert executor.last_seen["cop"] == {"direction": "west", "steps": 1, "turns_since": 0}

    # Test 'No sign' for an agent that has never seen the opponent
    assert executor.last_seen["thief"] is None
    executor._update_belief_state(
        "thief", "You are at center. No sign of the opponent within your view."
    )
    assert executor.last_seen["thief"] is None

    # Test reset clears it
    executor.reset()
    assert executor.last_seen["cop"] is None
    assert executor.last_seen["thief"] is None

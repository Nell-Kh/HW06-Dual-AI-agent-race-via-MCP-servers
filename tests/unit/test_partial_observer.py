from unittest.mock import MagicMock

import pytest

from cop_thief.services.grid import Grid
from cop_thief.services.partial_observer import PartialObserver
from cop_thief.shared.config_loader import ConfigLoader


@pytest.fixture
def mock_config():
    config = MagicMock(spec=ConfigLoader)
    config._config = {"vision_radius": 2}
    config.get_grid_size.return_value = [5, 5]
    return config


def test_partial_observer_init(mock_config):
    obs = PartialObserver(mock_config)
    assert obs.radius == 2


def test_get_visible_state(mock_config):
    obs = PartialObserver(mock_config)
    grid = Grid(mock_config)
    grid.place_barrier(0, 0)

    state = obs.get_visible_state(grid, (2, 2))
    assert state[(2, 2)] == 0
    assert state[(0, 0)] == 1

    state = obs.get_visible_state(grid, (4, 4))
    assert state[(0, 0)] == "unknown"


def test_generate_description_movement(mock_config):
    obs = PartialObserver(mock_config)
    grid = Grid(mock_config)

    desc = obs.generate_description("cop", grid, (2, 2), (2, 4))
    assert "movement 2 steps east" in desc
    assert "cannot confirm position" in desc


def test_generate_description_barrier(mock_config):
    obs = PartialObserver(mock_config)
    grid = Grid(mock_config)
    grid.place_barrier(3, 2)

    desc = obs.generate_description("cop", grid, (2, 2), (4, 4))
    assert "barrier to your south" in desc


def test_generate_description_outside_radius(mock_config):
    obs = PartialObserver(mock_config)
    grid = Grid(mock_config)

    desc = obs.generate_description("cop", grid, (0, 0), (4, 4))
    assert "You cannot confirm opponent position" in desc

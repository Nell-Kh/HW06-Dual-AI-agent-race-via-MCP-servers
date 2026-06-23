
from cop_thief.services.html_replay import HTMLReplay
from cop_thief.shared.config_loader import ConfigLoader


def test_add_frame_stores_correctly():
    config = ConfigLoader("config/config.json")
    config._config = {"grid_size": [5, 5]}
    replay = HTMLReplay(config)
    replay.add_frame(1, 1, "cop", (0, 0), (4, 4), [(1, 1)], "up", "hello")
    assert len(replay.frames) == 1
    f = replay.frames[0]
    assert f["sub_game"] == 1
    assert f["agent"] == "cop"
    assert f["cop_pos"] == [0, 0]


def test_generate_html_creates_file(tmp_path):
    config = ConfigLoader("config/config.json")
    config._config = {"grid_size": [5, 5]}
    replay = HTMLReplay(config)
    out = tmp_path / "test.html"
    replay.generate_html(str(out))
    assert out.exists()


def test_html_contains_grid_elements(tmp_path):
    config = ConfigLoader("config/config.json")
    config._config = {"grid_size": [5, 5]}
    replay = HTMLReplay(config)
    out = tmp_path / "test.html"
    replay.generate_html(str(out))
    content = out.read_text()
    assert "grid" in content
    assert "<html" in content


def test_html_is_self_contained(tmp_path):
    config = ConfigLoader("config/config.json")
    config._config = {"grid_size": [5, 5]}
    replay = HTMLReplay(config)
    out = tmp_path / "test.html"
    replay.generate_html(str(out))
    content = out.read_text()
    assert "<script src=" not in content
    assert "<link rel=" not in content

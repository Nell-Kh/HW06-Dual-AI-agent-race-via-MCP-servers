import json
from unittest.mock import MagicMock

from cop_thief.services.transcript import TranscriptWriter


def test_record_move_appends_to_transcript():
    writer = TranscriptWriter(MagicMock())
    writer.record_move(1, 1, "cop", "obs", "up", "hello")
    assert len(writer.get_transcript()) == 1


def test_transcript_has_required_fields():
    writer = TranscriptWriter(MagicMock())
    writer.record_move(1, 1, "cop", "obs", "up", "hello")
    rec = writer.get_transcript()[0]

    assert "sub_game" in rec
    assert "turn" in rec
    assert "agent" in rec
    assert "observation" in rec
    assert "action" in rec
    assert "dialogue" in rec
    assert "timestamp" in rec


def test_save_creates_jsonl_file(tmp_path):
    writer = TranscriptWriter(MagicMock())
    p = tmp_path / "test.jsonl"
    writer.log_path = str(p)
    writer.record_move(1, 1, "cop", "obs", "up", "hello")
    writer.save()
    assert p.exists()
    with open(p) as f:
        line = f.readline()
        data = json.loads(line)
        assert data["agent"] == "cop"

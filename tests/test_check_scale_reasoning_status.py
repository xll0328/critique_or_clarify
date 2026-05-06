from __future__ import annotations

import fcntl
import importlib.util
import os
from pathlib import Path


def load_status_module():
    script_path = Path(__file__).resolve().parents[1] / "scripts" / "check_scale_reasoning_status.py"
    spec = importlib.util.spec_from_file_location("check_scale_reasoning_status", script_path)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_model_status_marks_old_partial_file_as_stalled(tmp_path: Path) -> None:
    status = load_status_module()
    shard_path = tmp_path / "model-00001-of-000002.safetensors"
    shard_path.write_bytes(b"0" * 40)
    os.utime(shard_path, (1_000.0, 1_000.0))

    state, progress, detail = status.model_status(
        shard_path,
        shard_path,
        100,
        now_seconds=1_000.0 + status.STALE_AFTER_SECONDS + 1,
    )

    assert state == "stalled"
    assert progress == "40.0%"
    assert "missing 60 B" in detail


def test_model_status_keeps_active_part_as_downloading(tmp_path: Path) -> None:
    status = load_status_module()
    shard_path = tmp_path / "model-00002-of-000002.safetensors"
    part_path = tmp_path / "model-00002-of-000002.safetensors.part"
    lock_path = tmp_path / "model-00002-of-000002.safetensors.lock"
    shard_path.write_bytes(b"0" * 40)
    part_path.write_bytes(b"1" * 20)

    with lock_path.open("w", encoding="utf-8") as lock_handle:
        fcntl.flock(lock_handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        state, progress, detail = status.model_status(shard_path, shard_path, 100, now_seconds=0)

    assert state == "downloading"
    assert progress == "60.0%"
    assert "missing 40 B" in detail


def test_model_status_ignores_stale_part_file(tmp_path: Path) -> None:
    status = load_status_module()
    shard_path = tmp_path / "model-00002-of-000002.safetensors"
    part_path = tmp_path / "model-00002-of-000002.safetensors.part"
    shard_path.write_bytes(b"0" * 40)
    part_path.write_bytes(b"1" * 20)
    os.utime(shard_path, (1_000.0, 1_000.0))
    os.utime(part_path, (1_000.0, 1_000.0))

    state, progress, detail = status.model_status(
        shard_path,
        shard_path,
        100,
        now_seconds=1_000.0 + status.STALE_AFTER_SECONDS + 1,
    )

    assert state == "stalled"
    assert progress == "40.0%"
    assert "missing 60 B" in detail
    assert "inactive part 20 B ignored" in detail


def test_model_status_marks_locked_direct_resume_as_downloading(tmp_path: Path) -> None:
    status = load_status_module()
    shard_path = tmp_path / "model-00002-of-000002.safetensors"
    lock_path = tmp_path / "model-00002-of-000002.safetensors.lock"
    shard_path.write_bytes(b"0" * 40)
    os.utime(shard_path, (1_000.0, 1_000.0))

    with lock_path.open("w", encoding="utf-8") as lock_handle:
        fcntl.flock(lock_handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        state, progress, detail = status.model_status(
            shard_path,
            shard_path,
            100,
            now_seconds=1_000.0,
        )

    assert state == "downloading"
    assert progress == "40.0%"
    assert "missing 60 B" in detail


def test_model_status_marks_oversized_file_as_corrupt(tmp_path: Path) -> None:
    status = load_status_module()
    shard_path = tmp_path / "model-00001-of-000002.safetensors"
    shard_path.write_bytes(b"0" * 120)

    state, progress, detail = status.model_status(shard_path, shard_path, 100)

    assert state == "oversized"
    assert progress == "120.0%"
    assert "exceeds expected by 20 B" in detail

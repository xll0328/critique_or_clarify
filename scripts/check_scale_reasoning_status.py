from __future__ import annotations

import fcntl
import json
import time
from pathlib import Path


REPO_ROOT = Path("/data/sony/emnlp2026_critique_or_clarify")
STALE_AFTER_SECONDS = 15 * 60
MODEL_ROWS = [
    (
        "Qwen2.5-1.5B model",
        Path("/data/sony/model_cache/Qwen2.5-1.5B-Instruct/model.safetensors"),
        Path("/data/sony/model_cache/Qwen2.5-1.5B-Instruct/model.safetensors.incomplete"),
        3_087_467_144,
    ),
    (
        "DeepSeek-R1-Qwen-7B shard1",
        Path("/data/sony/model_cache_reasoning/DeepSeek-R1-Distill-Qwen-7B/model-00001-of-000002.safetensors"),
        Path("/data/sony/model_cache_reasoning/DeepSeek-R1-Distill-Qwen-7B/model-00001-of-000002.safetensors"),
        8_606_596_466,
    ),
    (
        "DeepSeek-R1-Qwen-7B shard2",
        Path("/data/sony/model_cache_reasoning/DeepSeek-R1-Distill-Qwen-7B/model-00002-of-000002.safetensors"),
        Path("/data/sony/model_cache_reasoning/DeepSeek-R1-Distill-Qwen-7B/model-00002-of-000002.safetensors"),
        6_624_675_384,
    ),
]
METRIC_ROWS = [
    (
        "Qwen2.5-1.5B dev metrics",
        REPO_ROOT / "outputs/day1/qwen25_15b_day1_dev_metrics.json",
    ),
    (
        "Qwen2.5-1.5B quick+stale metrics",
        REPO_ROOT / "outputs/day1/qwen25_15b_day1_quick_plus_stale_grounded_metrics.json",
    ),
    (
        "DeepSeek-R1-Qwen-7B dev metrics",
        REPO_ROOT / "outputs/day1/deepseek_r1_qwen7b_day1_dev_useronlyfixed_reparsed_metrics.json",
    ),
    (
        "DeepSeek-R1-Qwen-7B quick+stale metrics",
        REPO_ROOT / "outputs/day1/deepseek_r1_qwen7b_day1_quick_plus_stale_useronlyfixed_reparsed_metrics.json",
    ),
]
REPORT_ROWS = [
    (
        "Scale/reasoning report",
        REPO_ROOT / "experiments/day1/day1_scale_reasoning_comparison.md",
    ),
    (
        "Scale/reasoning CI report",
        REPO_ROOT / "experiments/day1/day1_scale_reasoning_ci.md",
    ),
    (
        "Quick+stale report",
        REPO_ROOT / "experiments/day1/day1_quick_plus_stale_grounded_comparison.md",
    ),
]


def format_bytes(num_bytes: int) -> str:
    units = ["B", "KB", "MB", "GB", "TB"]
    value = float(num_bytes)
    for unit in units:
        if value < 1024 or unit == units[-1]:
            if unit == "B":
                return f"{int(value)} {unit}"
            return f"{value:.1f} {unit}"
        value /= 1024
    raise AssertionError("unreachable")


def model_status(
    final_path: Path,
    resume_path: Path,
    expected_bytes: int,
    *,
    now_seconds: float | None = None,
) -> tuple[str, str, str]:
    now = time.time() if now_seconds is None else now_seconds
    if final_path.exists():
        size = final_path.stat().st_size
        if size == expected_bytes:
            return "ready", "100.0%", f"{format_bytes(size)} / {format_bytes(expected_bytes)}"
        if size > expected_bytes:
            extra_bytes = size - expected_bytes
            return (
                "oversized",
                f"{100 * size / expected_bytes:.1f}%",
                f"{format_bytes(size)} / {format_bytes(expected_bytes)} (exceeds expected by {format_bytes(extra_bytes)})",
            )
    committed_size = resume_path.stat().st_size if resume_path.exists() else 0
    committed_mtime = resume_path.stat().st_mtime if resume_path.exists() else 0.0
    lock_path = Path(f"{resume_path}.lock")
    resume_lock_held = lock_is_held(lock_path)
    part_path = Path(f"{resume_path}.part")
    active_size = part_path.stat().st_size if part_path.exists() else 0
    part_is_active = (
        active_size > 0
        and now - part_path.stat().st_mtime < STALE_AFTER_SECONDS
        and resume_lock_held
    )
    direct_resume_active = (
        not part_is_active
        and committed_size > 0
        and resume_lock_held
        and now - committed_mtime < STALE_AFTER_SECONDS
    )
    displayed_size = committed_size + active_size if part_is_active else committed_size
    total_size = displayed_size
    if total_size == 0:
        return "pending", "0.0%", f"0 B / {format_bytes(expected_bytes)}"
    state = (
        "downloading"
        if part_is_active or direct_resume_active
        else stale_or_partial_state(final_path, resume_path, now)
    )
    missing_bytes = max(expected_bytes - total_size, 0)
    inactive_part_note = ""
    if active_size > 0 and not part_is_active:
        inactive_part_note = f"; inactive part {format_bytes(active_size)} ignored"
    return (
        state,
        f"{100 * total_size / expected_bytes:.1f}%",
        f"{format_bytes(total_size)} / {format_bytes(expected_bytes)} (missing {format_bytes(missing_bytes)}){inactive_part_note}",
    )


def lock_is_held(lock_path: Path) -> bool:
    if not lock_path.exists():
        return False
    with lock_path.open("a", encoding="utf-8") as handle:
        try:
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return True
        fcntl.flock(handle, fcntl.LOCK_UN)
        return False


def stale_or_partial_state(final_path: Path, resume_path: Path, now_seconds: float | None) -> str:
    latest_mtime = max(
        (path.stat().st_mtime for path in (final_path, resume_path) if path.exists()),
        default=None,
    )
    if latest_mtime is None:
        return "partial"
    now = time.time() if now_seconds is None else now_seconds
    if now - latest_mtime >= STALE_AFTER_SECONDS:
        return "stalled"
    return "partial"


def metric_status(path: Path) -> tuple[str, str, str]:
    if not path.exists():
        return "pending", "-", "-"
    payload = json.loads(path.read_text(encoding="utf-8"))
    summary = payload["summary"]
    return (
        "ready",
        f"acc={summary['action_accuracy']:.4f}",
        f"utility={summary['avg_utility']:.4f}",
    )


def report_status(path: Path) -> tuple[str, str, str]:
    if not path.exists():
        return "missing", "-", "-"
    lines = path.read_text(encoding="utf-8").splitlines()
    title = lines[0].removeprefix("# ").strip() if lines else "unknown"
    pending_line = next((line for line in lines if line.startswith("Pending checkpoints:")), "")
    state = "snapshot" if "Snapshot" in title else "comparison"
    detail = pending_line.removeprefix("Pending checkpoints: ").strip() or "-"
    return state, title, detail


def print_table(rows: list[tuple[str, str, str, str]]) -> None:
    print("| Artifact | State | Progress | Detail |")
    print("| --- | --- | --- | --- |")
    for artifact, state, progress, detail in rows:
        print(f"| {artifact} | {state} | {progress} | {detail} |")


def main() -> None:
    rows: list[tuple[str, str, str, str]] = []
    for label, final_path, partial_path, expected_bytes in MODEL_ROWS:
        state, progress, detail = model_status(final_path, partial_path, expected_bytes)
        rows.append((label, state, progress, detail))

    for label, path in METRIC_ROWS:
        state, progress, detail = metric_status(path)
        rows.append((label, state, progress, detail))

    for label, path in REPORT_ROWS:
        state, progress, detail = report_status(path)
        rows.append((label, state, progress, detail))

    print_table(rows)


if __name__ == "__main__":
    main()

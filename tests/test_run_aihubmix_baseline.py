from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


def load_module():
    script_path = Path(__file__).resolve().parents[1] / "scripts" / "run_aihubmix_baseline.py"
    script_dir = str(script_path.parent)
    if script_dir not in sys.path:
        sys.path.insert(0, script_dir)
    spec = importlib.util.spec_from_file_location("run_aihubmix_baseline", script_path)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_extract_content_supports_string_payload() -> None:
    module = load_module()
    payload = {"choices": [{"message": {"content": "{\"action\":\"answer\",\"response\":\"42\"}"}}]}
    assert module.extract_content(payload) == "{\"action\":\"answer\",\"response\":\"42\"}"


def test_extract_content_supports_text_parts_payload() -> None:
    module = load_module()
    payload = {
        "choices": [
            {
                "message": {
                    "content": [
                        {"type": "text", "text": "{\"action\":\"challenge\","},
                        {"type": "text", "text": "\"response\":\"bad premise\"}"},
                    ]
                }
            }
        ]
    }
    assert module.extract_content(payload) == "{\"action\":\"challenge\",\n\"response\":\"bad premise\"}"

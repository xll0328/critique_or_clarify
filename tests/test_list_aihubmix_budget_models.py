from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


def load_module():
    script_path = Path(__file__).resolve().parents[1] / "scripts" / "list_aihubmix_budget_models.py"
    script_dir = str(script_path.parent)
    if script_dir not in sys.path:
        sys.path.insert(0, script_dir)
    spec = importlib.util.spec_from_file_location("list_aihubmix_budget_models", script_path)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_rank_rows_sorts_by_blended_price() -> None:
    module = load_module()
    payload = {
        "data": [
            {"model_id": "m-expensive", "types": "llm", "pricing": {"input": "0.5", "output": "0.6"}},
            {"model_id": "m-cheap", "types": "llm", "pricing": {"input": "0.01", "output": "0.02"}},
            {"model_id": "m-mid", "types": "llm", "pricing": {"input": "0.1", "output": "0.1"}},
        ]
    }
    rows = module.rank_rows(payload, top_k=3)
    assert [row["model_id"] for row in rows] == ["m-cheap", "m-mid", "m-expensive"]


def test_render_markdown_contains_expected_columns() -> None:
    module = load_module()
    rows = [
        module.ModelRow(
            model_id="m-a",
            types="llm",
            input_price=0.01,
            output_price=0.03,
            blended_price=0.02,
            features="structured_outputs",
            context_length=128000,
            max_output=4096,
        )
    ]
    markdown = module.render_markdown(rows, "llm", ["structured_outputs"])
    assert "AIHubMix Budget Model Ranking" in markdown
    assert "| Rank | Model | Input Price | Output Price | Blended | Features | Context | Max Output |" in markdown
    assert "`m-a`" in markdown

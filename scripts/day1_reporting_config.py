from __future__ import annotations


EXPECTED_SCALE_REASONING_MODELS = [
    "Qwen2.5-0.5B-Instruct",
    "Qwen2.5-1.5B-Instruct",
    "DeepSeek-R1-Distill-Qwen-1.5B",
    "Qwen2.5-Coder-7B-Instruct",
    "DeepSeek-R1-Distill-Qwen-7B",
]


def pending_scale_reasoning_models(runs: list[dict]) -> list[str]:
    completed = {run["model"] for run in runs}
    return [model for model in EXPECTED_SCALE_REASONING_MODELS if model not in completed]


def format_markdown_model_list(models: list[str]) -> str:
    return ", ".join(f"`{model}`" for model in models)


def format_latex_model_list(models: list[str]) -> str:
    return ", ".join(rf"\texttt{{{model}}}" for model in models)

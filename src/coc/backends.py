from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any

from coc.prompts import build_messages
from coc.schema import Action, Example, Prediction


class BaseBackend:
    def predict(self, example: Example) -> Prediction:
        raise NotImplementedError


class HeuristicBackend(BaseBackend):
    def predict(self, example: Example) -> Prediction:
        metadata = example.metadata

        if metadata.get("requires_clarification"):
            action = Action.ASK
            response = (
                example.gold_response
                or "I need a bit more detail before I can help. Could you clarify the missing information?"
            )
            confidence = 0.82
        elif metadata.get("has_false_premise") or metadata.get("has_stale_premise"):
            action = Action.CHALLENGE
            response = (
                example.gold_response
                or "The question contains an incorrect or outdated premise, so I should correct that before answering."
            )
            confidence = 0.88
        elif metadata.get("has_irreconcilable_conflict") or metadata.get("is_unanswerable"):
            action = Action.ABSTAIN
            response = (
                example.gold_response
                or "I do not have enough reliable evidence to answer safely."
            )
            confidence = 0.79
        else:
            action = Action.ANSWER
            response = example.gold_answer or ""
            confidence = 0.93

        return Prediction(
            example_id=example.id,
            action=action,
            response=response,
            confidence=confidence,
            raw_output="heuristic",
            metadata={"backend": "heuristic"},
        )


@dataclass(slots=True)
class GenerationConfig:
    model_name: str
    prompt_style: str = "main"
    max_new_tokens: int = 160
    temperature: float = 0.0
    top_p: float = 1.0
    device_map: str = "auto"
    dtype: str = "auto"
    trust_remote_code: bool = False
    use_safetensors: bool = True
    local_files_only: bool = False
    include_system_prompt: bool = True
    assistant_prefix: str = ""
    seed: int | None = None


class TransformersBackend(BaseBackend):
    def __init__(self, config: GenerationConfig) -> None:
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer

        self.config = config
        self.torch = torch
        dtype = _resolve_dtype(torch, config.dtype)
        self.tokenizer = AutoTokenizer.from_pretrained(
            config.model_name,
            trust_remote_code=config.trust_remote_code,
            local_files_only=config.local_files_only,
        )
        try:
            self.model = AutoModelForCausalLM.from_pretrained(
                config.model_name,
                dtype=dtype,
                device_map=config.device_map,
                trust_remote_code=config.trust_remote_code,
                use_safetensors=config.use_safetensors,
                local_files_only=config.local_files_only,
            )
        except ValueError as exc:
            if "torch.load" in str(exc):
                raise ValueError(
                    "Model loading failed because this environment uses torch < 2.6 and the checkpoint "
                    "appears to require PyTorch .bin weights. Use a safetensors checkpoint "
                    "(for example Qwen/Qwen2.5-* or SmolLM2 instruct variants) or upgrade torch."
                ) from exc
            raise
        if self.tokenizer.pad_token_id is None and self.tokenizer.eos_token_id is not None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

    def predict(self, example: Example) -> Prediction:
        messages = build_messages(
            example,
            style=self.config.prompt_style,
            include_system_prompt=self.config.include_system_prompt,
        )
        prompt = self._render_prompt(messages)
        inputs = self.tokenizer(prompt, return_tensors="pt")
        device = next(self.model.parameters()).device
        inputs = {key: value.to(device) for key, value in inputs.items()}

        if self.config.seed is not None:
            self.torch.manual_seed(self.config.seed)
            if self.torch.cuda.is_available():
                self.torch.cuda.manual_seed_all(self.config.seed)

        do_sample = self.config.temperature > 0.0
        generate_kwargs = {
            "max_new_tokens": self.config.max_new_tokens,
            "do_sample": do_sample,
            "pad_token_id": self.tokenizer.pad_token_id,
            "eos_token_id": self.tokenizer.eos_token_id,
        }
        if do_sample:
            generate_kwargs["temperature"] = self.config.temperature
            generate_kwargs["top_p"] = self.config.top_p

        with self.torch.inference_mode():
            generated = self.model.generate(**inputs, **generate_kwargs)

        new_tokens = generated[0, inputs["input_ids"].shape[-1] :]
        raw_output = self.tokenizer.decode(new_tokens, skip_special_tokens=True).strip()
        prediction = parse_prediction(raw_output, example.id)
        prediction.metadata["backend"] = "transformers"
        prediction.metadata["model_name"] = self.config.model_name
        return prediction

    def _render_prompt(self, messages: list[dict[str, str]]) -> str:
        if hasattr(self.tokenizer, "apply_chat_template"):
            try:
                rendered = self.tokenizer.apply_chat_template(
                    messages,
                    tokenize=False,
                    add_generation_prompt=True,
                )
                return rendered + self.config.assistant_prefix
            except Exception:
                pass
        rendered = "\n\n".join(f"{message['role'].upper()}:\n{message['content']}" for message in messages)
        if self.config.assistant_prefix:
            rendered += f"\n\nASSISTANT:\n{self.config.assistant_prefix}"
        return rendered


def parse_prediction(raw_output: str, example_id: str) -> Prediction:
    payload = extract_first_json_object(raw_output)
    if isinstance(payload, dict):
        action = _coerce_action(payload.get("action"))
        response = str(payload.get("response", "")).strip()
        confidence = _coerce_confidence(payload.get("confidence"))
        return Prediction(
            example_id=example_id,
            action=action,
            response=response,
            confidence=confidence,
            raw_output=raw_output,
            metadata={"parsed_as": "json"},
        )

    final_response = _extract_final_response(raw_output)
    return Prediction(
        example_id=example_id,
        action=_infer_action(raw_output),
        response=final_response.strip(),
        confidence=None,
        raw_output=raw_output,
        metadata={"parsed_as": "fallback"},
    )


def extract_first_json_object(text: str) -> dict[str, Any] | None:
    decoder = json.JSONDecoder()
    for index, char in enumerate(text):
        if char != "{":
            continue
        try:
            candidate, _ = decoder.raw_decode(text[index:])
        except json.JSONDecodeError:
            continue
        if isinstance(candidate, dict):
            return candidate
    return None


def _infer_action(text: str) -> Action:
    final_response = _extract_final_response(text)
    explicit_action = _infer_action_from_explicit_declaration(final_response)
    if explicit_action is None and final_response != text:
        explicit_action = _infer_action_from_explicit_declaration(text)
    if explicit_action is not None:
        return explicit_action
    heuristic_action = _infer_action_from_final_response(final_response)
    if heuristic_action is not None:
        return heuristic_action
    lowered = final_response.lower()
    for action in Action:
        if re.search(rf"\b{action.value}\b", lowered):
            return action
    return Action.ABSTAIN


def _extract_final_response(text: str) -> str:
    stripped = text.strip()
    if "</think>" not in stripped:
        return stripped
    tail = stripped.rsplit("</think>", 1)[1].strip()
    return tail or stripped


def _infer_action_from_final_response(text: str) -> Action | None:
    lowered = text.lower().strip()
    if not lowered:
        return None

    ask_context_markers = (
        "follow-up question",
        "follow up question",
        "underspecified",
        "under-specified",
        "needs clarification",
        "need clarification",
        "requires clarification",
        "request clarification",
    )
    if any(marker in lowered for marker in ask_context_markers):
        return Action.ASK

    ask_markers = (
        "could you clarify",
        "can you clarify",
        "please clarify",
        "what do you mean",
        "which one",
        "what specific",
        "can you provide",
        "could you provide",
        "need more information",
        "i need more information",
        "i need a bit more detail",
        "follow-up question",
    )
    sentences = [sentence.strip() for sentence in re.split(r"(?<=[.!?])\s+", lowered) if sentence.strip()]
    if sentences and sentences[-1].endswith("?"):
        return Action.ASK
    if any(sentence.startswith(marker) for sentence in sentences for marker in ask_markers):
        return Action.ASK

    challenge_markers = (
        "incorrect premise",
        "false premise",
        "outdated premise",
        "stale premise",
        "that premise is incorrect",
        "that premise is wrong",
        "the premise is wrong",
        "the premise is incorrect",
        "the claim is incorrect",
        "that is incorrect",
        "that's incorrect",
        "that is wrong",
        "that's wrong",
        "contradicts",
        "conflicts with",
    )
    if any(marker in lowered for marker in challenge_markers):
        return Action.CHALLENGE

    abstain_markers = (
        "not enough information",
        "insufficient information",
        "insufficient evidence",
        "not enough evidence",
        "cannot determine",
        "can't determine",
        "cannot answer",
        "can't answer",
        "unable to answer",
        "i don't know",
        "i do not know",
        "unclear from the provided",
        "conflicting evidence",
        "evidence conflicts",
    )
    if any(marker in lowered for marker in abstain_markers):
        return Action.ABSTAIN

    if "</think>" in text or _looks_like_final_answer(lowered):
        return Action.ANSWER
    return None


def _looks_like_final_answer(text: str) -> bool:
    if not text or "?" in text:
        return False
    if any(marker in text for marker in ("```", "{", "}")):
        return False
    nonempty_lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not nonempty_lines:
        return False
    if len(nonempty_lines) > 3:
        return False
    last_line = nonempty_lines[-1]
    return len(last_line.split()) <= 20


def _infer_action_from_explicit_declaration(text: str) -> Action | None:
    action_pattern = r"answer|ask|challenge|abstain"
    patterns = (
        rf"\b(?:appropriate|correct)\s+action(?:\s+\w+)?\s+is\s+to\s+(?P<action>{action_pattern})\b",
        rf"\b(?:appropriate|correct)\s+action(?:\s+\w+)?\s+is\s+to\s+use\s+(?:the\s+)?['\"]?(?P<action>{action_pattern})['\"]?(?:\s+(?:action|key))?\b",
        rf"\b(?:appropriate|correct)\s+action(?:\s+\w+)?\s+is\s+(?:the\s+)?['\"]?(?P<action>{action_pattern})['\"]?(?:\s+(?:action|key))?\b",
        rf"\b(?:the\s+)?correct\s+action\s+is\s+to\s+(?P<action>{action_pattern})\b",
        rf"\bthe\s+action\s+should\s+be\s+(?:to\s+)?['\"]?(?P<action>{action_pattern})['\"]?\b",
        rf"\b(?:i|we)\s+should\s+use\s+(?:the\s+)?(?:action|key)\s+['\"]?(?P<action>{action_pattern})['\"]?\b",
        rf"\b(?:i|we)\s+should\s+use\s+(?:the\s+)?['\"]?(?P<action>{action_pattern})['\"]?(?:\s+(?:action|key))?\b",
        rf"\b(?:i|we)\s+should\s+(?P<action>{action_pattern})\b",
        rf"\bthe\s+correct\s+choice\s+is\s+(?:to\s+)?['\"]?(?P<action>{action_pattern})['\"]?\b",
        rf"\b['\"]?(?P<action>{action_pattern})['\"]?\s+is\s+the\s+correct\s+choice\b",
    )
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match is None:
            continue
        return Action(match.group("action").lower())
    return None


def _coerce_action(value: Any) -> Action:
    try:
        return Action(str(value).strip().lower())
    except ValueError:
        return Action.ABSTAIN


def _coerce_confidence(value: Any) -> float | None:
    if value is None:
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return max(0.0, min(1.0, number))


def _resolve_dtype(torch_module: Any, dtype_name: str) -> Any:
    normalized = dtype_name.strip().lower()
    if normalized == "auto":
        return "auto"
    mapping = {
        "bfloat16": torch_module.bfloat16,
        "bf16": torch_module.bfloat16,
        "float16": torch_module.float16,
        "fp16": torch_module.float16,
        "float32": torch_module.float32,
        "fp32": torch_module.float32,
    }
    return mapping.get(normalized, "auto")

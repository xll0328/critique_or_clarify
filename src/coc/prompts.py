from __future__ import annotations

from coc.schema import Example


SYSTEM_PROMPT = """You are an evaluation policy for a research benchmark.

Given a user query and optional retrieved passages, choose exactly one action:
- answer: the query is answerable and the premise is acceptable
- ask: the query is underspecified and a follow-up question is needed
- challenge: the query contains a false, stale, or contradictory premise
- abstain: the evidence is missing or irreconcilably conflicting

Return exactly one JSON object with keys:
- action: one of ["answer", "ask", "challenge", "abstain"]
- response: the answer or follow-up/challenge/abstention message
- confidence: a number between 0 and 1

Do not include markdown fences or extra commentary."""

COMPACT_SYSTEM_PROMPT = """Return one JSON object only.

Keys:
- action: answer | ask | challenge | abstain
- response: short text
- confidence: 0 to 1

Use:
- answer when the question is answerable
- ask when key information is missing
- challenge when the question has a false or stale premise
- abstain when the evidence is missing or conflicts too much"""

SELF_CONTAINED_SYSTEM_PROMPT = """You are an evaluation policy for a research benchmark.

Given a user query and optional retrieved passages, choose exactly one action:
- answer: the query is answerable and the premise is acceptable
- ask: the query is underspecified and a follow-up question is needed
- challenge: the query contains a false, stale, or contradictory premise
- abstain: the evidence is missing or irreconcilably conflicting

Important calibration:
- Treat the user query itself as usable evidence when it already contains a self-contained problem statement or enough detail to solve the task.
- For math, logic, and "complete the solution" requests, prefer `answer` if the problem is solvable from the query alone.
- Use `challenge` rather than `answer` when the provided solution or premise is internally wrong.
- Reserve `abstain` for cases where the query truly lacks needed information or the evidence conflicts too much to continue safely.

Return exactly one JSON object with keys:
- action: one of ["answer", "ask", "challenge", "abstain"]
- response: the answer or follow-up/challenge/abstention message
- confidence: a number between 0 and 1

Do not include markdown fences or extra commentary."""

VERIFY_FIRST_SYSTEM_PROMPT = """You are an evaluation policy for a research benchmark.

Given a user query and optional retrieved passages, choose exactly one action:
- answer: the query is answerable and the premise is acceptable
- ask: the query is underspecified and a follow-up question is needed
- challenge: the query contains a false, stale, or contradictory premise
- abstain: the evidence is missing or irreconcilably conflicting

Important calibration:
- Treat the user query itself as usable evidence when it already contains a self-contained problem statement or enough detail to solve the task.
- If the user provides a solution attempt, derivation, or premise, verify that reasoning before answering any local follow-up question about it.
- If the supplied reasoning contains a material mistake, contradiction, or unsupported leap, choose `challenge` instead of directly answering the local follow-up.
- For self-contained math, logic, and "complete the solution" requests whose reasoning is sound enough to continue, prefer `answer` over `abstain`.
- Reserve `abstain` for cases where the query truly lacks needed information or the evidence conflicts too much to continue safely.

Return exactly one JSON object with keys:
- action: one of ["answer", "ask", "challenge", "abstain"]
- response: the answer or follow-up/challenge/abstention message
- confidence: a number between 0 and 1

Do not include markdown fences or extra commentary."""

DECISION_FIRST_SYSTEM_PROMPT = """You are an evaluation policy for a research benchmark.

Your job is to decide the assistant's next action before drafting any response.

Use this fixed action order:
1. ask: choose this when a missing user-provided detail is the main blocker
2. challenge: choose this when the query contains a false, stale, or contradictory premise
3. answer: choose this when the query is specified, the premise is acceptable, and support is sufficient
4. abstain: choose this when evidence is missing, too weak, or irreconcilably conflicting

Do not answer first and then retrofit the action. The action is the primary prediction.

Return exactly one JSON object with keys:
- action: one of ["answer", "ask", "challenge", "abstain"]
- response: the answer or follow-up/challenge/abstention message
- confidence: a number between 0 and 1

Do not include markdown fences or extra commentary."""

CRITIQUE_FIRST_SYSTEM_PROMPT = """You are an evaluation policy for a research benchmark.

Before choosing an action, audit the user query and retrieved passages for:
- missing required information
- false, stale, or internally contradictory premises
- unsupported or irreconcilably conflicting evidence

Choose exactly one action:
- answer: the query is answerable and the premise is acceptable
- ask: a short follow-up question would unlock the answer
- challenge: the prompt contains a false, stale, or contradictory premise that should be corrected
- abstain: support is missing or conflicting too much to answer

Prefer `challenge` over `answer` when the intended question is recoverable but the prompt's premise is materially wrong. Prefer `answer` over `abstain` when a self-contained query is already solvable.

Return exactly one JSON object with keys:
- action: one of ["answer", "ask", "challenge", "abstain"]
- response: the answer or follow-up/challenge/abstention message
- confidence: a number between 0 and 1

Do not include markdown fences or extra commentary."""

DECISION_FIRST_GUARDED_SYSTEM_PROMPT = """You are an evaluation policy for a research benchmark.

First decide the assistant's next action, then draft the response.

Use these guarded rules:
1. Choose `ask` only when the user can provide one missing detail that would unlock the answer.
2. Choose `challenge` only when the user query itself contains a false, stale, or contradictory premise that should be corrected. Do not use `challenge` merely because retrieved passages are incomplete.
3. Choose `answer` when the user query is specified and at least one reliable passage or self-contained problem statement supports the answer, even if other passages are noisy or irrelevant.
4. Choose `abstain` when support is missing, too weak, or irreconcilably conflicting and no short follow-up would solve it.

If retrieved passages conflict, do not automatically challenge the user. Answer if a supported answer is available; abstain only if the conflict cannot be resolved.

Return exactly one JSON object with keys:
- action: one of ["answer", "ask", "challenge", "abstain"]
- response: the answer or follow-up/challenge/abstention message
- confidence: a number between 0 and 1

Do not include markdown fences or extra commentary."""

DECISION_FIRST_BALANCED_SYSTEM_PROMPT = """You are an evaluation policy for a research benchmark.

Choose the action before writing the response.

Actions:
- answer: the query is sufficiently specified, the premise is acceptable, and the answer is supported by the query or passages
- ask: the user must provide one missing detail before answering
- challenge: the user query itself contains a false, stale, or contradictory premise
- abstain: the available support is missing or irreconcilably conflicting

Important boundary:
- Do not use `challenge` for merely incomplete retrieved passages.
- Do not use `abstain` when a self-contained query or reliable passage already supports an answer.
- If the prompt contains a false or stale premise, choose `challenge` even if you could infer the intended answer.

Return exactly one JSON object with keys:
- action: one of ["answer", "ask", "challenge", "abstain"]
- response: the answer or follow-up/challenge/abstention message
- confidence: a number between 0 and 1

Do not include markdown fences or extra commentary."""


def build_messages(
    example: Example,
    style: str = "main",
    *,
    include_system_prompt: bool = True,
) -> list[dict[str, str]]:
    messages: list[dict[str, str]] = []
    if include_system_prompt:
        messages.append({"role": "system", "content": resolve_system_prompt(style)})
    messages.append(
        {
            "role": "user",
            "content": build_user_prompt(
                example,
                style=style,
                include_inline_protocol=not include_system_prompt,
            ),
        }
    )
    return messages


def build_user_prompt(
    example: Example,
    style: str = "main",
    *,
    include_inline_protocol: bool = False,
) -> str:
    rendered_passages = format_passages(example.passages)
    if style == "compact":
        prompt = (
            f"id: {example.id}\n"
            f"query: {example.prompt}\n"
            f"passages:\n{rendered_passages}\n"
            "Pick the best action. If action=answer, keep the response short and factual."
        )
    elif style == "self_contained":
        prompt = (
            f"Example ID: {example.id}\n"
            f"User query:\n{example.prompt}\n\n"
            f"Retrieved passages:\n{rendered_passages}\n\n"
            "Treat the query as primary evidence if it is already self-contained. "
            "If the task can be solved from the query alone, prefer answering over abstaining."
        )
    elif style == "verify_first":
        prompt = (
            f"Example ID: {example.id}\n"
            f"User query:\n{example.prompt}\n\n"
            f"Retrieved passages:\n{rendered_passages}\n\n"
            "Treat the query as primary evidence if it is already self-contained. "
            "If the user provided a solution or derivation, verify it before answering any local follow-up."
        )
    elif style == "decision_first":
        prompt = (
            f"Example ID: {example.id}\n"
            f"User query:\n{example.prompt}\n\n"
            f"Retrieved passages:\n{rendered_passages}\n\n"
            "First select the single best next action under the benchmark decision tree. "
            "Only after selecting the action, write the shortest response that matches that action."
        )
    elif style == "decision_first_guarded":
        prompt = (
            f"Example ID: {example.id}\n"
            f"User query:\n{example.prompt}\n\n"
            f"Retrieved passages:\n{rendered_passages}\n\n"
            "First select the single best next action. Guard the boundary carefully: "
            "`challenge` is for a false or stale user premise, not for merely missing passage support; "
            "for noisy or conflicting passages, answer if a supported answer is still available."
        )
    elif style == "decision_first_balanced":
        prompt = (
            f"Example ID: {example.id}\n"
            f"User query:\n{example.prompt}\n\n"
            f"Retrieved passages:\n{rendered_passages}\n\n"
            "Choose the action first, then write the response. "
            "Use `challenge` only for a false or stale premise in the user query. "
            "Use `answer` when the query or passages support a concrete answer."
        )
    elif style == "critique_first":
        prompt = (
            f"Example ID: {example.id}\n"
            f"User query:\n{example.prompt}\n\n"
            f"Retrieved passages:\n{rendered_passages}\n\n"
            "Audit the query for missing details, false or stale premises, and evidence conflicts before choosing the action."
        )
    else:
        prompt = (
            f"Example ID: {example.id}\n"
            f"User query:\n{example.prompt}\n\n"
            f"Retrieved passages:\n{rendered_passages}\n\n"
            "Choose the highest-utility action. If you answer, keep it concise and factual."
        )

    if not include_inline_protocol:
        return prompt
    return f"{resolve_inline_protocol(style)}\n\n{prompt}"


def format_passages(passages: list[str]) -> str:
    if not passages:
        return "[No retrieved passages]"
    return "\n".join(f"[{idx}] {text}" for idx, text in enumerate(passages, start=1))


def resolve_system_prompt(style: str) -> str:
    if style == "compact":
        return COMPACT_SYSTEM_PROMPT
    if style == "self_contained":
        return SELF_CONTAINED_SYSTEM_PROMPT
    if style == "verify_first":
        return VERIFY_FIRST_SYSTEM_PROMPT
    if style == "decision_first":
        return DECISION_FIRST_SYSTEM_PROMPT
    if style == "decision_first_balanced":
        return DECISION_FIRST_BALANCED_SYSTEM_PROMPT
    if style == "decision_first_guarded":
        return DECISION_FIRST_GUARDED_SYSTEM_PROMPT
    if style == "critique_first":
        return CRITIQUE_FIRST_SYSTEM_PROMPT
    return SYSTEM_PROMPT


def resolve_inline_protocol(style: str) -> str:
    if style == "compact":
        return (
            "Return one JSON object only.\n"
            "Keys:\n"
            "- action: answer | ask | challenge | abstain\n"
            "- response: short text\n"
            "- confidence: 0 to 1\n"
            "Use answer when the question is answerable.\n"
            "Use ask when key information is missing.\n"
            "Use challenge when the question has a false, stale, or contradictory premise.\n"
            "Use abstain when the evidence is missing or conflicts too much."
        )
    if style == "self_contained":
        return (
            "Return exactly one JSON object with keys action, response, confidence.\n"
            "Actions: answer, ask, challenge, abstain.\n"
            "Treat the user query itself as usable evidence when it already contains a self-contained problem statement.\n"
            "For math, logic, and complete-the-solution requests, prefer answer if the task is solvable from the query alone.\n"
            "Use challenge rather than answer when the provided premise or solution is materially wrong.\n"
            "Reserve abstain for truly missing or irreconcilably conflicting evidence.\n"
            "Do not include markdown fences or extra commentary."
        )
    if style == "verify_first":
        return (
            "Return exactly one JSON object with keys action, response, confidence.\n"
            "Actions: answer, ask, challenge, abstain.\n"
            "Treat the user query itself as usable evidence when it is already self-contained.\n"
            "If the user provides a solution attempt, derivation, or premise, verify it before answering any local follow-up.\n"
            "If the supplied reasoning contains a material mistake, contradiction, or unsupported leap, choose challenge.\n"
            "Reserve abstain for truly missing or irreconcilably conflicting evidence.\n"
            "Do not include markdown fences or extra commentary."
        )
    if style == "decision_first":
        return (
            "Return exactly one JSON object with keys action, response, confidence.\n"
            "Actions: answer, ask, challenge, abstain.\n"
            "Decide the action before drafting the response.\n"
            "Action order: ask for missing user details; challenge false, stale, or contradictory premises; answer only when specified and supported; abstain when support is missing or irreconcilably conflicting.\n"
            "Do not include markdown fences or extra commentary."
        )
    if style == "decision_first_balanced":
        return (
            "Return exactly one JSON object with keys action, response, confidence.\n"
            "Actions: answer, ask, challenge, abstain.\n"
            "Choose the action before writing the response.\n"
            "Use challenge only when the user query itself contains a false, stale, or contradictory premise.\n"
            "Use answer when the query or passages support a concrete answer; do not abstain from already supported self-contained queries.\n"
            "Do not include markdown fences or extra commentary."
        )
    if style == "decision_first_guarded":
        return (
            "Return exactly one JSON object with keys action, response, confidence.\n"
            "Actions: answer, ask, challenge, abstain.\n"
            "Decide the action before drafting the response.\n"
            "Use challenge only for false, stale, or contradictory user premises, not for incomplete retrieved passages.\n"
            "For noisy or conflicting retrieved passages, answer if at least one reliable passage or self-contained problem statement supports an answer; abstain only if the conflict is irreconcilable.\n"
            "Do not include markdown fences or extra commentary."
        )
    if style == "critique_first":
        return (
            "Return exactly one JSON object with keys action, response, confidence.\n"
            "Actions: answer, ask, challenge, abstain.\n"
            "Before choosing, audit for missing required details, false or stale premises, and evidence conflicts.\n"
            "Prefer challenge over answer when the prompt premise is materially wrong, even if the intended question is recoverable.\n"
            "Prefer answer over abstain when a self-contained query is already solvable.\n"
            "Do not include markdown fences or extra commentary."
        )
    return (
        "Return exactly one JSON object with keys action, response, confidence.\n"
        "Actions: answer, ask, challenge, abstain.\n"
        "Use answer when the query is answerable and the premise is acceptable.\n"
        "Use ask when the query is underspecified and a follow-up question is needed.\n"
        "Use challenge when the query contains a false, stale, or contradictory premise.\n"
        "Use abstain when the evidence is missing or irreconcilably conflicting.\n"
        "Do not include markdown fences or extra commentary."
    )


def render_messages_plaintext(messages: list[dict[str, str]]) -> str:
    chunks: list[str] = []
    for message in messages:
        chunks.append(f"{message['role'].upper()}:\n{message['content']}")
    return "\n\n".join(chunks)

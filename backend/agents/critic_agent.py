# backend/agents/critic_agent.py
import json
import re
from ..tools.llm_client import generate

def clean_json(text: str) -> str:
    """
    Robust JSON extractor: fenced blocks, or bracket-matched JSON extraction.
    """
    if not isinstance(text, str):
        return ""

    t = text.strip()
    m = re.search(r"```(?:json)?\s*(.*?)\s*```", t, flags=re.S | re.I)
    if m:
        return m.group(1).strip()

    first_pos = None
    first_char = None
    for i, ch in enumerate(t):
        if ch in "{[":
            first_pos = i
            first_char = ch
            break
    if first_pos is None:
        return t

    open_ch = first_char
    close_ch = "}" if open_ch == "{" else "]"
    depth = 0
    end_pos = None
    for i in range(first_pos, len(t)):
        ch = t[i]
        if ch == open_ch:
            depth += 1
        elif ch == close_ch:
            depth -= 1
            if depth == 0:
                end_pos = i
                break

    if end_pos is not None:
        return t[first_pos:end_pos + 1].strip()

    if (t.startswith("`") and t.endswith("`")) or (t.startswith('"') and t.endswith('"')):
        return t.strip("`\"' \n\r\t")
    return t


class CriticAgent:
    def __init__(self, memory, log_fn=None):
        self.memory = memory
        self.log = log_fn or (lambda m: None)

    async def run(self, results):
        self.log("Critic: evaluating results using LLM...")

        results_str = json.dumps(results)[:1000]

        prompt = (
            f"Critique these experiment results: {results_str}. "
            "Return ONLY valid JSON with keys 'critique' (string) and 'confidence' (0-1). "
            "Example: {\"critique\": \"...\", \"confidence\": 0.7}. "
            "Do NOT include explanations or extra text. If needed, wrap JSON in triple backticks."
        )

        raw = await generate(prompt)
        self.log("Critic: LLM response received")

        text = clean_json(raw)

        try:
            parsed = json.loads(text)
            critique = parsed.get("critique")
            confidence = parsed.get("confidence")
            if critique is not None and confidence is not None:
                try:
                    confidence = float(confidence)
                except Exception:
                    confidence = 0.7
                return {"critique": critique, "confidence": confidence}
        except Exception as e:
            self.log(f"Critic: JSON parse failed: {e}")

        return {"critique": "Fallback critique", "confidence": 0.7}

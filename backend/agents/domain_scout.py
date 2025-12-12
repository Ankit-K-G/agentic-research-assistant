# backend/agents/domain_scout.py
from typing import List, Dict
import json
import re
from tools.llm_client import generate

def clean_json(text: str) -> str:
    """
    Attempt to extract a JSON object or array from model output.
    Strategy:
      1. If there is a fenced block (```json ... ``` or ``` ... ```), extract inner content.
      2. Otherwise find the first '{' or '[' and match until the corresponding '}' or ']'
         using a depth counter to handle nested braces.
      3. If nothing found, return the original trimmed text.
    """
    if not isinstance(text, str):
        return ""

    t = text.strip()

    # 1) fenced block
    m = re.search(r"```(?:json)?\s*(.*?)\s*```", t, flags=re.S | re.I)
    if m:
        return m.group(1).strip()

    # 2) bracket matching for first JSON block
    first_pos = None
    first_char = None
    for i, ch in enumerate(t):
        if ch in "{[":
            first_pos = i
            first_char = ch
            break
    if first_pos is None:
        # no JSON-like start found
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
        candidate = t[first_pos:end_pos + 1].strip()
        return candidate

    # 3) fallback: strip surrounding quotes/backticks if present
    if (t.startswith("`") and t.endswith("`")) or (t.startswith('"') and t.endswith('"')):
        return t.strip("`\"' \n\r\t")
    return t


class DomainScoutAgent:
    def __init__(self, memory, log_fn=None):
        self.memory = memory
        self.log = log_fn or (lambda m: None)

    async def run(self) -> List[Dict]:
        self.log("DomainScout: searching for emerging domains...")

        # STRICT JSON PROMPT
        prompt = (
            "You are a research scout. List 3 emerging research topics (short names) with a confidence score (0-1). "
            "Return ONLY valid JSON (no extra commentary) with the key 'domains' as a list of objects: "
            "e.g. {\"domains\": [{\"name\": \"...\", \"confidence\": 0.72}, ...]}. "
            "Wrap the JSON in triple backticks if you must. Keep it concise and strictly machine-readable."
        )

        raw = await generate(prompt)
        self.log("DomainScout: LLM response received")

        cleaned = clean_json(raw)

        try:
            parsed = json.loads(cleaned)
            domains = parsed.get("domains", [])
            if isinstance(domains, list) and domains:
                return domains
        except Exception as e:
            self.log(f"DomainScout: JSON parse failed: {e}")

        self.log("DomainScout: using fallback domain list")
        return [
            {"name": "Quantum-inspired GNNs for drug repurposing", "confidence": 0.72},
            {"name": "Neuro-symbolic causal discovery in climate models", "confidence": 0.68},
            {"name": "Microscopy transformer embeddings for histopathology", "confidence": 0.65},
        ]

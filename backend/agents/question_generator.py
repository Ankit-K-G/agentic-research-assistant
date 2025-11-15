# backend/agents/question_generator.py
import json
import re
from ..tools.llm_client import generate

def clean_json(text: str) -> str:
    """
    Same robust extractor as in other agents.
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


class QuestionGeneratorAgent:
    def __init__(self, memory, log_fn=None):
        self.memory = memory
        self.log = log_fn or (lambda m: None)

    async def run(self, domains):
        self.log("QuestionGenerator: generating questions...")

        # Extract names safely
        domain_names = [d["name"] for d in domains if isinstance(d, dict) and "name" in d]

        # STRICT JSON PROMPT
        prompt = (
            f"Given these research topics: {domain_names}. "
            "Generate 3 concise, testable research questions (single sentences). "
            "Return ONLY valid JSON like {\"questions\": [\"q1\",\"q2\",\"q3\"]} with no explanatory text. "
            "Wrap JSON in triple backticks if you must. Be concise and scientific."
        )

        raw = await generate(prompt)
        self.log("QuestionGenerator: LLM response received")

        cleaned = clean_json(raw)

        try:
            parsed = json.loads(cleaned)
            qs = parsed.get("questions", [])
            if isinstance(qs, list) and qs:
                return [q.strip() for q in qs if isinstance(q, str) and q.strip()]
        except Exception as e:
            self.log(f"QuestionGenerator: JSON parse failed: {e}")

        return [
            "Fallback question 1",
            "Fallback question 2",
            "Fallback question 3",
        ]

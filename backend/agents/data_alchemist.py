# backend/agents/data_alchemist.py
import asyncio
import random
from typing import Any, Dict

class DataAlchemistAgent:
    def __init__(self, memory, log_fn=None):
        self.memory = memory
        # default to a no-op logger if none provided (avoids printing during tests)
        self.log = log_fn or (lambda *a, **k: None)

    async def run(self, question: Any) -> Dict:
        """
        Simulate collecting / synthesizing a small dataset for the given question.
        Keeps things lightweight and deterministic-ish for tests.
        Returns a dict with 'rows' (list of dicts) and 'meta'.
        """
        try:
            # extract question text if passed as dict/obj
            qtext = None
            if isinstance(question, str):
                qtext = question
            else:
                try:
                    # try common keys
                    qtext = question.get("text") if hasattr(question, "get") else str(question)
                except Exception:
                    qtext = str(question)

            self.log(f"DataAlchemist: collecting data for question: {qtext}")
            # simulate some I/O / wait
            await asyncio.sleep(0.8)

            # create a small synthetic dataset (deterministic-ish using hash of question)
            seed = abs(hash(qtext)) % (2**32) if qtext else random.randint(0, 2**32 - 1)
            rnd = random.Random(seed)

            rows = []
            # synthesize N rows between 6 and 12
            n = 8 + (seed % 5)
            for i in range(1, n + 1):
                feature = round(rnd.uniform(0.0, 1.0), 4)
                # simple label rule correlated with feature + noise
                label = 1 if feature + rnd.uniform(-0.15, 0.15) > 0.5 else 0
                rows.append({"id": i, "feature": feature, "label": label})

            dataset = {
                "rows": rows,
                "meta": {
                    "sources": ["synthetic://generated", "example.pdf"],
                    "question": qtext,
                    "n_rows": len(rows),
                },
            }

            # store to memory (assuming memory has add method)
            try:
                if hasattr(self.memory, "add"):
                    self.memory.add("dataset", dataset)
            except Exception as e:
                self.log(f"DataAlchemist: memory.add failed: {e}")

            self.log(f"DataAlchemist: dataset ready with {len(rows)} rows")
            return dataset

        except Exception as exc:
            # never raise from agent - return an empty dataset and log the error
            self.log(f"DataAlchemist: unexpected error: {exc}")
            return {"rows": [], "meta": {"error": str(exc)}}

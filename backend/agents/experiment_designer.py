# backend/agents/experiment_designer.py
import asyncio
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

class ExperimentDesignerAgent:
    def __init__(self, memory, log_fn=None):
        self.memory = memory
        self.log = log_fn or (lambda *a, **k: None)

    async def _fit_and_eval(self, X, y):
        # run sklearn fitting in a thread to avoid blocking the event loop
        def sync_work():
            model = LogisticRegression(solver="lbfgs", max_iter=200)
            model.fit(X, y)
            preds = model.predict(X)
            acc = accuracy_score(y, preds)
            return model, float(acc)

        loop = asyncio.get_running_loop()
        model, acc = await loop.run_in_executor(None, sync_work)
        return model, acc

    async def run(self, dataset, question):
        try:
            self.log("ExperimentDesigner: preparing experiment")
            rows = dataset.get("rows", []) if isinstance(dataset, dict) else []
            X = np.array([[r.get('feature', 0.0)] for r in rows])
            y = np.array([r.get('label', 0) for r in rows])

            if X.shape[0] < 3:
                self.log("ExperimentDesigner: not enough data to run experiment")
                results = {"summary": "not enough data", "details": {"n_rows": int(X.shape[0])}}
                try:
                    if hasattr(self.memory, "add"):
                        self.memory.add('results', results)
                except Exception:
                    pass
                return results

            self.log(f"ExperimentDesigner: running model on {X.shape[0]} rows")
            model, acc = await self._fit_and_eval(X, y)

            results = {
                "summary": {"accuracy": acc},
                "model_coef": model.coef_.tolist() if hasattr(model, "coef_") else None,
                "n_rows": int(X.shape[0]),
            }

            try:
                if hasattr(self.memory, "add"):
                    self.memory.add('results', results)
            except Exception as e:
                self.log(f"ExperimentDesigner: memory.add failed: {e}")

            self.log(f"ExperimentDesigner: finished (accuracy={acc})")
            return results

        except Exception as exc:
            self.log(f"ExperimentDesigner: unexpected error: {exc}")
            return {"summary": "error", "details": {"error": str(exc)}}

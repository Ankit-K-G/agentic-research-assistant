import uuid
import asyncio
from collections import defaultdict
from ..tools.memory_manager import MemoryManager
from .domain_scout import DomainScoutAgent
from .question_generator import QuestionGeneratorAgent
from .data_alchemist import DataAlchemistAgent
from .experiment_designer import ExperimentDesignerAgent
from .critic_agent import CriticAgent


class Orchestrator:
    def __init__(self):
        self.runs = {}
        self.status = defaultdict(dict)
        self.memory = MemoryManager()

    def start(self, mode: str = "default"):
        """
        Start a pipeline run.

        mode:
          - "default": full pipeline (scout -> qgen -> data -> exp -> critic -> paper)
          - "explore": domain exploration + question generation (fast)
          - "summarize": summarization mode (stub - placeholder)
          - "simulate": run experiment simulation (data alchemy + experiment designer)
        """
        run_id = str(uuid.uuid4())
        self.status[run_id] = {"phase": "initialized", "logs": [], "mode": mode}
        # start pipeline in background
        asyncio.create_task(self._pipeline(run_id, mode=mode))
        return run_id

    async def _pipeline(self, run_id: str, mode: str = "default"):
        try:
            self._log(run_id, f"Starting pipeline (mode={mode})")

            # ---------- MODE: explore ----------
            if mode == "explore":
                self._log(run_id, "DomainScout: searching for emerging domains...")
                scout = DomainScoutAgent(self.memory, log_fn=lambda m: self._log(run_id, m))
                domains = await scout.run()
                self._log(run_id, f"Scout found: {domains}")

                self._log(run_id, "QuestionGenerator: generating questions...")
                qgen = QuestionGeneratorAgent(self.memory, log_fn=lambda m: self._log(run_id, m))
                questions = await qgen.run(domains)
                self._log(run_id, f"Questions: {questions}")

                chosen_q = questions[0] if questions else "Exploration result"
                self._log(run_id, f"Chosen question: {chosen_q}")

                paper = {
                    "title": f"Exploration: {chosen_q}",
                    "abstract": "Auto-generated exploration summary.",
                    "results": {"domains": domains, "questions": questions},
                    "critique": {},
                }

                self.runs[run_id] = paper
                self.status[run_id]["phase"] = "completed"
                self._log(run_id, "Explore pipeline finished")
                return

            # ---------- MODE: summarize ----------
            if mode == "summarize":
                # NOTE: uploading/watching for uploaded file not implemented here.
                # This is a placeholder to show summarization mode working.
                self._log(run_id, "Summarization mode: running placeholder summarizer")
                # If you later add an upload endpoint, the orchestrator can wait for content here.
                paper = {
                    "title": "Summarized Paper (placeholder)",
                    "abstract": "This is an auto-generated summary (placeholder).",
                    "results": {},
                    "critique": {},
                }
                self.runs[run_id] = paper
                self.status[run_id]["phase"] = "completed"
                self._log(run_id, "Summarization completed (placeholder)")
                return

            # ---------- MODE: simulate ----------
            if mode == "simulate":
                self._log(run_id, "Simulation: running data alchemy and experiment designer...")
                da = DataAlchemistAgent(self.memory, log_fn=lambda m: self._log(run_id, m))
                # Use a placeholder question/prompt for simulation
                sim_prompt = "simulate_experiment"
                dataset = await da.run(sim_prompt)
                # log dataset shape/info if possible
                try:
                    rows = len(dataset.get("rows", []))
                except Exception:
                    rows = None
                self._log(run_id, f"Simulated dataset created (rows={rows})")

                ed = ExperimentDesignerAgent(self.memory, log_fn=lambda m: self._log(run_id, m))
                results = await ed.run(dataset, sim_prompt)
                self._log(run_id, f"Simulation results: {results.get('summary', results)}")

                critic = CriticAgent(self.memory, log_fn=lambda m: self._log(run_id, m))
                critique = await critic.run(results)
                self._log(run_id, f"Critic: {critique}")

                paper = {
                    "title": "Experiment Simulation Results",
                    "abstract": "Auto-generated simulation abstract.",
                    "results": results,
                    "critique": critique,
                }
                self.runs[run_id] = paper
                self.status[run_id]["phase"] = "completed"
                self._log(run_id, "Simulation pipeline finished")
                return

            # ---------- DEFAULT: full pipeline ----------
            # Keep your original pipeline behaviour here (scout -> qgen -> data -> exp -> critic -> paper)
            self._log(run_id, "Running full default pipeline")

            scout = DomainScoutAgent(self.memory, log_fn=lambda m: self._log(run_id, m))
            domains = await scout.run()
            self._log(run_id, f"Scout found: {domains}")

            qgen = QuestionGeneratorAgent(self.memory, log_fn=lambda m: self._log(run_id, m))
            questions = await qgen.run(domains)
            self._log(run_id, f"Questions: {questions}")

            chosen_q = questions[0] if questions else "Untitled question"
            self._log(run_id, f"Chosen question: {chosen_q}")

            data_agent = DataAlchemistAgent(self.memory, log_fn=lambda m: self._log(run_id, m))
            dataset = await data_agent.run(chosen_q)
            try:
                num_rows = len(dataset.get("rows", []))
            except Exception:
                num_rows = None
            self._log(run_id, f"Dataset ready: rows={num_rows}")

            exp_agent = ExperimentDesignerAgent(self.memory, log_fn=lambda m: self._log(run_id, m))
            results = await exp_agent.run(dataset, chosen_q)
            self._log(run_id, f"Experiment results summary: {results.get('summary', {})}")

            critic = CriticAgent(self.memory, log_fn=lambda m: self._log(run_id, m))
            critique = await critic.run(results)
            self._log(run_id, f"Critic: {critique}")

            paper = {
                "title": f"Mini paper for {chosen_q}",
                "abstract": "Auto-generated abstract...",
                "results": results,
                "critique": critique,
            }

            self.runs[run_id] = paper
            self.status[run_id]["phase"] = "completed"
            self._log(run_id, "Pipeline finished")

        except Exception as e:
            # Log the error and set phase to error so frontend can show status
            self._log(run_id, f"Pipeline error: {repr(e)}")
            self.status[run_id]["phase"] = "error"

    def _log(self, run_id, message):
        # add to logs (create run entry if missing)
        self.status.setdefault(run_id, {}).setdefault("logs", []).append(message)

    def get_status(self, run_id):
        # Return the full status dict (phase, logs, mode if present)
        return self.status.get(run_id, {"phase": "unknown", "logs": []})

    def get_result(self, run_id):
        return self.runs.get(run_id, {})

import React, { useState } from "react";

export default function RunButton() {
  const [running, setRunning] = useState(false);
  const [mode, setMode] = useState("default");

  const start = async () => {
    setRunning(true);
    try {
      const base = import.meta.env.VITE_API_URL || "";
      // call /run with mode as query param
      const res = await fetch(`${base}/run?mode=${encodeURIComponent(mode)}`, {
        method: "POST",
      });
      if (!res.ok) throw new Error("Backend error");
      const data = await res.json();
      localStorage.setItem("agent_run_id", data.run_id);
      // optional: store chosen mode
      localStorage.setItem("agent_mode", mode);
    } catch (e) {
      alert("Backend not running or an error occurred.");
      console.error(e);
    } finally {
      setRunning(false);
    }
  };

  return (
    <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
      <select
        value={mode}
        onChange={(e) => setMode(e.target.value)}
        style={{ padding: 8, borderRadius: 6 }}
      >
        <option value="default">Default (full pipeline)</option>
        <option value="explore">Domain Exploration</option>
        <option value="summarize">Summarization</option>
        <option value="simulate">Experiment Simulation</option>
      </select>

      <button
        className="button"
        style={{ marginLeft: 8, minWidth: 160 }}
        onClick={start}
        disabled={running}
      >
        {running ? "Starting..." : "Start Research"}
      </button>
    </div>
  );
}

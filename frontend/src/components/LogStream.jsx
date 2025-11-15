import React, { useEffect, useState } from "react";

export default function LogStream() {
  const [logs, setLogs] = useState([]);

  useEffect(() => {
    const interval = setInterval(async () => {
      const run_id = localStorage.getItem("agent_run_id");
      if (!run_id) return;
      const base = import.meta.env.VITE_API_URL || "";
      try {
        const res = await fetch(`${base}/status/${run_id}`);
        const data = await res.json();
        setLogs(data.logs || []);
      } catch (e) {
        // ignore
      }
    }, 1500);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="logbox">
      {logs.length === 0 ? (
        <div>No logs yet. Start a run.</div>
      ) : (
        logs.map((l, i) => (
          <div key={i} style={{ marginBottom: 6 }}>
            {typeof l === "string" ? l : JSON.stringify(l)}
          </div>
        ))
      )}
    </div>
  );
}

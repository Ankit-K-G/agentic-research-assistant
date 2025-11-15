import React, { useEffect, useState } from "react";

export default function MarkdownViewer() {
  const [paper, setPaper] = useState(null);
  const [loading, setLoading] = useState(false);

  // Poll backend for updated paper every 2 seconds
  useEffect(() => {
    const interval = setInterval(async () => {
      const run_id = localStorage.getItem("agent_run_id");
      if (!run_id) return;
      const base = import.meta.env.VITE_API_URL || "";
      try {
        const res = await fetch(`${base}/result/${run_id}`);
        const data = await res.json();
        setPaper(data);
      } catch (e) {
        console.error(e);
      }
    }, 2000);

    return () => clearInterval(interval);
  }, []);

  async function download(format) {
    const run_id = localStorage.getItem("agent_run_id");
    if (!run_id) {
      alert("No run found. Start research first!");
      return;
    }

    const base = import.meta.env.VITE_API_URL || "";
    const url = `${base}/result/${run_id}/download?format=${format}`;

    setLoading(true);

    try {
      const res = await fetch(url);
      if (!res.ok) {
        alert("Download failed");
        setLoading(false);
        return;
      }

      const blob = await res.blob();
      const ext = format === "pdf" ? "pdf" : "md";
      const filename = `paper_${run_id}.${ext}`;

      const link = document.createElement("a");
      link.href = window.URL.createObjectURL(blob);
      link.download = filename;
      link.click();
    } catch (e) {
      console.error(e);
      alert("Download error: " + e.message);
    }

    setLoading(false);
  }

  if (!paper || Object.keys(paper).length === 0) {
    return <div>No paper yet — run the pipeline first.</div>;
  }

  return (
    <div>
      <div style={{ display: "flex", gap: "10px", marginBottom: "15px" }}>
        <button
          className="button"
          disabled={loading}
          onClick={() => download("md")}
        >
          {loading ? "Preparing..." : "Download .md"}
        </button>

        <button
          className="button"
          disabled={loading}
          onClick={() => download("pdf")}
        >
          {loading ? "Preparing..." : "Download .pdf"}
        </button>
      </div>

      <h4>{paper.title}</h4>

      <p>
        <strong>Abstract:</strong> {paper.abstract}
      </p>

      <pre
        style={{
          whiteSpace: "pre-wrap",
          background: "#0f172a",
          color: "#e6edf3",
          padding: "12px",
          borderRadius: "8px",
        }}
      >
        {JSON.stringify(paper.results || {}, null, 2)}
      </pre>

      <div style={{ marginTop: "10px" }}>
        <strong>Critic:</strong>
        <pre style={{ whiteSpace: "pre-wrap" }}>
          {JSON.stringify(paper.critique, null, 2)}
        </pre>
      </div>
    </div>
  );
}

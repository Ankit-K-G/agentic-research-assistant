import React from "react";
import RunButton from "./components/RunButton";
import LogStream from "./components/LogStream";
import MarkdownViewer from "./components/MarkdownViewer";

export default function App() {
  return (
    <div className="container">
      <h1>Agentic Research Assistant</h1>
      <RunButton />
      <div className="card">
        <h3>Live Logs</h3>
        <LogStream />
      </div>
      <div className="card">
        <h3>Paper Output</h3>
        <MarkdownViewer />
      </div>
    </div>
  );
}

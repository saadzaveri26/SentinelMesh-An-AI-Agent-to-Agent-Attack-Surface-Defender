"use client";

import { useState, useEffect } from "react";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

function scoreColor(score) {
  if (score >= 0.5) return "var(--normal)";
  if (score >= 0.3) return "var(--anomalous)";
  return "var(--critical)";
}

export default function SelectionPanel({ selected }) {
  const [agentEdges, setAgentEdges] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!selected || selected.type !== "agent") {
      setAgentEdges(null);
      return;
    }
    setLoading(true);
    fetch(`${API}/api/trust-graph/${encodeURIComponent(selected.name)}`)
      .then((r) => r.ok ? r.json() : [])
      .then((data) => {
        setAgentEdges(data);
        setLoading(false);
      })
      .catch(() => {
        setAgentEdges([]);
        setLoading(false);
      });
  }, [selected]);

  if (!selected) {
    return (
      <div className="selection-panel">
        <div className="selection-hint">Select an agent or edge to view details</div>
      </div>
    );
  }

  if (selected.type === "agent") {
    const incoming = (agentEdges || []).filter(
      (e) => e.target_name === selected.name
    );
    const outgoing = (agentEdges || []).filter(
      (e) => e.source_name === selected.name
    );

    return (
      <div className="selection-panel">
        <div className="selection-title">{selected.name}</div>

        {selected.createdAt && (
          <div className="selection-field">
            <div className="selection-field-label">First seen</div>
            <div className="selection-field-value">
              {new Date(selected.createdAt).toLocaleString()}
            </div>
          </div>
        )}

        {loading ? (
          <div style={{ color: "var(--text-tertiary)", fontSize: 13, marginTop: 16 }}>
            Loading edges...
          </div>
        ) : (
          <>
            <div className="selection-section-label">
              Incoming ({incoming.length})
            </div>
            {incoming.length === 0 ? (
              <div style={{ fontSize: 12, color: "var(--text-tertiary)" }}>None</div>
            ) : (
              <ul className="selection-edge-list">
                {incoming.map((e) => (
                  <li key={e.id} className="selection-edge-item">
                    <span className="selection-edge-name">{e.source_name}</span>
                    <span
                      className="selection-edge-score"
                      style={{ color: scoreColor(e.score) }}
                    >
                      {e.score.toFixed(2)}
                    </span>
                  </li>
                ))}
              </ul>
            )}

            <div className="selection-section-label">
              Outgoing ({outgoing.length})
            </div>
            {outgoing.length === 0 ? (
              <div style={{ fontSize: 12, color: "var(--text-tertiary)" }}>None</div>
            ) : (
              <ul className="selection-edge-list">
                {outgoing.map((e) => (
                  <li key={e.id} className="selection-edge-item">
                    <span className="selection-edge-name">{e.target_name}</span>
                    <span
                      className="selection-edge-score"
                      style={{ color: scoreColor(e.score) }}
                    >
                      {e.score.toFixed(2)}
                    </span>
                  </li>
                ))}
              </ul>
            )}
          </>
        )}
      </div>
    );
  }

  if (selected.type === "edge") {
    const d = selected.data || {};
    return (
      <div className="selection-panel">
        <div className="selection-title">
          {d.source_name || "?"} → {d.target_name || "?"}
        </div>

        <div className="selection-field">
          <div className="selection-field-label">Trust score</div>
          <div
            className="selection-field-value"
            style={{ color: scoreColor(d.score || 0) }}
          >
            {(d.score || 0).toFixed(2)}
          </div>
        </div>

        <div className="selection-field">
          <div className="selection-field-label">Interactions</div>
          <div className="selection-field-value">
            {d.interaction_count || 0}
          </div>
        </div>

        <div className="selection-field">
          <div className="selection-field-label">Last interaction</div>
          <div className="selection-field-value">
            {d.last_interaction
              ? new Date(d.last_interaction).toLocaleString()
              : "N/A"}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="selection-panel">
      <div className="selection-hint">Select an agent or edge to view details</div>
    </div>
  );
}

"use client";

function scoreColor(score) {
  if (score >= 0.7) return "#E5484D";
  if (score >= 0.4) return "#E8A33D";
  return "#3DDC97";
}

function formatTs(iso) {
  const d = new Date(iso);
  return d.toLocaleTimeString("en-GB", {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hour12: false,
  });
}

export default function IncidentFeed({ incidents }) {
  return (
    <div className="incident-panel">
      <div className="incident-header">
        <h2>Incident Feed ({incidents.length})</h2>
      </div>

      {incidents.length === 0 ? (
        <div className="empty-state" style={{ height: "200px" }}>
          No flagged messages
        </div>
      ) : (
        <ul className="incident-list">
          {incidents.map((inc) => (
            <li key={inc.id} className="incident-item">
              <span className="incident-ts">{formatTs(inc.timestamp)}</span>
              <span className="incident-pair">
                {inc.sender} → {inc.receiver}
              </span>
              <span
                className="incident-score"
                style={{ color: scoreColor(inc.threat_score) }}
              >
                {inc.threat_score.toFixed(2)}
              </span>
              <span className="incident-preview">{inc.content_preview}</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

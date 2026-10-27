"use client";

function scoreColor(score) {
  if (score >= 0.7) return "#E5484D";
  if (score >= 0.4) return "#E8A33D";
  return "#3DDC97";
}

function formatTs(iso) {
  if (!iso) return "";
  const d = new Date(iso);
  const now = new Date();
  const time = d.toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hour12: false,
  });
  if (
    d.getDate() === now.getDate() &&
    d.getMonth() === now.getMonth() &&
    d.getFullYear() === now.getFullYear()
  ) {
    return time;
  }
  const date = d.toLocaleDateString("en-GB", {
    day: "numeric",
    month: "short",
  });
  return `${date} ${time}`;
}


export default function IncidentFeed({ incidents }) {
  const items = (incidents || []).filter(
    (inc) => inc.flagged || (inc.anomaly_flags && inc.anomaly_flags.length > 0) || inc.flag_name
  );

  return (
    <div className="incident-panel">
      <div className="incident-header">
        <h2>Incident Feed ({items.length})</h2>
      </div>

      {items.length === 0 ? (
        <div className="empty-state" style={{ height: "200px" }}>
          No flagged messages
        </div>
      ) : (
        <ul className="incident-list">
          {items.map((inc) => {
            const isAnomalyOnly = !inc.flagged && ((inc.anomaly_flags && inc.anomaly_flags.length > 0) || inc.flag_name);
            const flagName = inc.flag_name || (inc.anomaly_flags && inc.anomaly_flags[0]) || "anomaly";
            const score = inc.bert_score !== undefined ? inc.bert_score : inc.threat_score;

            return (
              <li
                key={inc.id}
                className={isAnomalyOnly ? "incident-item amber-row" : "incident-item"}
              >
                <span className="incident-ts">{formatTs(inc.timestamp)}</span>
                <span className="incident-pair">
                  {inc.sender} → {inc.receiver}
                </span>
                <span
                  className="incident-score"
                  style={{ color: isAnomalyOnly ? "#E8A33D" : scoreColor(score) }}
                >
                  {isAnomalyOnly ? flagName : (score !== undefined && score !== null ? Number(score).toFixed(2) : "0.00")}
                </span>
                <span className="incident-preview">{inc.content_preview}</span>
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}

"use client";

export default function KpiCards({ stats, flashes }) {
  const isFlagged = stats.messages_flagged > 0;

  return (
    <div className="kpi-row">
      <div className="kpi-card">
        <div className="kpi-label">Active agents</div>
        <div className={`kpi-value${flashes?.has("active_agents") ? " kpi-val-flash" : ""}`}>
          {stats.active_agents}
        </div>
      </div>
      <div className="kpi-card">
        <div className="kpi-label">Messages inspected</div>
        <div className={`kpi-value${flashes?.has("messages_inspected") ? " kpi-val-flash" : ""}`}>
          {stats.messages_inspected}
        </div>
      </div>
      <div className={`kpi-card${isFlagged ? " kpi-flagged-active" : ""}`}>
        <div className="kpi-label">Messages flagged</div>
        <div className={`kpi-value${flashes?.has("messages_flagged") ? " kpi-val-flash" : ""}`}>
          {stats.messages_flagged}
        </div>
      </div>
      <div className="kpi-card">
        <div className="kpi-label">Trust edges</div>
        <div className={`kpi-value${flashes?.has("trust_edges") ? " kpi-val-flash" : ""}`}>
          {stats.trust_edges}
        </div>
      </div>
    </div>
  );
}

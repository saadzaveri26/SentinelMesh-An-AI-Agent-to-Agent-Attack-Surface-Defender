"use client";

export default function StatsPanel({ stats }) {
  return (
    <div className="stats-panel">
      <h2>System Overview</h2>

      <div className="stat-row">
        <span className="stat-label">Active Agents</span>
        <span className="stat-value green">{stats.active_agents}</span>
      </div>

      <div className="stat-row">
        <span className="stat-label">Messages Inspected</span>
        <span className="stat-value">{stats.messages_inspected}</span>
      </div>

      <div className="stat-row">
        <span className="stat-label">Messages Flagged</span>
        <span className="stat-value red">{stats.messages_flagged}</span>
      </div>

      <div className="stat-row">
        <span className="stat-label">Trust Edges</span>
        <span className="stat-value amber">{stats.trust_edges}</span>
      </div>

      <div className="legend">
        <div className="legend-item">
          <div className="legend-line" style={{ background: "#3DDC97" }} />
          Normal
        </div>
        <div className="legend-item">
          <div className="legend-line" style={{ background: "#E8A33D" }} />
          Anomalous
        </div>
        <div className="legend-item">
          <div className="legend-line" style={{ background: "#E5484D" }} />
          Critical
        </div>
      </div>
    </div>
  );
}

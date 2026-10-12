"use client";

import useDashboard from "./hooks/useDashboard";
import TrustGraph from "./components/TrustGraph";
import StatsPanel from "./components/StatsPanel";
import IncidentFeed from "./components/IncidentFeed";

export default function Dashboard() {
  const { graph, stats, incidents, error } = useDashboard(4000);

  return (
    <div className="dashboard">
      <header className="header">
        <h1>SentinelMesh</h1>
        <div className="header-status">
          <span className="dot" />
          {error ? (
            <span style={{ color: "#E5484D" }}>Backend offline</span>
          ) : (
            <span>Live — polling every 4s</span>
          )}
        </div>
      </header>

      <div className="graph-panel">
        <TrustGraph nodes={graph.nodes} edges={graph.edges} />
      </div>

      <StatsPanel stats={stats} />

      <IncidentFeed incidents={incidents} />
    </div>
  );
}

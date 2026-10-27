"use client";

import { useState, useRef, useCallback } from "react";
import useDashboard from "./hooks/useDashboard";
import Shell from "./components/Shell";
import KpiCards from "./components/KpiCards";
import TrustGraph from "./components/TrustGraph";
import SelectionPanel from "./components/SelectionPanel";
import IncidentTable from "./components/IncidentTable";

export default function Overview() {
  const { graph, stats, incidents, error, lastUpdated, refetch, events } = useDashboard(4000);
  const [selected, setSelected] = useState(null);
  const idleRef = useRef(null);
  const fitRef = useRef(0);

  const handleNodeClick = useCallback((node) => {
    setSelected({
      type: "agent",
      id: node.id,
      name: node.data?.label || "unknown",
      createdAt: node.data?.created_at || null,
    });
  }, []);

  const handleEdgeClick = useCallback((edge) => {
    setSelected({ type: "edge", id: edge.id, data: edge.data || {} });
  }, []);

  const idle = idleRef.current;

  return (
    <Shell
      title="Overview"
      activeNav="overview"
      stats={stats}
      error={error}
      lastUpdated={lastUpdated}
    >
      <KpiCards stats={stats} flashes={events?.kpiFlashes} />

      <div className="graph-selection">
        <div className="graph-card">
          <div className="graph-header">
            <div className="graph-header-left">
              <span className="graph-header-title">Trust graph</span>
              <span className="graph-header-sub">
                {stats.active_agents} agents, {stats.trust_edges} edges
              </span>
            </div>
            <div className="graph-actions">
              {idle && idle.hasIdle && (
                <button className="graph-btn" onClick={idle.toggle}>
                  {idle.active
                    ? `Hide ${idle.count} idle`
                    : `Show ${idle.count} idle`}
                </button>
              )}
              <button className="graph-btn" onClick={refetch}>
                Refresh
              </button>
            </div>
          </div>
          <div className="graph-body">
            <TrustGraph
              nodes={graph.nodes}
              edges={graph.edges}
              onNodeClick={handleNodeClick}
              onEdgeClick={handleEdgeClick}
              showIdleToggle={idleRef}
              onFitView={fitRef}
              edgeEvents={events?.edgeEvents}
              blockedTargets={events?.blockedTargets}
            />
          </div>
          <div className="graph-legend">
            <div className="legend-item">
              <div className="legend-line" style={{ background: "#3DDC97" }} />
              Normal
            </div>
            <div className="legend-item">
              <div className="legend-line" style={{ background: "#F2A93B" }} />
              Anomalous
            </div>
            <div className="legend-item">
              <div className="legend-line" style={{ background: "#F0545A", borderTop: "2px dashed #F0545A", height: 0 }} />
              Critical
            </div>
          </div>
        </div>

        <SelectionPanel selected={selected} />
      </div>

      <IncidentTable incidents={incidents} newIds={events?.newIncidentIds} />
    </Shell>
  );
}

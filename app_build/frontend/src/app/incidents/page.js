"use client";

import useDashboard from "../hooks/useDashboard";
import Shell from "../components/Shell";
import IncidentTable from "../components/IncidentTable";

export default function IncidentsPage() {
  const { stats, incidents, error, lastUpdated, events } = useDashboard(4000, 100);

  return (
    <Shell
      title="Incidents"
      activeNav="incidents"
      stats={stats}
      error={error}
      lastUpdated={lastUpdated}
    >
      <IncidentTable incidents={incidents} fullHeight={true} newIds={events?.newIncidentIds} />
    </Shell>
  );
}

"use client";

import { useState, useEffect, useCallback, useRef } from "react";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function useDashboard(interval = 4000, incidentLimit = 20) {
  const [graph, setGraph] = useState({ nodes: [], edges: [] });
  const [stats, setStats] = useState({
    active_agents: 0,
    messages_inspected: 0,
    messages_flagged: 0,
    trust_edges: 0,
  });
  const [incidents, setIncidents] = useState([]);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);

  const [edgeEvents, setEdgeEvents] = useState({});
  const [newIncidentIds, setNewIncidentIds] = useState(new Set());
  const [blockedTargets, setBlockedTargets] = useState(new Set());
  const [kpiFlashes, setKpiFlashes] = useState(new Set());

  const isInitial = useRef(true);
  const prevEdges = useRef(new Map());
  const prevStats = useRef(null);
  const prevIncidents = useRef(new Set());

  const fetchAll = useCallback(async () => {
    try {
      const [gRes, sRes, iRes] = await Promise.all([
        fetch(`${API}/api/dashboard/graph`),
        fetch(`${API}/api/dashboard/stats`),
        fetch(`${API}/api/dashboard/incidents?limit=${incidentLimit}`),
      ]);

      if (gRes.ok && sRes.ok && iRes.ok) {
        const gData = await gRes.json();
        const sData = await sRes.json();
        const iData = await iRes.json();

        if (isInitial.current) {
          isInitial.current = false;
          (gData.edges || []).forEach((e) => {
            prevEdges.current.set(String(e.id), e.data?.interaction_count ?? 0);
          });
          prevStats.current = { ...sData };
          (iData || []).forEach((inc) => prevIncidents.current.add(String(inc.id)));
        } else {
          const freshEdgeEvents = {};
          (gData.edges || []).forEach((e) => {
            const count = e.data?.interaction_count ?? 0;
            const prev = prevEdges.current.get(String(e.id));
            if (prev !== undefined && count > prev) {
              freshEdgeEvents[String(e.id)] = Date.now();
            }
            prevEdges.current.set(String(e.id), count);
          });
          if (Object.keys(freshEdgeEvents).length > 0) {
            setEdgeEvents(freshEdgeEvents);
            setTimeout(() => setEdgeEvents({}), 750);
          }

          const freshIncIds = new Set();
          const freshBlocked = new Set();
          (iData || []).forEach((inc) => {
            const id = String(inc.id);
            if (!prevIncidents.current.has(id)) {
              freshIncIds.add(id);
              if (inc.flagged && inc.receiver) {
                freshBlocked.add(String(inc.receiver));
              }
            }
            prevIncidents.current.add(id);
          });

          if (freshIncIds.size > 0) {
            setNewIncidentIds(freshIncIds);
            setTimeout(() => setNewIncidentIds(new Set()), 1600);
          }

          if (freshBlocked.size > 0) {
            setBlockedTargets(freshBlocked);
            setTimeout(() => setBlockedTargets(new Set()), 650);
          }

          if (prevStats.current) {
            const flashes = new Set();
            for (const key of ["active_agents", "messages_inspected", "messages_flagged", "trust_edges"]) {
              if (sData[key] !== prevStats.current[key]) {
                flashes.add(key);
              }
            }
            if (flashes.size > 0) {
              setKpiFlashes(flashes);
              setTimeout(() => setKpiFlashes(new Set()), 450);
            }
          }
          prevStats.current = { ...sData };
        }

        setGraph(gData);
        setStats(sData);
        setIncidents(iData);
        setLastUpdated(new Date());
        setError(null);
      }
    } catch (e) {
      setError(e.message);
    }
  }, [incidentLimit]);

  useEffect(() => {
    fetchAll();
    const id = setInterval(fetchAll, interval);
    return () => clearInterval(id);
  }, [fetchAll, interval]);

  return {
    graph,
    stats,
    incidents,
    error,
    lastUpdated,
    refetch: fetchAll,
    events: {
      edgeEvents,
      newIncidentIds,
      blockedTargets,
      kpiFlashes,
    },
  };
}

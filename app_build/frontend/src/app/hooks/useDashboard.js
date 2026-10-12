"use client";

import { useState, useEffect, useCallback } from "react";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function useDashboard(interval = 4000) {
  const [graph, setGraph] = useState({ nodes: [], edges: [] });
  const [stats, setStats] = useState({
    active_agents: 0,
    messages_inspected: 0,
    messages_flagged: 0,
    trust_edges: 0,
  });
  const [incidents, setIncidents] = useState([]);
  const [error, setError] = useState(null);

  const fetchAll = useCallback(async () => {
    try {
      const [gRes, sRes, iRes] = await Promise.all([
        fetch(`${API}/api/dashboard/graph`),
        fetch(`${API}/api/dashboard/stats`),
        fetch(`${API}/api/dashboard/incidents`),
      ]);

      if (gRes.ok) setGraph(await gRes.json());
      if (sRes.ok) setStats(await sRes.json());
      if (iRes.ok) setIncidents(await iRes.json());
      setError(null);
    } catch (e) {
      setError(e.message);
    }
  }, []);

  useEffect(() => {
    fetchAll();
    const id = setInterval(fetchAll, interval);
    return () => clearInterval(id);
  }, [fetchAll, interval]);

  return { graph, stats, incidents, error };
}

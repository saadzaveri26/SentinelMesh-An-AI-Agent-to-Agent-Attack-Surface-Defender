"use client";

import Link from "next/link";

function formatTime(d) {
  if (!d) return "";
  return d.toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hour12: false,
  });
}

export default function Shell({ title, activeNav, stats, error, lastUpdated, children }) {
  const flagged = stats?.messages_flagged || 0;

  return (
    <div className="shell">
      <nav className="sidebar">
        <div className="sidebar-title">SentinelMesh</div>
        <ul className="sidebar-nav">
          <li>
            <Link
              href="/"
              className={`sidebar-item${activeNav === "overview" ? " active" : ""}`}
            >
              Overview
            </Link>
          </li>
          <li>
            <Link
              href="/trust-graph"
              className={`sidebar-item${activeNav === "graph" ? " active" : ""}`}
            >
              Trust Graph
            </Link>
          </li>
          <li>
            <Link
              href="/incidents"
              className={`sidebar-item${activeNav === "incidents" ? " active" : ""}`}
            >
              Incidents
              {flagged > 0 && <span className="sidebar-badge">{flagged}</span>}
            </Link>
          </li>
        </ul>
      </nav>

      <div className="main">
        <div className="topbar">
          <span className="topbar-title">{title}</span>
          <div className="topbar-status">
            <span className={`topbar-dot${error ? " error" : ""}`} />
            {error ? (
              <span style={{ color: "var(--critical)" }}>Disconnected</span>
            ) : (
              <span>Live, polling every 4s</span>
            )}
            {lastUpdated && !error && (
              <span className="topbar-time">Updated {formatTime(lastUpdated)}</span>
            )}
          </div>
        </div>

        <div className="page-content">{children}</div>
      </div>
    </div>
  );
}

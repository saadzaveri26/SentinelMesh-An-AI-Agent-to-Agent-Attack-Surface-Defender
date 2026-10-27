"use client";

import { useState, useMemo } from "react";

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
  const date = d.toLocaleDateString("en-GB", { day: "numeric", month: "short" });
  return `${date} ${time}`;
}

function formatUtc(iso) {
  if (!iso) return "";
  const d = new Date(iso);
  return d.toISOString().replace("T", " ").replace("Z", " UTC");
}

export default function IncidentTable({ incidents, fullHeight = false, newIds }) {
  const [search, setSearch] = useState("");
  const [filter, setFilter] = useState("all");
  const [drawerItem, setDrawerItem] = useState(null);

  const items = useMemo(() => {
    let rows = (incidents || []).filter(
      (inc) => inc.flagged || (inc.anomaly_flags && inc.anomaly_flags.length > 0) || inc.flag_name
    );

    if (filter === "blocked") {
      rows = rows.filter((r) => r.flagged);
    } else if (filter === "anomaly") {
      rows = rows.filter(
        (r) => !r.flagged && ((r.anomaly_flags && r.anomaly_flags.length > 0) || r.flag_name)
      );
    }

    if (search.trim()) {
      const q = search.trim().toLowerCase();
      rows = rows.filter(
        (r) =>
          (r.sender || "").toLowerCase().includes(q) ||
          (r.receiver || "").toLowerCase().includes(q) ||
          (r.content_preview || "").toLowerCase().includes(q)
      );
    }

    return rows;
  }, [incidents, filter, search]);

  return (
    <div className={`incident-section${fullHeight ? " full-height" : ""}`}>
      <div className="incident-toolbar">
        <span className="incident-toolbar-title">Incidents ({items.length})</span>
        <input
          className="incident-search"
          placeholder="Search sender, receiver, content"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <div className="incident-filter">
          {["all", "blocked", "anomaly"].map((f) => (
            <button
              key={f}
              className={`filter-btn${filter === f ? " active" : ""}`}
              onClick={() => setFilter(f)}
            >
              {f.charAt(0).toUpperCase() + f.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {items.length === 0 ? (
        <div className="empty-state" style={{ height: 160 }}>
          No incidents yet
        </div>
      ) : (
        <div className="incident-table-wrap">
          <table className="incident-tbl">
            <thead>
              <tr>
                <th>Time</th>
                <th>Path</th>
                <th>Score / Flag</th>
                <th>Description</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {items.map((inc) => {
                const isBlocked = !!inc.flagged;
                const isAnomalyOnly = !isBlocked &&
                  ((inc.anomaly_flags && inc.anomaly_flags.length > 0) || inc.flag_name);
                const flagName = inc.flag_name ||
                  (inc.anomaly_flags && inc.anomaly_flags[0]) || "anomaly";
                const score = inc.bert_score;
                const isNew = newIds?.has(String(inc.id));

                let rowClass = "";
                if (isBlocked) rowClass += " row-blocked";
                else if (isAnomalyOnly) rowClass += " row-anomaly";
                if (isNew) rowClass += " incident-row-new";
                if (drawerItem?.id === inc.id) rowClass += " selected-row";

                return (
                  <tr
                    key={inc.id}
                    className={rowClass.trim()}
                    onClick={() => setDrawerItem(inc)}
                  >
                    <td className="mono">{formatTs(inc.timestamp)}</td>
                    <td className="mono">{inc.sender} → {inc.receiver}</td>
                    <td>
                      {isAnomalyOnly ? (
                        <span className="score-val anomaly-score">{flagName}</span>
                      ) : (
                        <span className="score-val flagged">
                          {score !== undefined && score !== null
                            ? Number(score).toFixed(2)
                            : "0.00"}
                        </span>
                      )}
                    </td>
                    <td className="td-desc">{inc.content_preview}</td>
                    <td>
                      {isBlocked ? (
                        <span className="status-chip blocked">Blocked</span>
                      ) : (
                        <span className="status-chip anomaly-chip">Anomaly</span>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {drawerItem && (
        <>
          <div className="drawer-overlay" onClick={() => setDrawerItem(null)} />
          <div className="drawer">
            <div className="drawer-head">
              <h3>Incident Detail</h3>
              <button className="drawer-close" onClick={() => setDrawerItem(null)}>
                ✕
              </button>
            </div>
            <div className="drawer-body">
              <div className="drawer-field">
                <div className="drawer-field-label">Status</div>
                <div className="drawer-field-value">
                  {drawerItem.flagged ? (
                    <span className="status-chip blocked">Blocked</span>
                  ) : (
                    <span className="status-chip anomaly-chip">Anomaly</span>
                  )}
                </div>
              </div>

              <div className="drawer-field">
                <div className="drawer-field-label">Sender</div>
                <div className="drawer-field-value">{drawerItem.sender}</div>
              </div>

              <div className="drawer-field">
                <div className="drawer-field-label">Receiver</div>
                <div className="drawer-field-value">{drawerItem.receiver}</div>
              </div>

              <div className="drawer-field">
                <div className="drawer-field-label">BERT Score</div>
                <div className="drawer-field-value">
                  {drawerItem.bert_score !== undefined && drawerItem.bert_score !== null
                    ? Number(drawerItem.bert_score).toFixed(4)
                    : "N/A"}
                </div>
              </div>

              {drawerItem.rule_hits && Object.keys(drawerItem.rule_hits).length > 0 && (
                <div className="drawer-field">
                  <div className="drawer-field-label">Rule Hits</div>
                  <div className="drawer-content-block">
                    {JSON.stringify(drawerItem.rule_hits, null, 2)}
                  </div>
                </div>
              )}

              {drawerItem.anomaly_flags && drawerItem.anomaly_flags.length > 0 && (
                <div className="drawer-field">
                  <div className="drawer-field-label">Anomaly Flags</div>
                  <div className="drawer-field-value">
                    {drawerItem.anomaly_flags.join(", ")}
                  </div>
                </div>
              )}

              <div className="drawer-field">
                <div className="drawer-field-label">Timestamp (local)</div>
                <div className="drawer-field-value">
                  {drawerItem.timestamp
                    ? new Date(drawerItem.timestamp).toLocaleString()
                    : "N/A"}
                </div>
              </div>

              <div className="drawer-field">
                <div className="drawer-field-label">Timestamp (UTC)</div>
                <div className="drawer-field-value">
                  {formatUtc(drawerItem.timestamp)}
                </div>
              </div>

              <div className="drawer-field">
                <div className="drawer-field-label">Content</div>
                <div className="drawer-content-block">
                  {drawerItem.content || drawerItem.content_preview || "N/A"}
                </div>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}

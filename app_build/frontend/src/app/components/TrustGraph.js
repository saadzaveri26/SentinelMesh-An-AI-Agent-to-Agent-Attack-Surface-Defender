"use client";

import {
  ReactFlow,
  Background,
  Controls,
  useNodesState,
  useEdgesState,
  useReactFlow,
  BaseEdge,
  EdgeLabelRenderer,
  getStraightPath,
  useInternalNode,
  Handle,
  Position,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import { useEffect, useState, useMemo, useCallback } from "react";

function GraphFit({ count }) {
  const { fitView } = useReactFlow();

  useEffect(() => {
    if (count > 0) {
      const id = requestAnimationFrame(() => {
        fitView({ padding: 0.3, duration: 200 });
      });
      return () => cancelAnimationFrame(id);
    }
  }, [count, fitView]);

  return null;
}

function edgeStateColor(score) {
  if (score >= 0.5) return "#3DDC97";
  if (score >= 0.3) return "#F2A93B";
  return "#F0545A";
}

function worstEdgeColor(nodeId, edges) {
  let worst = 1;
  let hasEdge = false;
  for (const e of edges) {
    if (String(e.source) === String(nodeId) || String(e.target) === String(nodeId)) {
      hasEdge = true;
      const s = e.data?.score ?? 1;
      if (s < worst) worst = s;
    }
  }
  if (!hasEdge) return "#2A3850";
  return edgeStateColor(worst);
}

function getNodeCenter(node) {
  const x = (node.internals?.positionAbsolute?.x ?? node.position?.x ?? 0) + (node.measured?.width || 140) / 2;
  const y = (node.internals?.positionAbsolute?.y ?? node.position?.y ?? 0) + (node.measured?.height || 38) / 2;
  return { x, y };
}

function getNodeIntersection(intersectionNode, targetNode) {
  const w = intersectionNode.measured?.width || 140;
  const h = intersectionNode.measured?.height || 38;
  const pos = intersectionNode.internals?.positionAbsolute ?? intersectionNode.position ?? { x: 0, y: 0 };
  const center = { x: pos.x + w / 2, y: pos.y + h / 2 };
  const targetCenter = getNodeCenter(targetNode);

  const dx = targetCenter.x - center.x;
  const dy = targetCenter.y - center.y;
  if (dx === 0 && dy === 0) return center;

  const slope = Math.abs(dy / dx);
  const nodeRatio = h / w;

  if (slope <= nodeRatio) {
    const signX = dx > 0 ? 1 : -1;
    return {
      x: center.x + signX * (w / 2),
      y: center.y + signX * (w / 2) * (dy / dx),
    };
  }
  const signY = dy > 0 ? 1 : -1;
  return {
    x: center.x + signY * (h / 2) * (dx / dy),
    y: center.y + signY * (h / 2),
  };
}

function FloatingEdge({ id, source, target, data, style }) {
  const sourceNode = useInternalNode(source);
  const targetNode = useInternalNode(target);

  if (!sourceNode || !targetNode) return null;

  const sourceP = getNodeIntersection(sourceNode, targetNode);
  const targetP = getNodeIntersection(targetNode, sourceNode);

  const [edgePath, labelX, labelY] = getStraightPath({
    sourceX: sourceP.x,
    sourceY: sourceP.y,
    targetX: targetP.x,
    targetY: targetP.y,
  });

  const score = data?.score ?? 0.5;
  let stateClass = "normal";
  let strokeColor = "#3DDC97";
  let isCritical = false;

  if (score >= 0.5) {
    stateClass = "normal";
    strokeColor = "#3DDC97";
  } else if (score >= 0.3) {
    stateClass = "anomalous";
    strokeColor = "#F2A93B";
  } else {
    stateClass = "critical";
    strokeColor = "#F0545A";
    isCritical = true;
  }

  const edgeStyle = {
    ...style,
    stroke: strokeColor,
    strokeWidth: 2,
    strokeDasharray: isCritical ? "4 3" : undefined,
  };

  const hasTraffic = !!data?.hasTraffic;

  return (
    <>
      <BaseEdge id={id} path={edgePath} style={edgeStyle} />
      {hasTraffic && (
        <circle r={3.5} fill={strokeColor} className="edge-traveling-dot">
          <animateMotion
            path={edgePath}
            dur="700ms"
            repeatCount="1"
            fill="remove"
            keyTimes="0;1"
            keySplines="0.2 0 0 1"
            calcMode="spline"
          />
        </circle>
      )}
      <EdgeLabelRenderer>
        <div
          style={{
            position: "absolute",
            transform: `translate(-50%, -50%) translate(${labelX}px,${labelY}px)`,
          }}
          className={`edge-chip ${stateClass}`}
        >
          {score.toFixed(2)}
        </div>
      </EdgeLabelRenderer>
    </>
  );
}

function AgentNode({ data, selected }) {
  const isBlocked = !!data?.blockedRing;
  const worstColor = data?.worstColor || "#2A3850";

  return (
    <div
      className={`agent-node${selected ? " selected" : ""}`}
      style={{ borderColor: worstColor }}
    >
      <Handle type="target" position={Position.Top} style={{ opacity: 0, width: 1, height: 1 }} />
      <Handle type="source" position={Position.Bottom} style={{ opacity: 0, width: 1, height: 1 }} />
      <span className="agent-node-dot" style={{ background: worstColor }} />
      <span className="agent-node-label">{data.label}</span>
      {isBlocked && <span className="agent-node-ring" />}
    </div>
  );
}

const nodeTypes = { agent: AgentNode };
const edgeTypes = { floating: FloatingEdge };

export default function TrustGraph({
  nodes: incoming,
  edges: incomingEdges,
  onNodeClick,
  onEdgeClick,
  onFitView,
  showIdleToggle,
  edgeEvents,
  blockedTargets,
}) {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [showIdle, setShowIdle] = useState(false);

  const { activeNodes, idleNodes } = useMemo(() => {
    const ids = new Set();
    (incomingEdges || []).forEach((e) => {
      ids.add(String(e.source));
      ids.add(String(e.target));
    });
    const act = (incoming || []).filter((n) => ids.has(String(n.id)));
    const idl = (incoming || []).filter((n) => !ids.has(String(n.id)));
    return { activeNodes: act, idleNodes: idl };
  }, [incoming, incomingEdges]);

  const visibleNodes = useMemo(() => {
    if (showIdle || activeNodes.length === 0) return incoming || [];
    return activeNodes;
  }, [showIdle, activeNodes, incoming]);

  useEffect(() => {
    if (visibleNodes.length > 0) {
      const angle = (2 * Math.PI) / visibleNodes.length;
      const cx = 400, cy = 300, r = Math.min(220, Math.max(120, visibleNodes.length * 25));
      const positioned = visibleNodes.map((n, i) => {
        const label = n.data?.label || n.id;
        const isBlocked = blockedTargets && (blockedTargets.has(label) || blockedTargets.has(String(n.id)));
        const worstColor = worstEdgeColor(n.id, incomingEdges || []);
        return {
          ...n,
          type: "agent",
          position: {
            x: cx + r * Math.cos(angle * i - Math.PI / 2),
            y: cy + r * Math.sin(angle * i - Math.PI / 2),
          },
          data: {
            ...n.data,
            label,
            worstColor,
            blockedRing: isBlocked,
          },
        };
      });
      setNodes(positioned);
    } else {
      setNodes([]);
    }
  }, [visibleNodes, incomingEdges, blockedTargets, setNodes]);

  useEffect(() => {
    if (incomingEdges) {
      const floatEdges = incomingEdges.map((e) => {
        const hasTraffic = edgeEvents && !!edgeEvents[String(e.id)];
        return {
          ...e,
          type: "floating",
          data: {
            ...e.data,
            hasTraffic,
          },
        };
      });
      setEdges(floatEdges);
    }
  }, [incomingEdges, edgeEvents, setEdges]);

  const handleNodeClick = useCallback((_event, node) => {
    if (onNodeClick) onNodeClick(node);
  }, [onNodeClick]);

  const handleEdgeClick = useCallback((_event, edge) => {
    if (onEdgeClick) onEdgeClick(edge);
  }, [onEdgeClick]);

  if (showIdleToggle) {
    showIdleToggle.current = {
      count: idleNodes.length,
      active: showIdle,
      toggle: () => setShowIdle(!showIdle),
      hasIdle: idleNodes.length > 0 && activeNodes.length > 0,
    };
  }

  if (onFitView) {
    onFitView.current = nodes.length;
  }

  if (!incoming || incoming.length === 0) {
    return <div className="empty-state">No agents detected yet</div>;
  }

  return (
    <div style={{ width: "100%", height: "100%", position: "relative" }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        nodeTypes={nodeTypes}
        edgeTypes={edgeTypes}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onNodeClick={handleNodeClick}
        onEdgeClick={handleEdgeClick}
        fitView
        fitViewOptions={{ padding: 0.3 }}
        proOptions={{ hideAttribution: true }}
        minZoom={0.3}
        maxZoom={2}
      >
        <Background color="#1B2535" gap={20} size={1} />
        <Controls position="bottom-left" />
        <GraphFit count={nodes.length} />
      </ReactFlow>
    </div>
  );
}

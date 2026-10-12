"use client";

import {
  ReactFlow,
  Background,
  Controls,
  useNodesState,
  useEdgesState,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import { useEffect } from "react";

export default function TrustGraph({ nodes: incoming, edges: incomingEdges }) {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);

  useEffect(() => {
    if (incoming.length > 0) {
      const angle = (2 * Math.PI) / incoming.length;
      const cx = 400, cy = 300, r = 220;
      const positioned = incoming.map((n, i) => ({
        ...n,
        position: n.position || {
          x: cx + r * Math.cos(angle * i - Math.PI / 2),
          y: cy + r * Math.sin(angle * i - Math.PI / 2),
        },
        type: "default",
      }));
      setNodes(positioned);
    }
  }, [incoming, setNodes]);

  useEffect(() => {
    if (incomingEdges.length > 0) {
      setEdges(incomingEdges);
    }
  }, [incomingEdges, setEdges]);

  if (incoming.length === 0) {
    return <div className="empty-state">No agents detected yet</div>;
  }

  return (
    <ReactFlow
      nodes={nodes}
      edges={edges}
      onNodesChange={onNodesChange}
      onEdgesChange={onEdgesChange}
      fitView
      fitViewOptions={{ padding: 0.3 }}
      proOptions={{ hideAttribution: true }}
      minZoom={0.3}
      maxZoom={2}
    >
      <Background color="#1E2433" gap={20} size={1} />
      <Controls position="bottom-left" />
    </ReactFlow>
  );
}

import React, { useRef, useEffect, useState } from 'react';
import { GoalRelationshipMap, GoalRelationship } from '../../../services/goalRelationshipService';

interface Node {
  id: string;
  label: string;
  x: number;
  y: number;
  radius: number;
  color: string;
  icon: string;
}

interface Edge {
  source: string;
  target: string;
  type: 'synergistic' | 'conflicting' | 'neutral' | 'complementary' | 'prerequisite';
  strength: number;
  color: string;
  strokeWidth: number;
}

interface GoalRelationshipGraphProps {
  relationshipMap: GoalRelationshipMap;
  width?: number;
  height?: number;
  className?: string;
  onNodeClick?: (goalId: string) => void;
}

const GoalRelationshipGraph: React.FC<GoalRelationshipGraphProps> = ({
  relationshipMap,
  width = 600,
  height = 400,
  className = '',
  onNodeClick
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [hoveredNode, setHoveredNode] = useState<string | null>(null);
  const [nodes, setNodes] = useState<Node[]>([]);
  const [edges, setEdges] = useState<Edge[]>([]);

  // Goal icons mapping
  const goalIcons: Record<string, string> = {
    'anxiety_reduction': '🧘',
    'depression_management': '🌅',
    'stress_management': '🌿',
    'emotional_regulation': '💙',
    'mindfulness_practice': '🧠',
    'self_esteem_building': '⭐',
    'relationship_skills': '🤝',
    'communication_improvement': '💬',
    'trauma_recovery': '🌱',
    'grief_processing': '🕊️',
    'anger_management': '🔥',
    'perfectionism_reduction': '🎯',
    'work_life_balance': '⚖️',
    'sleep_improvement': '😴',
    'addiction_recovery': '🔓'
  };

  // Color mapping for relationship types
  const relationshipColors = {
    synergistic: '#10B981', // green
    complementary: '#3B82F6', // blue
    prerequisite: '#8B5CF6', // purple
    neutral: '#6B7280', // gray
    conflicting: '#EF4444' // red
  };

  // Initialize nodes and edges
  useEffect(() => {
    if (!relationshipMap.goals.length) {
      setNodes([]);
      setEdges([]);
      return;
    }

    // Create nodes
    const nodeRadius = 30;
    const centerX = width / 2;
    const centerY = height / 2;
    const radius = Math.min(width, height) * 0.3;

    const newNodes: Node[] = relationshipMap.goals.map((goalId, index) => {
      const angle = (index / relationshipMap.goals.length) * 2 * Math.PI;
      const x = centerX + radius * Math.cos(angle);
      const y = centerY + radius * Math.sin(angle);

      return {
        id: goalId,
        label: goalId.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
        x,
        y,
        radius: nodeRadius,
        color: '#3B82F6',
        icon: goalIcons[goalId] || '🎯'
      };
    });

    // Create edges
    const newEdges: Edge[] = relationshipMap.relationships.map(rel => ({
      source: rel.sourceGoal,
      target: rel.targetGoal,
      type: rel.relationshipType,
      strength: rel.strength,
      color: relationshipColors[rel.relationshipType],
      strokeWidth: Math.max(1, rel.strength * 4)
    }));

    setNodes(newNodes);
    setEdges(newEdges);
  }, [relationshipMap, width, height]);

  // Draw the graph
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Clear canvas
    ctx.clearRect(0, 0, width, height);

    // Draw edges
    edges.forEach(edge => {
      const sourceNode = nodes.find(n => n.id === edge.source);
      const targetNode = nodes.find(n => n.id === edge.target);
      
      if (!sourceNode || !targetNode) return;

      ctx.beginPath();
      ctx.moveTo(sourceNode.x, sourceNode.y);
      ctx.lineTo(targetNode.x, targetNode.y);
      ctx.strokeStyle = edge.color;
      ctx.lineWidth = edge.strokeWidth;
      ctx.globalAlpha = 0.7;
      ctx.stroke();
      ctx.globalAlpha = 1;

      // Draw relationship type indicator
      const midX = (sourceNode.x + targetNode.x) / 2;
      const midY = (sourceNode.y + targetNode.y) / 2;
      
      ctx.fillStyle = edge.color;
      ctx.beginPath();
      ctx.arc(midX, midY, 3, 0, 2 * Math.PI);
      ctx.fill();
    });

    // Draw nodes
    nodes.forEach(node => {
      const isHovered = hoveredNode === node.id;
      const nodeRadius = isHovered ? node.radius * 1.2 : node.radius;

      // Draw node circle
      ctx.beginPath();
      ctx.arc(node.x, node.y, nodeRadius, 0, 2 * Math.PI);
      ctx.fillStyle = isHovered ? '#1D4ED8' : node.color;
      ctx.fill();
      ctx.strokeStyle = '#FFFFFF';
      ctx.lineWidth = 3;
      ctx.stroke();

      // Draw icon
      ctx.font = '20px Arial';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillStyle = '#FFFFFF';
      ctx.fillText(node.icon, node.x, node.y);

      // Draw label
      if (isHovered) {
        ctx.font = '12px Arial';
        ctx.fillStyle = '#374151';
        ctx.textAlign = 'center';
        ctx.fillText(node.label, node.x, node.y + nodeRadius + 15);
      }
    });
  }, [nodes, edges, hoveredNode, width, height]);

  // Handle mouse events
  const handleMouseMove = (event: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const rect = canvas.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;

    // Check if mouse is over a node
    const hoveredNodeId = nodes.find(node => {
      const distance = Math.sqrt((x - node.x) ** 2 + (y - node.y) ** 2);
      return distance <= node.radius;
    })?.id || null;

    setHoveredNode(hoveredNodeId);
  };

  const handleClick = (event: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    if (!canvas || !onNodeClick) return;

    const rect = canvas.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;

    // Check if click is on a node
    const clickedNode = nodes.find(node => {
      const distance = Math.sqrt((x - node.x) ** 2 + (y - node.y) ** 2);
      return distance <= node.radius;
    });

    if (clickedNode) {
      onNodeClick(clickedNode.id);
    }
  };

  if (!relationshipMap.goals.length) {
    return (
      <div className={`flex items-center justify-center bg-gray-50 rounded-lg ${className}`} style={{ width, height }}>
        <div className="text-center text-gray-500">
          <div className="text-4xl mb-2">🎯</div>
          <p>Select goals to see relationships</p>
        </div>
      </div>
    );
  }

  return (
    <div className={`relative ${className}`}>
      <canvas
        ref={canvasRef}
        width={width}
        height={height}
        className="border border-gray-200 rounded-lg cursor-pointer"
        onMouseMove={handleMouseMove}
        onClick={handleClick}
        style={{ width, height }}
      />
      
      {/* Legend */}
      <div className="absolute top-2 right-2 bg-white bg-opacity-90 rounded-lg p-2 text-xs">
        <div className="space-y-1">
          <div className="flex items-center space-x-2">
            <div className="w-3 h-0.5 bg-green-500"></div>
            <span>Synergistic</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-0.5 bg-blue-500"></div>
            <span>Complementary</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-0.5 bg-purple-500"></div>
            <span>Prerequisite</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-0.5 bg-red-500"></div>
            <span>Conflicting</span>
          </div>
        </div>
      </div>

      {/* Hover tooltip */}
      {hoveredNode && (
        <div className="absolute bottom-2 left-2 bg-black bg-opacity-75 text-white rounded px-2 py-1 text-sm">
          {nodes.find(n => n.id === hoveredNode)?.label}
        </div>
      )}
    </div>
  );
};

export default GoalRelationshipGraph;

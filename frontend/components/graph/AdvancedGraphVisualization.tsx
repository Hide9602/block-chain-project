'use client';

import React, { useEffect, useRef, useState } from 'react';
import cytoscape, { Core, NodeSingular, EdgeSingular, Layouts } from 'cytoscape';
import { useTranslation } from 'react-i18next';

// Extended graph data types with ML insights
interface GraphNode {
  id: string;
  address: string;
  nodeType: 'wallet' | 'exchange' | 'mixer' | 'contract' | 'unknown';
  label?: string;
  balance?: number;
  riskLevel: 'critical' | 'high' | 'medium' | 'low' | 'minimal' | 'none';
  riskScore?: number;
  isSanctioned: boolean;
  transactionCount?: number;
  totalReceived?: number;
  totalSent?: number;
  detectedPatterns: string[];
}

interface GraphEdge {
  id: string;
  source: string;
  target: string;
  amount: number;
  timestamp: string;
  txHash: string;
  isSuspicious: boolean;
  riskIndicators: string[];
  confidence?: number;
}

interface AdvancedGraphVisualizationProps {
  nodes: GraphNode[];
  edges: GraphEdge[];
  highRiskNodes?: string[];
  suspiciousEdges?: string[];
  onNodeClick?: (node: GraphNode) => void;
  onEdgeClick?: (edge: GraphEdge) => void;
  height?: string;
  className?: string;
}

type LayoutType = 'cose' | 'circle' | 'grid' | 'concentric' | 'breadthfirst';
type FilterMode = 'all' | 'high-risk' | 'suspicious' | 'sanctioned';

export const AdvancedGraphVisualization: React.FC<AdvancedGraphVisualizationProps> = ({
  nodes,
  edges,
  highRiskNodes = [],
  suspiciousEdges = [],
  onNodeClick,
  onEdgeClick,
  height = '700px',
  className = '',
}) => {
  const { t } = useTranslation('glossary');
  const containerRef = useRef<HTMLDivElement>(null);
  const cyRef = useRef<Core | null>(null);
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
  const [selectedEdge, setSelectedEdge] = useState<GraphEdge | null>(null);
  const [layout, setLayout] = useState<LayoutType>('cose');
  const [filterMode, setFilterMode] = useState<FilterMode>('all');
  const [showLabels, setShowLabels] = useState(true);
  const [highlightClusters, setHighlightClusters] = useState(false);

  // Enhanced risk color mapping with critical level
  const getRiskColor = (riskLevel: string): string => {
    switch (riskLevel) {
      case 'critical':
        return '#dc2626'; // Deep red
      case 'high':
        return '#ef4444'; // Red
      case 'medium':
        return '#f59e0b'; // Orange
      case 'low':
        return '#22c55e'; // Green
      case 'minimal':
        return '#6ee7b7'; // Light green
      default:
        return '#64748b'; // Gray
    }
  };

  // Node type colors with enhanced palette
  const getNodeTypeColor = (nodeType: string): string => {
    switch (nodeType) {
      case 'wallet':
        return '#3b82f6'; // Blue
      case 'exchange':
        return '#8b5cf6'; // Purple
      case 'mixer':
        return '#dc2626'; // Deep red (sanctioned)
      case 'contract':
        return '#06b6d4'; // Cyan
      default:
        return '#94a3b8'; // Gray
    }
  };

  // Get node size based on transaction volume
  const getNodeSize = (node: GraphNode): number => {
    const baseSize = 40;
    const volume = (node.totalReceived || 0) + (node.totalSent || 0);
    
    if (volume > 100) return 80;
    if (volume > 50) return 65;
    if (volume > 10) return 55;
    if (volume > 1) return 45;
    return baseSize;
  };

  // Filter nodes and edges based on filter mode
  const getFilteredElements = () => {
    let filteredNodes = nodes;
    let filteredEdges = edges;

    switch (filterMode) {
      case 'high-risk':
        filteredNodes = nodes.filter(n => 
          ['critical', 'high'].includes(n.riskLevel)
        );
        // Only show edges between high-risk nodes
        const highRiskIds = new Set(filteredNodes.map(n => n.id));
        filteredEdges = edges.filter(e => 
          highRiskIds.has(e.source) && highRiskIds.has(e.target)
        );
        break;
      
      case 'suspicious':
        // Show all nodes but only suspicious edges
        filteredEdges = edges.filter(e => e.isSuspicious);
        // Include nodes that have suspicious edges
        const suspiciousNodeIds = new Set<string>();
        filteredEdges.forEach(e => {
          suspiciousNodeIds.add(e.source);
          suspiciousNodeIds.add(e.target);
        });
        filteredNodes = nodes.filter(n => suspiciousNodeIds.has(n.id));
        break;
      
      case 'sanctioned':
        filteredNodes = nodes.filter(n => n.isSanctioned);
        const sanctionedIds = new Set(filteredNodes.map(n => n.id));
        filteredEdges = edges.filter(e => 
          sanctionedIds.has(e.source) || sanctionedIds.has(e.target)
        );
        break;
      
      default:
        // Show all
        break;
    }

    return { filteredNodes, filteredEdges };
  };

  useEffect(() => {
    if (!containerRef.current || nodes.length === 0) return;

    const { filteredNodes, filteredEdges } = getFilteredElements();

    // Cytoscape initialization with enhanced styling
    const cy = cytoscape({
      container: containerRef.current,
      elements: [
        // Nodes
        ...filteredNodes.map((node) => ({
          data: {
            ...node,
            id: node.id,
            label: showLabels ? (node.label || node.address.substring(0, 8) + '...') : '',
          },
        })),
        // Edges
        ...filteredEdges.map((edge) => ({
          data: {
            ...edge,
            id: edge.id,
            source: edge.source,
            target: edge.target,
            label: showLabels ? `${edge.amount.toFixed(2)} ETH` : '',
          },
        })),
      ],
      style: [
        // Base node style
        {
          selector: 'node',
          style: {
            'background-color': (ele: NodeSingular) => {
              const node = ele.data() as GraphNode;
              if (node.isSanctioned) return '#dc2626';
              if (highlightClusters) {
                // Use risk level for clustering
                return getRiskColor(node.riskLevel);
              }
              return getNodeTypeColor(node.nodeType);
            },
            label: 'data(label)',
            'text-valign': 'center',
            'text-halign': 'center',
            color: '#fff',
            'font-size': '11px',
            'font-weight': 'bold',
            'text-outline-width': 2,
            'text-outline-color': '#000',
            width: (ele: NodeSingular) => {
              const node = ele.data() as GraphNode;
              return getNodeSize(node);
            },
            height: (ele: NodeSingular) => {
              const node = ele.data() as GraphNode;
              return getNodeSize(node);
            },
            'border-width': (ele: NodeSingular) => {
              const node = ele.data() as GraphNode;
              if (node.riskLevel === 'critical') return 6;
              if (node.riskLevel === 'high') return 4;
              return 2;
            },
            'border-color': (ele: NodeSingular) => {
              const node = ele.data() as GraphNode;
              return getRiskColor(node.riskLevel);
            },
            'border-style': (ele: NodeSingular) => {
              const node = ele.data() as GraphNode;
              return node.isSanctioned ? 'double' : 'solid';
            },
          },
        },
        // High-risk node highlight
        {
          selector: `[id^="node-"][riskLevel = "critical"], [id^="node-"][riskLevel = "high"]`,
          style: {
            'background-opacity': 0.9,
            'overlay-color': '#ef4444',
            'overlay-padding': 5,
            'overlay-opacity': 0.3,
          },
        },
        // Edge style
        {
          selector: 'edge',
          style: {
            width: (ele: EdgeSingular) => {
              const edge = ele.data() as GraphEdge;
              return Math.min(Math.max(edge.amount / 2, 1), 12);
            },
            'line-color': (ele: EdgeSingular) => {
              const edge = ele.data() as GraphEdge;
              if (edge.isSuspicious) return '#ef4444';
              return '#cbd5e1';
            },
            'target-arrow-color': (ele: EdgeSingular) => {
              const edge = ele.data() as GraphEdge;
              if (edge.isSuspicious) return '#ef4444';
              return '#cbd5e1';
            },
            'target-arrow-shape': 'triangle',
            'curve-style': 'bezier',
            label: 'data(label)',
            'font-size': '9px',
            color: '#1e293b',
            'text-rotation': 'autorotate',
            'text-margin-y': -8,
            'text-background-color': '#fff',
            'text-background-opacity': 0.8,
            'text-background-padding': '2px',
            opacity: (ele: EdgeSingular) => {
              const edge = ele.data() as GraphEdge;
              return edge.isSuspicious ? 1.0 : 0.6;
            },
            'line-style': (ele: EdgeSingular) => {
              const edge = ele.data() as GraphEdge;
              return edge.isSuspicious ? 'solid' : 'solid';
            },
          },
        },
        // Suspicious edge highlight
        {
          selector: 'edge[isSuspicious = true]',
          style: {
            'line-dash-pattern': [6, 3],
            'arrow-scale': 1.5,
          },
        },
        // Selection style
        {
          selector: ':selected',
          style: {
            'border-width': 6,
            'border-color': '#0ea5e9',
            'background-color': '#0ea5e9',
            'line-color': '#0ea5e9',
            'target-arrow-color': '#0ea5e9',
            'z-index': 999,
          },
        },
        // Hover style
        {
          selector: 'node:active',
          style: {
            'overlay-color': '#0ea5e9',
            'overlay-padding': 10,
            'overlay-opacity': 0.3,
          },
        },
      ],
      layout: {
        name: layout,
        animate: true,
        animationDuration: 500,
        // Layout-specific options
        ...(layout === 'cose' && {
          nodeRepulsion: 10000,
          idealEdgeLength: 120,
          edgeElasticity: 100,
          nestingFactor: 5,
          gravity: 100,
          numIter: 1000,
          initialTemp: 200,
          coolingFactor: 0.95,
          minTemp: 1.0,
        }),
        ...(layout === 'concentric' && {
          concentric: (node: NodeSingular) => {
            const n = node.data() as GraphNode;
            // Arrange by risk level
            const riskOrder = { critical: 5, high: 4, medium: 3, low: 2, minimal: 1, none: 0 };
            return riskOrder[n.riskLevel as keyof typeof riskOrder] || 0;
          },
          levelWidth: () => 2,
        }),
      },
      minZoom: 0.2,
      maxZoom: 4,
      wheelSensitivity: 0.2,
    });

    // Event handlers
    cy.on('tap', 'node', (event) => {
      const node = event.target.data() as GraphNode;
      setSelectedNode(node);
      setSelectedEdge(null);
      if (onNodeClick) {
        onNodeClick(node);
      }
    });

    cy.on('tap', 'edge', (event) => {
      const edge = event.target.data() as GraphEdge;
      setSelectedEdge(edge);
      setSelectedNode(null);
      if (onEdgeClick) {
        onEdgeClick(edge);
      }
    });

    cy.on('tap', (event) => {
      if (event.target === cy) {
        setSelectedNode(null);
        setSelectedEdge(null);
      }
    });

    cyRef.current = cy;

    return () => {
      cy.destroy();
    };
  }, [nodes, edges, layout, filterMode, showLabels, highlightClusters, onNodeClick, onEdgeClick]);

  // Control functions
  const fitGraph = () => cyRef.current?.fit(undefined, 50);
  const centerGraph = () => cyRef.current?.center();
  const resetZoom = () => {
    cyRef.current?.zoom(1);
    cyRef.current?.center();
  };
  const exportImage = () => {
    if (!cyRef.current) return;
    const png = cyRef.current.png({ scale: 3, full: true, bg: '#ffffff' });
    const link = document.createElement('a');
    link.href = png;
    link.download = `graph-export-${new Date().getTime()}.png`;
    link.click();
  };

  const changeLayout = (newLayout: LayoutType) => {
    setLayout(newLayout);
  };

  return (
    <div className={`relative ${className}`}>
      {/* Enhanced control panel */}
      <div className="absolute top-4 left-4 z-10 rounded-lg bg-white p-3 shadow-lg">
        <h4 className="mb-2 text-sm font-bold">{t('graphVisualization.controls', 'Controls')}</h4>
        
        {/* Layout selector */}
        <div className="mb-3">
          <label className="mb-1 block text-xs font-semibold">Layout</label>
          <select
            value={layout}
            onChange={(e) => changeLayout(e.target.value as LayoutType)}
            className="w-full rounded border px-2 py-1 text-xs"
          >
            <option value="cose">Force-Directed (COSE)</option>
            <option value="circle">Circle</option>
            <option value="grid">Grid</option>
            <option value="concentric">Concentric (Risk-based)</option>
            <option value="breadthfirst">Breadth-First</option>
          </select>
        </div>

        {/* Filter mode */}
        <div className="mb-3">
          <label className="mb-1 block text-xs font-semibold">Filter</label>
          <select
            value={filterMode}
            onChange={(e) => setFilterMode(e.target.value as FilterMode)}
            className="w-full rounded border px-2 py-1 text-xs"
          >
            <option value="all">All Transactions</option>
            <option value="high-risk">High Risk Only</option>
            <option value="suspicious">Suspicious Only</option>
            <option value="sanctioned">Sanctioned Addresses</option>
          </select>
        </div>

        {/* Toggle switches */}
        <div className="space-y-2">
          <label className="flex items-center text-xs">
            <input
              type="checkbox"
              checked={showLabels}
              onChange={(e) => setShowLabels(e.target.checked)}
              className="mr-2"
            />
            Show Labels
          </label>
          <label className="flex items-center text-xs">
            <input
              type="checkbox"
              checked={highlightClusters}
              onChange={(e) => setHighlightClusters(e.target.checked)}
              className="mr-2"
            />
            Color by Risk Level
          </label>
        </div>
      </div>

      {/* Zoom controls */}
      <div className="absolute top-4 right-4 z-10 flex flex-col gap-2">
        <button
          onClick={fitGraph}
          className="rounded-lg bg-white px-3 py-2 text-sm shadow-md hover:bg-gray-50"
          title="Fit Graph"
        >
          <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
          </svg>
        </button>
        <button
          onClick={centerGraph}
          className="rounded-lg bg-white px-3 py-2 text-sm shadow-md hover:bg-gray-50"
          title="Center"
        >
          <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
        </button>
        <button
          onClick={resetZoom}
          className="rounded-lg bg-white px-3 py-2 text-sm shadow-md hover:bg-gray-50"
          title="Reset Zoom"
        >
          <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM13 10H7" />
          </svg>
        </button>
        <button
          onClick={exportImage}
          className="rounded-lg bg-white px-3 py-2 text-sm shadow-md hover:bg-gray-50"
          title="Export Image"
        >
          <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
          </svg>
        </button>
      </div>

      {/* Graph container */}
      <div ref={containerRef} style={{ height, width: '100%' }} className="rounded-lg border bg-gray-50" />

      {/* Enhanced node details panel */}
      {selectedNode && (
        <div className="absolute bottom-4 left-4 z-10 w-96 rounded-lg bg-white p-4 shadow-xl">
          <h3 className="mb-3 flex items-center text-lg font-bold">
            <span className="mr-2">🔍</span>
            Node Details
          </h3>
          <div className="space-y-2 text-sm">
            <div className="rounded bg-gray-50 p-2">
              <span className="font-semibold">Address:</span>
              <br />
              <span className="font-mono text-xs">{selectedNode.address}</span>
            </div>
            <div className="flex justify-between">
              <span className="font-semibold">Type:</span>
              <span className="capitalize">{selectedNode.nodeType}</span>
            </div>
            {selectedNode.balance !== undefined && (
              <div className="flex justify-between">
                <span className="font-semibold">Balance:</span>
                <span>{selectedNode.balance.toFixed(4)} ETH</span>
              </div>
            )}
            {selectedNode.transactionCount !== undefined && (
              <div className="flex justify-between">
                <span className="font-semibold">Transactions:</span>
                <span>{selectedNode.transactionCount}</span>
              </div>
            )}
            <div className="flex justify-between">
              <span className="font-semibold">Risk Level:</span>
              <span
                className="rounded px-2 py-1 text-xs font-bold uppercase text-white"
                style={{ backgroundColor: getRiskColor(selectedNode.riskLevel) }}
              >
                {selectedNode.riskLevel}
              </span>
            </div>
            {selectedNode.riskScore !== undefined && (
              <div className="flex justify-between">
                <span className="font-semibold">Risk Score:</span>
                <span className="font-bold">{selectedNode.riskScore.toFixed(1)}/100</span>
              </div>
            )}
            {selectedNode.detectedPatterns.length > 0 && (
              <div>
                <span className="font-semibold">Patterns:</span>
                <div className="mt-1 flex flex-wrap gap-1">
                  {selectedNode.detectedPatterns.map((pattern, idx) => (
                    <span key={idx} className="rounded bg-orange-100 px-2 py-1 text-xs text-orange-800">
                      {pattern}
                    </span>
                  ))}
                </div>
              </div>
            )}
            {selectedNode.isSanctioned && (
              <div className="rounded bg-red-100 p-2 text-red-800">
                <span className="font-bold">⚠️ SANCTIONED ADDRESS</span>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Enhanced edge details panel */}
      {selectedEdge && (
        <div className="absolute bottom-4 left-4 z-10 w-96 rounded-lg bg-white p-4 shadow-xl">
          <h3 className="mb-3 flex items-center text-lg font-bold">
            <span className="mr-2">💸</span>
            Transaction Details
          </h3>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="font-semibold">Amount:</span>
              <span className="font-bold text-blue-600">{selectedEdge.amount.toFixed(4)} ETH</span>
            </div>
            <div className="flex justify-between">
              <span className="font-semibold">Timestamp:</span>
              <span>{new Date(selectedEdge.timestamp).toLocaleString()}</span>
            </div>
            <div className="rounded bg-gray-50 p-2">
              <span className="font-semibold">TX Hash:</span>
              <br />
              <span className="font-mono text-xs">{selectedEdge.txHash}</span>
            </div>
            {selectedEdge.riskIndicators.length > 0 && (
              <div>
                <span className="font-semibold">Risk Indicators:</span>
                <div className="mt-1 flex flex-wrap gap-1">
                  {selectedEdge.riskIndicators.map((indicator, idx) => (
                    <span key={idx} className="rounded bg-red-100 px-2 py-1 text-xs text-red-800">
                      {indicator.replace('_', ' ')}
                    </span>
                  ))}
                </div>
              </div>
            )}
            {selectedEdge.confidence !== undefined && (
              <div className="flex justify-between">
                <span className="font-semibold">Confidence:</span>
                <span>{(selectedEdge.confidence * 100).toFixed(0)}%</span>
              </div>
            )}
            {selectedEdge.isSuspicious && (
              <div className="rounded bg-red-100 p-2 text-red-800">
                <span className="font-bold">⚠️ SUSPICIOUS TRANSACTION</span>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Enhanced legend */}
      <div className="absolute bottom-4 right-4 z-10 rounded-lg bg-white p-4 shadow-md">
        <h4 className="mb-2 text-sm font-bold">Legend</h4>
        <div className="space-y-2 text-xs">
          <div className="font-semibold">Node Types:</div>
          <div className="flex items-center gap-2">
            <div className="h-4 w-4 rounded-full" style={{ backgroundColor: '#3b82f6' }} />
            <span>Wallet</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="h-4 w-4 rounded-full" style={{ backgroundColor: '#8b5cf6' }} />
            <span>Exchange</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="h-4 w-4 rounded-full" style={{ backgroundColor: '#dc2626' }} />
            <span>Mixer (Sanctioned)</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="h-4 w-4 rounded-full" style={{ backgroundColor: '#06b6d4' }} />
            <span>Contract</span>
          </div>
          
          <div className="mt-3 font-semibold">Risk Levels:</div>
          <div className="flex items-center gap-2">
            <div className="h-3 w-3 rounded" style={{ backgroundColor: '#dc2626' }} />
            <span>Critical</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="h-3 w-3 rounded" style={{ backgroundColor: '#ef4444' }} />
            <span>High</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="h-3 w-3 rounded" style={{ backgroundColor: '#f59e0b' }} />
            <span>Medium</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="h-3 w-3 rounded" style={{ backgroundColor: '#22c55e' }} />
            <span>Low</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdvancedGraphVisualization;

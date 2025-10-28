'use client';

import React, { useEffect, useRef, useState } from 'react';
import { useTranslation } from 'react-i18next';
import cytoscape, { Core, NodeSingular, EdgeSingular } from 'cytoscape';

interface GraphNode {
  id: string;
  address: string;
  nodeType: 'wallet' | 'exchange' | 'mixer' | 'contract' | 'unknown';
  label?: string;
  balance?: number;
  riskLevel: 'high' | 'medium' | 'low' | 'none';
  isSanctioned: boolean;
}

interface GraphEdge {
  id: string;
  source: string;
  target: string;
  amount: number;
  timestamp: string;
  txHash: string;
  isSuspicious: boolean;
}

interface GraphVisualizationProps {
  nodes: GraphNode[];
  edges: GraphEdge[];
  onNodeClick?: (node: GraphNode) => void;
  onEdgeClick?: (edge: GraphEdge) => void;
  height?: string;
  className?: string;
}

export const GraphVisualization: React.FC<GraphVisualizationProps> = ({
  nodes,
  edges,
  onNodeClick,
  onEdgeClick,
  height = '600px',
  className = '',
}) => {
  const { t } = useTranslation();
  const containerRef = useRef<HTMLDivElement>(null);
  const cyRef = useRef<Core | null>(null);
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
  const [selectedEdge, setSelectedEdge] = useState<GraphEdge | null>(null);
  const [layoutType, setLayoutType] = useState<'breadthfirst' | 'circle' | 'concentric'>('breadthfirst');

  // リスクレベルに応じた色
  const getRiskColor = (riskLevel: string): string => {
    switch (riskLevel) {
      case 'high':
        return '#ef4444'; // 赤
      case 'medium':
        return '#f59e0b'; // オレンジ
      case 'low':
        return '#22c55e'; // 緑
      default:
        return '#64748b'; // グレー
    }
  };

  // ノードタイプに応じた色
  const getNodeTypeColor = (nodeType: string): string => {
    switch (nodeType) {
      case 'wallet':
        return '#3b82f6'; // 青
      case 'exchange':
        return '#8b5cf6'; // 紫
      case 'mixer':
        return '#ef4444'; // 赤
      case 'contract':
        return '#06b6d4'; // シアン
      default:
        return '#94a3b8'; // グレー
    }
  };

  useEffect(() => {
    if (!containerRef.current || nodes.length === 0) return;

    // Cytoscapeインスタンスの初期化
    const cy = cytoscape({
      container: containerRef.current,
      elements: [
        // ノード
        ...nodes.map((node) => ({
          data: {
            id: node.id,
            label: node.label || node.address.substring(0, 10) + '...',
            ...node,
          },
        })),
        // エッジ
        ...edges.map((edge) => ({
          data: {
            id: edge.id,
            source: edge.source,
            target: edge.target,
            label: `${edge.amount} ETH`,
            ...edge,
          },
        })),
      ],
      style: [
        // ノードのスタイル
        {
          selector: 'node',
          style: {
            'background-color': function(ele: any) {
              const node = ele.data() as GraphNode;
              if (node.isSanctioned) return '#dc2626';
              return getNodeTypeColor(node.nodeType);
            },
            label: 'data(label)',
            'text-valign': 'center',
            'text-halign': 'center',
            color: '#ffffff',
            'text-outline-color': '#000000',
            'text-outline-width': 2,
            'font-size': '14px',
            'font-weight': 'bold',
            'text-wrap': 'wrap',
            'text-max-width': '80px',
            width: function(ele: any) {
              const node = ele.data() as GraphNode;
              const baseSize = 50;
              if (node.balance) {
                return Math.min(baseSize + node.balance * 3, 120);
              }
              return baseSize;
            },
            height: function(ele: any) {
              const node = ele.data() as GraphNode;
              const baseSize = 50;
              if (node.balance) {
                return Math.min(baseSize + node.balance * 3, 120);
              }
              return baseSize;
            },
            'border-width': function(ele: any) {
              const node = ele.data() as GraphNode;
              return node.riskLevel === 'high' ? 5 : 3;
            },
            'border-color': function(ele: any) {
              const node = ele.data() as GraphNode;
              return getRiskColor(node.riskLevel);
            },
          },
        },
        // エッジのスタイル
        {
          selector: 'edge',
          style: {
            width: function(ele: any) {
              const edge = ele.data() as GraphEdge;
              return Math.min(Math.max(edge.amount / 2, 2), 8);
            },
            'line-color': function(ele: any) {
              const edge = ele.data() as GraphEdge;
              return edge.isSuspicious ? '#ef4444' : '#94a3b8';
            },
            'target-arrow-color': function(ele: any) {
              const edge = ele.data() as GraphEdge;
              return edge.isSuspicious ? '#ef4444' : '#94a3b8';
            },
            'target-arrow-shape': 'triangle',
            'arrow-scale': 1.5,
            'curve-style': 'bezier',
            label: 'data(label)',
            'font-size': '11px',
            'font-weight': 'bold',
            color: '#1e293b',
            'text-background-color': '#ffffff',
            'text-background-opacity': 0.8,
            'text-background-padding': '3px',
            'text-rotation': 'autorotate',
            'text-margin-y': -10,
          },
        },
        // 選択時のスタイル
        {
          selector: ':selected',
          style: {
            'border-width': 4,
            'border-color': '#0ea5e9',
            'background-color': '#0ea5e9',
          },
        },
        // ホバー時のスタイル
        {
          selector: 'node:active',
          style: {
            'overlay-color': '#0ea5e9',
            'overlay-padding': 10,
            'overlay-opacity': 0.2,
          },
        },
      ],
      layout: {
        name: 'breadthfirst',
        directed: true,
        spacingFactor: 1.5,
        animate: true,
        animationDuration: 1000,
        avoidOverlap: true,
        nodeDimensionsIncludeLabels: true,
      },
      minZoom: 0.3,
      maxZoom: 3,
      wheelSensitivity: 0.2,
    });

    // イベントハンドラー
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

    // 背景クリックで選択解除
    cy.on('tap', (event) => {
      if (event.target === cy) {
        setSelectedNode(null);
        setSelectedEdge(null);
      }
    });

    // 右クリックメニュー（将来実装）
    cy.on('cxttap', 'node', (event) => {
      event.preventDefault();
      // TODO: コンテキストメニュー表示
    });

    cyRef.current = cy;

    // クリーンアップ
    return () => {
      cy.destroy();
    };
  }, [nodes, edges, onNodeClick, onEdgeClick]);

  // グラフ操作関数
  const fitGraph = () => {
    cyRef.current?.fit(undefined, 50);
  };

  const centerGraph = () => {
    cyRef.current?.center();
  };

  const resetZoom = () => {
    cyRef.current?.zoom(1);
    cyRef.current?.center();
  };

  const exportImage = () => {
    if (!cyRef.current) return;
    const png = cyRef.current.png({ scale: 2, full: true });
    const link = document.createElement('a');
    link.href = png;
    link.download = 'graph-export.png';
    link.click();
  };

  const changeLayout = (newLayout: 'breadthfirst' | 'circle' | 'concentric') => {
    if (!cyRef.current) return;
    setLayoutType(newLayout);
    
    const layoutOptions: any = {
      breadthfirst: {
        name: 'breadthfirst',
        directed: true,
        spacingFactor: 1.5,
        animate: true,
        animationDuration: 1000,
        avoidOverlap: true,
        nodeDimensionsIncludeLabels: true,
      },
      circle: {
        name: 'circle',
        animate: true,
        animationDuration: 1000,
        avoidOverlap: true,
        spacingFactor: 1.5,
      },
      concentric: {
        name: 'concentric',
        animate: true,
        animationDuration: 1000,
        avoidOverlap: true,
        spacingFactor: 1.5,
        concentric: function(node: any) {
          const n = node.data() as GraphNode;
          if (n.isSanctioned) return 100;
          if (n.riskLevel === 'high') return 80;
          if (n.riskLevel === 'medium') return 60;
          return 40;
        },
        levelWidth: function() {
          return 2;
        },
      },
    };

    cyRef.current.layout(layoutOptions[newLayout]).run();
  };

  return (
    <div className={`relative ${className}`}>
      {/* コントロールパネル */}
      <div className="absolute top-4 right-4 z-10 flex flex-col gap-2">
        {/* レイアウト選択 */}
        <div className="rounded-lg bg-white p-2 shadow-md">
          <div className="mb-1 text-xs font-semibold text-gray-600">{t('graph.controls.layout')}</div>
          <div className="flex flex-col gap-1">
            <button
              onClick={() => changeLayout('breadthfirst')}
              className={`rounded px-2 py-1 text-xs font-medium transition ${
                layoutType === 'breadthfirst'
                  ? 'bg-purple-500 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              {t('graph.controls.tree')}
            </button>
            <button
              onClick={() => changeLayout('circle')}
              className={`rounded px-2 py-1 text-xs font-medium transition ${
                layoutType === 'circle' 
                  ? 'bg-purple-500 text-white' 
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              {t('graph.controls.circle')}
            </button>
            <button
              onClick={() => changeLayout('concentric')}
              className={`rounded px-2 py-1 text-xs font-medium transition ${
                layoutType === 'concentric'
                  ? 'bg-purple-500 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              {t('graph.controls.risk')}
            </button>
          </div>
        </div>

        <button
          onClick={fitGraph}
          className="rounded-lg bg-white px-3 py-2 text-sm shadow-md hover:bg-gray-50"
          title={t('graph.controls.fit')}
        >
          <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4"
            />
          </svg>
        </button>

        <button
          onClick={centerGraph}
          className="rounded-lg bg-white px-3 py-2 text-sm shadow-md hover:bg-gray-50"
          title={t('graph.controls.center')}
        >
          <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 4v16m8-8H4"
            />
          </svg>
        </button>

        <button
          onClick={resetZoom}
          className="rounded-lg bg-white px-3 py-2 text-sm shadow-md hover:bg-gray-50"
          title={t('graph.controls.resetZoom')}
        >
          <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM13 10H7"
            />
          </svg>
        </button>

        <button
          onClick={exportImage}
          className="rounded-lg bg-white px-3 py-2 text-sm shadow-md hover:bg-gray-50"
          title={t('graph.controls.export')}
        >
          <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
            />
          </svg>
        </button>
      </div>

      {/* グラフコンテナ */}
      <div ref={containerRef} style={{ height, width: '100%' }} className="rounded-lg border" />

      {/* 選択ノード情報パネル */}
      {selectedNode && (
        <div className="absolute bottom-4 left-4 z-10 w-80 rounded-lg bg-white p-4 shadow-lg">
          <h3 className="mb-2 text-lg font-bold">{t('graph.nodeDetails')}</h3>
          <div className="space-y-1 text-sm">
            <p>
              <span className="font-semibold">{t('graph.fields.address')}:</span>{' '}
              <span className="font-mono">{selectedNode.address}</span>
            </p>
            <p>
              <span className="font-semibold">{t('graph.fields.type')}:</span>{' '}
              {selectedNode.nodeType}
            </p>
            {selectedNode.balance && (
              <p>
                <span className="font-semibold">{t('graph.fields.balance')}:</span>{' '}
                {selectedNode.balance} ETH
              </p>
            )}
            <p>
              <span className="font-semibold">{t('graph.fields.risk')}:</span>{' '}
              <span
                className="rounded px-2 py-1 text-xs font-bold text-white"
                style={{ backgroundColor: getRiskColor(selectedNode.riskLevel) }}
              >
                {selectedNode.riskLevel.toUpperCase()}
              </span>
            </p>
            {selectedNode.isSanctioned && (
              <p className="rounded bg-red-100 p-2 text-red-800">
                {t('graph.status.sanctioned')}
              </p>
            )}
          </div>
        </div>
      )}

      {/* 選択エッジ情報パネル */}
      {selectedEdge && (
        <div className="absolute bottom-4 left-4 z-10 w-80 rounded-lg bg-white p-4 shadow-lg">
          <h3 className="mb-2 text-lg font-bold">{t('graph.edgeDetails')}</h3>
          <div className="space-y-1 text-sm">
            <p>
              <span className="font-semibold">{t('graph.fields.amount')}:</span>{' '}
              {selectedEdge.amount} ETH
            </p>
            <p>
              <span className="font-semibold">{t('graph.fields.timestamp')}:</span>{' '}
              {new Date(selectedEdge.timestamp).toLocaleString()}
            </p>
            <p>
              <span className="font-semibold">{t('graph.fields.txHash')}:</span>{' '}
              <span className="font-mono text-xs">{selectedEdge.txHash}</span>
            </p>
            {selectedEdge.isSuspicious && (
              <p className="rounded bg-red-100 p-2 text-red-800">
                {t('graph.status.suspicious')}
              </p>
            )}
          </div>
        </div>
      )}

      {/* 凡例 */}
      <div className="absolute bottom-4 right-4 z-10 rounded-lg bg-white p-4 shadow-md">
        <h4 className="mb-2 text-sm font-bold">{t('graph.legend')}</h4>
        <div className="space-y-2 text-xs">
          <div className="flex items-center gap-2">
            <div className="h-4 w-4 rounded-full" style={{ backgroundColor: '#3b82f6' }} />
            <span>{t('graph.nodeTypes.wallet')}</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="h-4 w-4 rounded-full" style={{ backgroundColor: '#8b5cf6' }} />
            <span>{t('graph.nodeTypes.exchange')}</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="h-4 w-4 rounded-full" style={{ backgroundColor: '#ef4444' }} />
            <span>{t('graph.nodeTypes.mixer')}</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="h-4 w-4 rounded-full" style={{ backgroundColor: '#06b6d4' }} />
            <span>{t('graph.nodeTypes.contract')}</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default GraphVisualization;

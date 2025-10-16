'use client';

import React, { useEffect, useRef, useState } from 'react';
import cytoscape, { Core, NodeSingular, EdgeSingular } from 'cytoscape';
import { useTranslation } from 'react-i18next';

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
  const { t } = useTranslation('glossary');
  const containerRef = useRef<HTMLDivElement>(null);
  const cyRef = useRef<Core | null>(null);
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
  const [selectedEdge, setSelectedEdge] = useState<GraphEdge | null>(null);

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
            'background-color': (ele: NodeSingular) => {
              const node = ele.data() as GraphNode;
              if (node.isSanctioned) return '#dc2626'; // 制裁対象は濃い赤
              return getNodeTypeColor(node.nodeType);
            },
            label: 'data(label)',
            'text-valign': 'center',
            'text-halign': 'center',
            color: '#fff',
            'font-size': '12px',
            'font-weight': 'bold',
            width: (ele: NodeSingular) => {
              const node = ele.data() as GraphNode;
              // 残高に応じてサイズ変更
              const baseSize = 40;
              if (node.balance) {
                return Math.min(baseSize + node.balance * 2, 100);
              }
              return baseSize;
            },
            height: (ele: NodeSingular) => {
              const node = ele.data() as GraphNode;
              const baseSize = 40;
              if (node.balance) {
                return Math.min(baseSize + node.balance * 2, 100);
              }
              return baseSize;
            },
            'border-width': (ele: NodeSingular) => {
              const node = ele.data() as GraphNode;
              return node.riskLevel === 'high' ? 4 : 2;
            },
            'border-color': (ele: NodeSingular) => {
              const node = ele.data() as GraphNode;
              return getRiskColor(node.riskLevel);
            },
          },
        },
        // エッジのスタイル
        {
          selector: 'edge',
          style: {
            width: (ele: EdgeSingular) => {
              const edge = ele.data() as GraphEdge;
              // 金額に応じて太さ変更
              return Math.min(Math.max(edge.amount / 2, 1), 10);
            },
            'line-color': (ele: EdgeSingular) => {
              const edge = ele.data() as GraphEdge;
              return edge.isSuspicious ? '#ef4444' : '#cbd5e1';
            },
            'target-arrow-color': (ele: EdgeSingular) => {
              const edge = ele.data() as GraphEdge;
              return edge.isSuspicious ? '#ef4444' : '#cbd5e1';
            },
            'target-arrow-shape': 'triangle',
            'curve-style': 'bezier',
            label: 'data(label)',
            'font-size': '10px',
            color: '#475569',
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
        name: 'cose',
        animate: true,
        animationDuration: 500,
        nodeRepulsion: 8000,
        idealEdgeLength: 100,
        edgeElasticity: 100,
        nestingFactor: 5,
        gravity: 80,
        numIter: 1000,
        initialTemp: 200,
        coolingFactor: 0.95,
        minTemp: 1.0,
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

  return (
    <div className={`relative ${className}`}>
      {/* コントロールパネル */}
      <div className="absolute top-4 right-4 z-10 flex flex-col gap-2">
        <button
          onClick={fitGraph}
          className="rounded-lg bg-white px-3 py-2 text-sm shadow-md hover:bg-gray-50"
          title={t('graphVisualization.fitGraph', 'Fit Graph')}
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
          title={t('graphVisualization.center', 'Center')}
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
          title={t('graphVisualization.resetZoom', 'Reset Zoom')}
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
          title={t('graphVisualization.export', 'Export Image')}
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
          <h3 className="mb-2 text-lg font-bold">{t('graphVisualization.nodeDetails')}</h3>
          <div className="space-y-1 text-sm">
            <p>
              <span className="font-semibold">{t('blockchain.address')}:</span>{' '}
              <span className="font-mono">{selectedNode.address}</span>
            </p>
            <p>
              <span className="font-semibold">{t('graphVisualization.nodeType', 'Type')}:</span>{' '}
              {selectedNode.nodeType}
            </p>
            {selectedNode.balance && (
              <p>
                <span className="font-semibold">{t('blockchain.balance', 'Balance')}:</span>{' '}
                {selectedNode.balance} ETH
              </p>
            )}
            <p>
              <span className="font-semibold">{t('investigation.risk')}:</span>{' '}
              <span
                className="rounded px-2 py-1 text-xs font-bold text-white"
                style={{ backgroundColor: getRiskColor(selectedNode.riskLevel) }}
              >
                {selectedNode.riskLevel.toUpperCase()}
              </span>
            </p>
            {selectedNode.isSanctioned && (
              <p className="rounded bg-red-100 p-2 text-red-800">
                ⚠️ {t('riskAssessment.sanctioned')}
              </p>
            )}
          </div>
        </div>
      )}

      {/* 選択エッジ情報パネル */}
      {selectedEdge && (
        <div className="absolute bottom-4 left-4 z-10 w-80 rounded-lg bg-white p-4 shadow-lg">
          <h3 className="mb-2 text-lg font-bold">{t('graphVisualization.edgeDetails')}</h3>
          <div className="space-y-1 text-sm">
            <p>
              <span className="font-semibold">{t('blockchain.amount', 'Amount')}:</span>{' '}
              {selectedEdge.amount} ETH
            </p>
            <p>
              <span className="font-semibold">{t('blockchain.timestamp')}:</span>{' '}
              {new Date(selectedEdge.timestamp).toLocaleString()}
            </p>
            <p>
              <span className="font-semibold">{t('blockchain.txHash')}:</span>{' '}
              <span className="font-mono text-xs">{selectedEdge.txHash}</span>
            </p>
            {selectedEdge.isSuspicious && (
              <p className="rounded bg-red-100 p-2 text-red-800">
                ⚠️ {t('riskAssessment.suspicious')}
              </p>
            )}
          </div>
        </div>
      )}

      {/* 凡例 */}
      <div className="absolute bottom-4 right-4 z-10 rounded-lg bg-white p-4 shadow-md">
        <h4 className="mb-2 text-sm font-bold">{t('graphVisualization.legend', 'Legend')}</h4>
        <div className="space-y-2 text-xs">
          <div className="flex items-center gap-2">
            <div className="h-4 w-4 rounded-full" style={{ backgroundColor: '#3b82f6' }} />
            <span>{t('moneyLaundering.wallet', 'Wallet')}</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="h-4 w-4 rounded-full" style={{ backgroundColor: '#8b5cf6' }} />
            <span>{t('moneyLaundering.exchange', 'Exchange')}</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="h-4 w-4 rounded-full" style={{ backgroundColor: '#ef4444' }} />
            <span>{t('moneyLaundering.mixer', 'Mixer')}</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="h-4 w-4 rounded-full" style={{ backgroundColor: '#06b6d4' }} />
            <span>{t('blockchain.contract', 'Contract')}</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default GraphVisualization;

'use client';

import React from 'react';
import { useTranslation } from 'react-i18next';

interface ClusterStats {
  riskLevel: string;
  nodeCount: number;
  totalVolume: number;
  averageRiskScore: number;
  addresses: string[];
}

interface RiskClusterPanelProps {
  clusters: ClusterStats[];
  onClusterClick?: (cluster: ClusterStats) => void;
  className?: string;
}

export const RiskClusterPanel: React.FC<RiskClusterPanelProps> = ({
  clusters,
  onClusterClick,
  className = '',
}) => {
  const { t } = useTranslation('glossary');

  const getRiskColor = (riskLevel: string): string => {
    switch (riskLevel) {
      case 'critical':
        return 'bg-red-600 text-white';
      case 'high':
        return 'bg-red-500 text-white';
      case 'medium':
        return 'bg-orange-500 text-white';
      case 'low':
        return 'bg-green-500 text-white';
      case 'minimal':
        return 'bg-green-300 text-gray-900';
      default:
        return 'bg-gray-400 text-white';
    }
  };

  const getRiskIcon = (riskLevel: string): string => {
    switch (riskLevel) {
      case 'critical':
        return '🚨';
      case 'high':
        return '⚠️';
      case 'medium':
        return '⚡';
      case 'low':
        return '✓';
      case 'minimal':
        return '✅';
      default:
        return '○';
    }
  };

  return (
    <div className={`rounded-lg bg-white p-4 shadow-lg ${className}`}>
      <h3 className="mb-4 text-lg font-bold">
        {t('riskAssessment.clusters', 'Risk Clusters')}
      </h3>
      
      <div className="space-y-3">
        {clusters.map((cluster, index) => (
          <div
            key={index}
            onClick={() => onClusterClick && onClusterClick(cluster)}
            className="cursor-pointer rounded-lg border-2 border-gray-200 p-3 transition-all hover:border-blue-500 hover:shadow-md"
          >
            <div className="mb-2 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="text-2xl">{getRiskIcon(cluster.riskLevel)}</span>
                <span
                  className={`rounded px-3 py-1 text-sm font-bold uppercase ${getRiskColor(cluster.riskLevel)}`}
                >
                  {cluster.riskLevel}
                </span>
              </div>
              <span className="text-lg font-bold text-gray-700">{cluster.nodeCount} nodes</span>
            </div>
            
            <div className="grid grid-cols-2 gap-2 text-sm">
              <div>
                <span className="font-semibold text-gray-600">Total Volume:</span>
                <div className="font-bold text-gray-900">
                  {cluster.totalVolume.toFixed(2)} ETH
                </div>
              </div>
              <div>
                <span className="font-semibold text-gray-600">Avg Risk Score:</span>
                <div className="font-bold text-gray-900">
                  {cluster.averageRiskScore.toFixed(1)}/100
                </div>
              </div>
            </div>
            
            {cluster.addresses.length > 0 && (
              <div className="mt-2 border-t pt-2">
                <span className="text-xs font-semibold text-gray-600">Sample Addresses:</span>
                <div className="mt-1 flex flex-wrap gap-1">
                  {cluster.addresses.slice(0, 3).map((addr, idx) => (
                    <span key={idx} className="rounded bg-gray-100 px-2 py-1 font-mono text-xs text-gray-700">
                      {addr.substring(0, 6)}...{addr.substring(addr.length - 4)}
                    </span>
                  ))}
                  {cluster.addresses.length > 3 && (
                    <span className="rounded bg-gray-100 px-2 py-1 text-xs text-gray-500">
                      +{cluster.addresses.length - 3} more
                    </span>
                  )}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
      
      {clusters.length === 0 && (
        <div className="py-8 text-center text-gray-500">
          No risk clusters detected
        </div>
      )}
    </div>
  );
};

export default RiskClusterPanel;

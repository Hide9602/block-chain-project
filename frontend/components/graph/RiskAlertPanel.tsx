'use client';

import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';

interface RiskAlert {
  id: string;
  severity: 'critical' | 'high' | 'medium';
  address: string;
  title: string;
  description: string;
  timestamp: string;
  indicators: string[];
  riskScore: number;
  actionRequired: boolean;
}

interface RiskAlertPanelProps {
  alerts: RiskAlert[];
  onAlertClick?: (alert: RiskAlert) => void;
  onDismiss?: (alertId: string) => void;
  className?: string;
}

export const RiskAlertPanel: React.FC<RiskAlertPanelProps> = ({
  alerts,
  onAlertClick,
  onDismiss,
  className = '',
}) => {
  const { t } = useTranslation('glossary');
  const [filter, setFilter] = useState<'all' | 'critical' | 'high' | 'medium'>('all');
  const [sortBy, setSortBy] = useState<'time' | 'severity' | 'score'>('severity');
  const [expandedAlert, setExpandedAlert] = useState<string | null>(null);

  const getSeverityColor = (severity: string): string => {
    switch (severity) {
      case 'critical':
        return 'bg-red-600';
      case 'high':
        return 'bg-orange-500';
      case 'medium':
        return 'bg-yellow-500';
      default:
        return 'bg-gray-400';
    }
  };

  const getSeverityIcon = (severity: string): string => {
    switch (severity) {
      case 'critical':
        return '🚨';
      case 'high':
        return '⚠️';
      case 'medium':
        return '⚡';
      default:
        return '○';
    }
  };

  const getSeverityWeight = (severity: string): number => {
    switch (severity) {
      case 'critical':
        return 3;
      case 'high':
        return 2;
      case 'medium':
        return 1;
      default:
        return 0;
    }
  };

  // Filter alerts
  const filteredAlerts = alerts.filter(alert => {
    if (filter === 'all') return true;
    return alert.severity === filter;
  });

  // Sort alerts
  const sortedAlerts = [...filteredAlerts].sort((a, b) => {
    switch (sortBy) {
      case 'severity':
        return getSeverityWeight(b.severity) - getSeverityWeight(a.severity);
      case 'score':
        return b.riskScore - a.riskScore;
      case 'time':
        return new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime();
      default:
        return 0;
    }
  });

  // Count by severity
  const criticalCount = alerts.filter(a => a.severity === 'critical').length;
  const highCount = alerts.filter(a => a.severity === 'high').length;
  const mediumCount = alerts.filter(a => a.severity === 'medium').length;

  // Play alert sound for new critical alerts
  useEffect(() => {
    if (criticalCount > 0) {
      // In production, play an alert sound
      console.log('Critical alert detected');
    }
  }, [criticalCount]);

  return (
    <div className={`rounded-lg bg-white shadow-lg ${className}`}>
      {/* Header */}
      <div className="border-b border-gray-200 p-4">
        <div className="mb-3 flex items-center justify-between">
          <h3 className="text-lg font-bold">
            {t('riskAssessment.alerts', 'Risk Alerts')}
          </h3>
          <div className="flex gap-2">
            <span className="flex items-center gap-1 rounded-full bg-red-100 px-3 py-1 text-xs font-bold text-red-800">
              🚨 {criticalCount}
            </span>
            <span className="flex items-center gap-1 rounded-full bg-orange-100 px-3 py-1 text-xs font-bold text-orange-800">
              ⚠️ {highCount}
            </span>
            <span className="flex items-center gap-1 rounded-full bg-yellow-100 px-3 py-1 text-xs font-bold text-yellow-800">
              ⚡ {mediumCount}
            </span>
          </div>
        </div>

        {/* Filters and sorting */}
        <div className="flex gap-2">
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value as any)}
            className="flex-1 rounded border px-3 py-1 text-sm"
          >
            <option value="all">All Alerts</option>
            <option value="critical">Critical Only</option>
            <option value="high">High Only</option>
            <option value="medium">Medium Only</option>
          </select>
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value as any)}
            className="flex-1 rounded border px-3 py-1 text-sm"
          >
            <option value="severity">Sort by Severity</option>
            <option value="score">Sort by Risk Score</option>
            <option value="time">Sort by Time</option>
          </select>
        </div>
      </div>

      {/* Alert list */}
      <div className="max-h-96 overflow-y-auto p-4">
        {sortedAlerts.length === 0 ? (
          <div className="py-8 text-center text-gray-500">
            <div className="mb-2 text-4xl">✅</div>
            <p>No alerts matching filter criteria</p>
          </div>
        ) : (
          <div className="space-y-3">
            {sortedAlerts.map((alert) => (
              <div
                key={alert.id}
                className={`cursor-pointer rounded-lg border-2 transition-all ${
                  expandedAlert === alert.id
                    ? 'border-blue-500 shadow-md'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
                onClick={() => {
                  setExpandedAlert(expandedAlert === alert.id ? null : alert.id);
                  if (onAlertClick) onAlertClick(alert);
                }}
              >
                {/* Alert header */}
                <div className="flex items-start gap-3 p-3">
                  <div className="flex-shrink-0 text-2xl">
                    {getSeverityIcon(alert.severity)}
                  </div>
                  <div className="flex-1">
                    <div className="mb-1 flex items-start justify-between">
                      <div>
                        <span
                          className={`inline-block rounded px-2 py-1 text-xs font-bold uppercase text-white ${getSeverityColor(
                            alert.severity
                          )}`}
                        >
                          {alert.severity}
                        </span>
                        {alert.actionRequired && (
                          <span className="ml-2 inline-block rounded bg-purple-100 px-2 py-1 text-xs font-bold text-purple-800">
                            ACTION REQUIRED
                          </span>
                        )}
                      </div>
                      <div className="text-right text-xs text-gray-500">
                        {new Date(alert.timestamp).toLocaleString()}
                      </div>
                    </div>
                    <h4 className="mb-1 font-bold text-gray-900">{alert.title}</h4>
                    <p className="mb-2 text-sm text-gray-600">{alert.description}</p>
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-xs text-gray-700">
                        {alert.address.substring(0, 10)}...{alert.address.substring(alert.address.length - 8)}
                      </span>
                      <span className="text-xs font-bold text-gray-900">
                        Risk: {alert.riskScore.toFixed(1)}/100
                      </span>
                    </div>
                  </div>
                </div>

                {/* Expanded details */}
                {expandedAlert === alert.id && (
                  <div className="border-t border-gray-200 bg-gray-50 p-3">
                    <div className="mb-2">
                      <span className="text-xs font-semibold text-gray-700">Risk Indicators:</span>
                      <div className="mt-1 flex flex-wrap gap-1">
                        {alert.indicators.map((indicator, idx) => (
                          <span
                            key={idx}
                            className="rounded bg-red-100 px-2 py-1 text-xs text-red-800"
                          >
                            {indicator}
                          </span>
                        ))}
                      </div>
                    </div>
                    <div className="flex gap-2">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          if (onAlertClick) onAlertClick(alert);
                        }}
                        className="flex-1 rounded bg-blue-600 px-3 py-2 text-sm font-bold text-white hover:bg-blue-700"
                      >
                        Investigate
                      </button>
                      {onDismiss && (
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            onDismiss(alert.id);
                          }}
                          className="flex-1 rounded border border-gray-300 px-3 py-2 text-sm font-bold text-gray-700 hover:bg-gray-100"
                        >
                          Dismiss
                        </button>
                      )}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Footer actions */}
      {sortedAlerts.length > 0 && (
        <div className="border-t border-gray-200 p-4">
          <button className="w-full rounded bg-gray-100 px-4 py-2 text-sm font-bold text-gray-700 hover:bg-gray-200">
            Export All Alerts ({sortedAlerts.length})
          </button>
        </div>
      )}
    </div>
  );
};

export default RiskAlertPanel;

'use client';

import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Layout } from '@/components/layout/Layout';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { GraphVisualization } from '@/components/graph/GraphVisualization';

export default function DashboardPage() {
  const { t } = useTranslation(['common', 'glossary']);
  const [searchAddress, setSearchAddress] = useState('');
  const [isSearching, setIsSearching] = useState(false);

  // サンプルグラフデータ
  const sampleNodes = [
    {
      id: 'node-1',
      address: '0x1234567890abcdef1234567890abcdef12345678',
      nodeType: 'wallet' as const,
      balance: 10.5,
      riskLevel: 'low' as const,
      isSanctioned: false,
    },
    {
      id: 'node-2',
      address: '0xabcdef1234567890abcdef1234567890abcdef12',
      nodeType: 'exchange' as const,
      label: 'Binance',
      balance: 1000.0,
      riskLevel: 'none' as const,
      isSanctioned: false,
    },
    {
      id: 'node-3',
      address: '0x9876543210fedcba9876543210fedcba98765432',
      nodeType: 'mixer' as const,
      label: 'Tornado Cash',
      balance: 500.0,
      riskLevel: 'high' as const,
      isSanctioned: true,
    },
    {
      id: 'node-4',
      address: '0xfedcba9876543210fedcba9876543210fedcba98',
      nodeType: 'wallet' as const,
      balance: 5.2,
      riskLevel: 'medium' as const,
      isSanctioned: false,
    },
    {
      id: 'node-5',
      address: '0x5678901234abcdef5678901234abcdef56789012',
      nodeType: 'contract' as const,
      label: 'DeFi Protocol',
      balance: 2000.0,
      riskLevel: 'low' as const,
      isSanctioned: false,
    },
  ];

  const sampleEdges = [
    {
      id: 'edge-1',
      source: 'node-1',
      target: 'node-2',
      amount: 5.0,
      timestamp: '2024-01-15T12:34:56Z',
      txHash: '0x123abc456def789...',
      isSuspicious: false,
    },
    {
      id: 'edge-2',
      source: 'node-1',
      target: 'node-3',
      amount: 3.0,
      timestamp: '2024-01-16T08:20:30Z',
      txHash: '0x789def123abc456...',
      isSuspicious: true,
    },
    {
      id: 'edge-3',
      source: 'node-3',
      target: 'node-4',
      amount: 2.5,
      timestamp: '2024-01-17T14:15:00Z',
      txHash: '0xabc123def456789...',
      isSuspicious: true,
    },
    {
      id: 'edge-4',
      source: 'node-2',
      target: 'node-5',
      amount: 100.0,
      timestamp: '2024-01-18T10:00:00Z',
      txHash: '0xdef456abc123789...',
      isSuspicious: false,
    },
  ];

  const handleSearch = async () => {
    if (!searchAddress) return;
    
    setIsSearching(true);
    // TODO: 実際のAPI呼び出し
    setTimeout(() => {
      setIsSearching(false);
    }, 2000);
  };

  const handleNodeClick = (node: any) => {
    console.log('Node clicked:', node);
    // TODO: ノード詳細モーダル表示
  };

  const handleEdgeClick = (edge: any) => {
    console.log('Edge clicked:', edge);
    // TODO: トランザクション詳細モーダル表示
  };

  return (
    <Layout>
      <div className="space-y-6">
        {/* ページヘッダー */}
        <div>
          <h1 className="text-3xl font-bold text-gray-900">{t('nav.dashboard')}</h1>
          <p className="mt-2 text-gray-600">
            {t('dashboard.subtitle', 'ブロックチェーン分析ダッシュボード')}
          </p>
        </div>

        {/* 検索セクション */}
        <Card>
          <CardHeader>
            <CardTitle>{t('buttons.search')}</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex gap-4">
              <input
                type="text"
                value={searchAddress}
                onChange={(e) => setSearchAddress(e.target.value)}
                placeholder={t('dashboard.searchPlaceholder', 'ブロックチェーンアドレスを入力...')}
                className="flex-1 rounded-lg border px-4 py-2 focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
              <Button onClick={handleSearch} isLoading={isSearching}>
                {t('buttons.search')}
              </Button>
            </div>
            <div className="mt-4 flex gap-2">
              <select className="rounded-lg border px-4 py-2">
                <option value="ethereum">Ethereum</option>
                <option value="bitcoin">Bitcoin</option>
                <option value="polygon">Polygon</option>
                <option value="bsc">BSC</option>
              </select>
              <select className="rounded-lg border px-4 py-2">
                <option value="3">深度: 3 hops</option>
                <option value="5">深度: 5 hops</option>
                <option value="10">深度: 10 hops</option>
              </select>
            </div>
          </CardContent>
        </Card>

        {/* 統計サマリー */}
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
          <Card hover>
            <CardContent>
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">{t('statistics.total')} Addresses</p>
                  <p className="mt-2 text-3xl font-bold text-gray-900">1,234</p>
                  <p className="mt-1 text-sm text-green-600">+12.5% from last month</p>
                </div>
                <div className="rounded-full bg-primary-100 p-3">
                  <svg
                    className="h-8 w-8 text-primary-600"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"
                    />
                  </svg>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card hover>
            <CardContent>
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">{t('investigation.report')}s</p>
                  <p className="mt-2 text-3xl font-bold text-gray-900">87</p>
                  <p className="mt-1 text-sm text-green-600">+5 this week</p>
                </div>
                <div className="rounded-full bg-green-100 p-3">
                  <svg
                    className="h-8 w-8 text-green-600"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                    />
                  </svg>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card hover>
            <CardContent>
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">{t('riskAssessment.highRisk')}</p>
                  <p className="mt-2 text-3xl font-bold text-red-600">23</p>
                  <p className="mt-1 text-sm text-red-600">Requires attention</p>
                </div>
                <div className="rounded-full bg-red-100 p-3">
                  <svg
                    className="h-8 w-8 text-red-600"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                    />
                  </svg>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card hover>
            <CardContent>
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Total Volume</p>
                  <p className="mt-2 text-3xl font-bold text-gray-900">$2.5M</p>
                  <p className="mt-1 text-sm text-gray-600">Last 30 days</p>
                </div>
                <div className="rounded-full bg-yellow-100 p-3">
                  <svg
                    className="h-8 w-8 text-yellow-600"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                    />
                  </svg>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* グラフ可視化 */}
        <Card padding={false}>
          <div className="p-6">
            <CardHeader>
              <CardTitle>{t('glossary:graphVisualization.graph')}</CardTitle>
            </CardHeader>
          </div>
          <GraphVisualization
            nodes={sampleNodes}
            edges={sampleEdges}
            onNodeClick={handleNodeClick}
            onEdgeClick={handleEdgeClick}
            height="700px"
            className="p-6"
          />
        </Card>

        {/* 最近のアクティビティ */}
        <Card>
          <CardHeader>
            <CardTitle>{t('dashboard.recentActivity', '最近のアクティビティ')}</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {[
                {
                  type: 'analysis',
                  title: '新規分析完了',
                  description: '0x1234...5678 の分析が完了しました',
                  time: '5分前',
                  icon: '🔍',
                },
                {
                  type: 'report',
                  title: 'レポート生成',
                  description: 'CASE-2024-001 のPDFレポートが生成されました',
                  time: '1時間前',
                  icon: '📄',
                },
                {
                  type: 'alert',
                  title: '高リスク検出',
                  description: 'Tornado Cash との取引を検出',
                  time: '3時間前',
                  icon: '⚠️',
                },
              ].map((activity, index) => (
                <div key={index} className="flex items-start gap-4 rounded-lg border p-4">
                  <div className="text-2xl">{activity.icon}</div>
                  <div className="flex-1">
                    <h4 className="font-semibold text-gray-900">{activity.title}</h4>
                    <p className="text-sm text-gray-600">{activity.description}</p>
                    <p className="mt-1 text-xs text-gray-500">{activity.time}</p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </Layout>
  );
}

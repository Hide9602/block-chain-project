'use client';

import React, { useState, useEffect, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import { useTranslation } from 'react-i18next';
import Link from 'next/link';
import { GraphVisualization } from '@/components/graph/GraphVisualization';
import { LanguageSwitcher } from '@/components/LanguageSwitcher';

function InvestigationContent() {
  const searchParams = useSearchParams();
  const addressParam = searchParams.get('address');
  const { t } = useTranslation();
  
  const [address, setAddress] = useState(addressParam || '');
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'graph' | 'patterns' | 'risk' | 'narrative'>('graph');

  useEffect(() => {
    if (addressParam) {
      handleInvestigate(addressParam);
    }
  }, [addressParam]);

  const handleInvestigate = async (targetAddress: string) => {
    if (!targetAddress.trim()) {
      setError('Please enter a valid address');
      return;
    }

    setLoading(true);
    setError(null);
    setData(null);

    try {
      // Call backend API
      const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      
      // Fetch graph data
      const graphResponse = await fetch(`${API_BASE}/api/v1/graph/address/${targetAddress}?depth=3`);
      
      if (!graphResponse.ok) {
        throw new Error(`API Error: ${graphResponse.status}`);
      }

      const graphData = await graphResponse.json();

      // Fetch ML analysis
      const currentLanguage = typeof window !== 'undefined' 
        ? localStorage.getItem('i18nextLng') || 'en' 
        : 'en';
      
      const analysisResponse = await fetch(`${API_BASE}/api/v1/ml/analyze`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          address: targetAddress,
          depth: 3,
          include_patterns: true,
          include_anomalies: true,
          include_risk_score: true,
          include_narrative: true,
          language: currentLanguage,
        }),
      });

      const analysisData = analysisResponse.ok ? await analysisResponse.json() : null;

      setData({
        graph: graphData,
        analysis: analysisData,
      });
    } catch (err: any) {
      console.error('Investigation error:', err);
      const errorMessage = err.message || 'Failed to fetch data. Please check your connection and try again.';
      setError(errorMessage);
      
      // Show user-friendly error based on error type
      if (err.message?.includes('Failed to fetch')) {
        setError(t('errors.fetchFailed'));
      } else if (err.message?.includes('404')) {
        setError(t('errors.notFound'));
      } else if (err.message?.includes('400')) {
        setError(t('errors.invalidAddress'));
      } else if (err.message?.includes('500')) {
        setError(t('errors.serverError'));
      } else {
        setError(t('errors.generic'));
      }
    } finally {
      setLoading(false);
    }
  };

  const handleNodeClick = (node: any) => {
    console.log('Node clicked:', node);
    // Could open a modal with node details
  };

  const handleEdgeClick = (edge: any) => {
    console.log('Edge clicked:', edge);
    // Could open a modal with transaction details
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Navigation */}
      <nav className="border-b border-white/10 bg-black/20 backdrop-blur-lg">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="flex h-16 items-center justify-between">
            <Link href="/" className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-to-br from-purple-500 to-pink-500">
                <svg className="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </div>
              <span className="text-xl font-bold text-white">MetaSleuth NextGen</span>
            </Link>
            <div className="flex items-center gap-4">
              <LanguageSwitcher />
              <Link href="/dashboard" className="rounded-lg px-4 py-2 text-sm font-medium text-white/80 transition hover:bg-white/10 hover:text-white">
                Dashboard
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        {/* Search Bar */}
        <div className="rounded-2xl border border-white/10 bg-white/5 p-6 backdrop-blur-lg">
          <div className="flex flex-col gap-4 sm:flex-row">
            <input
              type="text"
              value={address}
              onChange={(e) => setAddress(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleInvestigate(address)}
              placeholder={t('search.placeholder')}
              className="flex-1 rounded-lg bg-white/90 px-6 py-3 text-gray-900 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500"
            />
            <button
              onClick={() => handleInvestigate(address)}
              disabled={loading}
              className="rounded-lg bg-gradient-to-r from-purple-600 to-pink-600 px-8 py-3 font-semibold text-white transition hover:from-purple-700 hover:to-pink-700 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {loading ? (
                <span className="flex items-center gap-2">
                  <svg className="h-5 w-5 animate-spin" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  {t('loading')}
                </span>
              ) : (
                t('search.button')
              )}
            </button>
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="mt-6 rounded-lg border border-red-500/50 bg-red-500/10 p-4 text-red-300">
            <div className="flex items-center gap-2">
              <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              {error}
            </div>
          </div>
        )}

        {/* Results */}
        {data && (
          <div className="mt-6 space-y-6">
            {/* Tabs */}
            <div className="flex gap-2 overflow-x-auto rounded-xl border border-white/10 bg-white/5 p-2 backdrop-blur-lg">
              {[
                { id: 'graph', label: t('tabs.graph'), icon: '🕸️' },
                { id: 'patterns', label: t('tabs.patterns'), icon: '🔍' },
                { id: 'risk', label: t('tabs.risk'), icon: '⚠️' },
                { id: 'narrative', label: t('tabs.narrative'), icon: '📄' },
              ].map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as any)}
                  className={`flex-1 whitespace-nowrap rounded-lg px-4 py-3 text-sm font-medium transition ${
                    activeTab === tab.id
                      ? 'bg-gradient-to-r from-purple-600 to-pink-600 text-white'
                      : 'text-white/60 hover:bg-white/10 hover:text-white'
                  }`}
                >
                  <span className="mr-2">{tab.icon}</span>
                  {tab.label}
                </button>
              ))}
            </div>

            {/* Tab Content */}
            <div className="rounded-2xl border border-white/10 bg-white/5 backdrop-blur-lg">
              {activeTab === 'graph' && (
                <div className="p-6">
                  <h2 className="mb-4 text-2xl font-bold text-white">{t('graph.title')}</h2>
                  {data.graph?.nodes && data.graph?.edges && data.graph.nodes.length > 0 ? (
                    <div className="rounded-lg bg-white/10 p-4">
                      <div className="mb-3 text-sm text-white/70">
                        {t('graph.stats', { nodes: data.graph.nodes.length, edges: data.graph.edges.length })}
                      </div>
                      <GraphVisualization
                        nodes={data.graph.nodes}
                        edges={data.graph.edges}
                        onNodeClick={handleNodeClick}
                        onEdgeClick={handleEdgeClick}
                        height="600px"
                      />
                    </div>
                  ) : (
                    <div className="rounded-lg bg-white/10 p-12 text-center">
                      <div className="text-4xl mb-4">📊</div>
                      <div className="text-white/60 text-lg mb-2">{t('graph.empty.title')}</div>
                      <div className="text-white/40 text-sm">{t('graph.empty.description')}</div>
                    </div>
                  )}
                </div>
              )}

              {activeTab === 'patterns' && (
                <div className="p-6">
                  <h2 className="mb-4 text-2xl font-bold text-white">{t('patterns.title')}</h2>
                  {data.analysis?.patterns?.length > 0 ? (
                    <div className="space-y-4">
                      {data.analysis.patterns.map((pattern: any, index: number) => (
                        <div key={index} className="rounded-lg border border-white/10 bg-white/5 p-6">
                          <div className="flex items-start justify-between">
                            <div className="flex-1">
                              <h3 className="text-lg font-semibold text-white">
                                {t(`patterns.types.${pattern.pattern_type || pattern.type}`, { defaultValue: pattern.pattern_type || pattern.type })}
                              </h3>
                              <p className="mt-2 text-gray-300">{pattern.description}</p>
                              {pattern.evidence && (
                                <div className="mt-4">
                                  <p className="text-sm font-medium text-white/80">{t('patterns.evidence')}:</p>
                                  <ul className="mt-2 space-y-1 text-sm text-gray-400">
                                    {pattern.evidence.map((item: string, i: number) => (
                                      <li key={i}>• {item}</li>
                                    ))}
                                  </ul>
                                </div>
                              )}
                            </div>
                            <div className="ml-4 flex flex-col items-end gap-2">
                              <span className={`rounded-full px-3 py-1 text-sm font-medium ${
                                pattern.confidence > 0.8 ? 'bg-red-500/20 text-red-300' :
                                pattern.confidence > 0.5 ? 'bg-yellow-500/20 text-yellow-300' :
                                'bg-green-500/20 text-green-300'
                              }`}>
                                {t('patterns.confidence', { value: Math.round(pattern.confidence * 100) })}
                              </span>
                              {pattern.severity && (
                                <span className="text-sm text-white/60">{t('patterns.severity', { level: pattern.severity })}</span>
                              )}
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="rounded-lg bg-white/10 p-12 text-center">
                      <div className="text-4xl mb-4">🔍</div>
                      <div className="text-white/60 text-lg">{t('patterns.empty')}</div>
                    </div>
                  )}
                </div>
              )}

              {activeTab === 'risk' && (
                <div className="p-6">
                  <h2 className="mb-4 text-2xl font-bold text-white">{t('risk.title')}</h2>
                  {data.analysis?.risk_assessment ? (
                    <div className="space-y-6">
                      {/* Risk Score */}
                      <div className="rounded-lg border border-white/10 bg-white/5 p-6">
                        <div className="text-center">
                          <div className="text-6xl font-bold text-white">
                            {data.analysis.risk_assessment.overall_score || 0}
                          </div>
                          <div className="mt-2 text-lg text-gray-400">{t('risk.overallScore')}</div>
                          <div className={`mt-4 inline-block rounded-full px-4 py-2 text-sm font-medium ${
                            (data.analysis.risk_assessment.overall_score || 0) > 70 ? 'bg-red-500/20 text-red-300' :
                            (data.analysis.risk_assessment.overall_score || 0) > 40 ? 'bg-yellow-500/20 text-yellow-300' :
                            'bg-green-500/20 text-green-300'
                          }`}>
                            {t(`risk.levels.${data.analysis.risk_assessment.risk_level}`, { defaultValue: data.analysis.risk_assessment.risk_level || 'Unknown' })}
                          </div>
                        </div>
                      </div>

                      {/* Contributing Factors */}
                      {data.analysis.risk_assessment.factors && (
                        <div className="rounded-lg border border-white/10 bg-white/5 p-6">
                          <h3 className="mb-4 text-lg font-semibold text-white">{t('risk.contributingFactors')}</h3>
                          <div className="space-y-3">
                            {data.analysis.risk_assessment.factors.map((factor: any, index: number) => (
                              <div key={index} className="flex items-center justify-between">
                                <span className="text-gray-300">{factor.name || factor}</span>
                                <span className="text-white">
                                  {t(`risk.levels.${factor.impact || factor.score}`, { defaultValue: factor.impact || factor.score })}
                                </span>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  ) : (
                    <div className="rounded-lg bg-white/10 p-12 text-center">
                      <div className="text-4xl mb-4">⚠️</div>
                      <div className="text-white/60 text-lg">{t('risk.empty')}</div>
                    </div>
                  )}
                </div>
              )}

              {activeTab === 'narrative' && (
                <div className="p-6">
                  <h2 className="mb-4 text-2xl font-bold text-white">{t('narrative.title')}</h2>
                  {data.analysis?.narrative ? (
                    <div className="space-y-4">
                      <div className="rounded-lg border border-white/10 bg-white/5 p-6">
                        <div className="prose prose-invert max-w-none">
                          <div className="whitespace-pre-wrap text-gray-300">
                            {typeof data.analysis.narrative === 'string' 
                              ? data.analysis.narrative 
                              : data.analysis.narrative.summary || JSON.stringify(data.analysis.narrative, null, 2)}
                          </div>
                        </div>
                      </div>
                      
                      {/* Export Button */}
                      <button className="rounded-lg bg-gradient-to-r from-purple-600 to-pink-600 px-6 py-3 font-semibold text-white transition hover:from-purple-700 hover:to-pink-700">
                        {t('narrative.exportPdf')}
                      </button>
                    </div>
                  ) : (
                    <div className="rounded-lg bg-white/10 p-12 text-center">
                      <div className="text-4xl mb-4">📄</div>
                      <div className="text-white/60 text-lg">{t('narrative.empty')}</div>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        )}

        {/* Empty State */}
        {!loading && !data && !error && (
          <div className="mt-12 text-center">
            <div className="inline-flex h-24 w-24 items-center justify-center rounded-full bg-white/5">
              <svg className="h-12 w-12 text-white/40" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
            <h3 className="mt-6 text-xl font-semibold text-white">{t('investigation.ready')}</h3>
            <p className="mt-2 text-gray-400">{t('investigation.enterAddress')}</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default function InvestigationPage() {
  return (
    <Suspense fallback={
      <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
        <div className="text-white">Loading...</div>
      </div>
    }>
      <InvestigationContent />
    </Suspense>
  );
}

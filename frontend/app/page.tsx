'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useTranslation } from 'react-i18next';
import Link from 'next/link';
import { LanguageSwitcher } from '@/components/LanguageSwitcher';

export default function HomePage() {
  const router = useRouter();
  const { t } = useTranslation();
  const [address, setAddress] = useState('');

  const handleInvestigate = () => {
    if (address.trim()) {
      router.push(`/investigation?address=${encodeURIComponent(address)}`);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleInvestigate();
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Navigation */}
      <nav className="border-b border-white/10 bg-black/20 backdrop-blur-lg">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="flex h-16 items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-to-br from-purple-500 to-pink-500">
                <svg className="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </div>
              <span className="text-xl font-bold text-white">MetaSleuth NextGen</span>
            </div>
            <div className="flex items-center gap-4">
              <LanguageSwitcher />
              <Link href="/dashboard" className="rounded-lg px-4 py-2 text-sm font-medium text-white/80 transition hover:bg-white/10 hover:text-white">
                Dashboard
              </Link>
              <Link href="/login" className="rounded-lg bg-purple-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-purple-700">
                Login
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <div className="mx-auto max-w-7xl px-4 pt-20 sm:px-6 lg:px-8">
        <div className="text-center">
          <h1 className="text-5xl font-extrabold tracking-tight text-white sm:text-6xl lg:text-7xl">
            {t('hero.title')}
            <span className="block bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
              {t('hero.subtitle')}
            </span>
          </h1>
          <p className="mx-auto mt-6 max-w-2xl text-xl text-gray-300">
            {t('hero.description')}
          </p>

          {/* Search Bar */}
          <div className="mx-auto mt-12 max-w-3xl">
            <div className="rounded-2xl bg-white/10 p-2 backdrop-blur-lg">
              <div className="flex flex-col gap-2 sm:flex-row">
                <input
                  type="text"
                  value={address}
                  onChange={(e) => setAddress(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder={t('search.placeholder')}
                  className="flex-1 rounded-lg bg-white/90 px-6 py-4 text-gray-900 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500"
                />
                <button
                  onClick={handleInvestigate}
                  className="rounded-lg bg-gradient-to-r from-purple-600 to-pink-600 px-8 py-4 font-semibold text-white transition hover:from-purple-700 hover:to-pink-700 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-offset-2"
                >
                  {t('search.button')}
                </button>
              </div>
            </div>
            <p className="mt-3 text-sm text-gray-400">
              Try: 0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb
            </p>
          </div>
        </div>

        {/* Features Grid */}
        <div className="mt-24 grid gap-8 sm:grid-cols-2 lg:grid-cols-4">
          {[
            {
              icon: (
                <svg className="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
              ),
              title: t('features.patternDetection.title'),
              description: t('features.patternDetection.description'),
              color: 'from-purple-500 to-purple-600',
            },
            {
              icon: (
                <svg className="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                </svg>
              ),
              title: t('features.riskAssessment.title'),
              description: t('features.riskAssessment.description'),
              color: 'from-pink-500 to-pink-600',
            },
            {
              icon: (
                <svg className="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              ),
              title: t('features.graphAnalysis.title'),
              description: t('features.graphAnalysis.description'),
              color: 'from-blue-500 to-blue-600',
            },
            {
              icon: (
                <svg className="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              ),
              title: t('features.aiReports.title'),
              description: t('features.aiReports.description'),
              color: 'from-green-500 to-green-600',
            },
          ].map((feature, index) => (
            <div
              key={index}
              className="group rounded-2xl border border-white/10 bg-white/5 p-6 backdrop-blur-lg transition hover:border-white/20 hover:bg-white/10"
            >
              <div className={`inline-flex rounded-lg bg-gradient-to-br ${feature.color} p-3 text-white`}>
                {feature.icon}
              </div>
              <h3 className="mt-4 text-lg font-semibold text-white">{feature.title}</h3>
              <p className="mt-2 text-sm text-gray-400">{feature.description}</p>
            </div>
          ))}
        </div>

        {/* Stats Section */}
        <div className="mt-24 rounded-2xl border border-white/10 bg-white/5 p-12 backdrop-blur-lg">
          <div className="grid gap-8 text-center sm:grid-cols-3">
            <div>
              <div className="text-4xl font-bold text-white">1,234+</div>
              <div className="mt-2 text-gray-400">Addresses Analyzed</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-white">87</div>
              <div className="mt-2 text-gray-400">Investigation Reports</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-white">99.7%</div>
              <div className="mt-2 text-gray-400">Detection Accuracy</div>
            </div>
          </div>
        </div>

        {/* CTA Section */}
        <div className="mt-24 pb-24 text-center">
          <h2 className="text-3xl font-bold text-white">Ready to start investigating?</h2>
          <p className="mt-4 text-gray-400">Join leading law enforcement and compliance teams worldwide</p>
          <div className="mt-8 flex justify-center gap-4">
            <Link
              href="/dashboard"
              className="rounded-lg bg-gradient-to-r from-purple-600 to-pink-600 px-8 py-4 font-semibold text-white transition hover:from-purple-700 hover:to-pink-700"
            >
              Go to Dashboard
            </Link>
            <Link
              href="/login"
              className="rounded-lg border border-white/20 px-8 py-4 font-semibold text-white backdrop-blur-lg transition hover:bg-white/10"
            >
              Sign In
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}

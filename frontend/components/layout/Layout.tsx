'use client';

import React from 'react';
import { Header } from './Header';
import { useTranslation } from 'react-i18next';

interface LayoutProps {
  children: React.ReactNode;
}

export const Layout: React.FC<LayoutProps> = ({ children }) => {
  const { t } = useTranslation('common');
  const currentYear = new Date().getFullYear();

  return (
    <div className="flex min-h-screen flex-col bg-gray-50">
      {/* ヘッダー */}
      <Header />

      {/* メインコンテンツ */}
      <main className="flex-1">
        <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">{children}</div>
      </main>

      {/* フッター */}
      <footer className="border-t bg-white">
        <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
          <div className="flex flex-col items-center justify-between gap-4 md:flex-row">
            <div className="text-sm text-gray-500">
              {t('footer.copyright', { year: currentYear })}
            </div>
            <div className="flex gap-6 text-sm">
              <a href="/privacy" className="text-gray-600 hover:text-gray-900">
                {t('footer.privacyPolicy')}
              </a>
              <a href="/terms" className="text-gray-600 hover:text-gray-900">
                {t('footer.termsOfService')}
              </a>
              <a href="/contact" className="text-gray-600 hover:text-gray-900">
                {t('footer.contact')}
              </a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Layout;

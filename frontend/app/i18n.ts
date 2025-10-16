import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

// 翻訳ファイルのインポート
import commonEn from '@/locales/en/common.json';
import commonJa from '@/locales/ja/common.json';
import glossaryEn from '@/locales/en/glossary.json';
import glossaryJa from '@/locales/ja/glossary.json';

const resources = {
  en: {
    common: commonEn,
    glossary: glossaryEn,
  },
  ja: {
    common: commonJa,
    glossary: glossaryJa,
  },
};

i18n
  .use(LanguageDetector) // ブラウザ言語検出
  .use(initReactI18next) // React統合
  .init({
    resources,
    defaultNS: 'common',
    ns: ['common', 'glossary'],
    fallbackLng: 'ja',
    debug: process.env.NODE_ENV === 'development',
    interpolation: {
      escapeValue: false, // Reactは既にエスケープしている
    },
    detection: {
      order: ['localStorage', 'navigator', 'htmlTag'],
      caches: ['localStorage'],
    },
  });

export default i18n;

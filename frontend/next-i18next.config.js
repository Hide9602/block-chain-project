module.exports = {
  i18n: {
    defaultLocale: 'ja',
    locales: ['en', 'ja'],
    localeDetection: true,
  },
  localePath: typeof window === 'undefined' ? require('path').resolve('./public/locales') : '/locales',
  reloadOnPrerender: process.env.NODE_ENV === 'development',
  
  // 翻訳キーがない場合の動作
  returnNull: false,
  returnEmptyString: false,
  
  // 名前空間設定
  ns: ['common', 'dashboard', 'analysis', 'reports', 'glossary'],
  defaultNS: 'common',
  
  // デバッグモード（開発時のみ）
  debug: process.env.NODE_ENV === 'development',
  
  // 翻訳の補間設定
  interpolation: {
    escapeValue: false,
  },
  
  // ブラウザ言語検出
  detection: {
    order: ['querystring', 'cookie', 'localStorage', 'navigator', 'htmlTag'],
    caches: ['cookie', 'localStorage'],
    lookupQuerystring: 'lang',
    lookupCookie: 'i18next',
    lookupLocalStorage: 'i18nextLng',
  },
};

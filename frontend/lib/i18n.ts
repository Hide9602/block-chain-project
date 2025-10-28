import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

// Translation resources
const resources = {
  en: {
    translation: {
      // Navigation
      home: 'Home',
      
      // Homepage
      hero: {
        title: 'MetaSleuth NextGen',
        subtitle: 'AI-Powered Blockchain Investigation Platform',
        description: 'Advanced transaction tracing, pattern recognition, and risk assessment for blockchain forensics',
        cta: 'Start Investigation',
      },
      
      search: {
        placeholder: 'Enter blockchain address (e.g., 0x1234...)',
        button: 'Investigate',
        label: 'Quick Investigation',
      },
      
      features: {
        title: 'Powerful Features',
        patternDetection: {
          title: 'Pattern Detection',
          description: 'Identify money laundering, Ponzi schemes, and 8+ fraud patterns automatically',
        },
        riskAssessment: {
          title: 'Risk Assessment',
          description: 'Real-time risk scoring from 0-100 with detailed contributing factors',
        },
        graphAnalysis: {
          title: 'Graph Analysis',
          description: 'Interactive 3D visualization of transaction networks and relationships',
        },
        aiReports: {
          title: 'AI Reports',
          description: 'Automated narrative generation with evidence-based investigation reports',
        },
      },
      
      // Investigation Page
      tabs: {
        graph: 'Transaction Graph',
        patterns: 'Pattern Detection',
        risk: 'Risk Assessment',
        narrative: 'AI Report',
      },
      
      // Graph Visualization
      graph: {
        title: 'Transaction Network',
        nodeDetails: 'Node Details',
        edgeDetails: 'Transaction Details',
        legend: 'Legend',
        controls: {
          layout: 'Layout',
          tree: 'Tree',
          circle: 'Circle',
          risk: 'Risk',
          fit: 'Fit Graph',
          center: 'Center',
          resetZoom: 'Reset Zoom',
          export: 'Export Image',
        },
        nodeTypes: {
          wallet: 'Wallet',
          exchange: 'Exchange',
          mixer: 'Mixer',
          contract: 'Contract',
        },
        fields: {
          address: 'Address',
          type: 'Type',
          balance: 'Balance',
          risk: 'Risk',
          amount: 'Amount',
          timestamp: 'Timestamp',
          txHash: 'Transaction Hash',
        },
        status: {
          sanctioned: '⚠️ Sanctioned',
          suspicious: '⚠️ Suspicious',
        },
        empty: {
          title: 'No graph data available',
          description: 'This address has no transactions to visualize',
        },
        stats: '{{nodes}} nodes, {{edges}} transactions',
      },
      
      // Patterns
      patterns: {
        title: 'Detected Patterns',
        confidence: '{{value}}% confidence',
        severity: 'Severity: {{level}}',
        empty: 'No suspicious patterns detected',
        addresses: 'Addresses Involved',
        evidence: 'Evidence',
        types: {
          'Wash Trading': 'Wash Trading',
          'Ponzi Scheme': 'Ponzi Scheme',
          'Money Laundering': 'Money Laundering',
          'Mixer Usage': 'Mixer Usage',
          'Rapid Movement': 'Rapid Movement',
          'Layering': 'Layering',
          'Structuring': 'Structuring',
        },
      },
      
      // Risk Assessment
      risk: {
        title: 'Risk Assessment',
        overallScore: 'Overall Risk Score',
        level: 'Risk Level',
        factors: 'Risk Factors',
        contributingFactors: 'Contributing Factors',
        recommendations: 'Recommendations',
        empty: 'No risk data available',
        levels: {
          'High Risk': 'High Risk',
          'Medium Risk': 'Medium Risk',
          'Low Risk': 'Low Risk',
          'High': 'High',
          'Medium': 'Medium',
          'Low': 'Low',
        },
      },
      
      // Narrative
      narrative: {
        title: 'AI-Generated Investigation Report',
        summary: 'Summary',
        timeline: 'Timeline',
        entities: 'Key Entities',
        findings: 'Findings',
        empty: 'No narrative available',
        exportPdf: 'Export as PDF',
      },
      
      // Investigation
      investigation: {
        ready: 'Ready to investigate',
        enterAddress: 'Enter a blockchain address above to start your analysis',
      },
      
      // States
      loading: 'Loading...',
      error: 'Error',
      noData: 'No data available',
      
      // Errors
      errors: {
        fetchFailed: 'Cannot connect to API server. Please check if the backend is running.',
        notFound: 'Address not found. Please verify the address and try again.',
        invalidAddress: 'Invalid address format. Please enter a valid blockchain address.',
        serverError: 'Server error. Please try again later.',
        generic: 'Failed to fetch data. Please check your connection and try again.',
      },
    },
  },
  ja: {
    translation: {
      // ナビゲーション
      home: 'ホーム',
      
      // ホームページ
      hero: {
        title: 'メタスルース ネクストジェン',
        subtitle: 'AI搭載ブロックチェーン調査プラットフォーム',
        description: '高度なトランザクション追跡、パターン認識、ブロックチェーンフォレンジックのためのリスク評価',
        cta: '調査を開始',
      },
      
      search: {
        placeholder: 'ブロックチェーンアドレスを入力 (例: 0x1234...)',
        button: '調査',
        label: 'クイック調査',
      },
      
      features: {
        title: '強力な機能',
        patternDetection: {
          title: 'パターン認識',
          description: 'マネーロンダリング、ポンジスキーム、その他8種類以上の詐欺パターンを自動識別',
        },
        riskAssessment: {
          title: 'リスク評価',
          description: '0-100のリアルタイムリスクスコアリングと詳細な寄与要因分析',
        },
        graphAnalysis: {
          title: 'グラフ分析',
          description: 'トランザクションネットワークと関係性のインタラクティブな3D可視化',
        },
        aiReports: {
          title: 'AIレポート',
          description: '証拠に基づく調査レポートの自動ナラティブ生成',
        },
      },
      
      // 調査ページ
      tabs: {
        graph: 'トランザクショングラフ',
        patterns: 'パターン検出',
        risk: 'リスク評価',
        narrative: 'AIレポート',
      },
      
      // グラフ可視化
      graph: {
        title: 'トランザクションネットワーク',
        nodeDetails: 'ノード詳細',
        edgeDetails: 'トランザクション詳細',
        legend: '凡例',
        controls: {
          layout: 'レイアウト',
          tree: 'ツリー',
          circle: '円形',
          risk: 'リスク',
          fit: 'フィット',
          center: '中央',
          resetZoom: 'ズームリセット',
          export: '画像エクスポート',
        },
        nodeTypes: {
          wallet: 'ウォレット',
          exchange: '取引所',
          mixer: 'ミキサー',
          contract: 'コントラクト',
        },
        fields: {
          address: 'アドレス',
          type: 'タイプ',
          balance: '残高',
          risk: 'リスク',
          amount: '金額',
          timestamp: 'タイムスタンプ',
          txHash: 'トランザクションハッシュ',
        },
        status: {
          sanctioned: '⚠️ 制裁対象',
          suspicious: '⚠️ 疑わしい',
        },
        empty: {
          title: 'グラフデータがありません',
          description: 'このアドレスには可視化するトランザクションがありません',
        },
        stats: '{{nodes}}ノード、{{edges}}トランザクション',
      },
      
      // パターン
      patterns: {
        title: '検出されたパターン',
        confidence: '信頼度 {{value}}%',
        severity: '深刻度: {{level}}',
        empty: '疑わしいパターンは検出されませんでした',
        addresses: '関連アドレス',
        evidence: '証拠',
        types: {
          'Wash Trading': 'ウォッシュトレーディング',
          'Ponzi Scheme': 'ポンジスキーム',
          'Money Laundering': 'マネーロンダリング',
          'Mixer Usage': 'ミキサー使用',
          'Rapid Movement': '高速移動',
          'Layering': 'レイヤリング',
          'Structuring': 'ストラクチャリング',
        },
      },
      
      // リスク評価
      risk: {
        title: 'リスク評価',
        overallScore: '総合リスクスコア',
        level: 'リスクレベル',
        factors: 'リスク要因',
        contributingFactors: '寄与要因',
        recommendations: '推奨事項',
        empty: 'リスクデータがありません',
        levels: {
          'High Risk': '高リスク',
          'Medium Risk': '中リスク',
          'Low Risk': '低リスク',
          'High': '高',
          'Medium': '中',
          'Low': '低',
        },
      },
      
      // ナラティブ
      narrative: {
        title: 'AI生成調査レポート',
        summary: '概要',
        timeline: 'タイムライン',
        entities: '主要エンティティ',
        findings: '調査結果',
        empty: 'レポートがありません',
        exportPdf: 'PDFとしてエクスポート',
      },
      
      // 調査
      investigation: {
        ready: '調査準備完了',
        enterAddress: '上記にブロックチェーンアドレスを入力して分析を開始してください',
      },
      
      // 状態
      loading: '読み込み中...',
      error: 'エラー',
      noData: 'データがありません',
      
      // エラー
      errors: {
        fetchFailed: 'APIサーバーに接続できません。バックエンドが起動しているか確認してください。',
        notFound: 'アドレスが見つかりません。アドレスを確認してもう一度お試しください。',
        invalidAddress: '無効なアドレス形式です。有効なブロックチェーンアドレスを入力してください。',
        serverError: 'サーバーエラーです。後でもう一度お試しください。',
        generic: 'データの取得に失敗しました。接続を確認してもう一度お試しください。',
      },
    },
  },
};

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources,
    fallbackLng: 'en',
    supportedLngs: ['en', 'ja'],
    interpolation: {
      escapeValue: false,
    },
    detection: {
      order: ['localStorage', 'navigator'],
      caches: ['localStorage'],
    },
  });

export default i18n;

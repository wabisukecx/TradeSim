# config/settings.py - 動的重み付け対応完全版
"""
アプリケーション設定管理（動的重み付け対応完全版）
"""

# === アプリケーション設定 ===
APP_CONFIG = {
    'page_title': "📱 株価分析学習アプリ（教育専用・動的重み付け対応）",
    'layout': "centered",
    'initial_sidebar_state': "collapsed"
}

# === テクニカル指標デフォルト値 ===
TECHNICAL_DEFAULTS = {
    'short_ma': 20,
    'long_ma': 50,
    'rsi_period': 14,
    'bb_period': 20,
    'bb_std': 2
}

# === テクニカル指標設定範囲 ===
TECHNICAL_RANGES = {
    'short_ma': {'min': 5, 'max': 50, 'step': 1},
    'long_ma': {'min': 20, 'max': 200, 'step': 1},
    'rsi_period': {'min': 5, 'max': 30, 'step': 1},
    'bb_period': {'min': 10, 'max': 30, 'step': 1}
}

# === バックテストデフォルト値 ===
BACKTEST_DEFAULTS = {
    'initial_capital': 1000000,  # 100万円
    'risk_per_trade': 2.0,      # 2%
    'stop_loss_pct': 5.0,       # 5%
    'take_profit_pct': 15.0,    # 15%
    'trade_cost_rate': 0.1      # 0.1%
}

# === バックテスト設定範囲 ===
BACKTEST_RANGES = {
    'initial_capital': {'min': 100000, 'max': 10000000, 'step': 100000},
    'risk_per_trade': {'min': 0.5, 'max': 5.0, 'step': 0.5},
    'stop_loss_pct': {'min': 1.0, 'max': 20.0, 'step': 0.5},
    'take_profit_pct': {'min': 2.0, 'max': 50.0, 'step': 1.0},
    'trade_cost_rate': {'min': 0.0, 'max': 1.0, 'step': 0.01}
}

# === シグナル閾値 ===
SIGNAL_THRESHOLDS = {
    'buy_threshold': 2.5,
    'sell_threshold': 2.5
}

# === RSI判定基準 ===
RSI_LEVELS = {
    'oversold': 35,      # 売られすぎ
    'overbought': 65,    # 買われすぎ
    'low': 30,
    'high': 70
}

# === パフォーマンス判定基準 ===
PERFORMANCE_CRITERIA = {
    'excellent': 10.0,   # 10%以上で優秀
    'good': 0.0,         # 0%以上で良好
    'sharpe_good': 1.0   # シャープレシオ1.0以上で良好
}

# === 期間オプション ===
PERIOD_OPTIONS = {
    "1ヶ月": 30,
    "3ヶ月": 90,
    "6ヶ月": 180,
    "1年": 365,
    "2年": 730
}

# === 免責事項 ===
DISCLAIMERS = {
    'analysis': """
    ⚠️ 重要な免責事項: この分析結果は教育・学習目的のみです。
    実際の投資判断は、必ず専門的なアドバイスを受けてから行ってください。
    投資にはリスクが伴います。
    """,
    'adaptive_analysis': """
    ⚠️ 重要な免責事項: この動的重み付け分析は教育・学習目的のみです。
    分析結果は参考情報であり、投資判断の保証はありません。
    実際の投資判断は、必ず専門的なアドバイスを受けてから行ってください。
    投資にはリスクが伴います。
    """,
    'backtest': """
    ⚠️ バックテスト免責事項: 過去の成績は将来の成果を保証するものではありません。
    実際の取引では、スリッページや流動性等の要因により結果が異なる場合があります。
    """
}

# === データ検証設定 ===
DATA_VALIDATION = {
    'max_na_ratio': 0.1,        # 欠損データ許容率
    'max_extreme_moves': 0.05,   # 極端な価格変動許容率
    'extreme_move_threshold': 0.5, # 極端な変動の閾値（50%）
    'max_zero_volume_ratio': 0.3   # ゼロ出来高許容率
}

# === API設定 ===
API_SETTINGS = {
    'alpha_vantage': {
        'base_url': "https://www.alphavantage.co/query",
        'function': 'SYMBOL_SEARCH',
        'max_results': 5
    }
}

# === 動的重み付けモード設定 ===
WEIGHT_MODES = {
    'fixed': {
        'name': '🔒 固定重み付け',
        'description': '安定した従来の分析手法。初心者に推奨。',
        'suitable_for': '投資初心者、安定志向',
        'risk_level': 'low',
        'features': ['安定性重視', '予測可能', '学習しやすい']
    },
    'adaptive': {
        'name': '🎯 適応重み付け',
        'description': '相場状況に応じて重み付けを自動調整する高精度分析。',
        'suitable_for': '中級者以上、高精度分析希望',
        'risk_level': 'medium',
        'features': ['高精度', 'パターン検出', '相場適応']
    },
    'manual': {
        'name': '🔧 手動重み付け',
        'description': '完全カスタマイズ可能な重み付け設定。',
        'suitable_for': '上級者、完全制御希望',
        'risk_level': 'variable',
        'features': ['完全制御', 'カスタマイズ', '経験者向け']
    }
}

# === 動的重み付けプロファイル ===
DYNAMIC_WEIGHT_PROFILES = {
    'uptrend': {
        'name': '上昇トレンド',
        'description': '価格が持続的に上昇している状態。移動平均線が上向きで、価格が移動平均を上回っている。',
        'strategy_hint': '移動平均とMACDを重視し、トレンドフォローを基本戦略とする。押し目買いのタイミングを狙う。',
        'risk_level': 'medium',
        'confidence_required': 0.7,
        'weights': {
            'ma_trend': 0.35,
            'macd': 0.30,
            'bollinger': 0.15,
            'rsi': 0.15,
            'volume': 0.05
        },
        'characteristics': ['持続的上昇', '移動平均上向き', 'モメンタム強い']
    },
    'downtrend': {
        'name': '下降トレンド',
        'description': '価格が持続的に下降している状態。移動平均線が下向きで、価格が移動平均を下回っている。',
        'strategy_hint': 'RSIとボリンジャーバンドを重視し、反発ポイントを見極める。下降継続には注意。',
        'risk_level': 'high',
        'confidence_required': 0.7,
        'weights': {
            'rsi': 0.30,
            'bollinger': 0.30,
            'ma_trend': 0.25,
            'macd': 0.10,
            'volume': 0.05
        },
        'characteristics': ['持続的下降', '移動平均下向き', '弱気相場']
    },
    'sideways': {
        'name': 'レンジ相場',
        'description': '価格が一定のレンジ内で推移している横ばい相場。明確なトレンドがない状態。',
        'strategy_hint': 'RSIとボリンジャーバンドを最重視し、レンジの上下限での売買を検討。',
        'risk_level': 'low',
        'confidence_required': 0.6,
        'weights': {
            'rsi': 0.35,
            'bollinger': 0.35,
            'ma_trend': 0.15,
            'macd': 0.10,
            'volume': 0.05
        },
        'characteristics': ['横ばい推移', 'レンジ内変動', '方向感なし']
    },
    'volatile': {
        'name': '高ボラティリティ',
        'description': '価格変動が激しく、予測困難な相場状況。急激な上下動を繰り返している。',
        'strategy_hint': 'MACDとボリュームを重視し、急激な変化を捉える。リスク管理を最優先。',
        'risk_level': 'high',
        'confidence_required': 0.8,
        'weights': {
            'macd': 0.40,
            'volume': 0.25,
            'bollinger': 0.20,
            'rsi': 0.10,
            'ma_trend': 0.05
        },
        'characteristics': ['急激変動', '高ボラティリティ', '出来高急増']
    },
    'consolidation': {
        'name': '調整局面',
        'description': '大きな動きの後の調整・休憩段階。エネルギーを蓄積している状態。',
        'strategy_hint': 'ボリンジャーバンドとRSIを重視し、次の動きに備える。',
        'risk_level': 'low',
        'confidence_required': 0.6,
        'weights': {
            'bollinger': 0.30,
            'rsi': 0.30,
            'ma_trend': 0.20,
            'macd': 0.15,
            'volume': 0.05
        },
        'characteristics': ['小幅変動', '調整中', 'エネルギー蓄積']
    }
}

# === リスクレベル設定 ===
RISK_LEVELS = {
    'low': {
        'name': '低リスク',
        'description': '安定した相場環境',
        'color': '#4CAF50',
        'icon': '🟢',
        'max_position_size': 0.6,
        'recommended_stop_loss': 3.0
    },
    'medium': {
        'name': '中リスク',
        'description': '標準的な相場環境',
        'color': '#FF9800',
        'icon': '🟡',
        'max_position_size': 0.4,
        'recommended_stop_loss': 5.0
    },
    'high': {
        'name': '高リスク',
        'description': '不安定な相場環境',
        'color': '#F44336',
        'icon': '🔴',
        'max_position_size': 0.2,
        'recommended_stop_loss': 8.0
    },
    'variable': {
        'name': '可変リスク',
        'description': 'ユーザー設定による',
        'color': '#9C27B0',
        'icon': '🟣',
        'max_position_size': 0.5,
        'recommended_stop_loss': 5.0
    }
}

# === パターン検出設定 ===
PATTERN_DETECTION_SETTINGS = {
    'min_data_points': 20,  # 最小データ数
    'confidence_threshold': 0.6,  # デフォルト信頼度閾値
    'stability_period': 3,  # パターン安定性チェック期間（日）
    'transition_smoothing': True,  # 遷移平滑化の有効化
    'fallback_mode': 'fixed'  # フォールバックモード
}

# === エラーメッセージ ===
ERROR_MESSAGES = {
    'data_fetch_failed': "❌ データを取得できませんでした",
    'data_empty': "❌ データが空です",
    'data_insufficient': "❌ 分析に必要な十分なデータがありません",
    'invalid_symbol': "❌ 無効な銘柄コードです",
    'api_error': "❌ API接続エラーが発生しました",
    'calculation_error': "❌ 計算エラーが発生しました",
    'pattern_detection_failed': "❌ パターン検出に失敗しました"
}

# === 成功メッセージ ===
SUCCESS_MESSAGES = {
    'data_loaded': "✅ データを正常に読み込みました",
    'analysis_completed': "✅ 分析が正常に完了しました",
    'pattern_detected': "✅ 相場パターンを検出しました",
    'backtest_completed': "✅ バックテストが正常に完了しました"
}

# === 警告メッセージ ===
WARNING_MESSAGES = {
    'extreme_volatility': "⚠️ データに異常な価格変動が検出されました",
    'high_zero_volume': "⚠️ 出来高データに多くの0が含まれています",
    'insufficient_data': "⚠️ データが十分ではありません",
    'low_confidence_pattern': "⚠️ パターン検出の信頼度が低いです",
    'adaptive_fallback': "⚠️ 動的重み付けから固定重み付けにフォールバックしました",
    'data_quality_low': "⚠️ データ品質が低いため結果の信頼性が低下する可能性があります",
    'api_rate_limit': "⚠️ API制限に近づいています。しばらく待ってから再試行してください",
    'network_unstable': "⚠️ ネットワークが不安定です",
    'calculation_precision': "⚠️ 計算精度が低下している可能性があります"
}

# === 情報メッセージ ===
INFO_MESSAGES = {
    'calculating': "🔄 計算中...",
    'fetching_data': "📊 データを取得中...",
    'detecting_pattern': "🎯 パターンを検出中...",
    'running_backtest': "⚡ バックテスト実行中...",
    'loading_settings': "⚙️ 設定を読み込み中...",
    'initializing': "🚀 アプリケーションを初期化中..."
}
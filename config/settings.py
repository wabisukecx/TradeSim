# config/settings.py
"""
アプリケーション設定管理（完全版）
"""

# === アプリケーション設定 ===
APP_CONFIG = {
    'page_title': "📱 株価分析学習アプリ（教育専用）",
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

# === エラーメッセージ ===
ERROR_MESSAGES = {
    'data_fetch_failed': "❌ データを取得できませんでした",
    'data_empty': "❌ データが空です",
    'data_insufficient': "❌ 分析に十分なデータがありません",
    'symbol_not_found': "❌ 指定された銘柄が見つかりません",
    'network_error': "❌ ネットワークエラーが発生しました",
    'api_limit': "❌ API制限に達しました",
    'invalid_symbol': "❌ 銘柄コードが正しくありません"
}

# === 成功メッセージ ===
SUCCESS_MESSAGES = {
    'data_fetched': "✅ データを正常に取得しました",
    'analysis_complete': "✅ 分析が完了しました",
    'portfolio_added': "✅ ポートフォリオに追加しました",
    'portfolio_removed': "✅ ポートフォリオから削除しました"
}

# === 警告メッセージ ===
WARNING_MESSAGES = {
    'extreme_volatility': "⚠️ データに異常な価格変動が検出されました",
    'high_zero_volume': "⚠️ 出来高データに多くの0が含まれています",
    'insufficient_data': "⚠️ データが十分ではありません",
}

# === 免責事項 ===
DISCLAIMERS = {
    'main': """
    ⚠️ このアプリは教育・学習専用です
    ⚠️ 投資助言や推奨ではありません
    ⚠️ 実際の投資判断は自己責任で行ってください
    ⚠️ 投資前には必ず専門家にご相談ください
    ⚠️ 株価は上がったり下がったりするのが普通です
    """,
    'analysis': "⚠️ 以下の結果は参考情報であり、投資助言ではありません。教育・学習目的でのみご利用ください。",
    'simulation': "⚠️ これらは機械的な分析結果であり、将来の価格を予測するものではありません。"
}
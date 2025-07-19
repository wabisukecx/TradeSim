# config/__init__.py - API設定管理対応版
"""
設定管理モジュール
アプリケーション全体の設定・定数・メッセージ・API認証情報を管理
"""

from .settings import (
    # アプリケーション設定
    APP_CONFIG,
    
    # デフォルト値
    TECHNICAL_DEFAULTS,
    BACKTEST_DEFAULTS,
    
    # 範囲設定
    TECHNICAL_RANGES,
    BACKTEST_RANGES,
    
    # オプション
    PERIOD_OPTIONS,
    
    # メッセージ
    DISCLAIMERS,
    WARNING_MESSAGES,
    SUCCESS_MESSAGES,
    ERROR_MESSAGES,
    INFO_MESSAGES,
    
    # 動的重み付け
    WEIGHT_MODES,
    DYNAMIC_WEIGHT_PROFILES,
    
    # リスクレベル
    RISK_LEVELS,
    
    # その他基本設定
    SIGNAL_THRESHOLDS,
    RSI_LEVELS,
    PERFORMANCE_CRITERIA,
)

# API設定管理機能
try:
    from .api_config import APIConfigManager, get_api_config_manager
    API_CONFIG_AVAILABLE = True
except ImportError:
    # API設定管理機能が利用できない場合
    APIConfigManager = None
    get_api_config_manager = None
    API_CONFIG_AVAILABLE = False

__all__ = [
    # アプリケーション設定
    'APP_CONFIG',
    
    # デフォルト値
    'TECHNICAL_DEFAULTS',
    'BACKTEST_DEFAULTS',
    
    # 範囲設定
    'TECHNICAL_RANGES',
    'BACKTEST_RANGES',
    
    # オプション
    'PERIOD_OPTIONS',
    
    # メッセージ
    'DISCLAIMERS',
    'WARNING_MESSAGES',
    'SUCCESS_MESSAGES',
    'ERROR_MESSAGES',
    'INFO_MESSAGES',
    
    # 動的重み付け
    'WEIGHT_MODES',
    'DYNAMIC_WEIGHT_PROFILES',
    
    # リスクレベル
    'RISK_LEVELS',
    
    # その他基本設定
    'SIGNAL_THRESHOLDS',
    'RSI_LEVELS',
    'PERFORMANCE_CRITERIA',
    
    # API設定管理
    'APIConfigManager',
    'get_api_config_manager',
    'API_CONFIG_AVAILABLE',
]
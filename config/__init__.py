# config/__init__.py
"""
設定管理モジュール
アプリケーション全体の設定・定数・メッセージを管理
"""

from .settings import (
    # アプリケーション設定
    APP_CONFIG,
    
    # デフォルト値
    TECHNICAL_DEFAULTS,
    BACKTEST_DEFAULTS,
    
    # オプション
    PERIOD_OPTIONS,
    
    # メッセージ
    DISCLAIMERS,
)

__all__ = [
    # アプリケーション設定
    'APP_CONFIG',
    
    # デフォルト値
    'TECHNICAL_DEFAULTS',
    'BACKTEST_DEFAULTS',
    
    # オプション
    'PERIOD_OPTIONS',
    
    # メッセージ
    'DISCLAIMERS',
]
# __init__.py - プロジェクトルート
"""
TradeSim - 株価分析学習アプリ
初心者向け株価分析とバックテストシミュレーションを提供するStreamlitアプリケーション
"""

__version__ = "1.0.0"
__author__ = "TradeSim Development Team"
__description__ = "教育・学習目的の株価分析アプリケーション"

# パッケージメタデータ（モジュールの直接インポートは削除）
__all__ = [
    'config',
    'data', 
    'analysis',
    'ui',
    'portfolio'
]

# 注意: プロジェクトルートではサブモジュールを直接インポートしません
# 各モジュールは app.py で必要に応じてインポートします
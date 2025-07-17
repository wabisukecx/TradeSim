"""
pytest 共通設定・フィクスチャ（修正版）
"""

import sys
import os
import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import Mock, MagicMock, patch

# プロジェクトルートをPythonパスに追加
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


# Streamlit session_stateの実際の動作に近いモック
class MockSessionState:
    def __init__(self):
        self._data = {}
    
    def __getattr__(self, name):
        return self._data.get(name, None)
    
    def __setattr__(self, name, value):
        if name == '_data':
            super().__setattr__(name, value)
        else:
            self._data[name] = value
    
    def __contains__(self, name):
        return name in self._data
    
    def get(self, name, default=None):
        return self._data.get(name, default)
    
    def clear(self):
        self._data.clear()


@pytest.fixture(scope="session")
def project_root_path():
    """プロジェクトルートパスを提供"""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@pytest.fixture
def mock_streamlit_session():
    """実際の動作に近いStreamlit session_state のモック"""
    session = MockSessionState()
    
    # 初期値設定
    session.analysis_data = None
    session.current_stock_code = None
    session.current_company_name = None
    session.portfolio = {}
    session.portfolio_history = []
    session.is_running_analysis = False
    session.weight_mode = 'fixed'
    session.preset_mode = 'balanced'
    session.auto_run_trigger = False
    session.last_direct_input = ""
    session.direct_input_symbol = "AAPL"
    session.selected_stock_name = None
    session.manual_weights = {
        'ma_trend': 0.2,
        'rsi': 0.2,
        'bollinger': 0.3,
        'macd': 0.3,
        'volume': 0.1
    }
    session.adaptive_analysis_history = []
    session.pattern_detection_settings = {
        'enable_transition_smoothing': True,
        'confidence_threshold': 0.6,
        'pattern_stability_required': False
    }
    session.adaptive_display_settings = {
        'show_pattern_confidence': True,
        'show_weight_breakdown': True,
        'show_strategy_hints': True,
        'show_risk_level': True,
        'show_pattern_history': False
    }
    session.last_detected_pattern = None
    session.weight_learning_enabled = False
    
    return session


@pytest.fixture(autouse=True)
def setup_streamlit_mock(mock_streamlit_session):
    """すべてのテストで自動的にStreamlitをモック"""
    import streamlit as st
    
    # session_stateを実際の動作に近いモックに置き換え
    original_session_state = getattr(st, 'session_state', None)
    st.session_state = mock_streamlit_session
    
    # 他のStreamlit関数もモック
    with patch('streamlit.error'), \
         patch('streamlit.warning'), \
         patch('streamlit.info'), \
         patch('streamlit.success'), \
         patch('streamlit.spinner'):
        yield
    
    # テスト後のクリーンアップ
    if original_session_state is not None:
        st.session_state = original_session_state
    else:
        if hasattr(st, 'session_state'):
            delattr(st, 'session_state')


@pytest.fixture
def sample_stock_data():
    """テスト用の株価データを提供するフィクスチャ"""
    np.random.seed(42)  # 再現可能な結果のため
    dates = pd.date_range(start='2023-01-01', periods=100, freq='D')
    
    # 現実的な株価データを生成
    base_prices = [1000 + i * 0.5 + np.random.normal(0, 10) for i in range(100)]
    
    return pd.DataFrame({
        'Open': [p * np.random.uniform(0.99, 1.01) for p in base_prices],
        'High': [p * np.random.uniform(1.00, 1.03) for p in base_prices],
        'Low': [p * np.random.uniform(0.97, 1.00) for p in base_prices],
        'Close': base_prices,
        'Volume': np.random.randint(10000, 100000, 100)
    }, index=dates)


@pytest.fixture
def sample_company_info():
    """テスト用の企業情報を提供"""
    return {
        'longName': 'Test Company Inc.',
        'currency': 'USD',
        'currentPrice': 1050.0,
        'marketCap': 1000000000,
        'trailingPE': 15.5,
        'dividendYield': 0.025,
        'fiftyTwoWeekHigh': 1100.0,
        'fiftyTwoWeekLow': 900.0
    }


@pytest.fixture
def uptrend_data():
    """上昇トレンドのテストデータ"""
    np.random.seed(42)
    dates = pd.date_range(start='2023-01-01', periods=100, freq='D')
    uptrend_prices = [1000 + i * 2 + np.random.normal(0, 5) for i in range(100)]
    
    return pd.DataFrame({
        'Open': [p * 0.99 for p in uptrend_prices],
        'High': [p * 1.02 for p in uptrend_prices],
        'Low': [p * 0.98 for p in uptrend_prices],
        'Close': uptrend_prices,
        'Volume': np.random.randint(10000, 50000, 100)
    }, index=dates)


@pytest.fixture
def downtrend_data():
    """下降トレンドのテストデータ"""
    np.random.seed(42)
    dates = pd.date_range(start='2023-01-01', periods=100, freq='D')
    downtrend_prices = [1200 - i * 1.5 + np.random.normal(0, 5) for i in range(100)]
    
    return pd.DataFrame({
        'Open': [p * 1.01 for p in downtrend_prices],
        'High': [p * 1.02 for p in downtrend_prices],
        'Low': [p * 0.98 for p in downtrend_prices],
        'Close': downtrend_prices,
        'Volume': np.random.randint(10000, 50000, 100)
    }, index=dates)


@pytest.fixture
def range_data():
    """レンジ相場のテストデータ"""
    np.random.seed(42)
    dates = pd.date_range(start='2023-01-01', periods=100, freq='D')
    range_prices = [1000 + 50 * np.sin(i * 0.1) + np.random.normal(0, 5) for i in range(100)]
    
    return pd.DataFrame({
        'Open': [p * 0.99 for p in range_prices],
        'High': [p * 1.02 for p in range_prices],
        'Low': [p * 0.98 for p in range_prices],
        'Close': range_prices,
        'Volume': np.random.randint(10000, 50000, 100)
    }, index=dates)


@pytest.fixture
def test_technical_params():
    """テクニカル分析用パラメータ"""
    return {
        'short_ma': 20,
        'long_ma': 50,
        'rsi_period': 14,
        'bb_period': 20,
        'bb_std': 2
    }


@pytest.fixture
def test_backtest_params():
    """バックテスト用パラメータ"""
    return {
        'initial_capital': 1000000,
        'risk_per_trade': 2.0,
        'stop_loss_pct': 5.0,
        'take_profit_pct': 15.0,
        'trade_cost_rate': 0.1
    }


# テスト用のユーティリティ関数
def create_test_data_with_indicators(data, analyzer=None):
    """テストデータにテクニカル指標を追加"""
    if analyzer is None:
        from analysis.technical import TechnicalAnalyzer
        analyzer = TechnicalAnalyzer()
    
    return analyzer.calculate_indicators(data)


def assert_dataframe_structure(df, expected_columns, min_rows=1):
    """DataFrameの構造をアサート"""
    assert isinstance(df, pd.DataFrame), "DataFrameでない"
    assert len(df) >= min_rows, f"行数が不足: {len(df)} < {min_rows}"
    
    for col in expected_columns:
        assert col in df.columns, f"列{col}が存在しない"


def assert_signal_structure(signals):
    """シグナルDataFrameの構造をアサート"""
    expected_columns = ['buy_score', 'sell_score', 'signal']
    assert_dataframe_structure(signals, expected_columns)
    
    # データ型の確認
    assert signals['buy_score'].dtype in [np.float64, np.int64], "buy_scoreの型が不正"
    assert signals['sell_score'].dtype in [np.float64, np.int64], "sell_scoreの型が不正"
    assert signals['signal'].dtype in [np.int64, np.float64], "signalの型が不正"


def reset_session_state():
    """セッション状態をテスト用にリセット"""
    import streamlit as st
    if hasattr(st, 'session_state') and hasattr(st.session_state, 'clear'):
        st.session_state.clear()
    elif hasattr(st, 'session_state'):
        # MockSessionStateの場合
        if hasattr(st.session_state, '_data'):
            st.session_state._data.clear()


# テスト実行時の設定
def pytest_configure(config):
    """pytest実行時の初期設定"""
    # カスタムマーカーの登録
    config.addinivalue_line("markers", "slow: mark test as slow running")
    config.addinivalue_line("markers", "integration: mark test as integration test")
    config.addinivalue_line("markers", "unit: mark test as unit test")


def pytest_collection_modifyitems(config, items):
    """テスト収集後の設定調整"""
    for item in items:
        # ファイル名ベースでマーカーを自動追加
        if "test_integration" in item.nodeid:
            item.add_marker(pytest.mark.integration)
        elif "test_" in item.nodeid:
            item.add_marker(pytest.mark.unit)
        
        # 時間のかかりそうなテストにslowマーカーを追加
        if "performance" in item.name.lower() or "large" in item.name.lower():
            item.add_marker(pytest.mark.slow)


# エラー処理のヘルパー
class TestException(Exception):
    """テスト専用例外"""
    pass


def skip_if_missing_module(module_name):
    """モジュールが存在しない場合テストをスキップ"""
    try:
        __import__(module_name)
        return False
    except ImportError:
        return True
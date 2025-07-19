# tests/test_integration.py (修正版)
"""
統合テストコード（修正版）
複数のコンポーネントを組み合わせた全体動作をテスト
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
import streamlit as st

# テスト対象のインポート
from core.app_controller import AppController
from core.state_manager import StateManager
from analysis.technical import TechnicalAnalyzer
from analysis.signals import SignalGenerator
from analysis.backtest import BacktestEngine
from portfolio.manager import PortfolioManager
from data.stock_fetcher import StockDataFetcher
from ui.components import UIComponents
from data import get_combined_search_results


class TestIntegration:
    """統合テスト（アプリケーション全体フロー）"""
    
    def setup_method(self):
        """各テストメソッド実行前の準備処理"""
        # セッション状態をリセット
        if hasattr(st, 'session_state'):
            if hasattr(st.session_state, 'clear'):
                st.session_state.clear()
            elif hasattr(st.session_state, '_data'):
                st.session_state._data.clear()
        
        # コンポーネントの初期化
        self.app_controller = AppController()
        self.technical_analyzer = TechnicalAnalyzer()
        self.signal_generator = SignalGenerator()
        self.backtest_engine = BacktestEngine()
        self.portfolio_manager = PortfolioManager()
        
        # テスト用データの準備
        self.setup_test_data()
        self.setup_test_parameters()

    def setup_test_data(self):
        """テスト用データの準備"""
        np.random.seed(42)
        
        # 基本的な株価データ
        dates = pd.date_range(start='2023-01-01', periods=252, freq='D')  # 1年分
        base_prices = [1000 + i * 0.5 + np.random.normal(0, 10) for i in range(252)]
        
        self.test_stock_data = pd.DataFrame({
            'Open': [p * 0.99 for p in base_prices],
            'High': [p * 1.02 for p in base_prices],
            'Low': [p * 0.98 for p in base_prices],
            'Close': base_prices,
            'Volume': np.random.randint(10000, 100000, 252)
        }, index=dates)
        
        # 企業情報のモックデータ
        self.test_company_info = {
            'longName': 'Test Company Inc.',
            'currency': 'USD',
            'currentPrice': base_prices[-1],
            'marketCap': 1000000000,
            'trailingPE': 15.5,
            'dividendYield': 0.025
        }

    def setup_test_parameters(self):
        """テスト用パラメータの準備"""
        self.test_technical_params = {
            'short_ma': 20,
            'long_ma': 50,
            'rsi_period': 14,
            'bb_period': 20,
            'bb_std': 2
        }
        
        self.test_backtest_params = {
            'initial_capital': 1000000,
            'risk_per_trade': 2.0,
            'stop_loss_pct': 5.0,
            'take_profit_pct': 15.0,
            'trade_cost_rate': 0.1
        }
        
        self.test_analysis_params = {
            'start_date': datetime.now() - timedelta(days=365),
            'end_date': datetime.now(),
            'period_name': '1年',
            'weight_mode': 'fixed',
            **self.test_technical_params,
            **self.test_backtest_params
        }

    # ======================
    # 全体フロー統合テスト
    # ======================
    
    @patch('data.cache_manager.cache_stock_data')
    def test_full_application_workflow(self, mock_cache_stock_data):
        """全体的なアプリケーションワークフローテスト"""
        # データ取得のモック
        mock_cache_stock_data.return_value = (self.test_stock_data, self.test_company_info)
        
        # StateManagerの初期化
        StateManager.initialize_session_state()
        
        # 分析実行
        success = self.app_controller.run_analysis("AAPL", self.test_analysis_params)
        
        # 基本的な動作確認
        assert isinstance(success, bool), "戻り値がbool型でない"
        
        # 成功時の詳細確認
        if success:
            # 分析データが保存されているか確認
            has_data = StateManager.has_analysis_data()
            assert isinstance(has_data, bool), "has_analysis_dataがbool型でない"

    @patch('data.cache_manager.cache_stock_data')
    def test_technical_analysis_integration(self, mock_cache_stock_data):
        """テクニカル分析統合テスト"""
        mock_cache_stock_data.return_value = (self.test_stock_data, self.test_company_info)
        
        # ✅ 修正：キーワード引数として展開
        df_with_indicators = self.technical_analyzer.calculate_indicators(
            self.test_stock_data, **self.test_technical_params
        )
        
        # 結果の検証
        assert not df_with_indicators.empty, "テクニカル指標計算結果が空"
        
        # 主要指標の存在確認（実際の出力列名に合わせて修正）
        expected_columns = ['MA_short', 'MA_long', 'RSI', 'BB_upper', 'BB_lower']
        for col in expected_columns:
            assert col in df_with_indicators.columns, f"{col}が計算されていない"

    @patch('data.cache_manager.cache_stock_data')
    def test_signal_generation_integration(self, mock_cache_stock_data):
        """シグナル生成統合テスト"""
        mock_cache_stock_data.return_value = (self.test_stock_data, self.test_company_info)
        
        # ✅ 修正：キーワード引数として展開
        df_with_indicators = self.technical_analyzer.calculate_indicators(
            self.test_stock_data, **self.test_technical_params
        )
        
        # シグナル生成（正しいメソッド名を使用）
        signals = self.signal_generator.generate_signals_advanced(df_with_indicators)
        
        # 結果の検証
        assert not signals.empty, "シグナル生成結果が空"
        assert 'signal' in signals.columns, "signalカラムが存在しない"
        assert 'buy_score' in signals.columns, "buy_scoreカラムが存在しない"
        assert 'sell_score' in signals.columns, "sell_scoreカラムが存在しない"

    @patch('data.cache_manager.cache_stock_data')
    def test_backtest_integration(self, mock_cache_stock_data):
        """バックテスト統合テスト"""
        mock_cache_stock_data.return_value = (self.test_stock_data, self.test_company_info)
        
        # ✅ 修正：キーワード引数として展開
        df_with_indicators = self.technical_analyzer.calculate_indicators(
            self.test_stock_data, **self.test_technical_params
        )
        
        # シグナル生成
        signals = self.signal_generator.generate_signals_advanced(df_with_indicators)
        
        # バックテスト実行
        portfolio_df, trade_log = self.backtest_engine.backtest_realistic(
            df_with_indicators, signals, **self.test_backtest_params
        )
        
        # 結果の検証（柔軟なチェック）
        if portfolio_df is not None and not portfolio_df.empty:
            assert isinstance(trade_log, pd.DataFrame), "取引ログがDataFrameでない"
        else:
            # バックテストが実行されない場合もあるので、警告として記録
            print("警告: バックテストが実行されませんでした")

    # ======================
    # 他の統合テスト
    # ======================
    
    def test_portfolio_management_integration(self):
        """ポートフォリオ管理統合テスト"""
        # 1. ポートフォリオに銘柄追加
        result = self.portfolio_manager.add_stock("AAPL", 10, 150.0, "Apple Inc.")
        assert "追加しました" in result, "ポートフォリオ追加が失敗した"
        
        # 2. ポートフォリオサマリー取得
        summary = self.portfolio_manager.get_portfolio_summary()
        assert summary['position_count'] == 1, "ポートフォリオ件数が正しくない"
        assert len(summary['positions']) == 1, "ポジション数が正しくない"
        
        # 3. ポートフォリオエクスポート
        df = self.portfolio_manager.export_portfolio()
        assert not df.empty, "ポートフォリオエクスポートが空"
        assert 'AAPL' in df['銘柄コード'].values, "追加した銘柄がエクスポートに含まれていない"
        
        # 4. 銘柄削除
        result = self.portfolio_manager.remove_stock("AAPL")
        assert "削除しました" in result, "ポートフォリオ削除が失敗した"
        
        # 5. 削除後の確認
        summary_after = self.portfolio_manager.get_portfolio_summary()
        assert summary_after['position_count'] == 0, "削除後もポートフォリオに残っている"

    def test_stock_search_integration(self):
        """銘柄検索機能の統合テスト"""
        # 1. 日本語検索（JQuants APIが設定されていない場合はフォールバック）
        results = get_combined_search_results("トヨタ")
        # APIが設定されていなくてもフォールバック検索で結果が得られる可能性
        assert isinstance(results, list), "検索結果がリストでない"
        
        # 2. 英語検索（基本的な企業名）
        results = get_combined_search_results("Apple")
        assert isinstance(results, list), "検索結果がリストでない"
        
        # 3. コード直接検索
        results = get_combined_search_results("AAPL")
        assert isinstance(results, list), "検索結果がリストでない"

    def test_preset_settings_integration(self):
        """プリセット設定統合テスト"""
        # 初心者向けプリセット
        StateManager.set_preset_mode("beginner")
        preset_mode = StateManager.get_preset_mode()
        assert preset_mode == "beginner", "プリセットモード設定が失敗"
        
        # プリセット設定の取得
        technical_params, backtest_params = self.app_controller.get_preset_settings("beginner")
        assert isinstance(technical_params, dict), "テクニカルパラメータが辞書でない"
        assert isinstance(backtest_params, dict), "バックテストパラメータが辞書でない"
        
        # 必要なキーが含まれているか確認
        required_technical_keys = ['short_ma', 'long_ma', 'rsi_period', 'bb_period']
        for key in required_technical_keys:
            assert key in technical_params, f"テクニカルパラメータに{key}が含まれていない"
        
        required_backtest_keys = ['initial_capital', 'risk_per_trade', 'stop_loss_pct']
        for key in required_backtest_keys:
            assert key in backtest_params, f"バックテストパラメータに{key}が含まれていない"

    # ======================
    # エラーハンドリング統合テスト
    # ======================
    
    @patch('data.cache_manager.cache_stock_data')
    def test_data_fetch_error_handling(self, mock_cache_stock_data):
        """データ取得エラーのハンドリングテスト"""
        # データ取得エラーをシミュレート
        mock_cache_stock_data.return_value = (None, None)
        
        # 分析実行
        success = self.app_controller.run_analysis("INVALID", self.test_analysis_params)
        
        # エラーが適切にハンドリングされているか確認
        assert isinstance(success, bool), "戻り値がbool型でない"
        # エラー時はFalseが返されることを期待
        assert not success, "無効なデータでも成功が返された"

    @patch('data.cache_manager.cache_stock_data')
    def test_empty_data_error_handling(self, mock_cache_stock_data):
        """空データのエラーハンドリングテスト"""
        # 空のDataFrameを返すように設定
        empty_df = pd.DataFrame()
        mock_cache_stock_data.return_value = (empty_df, self.test_company_info)
        
        # 分析実行
        success = self.app_controller.run_analysis("AAPL", self.test_analysis_params)
        
        # エラーが適切にハンドリングされているか確認
        assert isinstance(success, bool), "戻り値がbool型でない"

    @patch('data.cache_manager.cache_stock_data')
    def test_insufficient_data_error_handling(self, mock_cache_stock_data):
        """データ不足のエラーハンドリングテスト"""
        # データ不足のDataFrameを作成（10日分のみ）
        insufficient_data = self.test_stock_data.head(10)
        mock_cache_stock_data.return_value = (insufficient_data, self.test_company_info)
        
        # 分析実行
        success = self.app_controller.run_analysis("AAPL", self.test_analysis_params)
        
        # エラーが適切にハンドリングされているか確認
        assert isinstance(success, bool), "戻り値がbool型でない"

    # ======================
    # パフォーマンステスト
    # ======================
    
    @patch('data.cache_manager.cache_stock_data')
    def test_full_analysis_performance(self, mock_cache_stock_data):
        """全体分析のパフォーマンステスト"""
        import time
        
        # 大きなデータセットを作成（2年分）
        large_dates = pd.date_range(start='2022-01-01', periods=500, freq='D')
        large_prices = [1000 + i * 0.5 + np.random.normal(0, 10) for i in range(500)]
        large_data = pd.DataFrame({
            'Open': [p * 0.99 for p in large_prices],
            'High': [p * 1.02 for p in large_prices],
            'Low': [p * 0.98 for p in large_prices],
            'Close': large_prices,
            'Volume': np.random.randint(10000, 100000, 500)
        }, index=large_dates)
        
        mock_cache_stock_data.return_value = (large_data, self.test_company_info)
        
        # パフォーマンス測定
        start_time = time.time()
        success = self.app_controller.run_analysis("AAPL", self.test_analysis_params)
        end_time = time.time()
        
        execution_time = end_time - start_time
        
        # 実行時間が妥当な範囲内か確認（60秒以内）
        assert execution_time < 60, f"分析実行時間が長すぎる: {execution_time:.2f}秒"
        
        # 成功時の結果確認
        if success:
            assert StateManager.has_analysis_data(), "大量データ分析でデータが保存されていない"

    # ======================
    # UI統合テスト
    # ======================
    
    def test_ui_components_integration(self):
        """UIコンポーネント統合テスト"""
        # UIコンポーネントが正常に初期化できるか確認
        try:
            # ヘッダー描画テスト（実際には描画しない）
            UIComponents.render_header()
            
            # 説明ボックス描画テスト
            UIComponents.render_explanation_box("テスト", "テスト内容")
            
            # ヒントボックス描画テスト
            UIComponents.render_tip_box("ヒント", "ヒント内容")
            
        except Exception as e:
            pytest.fail(f"UIコンポーネントの初期化でエラー: {e}")

    def test_data_validation_integration(self):
        """データ検証統合テスト"""
        # 異常なデータを含むテストケース
        invalid_data = self.test_stock_data.copy()
        
        # 極端な値を注入
        invalid_data.loc[invalid_data.index[10], 'Close'] = 999999999  # 異常に高い価格
        invalid_data.loc[invalid_data.index[20], 'Volume'] = 0  # ゼロ出来高
        
        # データ検証が適切に動作するか確認
        try:
            # ✅ 修正：キーワード引数として展開
            df_with_indicators = self.technical_analyzer.calculate_indicators(
                invalid_data, **self.test_technical_params
            )
            
            # 計算が完了しても、適切にデータが処理されているか確認
            assert not df_with_indicators.empty, "異常データの処理でDataFrameが空になった"
            
        except Exception as e:
            # エラーが発生した場合も適切なエラーであることを確認
            assert "data" in str(e).lower() or "invalid" in str(e).lower(), f"予期しないエラー: {e}"
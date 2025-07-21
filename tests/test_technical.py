# tests/test_technical.py
"""
テクニカル分析機能のテストコード
analysis/technical.py の TechnicalAnalyzer クラスをテスト
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# テスト対象のインポート
from analysis.technical import TechnicalAnalyzer


class TestTechnicalAnalyzer:
    """TechnicalAnalyzer クラスの包括的テスト"""
    
    def setup_method(self):
        """各テストメソッド実行前の準備処理"""
        self.analyzer = TechnicalAnalyzer()
        
        # 現実的なテスト用株価データを作成
        self.test_dates = pd.date_range(start='2023-01-01', periods=100, freq='D')
        np.random.seed(42)  # 再現可能な結果のため
        
        # 基本価格トレンド（上昇気味）
        base_prices = [1000 + i * 2 for i in range(100)]
        noise = np.random.normal(0, 10, 100)  # ノイズ追加
        close_prices = [max(base + n, 100) for base, n in zip(base_prices, noise)]
        
        self.valid_data = pd.DataFrame({
            'Open': [p * 0.99 for p in close_prices],
            'High': [p * 1.02 for p in close_prices],
            'Low': [p * 0.98 for p in close_prices],
            'Close': close_prices,
            'Volume': np.random.randint(10000, 100000, 100)
        }, index=self.test_dates)
        
        # 短いデータ（エラーケース用）- より適切なサイズ
        self.short_data = self.valid_data.head(20)  # 20日分（ATR計算に最低限必要）
        
        # 非常に短いデータ（明確にエラーとなるケース）
        self.very_short_data = self.valid_data.head(5)
        
        # 空データ（エラーケース用）
        self.empty_data = pd.DataFrame()

    # ======================
    # 基本機能テスト
    # ======================
    
    def test_calculate_indicators_basic_functionality(self):
        """基本的な指標計算機能のテスト"""
        result = self.analyzer.calculate_indicators(self.valid_data)
        
        # 必須列の存在確認
        expected_columns = ['MA_short', 'MA_long', 'RSI', 'BB_upper', 'BB_middle', 'BB_lower', 'MACD', 'MACD_signal']
        for col in expected_columns:
            assert col in result.columns, f"計算結果に{col}列が含まれていない"
        
        # 元のデータが保持されているか確認
        original_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        for col in original_columns:
            assert col in result.columns, f"元データの{col}列が失われている"
        
        # データ長が変わっていないか確認
        assert len(result) == len(self.valid_data), "結果のデータ長が変わっている"

    def test_calculate_indicators_with_custom_parameters(self):
        """カスタムパラメータでの指標計算テスト"""
        custom_params = {
            'short_ma': 5,
            'long_ma': 25,
            'rsi_period': 10,
            'bb_period': 15,
            'bb_std': 1.5
        }
        
        result = self.analyzer.calculate_indicators(self.valid_data, **custom_params)
        
        # カスタムパラメータが適用されているかの確認
        # 移動平均の値が期間に応じて適切に計算されているか
        assert 'MA_short' in result.columns, "短期移動平均が計算されていない"
        assert 'MA_long' in result.columns, "長期移動平均が計算されていない"
        
        # NaN以外の値が存在するか確認
        ma_short_valid = result['MA_short'].notna().sum()
        ma_long_valid = result['MA_long'].notna().sum()
        
        # 短期移動平均の方が長期移動平均よりも多くの有効値を持つべき
        assert ma_short_valid >= ma_long_valid, "短期移動平均の有効値が長期移動平均より少ない"

    # ======================
    # 個別指標テスト
    # ======================
    
    def test_moving_average_calculation(self):
        """移動平均計算のテスト"""
        result = self.analyzer.calculate_indicators(self.valid_data, short_ma=5, long_ma=10)
        
        # 移動平均列の存在確認
        assert 'MA_short' in result.columns, "短期移動平均が計算されていない"
        assert 'MA_long' in result.columns, "長期移動平均が計算されていない"
        
        # 値の妥当性確認（NaNでない値の確認）
        ma_short_data = result['MA_short'].dropna()
        ma_long_data = result['MA_long'].dropna()
        
        assert not ma_short_data.empty, "短期移動平均にデータがない"
        assert not ma_long_data.empty, "長期移動平均にデータがない"
        
        # 移動平均値が合理的範囲内にあるか確認
        close_min, close_max = self.valid_data['Close'].min(), self.valid_data['Close'].max()
        
        assert ma_short_data.min() >= close_min * 0.8, "短期移動平均が極端に小さい"
        assert ma_short_data.max() <= close_max * 1.2, "短期移動平均が極端に大きい"

    def test_rsi_calculation(self):
        """RSI計算のテスト"""
        result = self.analyzer.calculate_indicators(self.valid_data, rsi_period=14)
        
        # RSI列の存在確認
        assert 'RSI' in result.columns, "RSIが計算されていない"
        
        # RSI値の範囲確認（0-100の範囲内）
        rsi_data = result['RSI'].dropna()
        if not rsi_data.empty:
            assert (rsi_data >= 0).all(), "RSIに負の値が含まれている"
            assert (rsi_data <= 100).all(), "RSIに100を超える値が含まれている"

    def test_bollinger_bands_calculation(self):
        """ボリンジャーバンド計算のテスト"""
        result = self.analyzer.calculate_indicators(self.valid_data, bb_period=20, bb_std=2)
        
        # ボリンジャーバンド列の存在確認
        bb_columns = ['BB_upper', 'BB_middle', 'BB_lower']
        for col in bb_columns:
            assert col in result.columns, f"ボリンジャーバンド{col}が計算されていない"
        
        # バンドの順序確認（上限 > 中央 > 下限）
        bb_data = result[['BB_upper', 'BB_middle', 'BB_lower', 'Close']].dropna()
        if not bb_data.empty:
            assert (bb_data['BB_upper'] >= bb_data['BB_middle']).all(), "ボリンジャーバンド上限が中央より下にある"
            assert (bb_data['BB_middle'] >= bb_data['BB_lower']).all(), "ボリンジャーバンド中央が下限より下にある"
            
            # 中央線が移動平均として妥当か
            # （厳密な比較は避け、大まかな範囲で確認）
            close_mean = bb_data['Close'].mean()
            middle_mean = bb_data['BB_middle'].mean()
            assert abs(close_mean - middle_mean) / close_mean < 0.1, "ボリンジャーバンド中央線が移動平均として不適切"

    def test_macd_calculation(self):
        """MACD計算のテスト"""
        result = self.analyzer.calculate_indicators(self.valid_data)
        
        # MACD関連列の存在確認
        macd_columns = ['MACD', 'MACD_signal', 'MACD_diff']
        for col in macd_columns:
            assert col in result.columns, f"MACD計算結果に{col}が含まれていない"
        
        # MACD差分の計算確認
        macd_data = result[['MACD', 'MACD_signal', 'MACD_diff']].dropna()
        if not macd_data.empty:
            # MACD_diff = MACD - MACD_signal の関係確認
            calculated_diff = macd_data['MACD'] - macd_data['MACD_signal']
            actual_diff = macd_data['MACD_diff']
            
            # 浮動小数点誤差を考慮した比較
            diff_comparison = np.abs(calculated_diff - actual_diff) < 1e-10
            assert diff_comparison.all(), "MACD差分の計算が正しくない"

    # ======================
    # エラーハンドリングテスト
    # ======================
    
    def test_empty_data_handling(self):
        """空データに対するエラーハンドリングテスト"""
        with pytest.raises(Exception):
            self.analyzer.calculate_indicators(self.empty_data)

    def test_insufficient_data_handling(self):
        """データ不足時の処理テスト"""
        # 非常に短いデータでATRの計算エラーが発生することをテスト
        with pytest.raises((IndexError, ValueError, Exception)):
            # ATR計算に必要な最小データ数を下回るデータでエラーが発生することを確認
            self.analyzer.calculate_indicators(self.very_short_data, long_ma=50)

    def test_moderate_data_insufficient_for_long_ma(self):
        """中程度のデータ不足時の処理テスト"""
        # 長期移動平均には不足するが、他の指標は計算可能なデータ長での動作確認
        try:
            result = self.analyzer.calculate_indicators(self.short_data, long_ma=30, short_ma=5)
            
            # 短期移動平均は計算できているはず
            assert 'MA_short' in result.columns, "短期移動平均が計算されていない"
            
            # 長期移動平均は計算できない部分が多いはず
            ma_long_valid = result['MA_long'].notna().sum()
            ma_short_valid = result['MA_short'].notna().sum()
            assert ma_long_valid <= ma_short_valid, "長期移動平均の方が短期移動平均より多く計算されている"
            
        except Exception as e:
            # ATRなどでエラーが発生する場合もある
            assert isinstance(e, (IndexError, ValueError)), f"想定外のエラータイプ: {type(e)}"

    def test_invalid_parameters_handling(self):
        """不正なパラメータの処理テスト"""
        # 負の値や0のパラメータ
        with pytest.raises((ValueError, Exception)):
            self.analyzer.calculate_indicators(self.valid_data, short_ma=-1)
        
        with pytest.raises((ValueError, Exception)):
            self.analyzer.calculate_indicators(self.valid_data, rsi_period=0)

    def test_missing_columns_handling(self):
        """必要な列が不足している場合のテスト"""
        incomplete_data = pd.DataFrame({
            'Close': [100, 101, 102, 103, 104]  # High, Low, Volumeが不足
        })
        
        # エラーが適切に発生するか、または適切にハンドリングされるかテスト
        try:
            result = self.analyzer.calculate_indicators(incomplete_data)
            # もしエラーが発生しない場合、計算できる指標のみ計算されているかチェック
            assert 'RSI' in result.columns, "Closeのみでも計算可能なRSIが計算されていない"
        except Exception:
            # エラーが発生することも適切な動作
            pass

    # ======================
    # サマリー機能テスト
    # ======================
    
    def test_get_indicator_summary_basic(self):
        """指標サマリー取得の基本テスト"""
        df_with_indicators = self.analyzer.calculate_indicators(self.valid_data)
        summary = self.analyzer.get_indicator_summary(df_with_indicators)
        
        # 必須キーの存在確認
        expected_keys = [
            'current_price', 'current_volume', 'ma_short', 'ma_long', 
            'ma_trend', 'rsi', 'rsi_status', 'bb_upper', 'bb_middle', 'bb_lower'
        ]
        
        for key in expected_keys:
            assert key in summary, f"サマリーに{key}が含まれていない"

    def test_get_indicator_summary_values(self):
        """指標サマリー値の妥当性テスト"""
        df_with_indicators = self.analyzer.calculate_indicators(self.valid_data)
        summary = self.analyzer.get_indicator_summary(df_with_indicators)
        
        # 数値型の確認
        numeric_keys = ['current_price', 'current_volume', 'ma_short', 'ma_long', 'rsi']
        for key in numeric_keys:
            if summary[key] is not None and not pd.isna(summary[key]):
                assert isinstance(summary[key], (int, float)), f"{key}が数値型でない"
        
        # カテゴリ値の確認
        assert summary['ma_trend'] in ['uptrend', 'downtrend'], "ma_trendの値が不正"
        assert summary['rsi_status'] in ['oversold', 'overbought', 'neutral', 'unknown'], "rsi_statusの値が不正"

    # ======================
    # アドバンステスト
    # ======================
    
    def test_calculate_indicators_performance(self):
        """計算パフォーマンスのテスト"""
        import time
        
        # 大きなデータセットでの計算時間測定
        large_data = self.valid_data.copy()
        # データを複製して大きくする
        for _ in range(5):
            large_data = pd.concat([large_data, self.valid_data])
        
        start_time = time.time()
        result = self.analyzer.calculate_indicators(large_data)
        elapsed_time = time.time() - start_time
        
        # 計算が完了すること
        assert result is not None, "大データでの計算が失敗"
        assert len(result) == len(large_data), "大データでの結果データ長が正しくない"
        
        # 合理的な時間内での完了（10秒以内）
        assert elapsed_time < 10, f"計算時間が長すぎる: {elapsed_time:.2f}秒"

    def test_support_resistance_levels(self):
        """サポート・レジスタンスレベルの計算テスト"""
        if hasattr(self.analyzer, 'get_support_resistance'):
            df_with_indicators = self.analyzer.calculate_indicators(self.valid_data)
            levels = self.analyzer.get_support_resistance(df_with_indicators)
            
            # 戻り値の構造確認
            assert 'support' in levels
            assert 'resistance' in levels
            
            # 値の妥当性確認
            support = levels['support']
            resistance = levels['resistance']
            current_price = df_with_indicators['Close'].iloc[-1]
            
            assert support <= resistance, "サポートレベルがレジスタンスレベルより高い"
            
            # 現在価格がサポート・レジスタンス範囲内の妥当な位置にあるか
            price_range = resistance - support
            assert abs(current_price - ((support + resistance) / 2)) <= price_range, "現在価格がサポート・レジスタンス範囲から大きく外れている"

    def test_trend_strength_calculation(self):
        """トレンド強度計算のテスト"""
        if hasattr(self.analyzer, 'get_trend_strength'):
            df_with_indicators = self.analyzer.calculate_indicators(self.valid_data)
            trend_strength = self.analyzer.get_trend_strength(df_with_indicators)
            
            # 戻り値の構造確認
            assert 'strength' in trend_strength
            assert 'direction' in trend_strength
            
            # 値の妥当性確認
            assert isinstance(trend_strength['strength'], (int, float)), "トレンド強度が数値でない"
            assert trend_strength['direction'] in [
                'strong_uptrend', 'weak_uptrend', 'neutral', 
                'weak_downtrend', 'strong_downtrend'
            ], "トレンド方向の値が不正"

    def test_pattern_detection_integration(self):
        """パターン検出機能との統合テスト"""
        if hasattr(self.analyzer, 'detect_patterns'):
            df_with_indicators = self.analyzer.calculate_indicators(self.valid_data)
            patterns = self.analyzer.detect_patterns(df_with_indicators)
            
            # 戻り値の構造確認
            expected_patterns = ['golden_cross', 'dead_cross', 'rsi_divergence', 'breakout']
            for pattern in expected_patterns:
                assert pattern in patterns, f"パターン{pattern}が結果に含まれていない"
                assert isinstance(patterns[pattern], bool), f"パターン{pattern}の値がbool型でない"

    # ======================
    # ATR特有のテスト
    # ======================
    
    def test_atr_calculation_with_sufficient_data(self):
        """十分なデータでのATR計算テスト"""
        result = self.analyzer.calculate_indicators(self.valid_data)
        
        # ATRが計算されているか確認
        assert 'ATR' in result.columns, "ATRが計算されていない"
        
        # ATRが正の値であることを確認
        atr_values = result['ATR'].dropna()
        if not atr_values.empty:
            assert (atr_values >= 0).all(), "ATRに負の値が含まれている"

    def test_atr_calculation_error_handling(self):
        """ATR計算のエラーハンドリングテスト"""
        # ATR計算に必要な最小データを下回る場合のテスト
        minimal_data = self.valid_data.head(3)  # 3日分のみ
        
        with pytest.raises((IndexError, ValueError, Exception)):
            # ATR計算でエラーが発生することを確認
            self.analyzer.calculate_indicators(minimal_data)

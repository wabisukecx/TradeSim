# analysis/signals.py
"""
シグナル生成機能
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple

from config.settings import SIGNAL_THRESHOLDS, RSI_LEVELS


class SignalGenerator:
    """シグナル生成クラス"""
    
    def __init__(self):
        self.signal_weights = {
            'ma_trend': 1.0,
            'rsi': 1.0,
            'bollinger': 1.5,
            'macd': 1.5,
            'volume': 0.5
        }
    
    def generate_signals_advanced(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        高度なシグナル生成
        
        Args:
            df: テクニカル指標が計算済みのDataFrame
            
        Returns:
            pd.DataFrame: シグナルが追加されたDataFrame
        """
        signals = pd.DataFrame(index=df.index)
        
        # 浮動小数点数で初期化してdtype警告を回避
        signals['buy_score'] = 0.0
        signals['sell_score'] = 0.0
        
        # 移動平均トレンドシグナル
        signals = self._add_ma_signals(signals, df)
        
        # RSIシグナル
        signals = self._add_rsi_signals(signals, df)
        
        # ボリンジャーバンドシグナル
        signals = self._add_bollinger_signals(signals, df)
        
        # MACDシグナル
        signals = self._add_macd_signals(signals, df)
        
        # 出来高シグナル
        signals = self._add_volume_signals(signals, df)
        
        # 最終シグナル決定
        signals = self._finalize_signals(signals)
        
        return signals
    
    def _add_ma_signals(self, signals: pd.DataFrame, df: pd.DataFrame) -> pd.DataFrame:
        """移動平均シグナルを追加"""
        if 'MA_short' in df.columns and 'MA_long' in df.columns:
            # 短期移動平均 > 長期移動平均 = 買いシグナル
            buy_condition = df['MA_short'] > df['MA_long']
            sell_condition = df['MA_short'] < df['MA_long']
            
            signals.loc[buy_condition, 'buy_score'] += self.signal_weights['ma_trend']
            signals.loc[sell_condition, 'sell_score'] += self.signal_weights['ma_trend']
        
        return signals
    
    def _add_rsi_signals(self, signals: pd.DataFrame, df: pd.DataFrame) -> pd.DataFrame:
        """RSIシグナルを追加"""
        if 'RSI' in df.columns:
            # RSI < 35 = 買いシグナル（売られすぎ）
            # RSI > 65 = 売りシグナル（買われすぎ）
            oversold_condition = df['RSI'] < RSI_LEVELS['oversold']
            overbought_condition = df['RSI'] > RSI_LEVELS['overbought']
            
            signals.loc[oversold_condition, 'buy_score'] += self.signal_weights['rsi']
            signals.loc[overbought_condition, 'sell_score'] += self.signal_weights['rsi']
        
        return signals
    
    def _add_bollinger_signals(self, signals: pd.DataFrame, df: pd.DataFrame) -> pd.DataFrame:
        """ボリンジャーバンドシグナルを追加"""
        if all(col in df.columns for col in ['Close', 'BB_upper', 'BB_lower']):
            # 価格 < 下限バンド = 買いシグナル
            # 価格 > 上限バンド = 売りシグナル
            below_lower = df['Close'] < df['BB_lower']
            above_upper = df['Close'] > df['BB_upper']
            
            signals.loc[below_lower, 'buy_score'] += self.signal_weights['bollinger']
            signals.loc[above_upper, 'sell_score'] += self.signal_weights['bollinger']
        
        return signals
    
    def _add_macd_signals(self, signals: pd.DataFrame, df: pd.DataFrame) -> pd.DataFrame:
        """MACDシグナルを追加"""
        if all(col in df.columns for col in ['MACD', 'MACD_signal']):
            # MACDラインがシグナルラインを上抜け = 買いシグナル
            # MACDラインがシグナルラインを下抜け = 売りシグナル
            
            # ゴールデンクロス検出
            macd_above = df['MACD'] > df['MACD_signal']
            macd_above_prev = df['MACD'].shift(1) <= df['MACD_signal'].shift(1)
            golden_cross = macd_above & macd_above_prev
            
            # デッドクロス検出
            macd_below = df['MACD'] < df['MACD_signal']
            macd_below_prev = df['MACD'].shift(1) >= df['MACD_signal'].shift(1)
            dead_cross = macd_below & macd_below_prev
            
            signals.loc[golden_cross, 'buy_score'] += self.signal_weights['macd']
            signals.loc[dead_cross, 'sell_score'] += self.signal_weights['macd']
        
        return signals
    
    def _add_volume_signals(self, signals: pd.DataFrame, df: pd.DataFrame) -> pd.DataFrame:
        """出来高シグナルを追加"""
        if all(col in df.columns for col in ['Volume', 'Volume_MA']):
            # 出来高 > 平均出来高 = 取引活発（買い・売り両方に加点）
            high_volume = df['Volume'] > df['Volume_MA']
            
            signals.loc[high_volume, 'buy_score'] += self.signal_weights['volume']
            signals.loc[high_volume, 'sell_score'] += self.signal_weights['volume']
        
        return signals
    
    def _finalize_signals(self, signals: pd.DataFrame) -> pd.DataFrame:
        """最終シグナルを決定"""
        buy_threshold = SIGNAL_THRESHOLDS['buy_threshold']
        sell_threshold = SIGNAL_THRESHOLDS['sell_threshold']
        
        signals['signal'] = 0
        signals.loc[signals['buy_score'] >= buy_threshold, 'signal'] = 1
        signals.loc[signals['sell_score'] >= sell_threshold, 'signal'] = -1
        
        return signals
    
    def get_signal_explanation(self, signals: pd.DataFrame, df: pd.DataFrame, index: int = -1) -> Dict[str, any]:
        """
        シグナルの詳細説明を取得
        
        Args:
            signals: シグナルDataFrame
            df: 株価データFrameDataFrame
            index: 説明を取得するインデックス（デフォルト: 最新）
            
        Returns:
            dict: シグナル説明
        """
        if abs(index) > len(signals):
            return {}
        
        signal_data = signals.iloc[index]
        price_data = df.iloc[index]
        
        explanation = {
            'signal': signal_data['signal'],
            'buy_score': signal_data['buy_score'],
            'sell_score': signal_data['sell_score'],
            'reasons': []
        }
        
        # 各指標の判断理由を追加
        reasons = []
        
        # 移動平均
        if 'MA_short' in df.columns and 'MA_long' in df.columns:
            ma_short = price_data['MA_short']
            ma_long = price_data['MA_long']
            if pd.notna(ma_short) and pd.notna(ma_long):
                if ma_short > ma_long:
                    reasons.append("✅ **上昇トレンド** - 短期平均 > 長期平均")
                else:
                    reasons.append("❌ **下降トレンド** - 短期平均 < 長期平均")
        
        # RSI
        if 'RSI' in df.columns:
            rsi = price_data['RSI']
            if pd.notna(rsi):
                if rsi < RSI_LEVELS['oversold']:
                    reasons.append(f"✅ **RSI低水準** - RSI = {rsi:.1f}（反発の可能性を示唆）")
                elif rsi > RSI_LEVELS['overbought']:
                    reasons.append(f"❌ **RSI高水準** - RSI = {rsi:.1f}（調整の可能性を示唆）")
                else:
                    reasons.append(f"⚪ **RSI中程度** - RSI = {rsi:.1f}（中立）")
        
        # ボリンジャーバンド
        if all(col in df.columns for col in ['Close', 'BB_upper', 'BB_lower']):
            close = price_data['Close']
            bb_upper = price_data['BB_upper']
            bb_lower = price_data['BB_lower']
            
            if all(pd.notna([close, bb_upper, bb_lower])):
                if close < bb_lower:
                    reasons.append("✅ **下側バンド突破** - ボリンジャーバンド下限を下回る")
                elif close > bb_upper:
                    reasons.append("❌ **上側バンド突破** - ボリンジャーバンド上限を上回る")
        
        # MACD
        if all(col in df.columns for col in ['MACD', 'MACD_signal']):
            macd = price_data['MACD']
            macd_signal = price_data['MACD_signal']
            
            if pd.notna(macd) and pd.notna(macd_signal):
                if macd > macd_signal:
                    reasons.append("✅ **MACD上向き** - 買い勢いを示唆")
                else:
                    reasons.append("❌ **MACD下向き** - 売り勢いを示唆")
        
        explanation['reasons'] = reasons
        
        return explanation
    
    def get_signal_statistics(self, signals: pd.DataFrame) -> Dict[str, any]:
        """
        シグナル統計情報を取得
        
        Args:
            signals: シグナルDataFrame
            
        Returns:
            dict: 統計情報
        """
        total_signals = len(signals)
        buy_signals = (signals['signal'] == 1).sum()
        sell_signals = (signals['signal'] == -1).sum()
        neutral_signals = (signals['signal'] == 0).sum()
        
        return {
            'total_signals': total_signals,
            'buy_signals': buy_signals,
            'sell_signals': sell_signals,
            'neutral_signals': neutral_signals,
            'buy_ratio': buy_signals / total_signals * 100 if total_signals > 0 else 0,
            'sell_ratio': sell_signals / total_signals * 100 if total_signals > 0 else 0,
            'avg_buy_score': signals[signals['signal'] == 1]['buy_score'].mean() if buy_signals > 0 else 0,
            'avg_sell_score': signals[signals['signal'] == -1]['sell_score'].mean() if sell_signals > 0 else 0
        }
    
    def detect_signal_clusters(self, signals: pd.DataFrame, window: int = 5) -> List[Dict]:
        """
        シグナルクラスター（連続するシグナル）を検出
        
        Args:
            signals: シグナルDataFrame
            window: 検出ウィンドウ
            
        Returns:
            List[Dict]: クラスター情報のリスト
        """
        clusters = []
        
        for i in range(len(signals) - window + 1):
            window_signals = signals['signal'].iloc[i:i+window]
            
            # 買いシグナルクラスター
            if (window_signals == 1).sum() >= window * 0.6:
                clusters.append({
                    'type': 'buy_cluster',
                    'start_index': i,
                    'end_index': i + window - 1,
                    'strength': (window_signals == 1).sum() / window
                })
            
            # 売りシグナルクラスター
            if (window_signals == -1).sum() >= window * 0.6:
                clusters.append({
                    'type': 'sell_cluster',
                    'start_index': i,
                    'end_index': i + window - 1,
                    'strength': (window_signals == -1).sum() / window
                })
        
        return clusters
    
    def optimize_thresholds(self, signals: pd.DataFrame, returns: pd.Series) -> Dict[str, float]:
        """
        シグナル閾値を最適化
        
        Args:
            signals: シグナルDataFrame
            returns: リターンSeries
            
        Returns:
            dict: 最適化された閾値
        """
        best_buy_threshold = SIGNAL_THRESHOLDS['buy_threshold']
        best_sell_threshold = SIGNAL_THRESHOLDS['sell_threshold']
        best_sharpe = -np.inf
        
        # グリッドサーチで最適な閾値を探索
        for buy_threshold in np.arange(1.0, 4.0, 0.5):
            for sell_threshold in np.arange(1.0, 4.0, 0.5):
                # 新しい閾値でシグナルを再計算
                test_signals = signals.copy()
                test_signals['signal'] = 0
                test_signals.loc[test_signals['buy_score'] >= buy_threshold, 'signal'] = 1
                test_signals.loc[test_signals['sell_score'] >= sell_threshold, 'signal'] = -1
                
                # シンプルなリターン計算
                signal_returns = test_signals['signal'].shift(1) * returns
                if signal_returns.std() > 0:
                    sharpe = signal_returns.mean() / signal_returns.std()
                    if sharpe > best_sharpe:
                        best_sharpe = sharpe
                        best_buy_threshold = buy_threshold
                        best_sell_threshold = sell_threshold
        
        return {
            'buy_threshold': best_buy_threshold,
            'sell_threshold': best_sell_threshold,
            'optimized_sharpe': best_sharpe
        }
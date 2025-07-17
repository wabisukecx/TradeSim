# analysis/signals.py - 動的重み付け対応版
"""
シグナル生成機能（動的重み付け対応）
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional

from config.settings import SIGNAL_THRESHOLDS, RSI_LEVELS


class SignalGenerator:
    """シグナル生成クラス（動的重み付け対応）"""
    
    def __init__(self):
        # デフォルトの固定重み付け
        self.default_signal_weights = {
            'ma_trend': 1.0,
            'rsi': 1.0,
            'bollinger': 1.5,
            'macd': 1.5,
            'volume': 0.5
        }
        
        # 現在の重み付け設定
        self.signal_weights = self.default_signal_weights.copy()
        self.weight_mode = 'fixed'
        self.manual_weights = None
        
        # パターン検出情報（動的重み付け用）
        self.current_pattern_info = None
    
    def set_weight_mode(self, mode: str, manual_weights: Optional[Dict[str, float]] = None):
        """
        重み付けモードを設定
        
        Args:
            mode: 'fixed', 'adaptive', 'manual'のいずれか
            manual_weights: 手動重み付け（modeが'manual'の場合）
        """
        self.weight_mode = mode
        self.manual_weights = manual_weights
        
        if mode == 'fixed':
            self.signal_weights = self.default_signal_weights.copy()
        elif mode == 'manual' and manual_weights:
            self.signal_weights = manual_weights.copy()
        # adaptive modeの場合は、パターン検出時に動的に設定される
    
    def generate_signals_advanced(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        高度なシグナル生成（動的重み付け対応）
        
        Args:
            df: テクニカル指標が計算済みのDataFrame
            
        Returns:
            pd.DataFrame: シグナルが追加されたDataFrame
        """
        signals = pd.DataFrame(index=df.index)
        
        # 浮動小数点数で初期化してdtype警告を回避
        signals['buy_score'] = 0.0
        signals['sell_score'] = 0.0
        
        # 動的重み付けの場合はパターン検出を実行
        if self.weight_mode == 'adaptive':
            self._apply_adaptive_weights(df)
        
        # 現在の重み付けでシグナル生成
        signals = self._add_ma_signals(signals, df)
        signals = self._add_rsi_signals(signals, df)
        signals = self._add_bollinger_signals(signals, df)
        signals = self._add_macd_signals(signals, df)
        signals = self._add_volume_signals(signals, df)
        
        # 最終シグナル決定
        signals = self._finalize_signals(signals)
        
        return signals
    
    def _apply_adaptive_weights(self, df: pd.DataFrame):
        """動的重み付けを適用"""
        try:
            # パターン検出を試行
            from analysis.pattern_detector import MarketPatternDetector
            detector = MarketPatternDetector()
            pattern_info = detector.detect_market_pattern(df)
            
            # パターン情報を保存
            self.current_pattern_info = pattern_info
            
            # 検出されたパターンに基づいて重み付けを調整
            if pattern_info and pattern_info['confidence'] > 0.6:
                self.signal_weights = pattern_info['weights'].copy()
            else:
                # 信頼度が低い場合はデフォルト重み付けを使用
                self.signal_weights = self.default_signal_weights.copy()
                
        except ImportError:
            # パターン検出器が利用できない場合はデフォルト重み付けを使用
            self.signal_weights = self.default_signal_weights.copy()
            self.current_pattern_info = None
        except Exception as e:
            # その他のエラーの場合もデフォルト重み付けを使用
            self.signal_weights = self.default_signal_weights.copy()
            self.current_pattern_info = None
    
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
        シグナルの詳細説明を取得（動的重み付け対応）
        
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
            'reasons': [],
            'weights_breakdown': self.signal_weights.copy()  # 使用された重み付けを追加
        }
        
        # 動的重み付け情報の追加
        if self.current_pattern_info:
            explanation['pattern_info'] = {
                'pattern_name': self.current_pattern_info['pattern_info']['name'],
                'confidence': self.current_pattern_info['confidence'],
                'strategy_hint': self.current_pattern_info['pattern_info']['strategy_hint']
            }
        
        # 各指標の判断理由を追加
        reasons = []
        
        # 移動平均
        if 'MA_short' in df.columns and 'MA_long' in df.columns:
            ma_short = price_data['MA_short']
            ma_long = price_data['MA_long']
            if pd.notna(ma_short) and pd.notna(ma_long):
                weight_info = f"(重み: {self.signal_weights['ma_trend']:.1f})"
                if ma_short > ma_long:
                    reasons.append(f"✅ **上昇トレンド** - 短期平均 > 長期平均 {weight_info}")
                else:
                    reasons.append(f"❌ **下降トレンド** - 短期平均 < 長期平均 {weight_info}")
        
        # RSI
        if 'RSI' in df.columns:
            rsi = price_data['RSI']
            if pd.notna(rsi):
                weight_info = f"(重み: {self.signal_weights['rsi']:.1f})"
                if rsi < RSI_LEVELS['oversold']:
                    reasons.append(f"✅ **RSI低水準** - RSI = {rsi:.1f}（反発の可能性を示唆）{weight_info}")
                elif rsi > RSI_LEVELS['overbought']:
                    reasons.append(f"❌ **RSI高水準** - RSI = {rsi:.1f}（調整の可能性を示唆）{weight_info}")
                else:
                    reasons.append(f"⚪ **RSI中程度** - RSI = {rsi:.1f}（中立）{weight_info}")
        
        # ボリンジャーバンド
        if all(col in df.columns for col in ['Close', 'BB_upper', 'BB_lower']):
            close = price_data['Close']
            bb_upper = price_data['BB_upper']
            bb_lower = price_data['BB_lower']
            
            if all(pd.notna([close, bb_upper, bb_lower])):
                weight_info = f"(重み: {self.signal_weights['bollinger']:.1f})"
                if close < bb_lower:
                    reasons.append(f"✅ **下側バンド突破** - ボリンジャーバンド下限を下回る {weight_info}")
                elif close > bb_upper:
                    reasons.append(f"❌ **上側バンド突破** - ボリンジャーバンド上限を上回る {weight_info}")
        
        # MACD
        if all(col in df.columns for col in ['MACD', 'MACD_signal']):
            macd = price_data['MACD']
            macd_signal = price_data['MACD_signal']
            
            if pd.notna(macd) and pd.notna(macd_signal):
                weight_info = f"(重み: {self.signal_weights['macd']:.1f})"
                if macd > macd_signal:
                    reasons.append(f"✅ **MACD上向き** - 買い勢いを示唆 {weight_info}")
                else:
                    reasons.append(f"❌ **MACD下向き** - 売り勢いを示唆 {weight_info}")
        
        explanation['reasons'] = reasons
        
        return explanation
    
    def get_current_weights(self) -> Dict[str, float]:
        """現在の重み付けを取得"""
        return self.signal_weights.copy()
    
    def get_weight_mode_info(self) -> Dict[str, any]:
        """重み付けモード情報を取得"""
        return {
            'mode': self.weight_mode,
            'weights': self.signal_weights.copy(),
            'pattern_info': self.current_pattern_info
        }
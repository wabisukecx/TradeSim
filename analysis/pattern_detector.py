# analysis/pattern_detector.py - パターン検出機能
"""
市場パターン検出機能（動的重み付け用）
"""

import pandas as pd
import numpy as np
from typing import Dict, Any
from datetime import datetime

# 動的重み付け設定
DYNAMIC_WEIGHT_PROFILES = {
    'uptrend': {
        'name': '上昇トレンド',
        'description': '価格が持続的に上昇している状態',
        'strategy_hint': '移動平均とMACDを重視し、トレンドフォローを基本とする',
        'risk_level': 'medium',
        'weights': {
            'ma_trend': 0.35,
            'macd': 0.30,
            'bollinger': 0.15,
            'rsi': 0.15,
            'volume': 0.05
        }
    },
    'downtrend': {
        'name': '下降トレンド',
        'description': '価格が持続的に下降している状態',
        'strategy_hint': '移動平均とMACDを重視し、反転ポイントを慎重に判断',
        'risk_level': 'high',
        'weights': {
            'ma_trend': 0.35,
            'macd': 0.30,
            'rsi': 0.20,
            'bollinger': 0.10,
            'volume': 0.05
        }
    },
    'range': {
        'name': 'レンジ相場',
        'description': '価格が一定の範囲内で上下している状態',
        'strategy_hint': 'RSIとボリンジャーバンドを重視し、反転を狙う',
        'risk_level': 'low',
        'weights': {
            'rsi': 0.35,
            'bollinger': 0.35,
            'ma_trend': 0.15,
            'macd': 0.10,
            'volume': 0.05
        }
    },
    'transition': {
        'name': '転換期',
        'description': 'トレンドが変化している可能性がある状態',
        'strategy_hint': 'MACDを最重視し、転換点の早期検出を図る',
        'risk_level': 'high',
        'weights': {
            'macd': 0.45,
            'rsi': 0.25,
            'bollinger': 0.15,
            'ma_trend': 0.10,
            'volume': 0.05
        }
    },
    'acceleration': {
        'name': '加速相場',
        'description': '価格変動が急激に拡大している状態',
        'strategy_hint': '出来高を重視し、加速の持続性を判断',
        'risk_level': 'high',
        'weights': {
            'volume': 0.25,
            'macd': 0.30,
            'bollinger': 0.20,
            'ma_trend': 0.15,
            'rsi': 0.10
        }
    }
}


class MarketPatternDetector:
    """市場パターン検出クラス"""
    
    def __init__(self):
        self.pattern_profiles = DYNAMIC_WEIGHT_PROFILES
        
    def detect_market_pattern(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        市場パターンを検出
        
        Args:
            df: テクニカル指標が計算済みのDataFrame
            
        Returns:
            dict: パターン検出結果
        """
        if len(df) < 20:
            return self._get_default_pattern()
        
        try:
            # 各パターンのスコアを計算
            pattern_scores = {}
            
            # トレンド分析
            trend_analysis = self._analyze_trend(df)
            
            # ボラティリティ分析
            volatility_analysis = self._analyze_volatility(df)
            
            # モメンタム分析
            momentum_analysis = self._analyze_momentum(df)
            
            # 出来高分析
            volume_analysis = self._analyze_volume(df)
            
            # 各パターンのスコア計算
            pattern_scores['uptrend'] = self._calculate_uptrend_score(
                trend_analysis, momentum_analysis, volume_analysis
            )
            pattern_scores['downtrend'] = self._calculate_downtrend_score(
                trend_analysis, momentum_analysis, volume_analysis
            )
            pattern_scores['range'] = self._calculate_range_score(
                trend_analysis, volatility_analysis, momentum_analysis
            )
            pattern_scores['transition'] = self._calculate_transition_score(
                momentum_analysis, volatility_analysis
            )
            pattern_scores['acceleration'] = self._calculate_acceleration_score(
                volatility_analysis, volume_analysis, momentum_analysis
            )
            
            # 最高スコアのパターンを選択
            best_pattern = max(pattern_scores.items(), key=lambda x: x[1])
            pattern_type = best_pattern[0]
            confidence = best_pattern[1]
            
            # 信頼度が低すぎる場合はデフォルトパターンを使用
            if confidence < 0.3:
                return self._get_default_pattern()
            
            # パターン情報を構築
            pattern_info = self.pattern_profiles[pattern_type]
            
            return {
                'pattern': pattern_type,
                'pattern_info': pattern_info,
                'confidence': confidence,
                'weights': pattern_info['weights'],
                'detection_timestamp': datetime.now(),
                'analysis_details': {
                    'trend': trend_analysis,
                    'volatility': volatility_analysis,
                    'momentum': momentum_analysis,
                    'volume': volume_analysis
                },
                'pattern_scores': pattern_scores
            }
            
        except Exception as e:
            # エラー時はデフォルトパターンを返す
            return self._get_default_pattern()
    
    def _analyze_trend(self, df: pd.DataFrame) -> Dict[str, Any]:
        """トレンド分析"""
        if 'MA_short' not in df.columns or 'MA_long' not in df.columns:
            return {'direction': 'neutral', 'strength': 0.5, 'confidence': 0.0}
        
        ma_short = df['MA_short'].dropna()
        ma_long = df['MA_long'].dropna()
        
        if len(ma_short) < 10 or len(ma_long) < 10:
            return {'direction': 'neutral', 'strength': 0.5, 'confidence': 0.0}
        
        # 最近のトレンド方向
        recent_short = ma_short.tail(5).mean()
        recent_long = ma_long.tail(5).mean()
        
        # トレンドの強度（移動平均の傾き）
        short_slope = (ma_short.iloc[-1] - ma_short.iloc[-5]) / 5
        long_slope = (ma_long.iloc[-1] - ma_long.iloc[-5]) / 5
        
        if recent_short > recent_long and short_slope > 0:
            direction = 'up'
            strength = min(abs(short_slope) / ma_short.iloc[-1] * 100, 1.0)
        elif recent_short < recent_long and short_slope < 0:
            direction = 'down'
            strength = min(abs(short_slope) / ma_short.iloc[-1] * 100, 1.0)
        else:
            direction = 'neutral'
            strength = 0.5
        
        # 信頼度（移動平均の安定性）
        confidence = min(abs(recent_short - recent_long) / recent_long, 1.0) if recent_long != 0 else 0.0
        
        return {
            'direction': direction,
            'strength': strength,
            'confidence': confidence
        }
    
    def _analyze_volatility(self, df: pd.DataFrame) -> Dict[str, Any]:
        """ボラティリティ分析"""
        if 'Close' not in df.columns:
            return {'state': 'normal', 'level': 0.5, 'confidence': 0.0}
        
        returns = df['Close'].pct_change().dropna()
        
        if len(returns) < 20:
            return {'state': 'normal', 'level': 0.5, 'confidence': 0.0}
        
        # 最近のボラティリティ vs 過去のボラティリティ
        recent_vol = returns.tail(10).std()
        historical_vol = returns.std()
        
        vol_ratio = recent_vol / historical_vol if historical_vol != 0 else 1.0
        
        if vol_ratio > 1.3:
            state = 'expanding'
            level = min(vol_ratio - 1.0, 1.0)
        elif vol_ratio < 0.7:
            state = 'contracting'
            level = min(1.0 - vol_ratio, 1.0)
        else:
            state = 'normal'
            level = 0.5
        
        confidence = min(abs(vol_ratio - 1.0), 1.0)
        
        return {
            'state': state,
            'level': level,
            'confidence': confidence
        }
    
    def _analyze_momentum(self, df: pd.DataFrame) -> Dict[str, Any]:
        """モメンタム分析"""
        momentum_signals = {}
        
        # MACD分析
        if 'MACD' in df.columns and 'MACD_signal' in df.columns:
            macd = df['MACD'].dropna()
            macd_signal = df['MACD_signal'].dropna()
            
            if len(macd) >= 5 and len(macd_signal) >= 5:
                recent_macd = macd.iloc[-1]
                recent_signal = macd_signal.iloc[-1]
                
                macd_direction = 'bullish' if recent_macd > recent_signal else 'bearish'
                macd_strength = abs(recent_macd - recent_signal) / abs(recent_signal) if recent_signal != 0 else 0
                
                momentum_signals['macd'] = {
                    'direction': macd_direction,
                    'strength': min(macd_strength, 1.0)
                }
        
        # RSI分析
        if 'RSI' in df.columns:
            rsi = df['RSI'].dropna()
            
            if len(rsi) >= 5:
                recent_rsi = rsi.iloc[-1]
                
                if recent_rsi < 30:
                    rsi_signal = 'oversold'
                    rsi_strength = (30 - recent_rsi) / 30
                elif recent_rsi > 70:
                    rsi_signal = 'overbought'
                    rsi_strength = (recent_rsi - 70) / 30
                else:
                    rsi_signal = 'neutral'
                    rsi_strength = 0.5
                
                momentum_signals['rsi'] = {
                    'signal': rsi_signal,
                    'strength': rsi_strength
                }
        
        # 総合モメンタム評価
        if momentum_signals:
            # 簡単な総合判定
            overall_direction = 'neutral'
            overall_strength = 0.5
            confidence = 0.5
            
            if 'macd' in momentum_signals:
                if momentum_signals['macd']['direction'] == 'bullish':
                    overall_direction = 'bullish_momentum'
                    overall_strength = momentum_signals['macd']['strength']
                else:
                    overall_direction = 'bearish_momentum'
                    overall_strength = momentum_signals['macd']['strength']
                confidence = 0.7
        else:
            overall_direction = 'neutral'
            overall_strength = 0.5
            confidence = 0.0
        
        return {
            'direction': overall_direction,
            'strength': overall_strength,
            'confidence': confidence,
            'signals': momentum_signals
        }
    
    def _analyze_volume(self, df: pd.DataFrame) -> Dict[str, Any]:
        """出来高分析"""
        if 'Volume' not in df.columns:
            return {'trend': 'normal', 'confirmation': False, 'confidence': 0.0}
        
        volume = df['Volume'].dropna()
        
        if len(volume) < 10:
            return {'trend': 'normal', 'confirmation': False, 'confidence': 0.0}
        
        # 最近の出来高 vs 過去平均
        recent_vol = volume.tail(5).mean()
        historical_vol = volume.mean()
        
        vol_ratio = recent_vol / historical_vol if historical_vol != 0 else 1.0
        
        if vol_ratio > 1.2:
            trend = 'increasing'
            confirmation = True
        elif vol_ratio < 0.8:
            trend = 'decreasing'
            confirmation = False
        else:
            trend = 'normal'
            confirmation = True
        
        confidence = min(abs(vol_ratio - 1.0), 1.0)
        
        return {
            'trend': trend,
            'confirmation': confirmation,
            'confidence': confidence
        }
    
    def _calculate_uptrend_score(self, trend: Dict, momentum: Dict, volume: Dict) -> float:
        """上昇トレンドスコア計算"""
        score = 0.0
        
        # トレンド方向
        if trend['direction'] == 'up':
            score += 0.4 * trend['confidence']
        
        # モメンタム
        if momentum['direction'] == 'bullish_momentum':
            score += 0.3 * momentum['confidence']
        
        # 出来高確認
        if volume['confirmation'] and volume['trend'] == 'increasing':
            score += 0.3 * volume['confidence']
        
        return min(score, 1.0)
    
    def _calculate_downtrend_score(self, trend: Dict, momentum: Dict, volume: Dict) -> float:
        """下降トレンドスコア計算"""
        score = 0.0
        
        # トレンド方向
        if trend['direction'] == 'down':
            score += 0.4 * trend['confidence']
        
        # モメンタム
        if momentum['direction'] == 'bearish_momentum':
            score += 0.3 * momentum['confidence']
        
        # 出来高確認
        if volume['trend'] == 'increasing':
            score += 0.3 * volume['confidence']
        
        return min(score, 1.0)
    
    def _calculate_range_score(self, trend: Dict, volatility: Dict, momentum: Dict) -> float:
        """レンジ相場スコア計算"""
        score = 0.0
        
        # トレンドレス
        if trend['direction'] == 'neutral':
            score += 0.4
        
        # 低ボラティリティ
        if volatility['state'] == 'contracting':
            score += 0.3 * volatility['confidence']
        
        # 中立モメンタム
        if momentum['direction'] == 'neutral':
            score += 0.3
        
        return min(score, 1.0)
    
    def _calculate_transition_score(self, momentum: Dict, volatility: Dict) -> float:
        """転換期スコア計算"""
        score = 0.0
        
        # モメンタム変化
        if momentum['confidence'] > 0.5:
            score += 0.5 * momentum['confidence']
        
        # ボラティリティ拡大
        if volatility['state'] == 'expanding':
            score += 0.5 * volatility['confidence']
        
        return min(score, 1.0)
    
    def _calculate_acceleration_score(self, volatility: Dict, volume: Dict, momentum: Dict) -> float:
        """加速相場スコア計算"""
        score = 0.0
        
        # ボラティリティ拡大
        if volatility['state'] == 'expanding':
            score += 0.4 * volatility['confidence']
        
        # 出来高増加
        if volume['trend'] == 'increasing':
            score += 0.4 * volume['confidence']
        
        # 強いモメンタム
        if momentum['strength'] > 0.7:
            score += 0.2
        
        return min(score, 1.0)
    
    def _get_default_pattern(self) -> Dict[str, Any]:
        """デフォルトパターンを取得"""
        default_weights = {
            'ma_trend': 0.2,
            'rsi': 0.2,
            'bollinger': 0.3,
            'macd': 0.3,
            'volume': 0.1
        }
        
        return {
            'pattern': 'balanced',
            'pattern_info': {
                'name': 'バランス型',
                'description': 'バランスの取れた重み付け',
                'strategy_hint': '全指標をバランスよく活用',
                'risk_level': 'medium'
            },
            'confidence': 0.5,
            'weights': default_weights,
            'detection_timestamp': datetime.now(),
            'analysis_details': {},
            'pattern_scores': {}
        }
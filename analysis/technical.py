# analysis/technical.py
"""
テクニカル分析機能
"""

import pandas as pd
import ta
from typing import Dict, Any

from config.settings import TECHNICAL_DEFAULTS


class TechnicalAnalyzer:
    """テクニカル分析クラス"""
    
    def __init__(self):
        self.indicators = {}
    
    def calculate_indicators(self, df: pd.DataFrame, **params) -> pd.DataFrame:
        """
        テクニカル指標を計算
        
        Args:
            df: 株価データのDataFrame
            params: テクニカル指標のパラメータ
            
        Returns:
            pd.DataFrame: 指標が追加されたDataFrame
        """
        # パラメータのデフォルト値設定
        short_window = params.get('short_ma', TECHNICAL_DEFAULTS['short_ma'])
        long_window = params.get('long_ma', TECHNICAL_DEFAULTS['long_ma'])
        rsi_window = params.get('rsi_period', TECHNICAL_DEFAULTS['rsi_period'])
        bb_window = params.get('bb_period', TECHNICAL_DEFAULTS['bb_period'])
        bb_std = params.get('bb_std', TECHNICAL_DEFAULTS['bb_std'])
        
        # DataFrameをコピーして元データを保護
        df_copy = df.copy()
        
        # 移動平均線
        df_copy['MA_short'] = ta.trend.sma_indicator(df_copy['Close'], window=short_window)
        df_copy['MA_long'] = ta.trend.sma_indicator(df_copy['Close'], window=long_window)
        
        # RSI（相対力指数）
        df_copy['RSI'] = ta.momentum.rsi(df_copy['Close'], window=rsi_window)
        
        # ボリンジャーバンド
        bb = ta.volatility.BollingerBands(df_copy['Close'], window=bb_window, window_dev=bb_std)
        df_copy['BB_upper'] = bb.bollinger_hband()
        df_copy['BB_middle'] = bb.bollinger_mavg()
        df_copy['BB_lower'] = bb.bollinger_lband()
        
        # MACD（移動平均収束拡散）
        macd = ta.trend.MACD(df_copy['Close'])
        df_copy['MACD'] = macd.macd()
        df_copy['MACD_signal'] = macd.macd_signal()
        df_copy['MACD_diff'] = macd.macd_diff()
        
        # 出来高移動平均
        df_copy['Volume_MA'] = df_copy['Volume'].rolling(window=20).mean()
        
        # ATR（Average True Range）
        df_copy['ATR'] = ta.volatility.average_true_range(
            df_copy['High'], df_copy['Low'], df_copy['Close']
        )
        
        # 指標情報を保存
        self.indicators = {
            'short_ma': short_window,
            'long_ma': long_window,
            'rsi_period': rsi_window,
            'bb_period': bb_window,
            'bb_std': bb_std
        }
        
        return df_copy
    
    def get_indicator_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        指標のサマリー情報を取得
        
        Args:
            df: 指標が計算済みのDataFrame
            
        Returns:
            dict: 指標サマリー
        """
        if df.empty:
            return {}
        
        latest_data = df.iloc[-1]
        
        summary = {
            # 現在の価格情報
            'current_price': latest_data['Close'],
            'current_volume': latest_data['Volume'],
            
            # 移動平均
            'ma_short': latest_data.get('MA_short'),
            'ma_long': latest_data.get('MA_long'),
            'ma_trend': 'uptrend' if latest_data.get('MA_short', 0) > latest_data.get('MA_long', 0) else 'downtrend',
            
            # RSI
            'rsi': latest_data.get('RSI'),
            'rsi_status': self._get_rsi_status(latest_data.get('RSI')),
            
            # ボリンジャーバンド
            'bb_upper': latest_data.get('BB_upper'),
            'bb_middle': latest_data.get('BB_middle'),
            'bb_lower': latest_data.get('BB_lower'),
            'bb_position': self._get_bb_position(latest_data),
            
            # MACD
            'macd': latest_data.get('MACD'),
            'macd_signal': latest_data.get('MACD_signal'),
            'macd_trend': 'bullish' if latest_data.get('MACD', 0) > latest_data.get('MACD_signal', 0) else 'bearish',
            
            # 出来高
            'volume_trend': 'high' if latest_data.get('Volume', 0) > latest_data.get('Volume_MA', 0) else 'low',
            
            # ATR
            'atr': latest_data.get('ATR'),
            
            # 価格変動率（前日比）
            'price_change_pct': self._calculate_price_change(df) if len(df) > 1 else 0.0
        }
        
        return summary
    
    def _get_rsi_status(self, rsi: float) -> str:
        """RSIのステータスを取得"""
        if pd.isna(rsi):
            return 'unknown'
        elif rsi < 30:
            return 'oversold'
        elif rsi > 70:
            return 'overbought'
        else:
            return 'neutral'
    
    def _get_bb_position(self, data: pd.Series) -> str:
        """ボリンジャーバンドでの価格位置を取得"""
        price = data.get('Close')
        bb_upper = data.get('BB_upper')
        bb_lower = data.get('BB_lower')
        
        if pd.isna(price) or pd.isna(bb_upper) or pd.isna(bb_lower):
            return 'unknown'
        
        if price > bb_upper:
            return 'above_upper'
        elif price < bb_lower:
            return 'below_lower'
        else:
            return 'within_bands'
    
    def _calculate_price_change(self, df: pd.DataFrame) -> float:
        """価格変動率を計算"""
        if len(df) < 2:
            return 0.0
        
        current_price = df['Close'].iloc[-1]
        prev_price = df['Close'].iloc[-2]
        
        if prev_price == 0:
            return 0.0
        
        return ((current_price / prev_price) - 1) * 100
    
    def calculate_support_resistance(self, df: pd.DataFrame, window: int = 20) -> Dict[str, float]:
        """
        サポート・レジスタンスレベルを計算
        
        Args:
            df: 株価データ
            window: 計算期間
            
        Returns:
            dict: サポート・レジスタンスレベル
        """
        if len(df) < window:
            return {'support': 0.0, 'resistance': 0.0}
        
        recent_data = df.tail(window)
        
        support = recent_data['Low'].min()
        resistance = recent_data['High'].max()
        
        return {
            'support': support,
            'resistance': resistance,
            'current_price': df['Close'].iloc[-1]
        }
    
    def get_trend_strength(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        トレンド強度を計算
        
        Args:
            df: 指標が計算済みのDataFrame
            
        Returns:
            dict: トレンド強度情報
        """
        if len(df) < 20:
            return {'strength': 0, 'direction': 'neutral'}
        
        # 移動平均のトレンド
        ma_short = df['MA_short'].dropna()
        ma_long = df['MA_long'].dropna()
        
        if len(ma_short) < 10 or len(ma_long) < 10:
            return {'strength': 0, 'direction': 'neutral'}
        
        # トレンドの方向
        short_trend = 1 if ma_short.iloc[-1] > ma_short.iloc[-10] else -1
        long_trend = 1 if ma_long.iloc[-1] > ma_long.iloc[-10] else -1
        
        # トレンドの一致度
        if short_trend == long_trend:
            strength = 3 if short_trend == 1 else -3
            direction = 'strong_uptrend' if short_trend == 1 else 'strong_downtrend'
        else:
            strength = 1 if short_trend == 1 else -1
            direction = 'weak_uptrend' if short_trend == 1 else 'weak_downtrend'
        
        return {
            'strength': strength,
            'direction': direction,
            'short_trend': short_trend,
            'long_trend': long_trend
        }
    
    def detect_patterns(self, df: pd.DataFrame) -> Dict[str, bool]:
        """
        チャートパターンを検出
        
        Args:
            df: 株価データ
            
        Returns:
            dict: 検出されたパターン
        """
        patterns = {
            'golden_cross': False,
            'dead_cross': False,
            'rsi_divergence': False,
            'breakout': False
        }
        
        if len(df) < 5:
            return patterns
        
        # ゴールデンクロス・デッドクロスの検出
        if 'MA_short' in df.columns and 'MA_long' in df.columns:
            ma_short = df['MA_short'].dropna()
            ma_long = df['MA_long'].dropna()
            
            if len(ma_short) >= 2 and len(ma_long) >= 2:
                # 直近でクロスしたかチェック
                if (ma_short.iloc[-1] > ma_long.iloc[-1] and 
                    ma_short.iloc[-2] <= ma_long.iloc[-2]):
                    patterns['golden_cross'] = True
                
                if (ma_short.iloc[-1] < ma_long.iloc[-1] and 
                    ma_short.iloc[-2] >= ma_long.iloc[-2]):
                    patterns['dead_cross'] = True
        
        # ブレイクアウトの検出（ボリンジャーバンド）
        if 'BB_upper' in df.columns and 'BB_lower' in df.columns:
            recent_data = df.tail(3)
            if len(recent_data) >= 2:
                if (recent_data['Close'].iloc[-1] > recent_data['BB_upper'].iloc[-1] and
                    recent_data['Close'].iloc[-2] <= recent_data['BB_upper'].iloc[-2]):
                    patterns['breakout'] = True
        
        return patterns
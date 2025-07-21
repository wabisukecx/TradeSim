# data/validators.py
"""
データ検証機能
"""

import pandas as pd
import streamlit as st
from typing import Optional


class DataValidator:
    """データ検証クラス"""
    
    @staticmethod
    def validate_stock_data(df: Optional[pd.DataFrame], symbol: str) -> bool:
        """
        株価データの妥当性検証
        
        Args:
            df: 株価データのDataFrame
            symbol: 銘柄コード
            
        Returns:
            bool: 検証結果（True: 正常, False: 異常）
            
        Raises:
            ValueError: データに重大な問題がある場合
        """
        if df is None:
            raise ValueError(f"データが取得できませんでした: {symbol}")
        
        if df.empty:
            raise ValueError(f"データが空です: {symbol}")
        
        # 必要な列の存在確認
        required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"必要なデータ列が不足しています: {missing_columns}")
        
        # 欠損値チェック
        close_na_ratio = df['Close'].isna().sum() / len(df)
        if close_na_ratio > 0.1:  # 10%以上欠損していたらエラー
            raise ValueError(f"欠損データが多すぎます（{close_na_ratio:.1%}）")
        
        # 異常値検出
        close_prices = df['Close'].dropna()
        if len(close_prices) == 0:
            raise ValueError("有効な価格データがありません")
        
        # 価格の異常値チェック（極端な変動）
        daily_returns = close_prices.pct_change().dropna()
        extreme_moves = daily_returns.abs() > 0.5  # 50%を超える日次変動
        if extreme_moves.sum() > len(daily_returns) * 0.05:
            st.warning(f"⚠️ データに異常な価格変動が検出されました。結果の解釈には注意してください。")
        
        # ボリュームの妥当性チェック
        if 'Volume' in df.columns:
            zero_volume_ratio = (df['Volume'] == 0).sum() / len(df)
            if zero_volume_ratio > 0.3:
                st.warning(f"⚠️ 出来高データに多くの0が含まれています（{zero_volume_ratio:.1%}）")
        
        return True
    
    @staticmethod
    def validate_symbol_format(symbol: str) -> bool:
        """
        銘柄コードのフォーマット検証
        
        Args:
            symbol: 銘柄コード
            
        Returns:
            bool: フォーマットが正しいかどうか
        """
        if not symbol or len(symbol.strip()) == 0:
            return False
        
        symbol = symbol.strip().upper()
        
        # 基本的なフォーマットチェック
        if len(symbol) < 1 or len(symbol) > 10:
            return False
        
        # 日本株のフォーマット（例: 7203.T）
        if symbol.endswith('.T'):
            code_part = symbol[:-2]
            return code_part.isdigit() and len(code_part) == 4
        
        # 米国株のフォーマット（例: AAPL）
        if symbol.isalpha() and 1 <= len(symbol) <= 5:
            return True
        
        # その他の市場（基本的なチェックのみ）
        return symbol.replace('.', '').replace('-', '').isalnum()
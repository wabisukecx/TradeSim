# data/cache_manager.py - 最終修正版
"""
キャッシュ管理機能
"""

import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime
from typing import Optional, Tuple


class CacheManager:
    """キャッシュ管理クラス"""
    
    @staticmethod
    @st.cache_data(ttl=3600)  # 1時間キャッシュ
    def fetch_stock_data_cached(symbol: str, start: datetime, end: datetime) -> Tuple[Optional[pd.DataFrame], Optional[dict]]:
        """
        キャッシュ機能付き株価データ取得
        
        Args:
            symbol: 銘柄コード
            start: 開始日
            end: 終了日
            
        Returns:
            Tuple[DataFrame, dict]: 株価データと企業情報のタプル
        """
        from .stock_fetcher import StockDataFetcher
        fetcher = StockDataFetcher()
        return fetcher.fetch_stock_data(symbol, start, end)
    
    @staticmethod
    @st.cache_data(ttl=1800)  # 30分キャッシュ
    def get_current_price_cached(symbol: str) -> float:
        """
        キャッシュ機能付き現在価格取得
        
        Args:
            symbol: 銘柄コード
            
        Returns:
            float: 現在価格
        """
        from .stock_fetcher import StockDataFetcher
        fetcher = StockDataFetcher()
        return fetcher.get_current_price(symbol)
    
    @staticmethod
    def clear_cache() -> None:
        """全キャッシュをクリア"""
        st.cache_data.clear()


# === app.py用のエイリアス関数 ===
@st.cache_data(ttl=3600)
def cache_stock_data(symbol: str, start: datetime, end: datetime) -> Tuple[Optional[pd.DataFrame], Optional[dict]]:
    """
    キャッシュ機能付き株価データ取得（app.py用エイリアス）
    
    Args:
        symbol: 銘柄コード
        start: 開始日
        end: 終了日
        
    Returns:
        Tuple[DataFrame, dict]: 株価データと企業情報のタプル
    """
    try:
        stock = yf.Ticker(symbol)
        df = stock.history(start=start, end=end)
        info = stock.info
        
        # 基本的なデータ検証
        if df.empty:
            return None, None
        
        return df, info
    except Exception as e:
        print(f"データ取得エラー: {e}")
        return None, None


# === portfolio用のエイリアス関数 ===
@st.cache_data(ttl=1800)
def cache_current_price(symbol: str) -> float:
    """
    キャッシュ機能付き現在価格取得（portfolio用エイリアス）
    
    Args:
        symbol: 銘柄コード
        
    Returns:
        float: 現在価格
    """
    try:
        stock = yf.Ticker(symbol)
        info = stock.info
        current_price = info.get('currentPrice', info.get('regularMarketPrice', 0))
        
        # 価格が0の場合は履歴データから取得を試行
        if current_price == 0:
            hist = stock.history(period="1d")
            if not hist.empty:
                current_price = hist['Close'].iloc[-1]
        
        return float(current_price) if current_price else 0.0
    except Exception as e:
        print(f"価格取得エラー: {e}")
        return 0.0


# === 追加のキャッシュ関数 ===
@st.cache_data(ttl=86400)  # 24時間キャッシュ
def cache_company_info(symbol: str) -> Optional[dict]:
    """
    キャッシュ機能付き企業情報取得
    
    Args:
        symbol: 銘柄コード
        
    Returns:
        dict: 企業情報
    """
    try:
        stock = yf.Ticker(symbol)
        return stock.info
    except Exception as e:
        print(f"企業情報取得エラー: {e}")
        return None


# === デバッグ用関数 ===
def test_cache_functions():
    """キャッシュ関数のテスト"""
    print("🔍 キャッシュ関数テスト開始...")
    
    # cache_current_price のテスト
    try:
        price = cache_current_price("AAPL")
        print(f"✅ cache_current_price('AAPL') = {price}")
    except Exception as e:
        print(f"❌ cache_current_price エラー: {e}")
    
    # cache_stock_data のテスト
    try:
        from datetime import datetime, timedelta
        start = datetime.now() - timedelta(days=30)
        end = datetime.now()
        df, info = cache_stock_data("AAPL", start, end)
        print(f"✅ cache_stock_data('AAPL') = {len(df) if df is not None else 0}行")
    except Exception as e:
        print(f"❌ cache_stock_data エラー: {e}")
    
    print("🎯 キャッシュ関数テスト完了")


if __name__ == "__main__":
    test_cache_functions()
# data/stock_fetcher.py - 修正版（人気銘柄メソッド削除）
"""
株価データ取得機能
"""

import yfinance as yf
import requests
import streamlit as st
from typing import Optional, Tuple, List, Dict
from datetime import datetime

from .validators import DataValidator


class StockDataFetcher:
    """株価データ取得クラス"""
    
    def __init__(self):
        self.validator = DataValidator()
    
    def fetch_stock_data(self, symbol: str, start: datetime, end: datetime) -> Tuple[Optional[object], Optional[dict]]:
        """
        株価データと企業情報を取得
        
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
            
            # データ検証
            self.validator.validate_stock_data(df, symbol)
            
            return df, info
            
        except ValueError as ve:
            st.error(f"❌ データ検証エラー: {ve}")
            return None, None
        except Exception as e:
            st.error(f"❌ データ取得エラー: {e}")
            return None, None
    
    def get_current_price(self, symbol: str) -> float:
        """現在価格を取得"""
        try:
            stock = yf.Ticker(symbol)
            info = stock.info
            return info.get('currentPrice', info.get('regularMarketPrice', 0))
        except:
            return 0.0


class LocalStockSearch:
    """ローカル銘柄検索クラス"""
    
    def __init__(self):
        self.stock_dict = {
            # 日本の主要銘柄
            "トヨタ": "7203.T", "toyota": "7203.T", "トヨタ自動車": "7203.T",
            "ソニー": "6758.T", "sony": "6758.T", "ソニーグループ": "6758.T",
            "任天堂": "7974.T", "nintendo": "7974.T",
            "ホンダ": "7267.T", "honda": "7267.T", "本田技研": "7267.T",
            "日産": "7201.T", "nissan": "7201.T", "日産自動車": "7201.T",
            "ソフトバンク": "9984.T", "softbank": "9984.T",
            "楽天": "4755.T", "rakuten": "4755.T",
            "ユニクロ": "9983.T", "ファーストリテイリング": "9983.T",
            "キーエンス": "6861.T", "keyence": "6861.T",
            
            # 米国の主要銘柄
            "apple": "AAPL", "アップル": "AAPL", "iphone": "AAPL",
            "microsoft": "MSFT", "マイクロソフト": "MSFT", "windows": "MSFT",
            "google": "GOOGL", "グーグル": "GOOGL", "alphabet": "GOOGL",
            "amazon": "AMZN", "アマゾン": "AMZN",
            "tesla": "TSLA", "テスラ": "TSLA",
            "nvidia": "NVDA", "エヌビディア": "NVDA",
            "meta": "META", "facebook": "META", "フェイスブック": "META",
            "netflix": "NFLX", "ネットフリックス": "NFLX",
            "disney": "DIS", "ディズニー": "DIS",
            "nike": "NKE", "ナイキ": "NKE",
        }
    
    def search(self, keyword: str) -> List[Dict[str, str]]:
        """
        キーワードから銘柄コードを検索
        
        Args:
            keyword: 検索キーワード
            
        Returns:
            List[Dict]: 検索結果のリスト
        """
        keyword_lower = keyword.lower().strip()
        results = []
        
        # 完全一致
        if keyword_lower in self.stock_dict:
            symbol = self.stock_dict[keyword_lower]
            results.append({
                'symbol': symbol,
                'name': keyword,
                'match_type': '完全一致'
            })
        
        # 部分一致
        for name, symbol in self.stock_dict.items():
            if keyword_lower in name.lower() and keyword_lower != name.lower():
                results.append({
                    'symbol': symbol,
                    'name': name,
                    'match_type': '部分一致'
                })
        
        return results[:5]  # 上位5件


class AlphaVantageSearch:
    """Alpha Vantage API銘柄検索クラス"""
    
    @staticmethod
    def search(keyword: str, api_key: str) -> List[Dict[str, str]]:
        """
        Alpha Vantage APIで銘柄検索
        
        Args:
            keyword: 検索キーワード
            api_key: API Key
            
        Returns:
            List[Dict]: 検索結果のリスト
        """
        if not api_key:
            return []
        
        try:
            url = "https://www.alphavantage.co/query"
            params = {
                'function': 'SYMBOL_SEARCH',
                'keywords': keyword,
                'apikey': api_key
            }
            
            response = requests.get(url, params=params)
            data = response.json()
            
            if 'bestMatches' in data:
                results = []
                for match in data['bestMatches']:
                    results.append({
                        'symbol': match.get('1. symbol', ''),
                        'name': match.get('2. name', ''),
                        'region': match.get('4. region', ''),
                        'match_type': 'API検索'
                    })
                return results[:5]
            return []
        except Exception:
            return []


def get_combined_search_results(keyword: str, api_key: Optional[str] = None) -> List[Dict[str, str]]:
    """
    ローカル検索とAPI検索の結果を統合
    
    Args:
        keyword: 検索キーワード
        api_key: Alpha Vantage API Key（オプション）
        
    Returns:
        List[Dict]: 統合された検索結果
    """
    local_searcher = LocalStockSearch()
    local_results = local_searcher.search(keyword)
    
    api_results = []
    if api_key:
        api_results = AlphaVantageSearch.search(keyword, api_key)
    
    # 結果をまとめる
    all_results = local_results + api_results
    
    # 重複除去
    seen_symbols = set()
    unique_results = []
    for result in all_results:
        symbol = result['symbol']
        if symbol not in seen_symbols:
            seen_symbols.add(symbol)
            unique_results.append(result)
    
    return unique_results
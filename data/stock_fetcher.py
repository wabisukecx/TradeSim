# data/stock_fetcher.py - JQuants API完全対応版
"""
株価データ取得機能（JQuants API完全対応版）
"""

import yfinance as yf
import requests
import streamlit as st
import time
import json
from typing import Optional, Tuple, List, Dict
from datetime import datetime

try:
    from .validators import DataValidator
except ImportError:
    # 相対インポートが失敗した場合の対応
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from validators import DataValidator


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


class JQuantsSearch:
    """JQuants API検索クラス（日本株専用）"""
    
    def __init__(self):
        self.auth_token = None
        self.token_expires = None
        self.base_url = "https://api.jquants.com/v1"
    
    def _get_auth_token(self, email: str, password: str) -> bool:
        """
        JQuants API認証トークンを取得（2段階認証対応）
        
        Args:
            email: JQuantsメールアドレス
            password: JQuantsパスワード
            
        Returns:
            bool: 認証成功フラグ
        """
        try:
            # トークンキャッシュチェック
            if self.auth_token and self.token_expires and time.time() < self.token_expires:
                return True
            
            # ステップ1: リフレッシュトークン取得
            auth_url = f"{self.base_url}/token/auth_user"
            auth_data = {
                "mailaddress": email,
                "password": password
            }
            
            # 正しいヘッダーとデータ形式で送信
            headers = {"Content-Type": "application/json"}
            response = requests.post(
                auth_url, 
                data=json.dumps(auth_data), 
                headers=headers, 
                timeout=10
            )
            
            if response.status_code != 200:
                st.error(f"🔐 JQuantsリフレッシュトークン取得エラー: {response.status_code}")
                if response.status_code == 400:
                    st.error("⚠️ メールアドレスまたはパスワードが正しくありません。")
                elif response.status_code == 401:
                    st.error("⚠️ 認証情報が無効です。JQuantsアカウントが有効か確認してください。")
                return False
            
            refresh_token = response.json().get("refreshToken")
            if not refresh_token:
                st.error("🔐 リフレッシュトークンの取得に失敗しました")
                return False
            
            # ステップ2: IDトークン取得
            id_token_url = f"{self.base_url}/token/auth_refresh?refreshtoken={refresh_token}"
            id_response = requests.post(id_token_url, timeout=10)
            
            if id_response.status_code != 200:
                st.error(f"🔐 JQuantsIDトークン取得エラー: {id_response.status_code}")
                return False
            
            id_token = id_response.json().get("idToken")
            if not id_token:
                st.error("🔐 IDトークンの取得に失敗しました")
                return False
            
            # IDトークンを保存（24時間有効）
            self.auth_token = id_token
            self.token_expires = time.time() + 86400  # 24時間有効
            
            st.success("✅ JQuants認証成功")
            return True
                
        except Exception as e:
            st.error(f"🔐 JQuants認証例外: {str(e)}")
            return False
    
    def search(self, keyword: str, email: str, password: str) -> List[Dict[str, str]]:
        """
        JQuants APIで日本株を検索
        
        Args:
            keyword: 検索キーワード
            email: JQuantsメールアドレス
            password: JQuantsパスワード
            
        Returns:
            List[Dict]: 検索結果のリスト
        """
        try:
            # 認証（IDトークン取得）
            if not self._get_auth_token(email, password):
                st.warning("⚠️ JQuants API認証に失敗しました。メールアドレスとパスワードを確認してください。")
                return []
            
            # 銘柄マスター取得
            list_url = f"{self.base_url}/listed/info"
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            st.info("📡 JQuants APIから銘柄情報を取得中...")
            response = requests.get(list_url, headers=headers, timeout=30)
            
            if response.status_code != 200:
                st.error(f"🔍 JQuants API検索エラー: {response.status_code}")
                if response.status_code == 401:
                    st.error("⚠️ 認証トークンが無効です。再認証を試してください。")
                elif response.status_code == 403:
                    st.error("⚠️ API利用権限がありません。プランを確認してください。")
                return []
            
            data = response.json()
            companies = data.get("info", [])
            
            if not companies:
                st.warning("⚠️ 銘柄情報の取得に失敗しました")
                return []
            
            st.success(f"✅ {len(companies)}社の銘柄情報を取得完了")
            
            # キーワードで検索
            keyword_lower = keyword.lower()
            results = []
            
            for company in companies:
                symbol = company.get("Code", "")
                name_jp = company.get("CompanyName", "")
                name_en = company.get("CompanyNameEnglish", "")
                market = company.get("MarketCode", "")
                sector = company.get("Sector33Code", "")
                
                # マッチング（日本語名、英語名、コード）
                match_score = 0
                match_type = ""
                
                if keyword_lower in name_jp.lower():
                    match_score = 3
                    match_type = "日本語社名一致"
                elif keyword_lower in name_en.lower():
                    match_score = 2
                    match_type = "英語社名一致"
                elif keyword_lower in symbol.lower():
                    match_score = 1
                    match_type = "銘柄コード一致"
                
                if match_score > 0:
                    # 東証コードに変換（銘柄コードの正規化）
                    if symbol and symbol.isdigit():
                        # JQuants APIの銘柄コードは5桁の場合があるため4桁に正規化
                        if len(symbol) == 5:
                            # 5桁の場合は最初の4桁を使用
                            symbol_normalized = symbol[:4]
                        elif len(symbol) == 4:
                            symbol_normalized = symbol
                        else:
                            # その他の桁数の場合は先頭4桁または後ろから4桁
                            symbol_normalized = symbol[:4] if len(symbol) > 4 else symbol.zfill(4)
                        symbol_with_suffix = f"{symbol_normalized}.T"
                    else:
                        symbol_with_suffix = symbol
                    
                    # 市場名変換
                    market_name = {
                        "0101": "東証プライム",
                        "0102": "東証スタンダード", 
                        "0103": "東証グロース",
                        "0104": "東証その他"
                    }.get(market, "東証")
                    
                    results.append({
                        'symbol': symbol_with_suffix,
                        'name': name_jp,
                        'name_en': name_en or "N/A",
                        'market': market_name,
                        'sector': sector,
                        'match_type': f'JQuants検索({match_type})',
                        'match_score': match_score
                    })
            
            # スコア順に並び替えて上位5件
            results.sort(key=lambda x: x['match_score'], reverse=True)
            
            if results:
                st.success(f"🎯 「{keyword}」で{len(results[:5])}件の結果を発見")
            else:
                st.warning(f"🔍 「{keyword}」に一致する銘柄が見つかりませんでした")
            
            return results[:5]
            
        except Exception as e:
            st.error(f"🔍 JQuants検索例外: {str(e)}")
            return []


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
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            # エラーチェック
            if 'Error Message' in data:
                st.error(f"🌍 Alpha Vantage API エラー: {data['Error Message']}")
                return []
            
            if 'Note' in data:
                st.warning("⚠️ Alpha Vantage API制限に達しました。しばらく待ってから再試行してください。")
                return []
            
            if 'bestMatches' in data:
                results = []
                for match in data['bestMatches']:
                    symbol = match.get('1. symbol', '')
                    name = match.get('2. name', '')
                    region = match.get('4. region', '')
                    currency = match.get('8. currency', 'USD')
                    
                    # 通貨から取引所を推定
                    exchange = AlphaVantageSearch._get_exchange_from_currency(currency, region)
                    
                    results.append({
                        'symbol': symbol,
                        'name': name,
                        'region': region,
                        'currency': currency,
                        'exchange': exchange,
                        'match_type': 'Alpha Vantage検索',
                        'match_score': 1  # Alpha Vantageは全て同じスコア
                    })
                return results[:5]
            return []
        except Exception as e:
            st.error(f"🌍 Alpha Vantage検索例外: {str(e)}")
            return []
    
    @staticmethod
    def _get_exchange_from_currency(currency: str, region: str) -> str:
        """通貨・地域から取引所名を推定"""
        if currency == 'USD':
            return 'NASDAQ/NYSE'
        elif currency == 'JPY':
            return '東京証券取引所'
        elif currency == 'EUR':
            return 'EURONEXT'
        elif currency == 'GBP':
            return 'London Stock Exchange'
        elif currency == 'HKD':
            return 'Hong Kong Stock Exchange'
        else:
            return f'{region} Exchange'


def _fallback_search(keyword: str) -> List[Dict[str, str]]:
    """
    フォールバック検索（API無し時の基本検索）
    
    Args:
        keyword: 検索キーワード
        
    Returns:
        List[Dict]: 検索結果（空または基本的な例）
    """
    # 一般的な銘柄の例を提供
    common_stocks = {
        'apple': 'AAPL',
        'microsoft': 'MSFT', 
        'google': 'GOOGL',
        'amazon': 'AMZN',
        'tesla': 'TSLA',
        'トヨタ': '7203.T',
        'ソニー': '6758.T',
        'ソフトバンク': '9984.T',
        '任天堂': '7974.T'
    }
    
    keyword_lower = keyword.lower()
    results = []
    
    for name, symbol in common_stocks.items():
        if keyword_lower in name.lower():
            results.append({
                'symbol': symbol,
                'name': name,
                'match_type': '基本検索',
                'match_score': 1
            })
    
    return results[:3]


def get_combined_search_results(keyword: str, 
                               alpha_vantage_key: Optional[str] = None,
                               jquants_config: Optional[Dict[str, str]] = None) -> List[Dict[str, str]]:
    """
    統合検索機能（JQuants + Alpha Vantage + フォールバック）
    
    Args:
        keyword: 検索キーワード
        alpha_vantage_key: Alpha Vantage API Key（オプション）
        jquants_config: JQuants設定 {"email": "xxx", "password": "yyy"}（オプション）
        
    Returns:
        List[Dict]: 統合された検索結果
    """
    all_results = []
    
    # 日本語文字が含まれているかチェック
    has_japanese = any('あ' <= char <= 'ん' or 'ア' <= char <= 'ン' or 'ひ' <= char <= 'ゟ' for char in keyword)
    
    # JQuants検索（日本株）
    if jquants_config and jquants_config.get('email') and jquants_config.get('password'):
        try:
            jquants_searcher = JQuantsSearch()
            jquants_results = jquants_searcher.search(
                keyword, 
                jquants_config['email'], 
                jquants_config['password']
            )
            all_results.extend(jquants_results)
        except Exception as e:
            st.error(f"❌ JQuants検索エラー: {str(e)}")
    
    # Alpha Vantage検索（グローバル）
    if alpha_vantage_key:
        try:
            alpha_results = AlphaVantageSearch.search(keyword, alpha_vantage_key)
            all_results.extend(alpha_results)
        except Exception as e:
            st.error(f"❌ Alpha Vantage検索エラー: {str(e)}")
    
    # フォールバック検索（API無し時の基本検索）
    if not all_results:
        fallback_results = _fallback_search(keyword)
        all_results.extend(fallback_results)
    
    # 重複除去（同じsymbolの場合）
    seen_symbols = set()
    unique_results = []
    
    # 日本語検索の場合はJQuants結果を優先
    if has_japanese:
        # JQuants結果を先に処理
        jquants_first = sorted(all_results, key=lambda x: 0 if x['match_type'] == 'JQuants検索' else 1)
        all_results = jquants_first
    
    for result in all_results:
        symbol = result['symbol']
        if symbol not in seen_symbols:
            seen_symbols.add(symbol)
            unique_results.append(result)
    
    return unique_results[:5]  # 上位5件


def validate_stock_symbol(symbol: str) -> Tuple[bool, str, Dict[str, str]]:
    """
    銘柄コードの検証（市場情報付き）
    
    Args:
        symbol: 銘柄コード
        
    Returns:
        Tuple[bool, str, Dict]: (有効性, メッセージ, 市場情報)
    """
    if not symbol:
        return False, "銘柄コードを入力してください", {}
    
    symbol = symbol.upper().strip()
    
    # 日本株の形式チェック
    if symbol.endswith('.T'):
        market_info = {
            'market': '東京証券取引所',
            'exchange': 'Tokyo Stock Exchange',
            'currency': 'JPY',
            'region': 'Japan'
        }
        return True, f"日本株として認識: {symbol}", market_info
    
    # 米国株の形式チェック
    if len(symbol) >= 1 and symbol.replace('.', '').replace('-', '').isalnum():
        if '.' not in symbol and '-' not in symbol and len(symbol) <= 5:
            market_info = {
                'market': 'NASDAQ/NYSE',
                'exchange': 'US Stock Exchange',
                'currency': 'USD',
                'region': 'United States'
            }
            return True, f"米国株として認識: {symbol}", market_info
    
    # その他の形式
    market_info = {
        'market': 'Unknown',
        'exchange': 'Unknown',
        'currency': 'Unknown',
        'region': 'Unknown'
    }
    return True, f"銘柄コードとして認識: {symbol}", market_info
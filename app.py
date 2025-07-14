# TradeSim - 初心者向け株価分析アプリ

# 完全版 app.py

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import ta
from datetime import datetime, timedelta
import requests
import re
from typing import List, Dict
import time
import warnings
warnings.filterwarnings(‘ignore’)

# =============================================================================

# ページ設定

# =============================================================================

st.set_page_config(
page_title=“TradeSim - 株価分析アプリ”,
page_icon=“📈”,
layout=“wide”,
initial_sidebar_state=“expanded”
)

# CSS設定

st.markdown(”””

<style>
    .main > div {
        padding-top: 2rem;
    }
    .explanation-box {
        background: linear-gradient(90deg, #e3f2fd 0%, #f3e5f5 100%);
        border: 3px solid #2196f3;
        border-radius: 15px;
        padding: 20px;
        margin: 15px 0;
        color: #000000;
        font-weight: 500;
    }
    .explanation-box strong {
        color: #1976d2;
        font-size: 1.1rem;
    }
    .tip-box {
        background: linear-gradient(90deg, #fff3e0 0%, #fce4ec 100%);
        border: 3px solid #ff9800;
        border-radius: 12px;
        padding: 15px;
        margin: 10px 0;
        color: #000000;
    }
    .stButton > button {
        width: 100%;
        font-size: 1.2rem;
        padding: 0.75rem;
        border-radius: 10px;
        transition: all 0.3s ease;
    }
    .metric-card {
        background: white;
        padding: 15px;
        border-radius: 10px;
        border: 2px solid #e0e0e0;
        margin: 5px 0;
    }
    .success-alert {
        background: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .warning-alert {
        background: #fff3cd;
        border: 1px solid #ffeaa7;
        color: #856404;
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0;
    }
    @media (max-width: 768px) {
        .stButton > button {
            font-size: 1rem;
            padding: 0.5rem;
        }
        .explanation-box {
            padding: 15px;
            font-size: 0.9rem;
        }
    }
</style>

“””, unsafe_allow_html=True)

# =============================================================================

# 強化された日本企業検索システム

# =============================================================================

class EnhancedJapanStockSearch:
“”“日本企業検索強化版”””

```
def __init__(self):
    self.core_jp_stocks = {
        "トヨタ": "7203.T", "ソニー": "6758.T", "任天堂": "7974.T",
        "ソフトバンク": "9984.T", "楽天": "4755.T", "ユニクロ": "9983.T",
        "みずほ": "8411.T", "三菱ufj": "8306.T", "三井住友": "8316.T",
        "kddi": "9433.T", "ntt": "9432.T", "武田薬品": "4502.T",
        "キーエンス": "6861.T", "信越化学": "4063.T", "東京エレクトロン": "8035.T",
        "パナソニック": "6752.T", "日立": "6501.T", "セブン": "3382.T",
        "イオン": "8267.T", "ファナック": "6954.T", "村田製作所": "6981.T"
    }
    
    self.sector_patterns = {
        "銀行": {
            "codes": ["8306", "8316", "8411", "8355", "8377"],
            "keywords": ["銀行", "bank", "金融"]
        },
        "自動車": {
            "codes": ["7203", "7267", "7201", "7261", "7269"],
            "keywords": ["自動車", "車", "automotive", "motor"]
        },
        "通信": {
            "codes": ["9432", "9433", "9984", "4751"],
            "keywords": ["通信", "telecom", "携帯", "mobile"]
        },
        "ゲーム": {
            "codes": ["7974", "9684", "3659", "4751"],
            "keywords": ["ゲーム", "game", "エンタメ"]
        },
        "小売": {
            "codes": ["3382", "8267", "9983", "2702"],
            "keywords": ["小売", "retail", "店", "ショップ"]
        }
    }

def enhanced_search(self, keyword: str) -> List[Dict]:
    if not keyword or not keyword.strip():
        return []
        
    results = []
    keyword = keyword.strip()
    
    # 基本辞書検索
    basic_results = self._search_core_dict(keyword)
    results.extend(basic_results)
    
    # 動的検索
    if len(results) < 3:
        dynamic_results = self._dynamic_jp_search(keyword)
        results.extend(dynamic_results)
    
    # 業界検索
    if len(results) < 5:
        sector_results = self._sector_based_search(keyword)
        results.extend(sector_results)
    
    return self._clean_and_rank_results(results)

def _search_core_dict(self, keyword: str) -> List[Dict]:
    keyword_lower = keyword.lower()
    results = []
    
    if keyword_lower in self.core_jp_stocks:
        symbol = self.core_jp_stocks[keyword_lower]
        results.append({
            'symbol': symbol,
            'name': keyword,
            'match_type': '✅ 確実一致',
            'confidence': 1.0,
            'source': 'core'
        })
    
    for name, symbol in self.core_jp_stocks.items():
        if (keyword_lower in name.lower() or name.lower() in keyword_lower) and keyword_lower != name.lower():
            confidence = min(len(keyword_lower) / len(name), 0.8)
            results.append({
                'symbol': symbol,
                'name': name,
                'match_type': '📝 部分一致',
                'confidence': confidence,
                'source': 'core'
            })
    
    return results

def _dynamic_jp_search(self, keyword: str) -> List[Dict]:
    results = []
    
    if keyword.isdigit():
        code_patterns = [f"{keyword}.T", f"{int(keyword):04d}.T"]
        for pattern in code_patterns:
            result = self._test_japanese_stock(pattern, keyword)
            if result:
                results.append(result)
                break
    else:
        test_ranges = self._generate_test_codes(keyword)
        for code in test_ranges[:5]:
            symbol = f"{code}.T"
            result = self._test_japanese_stock(symbol, keyword)
            if result:
                results.append(result)
    
    return results

def _generate_test_codes(self, keyword: str) -> List[str]:
    likely_codes = []
    for sector, info in self.sector_patterns.items():
        if any(kw in keyword.lower() for kw in info["keywords"]):
            likely_codes.extend(info["codes"])
    
    if not likely_codes:
        likely_codes = ["7203", "6758", "9984", "4755", "8306"]
    
    return likely_codes

def _sector_based_search(self, keyword: str) -> List[Dict]:
    results = []
    for sector, info in self.sector_patterns.items():
        if any(kw in keyword.lower() for kw in info["keywords"]):
            for code in info["codes"][:3]:
                symbol = f"{code}.T"
                result = self._test_japanese_stock(symbol, f"{sector}企業")
                if result:
                    result['match_type'] = f'🏢 {sector}業界'
                    result['confidence'] = 0.6
                    results.append(result)
    return results

def _test_japanese_stock(self, symbol: str, original_keyword: str) -> Dict:
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        if (info and info.get('symbol') and info.get('longName') and self._is_japanese_stock(info)):
            return {
                'symbol': symbol,
                'name': info.get('longName', info.get('shortName', original_keyword)),
                'match_type': '🎌 動的検索',
                'confidence': 0.7,
                'source': 'dynamic'
            }
    except Exception:
        pass
    return None

def _is_japanese_stock(self, info: dict) -> bool:
    currency = info.get('currency', '')
    country = info.get('country', '')
    exchange = info.get('exchange', '')
    return (currency == 'JPY' or country == 'Japan' or 'TSE' in str(exchange))

def _clean_and_rank_results(self, results: List[Dict]) -> List[Dict]:
    seen_symbols = set()
    unique_results = []
    sorted_results = sorted(results, key=lambda x: x['confidence'], reverse=True)
    
    for result in sorted_results:
        symbol = result['symbol']
        if symbol not in seen_symbols:
            seen_symbols.add(symbol)
            unique_results.append(result)
    
    return unique_results[:6]
```

# =============================================================================

# ユーザー学習システム

# =============================================================================

class UserLearningSystem:
@staticmethod
def add_user_choice(keyword: str, symbol: str, name: str):
if ‘user_stock_choices’ not in st.session_state:
st.session_state.user_stock_choices = {}

```
    key = keyword.lower().strip()
    st.session_state.user_stock_choices[key] = {
        'symbol': symbol,
        'name': name,
        'count': st.session_state.user_stock_choices.get(key, {}).get('count', 0) + 1,
        'last_used': datetime.now()
    }

@staticmethod
def get_user_suggestions(keyword: str) -> List[Dict]:
    if 'user_stock_choices' not in st.session_state:
        return []
    
    keyword_lower = keyword.lower().strip()
    results = []
    
    if keyword_lower in st.session_state.user_stock_choices:
        data = st.session_state.user_stock_choices[keyword_lower]
        results.append({
            'symbol': data['symbol'],
            'name': data['name'],
            'match_type': '📚 学習済み',
            'confidence': 0.95,
            'source': 'user'
        })
    
    for stored_key, data in st.session_state.user_stock_choices.items():
        if (keyword_lower in stored_key or stored_key in keyword_lower) and keyword_lower != stored_key:
            confidence = 0.8 * min(data['count'] / 5, 1.0)
            results.append({
                'symbol': data['symbol'],
                'name': data['name'],
                'match_type': '📖 履歴',
                'confidence': confidence,
                'source': 'user'
            })
    
    return sorted(results, key=lambda x: x['confidence'], reverse=True)[:3]
```

# =============================================================================

# 既存の検索システム

# =============================================================================

class SuperStockSearch:
def **init**(self):
self.stock_dict = {
# 日本の主要銘柄
“トヨタ”: “7203.T”, “toyota”: “7203.T”, “トヨタ自動車”: “7203.T”,
“ソニー”: “6758.T”, “sony”: “6758.T”, “ソニーグループ”: “6758.T”,
“任天堂”: “7974.T”, “nintendo”: “7974.T”,
“ホンダ”: “7267.T”, “honda”: “7267.T”, “本田技研”: “7267.T”,
“日産”: “7201.T”, “nissan”: “7201.T”, “日産自動車”: “7201.T”,
“ソフトバンク”: “9984.T”, “softbank”: “9984.T”,
“楽天”: “4755.T”, “rakuten”: “4755.T”,
“ユニクロ”: “9983.T”, “ファーストリテイリング”: “9983.T”,

```
        # 米国の主要銘柄
        "apple": "AAPL", "アップル": "AAPL", "iphone": "AAPL",
        "microsoft": "MSFT", "マイクロソフト": "MSFT",
        "google": "GOOGL", "グーグル": "GOOGL", "alphabet": "GOOGL",
        "amazon": "AMZN", "アマゾン": "AMZN",
        "tesla": "TSLA", "テスラ": "TSLA",
        "nvidia": "NVDA", "エヌビディア": "NVDA",
        "meta": "META", "facebook": "META", "フェイスブック": "META",
        "netflix": "NFLX", "ネットフリックス": "NFLX",
        "disney": "DIS", "ディズニー": "DIS",
        "nike": "NKE", "ナイキ": "NKE",
    }

def search(self, keyword: str) -> List[Dict]:
    keyword = keyword.strip()
    if not keyword:
        return []
        
    results = []
    basic_results = self._search_basic_dict(keyword)
    results.extend(basic_results)
    
    yf_results = self._search_yfinance_direct(keyword)
    results.extend(yf_results)
    
    partial_results = self._search_partial_match(keyword)
    results.extend(partial_results)
    
    return self._remove_duplicates(results)

def _search_basic_dict(self, keyword: str) -> List[Dict]:
    keyword_lower = keyword.lower()
    results = []
    
    if keyword_lower in self.stock_dict:
        symbol = self.stock_dict[keyword_lower]
        results.append({
            'symbol': symbol,
            'name': keyword,
            'match_type': '✅ 完全一致',
            'confidence': 1.0
        })
    
    return results

def _search_yfinance_direct(self, keyword: str) -> List[Dict]:
    results = []
    test_symbols = [keyword.upper(), f"{keyword.upper()}.T"]
    
    if keyword.isdigit():
        test_symbols.extend([f"{keyword}.T"])
    
    for symbol in test_symbols:
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            if (info and info.get('symbol') and info.get('longName')):
                results.append({
                    'symbol': symbol,
                    'name': info.get('longName', symbol),
                    'match_type': '🎯 直接検索',
                    'confidence': 0.85,
                })
                break
        except Exception:
            continue
    
    return results

def _search_partial_match(self, keyword: str) -> List[Dict]:
    keyword_lower = keyword.lower()
    results = []
    
    for name, symbol in self.stock_dict.items():
        if (keyword_lower in name.lower() or name.lower() in keyword_lower) and keyword_lower != name.lower():
            confidence = min(len(keyword_lower) / len(name), 0.7)
            results.append({
                'symbol': symbol,
                'name': name,
                'match_type': '📝 部分一致',
                'confidence': confidence
            })
    
    return sorted(results, key=lambda x: x['confidence'], reverse=True)

def _remove_duplicates(self, results: List[Dict]) -> List[Dict]:
    seen_symbols = set()
    unique_results = []
    sorted_results = sorted(results, key=lambda x: x['confidence'], reverse=True)
    
    for result in sorted_results:
        symbol = result['symbol']
        if symbol not in seen_symbols:
            seen_symbols.add(symbol)
            unique_results.append(result)
            
    return unique_results[:8]
```

# =============================================================================

# 統合検索機能

# =============================================================================

def integrated_stock_search(keyword: str, api_key: str = None) -> List[Dict]:
if not keyword or not keyword.strip():
return []

```
all_results = []

# ユーザー学習結果
user_results = UserLearningSystem.get_user_suggestions(keyword)
all_results.extend(user_results)

# 既存検索
if 'searcher' not in st.session_state:
    st.session_state.searcher = SuperStockSearch()

super_results = st.session_state.searcher.search(keyword)
all_results.extend(super_results)

# 強化された日本企業検索
if len(all_results) < 4:
    if 'jp_searcher' not in st.session_state:
        st.session_state.jp_searcher = EnhancedJapanStockSearch()
    
    enhanced_results = st.session_state.jp_searcher.enhanced_search(keyword)
    all_results.extend(enhanced_results)

# Alpha Vantage API
if api_key and len(all_results) < 6:
    api_results = search_alpha_vantage_enhanced(keyword, api_key)
    all_results.extend(api_results)

return remove_duplicates_final(all_results)
```

def remove_duplicates_final(results: List[Dict]) -> List[Dict]:
seen_symbols = set()
unique_results = []
source_priority = {‘user’: 3, ‘core’: 2, ‘dynamic’: 1, ‘api’: 0}

```
def sort_key(result):
    source = result.get('source', 'unknown')
    priority = source_priority.get(source, 0)
    confidence = result.get('confidence', 0)
    return (priority, confidence)

sorted_results = sorted(results, key=sort_key, reverse=True)

for result in sorted_results:
    symbol = result['symbol']
    if symbol not in seen_symbols:
        seen_symbols.add(symbol)
        unique_results.append(result)

return unique_results[:8]
```

def search_alpha_vantage_enhanced(keyword, api_key):
if not api_key:
return []

```
try:
    url = "https://www.alphavantage.co/query"
    params = {
        'function': 'SYMBOL_SEARCH',
        'keywords': keyword,
        'apikey': api_key
    }
    
    response = requests.get(url, params=params, timeout=8)
    if response.status_code == 200:
        data = response.json()
        results = []
        if 'bestMatches' in data:
            for match in data['bestMatches']:
                symbol = match.get('1. symbol', '')
                name = match.get('2. name', '')
                match_score = float(match.get('9. matchScore', '0'))
                
                if symbol and name and match_score > 0.3:
                    results.append({
                        'symbol': symbol,
                        'name': name,
                        'match_type': '🌐 API検索',
                        'confidence': min(match_score, 0.8),
                        'source': 'api'
                    })
        
        return sorted(results, key=lambda x: x['confidence'], reverse=True)[:5]
    
except Exception as e:
    st.warning(f"API検索でエラーが発生しました: {e}")

return []
```

# =============================================================================

# データ取得・分析機能

# =============================================================================

@st.cache_data
def fetch_stock_data(symbol, start_date, end_date):
“”“株価データの取得”””
try:
ticker = yf.Ticker(symbol)
data = ticker.history(start=start_date, end=end_date)

```
    if data.empty:
        return None, None
    
    info = ticker.info
    return data, info
except Exception as e:
    st.error(f"データ取得エラー: {e}")
    return None, None
```

def calculate_indicators(data):
“”“テクニカル指標の計算”””
if data is None or len(data) < 50:
return None

```
df = data.copy()

# 移動平均線
df['MA20'] = ta.trend.sma_indicator(df['Close'], window=20)
df['MA50'] = ta.trend.sma_indicator(df['Close'], window=50)

# RSI
df['RSI'] = ta.momentum.rsi(df['Close'], window=14)

# ボリンジャーバンド
bb_indicator = ta.volatility.BollingerBands(df['Close'], window=20, window_dev=2)
df['BB_upper'] = bb_indicator.bollinger_hband()
df['BB_middle'] = bb_indicator.bollinger_mavg()
df['BB_lower'] = bb_indicator.bollinger_lband()

# MACD
macd_indicator = ta.trend.MACD(df['Close'])
df['MACD'] = macd_indicator.macd()
df['MACD_signal'] = macd_indicator.macd_signal()
df['MACD_histogram'] = macd_indicator.macd_diff()

# 出来高移動平均
df['Volume_MA'] = ta.trend.sma_indicator(df['Volume'], window=20)

return df
```

def generate_signals_advanced(df):
“”“高度な売買シグナル生成”””
if df is None or len(df) < 50:
return “データ不足”, 0, []

```
latest = df.iloc[-1]
signals = []
buy_score = 0
sell_score = 0

# 移動平均線シグナル
if latest['MA20'] > latest['MA50']:
    buy_score += 1
    signals.append("✅ 短期移動平均が長期移動平均を上回っています（上昇トレンド）")
else:
    sell_score += 1
    signals.append("❌ 短期移動平均が長期移動平均を下回っています（下降トレンド）")

# RSIシグナル
rsi = latest['RSI']
if rsi < 35:
    buy_score += 1
    signals.append(f"✅ RSI({rsi:.1f})が売られすぎ水準です（買いシグナル）")
elif rsi > 65:
    sell_score += 1
    signals.append(f"❌ RSI({rsi:.1f})が買われすぎ水準です（売りシグナル）")
else:
    signals.append(f"➖ RSI({rsi:.1f})は中立的です")

# ボリンジャーバンドシグナル
price = latest['Close']
bb_upper = latest['BB_upper']
bb_lower = latest['BB_lower']

if price < bb_lower:
    buy_score += 1.5
    signals.append("✅ 価格がボリンジャーバンド下限を下回っています（割安）")
elif price > bb_upper:
    sell_score += 1.5
    signals.append("❌ 価格がボリンジャーバンド上限を上回っています（割高）")
else:
    signals.append("➖ 価格はボリンジャーバンド内で推移しています")

# MACDシグナル
macd_current = latest['MACD']
macd_signal_current = latest['MACD_signal']

if len(df) >= 2:
    macd_prev = df.iloc[-2]['MACD']
    signal_prev = df.iloc[-2]['MACD_signal']
    
    if macd_prev <= signal_prev and macd_current > macd_signal_current:
        buy_score += 1.5
        signals.append("✅ MACDがシグナル線を上抜けました（ゴールデンクロス）")
    elif macd_prev >= signal_prev and macd_current < macd_signal_current:
        sell_score += 1.5
        signals.append("❌ MACDがシグナル線を下抜けました（デッドクロス）")
    else:
        signals.append("➖ MACD は変化なしです")

# 出来高シグナル
volume_ratio = latest['Volume'] / latest['Volume_MA'] if latest['Volume_MA'] > 0 else 1
if volume_ratio > 1.5:
    buy_score += 0.5
    signals.append(f"✅ 出来高が平均の{volume_ratio:.1f}倍で活発です")
else:
    signals.append("➖ 出来高は通常レベルです")

# 総合判定
total_score = buy_score - sell_score

if total_score >= 2.5:
    judgment = "🟢 買い推奨"
    score = min(total_score / 5 * 100, 100)
elif total_score <= -2.5:
    judgment = "🔴 売り推奨"
    score = max(-total_score / 5 * 100, -100)
else:
    judgment = "🟡 中立・様子見"
    score = total_score / 5 * 100

return judgment, score, signals
```

def backtest_realistic(df, initial_capital=1000000, risk_pct=2.0, stop_loss_pct=5.0, take_profit_pct=15.0, cost_rate=0.001):
“”“リアリスティックなバックテスト”””
if df is None or len(df) < 100:
return None

```
results = {
    'dates': [],
    'portfolio_value': [],
    'positions': [],
    'trades': [],
    'returns': []
}

capital = initial_capital
position = 0
entry_price = 0
stop_loss_price = 0
take_profit_price = 0

for i in range(50, len(df)):
    current_data = df.iloc[:i+1]
    current_price = current_data.iloc[-1]['Close']
    current_date = current_data.index[-1]
    
    # シグナル生成
    judgment, score, _ = generate_signals_advanced(current_data)
    
    # ポジションがない場合の買いシグナル
    if position == 0 and "買い推奨" in judgment and score > 50:
        # リスクベースのポジションサイジング
        risk_amount = capital * (risk_pct / 100)
        potential_loss_per_share = current_price * (stop_loss_pct / 100)
        
        if potential_loss_per_share > 0:
            position_size = risk_amount / potential_loss_per_share
            position_cost = position_size * current_price * (1 + cost_rate)
            
            if position_cost <= capital:
                position = position_size
                entry_price = current_price
                stop_loss_price = entry_price * (1 - stop_loss_pct / 100)
                take_profit_price = entry_price * (1 + take_profit_pct / 100)
                capital -= position_cost
                
                results['trades'].append({
                    'date': current_date,
                    'type': 'BUY',
                    'price': current_price,
                    'size': position_size,
                    'reason': 'シグナル買い'
                })
    
    # ポジションがある場合の売りシグナル
    elif position > 0:
        sell_reason = None
        
        # 損切り
        if current_price <= stop_loss_price:
            sell_reason = "損切り"
        # 利益確定
        elif current_price >= take_profit_price:
            sell_reason = "利益確定"
        # シグナル売り
        elif "売り推奨" in judgment and score < -30:
            sell_reason = "シグナル売り"
        
        if sell_reason:
            sell_value = position * current_price * (1 - cost_rate)
            capital += sell_value
            
            results['trades'].append({
                'date': current_date,
                'type': 'SELL',
                'price': current_price,
                'size': position,
                'reason': sell_reason
            })
            
            position = 0
    
    # ポートフォリオ価値の計算
    portfolio_value = capital + (position * current_price if position > 0 else 0)
    
    results['dates'].append(current_date)
    results['portfolio_value'].append(portfolio_value)
    results['positions'].append(position)
    
    # リターン計算
    if len(results['portfolio_value']) > 1:
        daily_return = (portfolio_value / results['portfolio_value'][-2] - 1) * 100
        results['returns'].append(daily_return)
    else:
        results['returns'].append(0)

return results
```

# =============================================================================

# チャート作成機能

# =============================================================================

def create_comprehensive_chart(df, info):
“”“包括的なチャート作成”””
if df is None:
return None

```
# サブプロット作成
fig = make_subplots(
    rows=4, cols=1,
    shared_xaxes=True,
    vertical_spacing=0.03,
    subplot_titles=('株価とテクニカル指標', 'RSI', 'MACD', '出来高'),
    row_heights=[0.5, 0.2, 0.2, 0.1]
)

# 1. 株価チャート
fig.add_trace(
    go.Candlestick(
        x=df.index,
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        name="株価"
    ),
    row=1, col=1
)

# 移動平均線
if 'MA20' in df.columns:
    fig.add_trace(
        go.Scatter(x=df.index, y=df['MA20'], name="MA20", line=dict(color="orange")),
        row=1, col=1
    )

if 'MA50' in df.columns:
    fig.add_trace(
        go.Scatter(x=df.index, y=df['MA50'], name="MA50", line=dict(color="blue")),
        row=1, col=1
    )

# ボリンジャーバンド
if all(col in df.columns for col in ['BB_upper', 'BB_middle', 'BB_lower']):
    fig.add_trace(
        go.Scatter(x=df.index, y=df['BB_upper'], name="BB上限", line=dict(color="gray", dash="dash")),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(x=df.index, y=df['BB_lower'], name="BB下限", line=dict(color="gray", dash="dash"), fill='tonexty'),
        row=1, col=1
    )

# 2. RSI
if 'RSI' in df.columns:
    fig.add_trace(
        go.Scatter(x=df.index, y=df['RSI'], name="RSI", line=dict(color="purple")),
        row=2, col=1
    )
    fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)

# 3. MACD
if all(col in df.columns for col in ['MACD', 'MACD_signal', 'MACD_histogram']):
    fig.add_trace(
        go.Scatter(x=df.index, y=df['MACD'], name="MACD", line=dict(color="blue")),
        row=3, col=1
    )
    fig.add_trace(
        go.Scatter(x=df.index, y=df['MACD_signal'], name="シグナル", line=dict(color="red")),
        row=3, col=1
    )
    fig.add_trace(
        go.Bar(x=df.index, y=df['MACD_histogram'], name="ヒストグラム"),
        row=3, col=1
    )

# 4. 出来高
fig.add_trace(
    go.Bar(x=df.index, y=df['Volume'], name="出来高", marker_color="lightblue"),
    row=4, col=1
)

if 'Volume_MA' in df.columns:
    fig.add_trace(
        go.Scatter(x=df.index, y=df['Volume_MA'], name="出来高MA", line=dict(color="red")),
        row=4, col=1
    )

# レイアウト設定
company_name = info.get('longName', '銘柄') if info else '銘柄'
fig.update_layout(
    title=f"{company_name} - 包括的テクニカル分析",
    height=800,
    showlegend=True,
    xaxis_rangeslider_visible=False
)

return fig
```

def create_backtest_chart(backtest_results):
“”“バックテスト結果のチャート”””
if not backtest_results:
return None

```
fig = go.Figure()

# ポートフォリオ価値の推移
fig.add_trace(
    go.Scatter(
        x=backtest_results['dates'],
        y=backtest_results['portfolio_value'],
        mode='lines',
        name='ポートフォリオ価値',
        line=dict(color='blue', width=2)
    )
)

# 売買ポイントをマーク
buy_dates = []
buy_values = []
sell_dates = []
sell_values = []

for trade in backtest_results['trades']:
    if trade['type'] == 'BUY':
        idx = backtest_results['dates'].index(trade['date'])
        buy_dates.append(trade['date'])
        buy_values.append(backtest_results['portfolio_value'][idx])
    else:
        idx = backtest_results['dates'].index(trade['date'])
        sell_dates.append(trade['date'])
        sell_values.append(backtest_results['portfolio_value'][idx])

if buy_dates:
    fig.add_trace(
        go.Scatter(
            x=buy_dates,
            y=buy_values,
            mode='markers',
            name='買い',
            marker=dict(color='green', size=10, symbol='triangle-up')
        )
    )

if sell_dates:
    fig.add_trace(
        go.Scatter(
            x=sell_dates,
            y=sell_values,
            mode='markers',
            name='売り',
            marker=dict(color='red', size=10, symbol='triangle-down')
        )
    )

fig.update_layout(
    title="バックテスト結果 - ポートフォリオ価値の推移",
    xaxis_title="日付",
    yaxis_title="ポートフォリオ価値 (円)",
    height=500
)

return fig
```

# =============================================================================

# ポートフォリオ管理機能

# =============================================================================

def initialize_portfolio():
“”“ポートフォリオの初期化”””
if ‘portfolio’ not in st.session_state:
st.session_state.portfolio = {}

def add_to_portfolio(symbol, shares, avg_price, long_name):
“”“ポートフォリオに銘柄を追加”””
if symbol in st.session_state.portfolio:
# 既存銘柄の場合、平均単価を計算
existing = st.session_state.portfolio[symbol]
total_shares = existing[‘shares’] + shares
total_cost = (existing[‘shares’] * existing[‘avg_price’]) + (shares * avg_price)
new_avg_price = total_cost / total_shares

```
    st.session_state.portfolio[symbol] = {
        'shares': total_shares,
        'avg_price': new_avg_price,
        'longName': long_name
    }
else:
    st.session_state.portfolio[symbol] = {
        'shares': shares,
        'avg_price': avg_price,
        'longName': long_name
    }
```

def get_portfolio_performance():
“”“ポートフォリオのパフォーマンス計算”””
if not st.session_state.portfolio:
return None

```
portfolio_data = []
total_investment = 0
total_current_value = 0

for symbol, data in st.session_state.portfolio.items():
    try:
        ticker = yf.Ticker(symbol)
        current_price = ticker.info.get('regularMarketPrice')
        
        if current_price:
            investment = data['shares'] * data['avg_price']
            current_value = data['shares'] * current_price
            gain_loss = current_value - investment
            gain_loss_pct = (gain_loss / investment) * 100
            
            portfolio_data.append({
                'symbol': symbol,
                'name': data['longName'],
                'shares': data['shares'],
                'avg_price': data['avg_price'],
                'current_price': current_price,
                'investment': investment,
                'current_value': current_value,
                'gain_loss': gain_loss,
                'gain_loss_pct': gain_loss_pct
            })
            
            total_investment += investment
            total_current_value += current_value
    
    except Exception as e:
        st.warning(f"{symbol}の価格取得に失敗しました: {e}")
        continue

if portfolio_data:
    total_gain_loss = total_current_value - total_investment
    total_gain_loss_pct = (total_gain_loss / total_investment) * 100 if total_investment > 0 else 0
    
    return {
        'portfolio_data': portfolio_data,
        'total_investment': total_investment,
        'total_current_value': total_current_value,
        'total_gain_loss': total_gain_loss,
        'total_gain_loss_pct': total_gain_loss_pct
    }

return None
```

# =============================================================================

# メインアプリケーション

# =============================================================================

def main():
# サイドバー
st.sidebar.title(“📈 TradeSim”)
st.sidebar.markdown(”**初心者向け株価分析アプリ**”)

```
# ポートフォリオ初期化
initialize_portfolio()

# メインページ選択
page = st.sidebar.selectbox(
    "📋 機能選択",
    ["🔍 株価分析", "💼 ポートフォリオ管理", "📚 投資の基礎"]
)

if page == "🔍 株価分析":
    stock_analysis_page()
elif page == "💼 ポートフォリオ管理":
    portfolio_management_page()
elif page == "📚 投資の基礎":
    education_page()
```

def stock_analysis_page():
“”“株価分析ページ”””
st.title(“🔍 株価分析”)

```
# 銘柄選択方法
search_method = st.selectbox(
    "銘柄選択方法",
    ["🔍 会社名で検索", "⭐ 人気銘柄から選択", "📝 銘柄コード直接入力"]
)

stock_code = None

if search_method == "🔍 会社名で検索":
    st.markdown("""
    <div class="explanation-box">
    <strong>🚀 AIパワード企業検索</strong><br>
    <span>• 学習機能：よく使う銘柄を記憶</span><br>
    <span>• 動的検索：数千社の日本企業を自動発見</span><br>
    <span>• 業界検索：「銀行」「自動車」で関連企業を表示</span><br>
    <span>• 多言語対応：日本語・英語・銘柄コード</span>
    </div>
    """, unsafe_allow_html=True)
    
    # Alpha Vantage API Key
    api_key = None
    with st.expander("🔧 さらに多くの企業を検索（上級者向け）"):
        api_key = st.text_input(
            "Alpha Vantage API Key（省略可）",
            type="password",
            help="無料で取得可能。世界中の企業を検索できます"
        )
        st.markdown("""
        <div class="tip-box">
        💡 <strong>API Keyなしでも十分：</strong> <span>主要企業（数百社）+ 動的検索で数千社対応</span><br>
        <strong>API Keyがあると：</strong> <span>世界中の企業（数万社）を検索可能</span>
        </div>
        """, unsafe_allow_html=True)
    
    # 検索入力
    search_keyword = st.text_input(
        "🔍 企業名・銘柄コード・業界名を入力",
        placeholder="例: 三菱UFJ, 7203, 銀行, ゲーム, MSFT, テスラ",
        key="integrated_search_input"
    )
    
    if search_keyword:
        with st.spinner("🤖 AI検索中..."):
            search_results = integrated_stock_search(search_keyword, api_key)
        
        if search_results:
            st.success(f"🎯 '{search_keyword}' の検索結果: {len(search_results)}件")
            
            # 結果表示
            selected_stock = None
            for result in search_results:
                symbol = result['symbol']
                name = result['name']
                match_type = result['match_type']
                confidence = result.get('confidence', 0)
                
                if confidence > 0.9:
                    icon = "🎯"
                elif confidence > 0.7:
                    icon = "👍"
                else:
                    icon = "💡"
                
                if st.button(
                    f"{icon} {symbol} - {name}",
                    key=f"search_result_{symbol}_{hash(name)}",
                    help=f"{match_type} | 信頼度: {confidence:.2f}",
                    use_container_width=True
                ):
                    selected_stock = symbol
                    st.session_state.selected_stock_name = name
                    UserLearningSystem.add_user_choice(search_keyword, symbol, name)
                    st.success(f"✅ 選択しました: {symbol} - {name}")
                    st.balloons()
            
            if selected_stock:
                stock_code = selected_stock
            else:
                stock_code = search_results[0]['symbol'] if search_results else "AAPL"
        
        else:
            st.warning("🔍 検索結果が見つかりませんでした")
            stock_code = "AAPL"

elif search_method == "⭐ 人気銘柄から選択":
    st.markdown("""
    <div class="explanation-box">
    <strong>⭐ 人気銘柄セレクション</strong><br>
    <span>投資家に人気の銘柄を厳選しました</span>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**🇯🇵 日本株**")
        jp_stocks = {
            "🚗 トヨタ自動車": "7203.T",
            "🎮 任天堂": "7974.T",
            "📱 ソニー": "6758.T",
            "🏪 ユニクロ": "9983.T",
            "📞 ソフトバンク": "9984.T",
            "🛒 楽天": "4755.T"
        }
        
        for name, symbol in jp_stocks.items():
            if st.button(name, key=f"jp_{symbol}", use_container_width=True):
                stock_code = symbol
                st.success(f"✅ {name} を選択しました")
    
    with col2:
        st.markdown("**🇺🇸 米国株**")
        us_stocks = {
            "🍎 Apple": "AAPL",
            "🖥️ Microsoft": "MSFT",
            "🔍 Google": "GOOGL",
            "📦 Amazon": "AMZN",
            "⚡ Tesla": "TSLA",
            "🎬 Netflix": "NFLX"
        }
        
        for name, symbol in us_stocks.items():
            if st.button(name, key=f"us_{symbol}", use_container_width=True):
                stock_code = symbol
                st.success(f"✅ {name} を選択しました")

elif search_method == "📝 銘柄コード直接入力":
    st.markdown("""
    <div class="explanation-box">
    <strong>📝 銘柄コード直接入力</strong><br>
    <span>知っている銘柄コードを直接入力してください</span>
    </div>
    """, unsafe_allow_html=True)
    
    stock_code = st.text_input(
        "銘柄コードを入力",
        placeholder="例: AAPL, 7203.T, MSFT",
        help="米国株: AAPL, MSFT など / 日本株: 7203.T, 6758.T など"
    ).upper()

if not stock_code:
    stock_code = "AAPL"  # デフォルト

# 分析期間設定
st.markdown("### 📅 分析期間設定")

col1, col2 = st.columns(2)
with col1:
    period_option = st.selectbox(
        "期間選択",
        ["1ヶ月", "3ヶ月", "6ヶ月", "1年", "2年", "カスタム期間"]
    )

with col2:
    if period_option == "カスタム期間":
        end_date = st.date_input("終了日", datetime.now())
        start_date = st.date_input("開始日", datetime.now() - timedelta(days=365))
    else:
        period_map = {
            "1ヶ月": 30,
            "3ヶ月": 90,
            "6ヶ月": 180,
            "1年": 365,
            "2年": 730
        }
        days = period_map[period_option]
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

# 分析実行ボタン
if st.button("🚀 分析開始", type="primary", use_container_width=True):
    with st.spinner("📊 データを取得・分析中..."):
        # データ取得
        data, info = fetch_stock_data(stock_code, start_date, end_date)
        
        if data is None:
            st.error("❌ データの取得に失敗しました。銘柄コードを確認してください。")
            return
        
        # テクニカル指標計算
        df_with_indicators = calculate_indicators(data)
        
        if df_with_indicators is None:
            st.error("❌ データが不足しています。より長い期間を選択してください。")
            return
        
        # 会社情報表示
        if info:
            st.markdown("### 📊 企業情報")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("会社名", info.get('longName', 'N/A')[:20] + "...")
            
            with col2:
                current_price = info.get('regularMarketPrice', 0)
                prev_close = info.get('previousClose', 0)
                change = current_price - prev_close if current_price and prev_close else 0
                change_pct = (change / prev_close * 100) if prev_close else 0
                st.metric(
                    "現在価格", 
                    f"${current_price:.2f}" if current_price else "N/A",
                    f"{change:+.2f} ({change_pct:+.1f}%)"
                )
            
            with col3:
                market_cap = info.get('marketCap')
                if market_cap:
                    if market_cap >= 1e12:
                        market_cap_str = f"${market_cap/1e12:.1f}T"
                    elif market_cap >= 1e9:
                        market_cap_str = f"${market_cap/1e9:.1f}B"
                    else:
                        market_cap_str = f"${market_cap/1e6:.1f}M"
                else:
                    market_cap_str = "N/A"
                st.metric("時価総額", market_cap_str)
            
            with col4:
                st.metric("業界", info.get('sector', 'N/A'))
        
        # AIによる投資判断
        st.markdown("### 🤖 AI投資判断")
        judgment, score, signals = generate_signals_advanced(df_with_indicators)
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            # スコア表示
            if score > 0:
                st.success(f"**{judgment}**")
                st.progress(min(score/100, 1.0))
                st.write(f"信頼度: {abs(score):.1f}%")
            elif score < 0:
                st.error(f"**{judgment}**")
                st.progress(min(abs(score)/100, 1.0))
                st.write(f"信頼度: {abs(score):.1f}%")
            else:
                st.warning(f"**{judgment}**")
                st.write("信頼度: 50%")
        
        with col2:
            st.markdown("**📋 判断根拠:**")
            for signal in signals:
                st.write(signal)
        
        # チャート表示
        st.markdown("### 📈 テクニカル分析チャート")
        chart = create_comprehensive_chart(df_with_indicators, info)
        if chart:
            st.plotly_chart(chart, use_container_width=True)
        
        # バックテスト
        st.markdown("### 💰 投資シミュレーション")
        
        with st.expander("📊 シミュレーション設定", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                initial_capital = st.number_input(
                    "初期資金 (円)", 
                    value=1000000, 
                    min_value=100000, 
                    max_value=10000000,
                    step=100000
                )
                risk_pct = st.slider(
                    "1取引あたりのリスク (%)", 
                    min_value=0.5, 
                    max_value=5.0, 
                    value=2.0, 
                    step=0.1
                )
            
            with col2:
                stop_loss_pct = st.slider(
                    "損切りライン (%)", 
                    min_value=1.0, 
                    max_value=20.0, 
                    value=5.0, 
                    step=0.5
                )
                take_profit_pct = st.slider(
                    "利益確定ライン (%)", 
                    min_value=2.0, 
                    max_value=50.0, 
                    value=15.0, 
                    step=1.0
                )
        
        # バックテスト実行
        with st.spinner("📊 投資シミュレーション実行中..."):
            backtest_results = backtest_realistic(
                df_with_indicators, 
                initial_capital, 
                risk_pct, 
                stop_loss_pct, 
                take_profit_pct
            )
        
        if backtest_results:
            # バックテスト結果サマリー
            final_value = backtest_results['portfolio_value'][-1]
            total_return = (final_value / initial_capital - 1) * 100
            total_trades = len(backtest_results['trades'])
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "最終資産", 
                    f"¥{final_value:,.0f}",
                    f"{total_return:+.1f}%"
                )
            
            with col2:
                profit_loss = final_value - initial_capital
                st.metric(
                    "損益", 
                    f"¥{profit_loss:+,.0f}",
                    "profit" if profit_loss > 0 else "loss"
                )
            
            with col3:
                st.metric("総取引回数", f"{total_trades}回")
            
            with col4:
                if total_return > 10:
                    performance = "🎉 優秀"
                elif total_return > 0:
                    performance = "👍 良好"
                else:
                    performance = "📚 要改善"
                st.metric("成績評価", performance)
            
            # バックテストチャート
            backtest_chart = create_backtest_chart(backtest_results)
            if backtest_chart:
                st.plotly_chart(backtest_chart, use_container_width=True)
            
            # 取引履歴
            if backtest_results['trades']:
                st.markdown("### 📝 取引履歴")
                trades_df = pd.DataFrame(backtest_results['trades'])
                st.dataframe(trades_df, use_container_width=True)
        
        # ポートフォリオに追加オプション
        st.markdown("### 💼 ポートフォリオ管理")
        
        with st.expander("📝 この銘柄をポートフォリオに追加", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                shares = st.number_input(
                    "株数", 
                    value=100, 
                    min_value=1, 
                    max_value=10000
                )
            
            with col2:
                avg_price = st.number_input(
                    "平均取得価格", 
                    value=current_price if 'current_price' in locals() else 100.0,
                    min_value=0.01
                )
            
            if st.button("💼 ポートフォリオに追加", type="secondary"):
                company_name = info.get('longName', stock_code) if info else stock_code
                add_to_portfolio(stock_code, shares, avg_price, company_name)
                st.success(f"✅ {company_name} をポートフォリオに追加しました！")
```

def portfolio_management_page():
“”“ポートフォリオ管理ページ”””
st.title(“💼 ポートフォリオ管理”)

```
if not st.session_state.portfolio:
    st.info("📝 まだポートフォリオに銘柄が登録されていません。株価分析ページで銘柄を追加してください。")
    return

# ポートフォリオパフォーマンス取得
with st.spinner("📊 ポートフォリオ情報を取得中..."):
    portfolio_performance = get_portfolio_performance()

if not portfolio_performance:
    st.error("❌ ポートフォリオ情報の取得に失敗しました。")
    return

# 総合パフォーマンス表示
st.markdown("### 📊 ポートフォリオサマリー")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "総投資額", 
        f"¥{portfolio_performance['total_investment']:,.0f}"
    )

with col2:
    st.metric(
        "現在価値", 
        f"¥{portfolio_performance['total_current_value']:,.0f}",
        f"¥{portfolio_performance['total_gain_loss']:+,.0f}"
    )

with col3:
    gain_loss_pct = portfolio_performance['total_gain_loss_pct']
    st.metric(
        "損益率", 
        f"{gain_loss_pct:+.1f}%",
        "profit" if gain_loss_pct > 0 else "loss"
    )

with col4:
    num_holdings = len(portfolio_performance['portfolio_data'])
    st.metric("保有銘柄数", f"{num_holdings}銘柄")

# 個別銘柄詳細
st.markdown("### 📋 保有銘柄詳細")

portfolio_df = pd.DataFrame(portfolio_performance['portfolio_data'])

# データフレーム表示
st.dataframe(
    portfolio_df[[
        'symbol', 'name', 'shares', 'avg_price', 
        'current_price', 'investment', 'current_value', 
        'gain_loss', 'gain_loss_pct'
    ]].round(2),
    use_container_width=True
)

# ポートフォリオ構成チャート
st.markdown("### 📊 ポートフォリオ構成")

fig = px.pie(
    portfolio_df, 
    values='current_value', 
    names='symbol',
    title="保有銘柄別構成比"
)
st.plotly_chart(fig, use_container_width=True)

# 銘柄削除機能
st.markdown("### 🗑️ 銘柄管理")

with st.expander("銘柄を削除", expanded=False):
    symbol_to_remove = st.selectbox(
        "削除する銘柄を選択",
        list(st.session_state.portfolio.keys())
    )
    
    if st.button("🗑️ 削除", type="secondary"):
        del st.session_state.portfolio[symbol_to_remove]
        st.success(f"✅ {symbol_to_remove} をポートフォリオから削除しました")
        st.experimental_rerun()
```

def education_page():
“”“投資教育ページ”””
st.title(“📚 投資の基礎”)

```
tab1, tab2, tab3, tab4 = st.tabs(["💡 基本概念", "📊 テクニカル分析", "⚠️ リスク管理", "🎯 実践tips"])

with tab1:
    st.markdown("""
    ### 💡 投資の基本概念
    
    #### 🏢 株式とは？
    株式とは「会社の一部を買うこと」です。会社が成長すれば株価も上がり、利益が得られます。
    
    #### 📈 リスクとリターン
    - **リターン**: 投資で得られる利益
    - **リスク**: 損失を被る可能性
    - **重要**: 高いリターンには高いリスクが伴います
    
    #### 🎯 分散投資
    「卵を一つのカゴに盛らない」という格言通り、複数の銘柄に投資してリスクを分散させます。
    
    #### ⏰ 長期投資
    短期的な値動きに一喜一憂せず、長期的な成長を信じて投資を続けることが重要です。
    """)

with tab2:
    st.markdown("""
    ### 📊 テクニカル分析の基礎
    
    #### 📈 移動平均線
    - **短期移動平均**: 20日間の平均価格
    - **長期移動平均**: 50日間の平均価格
    - **ゴールデンクロス**: 短期が長期を上抜ける（買いシグナル）
    - **デッドクロス**: 短期が長期を下抜ける（売りシグナル）
    
    #### 🎯 RSI（相対力指数）
    - **0-100の範囲**: 現在の値動きの強さを表示
    - **70以上**: 買われすぎ（売りを検討）
    - **30以下**: 売られすぎ（買いを検討）
    
    #### 📊 ボリンジャーバンド
    - **上限・下限**: 価格の正常な変動範囲
    - **バンド下限**: 割安圏（買いを検討）
    - **バンド上限**: 割高圏（売りを検討）
    
    #### ⚡ MACD
    - **ゴールデンクロス**: MACDがシグナル線を上抜け
    - **デッドクロス**: MACDがシグナル線を下抜け
    """)

with tab3:
    st.markdown("""
    ### ⚠️ リスク管理
    
    #### 🛡️ 損切りの重要性
    - **2%ルール**: 1回の取引で総資産の2%以上リスクを取らない
    - **損切りライン**: 事前に損失限度額を決める
    - **感情的な判断を避ける**: ルールに従って機械的に実行
    
    #### 💰 ポジションサイジング
    ```
    投資額 = 総資産 × リスク許容度 ÷ 損切り幅
    ```
    
    #### 📚 学習の継続
    - **失敗から学ぶ**: 損失も大切な学習機会
    - **記録を取る**: 投資判断の根拠を記録
    - **情報収集**: 常に新しい情報をキャッチアップ
    """)

with tab4:
    st.markdown("""
    ### 🎯 実践的なTips
    
    #### 🚀 初心者向けスタートガイド
    1. **少額から始める**: 余裕資金で実践
    2. **知っている会社から**: 身近な企業を選ぶ
    3. **基本を学ぶ**: 企業分析の基礎を身につける
    4. **感情をコントロール**: 冷静な判断を心がける
    
    #### 💡 銘柄選択のコツ
    - **成長性**: 将来の事業拡大が期待できるか
    - **安定性**: 業績が安定しているか
    - **割安性**: 現在の株価は適正か
    
    #### 📱 このアプリの活用方法
    1. **検索機能**: 気になる企業を検索
    2. **AI判断**: 投資タイミングの参考に
    3. **バックテスト**: 投資戦略の検証
    4. **ポートフォリオ**: 保有銘柄の管理
    
    #### ⚠️ 注意事項
    - このアプリは教育目的です
    - 投資判断は自己責任で行ってください
    - リスクを理解した上で投資してください
    """)
```

if **name** == “**main**”:
main()
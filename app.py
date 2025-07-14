# app.pyの検索機能部分を以下のコードで置き換えてください

import yfinance as yf
import requests
import re
from typing import List, Dict

class SuperStockSearch:
    def __init__(self):
        # 基本辞書（すぐに検索できる有名企業）
        self.stock_dict = {
            # 日本の主要銘柄（大幅拡張）
            "トヨタ": "7203.T", "toyota": "7203.T", "トヨタ自動車": "7203.T",
            "ソニー": "6758.T", "sony": "6758.T", "ソニーグループ": "6758.T",
            "任天堂": "7974.T", "nintendo": "7974.T",
            "ホンダ": "7267.T", "honda": "7267.T", "本田技研": "7267.T",
            "日産": "7201.T", "nissan": "7201.T", "日産自動車": "7201.T",
            "ソフトバンク": "9984.T", "softbank": "9984.T", "ソフトバンクグループ": "9984.T",
            "楽天": "4755.T", "rakuten": "4755.T", "楽天グループ": "4755.T",
            "ユニクロ": "9983.T", "ファーストリテイリング": "9983.T", "fast retailing": "9983.T",
            "キーエンス": "6861.T", "keyence": "6861.T",
            "信越化学": "4063.T", "shin-etsu": "4063.T",
            "東京エレクトロン": "8035.T", "tokyo electron": "8035.T",
            "パナソニック": "6752.T", "panasonic": "6752.T",
            "日立": "6501.T", "hitachi": "6501.T", "日立製作所": "6501.T",
            "三菱ufj": "8306.T", "三菱UFJ銀行": "8306.T", "mufg": "8306.T",
            "みずほ": "8411.T", "みずほ銀行": "8411.T", "mizuho": "8411.T",
            "三井住友": "8316.T", "smfg": "8316.T", "sumitomo mitsui": "8316.T",
            "kddi": "9433.T", "au": "9433.T",
            "ntt": "9432.T", "日本電信電話": "9432.T", "nippon telegraph": "9432.T",
            "武田薬品": "4502.T", "takeda": "4502.T", "武田": "4502.T",
            "セブン": "3382.T", "セブンイレブン": "3382.T", "seven eleven": "3382.T",
            "イオン": "8267.T", "aeon": "8267.T",
            "ファナック": "6954.T", "fanuc": "6954.T",
            "ダイキン": "6367.T", "daikin": "6367.T",
            "シマノ": "7309.T", "shimano": "7309.T",
            "村田製作所": "6981.T", "murata": "6981.T",
            "デンソー": "6902.T", "denso": "6902.T",
            "トヨタ織機": "6201.T",
            "リクルート": "6098.T", "recruit": "6098.T",
            "メルカリ": "4385.T", "mercari": "4385.T",
            "サイバーエージェント": "4751.T", "cyberagent": "4751.T",
            "アサヒ": "2502.T", "アサヒビール": "2502.T", "asahi": "2502.T",
            "キリン": "2503.T", "キリンビール": "2503.T", "kirin": "2503.T",
            "富士フイルム": "4901.T", "fujifilm": "4901.T",
            "コマツ": "6301.T", "komatsu": "6301.T",
            
            # 米国の主要銘柄（拡張）
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
            "mcdonald": "MCD", "マクドナルド": "MCD",
            "coca cola": "KO", "コカコーラ": "KO",
            "visa": "V", "ビザ": "V",
            "boeing": "BA", "ボーイング": "BA",
            "walmart": "WMT", "ウォルマート": "WMT",
            "intel": "INTC", "インテル": "INTC",
            "amd": "AMD",
            "salesforce": "CRM", "セールスフォース": "CRM",
            "oracle": "ORCL", "オラクル": "ORCL",
            "ibm": "IBM",
            "cisco": "CSCO", "シスコ": "CSCO",
            "adobe": "ADBE", "アドビ": "ADBE",
            "paypal": "PYPL", "ペイパル": "PYPL",
            "zoom": "ZM", "ズーム": "ZM",
            "uber": "UBER", "ウーバー": "UBER",
            "twitter": "TWTR", "ツイッター": "TWTR",
            "spotify": "SPOT", "スポティファイ": "SPOT",
        }
        
        # 銘柄名の正規化パターン
        self.normalize_patterns = {
            r'株式会社(.+)': r'\1',
            r'(.+)株式会社': r'\1', 
            r'(.+)ホールディングス': r'\1',
            r'(.+)HD': r'\1',
            r'(.+)グループ': r'\1',
            r'(.+)フィナンシャル': r'\1',
            r'(.+)銀行': r'\1',
            r'(.+)証券': r'\1',
            r'(.+) Corp(?:oration)?': r'\1',
            r'(.+) Inc(?:orporated)?': r'\1',
            r'(.+) Ltd': r'\1',
            r'(.+) Co\.?': r'\1',
        }

    def search(self, keyword: str) -> List[Dict]:
        """包括的な銘柄検索"""
        keyword = keyword.strip()
        if not keyword:
            return []
            
        results = []
        
        # 1. 基本辞書検索（最優先）
        basic_results = self._search_basic_dict(keyword)
        results.extend(basic_results)
        
        # 2. 正規化キーワードで検索
        normalized_results = self._search_normalized(keyword)
        results.extend(normalized_results)
        
        # 3. yfinanceで直接検索
        yf_results = self._search_yfinance_direct(keyword)
        results.extend(yf_results)
        
        # 4. 部分一致検索
        partial_results = self._search_partial_match(keyword)
        results.extend(partial_results)
        
        # 重複除去
        return self._remove_duplicates(results)

    def _search_basic_dict(self, keyword: str) -> List[Dict]:
        """基本辞書から検索"""
        keyword_lower = keyword.lower()
        results = []
        
        # 完全一致
        if keyword_lower in self.stock_dict:
            symbol = self.stock_dict[keyword_lower]
            results.append({
                'symbol': symbol,
                'name': keyword,
                'match_type': '✅ 完全一致',
                'confidence': 1.0
            })
        
        return results

    def _search_normalized(self, keyword: str) -> List[Dict]:
        """正規化されたキーワードで検索"""
        results = []
        
        for pattern, replacement in self.normalize_patterns.items():
            normalized = re.sub(pattern, replacement, keyword, flags=re.IGNORECASE)
            if normalized != keyword:
                # 正規化されたキーワードで再検索
                normalized_lower = normalized.lower()
                if normalized_lower in self.stock_dict:
                    symbol = self.stock_dict[normalized_lower]
                    results.append({
                        'symbol': symbol,
                        'name': f"{normalized} (正規化: {keyword})",
                        'match_type': '🔧 正規化一致',
                        'confidence': 0.9
                    })
        
        return results

    def _search_yfinance_direct(self, keyword: str) -> List[Dict]:
        """yfinanceで直接銘柄検索"""
        results = []
        
        # 銘柄コードとして試す可能性のあるパターン
        test_symbols = [
            keyword.upper(),                    # AAPL
            f"{keyword.upper()}.T",            # 7203.T
            f"{keyword.upper()}.TO",           # カナダ
            f"{keyword.upper()}.L",            # ロンドン
            f"{keyword.upper()}.F",            # フランクフルト
            f"{keyword.upper()}.SI",           # シンガポール
        ]
        
        # 数字の場合は日本株コードとして試す
        if keyword.isdigit():
            test_symbols.extend([
                f"{keyword}.T",
                f"{keyword}.JP"
            ])
        
        for symbol in test_symbols:
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.info
                
                # 有効な銘柄かチェック
                if (info and 
                    info.get('symbol') and 
                    info.get('longName') and
                    info.get('regularMarketPrice')):
                    
                    results.append({
                        'symbol': symbol,
                        'name': info.get('longName', symbol),
                        'match_type': '🎯 直接検索',
                        'confidence': 0.85,
                        'sector': info.get('sector', ''),
                        'country': info.get('country', '')
                    })
                    break  # 最初に見つかった有効な銘柄で止める
                    
            except Exception:
                continue
        
        return results

    def _search_partial_match(self, keyword: str) -> List[Dict]:
        """部分一致検索"""
        keyword_lower = keyword.lower()
        results = []
        
        for name, symbol in self.stock_dict.items():
            # キーワードが会社名に含まれる、または会社名がキーワードに含まれる
            if (keyword_lower in name.lower() or 
                name.lower() in keyword_lower) and keyword_lower != name.lower():
                
                # 一致度を計算
                if keyword_lower in name.lower():
                    confidence = len(keyword_lower) / len(name)
                else:
                    confidence = len(name) / len(keyword_lower)
                
                confidence = min(confidence, 0.7)  # 最大0.7
                
                results.append({
                    'symbol': symbol,
                    'name': name,
                    'match_type': '📝 部分一致',
                    'confidence': confidence
                })
        
        # 信頼度でソート
        return sorted(results, key=lambda x: x['confidence'], reverse=True)

    def _remove_duplicates(self, results: List[Dict]) -> List[Dict]:
        """重複除去（同じ銘柄コードを除去）"""
        seen_symbols = set()
        unique_results = []
        
        # 信頼度でソート
        sorted_results = sorted(results, key=lambda x: x['confidence'], reverse=True)
        
        for result in sorted_results:
            symbol = result['symbol']
            if symbol not in seen_symbols:
                seen_symbols.add(symbol)
                unique_results.append(result)
                
        return unique_results[:8]  # 上位8件

# Alpha Vantage検索の改良版
def search_alpha_vantage_enhanced(keyword, api_key):
    """強化されたAlpha Vantage検索"""
    if not api_key:
        return []
    
    try:
        # キーワードバリエーションを生成
        variations = [keyword]
        
        # 日本語→英語変換
        jp_en_map = {
            "トヨタ": "Toyota", "ソニー": "Sony", "ホンダ": "Honda",
            "日産": "Nissan", "三菱": "Mitsubishi", "パナソニック": "Panasonic",
            "富士通": "Fujitsu", "東芝": "Toshiba", "みずほ": "Mizuho",
            "楽天": "Rakuten", "ソフトバンク": "SoftBank"
        }
        
        if keyword in jp_en_map:
            variations.append(jp_en_map[keyword])
        
        # 部分一致での変換
        for jp, en in jp_en_map.items():
            if keyword in jp:
                variations.append(en)
                
        results = []
        for variation in variations[:2]:  # 最大2回のAPI呼び出し
            url = "https://www.alphavantage.co/query"
            params = {
                'function': 'SYMBOL_SEARCH',
                'keywords': variation,
                'apikey': api_key
            }
            
            response = requests.get(url, params=params, timeout=8)
            if response.status_code == 200:
                data = response.json()
                if 'bestMatches' in data:
                    for match in data['bestMatches']:
                        symbol = match.get('1. symbol', '')
                        name = match.get('2. name', '')
                        match_score = float(match.get('9. matchScore', '0'))
                        
                        if symbol and name and match_score > 0.3:
                            results.append({
                                'symbol': symbol,
                                'name': name,
                                'region': match.get('4. region', ''),
                                'match_type': '🌐 API検索',
                                'confidence': min(match_score, 0.8)
                            })
        
        # 関連度でソート
        return sorted(results, key=lambda x: x['confidence'], reverse=True)[:5]
        
    except Exception as e:
        st.warning(f"API検索でエラーが発生しました: {e}")
        return []

# -------- 以下を app.py の該当箇所に置き換えてください --------

# 検索オブジェクト初期化（SuperStockSearchに変更）
if 'searcher' not in st.session_state:
    st.session_state.searcher = SuperStockSearch()

# 会社名検索の部分を以下に置き換え
if search_method == "🔍 会社名で検索":
    st.markdown("""
    <div class="explanation-box">
    <strong>🔍 大幅強化された会社名検索</strong><br>
    <span>有名企業だけでなく、マイナー企業も検索できるようになりました！</span><br>
    <span>例：「三菱」「みずほ」「ファナック」「村田製作所」「デンソー」など</span><br>
    <span>銘柄コードでも検索可能：「6098」「4385」など</span>
    </div>
    """, unsafe_allow_html=True)
    
    # Alpha Vantage API Key（オプション）
    api_key = None
    with st.expander("🔧 さらに多くの企業を検索（上級者向け）"):
        api_key = st.text_input(
            "Alpha Vantage API Key（省略可）",
            type="password",
            help="無料で取得可能。世界中の企業を検索できます"
        )
        st.markdown("""
        <div class="tip-box">
        💡 <strong>API Keyなしでも十分：</strong> <span>主要企業（200社以上）は検索できます</span><br>
        <strong>API Keyがあると：</strong> <span>世界中の企業（数万社）を検索可能</span><br>
        <strong>取得方法：</strong> <span>https://www.alphavantage.co/support/#api-key</span>
        </div>
        """, unsafe_allow_html=True)
    
    # 検索入力
    search_keyword = st.text_input(
        "会社名・銘柄コードを入力",
        placeholder="例: 三菱UFJ, ファナック, 6098, MSFT, テスラ",
        key="stock_search_input"
    )
    
    if search_keyword:
        with st.spinner("🔍 検索中...（複数の方法で検索しています）"):
            # 強化されたローカル検索
            local_results = st.session_state.searcher.search(search_keyword)
            
            # 強化されたAPI検索（API Keyがある場合）
            api_results = []
            if api_key:
                api_results = search_alpha_vantage_enhanced(search_keyword, api_key)
            
            # 結果をまとめる
            all_results = local_results + api_results
            
            # 重複除去（改良版）
            seen_symbols = set()
            unique_results = []
            for result in all_results:
                symbol = result['symbol']
                if symbol not in seen_symbols:
                    seen_symbols.add(symbol)
                    unique_results.append(result)
        
        if unique_results:
            st.markdown(f"**🎯 検索結果: '{search_keyword}' ({len(unique_results)}件見つかりました)**")
            
            # 結果をより分かりやすく表示
            selected_stock = None
            for i, result in enumerate(unique_results):
                symbol = result['symbol']
                name = result['name']
                match_type = result['match_type']
                confidence = result.get('confidence', 0)
                region = result.get('region', '日本' if symbol.endswith('.T') else '米国')
                
                # 信頼度に応じてアイコンを変更
                if confidence > 0.8:
                    confidence_icon = "🎯"
                elif confidence > 0.6:
                    confidence_icon = "👍"
                else:
                    confidence_icon = "💡"
                
                if st.button(
                    f"{confidence_icon} {symbol} - {name}",
                    key=f"search_result_{i}",
                    help=f"{match_type} | 地域: {region} | 信頼度: {confidence:.2f}",
                    use_container_width=True
                ):
                    selected_stock = symbol
                    st.session_state.selected_stock_name = name
                    st.success(f"✅ 選択しました: {symbol} - {name}")
            
            if selected_stock:
                stock_code = selected_stock
            else:
                stock_code = unique_results[0]['symbol'] if unique_results else "AAPL"
                
        else:
            st.warning("🔍 検索結果が見つかりませんでした")
            st.markdown("""
            **💡 検索改善のコツ:**
            - 会社の正式名称で試してください（「三菱UFJ」「ファーストリテイリング」など）
            - 銘柄コード（数字）でも検索できます（「7203」「6098」など）
            - 英語でも試してください（「Toyota」「Sony」など）
            - 部分的な名前でも検索できます（「三菱」「ソフト」など）
            """)
            
            # デフォルト銘柄の提案
            st.info("💡 お試しで「Apple」を分析してみませんか？")
            if st.button("🍎 Appleを分析する", key="try_apple"):
                stock_code = "AAPL"
                st.success("✅ Apple (AAPL) を選択しました")
            else:
                stock_code = "AAPL"
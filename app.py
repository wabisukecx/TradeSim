import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import ta
from scipy import stats
import requests

# スマホ最適化ページ設定
st.set_page_config(
    page_title="📱 株価分析学習アプリ（教育専用）",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# カスタムCSS（スマホ最適化・視認性大幅改善）
st.markdown("""
<style>
    /* 全体的なテキストの視認性向上 */
    .main-header {
        text-align: center;
        padding: 1.2rem 0;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white !important;
        margin: -1rem -1rem 2rem -1rem;
        border-radius: 0 0 1rem 1rem;
        font-weight: bold;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .metric-card {
        background: #ffffff !important;
        padding: 1.2rem;
        border-radius: 0.8rem;
        margin: 0.8rem 0;
        border: 2px solid #667eea !important;
        color: #000000 !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    /* 解説ボックスの大幅改善 */
    .explanation-box {
        background: #ffffff !important;
        border: 3px solid #2196F3 !important;
        padding: 1.2rem !important;
        border-radius: 1rem !important;
        margin: 1rem 0 !important;
        color: #000000 !important;
        font-weight: 600 !important;
        font-size: 1.05rem !important;
        line-height: 1.6 !important;
        box-shadow: 0 4px 12px rgba(33, 150, 243, 0.15) !important;
    }
    
    .explanation-box strong {
        color: #1565C0 !important;
        font-weight: 700 !important;
        font-size: 1.1rem !important;
    }
    
    .explanation-box span {
        color: #000000 !important;
        font-weight: 500 !important;
    }
    
    /* Tipボックスの大幅改善 */
    .tip-box {
        background: #fff8e1 !important;
        border: 3px solid #ff9800 !important;
        padding: 1.2rem !important;
        border-radius: 1rem !important;
        margin: 1rem 0 !important;
        color: #000000 !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        line-height: 1.6 !important;
        box-shadow: 0 4px 12px rgba(255, 152, 0, 0.15) !important;
    }
    
    .tip-box strong {
        color: #e65100 !important;
        font-weight: 700 !important;
        font-size: 1.05rem !important;
    }
    
    .tip-box span {
        color: #000000 !important;
        font-weight: 500 !important;
    }
    
    /* 免責事項の強調 */
    .disclaimer-box {
        background: #ffebee !important;
        border: 3px solid #f44336 !important;
        padding: 1.2rem !important;
        border-radius: 1rem !important;
        margin: 1rem 0 !important;
        color: #000000 !important;
        font-weight: 700 !important;
        font-size: 1.1rem !important;
        line-height: 1.6 !important;
        box-shadow: 0 4px 12px rgba(244, 67, 54, 0.15) !important;
    }
    
    /* すべてのテキストを強制的に黒色に */
    .explanation-box *, .tip-box *, .disclaimer-box * {
        color: #000000 !important;
    }
    
    .big-button {
        width: 100%;
        padding: 1.2rem;
        font-size: 1.3rem;
        margin: 1rem 0;
        font-weight: bold;
        border-radius: 0.8rem;
    }
    
    /* ダークモード対応（コントラスト重視） */
    @media (prefers-color-scheme: dark) {
        .explanation-box {
            background: #1a1a1a !important;
            border: 3px solid #64b5f6 !important;
            color: #ffffff !important;
        }
        .explanation-box strong {
            color: #90caf9 !important;
        }
        .explanation-box *, .explanation-box span {
            color: #ffffff !important;
        }
        .tip-box {
            background: #2d2d2d !important;
            border: 3px solid #ffb74d !important;
            color: #ffffff !important;
        }
        .tip-box strong {
            color: #ffcc02 !important;
        }
        .tip-box *, .tip-box span {
            color: #ffffff !important;
        }
        .disclaimer-box {
            background: #3d2d2d !important;
            border: 3px solid #ff6b6b !important;
            color: #ffffff !important;
        }
        .disclaimer-box * {
            color: #ffffff !important;
        }
        .metric-card {
            background: #2d2d2d !important;
            color: #ffffff !important;
            border: 2px solid #64b5f6 !important;
        }
    }
    
    /* スマホ向けレスポンシブ */
    @media (max-width: 768px) {
        .explanation-box, .tip-box, .disclaimer-box {
            font-size: 1rem !important;
            padding: 1rem !important;
            margin: 0.8rem 0 !important;
        }
        .main-header h1 {
            font-size: 1.6rem !important;
        }
        .main-header p {
            font-size: 1rem !important;
        }
    }
    
    /* Streamlitのデフォルトテキストも改善 */
    .stMarkdown {
        color: inherit !important;
    }
    
    /* エクスパンダー内のテキストも改善 */
    .streamlit-expanderHeader {
        font-weight: bold !important;
    }
</style>
""", unsafe_allow_html=True)

# --- ヘッダー ---
st.markdown("""
<div class="main-header">
    <h1>📱 株価分析学習アプリ</h1>
    <p>🔰 教育・学習専用ツール</p>
</div>
""", unsafe_allow_html=True)

# === データ検証機能 ===
def validate_stock_data(df, symbol):
    """株価データの妥当性検証"""
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
    if close_na_ratio > 0.1:
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

def safe_fetch_stock_data(symbol, start, end):
    """安全な株価データ取得（検証付き）"""
    try:
        stock = yf.Ticker(symbol)
        df = stock.history(start=start, end=end)
        info = stock.info
        
        # データ検証
        validate_stock_data(df, symbol)
        
        return df, info
    except ValueError as ve:
        st.error(f"❌ データ検証エラー: {ve}")
        return None, None
    except Exception as e:
        st.error(f"❌ データ取得エラー: {e}")
        return None, None

# --- 初心者向けガイド ---
with st.expander("🔰 このアプリって何？（初心者必読！）", expanded=False):
    st.markdown("""
    ### 📚 このアプリでできること
    
    **株って何？**  
    株は「会社の一部を買うこと」です。例えば、トヨタの株を買うと、トヨタの会社の小さな持ち主になれます！
    
    **このアプリの使い方**
    1. 📈 **会社を選ぶ** → 気になる会社の株価を調べる
    2. 🔍 **分析する** → その会社の株価の動きを学習する
    3. 💡 **参考情報を見る** → 分析結果を参考情報として確認する
    4. 💼 **ポートフォリオ** → 気になる会社をリストに保存できる
    """)
    
    st.markdown("""
    <div class="disclaimer-box">
    <strong>⚠️ とっても大切なこと</strong><br>
    • これは教育・学習用のアプリです<br>
    • 投資助言や推奨ではありません<br>
    • 実際の投資判断は自己責任で行ってください<br>
    • 投資前には必ず専門家にご相談ください<br>
    • 株価は上がったり下がったりするのが普通です
    </div>
    """, unsafe_allow_html=True)

# --- Streamlit セッション状態の初期化 ---
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = {}

# 分析結果の保存用セッション状態を初期化
if 'analysis_data' not in st.session_state:
    st.session_state.analysis_data = None

if 'current_stock_code' not in st.session_state:
    st.session_state.current_stock_code = None

if 'current_company_name' not in st.session_state:
    st.session_state.current_company_name = None

# --- 銘柄検索機能 ---
class LocalStockSearch:
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
            "信越化学": "4063.T",
            "東京エレクトロン": "8035.T",
            "パナソニック": "6752.T", "panasonic": "6752.T",
            "日立": "6501.T", "hitachi": "6501.T", "日立製作所": "6501.T",
            "三菱ufj": "8306.T", "三菱UFJ銀行": "8306.T",
            "kddi": "9433.T",
            "ntt": "9432.T", "日本電信電話": "9432.T",
            "武田薬品": "4502.T", "takeda": "4502.T",
            "セブン": "3382.T", "セブンイレブン": "3382.T",
            "イオン": "8267.T", "aeon": "8267.T",
            
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
            "mcdonald": "MCD", "マクドナルド": "MCD",
            "coca cola": "KO", "コカコーラ": "KO",
            "visa": "V", "ビザ": "V",
            "boeing": "BA", "ボーイング": "BA",
            "walmart": "WMT", "ウォルマート": "WMT",
        }
    
    def search(self, keyword):
        """キーワードから銘柄コードを検索"""
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

def search_alpha_vantage(keyword, api_key):
    """Alpha Vantage APIで銘柄検索"""
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
    except:
        return []

# 検索オブジェクト初期化
if 'searcher' not in st.session_state:
    st.session_state.searcher = LocalStockSearch()

# --- メイン設定エリア ---
with st.expander("⚙️ 分析設定（どの会社を調べる？）", expanded=True):
    st.markdown("### 📍 会社を選ぼう")
    
    # 検索方法の選択
    search_method = st.radio(
        "検索方法を選んでね",
        ["🔍 会社名で検索", "📋 人気の会社から選ぶ", "⌨️ コードを直接入力"],
        horizontal=True
    )

    if search_method == "🔍 会社名で検索":
        st.markdown("""
        <div class="explanation-box">
        <strong>🔍 会社名検索</strong><br>
        <span>知っている会社の名前を入力すると、銘柄コードを自動で見つけてくれます！</span><br>
        <span>例：「トヨタ」「Apple」「任天堂」「テスラ」など</span>
        </div>
        """, unsafe_allow_html=True)
        
        # Alpha Vantage API Key（オプション）
        api_key = None
        
        # expanderの代わりにtoggleを使用
        show_advanced_search = st.toggle("🔧 より多くの検索結果を得る（上級者向け）")
        
        if show_advanced_search:
            api_key = st.text_input(
                "Alpha Vantage API Key（省略可）",
                type="password",
                help="無料で取得可能。より多くの会社を検索できます"
            )
            st.markdown("""
            <div class="tip-box">
            💡 <strong>API Keyなしでも大丈夫：</strong> <span>主要な会社は検索できます</span><br>
            <strong>API Keyがあると：</strong> <span>世界中の会社を検索できます</span><br>
            <strong>取得方法：</strong> <span>https://www.alphavantage.co/support/#api-key で無料取得</span>
            </div>
            """, unsafe_allow_html=True)
        
        # 検索入力
        search_keyword = st.text_input(
            "会社名を入力してください",
            placeholder="例: トヨタ, Apple, 任天堂, Tesla",
            key="stock_search_input"
        )
        
        if search_keyword:
            with st.spinner("🔍 検索中..."):
                # ローカル検索
                local_results = st.session_state.searcher.search(search_keyword)
                
                # API検索（API Keyがある場合）
                api_results = []
                if api_key:
                    api_results = search_alpha_vantage(search_keyword, api_key)
                
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
            
            if unique_results:
                st.markdown(f"**🎯 検索結果: '{search_keyword}'**")
                
                # 結果をボタンで表示
                selected_stock = None
                for i, result in enumerate(unique_results):
                    symbol = result['symbol']
                    name = result['name']
                    match_type = result['match_type']
                    region = result.get('region', '日本' if symbol.endswith('.T') else '米国')
                    
                    if st.button(
                        f"📈 {symbol} - {name} ({region})",
                        key=f"search_result_{i}",
                        help=f"マッチタイプ: {match_type}"
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
                **💡 検索のコツ:**
                - 会社の正式名称で試してみてください
                - 英語と日本語両方で試してみてください  
                - 略称でも検索できます
                """)
                stock_code = "AAPL"

    elif search_method == "📋 人気の会社から選ぶ":
        st.markdown("""
        <div class="explanation-box">
        <strong>📋 人気銘柄から選択</strong><br>
        <span>よく注目される人気の会社から選べます（学習目的）</span>
        </div>
        """, unsafe_allow_html=True)
        
        popular_stocks = {
            "🚗 トヨタ自動車（世界最大の自動車メーカー）": "7203.T",
            "🎮 ソニーグループ（ゲーム・音楽・映画）": "6758.T",
            "🎯 任天堂（ゲーム会社の王者）": "7974.T",
            "🍎 Apple（iPhone・Mac作ってる会社）": "AAPL",
            "🚗 Tesla（電気自動車のパイオニア）": "TSLA",
            "💻 Microsoft（Windows・Office）": "MSFT",
            "🎮 NVIDIA（AI・ゲーム用チップ）": "NVDA",
            "🔍 Google（検索エンジン・YouTube）": "GOOGL",
            "📦 Amazon（ネットショッピング最大手）": "AMZN",
            "📱 Meta（Facebook・Instagram）": "META"
        }
        
        selected = st.selectbox(
            "会社を選んでね",
            list(popular_stocks.keys())
        )
        stock_code = popular_stocks[selected]
        st.info(f"選択中: **{selected}** ({stock_code})")

    elif search_method == "⌨️ コードを直接入力":  # コード直接入力
        st.markdown("""
        <div class="explanation-box">
        <strong>⌨️ 銘柄コード直接入力</strong><br>
        <span>すでに銘柄コードを知っている場合はこちら</span>
        </div>
        """, unsafe_allow_html=True)
        
        stock_code = st.text_input(
            "銘柄コード",
            "AAPL",
            placeholder="例: AAPL, 7203.T, TSLA"
        )
        st.markdown("""
        <div class="tip-box">
        💡 <strong>ヒント：</strong> <span>日本の会社は最後に「.T」が付きます（例：7203.T）</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("### 📅 どのくらいの期間を調べる？")
    st.markdown("""
    <div class="explanation-box">
    <strong>📊 期間の選び方</strong><br>
    <span>短い期間 → 最近の動きがよく分かる</span><br>
    <span>長い期間 → 大きな流れ（トレンド）が分かる</span>
    </div>
    """, unsafe_allow_html=True)
    
    period_options = {
        "1ヶ月": 30,
        "3ヶ月": 90,
        "6ヶ月": 180,
        "1年": 365,
        "2年": 730
    }
    selected_period = st.select_slider(
        "期間を選んでね",
        options=list(period_options.keys()),
        value="6ヶ月"
    )
    days = period_options[selected_period]
    start_date = datetime.now() - timedelta(days=days)
    end_date = datetime.now()

# --- 詳細設定（折りたたみ） ---
with st.expander("🔧 詳細設定（上級者向け）"):
    st.markdown("#### 📈 テクニカル指標（株価の動きを分析する道具）")
    
    st.markdown("""
    <div class="explanation-box">
    <strong>🔬 テクニカル指標って何？</strong><br>
    <span>株価のグラフを見て「動きのパターン」を数値化する道具です。</span><br>
    <span>数学を使って、人間には見えにくいパターンを可視化してくれます！</span>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**短期移動平均**")
        short_ma = st.slider("短期移動平均", 5, 50, 20)
        st.markdown("""
        <div class="tip-box">
        📊 <strong>これは何？</strong> <span>最近の株価の平均です</span><br>
        <strong>⬆️ 高くすると：</strong> <span>ゆっくり動く線になる</span><br>
        <strong>⬇️ 低くすると：</strong> <span>素早く動く線になる</span><br>
        <strong>👍 おすすめ：</strong> <span>初心者は20のままでOK</span>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("**RSI（人気度指標）**")
        rsi_period = st.slider("RSI期間", 5, 30, 14)
        st.markdown("""
        <div class="tip-box">
        📊 <strong>これは何？</strong> <span>株の「人気度」を0-100で表示</span><br>
        <strong>⬆️ 高くすると：</strong> <span>ゆっくり反応する（安定）</span><br>
        <strong>⬇️ 低くすると：</strong> <span>素早く反応する（敏感）</span><br>
        <strong>👍 おすすめ：</strong> <span>14のままでOK</span>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown("**長期移動平均**")
        long_ma = st.slider("長期移動平均", 20, 200, 50)
        st.markdown("""
        <div class="tip-box">
        📊 <strong>これは何？</strong> <span>長い期間の株価の平均です</span><br>
        <strong>⬆️ 高くすると：</strong> <span>とてもゆっくり動く線</span><br>
        <strong>⬇️ 低くすると：</strong> <span>少し早く動く線</span><br>
        <strong>👍 おすすめ：</strong> <span>短期より大きい数字にする</span>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("**ボリンジャーバンド期間**")
        bb_period = st.slider("BB期間", 10, 30, 20)
        st.markdown("""
        <div class="tip-box">
        📊 <strong>これは何？</strong> <span>株価の「普通の範囲」を表示する線</span><br>
        <strong>⬆️ 高くすると：</strong> <span>広い範囲を「普通」と判断</span><br>
        <strong>⬇️ 低くすると：</strong> <span>狭い範囲を「普通」と判断</span><br>
        <strong>👍 おすすめ：</strong> <span>20のままでOK</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("#### 💰 学習シミュレーション設定")
    
    st.markdown("""
    <div class="explanation-box">
    <strong>🎮 学習シミュレーションって何？</strong><br>
    <span>「もしこのルールで取引していたら、結果はどうなっていた？」を計算してくれます。</span><br>
    <span>実際のお金は使わないので安心です！教育目的のシミュレーションです。</span>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**仮想初期資金**")
        initial_capital = st.number_input(
            "仮想初期資金（万円）",
            10, 1000, 100, 10,
            format="%d"
        ) * 10000
        st.markdown("""
        <div class="tip-box">
        💰 <strong>これは何？</strong> <span>シミュレーション開始時の仮想資金</span><br>
        <strong>⬆️ 多くすると：</strong> <span>大きく変動する結果になる</span><br>
        <strong>⬇️ 少なくすると：</strong> <span>小さく変動する結果になる</span>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("**リスク許容率**")
        risk_per_trade = st.slider("リスク許容率(%)", 0.5, 5.0, 2.0, 0.5)
        st.markdown("""
        <div class="tip-box">
        ⚡ <strong>これは何？</strong> <span>1回の取引でどのくらいリスクを取るか</span><br>
        <strong>⬆️ 高くすると：</strong> <span>積極的な取引（ハイリスク）</span><br>
        <strong>⬇️ 低くすると：</strong> <span>慎重な取引（ローリスク）</span><br>
        <strong>👍 おすすめ：</strong> <span>初心者は2%以下</span>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown("**損切り率**")
        stop_loss_pct = st.slider("損切り率(%)", 1.0, 20.0, 5.0, 0.5)
        st.markdown("""
        <div class="tip-box">
        🛡️ <strong>これは何？</strong> <span>「これ以上下がったら売る」というルール</span><br>
        <strong>⬆️ 高くすると：</strong> <span>我慢強く保有し続ける</span><br>
        <strong>⬇️ 低くすると：</strong> <span>早めに損切りする</span><br>
        <strong>👍 おすすめ：</strong> <span>5-10%が一般的</span>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("**利益確定率**")
        take_profit_pct = st.slider("利益確定率(%)", 2.0, 50.0, 15.0, 1.0)
        st.markdown("""
        <div class="tip-box">
        🎯 <strong>これは何？</strong> <span>「これだけ上がったら売る」というルール</span><br>
        <strong>⬆️ 高くすると：</strong> <span>長期保有（もっと上がるまで待つ）</span><br>
        <strong>⬇️ 低くすると：</strong> <span>早めに利益確定（少し上がったら売る）</span><br>
        <strong>👍 おすすめ：</strong> <span>損切り率の2-3倍</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("**取引手数料率**")
    trade_cost_rate = st.slider("取引手数料率(%)", 0.0, 1.0, 0.1, 0.01)
    st.markdown("""
    <div class="tip-box">
    💳 <strong>これは何？</strong> <span>株を買ったり売ったりする時の手数料</span><br>
    <strong>⬆️ 高くすると：</strong> <span>現実的だけど、利益が減る</span><br>
    <strong>⬇️ 低くすると：</strong> <span>理想的だけど、現実とは違う</span><br>
    <strong>👍 おすすめ：</strong> <span>0.1%（大手ネット証券の平均）</span>
    </div>
    """, unsafe_allow_html=True)

# --- データ処理関数 ---
@st.cache_data
def fetch_stock_data(symbol, start, end):
    try:
        return safe_fetch_stock_data(symbol, start, end)
    except Exception as e:
        st.error(f"データ取得エラー: {e}")
        return None, None

def calculate_indicators(df, short_window, long_window, rsi_window, bb_window):
    df['MA_short'] = ta.trend.sma_indicator(df['Close'], window=short_window)
    df['MA_long'] = ta.trend.sma_indicator(df['Close'], window=long_window)
    df['RSI'] = ta.momentum.rsi(df['Close'], window=rsi_window)

    bb = ta.volatility.BollingerBands(df['Close'], window=bb_window, window_dev=2)
    df['BB_upper'] = bb.bollinger_hband()
    df['BB_middle'] = bb.bollinger_mavg()
    df['BB_lower'] = bb.bollinger_lband()

    macd = ta.trend.MACD(df['Close'])
    df['MACD'] = macd.macd()
    df['MACD_signal'] = macd.macd_signal()
    df['MACD_diff'] = macd.macd_diff()

    df['Volume_MA'] = df['Volume'].rolling(window=20).mean()
    df['ATR'] = ta.volatility.average_true_range(df['High'], df['Low'], df['Close'])

    return df

def generate_signals_advanced(df):
    signals = pd.DataFrame(index=df.index)
    # 浮動小数点数で初期化してdtype警告を回避
    signals['buy_score'] = 0.0
    signals['sell_score'] = 0.0

    signals.loc[df['MA_short'] > df['MA_long'], 'buy_score'] += 1.0
    signals.loc[df['MA_short'] < df['MA_long'], 'sell_score'] += 1.0

    signals.loc[df['RSI'] < 35, 'buy_score'] += 1.0
    signals.loc[df['RSI'] > 65, 'sell_score'] += 1.0

    signals.loc[df['Close'] < df['BB_lower'], 'buy_score'] += 1.5
    signals.loc[df['Close'] > df['BB_upper'], 'sell_score'] += 1.5

    signals.loc[(df['MACD'] > df['MACD_signal']) & (df['MACD'].shift(1) < df['MACD_signal'].shift(1)), 'buy_score'] += 1.5
    signals.loc[(df['MACD'] < df['MACD_signal']) & (df['MACD'].shift(1) > df['MACD_signal'].shift(1)), 'sell_score'] += 1.5

    signals.loc[df['Volume'] > df['Volume_MA'], 'buy_score'] += 0.5
    signals.loc[df['Volume'] > df['Volume_MA'], 'sell_score'] += 0.5

    buy_threshold = 2.5
    sell_threshold = 2.5
    signals['signal'] = 0
    signals.loc[signals['buy_score'] >= buy_threshold, 'signal'] = 1
    signals.loc[signals['sell_score'] >= sell_threshold, 'signal'] = -1

    return signals

def backtest_realistic(df, signals, initial_capital, risk_pct, stop_loss_pct, take_profit_pct, cost_pct):
    cash = initial_capital
    position = 0
    entry_price = 0
    portfolio_values = []
    trade_log = []

    cost_rate = cost_pct / 100.0

    for i in range(len(df)):
        current_price = df['Close'].iloc[i]
        signal = signals['signal'].iloc[i]

        if position > 0:
            stop_loss_price = entry_price * (1 - stop_loss_pct / 100.0)
            take_profit_price = entry_price * (1 + take_profit_pct / 100.0)

            if current_price <= stop_loss_price or current_price >= take_profit_price or signal == -1:
                revenue = position * current_price * (1 - cost_rate)
                cash += revenue
                trade_log.append({'Date': df.index[i], 'Type': 'Sell', 'Price': current_price, 'Shares': position, 'Portfolio': cash})
                position = 0
                entry_price = 0

        if position == 0 and signal == 1:
            risk_per_share = current_price - (current_price * (1 - stop_loss_pct / 100.0))
            if risk_per_share > 0:
                capital_at_risk = cash * (risk_pct / 100.0)
                shares_to_buy = int(capital_at_risk / risk_per_share)

                cost = shares_to_buy * current_price * (1 + cost_rate)

                if shares_to_buy > 0 and cash >= cost:
                    position = shares_to_buy
                    entry_price = current_price
                    cash -= cost
                    trade_log.append({'Date': df.index[i], 'Type': 'Buy', 'Price': current_price, 'Shares': position, 'Portfolio': cash + position * current_price})

        portfolio_value = cash + (position * current_price)
        portfolio_values.append(portfolio_value)

    portfolio = pd.DataFrame({'Total': portfolio_values}, index=df.index)
    portfolio['Returns'] = portfolio['Total'].pct_change()
    trade_df = pd.DataFrame(trade_log)

    return portfolio, trade_df

# ポートフォリオ管理関数
def add_to_portfolio(symbol, shares, price, longName):
    """ポートフォリオに銘柄を追加する関数"""
    if symbol in st.session_state.portfolio:
        current_shares = st.session_state.portfolio[symbol]['shares']
        current_avg_price = st.session_state.portfolio[symbol]['avg_price']
        new_total_cost = (current_shares * current_avg_price) + (shares * price)
        new_total_shares = current_shares + shares
        st.session_state.portfolio[symbol]['shares'] = new_total_shares
        st.session_state.portfolio[symbol]['avg_price'] = new_total_cost / new_total_shares
        return f"✅ ポートフォリオを更新しました: {longName} - {shares}株追加"
    else:
        st.session_state.portfolio[symbol] = {
            'shares': shares,
            'avg_price': price,
            'longName': longName
        }
        return f"✅ ポートフォリオに追加しました: {longName} - {shares}株"

def remove_from_portfolio(symbol):
    """ポートフォリオから銘柄を削除する関数"""
    if symbol in st.session_state.portfolio:
        longName = st.session_state.portfolio[symbol]['longName']
        del st.session_state.portfolio[symbol]
        return f"🗑️ ポートフォリオから削除しました: {longName}"
    else:
        return "ポートフォリオに銘柄がありません。"

# --- ポートフォリオ管理セクション ---
st.markdown("---")
st.markdown("## 💼 学習用ウォッチリスト（お気に入りリスト）")

st.markdown("""
<div class="explanation-box">
<strong>📂 ウォッチリストって何？</strong><br>
<span>気になる会社の株をリストにして保存できる機能です！</span><br>
<span>「後で勉強したい会社」や「注目している会社」を覚えておけます。</span>
</div>
""", unsafe_allow_html=True)

col_portfolio1, col_portfolio2 = st.columns(2)

with col_portfolio1:
    st.markdown("### ➕ 会社を追加")
    portfolio_symbol = st.text_input("会社コード", placeholder="例: AAPL, 7203.T", key="portfolio_symbol_input")
    portfolio_shares = st.number_input("仮想株数？", min_value=1, value=10, step=1, key="portfolio_shares_input")
    
    if st.button("リストに追加", key="add_portfolio_main", use_container_width=True):
        if portfolio_symbol:
            try:
                with st.spinner("🔍 会社情報を取得中..."):
                    temp_stock = yf.Ticker(portfolio_symbol)
                    temp_info = temp_stock.info
                    temp_price = temp_info.get('currentPrice', temp_info.get('regularMarketPrice', 0))
                    temp_name = temp_info.get('longName', portfolio_symbol)
                
                if temp_price > 0:
                    message = add_to_portfolio(portfolio_symbol, portfolio_shares, temp_price, temp_name)
                    st.success(message)
                    st.rerun()
                else:
                    st.error("❌ 会社の情報が見つかりませんでした")
            except Exception as e:
                st.error(f"❌ エラーが発生しました: {e}")
        else:
            st.warning("⚠️ 会社コードを入力してください")

with col_portfolio2:
    st.markdown("### ➖ 会社を削除")
    if st.session_state.portfolio:
        portfolio_symbols = list(st.session_state.portfolio.keys())
        symbol_to_remove = st.selectbox(
            "削除する会社", 
            portfolio_symbols,
            format_func=lambda x: f"{st.session_state.portfolio[x]['longName']} ({x})",
            key="remove_symbol_select"
        )
        
        if st.button("削除", key="remove_portfolio_main", use_container_width=True):
            message = remove_from_portfolio(symbol_to_remove)
            st.success(message)
            st.rerun()
    else:
        st.info("まだ会社が追加されていません")

# ポートフォリオ表示
if st.session_state.portfolio:
    with st.expander("📊 保存されている会社一覧", expanded=True):
        portfolio_data = []
        total_current_value = 0
        total_cost_basis = 0
        
        symbols_in_portfolio = list(st.session_state.portfolio.keys())
        try:
            if len(symbols_in_portfolio) == 1:
                stock = yf.Ticker(symbols_in_portfolio[0])
                info = stock.info
                current_price = info.get('currentPrice', info.get('regularMarketPrice', 0))
                current_prices_map = {symbols_in_portfolio[0]: current_price}
            else:
                current_prices_df = yf.download(symbols_in_portfolio, period="1d", progress=False)['Close']
                if isinstance(current_prices_df, pd.Series):
                    current_prices_map = {symbols_in_portfolio[0]: current_prices_df.iloc[-1]}
                else:
                    current_prices_map = current_prices_df.iloc[-1].to_dict()
        except:
            current_prices_map = {}

        for symbol, details in st.session_state.portfolio.items():
            long_name = details['longName']
            shares = details['shares']
            avg_price = details['avg_price']
            
            current_price = current_prices_map.get(symbol, avg_price)
            
            cost_basis = shares * avg_price
            current_value = shares * current_price
            profit_loss = current_value - cost_basis
            profit_loss_pct = (profit_loss / cost_basis) * 100 if cost_basis != 0 else 0

            portfolio_data.append({
                "会社名": long_name,
                "コード": symbol,
                "仮想株数": shares,
                "記録時の値段": f"¥{avg_price:,.2f}",
                "今の値段": f"¥{current_price:,.2f}",
                "仮想価値": f"¥{current_value:,.0f}",
                "変動": f"¥{profit_loss:,.0f}",
                "変動(%)": f"{profit_loss_pct:,.2f}%"
            })
            total_current_value += current_value
            total_cost_basis += cost_basis

        portfolio_df = pd.DataFrame(portfolio_data)
        st.dataframe(portfolio_df, hide_index=True, use_container_width=True)

        total_profit_loss = total_current_value - total_cost_basis
        total_profit_loss_pct = (total_profit_loss / total_cost_basis) * 100 if total_cost_basis != 0 else 0

        st.markdown("#### 📈 全体の変動（学習用）")
        col_summary1, col_summary2, col_summary3 = st.columns(3)
        with col_summary1:
            st.metric("💰 記録時の合計", f"¥{total_cost_basis:,.0f}")
        with col_summary2:
            st.metric("💎 現在の価値", f"¥{total_current_value:,.0f}")
        with col_summary3:
            st.metric("📊 変動", f"¥{total_profit_loss:,.0f}", delta=f"{total_profit_loss_pct:,.2f}%")

# --- メイン分析実行 ---
st.markdown("---")

# 分析実行ボタン
if st.button("🚀 分析開始", type="primary", use_container_width=True):
    with st.spinner("📊 データを分析中...少し時間がかかります"):
        df, info = fetch_stock_data(stock_code, start_date, end_date)

    if df is not None and len(df) > 0:
        df = calculate_indicators(df, short_ma, long_ma, rsi_period, bb_period)
        signals = generate_signals_advanced(df)
        portfolio, trade_log = backtest_realistic(df, signals, initial_capital, risk_per_trade, stop_loss_pct, take_profit_pct, trade_cost_rate)

        # 分析結果をセッション状態に保存
        st.session_state.analysis_data = {
            'df': df,
            'info': info,
            'signals': signals,
            'portfolio': portfolio,
            'trade_log': trade_log,
            'parameters': {
                'short_ma': short_ma,
                'long_ma': long_ma,
                'rsi_period': rsi_period,
                'bb_period': bb_period,
                'initial_capital': initial_capital,
                'risk_per_trade': risk_per_trade,
                'stop_loss_pct': stop_loss_pct,
                'take_profit_pct': take_profit_pct,
                'trade_cost_rate': trade_cost_rate
            }
        }
        st.session_state.current_stock_code = stock_code
        st.session_state.current_company_name = info.get('longName', stock_code)
        
        st.success("✅ 分析が完了しました！")
        st.rerun()
    else:
        st.error("""
        ❌ **データを取得できませんでした**

        以下を確認してください：
        - 銘柄コードが正しいか
        - インターネットに接続されているか
        - 市場が開いているか（平日の取引時間）
        - データが十分にあるか
        """)

# 分析結果が保存されている場合に表示
if st.session_state.analysis_data is not None:
    df = st.session_state.analysis_data['df']
    info = st.session_state.analysis_data['info']
    signals = st.session_state.analysis_data['signals']
    portfolio = st.session_state.analysis_data['portfolio']
    trade_log = st.session_state.analysis_data['trade_log']
    params = st.session_state.analysis_data['parameters']

    # --- 企業情報サマリー ---
    st.markdown("---")
    company_name = info.get('longName', st.session_state.current_stock_code)
    st.markdown(f"### 📊 {company_name} の分析結果")

    # 重要な免責事項を再表示
    st.warning("""
    ⚠️ 以下の結果は参考情報であり、投資助言ではありません。
    教育・学習目的でのみご利用ください。
    """)

    # 現在の分析銘柄をポートフォリオに追加
    st.markdown("**💼 この会社をリストに追加**")

    # 既にリストに追加されているかチェック
    already_in_portfolio = st.session_state.current_stock_code in st.session_state.portfolio
    if already_in_portfolio:
        current_data = st.session_state.portfolio[st.session_state.current_stock_code]
        st.info(f"✅ すでにリストに追加済み: {current_data['shares']}株 (平均価格: ¥{current_data['avg_price']:.2f})")

    col_quick1, col_quick2 = st.columns([3, 1])
    with col_quick1:
        quick_shares = st.number_input("仮想株数", min_value=1, value=10, step=1, key="quick_shares")
    with col_quick2:
        button_text = "株数を追加" if already_in_portfolio else "リストに追加"
        if st.button(button_text, key="quick_add_current", use_container_width=True):
            current_price = df['Close'].iloc[-1]
            
            # ポートフォリオに追加
            try:
                message = add_to_portfolio(st.session_state.current_stock_code, quick_shares, current_price, company_name)
                st.success(message)
                
                # 追加された内容を表示
                st.info(f"📈 {company_name} ({st.session_state.current_stock_code}) - {quick_shares}株追加 - ¥{current_price:.2f}/株")
                
                st.balloons()  # 成功時の視覚的フィードバック
                st.rerun()  # 再実行
            except Exception as e:
                st.error(f"❌ エラーが発生しました: {e}")

    st.markdown("---")

    # 主要指標（スマホ最適化レイアウト）
    col1, col2 = st.columns(2)
    with col1:
        current_price = df['Close'].iloc[-1]
        currency = info.get('currency', '')
        st.metric(
            "💰 現在の株価",
            f"{current_price:,.2f} {currency}"
        )

        volume = df['Volume'].iloc[-1]
        st.metric(
            "📦 売買量",
            f"{volume:,.0f}"
        )

    with col2:
        if len(df) > 1:
            prev_price = df['Close'].iloc[-2]
            change_pct = (current_price / prev_price - 1) * 100
            change_val = current_price - prev_price
            st.metric(
                "📈 前日からの変化",
                f"{change_pct:.2f}%",
                delta=f"{change_val:.2f}"
            )

        rsi_current = df['RSI'].iloc[-1]
        if rsi_current < 30:
            rsi_status = "低水準😢"
        elif rsi_current > 70:
            rsi_status = "高水準😱"
        else:
            rsi_status = "中程度😐"
        st.metric(
            "🌡️ RSI（人気度）",
            f"{rsi_current:.1f}",
            delta=rsi_status
        )

    # --- 分析結果サマリー（法的リスク軽減版） ---
    st.markdown("### 🎯 テクニカル分析結果（参考情報）")

    st.markdown("""
    <div class="explanation-box">
    <strong>🤖 分析結果の見方</strong><br>
    <span>コンピューターが色々な指標を見て、テクニカル分析を行いました。</span><br>
    <span>これは参考情報であり、投資助言ではありません。学習目的でご活用ください。</span>
    </div>
    """, unsafe_allow_html=True)

    latest_signal = signals['signal'].iloc[-1]
    buy_score = signals['buy_score'].iloc[-1]
    sell_score = signals['sell_score'].iloc[-1]

    if latest_signal == 1:
        st.info(f"""
        ### 🟢 買いサインを検出
        **スコア: {buy_score:.1f}点**

        複数の指標が「買いサイン」を示しています。
        
        ⚠️ これは参考情報です。投資判断は自己責任でお願いします 🤔
        """)
    elif latest_signal == -1:
        st.info(f"""
        ### 🔴 売りサインを検出  
        **スコア: {sell_score:.1f}点**

        複数の指標が「売りサイン」を示しています。
        
        ⚠️ これは参考情報です。実際の取引は慎重にご判断ください ⚠️
        """)
    else:
        st.info(f"""
        ### ⚪ 中立シグナル（様子見）
        **買いスコア: {buy_score:.1f}点 | 売りスコア: {sell_score:.1f}点**

        現在は明確なサインが出ていない状況です。
        
        ⚠️ 引き続き注視が必要です 👀
        """)

    # 判断根拠
    with st.expander("📋 分析の根拠（詳しい理由）"):
        st.markdown("""
        <div class="explanation-box">
        <strong>🔍 分析の根拠</strong><br>
        <span>以下の4つの要素を総合的に分析しました：</span><br>
        <span>1. 📈 <strong>移動平均</strong>：トレンドの方向性</span><br>
        <span>2. 🌡️ <strong>RSI</strong>：相対的な強弱</span><br>
        <span>3. 📊 <strong>ボリンジャーバンド</strong>：価格の相対的位置</span><br>
        <span>4. ⚡ <strong>MACD</strong>：モメンタムの変化</span>
        </div>
        """, unsafe_allow_html=True)
        
        reasons = []

        if df['MA_short'].iloc[-1] > df['MA_long'].iloc[-1]:
            reasons.append("✅ **上昇トレンド** - 短期平均 > 長期平均")
        else:
            reasons.append("❌ **下降トレンド** - 短期平均 < 長期平均")

        if df['RSI'].iloc[-1] < 35:
            reasons.append(f"✅ **RSI低水準** - RSI = {df['RSI'].iloc[-1]:.1f}（反発の可能性を示唆）")
        elif df['RSI'].iloc[-1] > 65:
            reasons.append(f"❌ **RSI高水準** - RSI = {df['RSI'].iloc[-1]:.1f}（調整の可能性を示唆）")
        else:
            reasons.append(f"⚪ **RSI中程度** - RSI = {df['RSI'].iloc[-1]:.1f}（中立）")

        if df['Close'].iloc[-1] < df['BB_lower'].iloc[-1]:
            reasons.append("✅ **下側バンド突破** - ボリンジャーバンド下限を下回る")
        elif df['Close'].iloc[-1] > df['BB_upper'].iloc[-1]:
            reasons.append("❌ **上側バンド突破** - ボリンジャーバンド上限を上回る")

        if df['MACD'].iloc[-1] > df['MACD_signal'].iloc[-1]:
            reasons.append("✅ **MACD上向き** - 買い勢いを示唆")
        else:
            reasons.append("❌ **MACD下向き** - 売り勢いを示唆")

        for reason in reasons:
            st.write(reason)
        
        st.warning("⚠️ これらは機械的な分析結果であり、将来の価格を予測するものではありません。")

    # --- チャート表示 ---
    with st.expander("📈 株価チャート（学習用）", expanded=True):
        st.markdown("""
        <div class="explanation-box">
        <strong>📊 チャートの見方</strong><br>
        <span><strong>🕯️ ローソク：</strong> 緑=上昇日、赤=下降日</span><br>
        <span><strong>📏 線：</strong> オレンジ=短期平均、青=長期平均</span><br>
        <span><strong>🎯 矢印：</strong> 🟢▲=買いサイン、🔴▼=売りサイン</span>
        </div>
        """, unsafe_allow_html=True)
        
        # チャート作成
        fig = make_subplots(
            rows=3, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.08,
            row_heights=[0.6, 0.2, 0.2],
            subplot_titles=('📈 株価・移動平均・ボリンジャーバンド', '🌡️ RSI（相対力指数）', '⚡ MACD（移動平均収束拡散）')
        )

        # 価格チャート
        fig.add_trace(
            go.Candlestick(
                x=df.index,
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close'],
                name='株価'
            ),
            row=1, col=1
        )

        # 移動平均線
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df['MA_short'],
                name=f'短期平均({params["short_ma"]}日)',
                line=dict(color='orange', width=2)
            ),
            row=1, col=1
        )
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df['MA_long'],
                name=f'長期平均({params["long_ma"]}日)',
                line=dict(color='blue', width=2)
            ),
            row=1, col=1
        )

        # ボリンジャーバンド
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df['BB_upper'],
                name='上限ライン',
                line=dict(color='gray', dash='dash', width=1)
            ),
            row=1, col=1
        )
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df['BB_lower'],
                name='下限ライン',
                line=dict(color='gray', dash='dash', width=1)
            ),
            row=1, col=1
        )

        # シグナル表示
        buy_signals = df.index[signals['signal'] == 1]
        sell_signals = df.index[signals['signal'] == -1]

        if len(buy_signals) > 0:
            fig.add_trace(
                go.Scatter(
                    x=buy_signals,
                    y=df.loc[buy_signals, 'Low'] * 0.98,
                    mode='markers',
                    name='🟢買いサイン',
                    marker=dict(symbol='triangle-up', size=12, color='green')
                ),
                row=1, col=1
            )

        if len(sell_signals) > 0:
            fig.add_trace(
                go.Scatter(
                    x=sell_signals,
                    y=df.loc[sell_signals, 'High'] * 1.02,
                    mode='markers',
                    name='🔴売りサイン',
                    marker=dict(symbol='triangle-down', size=12, color='red')
                ),
                row=1, col=1
            )

        # RSI
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df['RSI'],
                name='RSI',
                line=dict(color='purple', width=2)
            ),
            row=2, col=1
        )
        fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)

        # MACD
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df['MACD'],
                name='MACD',
                line=dict(color='blue', width=2)
            ),
            row=3, col=1
        )
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df['MACD_signal'],
                name='シグナル',
                line=dict(color='red', width=2)
            ),
            row=3, col=1
        )

        # レイアウト設定
        fig.update_layout(
            title=f"{st.session_state.current_stock_code} のテクニカル分析チャート",
            height=600,
            xaxis_rangeslider_visible=False,
            showlegend=False,
            margin=dict(l=10, r=10, t=50, b=10)
        )

        fig.update_yaxes(title_text="株価", row=1, col=1)
        fig.update_yaxes(title_text="RSI", row=2, col=1)
        fig.update_yaxes(title_text="MACD", row=3, col=1)

        st.plotly_chart(fig, use_container_width=True)

    # --- バックテスト結果 ---
    with st.expander("💰 取引シミュレーション結果（学習用）"):
        st.markdown("""
        <div class="explanation-box">
        <strong>🎮 シミュレーションって何？</strong><br>
        <span>「もし過去にこのルールで取引していたら、結果はどうなっていた？」を計算しました。</span><br>
        <span>これは教育目的のシミュレーションであり、実際の投資成果ではありません。</span>
        </div>
        """, unsafe_allow_html=True)
        
        total_return_pct = (portfolio['Total'].iloc[-1] / params['initial_capital'] - 1) * 100
        returns = portfolio['Returns'].dropna()
        sharpe_ratio = (returns.mean() / returns.std()) * np.sqrt(252) if returns.std() > 0 else 0
        max_drawdown = (portfolio['Total'] / portfolio['Total'].cummax() - 1).min() * 100

        # パフォーマンス指標
        col1, col2 = st.columns(2)
        with col1:
            st.metric(
                "💵 仮想最終資産",
                f"¥{portfolio['Total'].iloc[-1]:,.0f}",
                delta=f"¥{portfolio['Total'].iloc[-1] - params['initial_capital']:,.0f}"
            )
            st.metric(
                "📉 最大下落幅",
                f"{max_drawdown:.2f}%"
            )
        with col2:
            st.metric(
                "📈 総リターン",
                f"{total_return_pct:.2f}%"
            )
            st.metric(
                "⚡ シャープレシオ",
                f"{sharpe_ratio:.2f}"
            )

        # 成績判定（学習用解説）
        if total_return_pct > 10:
            st.success("🎉 **優秀な結果！** このシミュレーションでは年率10%以上の成果でした！")
        elif total_return_pct > 0:
            st.info("👍 **プラスの結果** 利益が出ていました！")
        else:
            st.warning("📚 **マイナスの結果** この戦略では損失が発生していました")

        # 分かりやすい説明
        st.markdown("""
        <div class="tip-box">
        <strong>🤔 結果の見方</strong><br>
        <span><strong>仮想最終資産：</strong> 最初の資金がいくらになったか</span><br>
        <span><strong>総リターン：</strong> 何%増えた（減った）か</span><br>
        <span><strong>最大下落幅：</strong> 一番調子が悪い時にどのくらい減ったか</span><br>
        <span><strong>シャープレシオ：</strong> リスクを考慮した成績（1.0以上なら良好）</span>
        </div>
        """, unsafe_allow_html=True)

        # 資産推移グラフ（シンプル版）
        st.markdown("#### 📈 仮想資産の推移")
        fig_portfolio = go.Figure()
        fig_portfolio.add_trace(
            go.Scatter(
                x=portfolio.index,
                y=portfolio['Total'],
                mode='lines',
                fill='tonexty',
                name='仮想資産の変化',
                line=dict(color='green', width=3)
            )
        )
        fig_portfolio.add_hline(
            y=params['initial_capital'],
            line_dash="dash",
            line_color="red",
            annotation_text="初期資金"
        )
        fig_portfolio.update_layout(
            height=300,
            showlegend=False,
            margin=dict(l=10, r=10, t=10, b=10),
            title="シミュレーション期間中の仮想資産変化"
        )
        st.plotly_chart(fig_portfolio, use_container_width=True)

    # --- 企業情報 ---
    with st.expander("🏢 企業情報（参考データ）"):
        st.markdown("""
        <div class="explanation-box">
        <strong>🏪 企業情報の見方</strong><br>
        <span>投資を検討する前に、その会社がどんな会社なのか知ることが大切です！</span><br>
        <span>ただし、これらは過去や現在のデータであり、将来を保証するものではありません。</span>
        </div>
        """, unsafe_allow_html=True)
        
        if info:
            # 基本情報
            if info.get('longBusinessSummary'):
                st.markdown("#### 📝 事業内容")
                summary = info.get('longBusinessSummary', '')
                if len(summary) > 200:
                    summary = summary[:200] + "..."
                st.write(summary)

            # 財務指標（参考情報として）
            st.markdown("#### 💼 主要財務指標（参考情報）")

            col1, col2 = st.columns(2)
            with col1:
                per = info.get('trailingPE', 'N/A')
                if per != 'N/A':
                    if per < 15:
                        per_status = "低い"
                    elif per > 25:
                        per_status = "高い"
                    else:
                        per_status = "標準的"
                    st.metric("PER（株価収益率）", f"{per:.1f}", delta=per_status)
                    st.markdown("""
                    <div class="tip-box">
                    💡 <strong>PERとは：</strong><br>
                    <span>株価が1株あたり利益の何倍かを示す指標</span><br>
                    <span>一般的に15以下は低い、25以上は高いとされます</span>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.metric("PER（株価収益率）", "データなし")

                sector = info.get('sector', 'N/A')
                st.metric("業種", sector)

            with col2:
                pbr = info.get('priceToBook', 'N/A')
                if pbr != 'N/A':
                    if pbr < 1.0:
                        pbr_status = "低い"
                    elif pbr > 3.0:
                        pbr_status = "高い"
                    else:
                        pbr_status = "標準的"
                    st.metric("PBR（株価純資産倍率）", f"{pbr:.1f}", delta=pbr_status)
                    st.markdown("""
                    <div class="tip-box">
                    💡 <strong>PBRとは：</strong><br>
                    <span>株価が1株あたり純資産の何倍かを示す指標</span><br>
                    <span>1.0以下は低い、3.0以上は高いとされます</span>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.metric("PBR（株価純資産倍率）", "データなし")

                # 配当利回りの安全な計算
                div_yield = info.get('dividendYield', 0)
                dividend_rate = info.get('dividendRate', 0)
                current_price_for_div = info.get('currentPrice', info.get('regularMarketPrice', 0))
                
                try:
                    if div_yield and div_yield > 0:
                        div_yield_pct = div_yield
                        if div_yield_pct > 50:
                            if dividend_rate and current_price_for_div and dividend_rate > 0 and current_price_for_div > 0:
                                calculated_yield = (dividend_rate / current_price_for_div) * 100
                                if calculated_yield <= 50:
                                    st.metric("配当利回り", f"{calculated_yield:.2f}%")
                                else:
                                    st.metric("配当利回り", "データ異常")
                                    st.warning("⚠️ 配当データに異常があります")
                            else:
                                st.metric("配当利回り", "データ異常")
                        else:
                            st.metric("配当利回り", f"{div_yield_pct:.2f}%")
                            st.markdown("""
                            <div class="tip-box">
                            💡 <strong>配当利回りとは：</strong><br>
                            <span>株価に対する年間配当金の割合</span><br>
                            <span>3%以上は一般的に高配当とされます</span>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        if dividend_rate and current_price_for_div and dividend_rate > 0 and current_price_for_div > 0:
                            calculated_yield = (dividend_rate / current_price_for_div) * 100
                            if calculated_yield <= 50:
                                st.metric("配当利回り", f"{calculated_yield:.2f}%")
                            else:
                                st.metric("配当利回り", "計算不可")
                        else:
                            st.metric("配当利回り", "配当なし")
                except Exception as e:
                    st.metric("配当利回り", "データなし")

            # 52週高安値
            st.markdown("#### 📊 52週高安値")
            col1, col2 = st.columns(2)
            with col1:
                high_52 = info.get('fiftyTwoWeekHigh', 'N/A')
                if high_52 != 'N/A':
                    st.metric("52週高値", f"{high_52:,.2f} {currency}")
                else:
                    st.metric("52週高値", "データなし")
            with col2:
                low_52 = info.get('fiftyTwoWeekLow', 'N/A')
                if low_52 != 'N/A':
                    st.metric("52週安値", f"{low_52:,.2f} {currency}")
                else:
                    st.metric("52週安値", "データなし")
            
            st.markdown("""
            <div class="tip-box">
            💡 <span>現在の株価が52週間の高値・安値のどの位置にあるかを確認できます</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.warning("❌ 企業の詳しい情報を取得できませんでした")

# --- 使い方ガイド ---
with st.expander("📱 使い方ガイド（困った時はここを見て）"):
    st.markdown("""
    ### 📖 このアプリの使い方

    **🎯 基本的な流れ**
    1. 📈 **会社を選ぶ** → 気になる会社の株価を調べる
    2. ⚙️ **設定する** → 分析の期間や条件を決める
    3. 🚀 **分析開始** → ボタンを押して分析する
    4. 📊 **結果を見る** → テクニカル分析結果を確認する
    5. 💼 **保存する** → 気に入った会社をリストに保存

    **📊 結果の見方**

    **テクニカル分析結果**
    - 🟢 = 買いサインを検出（複数指標が上昇を示唆）
    - 🔴 = 売りサインを検出（複数指標が下降を示唆）
    - ⚪ = 中立シグナル（明確な方向性なし）

    **チャートの見方**
    - 🟢のローソク = その日は株価が上昇
    - 🔴のローソク = その日は株価が下降
    - 🧡の線 = 短期移動平均（最近の平均）
    - 🔵の線 = 長期移動平均（長期の平均）
    - 🟢▲ = 買いサイン検出地点
    - 🔴▼ = 売りサイン検出地点

    **指標の説明**

    **RSI（相対力指数）**
    - 70以上 = 高水準（調整の可能性）
    - 30以下 = 低水準（反発の可能性）
    - 50付近 = 中立的な状態

    **移動平均**
    - 短期 > 長期 = 上昇トレンド
    - 短期 < 長期 = 下降トレンド

    **シミュレーション**
    「もし過去にこのルールで取引していたら？」を検証
    - これは教育目的のシミュレーションです
    - 実際の投資結果とは異なります

    **ウォッチリスト機能**
    - 気になる会社をリストに保存できます
    - 価格変動を追跡できます（学習用）
    - 「お気に入りリスト」のような機能です
    """)
    
    st.markdown("""
    <div class="disclaimer-box">
    <strong>⚠️ とっても大切なこと</strong><br>
    • このアプリは教育・学習用です<br>
    • 投資助言や推奨は行いません<br>
    • 実際の投資判断は自己責任でお願いします<br>
    • 投資前には必ず専門家にご相談ください<br>
    • 過去の分析結果が将来も続くとは限りません
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    ### 💡 投資学習の基本ルール
    - 📚 **勉強する** → 分からないことは調べる
    - 💰 **余裕資金で** → なくなっても大丈夫なお金だけ使う
    - 🎯 **分散投資** → 1つの会社だけでなく、色々な会社に投資
    - 🛡️ **リスク管理** → 損失をコントロールする方法を学ぶ
    - 😌 **感情的にならない** → 慌てて売買しない
    - 📈 **長期目線** → 短期間で大儲けしようと思わない

    ### 🤔 よくある質問

    **Q: このアプリの分析結果は信頼できますか？**
    A: 参考情報として活用してください。投資判断は必ず自己責任で行い、専門家にもご相談ください。

    **Q: 実際の投資に使っても大丈夫ですか？**
    A: このアプリは教育目的です。実際の投資前には十分な検討と専門家への相談をお勧めします。

    **Q: なぜシミュレーション結果と実際の投資で違いが出るのですか？**
    A: 市場環境、取引コスト、心理的要因など多くの要素が影響するためです。

    **Q: どの銘柄を選べばいいですか？**
    A: 自分がよく知っている業界・会社から学習を始めることをお勧めします。

    **Q: 毎日チェックした方がいいですか？**
    A: 学習目的であれば週1-2回程度で十分です。頻繁な確認は不要です。
    """)

# --- フッター ---
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 1rem;'>
    📱 株価分析学習アプリ - 教育目的専用ツール<br>
    <small>🔰 投資学習用 - 実際の投資は専門家にご相談ください</small><br>
    <small>💡 分からないことがあったら「使い方ガイド」をご確認ください</small><br>
    <small>⚠️ 本アプリは投資助言を行うものではありません</small>
</div>
""", unsafe_allow_html=True)

# === 最終免責事項 ===
st.error("""
⚠️ **最終確認**
本アプリケーションは教育・学習目的のみで作成されています。
投資に関するいかなる助言・推奨も行いません。
実際の投資判断は自己責任で行い、必要に応じて専門家にご相談ください。
""")

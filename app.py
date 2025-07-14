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
    page_title="📱 株価分析アプリ（初心者向け）",
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
    
    /* すべてのテキストを強制的に黒色に */
    .explanation-box *, .tip-box * {
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
        .metric-card {
            background: #2d2d2d !important;
            color: #ffffff !important;
            border: 2px solid #64b5f6 !important;
        }
    }
    
    /* スマホ向けレスポンシブ */
    @media (max-width: 768px) {
        .explanation-box, .tip-box {
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
    <h1>📱 株価分析アプリ</h1>
    <p>🔰 初心者・中学生でも分かる投資分析</p>
</div>
""", unsafe_allow_html=True)

# --- 初心者向けガイド ---
with st.expander("🔰 このアプリって何？（初心者必読！）", expanded=False):
    st.markdown("""
    ### 📚 このアプリでできること
    
    **株って何？**  
    株は「会社の一部を買うこと」です。例えば、トヨタの株を買うと、トヨタの会社の小さな持ち主になれます！
    
    **このアプリの使い方**
    1. 📈 **会社を選ぶ** → 気になる会社の株価を調べる
    2. 🔍 **分析する** → その会社の株価が上がりそうか下がりそうかを調べる  
    3. 💡 **判断を見る** → コンピューターが「買い」「売り」「様子見」を教えてくれる
    4. 💼 **ポートフォリオ** → 気になる会社をリストに保存できる
    
    **⚠️ 大切なこと**
    - これは勉強用のアプリです
    - 実際にお金を使う時は、大人と相談しましょう
    - 株価は上がったり下がったりするのが普通です
    """)

# --- Streamlit セッション状態の初期化 ---
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = {}

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
        with st.expander("🔧 より多くの検索結果を得る（上級者向け）"):
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
        <span>よく投資される人気の会社から選べます</span>
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

    else:  # コード直接入力
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
    <span>株価のグラフを見て「上がりそう」「下がりそう」を判断するための道具です。</span><br>
    <span>数学を使って、人間には見えないパターンを見つけてくれます！</span>
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
        
        st.markdown("**RSI（買われすぎ・売られすぎ）**")
        rsi_period = st.slider("RSI期間", 5, 30, 14)
        st.markdown("""
        <div class="tip-box">
        📊 <strong>これは何？</strong> <span>株が「買われすぎ」か「売られすぎ」かを0-100で表示</span><br>
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

    st.markdown("#### 💰 投資シミュレーション設定")
    
    st.markdown("""
    <div class="explanation-box">
    <strong>🎮 投資シミュレーションって何？</strong><br>
    <span>「もしこのルールで投資していたら、お金はどうなっていた？」を計算してくれます。</span><br>
    <span>実際のお金は使わないので安心です！</span>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**初期資金**")
        initial_capital = st.number_input(
            "初期資金（万円）",
            10, 1000, 100, 10,
            format="%d"
        ) * 10000
        st.markdown("""
        <div class="tip-box">
        💰 <strong>これは何？</strong> <span>投資を始める時のお金</span><br>
        <strong>⬆️ 多くすると：</strong> <span>大きく儲かるけど、大きく損する可能性も</span><br>
        <strong>⬇️ 少なくすると：</strong> <span>安全だけど、儲けも少ない</span>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("**リスク許容率**")
        risk_per_trade = st.slider("リスク許容率(%)", 0.5, 5.0, 2.0, 0.5)
        st.markdown("""
        <div class="tip-box">
        ⚡ <strong>これは何？</strong> <span>1回の投資でどのくらいリスクを取るか</span><br>
        <strong>⬆️ 高くすると：</strong> <span>大胆に投資（ハイリスク・ハイリターン）</span><br>
        <strong>⬇️ 低くすると：</strong> <span>慎重に投資（ローリスク・ローリターン）</span><br>
        <strong>👍 おすすめ：</strong> <span>初心者は2%以下</span>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown("**損切り率**")
        stop_loss_pct = st.slider("損切り率(%)", 1.0, 20.0, 5.0, 0.5)
        st.markdown("""
        <div class="tip-box">
        🛡️ <strong>これは何？</strong> <span>「これ以上下がったら売る」というルール</span><br>
        <strong>⬆️ 高くすると：</strong> <span>我慢強く持ち続ける（大きく下がっても売らない）</span><br>
        <strong>⬇️ 低くすると：</strong> <span>早めに売る（小さく下がったら売る）</span><br>
        <strong>👍 おすすめ：</strong> <span>5-10%が一般的</span>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("**利益確定率**")
        take_profit_pct = st.slider("利益確定率(%)", 2.0, 50.0, 15.0, 1.0)
        st.markdown("""
        <div class="tip-box">
        🎯 <strong>これは何？</strong> <span>「これだけ上がったら売る」というルール</span><br>
        <strong>⬆️ 高くすると：</strong> <span>欲張って長く持つ（もっと上がるまで待つ）</span><br>
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
        stock = yf.Ticker(symbol)
        df = stock.history(start=start, end=end)
        if df.empty:
            return None, None
        info = stock.info
        return df, info
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
    signals['buy_score'] = 0
    signals['sell_score'] = 0

    signals.loc[df['MA_short'] > df['MA_long'], 'buy_score'] += 1
    signals.loc[df['MA_short'] < df['MA_long'], 'sell_score'] += 1

    signals.loc[df['RSI'] < 35, 'buy_score'] += 1
    signals.loc[df['RSI'] > 65, 'sell_score'] += 1

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
    if symbol in st.session_state.portfolio:
        current_shares = st.session_state.portfolio[symbol]['shares']
        current_avg_price = st.session_state.portfolio[symbol]['avg_price']
        new_total_cost = (current_shares * current_avg_price) + (shares * price)
        new_total_shares = current_shares + shares
        st.session_state.portfolio[symbol]['shares'] = new_total_shares
        st.session_state.portfolio[symbol]['avg_price'] = new_total_cost / new_total_shares
        st.success(f"✅ ポートフォリオを更新しました: {longName} - {shares}株追加")
    else:
        st.session_state.portfolio[symbol] = {
            'shares': shares,
            'avg_price': price,
            'longName': longName
        }
        st.success(f"✅ ポートフォリオに追加しました: {longName} - {shares}株")

def remove_from_portfolio(symbol):
    if symbol in st.session_state.portfolio:
        longName = st.session_state.portfolio[symbol]['longName']
        del st.session_state.portfolio[symbol]
        st.success(f"🗑️ ポートフォリオから削除しました: {longName}")
    else:
        st.warning("ポートフォリオに銘柄がありません。")

# --- ポートフォリオ管理セクション ---
st.markdown("---")
st.markdown("## 💼 マイポートフォリオ（お気に入りリスト）")

st.markdown("""
<div class="explanation-box">
<strong>📂 ポートフォリオって何？</strong><br>
<span>気になる会社の株をリストにして保存できる機能です！</span><br>
<span>「後で見たい会社」や「買いたい会社」を覚えておけます。</span>
</div>
""", unsafe_allow_html=True)

col_portfolio1, col_portfolio2 = st.columns(2)

with col_portfolio1:
    st.markdown("### ➕ 会社を追加")
    portfolio_symbol = st.text_input("会社コード", placeholder="例: AAPL, 7203.T", key="portfolio_symbol_input")
    portfolio_shares = st.number_input("何株？", min_value=1, value=10, step=1, key="portfolio_shares_input")
    
    if st.button("リストに追加", key="add_portfolio_main", use_container_width=True):
        if portfolio_symbol:
            try:
                with st.spinner("🔍 会社情報を取得中..."):
                    temp_stock = yf.Ticker(portfolio_symbol)
                    temp_info = temp_stock.info
                    temp_price = temp_info.get('currentPrice', temp_info.get('regularMarketPrice', 0))
                    temp_name = temp_info.get('longName', portfolio_symbol)
                
                if temp_price > 0:
                    add_to_portfolio(portfolio_symbol, portfolio_shares, temp_price, temp_name)
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
            remove_from_portfolio(symbol_to_remove)
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
                "株数": shares,
                "買った時の値段": f"¥{avg_price:,.2f}",
                "今の値段": f"¥{current_price:,.2f}",
                "今の価値": f"¥{current_value:,.0f}",
                "儲け/損": f"¥{profit_loss:,.0f}",
                "儲け/損(%)": f"{profit_loss_pct:,.2f}%"
            })
            total_current_value += current_value
            total_cost_basis += cost_basis

        portfolio_df = pd.DataFrame(portfolio_data)
        st.dataframe(portfolio_df, hide_index=True, use_container_width=True)

        total_profit_loss = total_current_value - total_cost_basis
        total_profit_loss_pct = (total_profit_loss / total_cost_basis) * 100 if total_cost_basis != 0 else 0

        st.markdown("#### 📈 全体の成績")
        col_summary1, col_summary2, col_summary3 = st.columns(3)
        with col_summary1:
            st.metric("💰 投資した金額", f"¥{total_cost_basis:,.0f}")
        with col_summary2:
            st.metric("💎 今の価値", f"¥{total_current_value:,.0f}")
        with col_summary3:
            st.metric("📊 儲け/損", f"¥{total_profit_loss:,.0f}", delta=f"{total_profit_loss_pct:,.2f}%")

# --- メイン分析実行 ---
st.markdown("---")
if st.button("🚀 分析開始", type="primary", use_container_width=True):

    with st.spinner("📊 データを分析中...少し時間がかかります"):
        df, info = fetch_stock_data(stock_code, start_date, end_date)

    if df is not None and len(df) > 0:
        df = calculate_indicators(df, short_ma, long_ma, rsi_period, bb_period)
        signals = generate_signals_advanced(df)
        portfolio, trade_log = backtest_realistic(df, signals, initial_capital, risk_per_trade, stop_loss_pct, take_profit_pct, trade_cost_rate)

        # --- 企業情報サマリー ---
        st.markdown("---")
        company_name = info.get('longName', stock_code)
        st.markdown(f"### 📊 {company_name} の分析結果")

        # 現在の分析銘柄をポートフォリオに追加
        st.markdown("**💼 この会社をリストに保存**")
        col_quick1, col_quick2 = st.columns([3, 1])
        with col_quick1:
            quick_shares = st.number_input("株数", min_value=1, value=10, step=1, key="quick_shares")
        with col_quick2:
            if st.button("保存", key="quick_add_current", use_container_width=True):
                current_price = df['Close'].iloc[-1]
                add_to_portfolio(stock_code, quick_shares, current_price, company_name)
                st.rerun()

        st.markdown("---")

        # 主要指標（スマホ最適化レイアウト）
        col1, col2 = st.columns(2)
        with col1:
            current_price = df['Close'].iloc[-1]
            currency = info.get('currency', '')
            st.metric(
                "💰 今の株価",
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
                    "📈 昨日からの変化",
                    f"{change_pct:.2f}%",
                    delta=f"{change_val:.2f}"
                )

            rsi_current = df['RSI'].iloc[-1]
            if rsi_current < 30:
                rsi_status = "売られすぎ😢"
            elif rsi_current > 70:
                rsi_status = "買われすぎ😱"
            else:
                rsi_status = "普通😐"
            st.metric(
                "🌡️ RSI（人気度）",
                f"{rsi_current:.1f}",
                delta=rsi_status
            )

        # --- 投資判断サマリー ---
        st.markdown("### 🎯 コンピューターの判断")

        st.markdown("""
        <div class="explanation-box">
        <strong>🤖 判断の見方</strong><br>
        <span>コンピューターが色々な指標を見て、総合的に判断しました。</span><br>
        <span>でも、100%当たるわけではないので参考程度に見てくださいね！</span>
        </div>
        """, unsafe_allow_html=True)

        latest_signal = signals['signal'].iloc[-1]
        buy_score = signals['buy_score'].iloc[-1]
        sell_score = signals['sell_score'].iloc[-1]

        if latest_signal == 1:
            st.success(f"""
            ### 🟢 買い推奨
            **スコア: {buy_score:.1f}点**

            色々な指標が「今は買い時かも」と言っています！
            
            でも、最終的な判断は自分で決めましょう 🤔
            """)
        elif latest_signal == -1:
            st.error(f"""
            ### 🔴 売り推奨  
            **スコア: {sell_score:.1f}点**

            色々な指標が「今は売り時かも」と言っています。
            
            持っている人は要注意 ⚠️
            """)
        else:
            st.info(f"""
            ### ⚪ 中立（様子見）
            **買いスコア: {buy_score:.1f}点 | 売りスコア: {sell_score:.1f}点**

            今はどちらとも言えない状況です。
            
            もう少し様子を見ましょう 👀
            """)

        # 判断根拠
        with st.expander("📋 なぜその判断になったの？（詳しい理由）"):
            st.markdown("""
            <div class="explanation-box">
            <strong>🔍 判断の根拠</strong><br>
            <span>コンピューターが以下の4つの要素を見て判断しました：</span><br>
            <span>1. 📈 <strong>移動平均</strong>：最近の流れ</span><br>
            <span>2. 🌡️ <strong>RSI</strong>：買われすぎ・売られすぎ</span><br>
            <span>3. 📊 <strong>ボリンジャーバンド</strong>：普通の値段の範囲</span><br>
            <span>4. ⚡ <strong>MACD</strong>：勢いの変化</span>
            </div>
            """, unsafe_allow_html=True)
            
            reasons = []

            if df['MA_short'].iloc[-1] > df['MA_long'].iloc[-1]:
                reasons.append("✅ **流れが良い** - 短期の平均 > 長期の平均（上昇トレンド）")
            else:
                reasons.append("❌ **流れが悪い** - 短期の平均 < 長期の平均（下降トレンド）")

            if df['RSI'].iloc[-1] < 35:
                reasons.append(f"✅ **売られすぎ** - RSI = {df['RSI'].iloc[-1]:.1f}（反発の可能性）")
            elif df['RSI'].iloc[-1] > 65:
                reasons.append(f"❌ **買われすぎ** - RSI = {df['RSI'].iloc[-1]:.1f}（下がる可能性）")
            else:
                reasons.append(f"⚪ **普通の人気** - RSI = {df['RSI'].iloc[-1]:.1f}（中立）")

            if df['Close'].iloc[-1] < df['BB_lower'].iloc[-1]:
                reasons.append("✅ **安すぎる** - 普通の範囲より安い（買いチャンス？）")
            elif df['Close'].iloc[-1] > df['BB_upper'].iloc[-1]:
                reasons.append("❌ **高すぎる** - 普通の範囲より高い（注意）")

            if df['MACD'].iloc[-1] > df['MACD_signal'].iloc[-1]:
                reasons.append("✅ **勢いが良い** - 上がる力が強い")
            else:
                reasons.append("❌ **勢いが弱い** - 上がる力が弱い")

            for reason in reasons:
                st.write(reason)

        # --- チャート表示 ---
        with st.expander("📈 株価のグラフ（チャート）", expanded=True):
            st.markdown("""
            <div class="explanation-box">
            <strong>📊 グラフの見方</strong><br>
            <span><strong>🕯️ ローソク：</strong> 緑=上がった日、赤=下がった日</span><br>
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
                subplot_titles=('📈 株価・移動平均・ボリンジャーバンド', '🌡️ RSI（人気度）', '⚡ MACD（勢い）')
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
                    name=f'短期平均({short_ma}日)',
                    line=dict(color='orange', width=2)
                ),
                row=1, col=1
            )
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df['MA_long'],
                    name=f'長期平均({long_ma}日)',
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

            # 売買シグナル
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
                title=f"{stock_code} の分析チャート",
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
        with st.expander("💰 投資シミュレーション結果"):
            st.markdown("""
            <div class="explanation-box">
            <strong>🎮 シミュレーションって何？</strong><br>
            <span>「もし過去にこのルールで投資していたら、お金はどうなっていた？」を計算しました。</span><br>
            <span>実際のお金は使っていないので安心してください！</span>
            </div>
            """, unsafe_allow_html=True)
            
            total_return_pct = (portfolio['Total'].iloc[-1] / initial_capital - 1) * 100
            returns = portfolio['Returns'].dropna()
            sharpe_ratio = (returns.mean() / returns.std()) * np.sqrt(252) if returns.std() > 0 else 0
            max_drawdown = (portfolio['Total'] / portfolio['Total'].cummax() - 1).min() * 100

            # パフォーマンス指標
            col1, col2 = st.columns(2)
            with col1:
                st.metric(
                    "💵 最終的なお金",
                    f"¥{portfolio['Total'].iloc[-1]:,.0f}",
                    delta=f"¥{portfolio['Total'].iloc[-1] - initial_capital:,.0f}"
                )
                st.metric(
                    "📉 最大の落ち込み",
                    f"{max_drawdown:.2f}%"
                )
            with col2:
                st.metric(
                    "📈 全体の成果",
                    f"{total_return_pct:.2f}%"
                )
                st.metric(
                    "⚡ リスク調整後の成果",
                    f"{sharpe_ratio:.2f}"
                )

            # 成績判定（中学生向け解説）
            if total_return_pct > 10:
                st.success("🎉 **素晴らしい成績！** この方法だと年率10%以上儲かっていました！")
                st.info("💡 でも過去の結果なので、将来も同じとは限りません")
            elif total_return_pct > 0:
                st.info("👍 **まずまずの成績** 利益は出ていました！")
                st.info("💡 投資では「プラス」になるだけでも良い結果です")
            else:
                st.warning("📚 **改善が必要** この方法だと損をしていました")
                st.info("💡 設定を変えてみると結果が変わるかもしれません")

            # 分かりやすい説明
            st.markdown("""
            <div class="tip-box">
            <strong>🤔 結果の見方</strong><br>
            <span><strong>最終的なお金：</strong> 最初のお金がいくらになったか</span><br>
            <span><strong>全体の成果：</strong> 何%増えた（減った）か</span><br>
            <span><strong>最大の落ち込み：</strong> 一番調子が悪い時にどのくらい減ったか</span><br>
            <span><strong>リスク調整後の成果：</strong> リスクを考慮した成績（1.0以上なら優秀）</span>
            </div>
            """, unsafe_allow_html=True)

            # 資産推移グラフ（シンプル版）
            st.markdown("#### 📈 お金の変化")
            fig_portfolio = go.Figure()
            fig_portfolio.add_trace(
                go.Scatter(
                    x=portfolio.index,
                    y=portfolio['Total'],
                    mode='lines',
                    fill='tonexty',
                    name='お金の変化',
                    line=dict(color='green', width=3)
                )
            )
            fig_portfolio.add_hline(
                y=initial_capital,
                line_dash="dash",
                line_color="red",
                annotation_text="最初のお金"
            )
            fig_portfolio.update_layout(
                height=300,
                showlegend=False,
                margin=dict(l=10, r=10, t=10, b=10),
                title="時間とともにお金がどう変化したか"
            )
            st.plotly_chart(fig_portfolio, use_container_width=True)

        # --- 企業情報 ---
        with st.expander("🏢 この会社について"):
            st.markdown("""
            <div class="explanation-box">
            <strong>🏪 会社情報の見方</strong><br>
            <span>投資する前に、その会社がどんな会社なのか知ることが大切です！</span>
            </div>
            """, unsafe_allow_html=True)
            
            if info:
                # 基本情報
                if info.get('longBusinessSummary'):
                    st.markdown("#### 📝 この会社は何をしている？")
                    summary = info.get('longBusinessSummary', '')
                    if len(summary) > 200:
                        summary = summary[:200] + "..."
                    st.write(summary)

                # 財務指標（中学生向け解説付き）
                st.markdown("#### 💼 会社の通信簿")

                col1, col2 = st.columns(2)
                with col1:
                    per = info.get('trailingPE', 'N/A')
                    if per != 'N/A':
                        if per < 15:
                            per_status = "安い😊"
                        elif per > 25:
                            per_status = "高い😰"
                        else:
                            per_status = "普通😐"
                        st.metric("PER（株価の高さ）", f"{per:.1f}", delta=per_status)
                        st.markdown("""
                        <div class="tip-box">
                        💡 <strong>PERって何？</strong><br>
                        <span>株価が会社の利益に比べて高いか安いかを表す数字</span><br>
                        <span>15以下＝安い、25以上＝高い</span>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.metric("PER（株価の高さ）", "データなし")

                    sector = info.get('sector', 'N/A')
                    st.metric("業種", sector)

                with col2:
                    pbr = info.get('priceToBook', 'N/A')
                    if pbr != 'N/A':
                        if pbr < 1.0:
                            pbr_status = "安い😊"
                        elif pbr > 3.0:
                            pbr_status = "高い😰"
                        else:
                            pbr_status = "普通😐"
                        st.metric("PBR（資産価値との比較）", f"{pbr:.1f}", delta=pbr_status)
                        st.markdown("""
                        <div class="tip-box">
                        💡 <strong>PBRって何？</strong><br>
                        <span>株価が会社の資産に比べて高いか安いかを表す数字</span><br>
                        <span>1.0以下＝安い、3.0以上＝高い</span>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.metric("PBR（資産価値との比較）", "データなし")

                    div_yield = info.get('dividendYield', 0)
                    if div_yield:
                        st.metric("配当利回り（お小遣い）", f"{div_yield * 100:.2f}%")
                        st.markdown("""
                        <div class="tip-box">
                        💡 <strong>配当って何？</strong><br>
                        <span>会社が株主にくれる「お小遣い」</span><br>
                        <span>3%以上あれば結構良い</span>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.metric("配当利回り（お小遣い）", "なし")

                # 52週高安値
                st.markdown("#### 📊 この1年の最高値・最安値")
                col1, col2 = st.columns(2)
                with col1:
                    high_52 = info.get('fiftyTwoWeekHigh', 'N/A')
                    st.metric("1年で一番高かった時", f"¥{high_52}" if high_52 != 'N/A' else "データなし")
                with col2:
                    low_52 = info.get('fiftyTwoWeekLow', 'N/A')
                    st.metric("1年で一番安かった時", f"¥{low_52}" if low_52 != 'N/A' else "データなし")
                
                st.markdown("""
                <div class="tip-box">
                💡 <span>今の株価が最高値に近いか最安値に近いかで、買うタイミングを考えましょう</span>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.warning("❌ 会社の詳しい情報を取得できませんでした")

    else:
        st.error("""
        ❌ **データを取得できませんでした**

        以下を確認してください：
        - 会社のコード（記号）が正しいか
        - インターネットに接続されているか
        - 株式市場が開いているか（平日の昼間）
        """)

# --- 使い方ガイド ---
with st.expander("📱 使い方ガイド（困った時はここを見て）"):
    st.markdown("""
    ### 📖 このアプリの使い方

    **🎯 基本的な流れ**
    1. 📈 **会社を選ぶ** → 気になる会社の株価を調べる
    2. ⚙️ **設定する** → 分析の期間や条件を決める
    3. 🚀 **分析開始** → ボタンを押して分析する
    4. 📊 **結果を見る** → コンピューターの判断を確認する
    5. 💼 **保存する** → 気に入った会社をリストに保存

    **📊 結果の見方**

    **投資判断**
    - 🟢 = 買い推奨（今が買い時かも）
    - 🔴 = 売り推奨（持ってたら売り時かも）
    - ⚪ = 様子見（もう少し待った方がいいかも）

    **チャートの見方**
    - 🟢のローソク = その日は株価が上がった
    - 🔴のローソク = その日は株価が下がった
    - 🧡の線 = 短期移動平均（最近の平均）
    - 🔵の線 = 長期移動平均（長期の平均）
    - 🟢▲ = 買いサイン
    - 🔴▼ = 売りサイン

    **指標の説明**

    **RSI（買われすぎ・売られすぎ）**
    - 70以上 = みんなが買いすぎ（下がるかも）
    - 30以下 = みんなが売りすぎ（上がるかも）
    - 50付近 = 普通の状態

    **移動平均**
    - 短期 > 長期 = 上昇トレンド（調子が良い）
    - 短期 < 長期 = 下降トレンド（調子が悪い）

    **バックテスト**
    「もし過去にこのルールで投資していたら？」をシミュレーション
    - でも過去の結果なので、将来も同じとは限りません！

    **ポートフォリオ機能**
    - 気になる会社をリストに保存できます
    - 後で値段の変化を確認できます
    - 「お気に入りリスト」みたいなものです

    **⚠️ とっても大切なこと**
    - ⚠️ このアプリは勉強用です
    - ⚠️ 実際にお金を使う時は、大人と相談しましょう
    - ⚠️ コンピューターの判断が100%正しいわけではありません
    - ⚠️ 株価は上がったり下がったりするのが普通です

    ### 💡 投資の基本ルール
    - 📚 **勉強する** → 分からないことは調べる
    - 💰 **余裕資金で** → なくなっても大丈夫なお金だけ使う
    - 🎯 **分散投資** → 1つの会社だけじゃなく、色々な会社に投資
    - 🛡️ **損切りルール** → 下がりすぎたら売る勇気
    - 😌 **感情的にならない** → 慌てて売ったり買ったりしない
    - 📈 **長期目線** → 短期間で大儲けしようと思わない

    ### 🤔 よくある質問

    **Q: 株って危険じゃないの？**
    A: リスクはありますが、正しく勉強すれば怖くありません。まずは少額から始めましょう。

    **Q: いくらから始められるの？**
    A: 今は1株から買える証券会社もあります。数百円から始められます。

    **Q: どの会社の株を買えばいいの？**
    A: 自分がよく知っている会社から始めるのがおすすめです。

    **Q: いつ売ればいいの？**
    A: 最初に「これくらい上がったら売る」「これくらい下がったら売る」を決めておきましょう。

    **Q: 毎日チェックした方がいいの？**
    A: 毎日見すぎると心配になります。週1回くらいで十分です。
    """)

# --- フッター ---
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 1rem;'>
    📱 中学生でも分かる株価分析アプリ<br>
    <small>🔰 投資の勉強用 - 実際の投資は大人と相談してね！</small><br>
    <small>💡 分からないことがあったら「使い方ガイド」を見てください</small>
</div>
""", unsafe_allow_html=True)

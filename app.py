import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import ta
from scipy import stats

# スマホ最適化ページ設定
st.set_page_config(
    page_title="📱 株価分析アプリ",
    layout="centered",  # スマホ向けにcentered使用
    initial_sidebar_state="collapsed"  # サイドバーを最初は折りたたみ
)

# カスタムCSS（スマホ最適化）
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1rem 0;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        margin: -1rem -1rem 2rem -1rem;
        border-radius: 0 0 1rem 1rem;
    }
    .metric-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        border-left: 4px solid #667eea;
    }
    .big-button {
        width: 100%;
        padding: 1rem;
        font-size: 1.2rem;
        margin: 1rem 0;
    }
    .stExpander > div > div > div {
        padding: 1rem;
    }
    /* チャートのスマホ最適化 */
    .plotly-graph-div {
        margin: 0 -1rem;
    }
    @media (max-width: 768px) {
        .stColumns {
            flex-direction: column;
        }
        .stColumn {
            width: 100% !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# --- ヘッダー ---
st.markdown("""
<div class="main-header">
    <h1>📱 株価分析アプリ</h1>
    <p>スマホで簡単に株式投資分析</p>
</div>
""", unsafe_allow_html=True)

# --- Streamlit セッション状態の初期化 ---
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = {} # {symbol: {'shares': X, 'avg_price': Y, 'longName': Z}}

# --- メイン設定エリア（サイドバーの代わり） ---
with st.expander("⚙️ 分析設定", expanded=True):
    st.markdown("### 📍 銘柄選択")

    # 銘柄入力方法
    input_type = st.radio(
        "入力方法",
        ["人気銘柄から選択", "銘柄コード入力"],
        horizontal=True
    )

    if input_type == "人気銘柄から選択":
        popular_stocks = {
            "🇯🇵 トヨタ自動車": "7203.T",
            "🇯🇵 ソニーグループ": "6758.T",
            "🇯🇵 任天堂": "7974.T",
            "🇺🇸 Apple": "AAPL",
            "🇺🇸 Tesla": "TSLA",
            "🇺🇸 Microsoft": "MSFT",
            "🇺🇸 NVIDIA": "NVDA",
            "🇺🇸 Google": "GOOGL"
        }
        selected = st.selectbox(
            "銘柄を選択",
            list(popular_stocks.keys())
        )
        stock_code = popular_stocks[selected]
        st.info(f"選択中: **{selected}** ({stock_code})")
    else:
        stock_code = st.text_input(
            "銘柄コード",
            "AAPL",
            placeholder="例: AAPL, 7203.T"
        )

    st.markdown("### 📅 分析期間")
    period_options = {
        "1ヶ月": 30,
        "3ヶ月": 90,
        "6ヶ月": 180,
        "1年": 365,
        "2年": 730
    }
    selected_period = st.select_slider(
        "期間を選択",
        options=list(period_options.keys()),
        value="6ヶ月"
    )
    days = period_options[selected_period]
    start_date = datetime.now() - timedelta(days=days)
    end_date = datetime.now()

# --- 詳細設定（折りたたみ） ---
with st.expander("🔧 詳細設定"):
    st.markdown("#### テクニカル指標")

    col1, col2 = st.columns(2)
    with col1:
        short_ma = st.slider("短期移動平均", 5, 50, 20)
        rsi_period = st.slider("RSI期間", 5, 30, 14)
    with col2:
        long_ma = st.slider("長期移動平均", 20, 200, 50)
        bb_period = st.slider("BB期間", 10, 30, 20)

    st.markdown("#### バックテスト設定")

    col1, col2 = st.columns(2)
    with col1:
        initial_capital = st.number_input(
            "初期資金（万円）",
            10, 1000, 100, 10,
            format="%d"
        ) * 10000
        risk_per_trade = st.slider("リスク許容率(%)", 0.5, 5.0, 2.0, 0.5)
    with col2:
        stop_loss_pct = st.slider("損切り率(%)", 1.0, 20.0, 5.0, 0.5)
        take_profit_pct = st.slider("利益確定率(%)", 2.0, 50.0, 15.0, 1.0)

    trade_cost_rate = st.slider("取引手数料率(%)", 0.0, 1.0, 0.1, 0.01)

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

# --- ポートフォリオ管理関数 ---
def add_to_portfolio(symbol, shares, price, longName):
    if symbol in st.session_state.portfolio:
        # Update existing holding
        current_shares = st.session_state.portfolio[symbol]['shares']
        current_avg_price = st.session_state.portfolio[symbol]['avg_price']
        new_total_cost = (current_shares * current_avg_price) + (shares * price)
        new_total_shares = current_shares + shares
        st.session_state.portfolio[symbol]['shares'] = new_total_shares
        st.session_state.portfolio[symbol]['avg_price'] = new_total_cost / new_total_shares
        st.success(f"ポートフォリオを更新しました: {longName} - {shares}株追加")
    else:
        # Add new holding
        st.session_state.portfolio[symbol] = {
            'shares': shares,
            'avg_price': price,
            'longName': longName
        }
        st.success(f"ポートフォリオに追加しました: {longName} - {shares}株")

def remove_from_portfolio(symbol):
    if symbol in st.session_state.portfolio:
        longName = st.session_state.portfolio[symbol]['longName']
        del st.session_state.portfolio[symbol]
        st.success(f"ポートフォリオから削除しました: {longName}")
    else:
        st.warning("ポートフォリオに銘柄がありません。")

# --- メイン分析実行 ---
if st.button("🚀 分析開始", type="primary", use_container_width=True):

    with st.spinner("📊 データ分析中..."):
        df, info = fetch_stock_data(stock_code, start_date, end_date)

    if df is not None and len(df) > 0:
        df = calculate_indicators(df, short_ma, long_ma, rsi_period, bb_period)
        signals = generate_signals_advanced(df)
        portfolio, trade_log = backtest_realistic(df, signals, initial_capital, risk_per_trade, stop_loss_pct, take_profit_pct, trade_cost_rate)

        # --- 企業情報サマリー ---
        st.markdown("---")
        company_name = info.get('longName', stock_code)
        st.markdown(f"### 📊 {company_name}")

        # 主要指標（スマホ最適化レイアウト）
        col1, col2 = st.columns(2)
        with col1:
            current_price = df['Close'].iloc[-1]
            currency = info.get('currency', '')
            st.metric(
                "💰 現在価格",
                f"{current_price:,.2f} {currency}"
            )

            volume = df['Volume'].iloc[-1]
            st.metric(
                "📦 出来高",
                f"{volume:,.0f}"
            )

        with col2:
            if len(df) > 1:
                prev_price = df['Close'].iloc[-2]
                change_pct = (current_price / prev_price - 1) * 100
                change_val = current_price - prev_price
                st.metric(
                    "📈 前日比",
                    f"{change_pct:.2f}%",
                    delta=f"{change_val:.2f}"
                )

            rsi_current = df['RSI'].iloc[-1]
            rsi_status = "売られすぎ" if rsi_current < 30 else "買われすぎ" if rsi_current > 70 else "中立"
            st.metric(
                "🌡️ RSI",
                f"{rsi_current:.1f}",
                delta=rsi_status
            )

        # --- ポートフォリオ追加/削除ボタン ---
        st.markdown("### 💼 ポートフォリオに追加")
        col_port1, col_port2 = st.columns(2)
        with col_port1:
            shares_to_add = st.number_input("追加する株数", min_value=1, value=10, step=1)
        with col_port2:
            if st.button("ポートフォリオに追加", key="add_to_portfolio_btn", use_container_width=True):
                add_to_portfolio(stock_code, shares_to_add, current_price, company_name)
        if stock_code in st.session_state.portfolio:
            if st.button(f"{company_name}をポートフォリオから削除", key="remove_from_portfolio_btn", use_container_width=True):
                remove_from_portfolio(stock_code)
        st.markdown("---")


        # --- 投資判断サマリー ---
        st.markdown("### 🎯 投資判断")

        latest_signal = signals['signal'].iloc[-1]
        buy_score = signals['buy_score'].iloc[-1]
        sell_score = signals['sell_score'].iloc[-1]

        if latest_signal == 1:
            st.success(f"""
            ### 🟢 買い推奨
            **スコア: {buy_score:.1f}点**

            複数の指標が買いを示唆しています
            """)
        elif latest_signal == -1:
            st.error(f"""
            ### 🔴 売り推奨
            **スコア: {sell_score:.1f}点**

            複数の指標が売りを示唆しています
            """)
        else:
            st.info(f"""
            ### ⚪ 中立（様子見）
            **買いスコア: {buy_score:.1f}点 | 売りスコア: {sell_score:.1f}点**

            明確なシグナルが出ていません
            """)

        # 判断根拠
        with st.expander("📋 判断根拠の詳細"):
            reasons = []

            if df['MA_short'].iloc[-1] > df['MA_long'].iloc[-1]:
                reasons.append("✅ 短期移動平均 > 長期移動平均（上昇トレンド）")
            else:
                reasons.append("❌ 短期移動平均 < 長期移動平均（下降トレンド）")

            if df['RSI'].iloc[-1] < 35:
                reasons.append(f"✅ RSI = {df['RSI'].iloc[-1]:.1f}（売られすぎ）")
            elif df['RSI'].iloc[-1] > 65:
                reasons.append(f"❌ RSI = {df['RSI'].iloc[-1]:.1f}（買われすぎ）")
            else:
                reasons.append(f"⚪ RSI = {df['RSI'].iloc[-1]:.1f}（中立）")

            if df['Close'].iloc[-1] < df['BB_lower'].iloc[-1]:
                reasons.append("✅ 株価がボリンジャーバンド下限突破（反発期待）")
            elif df['Close'].iloc[-1] > df['BB_upper'].iloc[-1]:
                reasons.append("❌ 株価がボリンジャーバンド上限突破（過熱）")

            if df['MACD'].iloc[-1] > df['MACD_signal'].iloc[-1]:
                reasons.append("✅ MACD > シグナル（勢い良好）")
            else:
                reasons.append("❌ MACD < シグナル（勢い低下）")

            for reason in reasons:
                st.write(reason)

        # --- チャート表示 ---
        with st.expander("📈 テクニカルチャート", expanded=True):
            # スマホ最適化チャート
            fig = make_subplots(
                rows=3, cols=1,
                shared_xaxes=True,
                vertical_spacing=0.08,
                row_heights=[0.6, 0.2, 0.2],
                subplot_titles=('株価・移動平均・BB', 'RSI', 'MACD')
            )

            # 価格チャート
            fig.add_trace(
                go.Candlestick(
                    x=df.index,
                    open=df['Open'],
                    high=df['High'],
                    low=df['Low'],
                    close=df['Close'],
                    name='価格'
                ),
                row=1, col=1
            )

            # 移動平均線
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df['MA_short'],
                    name=f'短期MA({short_ma})',
                    line=dict(color='orange', width=2)
                ),
                row=1, col=1
            )
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df['MA_long'],
                    name=f'長期MA({long_ma})',
                    line=dict(color='blue', width=2)
                ),
                row=1, col=1
            )

            # ボリンジャーバンド
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df['BB_upper'],
                    name='BB上限',
                    line=dict(color='gray', dash='dash', width=1)
                ),
                row=1, col=1
            )
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df['BB_lower'],
                    name='BB下限',
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
                        name='🟢買いシグナル',
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
                        name='🔴売りシグナル',
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
                    name='Signal',
                    line=dict(color='red', width=2)
                ),
                row=3, col=1
            )

            # レイアウト設定（スマホ最適化）
            fig.update_layout(
                title=f"{stock_code} テクニカル分析",
                height=600,  # スマホ向けに高さ調整
                xaxis_rangeslider_visible=False,
                showlegend=False,  # 凡例を非表示でスッキリ
                margin=dict(l=10, r=10, t=50, b=10)
            )

            fig.update_yaxes(title_text="価格", row=1, col=1)
            fig.update_yaxes(title_text="RSI", row=2, col=1)
            fig.update_yaxes(title_text="MACD", row=3, col=1)

            st.plotly_chart(fig, use_container_width=True)

        # --- バックテスト結果 ---
        with st.expander("💰 バックテスト結果"):
            total_return_pct = (portfolio['Total'].iloc[-1] / initial_capital - 1) * 100
            returns = portfolio['Returns'].dropna()
            sharpe_ratio = (returns.mean() / returns.std()) * np.sqrt(252) if returns.std() > 0 else 0
            max_drawdown = (portfolio['Total'] / portfolio['Total'].cummax() - 1).min() * 100

            # パフォーマンス指標
            col1, col2 = st.columns(2)
            with col1:
                st.metric(
                    "💵 最終資産",
                    f"¥{portfolio['Total'].iloc[-1]:,.0f}",
                    delta=f"¥{portfolio['Total'].iloc[-1] - initial_capital:,.0f}"
                )
                st.metric(
                    "📉 最大DD",
                    f"{max_drawdown:.2f}%"
                )
            with col2:
                st.metric(
                    "📈 総リターン",
                    f"{total_return_pct:.2f}%"
                )
                st.metric(
                    "⚡ シャープ比",
                    f"{sharpe_ratio:.2f}"
                )

            # 成績判定
            if total_return_pct > 10:
                st.success("🎉 **優秀な成績！** 年率10%以上のリターンです！")
            elif total_return_pct > 0:
                st.info("👍 **プラスの成績** 利益を出せました！")
            else:
                st.warning("📚 **改善の余地あり** 設定を見直してみましょう")

            # 資産推移グラフ（シンプル版）
            st.markdown("#### 📈 資産の推移")
            fig_portfolio = go.Figure()
            fig_portfolio.add_trace(
                go.Scatter(
                    x=portfolio.index,
                    y=portfolio['Total'],
                    mode='lines',
                    fill='tonexty',
                    name='ポートフォリオ価値',
                    line=dict(color='green', width=3)
                )
            )
            fig_portfolio.add_hline(
                y=initial_capital,
                line_dash="dash",
                line_color="red",
                annotation_text="初期資金"
            )
            fig_portfolio.update_layout(
                height=300,
                showlegend=False,
                margin=dict(l=10, r=10, t=10, b=10)
            )
            st.plotly_chart(fig_portfolio, use_container_width=True)

        # --- 企業情報 ---
        with st.expander("🏢 企業基本情報"):
            if info:
                # 基本情報
                if info.get('longBusinessSummary'):
                    st.markdown("#### 📝 事業概要")
                    summary = info.get('longBusinessSummary', '')
                    # 長すぎる場合は要約
                    if len(summary) > 200:
                        summary = summary[:200] + "..."
                    st.write(summary)

                # 財務指標
                st.markdown("#### 💼 主要指標")

                col1, col2 = st.columns(2)
                with col1:
                    per = info.get('trailingPE', 'N/A')
                    if per != 'N/A':
                        per_status = "割安" if per < 15 else "高め" if per > 25 else "普通"
                        st.metric("PER", f"{per:.1f}", delta=per_status)
                    else:
                        st.metric("PER", "N/A")

                    sector = info.get('sector', 'N/A')
                    st.metric("業種", sector)

                with col2:
                    pbr = info.get('priceToBook', 'N/A')
                    if pbr != 'N/A':
                        pbr_status = "割安" if pbr < 1.0 else "高め" if pbr > 3.0 else "普通"
                        st.metric("PBR", f"{pbr:.1f}", delta=pbr_status)
                    else:
                        st.metric("PBR", "N/A")

                    div_yield = info.get('dividendYield', 0)
                    if div_yield:
                        st.metric("配当利回り", f"{div_yield * 100:.2f}%")
                    else:
                        st.metric("配当利回り", "N/A")

                # 52週高安値
                col1, col2 = st.columns(2)
                with col1:
                    high_52 = info.get('fiftyTwoWeekHigh', 'N/A')
                    st.metric("52週高値", f"{high_52}" if high_52 != 'N/A' else "N/A")
                with col2:
                    low_52 = info.get('fiftyTwoWeekLow', 'N/A')
                    st.metric("52週安値", f"{low_52}" if low_52 != 'N/A' else "N/A")
            else:
                st.warning("企業情報を取得できませんでした")

    else:
        st.error("""
        ❌ **データを取得できませんでした**

        以下を確認してください：
        - 銘柄コードが正しいか
        - インターネット接続
        - 市場が開いているか
        """)

# --- ポートフォリオ表示エリア ---
st.markdown("---")
st.markdown("## 💼 マイポートフォリオ")

if st.session_state.portfolio:
    portfolio_data = []
    total_current_value = 0
    total_cost_basis = 0
    
    # 最新の株価を取得
    symbols_in_portfolio = list(st.session_state.portfolio.keys())
    # Yahoo Financeから複数銘柄の最新株価を一括で取得
    try:
        current_prices_df = yf.download(symbols_in_portfolio, period="1d")['Close']
        if isinstance(current_prices_df, pd.Series): # Only one stock downloaded
            current_prices_map = {symbols_in_portfolio[0]: current_prices_df.iloc[-1]}
        else: # Multiple stocks downloaded
            current_prices_map = current_prices_df.iloc[-1].to_dict()
    except Exception as e:
        st.warning(f"ポートフォリオ銘柄の最新価格取得エラー: {e}")
        current_prices_map = {} # Fallback to empty if error

    for symbol, details in st.session_state.portfolio.items():
        long_name = details['longName']
        shares = details['shares']
        avg_price = details['avg_price']
        
        current_price = current_prices_map.get(symbol, avg_price) # Use avg_price as fallback if current price not fetched
        
        cost_basis = shares * avg_price
        current_value = shares * current_price
        daily_change = (current_price - (current_prices_df.iloc[-2].get(symbol) if isinstance(current_prices_df, pd.DataFrame) and len(current_prices_df) > 1 else current_price)) * shares # Simple daily change if prev day price available
        
        profit_loss = current_value - cost_basis
        profit_loss_pct = (profit_loss / cost_basis) * 100 if cost_basis != 0 else 0

        portfolio_data.append({
            "銘柄": long_name,
            "コード": symbol,
            "株数": shares,
            "平均取得価格": f"¥{avg_price:,.2f}",
            "現在価格": f"¥{current_price:,.2f}",
            "現在価値": f"¥{current_value:,.0f}",
            "評価損益": f"¥{profit_loss:,.0f}",
            "評価損益(%)": f"{profit_loss_pct:,.2f}%"
        })
        total_current_value += current_value
        total_cost_basis += cost_basis

    portfolio_df = pd.DataFrame(portfolio_data)
    st.dataframe(portfolio_df, hide_index=True, use_container_width=True)

    # ポートフォリオ全体サマリー
    total_profit_loss = total_current_value - total_cost_basis
    total_profit_loss_pct = (total_profit_loss / total_cost_basis) * 100 if total_cost_basis != 0 else 0

    st.markdown("#### 📈 ポートフォリオ全体サマリー")
    col_summary1, col_summary2 = st.columns(2)
    with col_summary1:
        st.metric("総現在価値", f"¥{total_current_value:,.0f}")
    with col_summary2:
        st.metric("総評価損益", f"¥{total_profit_loss:,.0f}", delta=f"{total_profit_loss_pct:,.2f}%")

else:
    st.info("ポートフォリオに銘柄が追加されていません。")

# --- 使い方ガイド ---
with st.expander("📱 使い方ガイド"):
    st.markdown("""
    ### 📖 このアプリの使い方

    **🎯 基本的な流れ**
    1. 上部で銘柄を選択
    2. 分析期間を設定
    3. 「🚀 分析開始」をタップ
    4. 結果を確認

    **📊 見方のポイント**

    **投資判断**
    - 🟢 = 買い推奨
    - 🔴 = 売り推奨
    - ⚪ = 様子見

    **チャートの見方**
    - 緑のローソク = 上昇日
    - 赤のローソク = 下降日
    - オレンジ線 = 短期移動平均
    - 青線 = 長期移動平均
    - 🟢▲ = 買いシグナル
    - 🔴▼ = 売りシグナル

    **RSI（買われすぎ・売られすぎ）**
    - 70以上 = 買われすぎ
    - 30以下 = 売られすぎ
    - 50付近 = 中立

    **バックテスト**
    過去のデータで「もしこのルールで投資していたら？」をシミュレーション

    **ポートフォリオ機能**
    - 分析中の銘柄を「ポートフォリオに追加」ボタンで簡単に追加できます。
    - 追加した銘柄は「マイポートフォリオ」セクションに表示され、現在の評価額や損益を確認できます。

    **重要な注意**
    ⚠️ このアプリは教育目的です
    ⚠️ 実際の投資は自己責任で
    ⚠️ 100%の予測はできません

    ### 💡 投資の基本
    - 余裕資金で投資する
    - 分散投資を心がける
    - 損切りルールを守る
    - 感情的にならない
    - 継続的に学習する
    """)

# --- フッター ---
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 1rem;'>
    📱 スマホ対応株価分析アプリ<br>
    <small>教育目的での使用を推奨します</small>
</div>
""", unsafe_allow_html=True)

# スマホ最適化のためのJavaScript
st.markdown("""
<script>
// タッチ操作の最適化
document.addEventListener('DOMContentLoaded', function() {
    // ピンチズーム無効化（チャート操作を改善）
    document.addEventListener('touchstart', function(e) {
        if (e.touches.length > 1) {
            e.preventDefault();
        }
    });

    // ダブルタップズーム無効化
    let lastTouchEnd = 0;
    document.addEventListener('touchend', function(e) {
        let now = (new Date()).getTime();
        if (now - lastTouchEnd <= 300) {
            e.preventDefault();
        }
        lastTouchEnd = now;
    }, false);
});
</script>
""", unsafe_allow_html=True)
# ui/components.py - 改善版（人気銘柄選択削除）
"""
UIコンポーネント機能 - Enter実行対応版
"""

import streamlit as st
import pandas as pd
from typing import Dict, List, Any, Optional

from config.settings import (
    TECHNICAL_RANGES, BACKTEST_RANGES, PERIOD_OPTIONS, 
    DISCLAIMERS, WARNING_MESSAGES, SUCCESS_MESSAGES
)


class UIComponents:
    """UIコンポーネントクラス"""
    
    @staticmethod
    def render_header():
        """ヘッダーを表示"""
        st.markdown("""
        <div class="main-header">
            <h1>📱 株価分析学習アプリ</h1>
            <p>🔰 教育・学習専用ツール</p>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_beginner_guide():
        """初心者向けガイドを表示"""
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
    
    @staticmethod
    def render_explanation_box(title: str, content: str):
        """解説ボックスを表示"""
        st.markdown(f"""
        <div class="explanation-box">
        <strong>{title}</strong><br>
        <span>{content}</span>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_tip_box(title: str, content: str):
        """Tipボックスを表示"""
        st.markdown(f"""
        <div class="tip-box">
        <strong>{title}</strong><br>
        <span>{content}</span>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_disclaimer_box(content: str):
        """免責事項ボックスを表示"""
        st.markdown(f"""
        <div class="disclaimer-box">
        {content}
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_stock_search_section() -> tuple:
        """銘柄検索セクションを表示"""
        UIComponents.render_explanation_box(
            "📍 会社を選ぼう",
            "どの会社の株価を分析したいか選択してください"
        )
        
        # 検索方法の選択（人気の会社から選ぶを削除）
        search_method = st.radio(
            "検索方法を選んでね",
            ["🔍 会社名で検索", "⌨️ コードを直接入力"],
            horizontal=True
        )
        
        return search_method
    
    @staticmethod
    def render_company_search() -> tuple:
        """会社名検索UIを表示"""
        UIComponents.render_explanation_box(
            "🔍 会社名検索",
            "知っている会社の名前を入力すると、銘柄コードを自動で見つけてくれます！<br>例：「トヨタ」「Apple」「任天堂」「テスラ」など"
        )
        
        # API Key設定（オプション）
        show_advanced = st.toggle("🔧 より多くの検索結果を得る（上級者向け）")
        api_key = None
        
        if show_advanced:
            api_key = st.text_input(
                "Alpha Vantage API Key（省略可）",
                type="password",
                help="無料で取得可能。より多くの会社を検索できます"
            )
            UIComponents.render_tip_box(
                "💡 API Keyについて",
                "API Keyなしでも大丈夫：主要な会社は検索できます<br>" +
                "API Keyがあると：世界中の会社を検索できます<br>" +
                "取得方法：https://www.alphavantage.co/support/#api-key で無料取得"
            )
        
        # 検索入力
        search_keyword = st.text_input(
            "会社名を入力してください",
            placeholder="例: トヨタ, Apple, 任天堂, Tesla",
            key="stock_search_input"
        )
        
        return search_keyword, api_key
    
    @staticmethod
    def render_direct_input() -> str:
        """直接入力UIを表示（Enter対応版）"""
        UIComponents.render_explanation_box(
            "⌨️ 銘柄コード直接入力",
            "すでに銘柄コードを知っている場合はこちら<br>" +
            "💡 入力後にEnterキーを押すか、下の「🚀 分析開始」ボタンを押してください"
        )
        
        # セッション状態の初期化
        if 'direct_input_symbol' not in st.session_state:
            st.session_state.direct_input_symbol = "AAPL"
        
        # 銘柄コード入力（Enter対応）
        stock_code = st.text_input(
            "銘柄コード",
            value=st.session_state.direct_input_symbol,
            placeholder="例: AAPL, 7203.T, TSLA",
            key="direct_stock_input",
            help="入力後にEnterキーを押すと自動で検証されます"
        )
        
        # 入力値が変更された場合の処理
        if stock_code != st.session_state.direct_input_symbol:
            st.session_state.direct_input_symbol = stock_code
            
            # リアルタイム検証
            if stock_code.strip():
                validation_result = UIComponents._validate_stock_symbol(stock_code)
                
                if validation_result['is_valid']:
                    st.success(f"✅ {validation_result['message']}")
                    # 簡易的な企業情報表示
                    if validation_result.get('company_info'):
                        st.info(f"💼 {validation_result['company_info']}")
                else:
                    st.warning(f"⚠️ {validation_result['message']}")
        
        # Enter実行の説明
        UIComponents.render_tip_box(
            "⚡ 使い方",
            "💡 銘柄コードを入力してEnterを押すと、そのまま使用できます<br>" +
            "💡 日本の会社は最後に「.T」が付きます（例：7203.T）<br>" +
            "💡 アメリカの会社は英字のみです（例：AAPL, TSLA）"
        )
        
        # よく使われる銘柄の例示
        with st.expander("📖 よく使われる銘柄コード例", expanded=False):
            st.markdown("""
            **🇯🇵 日本の主要銘柄:**
            - 7203.T (トヨタ自動車)
            - 6758.T (ソニーグループ)
            - 7974.T (任天堂)
            - 9984.T (ソフトバンクグループ)
            - 6861.T (キーエンス)
            
            **🇺🇸 アメリカの主要銘柄:**
            - AAPL (Apple)
            - MSFT (Microsoft)
            - GOOGL (Google/Alphabet)
            - AMZN (Amazon)
            - TSLA (Tesla)
            - NVDA (NVIDIA)
            - META (Meta/Facebook)
            """)
        
        return stock_code
    
    @staticmethod
    def _validate_stock_symbol(symbol: str) -> Dict[str, Any]:
        """
        銘柄コードの検証（リアルタイム用）
        
        Args:
            symbol: 銘柄コード
            
        Returns:
            dict: 検証結果
        """
        symbol = symbol.strip().upper()
        
        if not symbol:
            return {'is_valid': False, 'message': '銘柄コードを入力してください'}
        
        # 基本的なフォーマットチェック
        if len(symbol) < 1 or len(symbol) > 10:
            return {'is_valid': False, 'message': '銘柄コードの長さが正しくありません'}
        
        # 日本株のフォーマット（例: 7203.T）
        if symbol.endswith('.T'):
            code_part = symbol[:-2]
            if code_part.isdigit() and len(code_part) == 4:
                company_info = UIComponents._get_japanese_company_info(symbol)
                return {
                    'is_valid': True, 
                    'message': f'日本株として認識されました: {symbol}',
                    'company_info': company_info
                }
            else:
                return {'is_valid': False, 'message': '日本株の形式が正しくありません（例: 7203.T）'}
        
        # 米国株のフォーマット（例: AAPL）
        if symbol.isalpha() and 1 <= len(symbol) <= 5:
            company_info = UIComponents._get_us_company_info(symbol)
            return {
                'is_valid': True, 
                'message': f'米国株として認識されました: {symbol}',
                'company_info': company_info
            }
        
        # その他の市場
        if symbol.replace('.', '').replace('-', '').isalnum():
            return {
                'is_valid': True, 
                'message': f'銘柄コードとして認識されました: {symbol}',
                'company_info': '※ 詳細は分析実行時に取得されます'
            }
        
        return {'is_valid': False, 'message': '銘柄コードの形式が正しくありません'}
    
    @staticmethod
    def _get_japanese_company_info(symbol: str) -> str:
        """日本企業の簡易情報を取得"""
        japanese_companies = {
            "7203.T": "トヨタ自動車 - 世界最大の自動車メーカー",
            "6758.T": "ソニーグループ - エンターテインメント・テクノロジー企業",
            "7974.T": "任天堂 - ゲーム・娯楽機器メーカー",
            "9984.T": "ソフトバンクグループ - 投資・通信企業",
            "6861.T": "キーエンス - 自動化機器メーカー",
            "4755.T": "楽天グループ - インターネットサービス",
            "9983.T": "ファーストリテイリング - 衣料品企業（ユニクロ）",
            "7267.T": "ホンダ - 自動車・バイクメーカー",
            "7201.T": "日産自動車 - 自動車メーカー"
        }
        return japanese_companies.get(symbol, "日本の上場企業")
    
    @staticmethod
    def _get_us_company_info(symbol: str) -> str:
        """米国企業の簡易情報を取得"""
        us_companies = {
            "AAPL": "Apple Inc. - iPhone・Mac等を製造するテクノロジー企業",
            "MSFT": "Microsoft Corporation - Windows・Office等のソフトウェア企業",
            "GOOGL": "Alphabet Inc. - Google検索・YouTube等を運営",
            "AMZN": "Amazon.com Inc. - 電子商取引・クラウドサービス企業",
            "TSLA": "Tesla Inc. - 電気自動車・エネルギー企業",
            "NVDA": "NVIDIA Corporation - GPU・AI半導体メーカー",
            "META": "Meta Platforms Inc. - Facebook・Instagram等を運営",
            "NFLX": "Netflix Inc. - 動画配信サービス",
            "DIS": "The Walt Disney Company - エンターテインメント企業",
            "NKE": "Nike Inc. - スポーツ用品メーカー"
        }
        return us_companies.get(symbol, "米国の上場企業")
    
    @staticmethod
    def render_period_selection() -> tuple:
        """期間選択UIを表示"""
        st.markdown("### 📅 どのくらいの期間を調べる？")
        
        UIComponents.render_explanation_box(
            "📊 期間の選び方",
            "短い期間 → 最近の動きがよく分かる<br>長い期間 → 大きな流れ（トレンド）が分かる"
        )
        
        selected_period = st.select_slider(
            "期間を選んでね",
            options=list(PERIOD_OPTIONS.keys()),
            value="6ヶ月"
        )
        
        days = PERIOD_OPTIONS[selected_period]
        return selected_period, days
    
    @staticmethod
    def render_technical_settings() -> Dict[str, int]:        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**短期移動平均**")
            short_ma = st.slider(
                "短期移動平均", 
                TECHNICAL_RANGES['short_ma']['min'],
                TECHNICAL_RANGES['short_ma']['max'],
                20
            )
            UIComponents.render_tip_box(
                "📊 短期移動平均とは",
                "最近の株価の平均です<br>" +
                "⬆️ 高くすると：急な株価の動きには反応しない（なだらかな線）<br>" +
                "⬇️ 低くすると：株価の変化にすぐ反応する（動きが速い）<br>" +
                "👍 おすすめ：初心者は20のままでOK<br>" +
                "📌使い方の例：短期線が長期線を上に抜けたら買いのサイン"
            )
            
            st.markdown("**RSI（人気度指標）**")
            rsi_period = st.slider(
                "RSI期間",
                TECHNICAL_RANGES['rsi_period']['min'],
                TECHNICAL_RANGES['rsi_period']['max'],
                14
            )
            UIComponents.render_tip_box(
                "📊 RSIとは",
                "株の「人気度」を0〜100で表示します<br>" +
                "⬆️ 高くすると：ゆっくり反応する（安定）<br>" +
                "⬇️ 低くすると：素早く反応する（敏感）<br>" +
                "👍 おすすめ：14のままでOK<br>" +
                "📌使い方の例：30以下は売られすぎ、70以上は買われすぎの目安"
            )

        with col2:
            st.markdown("**長期移動平均**")
            long_ma = st.slider(
                "長期移動平均",
                TECHNICAL_RANGES['long_ma']['min'],
                TECHNICAL_RANGES['long_ma']['max'],
                50
            )
            UIComponents.render_tip_box(
                "📊 長期移動平均とは",
                "長い期間の株価の平均です<br>" +
                "⬆️ 高くすると：とてもゆっくり動く線<br>" +
                "⬇️ 低くすると：やや速く動く線<br>" +
                "👍 おすすめ：短期より大きい数字にする<br>" +
                "📌使い方の例：長期線より短期線が上なら上昇トレンド"
            )
 
            st.markdown("**ボリンジャーバンド期間**")
            bb_period = st.slider(
                "BB期間",
                TECHNICAL_RANGES['bb_period']['min'],
                TECHNICAL_RANGES['bb_period']['max'],
                20
            )
            UIComponents.render_tip_box(
                "📊 ボリンジャーバンドとは",
                "株価の「普通の範囲」を表示する線です<br>" +
                "⬆️ 高くすると：広い範囲を普通と判断（緩やか）<br>" +
                "⬇️ 低くすると：狭い範囲を普通と判断（敏感）<br>" +
                "👍 おすすめ：20のままでOK<br>" +
                "📌使い方の例：バンドの下限に近いと反発の可能性"
            )
     
        return {
            'short_ma': short_ma,
            'long_ma': long_ma,
            'rsi_period': rsi_period,
            'bb_period': bb_period
        }
    
    @staticmethod
    def render_backtest_settings() -> Dict[str, float]:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**仮想初期資金**")
            initial_capital = st.number_input(
                "仮想初期資金（万円）",
                min_value=10, max_value=1000, value=100, step=10,
                format="%d"
            ) * 10000
            
            UIComponents.render_tip_box(
                "💰 仮想初期資金",
                "シミュレーション開始時の仮想資金です<br>" +
                "⬆️ 多くすると：変動幅が大きく見える<br>" +
                "⬇️ 少なくすると：変動が小さく見える<br>" +
                "📌使い方の例：大きな資金だと取引余地が広がります"
            )

            st.markdown("**リスク許容率**")
            risk_per_trade = st.slider(
                "リスク許容率(%)",
                BACKTEST_RANGES['risk_per_trade']['min'],
                BACKTEST_RANGES['risk_per_trade']['max'],
                2.0, 0.5
            )
            
            UIComponents.render_tip_box(
                "⚡ リスク許容率",
                "1回の取引でどれくらいの損失を許容するかの割合です<br>" +
                "⬆️ 高くすると：利益も損も大きくなる（攻め）<br>" +
                "⬇️ 低くすると：小さな変動で抑える（守り）<br>" +
                "👍 おすすめ：初心者は2%以下<br>" +
                "📌使い方の例：高すぎると連敗時に資金が急減する"
            )
 
        with col2:
            st.markdown("**損切り率**")
            stop_loss_pct = st.slider(
                "損切り率(%)",
                BACKTEST_RANGES['stop_loss_pct']['min'],
                BACKTEST_RANGES['stop_loss_pct']['max'],
                5.0, 0.5
            )
            
            UIComponents.render_tip_box(
                "🛡️ 損切り率",
                "「これ以上下がったら売る」という損失ルールです<br>" +
                "⬆️ 高くすると：下落しても我慢して保有<br>" +
                "⬇️ 低くすると：早めに損切りして撤退<br>" +
                "👍 おすすめ：5〜10%が一般的<br>" +
                "📌使い方の例：自分で決めた損失ラインで機械的に売る"
            )
    
            st.markdown("**利益確定率**")
            take_profit_pct = st.slider(
                "利益確定率(%)",
                BACKTEST_RANGES['take_profit_pct']['min'],
                BACKTEST_RANGES['take_profit_pct']['max'],
                15.0, 1.0
            )
            
            UIComponents.render_tip_box(
                "🎯 利益確定率",
                "「これだけ上がったら売る」という利益の目安です<br>" +
                "⬆️ 高くすると：長く保有して大きな利益を狙う<br>" +
                "⬇️ 低くすると：小さな利益で確定する<br>" +
                "👍 おすすめ：損切り率の2〜3倍<br>" +
                "📌使い方の例：損より利益を大きくする戦略が安定"
            )
   
        st.markdown("**取引手数料率**")
        trade_cost_rate = st.slider(
            "取引手数料率(%)",
            BACKTEST_RANGES['trade_cost_rate']['min'],
            BACKTEST_RANGES['trade_cost_rate']['max'],
            0.1, 0.01
        )
        
        UIComponents.render_tip_box(
            "💳 取引手数料率",
            "株の売買ごとにかかるコストです<br>" +
            "⬆️ 高くすると：現実に近く利益が減る<br>" +
            "⬇️ 低くすると：利益は出やすいが非現実的<br>" +
            "👍 おすすめ：0.1%（ネット証券の平均）<br>" +
            "📌使い方の例：頻繁な売買では手数料が成績に影響"
        )
        
        return {
            'initial_capital': initial_capital,
            'risk_per_trade': risk_per_trade,
            'stop_loss_pct': stop_loss_pct,
            'take_profit_pct': take_profit_pct,
            'trade_cost_rate': trade_cost_rate
        }
    
    @staticmethod
    def render_quick_start_tips():
        """クイックスタートのヒントを表示"""
        with st.expander("⚡ クイックスタート（初回利用の方）", expanded=False):
            st.markdown("""
            ### 🚀 3分で始める株価分析
            
            **🤔 特定の会社を調べたい方:**
            1. 「🔍 会社名で検索」を選択
            2. 調べたい会社名を入力（例：トヨタ、テスラ）
            3. 検索結果から選択して「🚀 分析開始」
            
            **🎯 銘柄コードを知っている方:**
            1. 「⌨️ コードを直接入力」を選択
            2. 銘柄コードを入力してEnter（例：AAPL、7203.T）
            3. または「🚀 分析開始」ボタンを押す
            """)
    
    @staticmethod
    def render_analysis_results(analysis_data: Dict[str, Any]):
        """分析結果を表示"""
        if not analysis_data:
            return
            
        st.markdown("### 🎯 テクニカル分析結果（参考情報）")
        
        UIComponents.render_explanation_box(
            "🤖 分析結果の見方",
            "コンピューターが色々な指標を見て、テクニカル分析を行いました。<br>" +
            "これは参考情報であり、投資助言ではありません。学習目的でご活用ください。"
        )
        
        # シグナル結果表示
        signals = analysis_data['signals']
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
    
    @staticmethod
    def render_metrics(current_price: float, info: Dict[str, Any], df: pd.DataFrame):
        """主要指標を表示"""
        col1, col2 = st.columns(2)
        
        with col1:
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
    
    @staticmethod
    def render_footer():
        """フッターを表示"""
        st.markdown("---")
        st.markdown("""
        <div style='text-align: center; color: #666; padding: 1rem;'>
            📱 株価分析学習アプリ - 教育目的専用ツール<br>
            <small>🔰 投資学習用 - 実際の投資は専門家にご相談ください</small><br>
            <small>💡 分からないことがあったら「使い方ガイド」をご確認ください</small><br>
            <small>⚠️ 本アプリは投資助言を行うものではありません</small>
        </div>
        """, unsafe_allow_html=True)
        
        # 最終免責事項
        st.error(
            """
        ⚠️ **最終確認**

        本アプリケーションは教育・学習目的のみで作成されています。  
        投資に関するいかなる助言・推奨も行いません。  
        実際の投資判断は自己責任で行い、必要に応じて専門家にご相談ください。  
        """
        )

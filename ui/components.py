# ui/components.py - JQuants API対応・API設定常時表示版
"""
UIコンポーネント機能 - JQuants API対応・API設定常時表示版
"""

import streamlit as st
import pandas as pd
from typing import Dict, List, Any, Optional

from config.settings import (
    TECHNICAL_RANGES, BACKTEST_RANGES, PERIOD_OPTIONS, 
    DISCLAIMERS, WARNING_MESSAGES, SUCCESS_MESSAGES
)


class UIComponents:
    """UIコンポーネントクラス（JQuants API対応・API設定常時表示）"""
    
    @staticmethod
    def render_header():
        """ヘッダーを表示"""
        st.markdown("""
        <div class="main-header">
            <h1>📱 株価分析学習アプリ</h1>
            <p>🔰 教育・学習専用ツール | 🆕 JQuants API対応</p>
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
            
            **🆕 JQuants API対応で更に便利に！**
            - 🇯🇵 **日本株**: 全上場企業を会社名で検索可能
            - 🌍 **海外株**: Alpha Vantage APIで世界中の株式検索
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
        
        # 検索方法の選択
        search_method = st.radio(
            "検索方法を選んでね",
            ["🔍 会社名で検索", "⌨️ コードを直接入力"],
            horizontal=True
        )
        
        return search_method
    
    @staticmethod
    def render_company_search() -> tuple:
        """会社名検索UIを表示（JQuants対応・API設定常時表示）"""
        UIComponents.render_explanation_box(
            "🔍 会社名検索（🆕JQuants対応）",
            "🇯🇵 **日本株**: 全上場企業をリアルタイム検索（JQuants API）<br>" +
            "🌍 **世界株**: グローバル株式検索（Alpha Vantage API）<br>" +
            "💡 例：「トヨタ」「Apple」「任天堂」「Tesla」など"
        )
        
        # API設定セクション（常時表示）
        api_settings = UIComponents._render_api_settings()
        
        # 検索入力
        search_keyword = st.text_input(
            "🔍 会社名を入力してください",
            placeholder="例: トヨタ, Apple, 任天堂, Tesla",
            key="stock_search_input"
        )
        
        # 検索実行時のAPI使用状況を事前に表示（削除）
        # if search_keyword:
        #     UIComponents._display_search_execution_plan(api_settings, search_keyword)
        
        return search_keyword, api_settings
    
    @staticmethod
    def _render_api_settings() -> Dict[str, Optional[str]]:
        """API設定UIを表示（常時表示版・外部ファイル対応）"""
        
        # API設定管理機能の読み込み
        try:
            from config.api_config import get_api_config_manager
            api_manager = get_api_config_manager()
        except ImportError:
            st.error("❌ API設定管理機能が見つかりません")
            api_manager = None
        
        # チェックボックスを削除し、常にAPI設定を表示
        st.markdown("---")
        st.markdown("### 🔧 API設定")
        
        jquants_config = None
        alpha_vantage_key = None
        
        # 外部ファイルからの設定読み込み
        if api_manager:
            file_jquants_config = api_manager.get_jquants_config()
            file_alpha_vantage_key = api_manager.get_alpha_vantage_key()
            
            if file_jquants_config or file_alpha_vantage_key:
                st.success("📁 外部設定ファイルから認証情報を読み込みました")
                
                # 認証成功メッセージを個別に表示
                if file_jquants_config:
                    st.info("🇯🇵 **JQuants認証成功**")
                    jquants_config = file_jquants_config
                
                if file_alpha_vantage_key:
                    st.info("🌍 **Alpha Vantage認証成功**")
                    alpha_vantage_key = file_alpha_vantage_key
                
                # 手動入力オプション
                use_manual_input = st.checkbox(
                    "🖥️ 手動でAPI設定を入力",
                    value=False
                )
            else:
                use_manual_input = True
                st.info("📝 API設定ファイルが見つかりません。手動で設定してください。")
        else:
            use_manual_input = True
            st.info("📝 手動でAPI設定を入力してください。")
        
        # 手動入力UI
        if use_manual_input:
            st.markdown("#### 🇯🇵 JQuants API（日本株専用）")
            col1, col2 = st.columns(2)
            
            with col1:
                jquants_email = st.text_input(
                    "メールアドレス", 
                    key="jquants_email",
                    help="JQuantsアカウントのメールアドレス"
                )
            
            with col2:
                jquants_password = st.text_input(
                    "パスワード",
                    type="password",
                    key="jquants_password",
                    help="JQuantsアカウントのパスワード"
                )
            
            if jquants_email and jquants_password:
                jquants_config = {
                    'email': jquants_email,
                    'password': jquants_password
                }
            
            st.markdown("#### 🌍 Alpha Vantage API（米国株・グローバル）")
            alpha_vantage_key = st.text_input(
                "API Key",
                type="password",
                key="alpha_vantage_key",
                help="Alpha Vantage API Key (無料取得可能)"
            )
            
            # API Key取得ヘルプ（expanderの代わりにinfoを使用）
            st.info("""
            **📚 API Key取得方法**
            
            **🇯🇵 JQuants API (日本株)**
            - サイト: https://jpx-jquants.com/
            - 無料プランあり
            - 日本の全上場企業を検索可能
            
            **🌍 Alpha Vantage API (グローバル)**
            - サイト: https://www.alphavantage.co/support/#api-key
            - 無料プランあり（月500回まで）
            - 世界中の株式を検索可能
            """)
        
        return {
            'jquants_config': jquants_config,
            'alpha_vantage_key': alpha_vantage_key
        }
    
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
            help="入力後にEnterキーを押すか、「🚀 分析開始」ボタンを押してください"
        )
        
        # 入力値の保存（次回開いた時のため）
        if stock_code and stock_code != st.session_state.direct_input_symbol:
            st.session_state.direct_input_symbol = stock_code
        
        # 銘柄コードの簡易説明
        if stock_code:
            company_info = UIComponents._get_company_description(stock_code)
            if company_info != "銘柄コードの説明を取得できませんでした":
                st.info(f"💼 {company_info}")
        
        UIComponents.render_tip_box(
            "💡 銘柄コードの例",
            "🇯🇵 **日本株**: 7203.T（トヨタ）、6758.T（ソニー）、9984.T（ソフトバンク）<br>" +
            "🇺🇸 **米国株**: AAPL（Apple）、GOOGL（Google）、TSLA（Tesla）、NVDA（NVIDIA）<br>" +
            "💡 **ヒント**: .Tは東京証券取引所を意味します"
        )
        
        return stock_code
    
    @staticmethod
    def _get_company_description(symbol: str) -> str:
        """銘柄コードから会社説明を取得"""
        # 日本の主要企業
        japan_companies = {
            "7203.T": "トヨタ自動車 - 世界最大級の自動車メーカー",
            "6758.T": "ソニーグループ - エレクトロニクス・エンタテインメント企業", 
            "9984.T": "ソフトバンクグループ - 通信・投資企業",
            "6861.T": "キーエンス - 産業用センサー・測定機器メーカー",
            "4519.T": "中外製薬 - 医薬品メーカー",
            "7974.T": "任天堂 - ゲーム機・ソフトメーカー",
            "9983.T": "ファーストリテイリング - ユニクロ運営企業",
            "8035.T": "東京エレクトロン - 半導体製造装置メーカー",
            "6954.T": "ファナック - 産業用ロボットメーカー",
            "4661.T": "オリエンタルランド - 東京ディズニーランド運営"
        }
        
        # 米国の主要企業  
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
        
        # 日本企業の説明を最初に検索
        if symbol in japan_companies:
            return japan_companies[symbol]
        
        # 米国企業の説明を検索
        if symbol in us_companies:
            return us_companies[symbol]
        
        # その他の場合
        if symbol.endswith('.T'):
            return "日本の上場企業"
        elif symbol.replace('.', '').replace('-', '').isalnum():
            return "米国の上場企業"
        
        return "銘柄コードの説明を取得できませんでした"
    
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
                "株が「買われ過ぎ」「売られ過ぎ」かを測る指標です<br>" +
                "⬆️ 期間を長くすると：変化がゆっくり（反応が遅い）<br>" +
                "⬇️ 期間を短くすると：変化が早い（敏感）<br>" +
                "👍 おすすめ：初心者は14のままでOK<br>" +
                "📌使い方の例：RSI 70%超で売り、30%未満で買いの目安"
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
            st.markdown("**初期資金**")
            initial_capital = st.number_input(
                "初期資金（円）",
                min_value=BACKTEST_RANGES['initial_capital']['min'],
                max_value=BACKTEST_RANGES['initial_capital']['max'],
                value=1000000,
                step=100000
            )
            UIComponents.render_tip_box(
                "💰 初期資金とは",
                "投資シミュレーションで使う仮想のお金です<br>" +
                "⬆️ 多くすると：利益・損失の金額が大きくなる<br>" +
                "⬇️ 少なくすると：利益・損失の金額が小さくなる<br>" +
                "👍 おすすめ：100万円程度で練習"
            )
            
            st.markdown("**取引手数料（%）**")
            trade_cost_rate = st.slider(
                "手数料",
                BACKTEST_RANGES['trade_cost_rate']['min'],
                BACKTEST_RANGES['trade_cost_rate']['max'],
                0.1,
                step=0.01
            )
            UIComponents.render_tip_box(
                "💳 取引手数料とは",
                "株を買ったり売ったりする時にかかる費用です<br>" +
                "⬆️ 高くすると：より現実的なシミュレーション<br>" +
                "⬇️ 低くすると：手数料の影響が少ない<br>" +
                "👍 おすすめ：ネット証券なら0.1%程度"
            )
        
        with col2:
            st.markdown("**ストップロス（%）**")
            stop_loss_pct = st.slider(
                "損切り",
                BACKTEST_RANGES['stop_loss_pct']['min'],
                BACKTEST_RANGES['stop_loss_pct']['max'],
                5.0,
                step=0.5
            )
            UIComponents.render_tip_box(
                "🛡️ ストップロスとは",
                "損失を制限するための自動売却設定です<br>" +
                "⬆️ 高くすると：大きな損失まで我慢する<br>" +
                "⬇️ 低くすると：小さな損失で早めに売却<br>" +
                "👍 おすすめ：初心者は5%程度"
            )
            
            st.markdown("**1回の取引リスク（%）**")
            risk_per_trade = st.slider(
                "取引リスク",
                BACKTEST_RANGES['risk_per_trade']['min'],
                BACKTEST_RANGES['risk_per_trade']['max'],
                2.0,
                step=0.1
            )
            UIComponents.render_tip_box(
                "⚖️ 取引リスクとは",
                "1回の取引で資金の何%まで使うかです<br>" +
                "⬆️ 高くすると：大きな利益も大きな損失も可能<br>" +
                "⬇️ 低くすると：安全だが利益も小さい<br>" +
                "👍 おすすめ：初心者は2%程度で安全に"
            )
     
        return {
            'initial_capital': initial_capital,
            'trade_cost_rate': trade_cost_rate / 100,  # パーセンテージを小数に変換
            'stop_loss_pct': stop_loss_pct / 100,
            'risk_per_trade': risk_per_trade / 100
        }
    
    @staticmethod
    def render_metrics(current_price: float, info: Dict[str, Any], df: pd.DataFrame):
        """主要指標を表示（メトリクス色分け修正版）"""
        col1, col2 = st.columns(2)
        
        with col1:
            # 通貨情報を取得
            currency = info.get('currency', 'USD')
            if currency == 'JPY':
                currency_symbol = '¥'
            elif currency == 'USD':
                currency_symbol = '$'
            elif currency == 'EUR':
                currency_symbol = '€'
            elif currency == 'GBP':
                currency_symbol = '£'
            else:
                currency_symbol = f'{currency} '
            
            st.metric(
                "💰 現在の株価",
                f"{currency_symbol}{current_price:,.2f}"
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
                
                # 前日からの変化 - デルタ値を適切にフォーマット
                st.metric(
                    "📈 前日比",
                    f"{change_pct:+.2f}%",
                    delta=f"{currency_symbol}{change_val:+.2f}"
                )
                
                # 期間中の変化率
                start_price = df['Close'].iloc[0]
                period_change_pct = (current_price / start_price - 1) * 100
                period_change_val = current_price - start_price
                
                st.metric(
                    "📊 期間全体",
                    f"{period_change_pct:+.2f}%",
                    delta=f"{currency_symbol}{period_change_val:+.2f}"
                )
            else:
                st.metric("📈 前日比", "データ不足")
                st.metric("📊 期間全体", "データ不足")
    
    @staticmethod
    def render_success_message(message_type: str, custom_message: str = None):
        """成功メッセージを表示"""
        if custom_message:
            st.success(custom_message)
        else:
            st.success("✅ 操作が完了しました")
    
    @staticmethod
    def render_warning_message(message_type: str, custom_message: str = None):
        """警告メッセージを表示"""
        if custom_message:
            st.warning(custom_message)
        else:
            st.warning("⚠️ 注意が必要です")
    
    @staticmethod
    def render_analysis_metrics(metrics_data: Dict[str, Any]):
        """分析メトリクスを表示"""
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_return = metrics_data.get('total_return', 0)
            st.metric(
                "総リターン",
                f"{total_return:.2f}%",
                delta=None
            )
        
        with col2:
            win_rate = metrics_data.get('win_rate', 0)
            st.metric(
                "勝率",
                f"{win_rate:.1f}%",
                delta=None
            )
        
        with col3:
            max_drawdown = metrics_data.get('max_drawdown', 0)
            st.metric(
                "最大ドローダウン",
                f"{max_drawdown:.2f}%",
                delta=None
            )
        
        with col4:
            sharpe_ratio = metrics_data.get('sharpe_ratio', 0)
            st.metric(
                "シャープレシオ",
                f"{sharpe_ratio:.2f}",
                delta=None
            )
    
    @staticmethod 
    def _validate_stock_symbol(symbol: str) -> Dict[str, Any]:
        """銘柄コードの簡易検証"""
        if not symbol:
            return {
                'is_valid': False, 
                'message': '銘柄コードを入力してください',
                'company_info': None
            }
        
        symbol = symbol.upper().strip()
        
        # 日本株の形式チェック
        if symbol.endswith('.T'):
            return {
                'is_valid': True, 
                'message': f'日本株として認識されました: {symbol}',
                'company_info': '日本の上場企業'
            }
        
        # 米国株やその他の形式チェック
        if len(symbol) >= 1 and symbol.replace('.', '').replace('-', '').isalnum():
            return {
                'is_valid': True, 
                'message': f'銘柄コードとして認識されました: {symbol}',
                'company_info': '海外の上場企業'
            }
        
        return {
            'is_valid': False, 
            'message': '銘柄コードの形式が正しくありません',
            'company_info': None
        }
    
    @staticmethod
    def _display_search_execution_plan(api_settings: Dict[str, Any], search_keyword: str):
        """検索実行計画を表示（削除済み）"""
        pass  # デバッグメッセージを削除
    
    @staticmethod
    def display_detailed_search_results(results: List[Dict[str, Any]], api_settings: Dict[str, Any]):
        """詳細な検索結果とAPI使用状況を表示（削除済み）"""
        pass  # デバッグメッセージを削除
    
    @staticmethod
    def show_search_debug_instructions():
        """検索デバッグ手順の表示（削除済み）"""
        pass  # デバッグメッセージを削除
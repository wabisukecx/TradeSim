# ui/settings_ui.py - 動的重み付け設定UI対応版
"""
設定UI - 銘柄選択、期間設定、テクニカル・バックテスト設定（動的重み付け対応）
"""

import streamlit as st
from typing import Dict, Any, Tuple
from datetime import datetime, timedelta

from config.settings import PERIOD_OPTIONS, WEIGHT_MODES, DYNAMIC_WEIGHT_PROFILES
from data import get_combined_search_results
from ui.components import UIComponents
from core.state_manager import StateManager
from core.app_controller import AppController


class SettingsUI:
    """設定UI管理クラス（動的重み付け対応）"""
    
    def __init__(self):
        self.app_controller = AppController()
    
    def render_main_settings(self) -> Tuple[str, Dict[str, Any]]:
        """メイン設定エリアを表示"""
        with st.expander("⚙️ 分析設定（どの会社を調べる？）", expanded=True):
            
            # 銘柄検索
            search_method = UIComponents.render_stock_search_section()
            
            if search_method == "🔍 会社名で検索":
                stock_code = self._handle_company_search()
            else:  # 直接入力
                stock_code = self._handle_direct_input()
            
            # 期間選択
            selected_period, days = UIComponents.render_period_selection()
            
            # 基本設定完了メッセージ
            st.markdown("---")
            st.success("✅ 基本設定完了！このまま「🚀 分析開始」を押してもOKです")
            
            UIComponents.render_tip_box(
                "💡 設定について",
                "上級者の方は下の「🔧 詳細設定」で細かく調整できます。<br>" +
                "初心者の方はそのままでも十分分析できます！"
            )
        
        # 詳細設定を独立したexpanderとして外部に配置
        technical_params, backtest_params, adaptive_params = self._render_advanced_settings_section()
        
        analysis_params = self.app_controller.get_analysis_parameters(
            selected_period, technical_params, backtest_params, adaptive_params
        )
        
        return stock_code, analysis_params
    
    def _handle_company_search(self) -> str:
        """会社名検索を処理（変更なし）"""
        search_keyword, api_key = UIComponents.render_company_search()
        
        if search_keyword:
            with st.spinner("🔍 検索中..."):
                results = get_combined_search_results(search_keyword, api_key)
            
            if results:
                st.markdown(f"**🎯 検索結果: '{search_keyword}'**")
                
                selected_stock = None
                for i, result in enumerate(results):
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
                
                return selected_stock if selected_stock else results[0]['symbol']
            else:
                st.warning("🔍 検索結果が見つかりませんでした")
                st.markdown("""
                **💡 検索のコツ:**
                - 会社の正式名称で試してみてください
                - 英語と日本語両方で試してみてください  
                - 略称でも検索できます
                """)
                return "AAPL"
        
        return "AAPL"
    
    def _handle_direct_input(self) -> str:
        """直接入力を処理（変更なし）"""
        UIComponents.render_explanation_box(
            "⌨️ 銘柄コード直接入力",
            "すでに銘柄コードを知っている場合はこちら<br>" +
            "💡 入力後にEnterキーを押すか、下の「🚀 分析開始」ボタンを押してください"
        )
        
        # 自動実行オプション
        col1, col2 = st.columns([3, 1])
        
        with col1:
            stock_code = st.text_input(
                "銘柄コード",
                value=StateManager.get_direct_input(),
                placeholder="例: AAPL, 7203.T, TSLA",
                key="direct_stock_input",
                help="入力後にEnterキーを押すと自動で検証されます"
            )
        
        with col2:
            auto_run = st.checkbox(
                "⚡ 自動実行", 
                value=False,
                help="チェックすると、銘柄コード入力後に自動で分析開始"
            )
        
        # 入力値の変更検知と処理
        if stock_code != StateManager.get_direct_input():
            StateManager.set_direct_input(stock_code)
            
            # リアルタイム検証と表示
            if stock_code.strip():
                is_valid, message, company_info = self.app_controller.validate_stock_symbol(stock_code)
                
                if is_valid:
                    st.success(f"✅ {message}")
                    if company_info:
                        st.info(f"💼 {company_info}")
                    
                    # 自動実行が有効で、有効な銘柄コードの場合
                    if auto_run and not StateManager.is_running():
                        st.info("🚀 自動分析を実行します...")
                        StateManager.trigger_auto_run()
                else:
                    st.warning(f"⚠️ {message}")
        return stock_code
    
    def _render_advanced_settings_section(self) -> Tuple[Dict[str, int], Dict[str, float], Dict[str, Any]]:
        """詳細設定セクション（動的重み付け対応）"""
        with st.expander("🔧 詳細設定（上級者向け）", expanded=False):
            st.markdown("### 🎛️ 分析・バックテスト詳細設定")
            
            UIComponents.render_explanation_box(
                "🎛️ 詳細設定について",
                "これらの設定は分析の精度や取引シミュレーションの条件を変更できます。<br>" +
                "💡 **初心者の方はそのままでOK** - デフォルト設定で十分学習できます！<br>" +
                "🔧 **上級者の方** - お好みに合わせて調整してください。"
            )
            
            # クイック設定プリセット
            self._render_preset_buttons()
            
            st.markdown("---")
            
            # === 新機能：重み付けモード選択 ===
            adaptive_params = self._render_weight_mode_selection()
            
            st.markdown("---")
            
            # 簡単設定 vs 詳細設定の選択
            setting_mode = st.radio(
                "設定モード",
                ["🔰 簡単設定（推奨）", "🔧 詳細設定（カスタマイズ）"],
                horizontal=True
            )
            
            if setting_mode == "🔰 簡単設定（推奨）":
                # 簡単設定モード
                self._render_simple_settings()
                
                # プリセット設定を使用
                preset_mode = StateManager.get_preset_mode()
                technical_params, backtest_params = self.app_controller.get_preset_settings(preset_mode)
            
            else:
                # 詳細設定モード
                st.markdown("#### 📈 テクニカル指標の詳細設定")
                technical_params = UIComponents.render_technical_settings()
                
                st.markdown("#### 💰 バックテスト詳細設定")
                backtest_params = UIComponents.render_backtest_settings()
        
        return technical_params, backtest_params, adaptive_params
    
    def _render_weight_mode_selection(self) -> Dict[str, Any]:
        """重み付けモード選択UIを表示"""
        st.markdown("### 🎯 分析手法の選択（NEW!）")
        
        UIComponents.render_explanation_box(
            "🆕 新機能：動的重み付け分析",
            "相場の状況に応じて分析手法を自動調整する高度な機能が追加されました！<br>" +
            "📊 **固定モード：** 従来の安定した分析（初心者推奨）<br>" +
            "🎯 **適応モード：** 相場パターンに応じた高精度分析（中級者以上）<br>" +
            "🔧 **手動モード：** 完全カスタマイズ（上級者向け）"
        )
        
        # 重み付けモード選択
        weight_modes = list(WEIGHT_MODES.keys())
        mode_names = [WEIGHT_MODES[mode]['name'] for mode in weight_modes]
        
        current_mode = StateManager.get_weight_mode()
        current_index = weight_modes.index(current_mode) if current_mode in weight_modes else 0
        
        selected_mode_index = st.selectbox(
            "分析手法を選択",
            range(len(mode_names)),
            index=current_index,
            format_func=lambda x: mode_names[x],
            key="weight_mode_select"
        )
        
        selected_mode = weight_modes[selected_mode_index]
        
        # モード説明
        mode_info = WEIGHT_MODES[selected_mode]
        st.info(f"""
        **{mode_info['name']}**  
        {mode_info['description']}  
        **適用対象:** {mode_info['suitable_for']}
        """)
        
        # 状態更新
        if selected_mode != StateManager.get_weight_mode():
            StateManager.set_weight_mode(selected_mode)
        
        adaptive_params = {'weight_mode': selected_mode}
        
        # モード別の詳細設定
        if selected_mode == 'adaptive':
            adaptive_params.update(self._render_adaptive_mode_settings())
        elif selected_mode == 'manual':
            adaptive_params.update(self._render_manual_mode_settings())
        
        return adaptive_params
    
    def _render_adaptive_mode_settings(self) -> Dict[str, Any]:
        """適応モード設定UIを表示"""
        st.markdown("#### 🎯 適応モード詳細設定")
        
        UIComponents.render_explanation_box(
            "🤖 適応モードの仕組み",
            "相場の波形パターンを自動検出し、最適な重み付けを適用します：<br>" +
            "📈 **上昇トレンド:** 移動平均・MACD重視<br>" +
            "📊 **レンジ相場:** RSI・ボリンジャーバンド重視<br>" +
            "⚡ **転換期:** MACD最重視で変化をキャッチ"
        )
        
        # パターン検出設定
        settings = StateManager.get_pattern_detection_settings()
        
        col1, col2 = st.columns(2)
        
        with col1:
            smoothing = st.checkbox(
                "📊 遷移平滑化",
                value=settings['enable_transition_smoothing'],
                help="パターン転換時の重み変化を滑らかにします"
            )
            
            StateManager.set_pattern_detection_setting('enable_transition_smoothing', smoothing)
        
        with col2:
            confidence_threshold = st.slider(
                "🎯 信頼度閾値",
                min_value=0.0,
                max_value=1.0,
                value=settings['confidence_threshold'],
                step=0.1,
                help="この値未満の信頼度の場合、固定重み付けを使用"
            )
            
            StateManager.set_pattern_detection_setting('confidence_threshold', confidence_threshold)
        
        # パターン一覧表示（expanderの代わりにチェックボックスで制御）
        show_patterns = st.checkbox("📋 検出可能なパターン一覧を表示", value=False)
        
        if show_patterns:
            st.markdown("##### 🎯 検出可能なパターン詳細")
            for pattern_key, pattern_info in DYNAMIC_WEIGHT_PROFILES.items():
                with st.container():
                    st.markdown(f"**{pattern_info['name']}**")
                    st.markdown(f"- {pattern_info['description']}")
                    st.markdown(f"- 戦略: {pattern_info['strategy_hint']}")
                    st.markdown("---")
        
        return {
            'enable_transition_smoothing': smoothing,
            'confidence_threshold': confidence_threshold
        }
    
    def _render_manual_mode_settings(self) -> Dict[str, Any]:
        """手動モード設定UIを表示"""
        st.markdown("#### 🔧 手動重み付け設定")
        
        UIComponents.render_explanation_box(
            "⚖️ 重み付けのカスタマイズ",
            "各テクニカル指標の重要度を手動で調整できます。<br>" +
            "合計が100%になるよう自動調整されます。"
        )
        
        current_weights = StateManager.get_manual_weights()
        
        # 重み付けスライダー
        col1, col2 = st.columns(2)
        
        with col1:
            ma_weight = st.slider(
                "📈 移動平均の重み",
                min_value=0.0,
                max_value=1.0,
                value=current_weights['ma_trend'],
                step=0.05,
                help="トレンドの方向性を重視する度合い"
            )
            
            rsi_weight = st.slider(
                "🌡️ RSIの重み",
                min_value=0.0,
                max_value=1.0,
                value=current_weights['rsi'],
                step=0.05,
                help="買われすぎ・売られすぎを重視する度合い"
            )
            
            volume_weight = st.slider(
                "📦 出来高の重み",
                min_value=0.0,
                max_value=1.0,
                value=current_weights['volume'],
                step=0.05,
                help="取引量の変化を重視する度合い"
            )
        
        with col2:
            bollinger_weight = st.slider(
                "📊 ボリンジャーバンドの重み",
                min_value=0.0,
                max_value=1.0,
                value=current_weights['bollinger'],
                step=0.05,
                help="価格の相対的位置を重視する度合い"
            )
            
            macd_weight = st.slider(
                "⚡ MACDの重み",
                min_value=0.0,
                max_value=1.0,
                value=current_weights['macd'],
                step=0.05,
                help="モメンタムの変化を重視する度合い"
            )
        
        # 重み付けの正規化と更新
        manual_weights = {
            'ma_trend': ma_weight,
            'rsi': rsi_weight,
            'bollinger': bollinger_weight,
            'macd': macd_weight,
            'volume': volume_weight
        }
        
        # 正規化
        total_weight = sum(manual_weights.values())
        if total_weight > 0:
            normalized_weights = {k: v / total_weight for k, v in manual_weights.items()}
        else:
            normalized_weights = {k: 0.2 for k in manual_weights.keys()}  # 均等配分
        
        StateManager.set_manual_weights(normalized_weights)
        
        # 重み配分表示
        st.markdown("**現在の重み配分:**")
        weight_display = "  ".join([
            f"{k}: {v:.1%}" for k, v in normalized_weights.items()
        ])
        st.code(weight_display)
        
        # プリセットボタン
        st.markdown("**クイック設定:**")
        preset_col1, preset_col2, preset_col3 = st.columns(3)
        
        with preset_col1:
            if st.button("📈 トレンド重視", help="移動平均・MACDを重視"):
                trend_weights = {
                    'ma_trend': 0.4, 'macd': 0.3, 'bollinger': 0.15,
                    'rsi': 0.1, 'volume': 0.05
                }
                StateManager.set_manual_weights(trend_weights)
                st.rerun()
        
        with preset_col2:
            if st.button("📊 レンジ重視", help="RSI・ボリンジャーを重視"):
                range_weights = {
                    'rsi': 0.35, 'bollinger': 0.35, 'ma_trend': 0.15,
                    'macd': 0.1, 'volume': 0.05
                }
                StateManager.set_manual_weights(range_weights)
                st.rerun()
        
        with preset_col3:
            if st.button("⚖️ バランス型", help="均等な重み付け"):
                balanced_weights = {
                    'ma_trend': 0.2, 'rsi': 0.2, 'bollinger': 0.3,
                    'macd': 0.3, 'volume': 0.1
                }
                StateManager.set_manual_weights(balanced_weights)
                st.rerun()
        
        return {'manual_weights': normalized_weights}
    
    def _render_preset_buttons(self):
        """設定プリセットボタンを表示（動的重み付け対応）"""
        st.markdown("#### 🎯 クイック設定プリセット")
        
        UIComponents.render_explanation_box(
            "🎯 プリセット選択",
            "お好みのリスクレベルに合わせて設定を一括変更できます。<br>" +
            "動的重み付けの設定も自動で最適化されます。"
        )
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔰 初心者向け", help="安全重視の設定", use_container_width=True):
                StateManager.set_preset_mode("beginner")
                # 初心者は固定重み付け
                StateManager.set_weight_mode("fixed")
                st.success("✅ 初心者向け設定を適用しました")
                st.rerun()
        
        with col2:
            if st.button("⚖️ バランス型", help="リスクとリターンのバランス", use_container_width=True):
                StateManager.set_preset_mode("balanced")
                # バランス型は適応モード
                StateManager.set_weight_mode("adaptive")
                st.success("✅ バランス型設定を適用しました")
                st.rerun()
        
        with col3:
            if st.button("🚀 積極型", help="高リスク・高リターン", use_container_width=True):
                StateManager.set_preset_mode("aggressive")
                # 積極型も適応モード
                StateManager.set_weight_mode("adaptive")
                st.success("✅ 積極型設定を適用しました")
                st.rerun()
    
    def _render_simple_settings(self):
        """簡単設定モードの表示（動的重み付け情報追加）"""
        UIComponents.render_explanation_box(
            "🔰 簡単設定モード",
            "初心者におすすめの設定を自動で使用します！<br>" +
            "📊 **分析期間:** 中期（20日・50日移動平均）<br>" +
            "💰 **仮想資金:** 100万円でシミュレーション<br>" +
            "⚡ **リスク設定:** 安全重視（2%リスク・5%損切り）<br>" +
            "🎯 **重み付け:** プリセットに応じて自動選択"
        )
        
        # 現在のプリセット表示
        current_preset = StateManager.get_preset_mode()
        current_weight_mode = StateManager.get_weight_mode()
        
        preset_names = {
            'beginner': '🔰 初心者向け（超安全・固定重み付け）',
            'balanced': '⚖️ バランス型（推奨・適応重み付け）',
            'aggressive': '🚀 積極型（ハイリスク・適応重み付け）'
        }
        
        weight_mode_names = {
            'fixed': '固定重み付け',
            'adaptive': '適応重み付け',
            'manual': '手動重み付け'
        }
        
        st.info(f"""
        📋 **現在の設定:**  
        - プリセット: {preset_names.get(current_preset, 'バランス型')}  
        - 重み付け方式: {weight_mode_names.get(current_weight_mode, '固定重み付け')}
        """)
        
        # 簡単設定の内容を表示
        technical_params, backtest_params = self.app_controller.get_preset_settings(current_preset)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**📈 分析設定**")
            st.info(f"""
            - 短期移動平均: {technical_params['short_ma']}日
            - 長期移動平均: {technical_params['long_ma']}日
            - RSI期間: {technical_params['rsi_period']}日
            - ボリンジャーバンド: {technical_params['bb_period']}日
            """)
        
        with col2:
            st.markdown("**💰 シミュレーション設定**")
            st.info(f"""
            - 仮想初期資金: {backtest_params['initial_capital']/10000:.0f}万円
            - リスク許容率: {backtest_params['risk_per_trade']}%
            - 損切りライン: {backtest_params['stop_loss_pct']}%
            - 利益確定: {backtest_params['take_profit_pct']}%
            """)
        
        UIComponents.render_tip_box(
            "💡 動的重み付けについて",
            f"現在は「{weight_mode_names.get(current_weight_mode)}」を使用中です。<br>" +
            "🔰 **固定重み付け:** 安定した従来の分析方式<br>" +
            "🎯 **適応重み付け:** 相場状況に応じて重み自動調整<br>" +
            "🔧 **手動重み付け:** お好みで完全カスタマイズ"
        )
# ui/settings_ui.py
"""
設定UI - 銘柄選択、期間設定、テクニカル・バックテスト設定（推奨文言削除版）
"""

import streamlit as st
from typing import Dict, Any, Tuple
from datetime import datetime, timedelta

from config.settings import PERIOD_OPTIONS
from data import get_combined_search_results
from ui.components import UIComponents
from core.state_manager import StateManager
from core.app_controller import AppController


class SettingsUI:
    """設定UI管理クラス"""
    
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
        technical_params, backtest_params = self._render_advanced_settings_section()
        
        analysis_params = self.app_controller.get_analysis_parameters(
            selected_period, technical_params, backtest_params
        )
        
        return stock_code, analysis_params
    
    def _handle_company_search(self) -> str:
        """会社名検索を処理"""
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
        """直接入力を処理"""
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
        
    def _render_advanced_settings_section(self) -> Tuple[Dict[str, int], Dict[str, float]]:
        """詳細設定セクション"""
        with st.expander("🔧 詳細設定（上級者向け）", expanded=False):
            st.markdown("### 🎛️ テクニカル・バックテスト詳細設定")
            
            UIComponents.render_explanation_box(
                "🎛️ 詳細設定について",
                "これらの設定は分析の精度や取引シミュレーションの条件を変更できます。<br>" +
                "💡 **初心者の方はそのままでOK** - デフォルト設定で十分学習できます！<br>" +
                "🔧 **上級者の方** - お好みに合わせて調整してください。"
            )
            
            # クイック設定プリセット
            self._render_preset_buttons()
            
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
        
        return technical_params, backtest_params
    
    def _render_preset_buttons(self):
        """設定プリセットボタンを表示"""
        st.markdown("#### 🎯 クイック設定プリセット")
        
        UIComponents.render_explanation_box(
            "🎯 プリセット選択",
            "お好みのリスクレベルに合わせて設定を一括変更できます"
        )
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔰 初心者向け", help="安全重視の設定", use_container_width=True):
                StateManager.set_preset_mode("beginner")
                st.success("✅ 初心者向け設定を適用しました")
                st.rerun()
        
        with col2:
            if st.button("⚖️ バランス型", help="リスクとリターンのバランス", use_container_width=True):
                StateManager.set_preset_mode("balanced")
                st.success("✅ バランス型設定を適用しました")
                st.rerun()
        
        with col3:
            if st.button("🚀 積極型", help="高リスク・高リターン", use_container_width=True):
                StateManager.set_preset_mode("aggressive")
                st.success("✅ 積極型設定を適用しました")
                st.rerun()
    
    def _render_simple_settings(self):
        """簡単設定モードの表示"""
        UIComponents.render_explanation_box(
            "🔰 簡単設定モード",
            "初心者におすすめの設定を自動で使用します！<br>" +
            "📊 **分析期間:** 中期（20日・50日移動平均）<br>" +
            "💰 **仮想資金:** 100万円でシミュレーション<br>" +
            "⚡ **リスク設定:** 安全重視（2%リスク・5%損切り）"
        )
        
        # 現在のプリセット表示
        current_preset = StateManager.get_preset_mode()
        preset_names = {
            'beginner': '🔰 初心者向け（超安全）',
            'balanced': '⚖️ バランス型（推奨）',
            'aggressive': '🚀 積極型（ハイリスク）'
        }
        
        st.info(f"📋 **現在の設定:** {preset_names.get(current_preset, 'バランス型')}")
        
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
            "💡 設定について",
            "これらは投資学習でよく使われる標準的な設定です。<br>" +
            "慣れてきたら「🔧 詳細設定」でカスタマイズしてみてください！"
        )
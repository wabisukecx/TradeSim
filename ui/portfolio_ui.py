# ui/portfolio_ui.py
"""
ポートフォリオ管理UI
"""

import streamlit as st
from typing import Dict, Any

from ui.components import UIComponents
from portfolio import PortfolioManager
from core.state_manager import StateManager


class PortfolioUI:
    """ポートフォリオUI管理クラス"""
    
    def __init__(self):
        self.portfolio_manager = PortfolioManager()
    
    def render_portfolio_section(self):
        """ポートフォリオ管理セクションを表示"""
        st.markdown("---")
        st.markdown("## 💼 ウォッチリスト")
        
        UIComponents.render_explanation_box(
            "📂 ウォッチリストって何？",
            "気になる会社の株をリストにして保存できる機能です！<br>" +
            "「後で勉強したい会社」や「注目している会社」を覚えておけます。"
        )
        
        # 削除機能のみ表示
        if st.session_state.portfolio:
            st.markdown("### ➖ 会社を削除")
            portfolio_symbols = list(st.session_state.portfolio.keys())
            symbol_to_remove = st.selectbox(
                "削除する会社",
                portfolio_symbols,
                format_func=lambda x: f"{st.session_state.portfolio[x]['longName']} ({x})",
                key="remove_symbol_select"
            )
            
            if st.button("削除", key="remove_portfolio_main", use_container_width=True):
                message = self.portfolio_manager.remove_stock(symbol_to_remove)
                st.success(message)
                st.rerun()
        else:
            st.info("💡 まだウォッチリストに会社がありません。上で会社を分析してから「リストに追加」してみてください！")
        
        # ポートフォリオ表示
        self._display_portfolio()
    
    def render_quick_portfolio_add(self):
        """ウォッチリスト追加UI（分析結果からの追加）"""
        st.markdown("### 💼 この会社をウォッチリストに追加")
        
        UIComponents.render_explanation_box(
            "📂 ウォッチリストへの追加",
            "分析結果を見て気に入った会社を「お気に入りリスト」に保存できます！<br>" +
            "後で他の会社と比較したり、定期的にチェックしたりするのに便利です。"
        )
        
        already_in_portfolio = st.session_state.current_stock_code in st.session_state.portfolio
        
        if already_in_portfolio:
            current_data = st.session_state.portfolio[st.session_state.current_stock_code]
            st.info(f"✅ すでにリストに追加済み: {current_data['shares']}株 (平均価格: ¥{current_data['avg_price']:.2f})")
        
        quick_shares = st.number_input(
            "仮想株数",
            min_value=1,
            value=10,
            step=1,
            key="quick_shares"
        )

        # ボタンも下にそのまま配置
        button_text = "株数を追加" if already_in_portfolio else "リストに追加"
        if st.button(button_text, key="quick_add_current", use_container_width=True):
            self._add_current_stock_to_portfolio(quick_shares)
    
    def _add_current_stock_to_portfolio(self, shares: int):
        """現在の銘柄をポートフォリオに追加"""
        analysis_data = StateManager.get_analysis_data()
        if not analysis_data:
            st.error("❌ 分析データがありません")
            return
        
        df = analysis_data['df']
        current_price = df['Close'].iloc[-1]
        company_name = st.session_state.current_company_name
        
        try:
            message = self.portfolio_manager.add_stock(
                st.session_state.current_stock_code, 
                shares, 
                current_price, 
                company_name
            )
            st.success(message)
            st.info(f"📈 {company_name} ({st.session_state.current_stock_code}) - {shares}株追加 - ¥{current_price:.2f}/株")
            st.balloons()
            st.rerun()
        except Exception as e:
            st.error(f"❌ エラーが発生しました: {e}")
    
    def _display_portfolio(self):
        """ポートフォリオを表示"""
        summary = self.portfolio_manager.get_portfolio_summary()
        
        if summary['position_count'] > 0:
            with st.expander("📊 保存されている会社一覧", expanded=True):
                
                # ポートフォリオテーブル
                df = self.portfolio_manager.export_portfolio()
                st.dataframe(df, hide_index=True, use_container_width=True)
                
                # 全体サマリー
                self._render_portfolio_summary(summary)
                
                # パフォーマンス分析
                self._render_portfolio_performance()
    
    def _render_portfolio_summary(self, summary: Dict[str, Any]):
        """ポートフォリオサマリーを表示"""
        st.markdown("#### 📈 全体の変動（学習用）")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("💰 記録時の合計", f"¥{summary['total_cost']:,.0f}")
        with col2:
            st.metric("💎 現在の価値", f"¥{summary['current_value']:,.0f}")
        with col3:
            st.metric(
                "📊 変動", 
                f"¥{summary['total_pnl']:,.0f}", 
                delta=f"{summary['total_pnl_pct']:,.2f}%"
            )
    
    def _render_portfolio_performance(self):
        """ポートフォリオパフォーマンスを表示"""
        performance = self.portfolio_manager.get_portfolio_performance()
        if not performance:
            return
        
        st.markdown("#### 🏆 パフォーマンス分析")
        col1, col2 = st.columns(2)
        
        with col1:
            if performance['best_performer']:
                best = performance['best_performer']
                st.success(f"📈 **最高パフォーマンス**\n{best['name']}: +{best['return_pct']:.2f}%")
        
        with col2:
            if performance['worst_performer']:
                worst = performance['worst_performer']
                st.error(f"📉 **最低パフォーマンス**\n{worst['name']}: {worst['return_pct']:.2f}%")
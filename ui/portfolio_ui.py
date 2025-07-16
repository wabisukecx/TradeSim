# ui/portfolio_ui.py - 変動%追加・全体変動削除版
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
            
            # ✅ 通貨情報を考慮した表示
            currency = current_data.get('currency', 'USD')
            if currency == 'JPY':
                currency_symbol = '¥'
                price_format = f"{current_data['avg_price']:.0f}"
            elif currency == 'USD':
                currency_symbol = '$'
                price_format = f"{current_data['avg_price']:.2f}"
            else:
                currency_symbol = f'{currency} '
                price_format = f"{current_data['avg_price']:.2f}"
            
            st.info(f"✅ すでにリストに追加済み: {current_data['shares']}株 (平均価格: {currency_symbol}{price_format})")
        
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
        """現在の銘柄をポートフォリオに追加（通貨対応版）"""
        analysis_data = StateManager.get_analysis_data()
        if not analysis_data:
            st.error("❌ 分析データがありません")
            return
        
        df = analysis_data['df']
        info = analysis_data['info']  # ✅ 企業情報も取得
        current_price = df['Close'].iloc[-1]
        company_name = st.session_state.current_company_name
        
        # ✅ 通貨情報を取得
        currency = info.get('currency', 'USD')
        
        # 日本株の場合は円に設定
        if st.session_state.current_stock_code.endswith('.T'):
            currency = 'JPY'
        
        try:
            # ✅ 既存のadd_stockメソッドは変更せず、通貨情報を後から追加
            message = self.portfolio_manager.add_stock(
                st.session_state.current_stock_code, 
                shares, 
                current_price, 
                company_name
            )
            
            # ✅ 通貨情報を後から追加
            if st.session_state.current_stock_code in st.session_state.portfolio:
                st.session_state.portfolio[st.session_state.current_stock_code]['currency'] = currency
            
            st.success(message)
            
            # ✅ 通貨記号を適切に表示
            if currency == 'JPY':
                currency_symbol = '¥'
            elif currency == 'USD':
                currency_symbol = '$'
            else:
                currency_symbol = f'{currency} '
                
            st.info(f"📈 {company_name} ({st.session_state.current_stock_code}) - {shares}株追加 - {currency_symbol}{current_price:.2f}")
            st.balloons()
            st.rerun()
            
        except Exception as e:
            st.error(f"❌ エラーが発生しました: {e}")
    
    def _display_portfolio(self):
        """ポートフォリオを表示（変動%付き・全体変動なし）"""
        summary = self.portfolio_manager.get_portfolio_summary()
        
        if summary['position_count'] > 0:
            with st.expander("📊 保存されている会社一覧", expanded=True):
                
                # ✅ 通貨混在の場合の注意表示
                currencies = set()
                for position in summary.get('positions', []):
                    currencies.add(position.get('currency', 'USD'))
                
                if len(currencies) > 1:
                    st.info("💱 **注意**: 複数通貨の銘柄が含まれています。")
                
                # ✅ 価格取得エラーがある場合の注意表示
                if summary.get('positions'):
                    error_symbols = []
                    for position in summary['positions']:
                        if position['current_price'] == position['avg_price'] and position['pnl'] == 0:
                            error_symbols.append(position['symbol'])
                    
                    if error_symbols:
                        st.warning(f"⚠️ **価格取得エラー**: {', '.join(error_symbols)} の最新価格が取得できませんでした。保存時の価格を表示しています。")
                
                # ✅ ポートフォリオテーブル（変動%付き）
                df = self.portfolio_manager.export_portfolio()
                
                # デバッグ: 列名確認（本番では削除可能）
                if not df.empty:
                    # st.write(f"🔍 デバッグ - 列名: {list(df.columns)}")  # デバッグ用（必要に応じてコメントアウト）
                    pass
                
                # 変動%の色付け用のスタイリング
                def highlight_pnl(val):
                    """変動%に応じて色を付ける"""
                    if isinstance(val, str) and '%' in val:
                        try:
                            # '+' と '%' を除去して数値に変換
                            num_val = float(val.replace('%', '').replace('+', ''))
                            if num_val > 0:
                                return 'background-color: rgba(76, 175, 80, 0.2); color: #2E7D32; font-weight: bold'  # 緑
                            elif num_val < 0:
                                return 'background-color: rgba(244, 67, 54, 0.2); color: #C62828; font-weight: bold'  # 赤
                            else:
                                return 'background-color: rgba(255, 152, 0, 0.2); color: #E65100; font-weight: bold'  # オレンジ
                        except:
                            return ''
                    return ''
                
                # スタイル付きでテーブル表示
                if not df.empty and '変動%' in df.columns:
                    try:
                        # ✅ Styler.map を使用（applymap は非推奨）
                        styled_df = df.style.map(highlight_pnl, subset=['変動%'])
                        st.dataframe(styled_df, hide_index=True, use_container_width=True)
                    except Exception as e:
                        # スタイリングでエラーが発生した場合は通常のテーブル表示
                        st.warning(f"⚠️ テーブルスタイリングでエラー: {e}")
                        st.dataframe(df, hide_index=True, use_container_width=True)
                else:
                    st.dataframe(df, hide_index=True, use_container_width=True)
                
                # ✅ パフォーマンス分析（簡略版）
                self._render_portfolio_performance()
    
    def _render_portfolio_performance(self):
        """ポートフォリオパフォーマンスを表示（簡略版）"""
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
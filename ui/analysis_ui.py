# ui/analysis_ui.py
"""
分析結果表示UI
"""

import streamlit as st
from typing import Dict, Any

from config.settings import DISCLAIMERS
from ui.components import UIComponents
from ui.charts import ChartGenerator
from core.state_manager import StateManager


class AnalysisUI:
    """分析結果表示UI管理クラス"""
    
    def __init__(self):
        self.chart_generator = ChartGenerator()
    
    def render_analysis_results(self):
        """分析結果を表示"""
        analysis_data = StateManager.get_analysis_data()
        if not analysis_data:
            return
        
        st.markdown("---")
        company_name = st.session_state.current_company_name
        st.markdown(f"### 📊 {company_name} の分析結果")
        
        # 免責事項
        st.warning(DISCLAIMERS['analysis'])
        
        st.markdown("---")
        
        # 主要指標表示
        self._render_key_metrics(analysis_data)
        
        # 分析結果サマリー
        self._render_signal_analysis(analysis_data)
        
        # チャート表示
        self._render_charts(analysis_data)
        
        # バックテスト結果
        self._render_backtest_results(analysis_data)
        
        # 企業情報
        self._render_company_info(analysis_data)
    
    def _render_key_metrics(self, analysis_data: Dict[str, Any]):
        """主要指標を表示"""
        df = analysis_data['df']
        info = analysis_data['info']
        summary = analysis_data['summary']
        
        UIComponents.render_metrics(summary['current_price'], info, df)
    
    def _render_signal_analysis(self, analysis_data: Dict[str, Any]):
        """シグナル分析を表示"""
        signals = analysis_data['signals']
        signal_explanation = analysis_data['signal_explanation']
        
        st.markdown("### 🎯 テクニカル分析結果（参考情報）")
        
        UIComponents.render_explanation_box(
            "🤖 分析結果の見方",
            "コンピューターが色々な指標を見て、テクニカル分析を行いました。<br>" +
            "これは参考情報であり、投資助言ではありません。学習目的でご活用ください。"
        )
        
        # シグナル表示
        signal = signal_explanation['signal']
        buy_score = signal_explanation['buy_score']
        sell_score = signal_explanation['sell_score']
        
        if signal == 1:
            st.info(f"""
            ### 🟢 買いサインを検出
            **スコア: {buy_score:.1f}点**

            複数の指標が「買いサイン」を示しています。
            
            ⚠️ これは参考情報です。投資判断は自己責任でお願いします 🤔
            """)
        elif signal == -1:
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
        st.markdown("#### 📋 分析の根拠（詳しい理由）")
        UIComponents.render_explanation_box(
            "🔍 分析の根拠",
            "以下の4つの要素を総合的に分析しました：<br>" +
            "1. 📈 移動平均：トレンドの方向性<br>" +
            "2. 🌡️ RSI：相対的な強弱<br>" +
            "3. 📊 ボリンジャーバンド：価格の相対的位置<br>" +
            "4. ⚡ MACD：モメンタムの変化"
        )
        
        for reason in signal_explanation['reasons']:
            st.write(reason)
        
        st.warning(DISCLAIMERS['simulation'])
    
    def _render_charts(self, analysis_data: Dict[str, Any]):
        """チャートを表示"""
        with st.expander("📈 株価チャート（学習用）", expanded=True):
            UIComponents.render_explanation_box(
                "📊 チャートの見方",
                "🕯️ ローソク：緑=上昇日、赤=下降日<br>" +
                "📏 線：オレンジ=短期平均、青=長期平均<br>" +
                "🎯 矢印：🟢▲=買いサイン、🔴▼=売りサイン"
            )
            
            fig = self.chart_generator.create_technical_chart(
                analysis_data['df'],
                analysis_data['signals'],
                st.session_state.current_stock_code,
                analysis_data['parameters']
            )
            
            self.chart_generator.display_chart_with_controls(fig, "technical")
    
    def _render_backtest_results(self, analysis_data: Dict[str, Any]):
        """バックテスト結果を表示"""
        with st.expander("💰 取引シミュレーション結果（学習用）"):
            UIComponents.render_explanation_box(
                "🎮 シミュレーションって何？",
                "「もし過去にこのルールで取引していたら、結果はどうなっていた？」を計算しました。<br>" +
                "これは教育目的のシミュレーションであり、実際の投資成果ではありません。"
            )
            
            # ❌ 削除：新しいインスタンス作成
            # from analysis import BacktestEngine
            # backtest_engine = BacktestEngine()
            # performance = backtest_engine.get_performance_summary()
            
            # ✅ 追加：analysis_dataから直接取得
            portfolio_df = analysis_data.get('portfolio')
            trade_log = analysis_data.get('trade_log')
            params = analysis_data.get('parameters', {})
            
            # ✅ 修正：データの存在確認
            if portfolio_df is not None and not portfolio_df.empty:
                # 基本指標計算
                initial_capital = params.get('initial_capital', 1000000)
                final_value = portfolio_df['Total'].iloc[-1]
                total_return_pct = (final_value / initial_capital - 1) * 100
                total_return_abs = final_value - initial_capital
                
                # 詳細指標計算
                returns = portfolio_df['Returns'].dropna()
                max_drawdown = 0
                sharpe_ratio = 0
                
                if len(returns) > 0:
                    portfolio_values = portfolio_df['Total']
                    peak = portfolio_values.expanding().max()
                    drawdown = (portfolio_values / peak - 1) * 100
                    max_drawdown = drawdown.min()
                    
                    sharpe_ratio = (returns.mean() / returns.std()) * (252 ** 0.5) if returns.std() > 0 else 0
                
                # ✅ 元のコードをそのまま使用
                # パフォーマンス指標
                col1, col2 = st.columns(2)
                with col1:
                    st.metric(
                        "💵 仮想最終資産",
                        f"¥{final_value:,.0f}",
                        delta=f"¥{total_return_abs:,.0f}"
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
                
                # 成績判定
                if total_return_pct > 10.0:
                    st.success("🎉 優秀 素晴らしい成績です！")
                elif total_return_pct > 0.0:
                    st.info("👍 良好 まずまずの成績です")
                else:
                    st.warning("📚 要改善 改善が必要です")
                
                # 結果の見方説明
                UIComponents.render_tip_box(
                    "🤔 結果の見方",
                    "仮想最終資産：最初の資金がいくらになったか<br>" +
                    "総リターン：何%増えた（減った）か<br>" +
                    "最大下落幅：一番調子が悪い時にどのくらい減ったか<br>" +
                    "シャープレシオ：リスクを考慮した成績（1.0以上なら良好）"
                )
                
                # 資産推移グラフ
                st.markdown("#### 📈 仮想資産の推移")
                portfolio_fig = self.chart_generator.create_portfolio_chart(
                    portfolio_df, 
                    initial_capital
                )
                st.plotly_chart(portfolio_fig, use_container_width=True)
                
            else:
                st.warning("⚠️ バックテストデータが利用できません")
                st.info("💡 「🚀 分析開始」ボタンで分析を実行してください")
    
    def _render_company_info(self, analysis_data: Dict[str, Any]):
        """企業情報を表示"""
        with st.expander("🏢 企業情報（参考データ）"):
            UIComponents.render_explanation_box(
                "🏪 企業情報の見方",
                "投資を検討する前に、その会社がどんな会社なのか知ることが大切です！<br>" +
                "ただし、これらは過去や現在のデータであり、将来を保証するものではありません。"
            )
            
            info = analysis_data.get('info')
            if not info:
                st.warning("❌ 企業の詳しい情報を取得できませんでした")
                return
            
            # 通貨情報を取得
            currency = info.get('currency', 'JPY')
            
            # 基本情報
            if info.get('longBusinessSummary'):
                st.markdown("#### 📝 事業内容")
                summary = info.get('longBusinessSummary', '')
                if len(summary) > 200:
                    summary = summary[:200] + "..."
                st.write(summary)
            
            # 財務指標
            self._render_financial_metrics(info, currency)
            
            # 52週高安値
            self._render_price_range(info, currency)
            
            # 追加の財務指標
            self._render_additional_metrics(info)
    
    def _render_financial_metrics(self, info: Dict[str, Any], currency: str):
        """主要財務指標を表示"""
        st.markdown("#### 💼 主要財務指標（参考情報）")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # PER（株価収益率）
            self._render_per_metric(info)
            
            # 業種
            sector = info.get('sector', 'N/A')
            st.metric("業種", sector)
            
            # 時価総額
            self._render_market_cap(info)
        
        with col2:
            # PBR（株価純資産倍率）
            self._render_pbr_metric(info)
            
            # 配当利回り
            self._render_dividend_yield(info)
            
            # 本社所在地
            country = info.get('country', 'N/A')
            st.metric("本社所在地", country)
            
            # 従業員数
            employees = info.get('fullTimeEmployees')
            if employees and employees > 0:
                st.metric("従業員数", f"{employees:,}人")
            else:
                st.metric("従業員数", "データなし")
    
    def _render_per_metric(self, info: Dict[str, Any]):
        """PER指標を表示"""
        per = info.get('trailingPE', 'N/A')
        if per != 'N/A' and per is not None:
            try:
                per_value = float(per)
                if per_value < 0:
                    per_status, per_color = "赤字", "🔴"
                elif per_value < 15:
                    per_status, per_color = "低い", "🟡"
                elif per_value > 25:
                    per_status, per_color = "高い", "🟡"
                else:
                    per_status, per_color = "標準的", "🟢"
                
                st.markdown(f"""
                <div style="background: white; padding: 1rem; border-radius: 0.5rem; border: 1px solid #ddd;">
                    <div style="color: #666; font-size: 0.9rem;">PER（株価収益率）</div>
                    <div style="font-size: 1.5rem; font-weight: bold; color: #333;">{per_value:.1f}</div>
                    <div style="color: {'red' if per_color == '🔴' else 'orange' if per_color == '🟡' else 'green'}; font-size: 0.9rem; margin-top: 0.3rem;">
                        {per_color} {per_status}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                UIComponents.render_tip_box(
                    "💡 PERとは：",
                    "株価が1株あたり利益の何倍かを示す指標<br>" +
                    "一般的に15以下は低い、25以上は高いとされます<br>" +
                    "マイナスの場合は赤字（最終損失）のため計算不可"
                )
            except (ValueError, TypeError):
                st.markdown("""
                <div style="background: white; padding: 1rem; border-radius: 0.5rem; border: 1px solid #ddd;">
                    <div style="color: #666; font-size: 0.9rem;">PER（株価収益率）</div>
                    <div style="font-size: 1.5rem; font-weight: bold; color: #333;">データ異常</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background: white; padding: 1rem; border-radius: 0.5rem; border: 1px solid #ddd;">
                <div style="color: #666; font-size: 0.9rem;">PER（株価収益率）</div>
                <div style="font-size: 1.5rem; font-weight: bold; color: #333;">データなし</div>
            </div>
            """, unsafe_allow_html=True)
    
    def _render_pbr_metric(self, info: Dict[str, Any]):
        """PBR指標を表示"""
        pbr = info.get('priceToBook', 'N/A')
        if pbr != 'N/A' and pbr is not None:
            try:
                pbr_value = float(pbr)
                if pbr_value > 3.0:
                    pbr_status, pbr_color = "高い", "🟡"
                elif pbr_value > 1.0:
                    pbr_status, pbr_color = "標準的", "🟢"
                elif pbr_value > 0:
                    pbr_status, pbr_color = "低い", "🟡"
                else:
                    pbr_status, pbr_color = "債務超過", "🔴"
                
                st.markdown(f"""
                <div style="background: white; padding: 1rem; border-radius: 0.5rem; border: 1px solid #ddd;">
                    <div style="color: #666; font-size: 0.9rem;">PBR（株価純資産倍率）</div>
                    <div style="font-size: 1.5rem; font-weight: bold; color: #333;">{pbr_value:.1f}</div>
                    <div style="color: {'red' if pbr_color == '🔴' else 'orange' if pbr_color == '🟡' else 'green'}; font-size: 0.9rem; margin-top: 0.3rem;">
                        {pbr_color} {pbr_status}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                UIComponents.render_tip_box(
                    "💡 PBRとは：",
                    "株価が1株あたり純資産の何倍かを示す指標<br>" +
                    "1.0以下は低い、3.0以上は高いとされます<br>" +
                    "マイナスの場合は債務超過（負債>資産）を意味します"
                )
            except (ValueError, TypeError):
                st.markdown("""
                <div style="background: white; padding: 1rem; border-radius: 0.5rem; border: 1px solid #ddd;">
                    <div style="color: #666; font-size: 0.9rem;">PBR（株価純資産倍率）</div>
                    <div style="font-size: 1.5rem; font-weight: bold; color: #333;">データ異常</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background: white; padding: 1rem; border-radius: 0.5rem; border: 1px solid #ddd;">
                <div style="color: #666; font-size: 0.9rem;">PBR（株価純資産倍率）</div>
                <div style="font-size: 1.5rem; font-weight: bold; color: #333;">データなし</div>
            </div>
            """, unsafe_allow_html=True)
    
    def _render_market_cap(self, info: Dict[str, Any]):
        """時価総額を表示"""
        market_cap = info.get('marketCap')
        if market_cap and market_cap > 0:
            if market_cap > 1e12:
                cap_display = f"{market_cap/1e12:.1f}兆円"
            elif market_cap > 1e9:
                cap_display = f"{market_cap/1e9:.1f}億円"
            else:
                cap_display = f"{market_cap/1e6:.1f}百万円"
            st.metric("時価総額", cap_display)
        else:
            st.metric("時価総額", "データなし")
    
    def _render_dividend_yield(self, info: Dict[str, Any]):
        """配当利回りを表示"""
        div_yield = info.get('dividendYield', 0)
        dividend_rate = info.get('dividendRate', 0)
        current_price_for_div = info.get('currentPrice', info.get('regularMarketPrice', 0))
        
        try:
            if div_yield and div_yield > 0:
                div_yield_pct = div_yield * 100 if div_yield < 1 else div_yield
                
                if div_yield_pct > 50:
                    if dividend_rate and current_price_for_div and dividend_rate > 0 and current_price_for_div > 0:
                        calculated_yield = (dividend_rate / current_price_for_div) * 100
                        if calculated_yield <= 50:
                            st.metric("配当利回り", f"{calculated_yield:.2f}%")
                        else:
                            st.metric("配当利回り", "データ異常")
                    else:
                        st.metric("配当利回り", "データ異常")
                else:
                    st.metric("配当利回り", f"{div_yield_pct:.2f}%")
                    UIComponents.render_tip_box(
                        "💡 配当利回りとは：",
                        "株価に対する年間配当金の割合<br>" +
                        "3%以上は一般的に高配当とされます"
                    )
            else:
                if dividend_rate and current_price_for_div and dividend_rate > 0 and current_price_for_div > 0:
                    calculated_yield = (dividend_rate / current_price_for_div) * 100
                    if calculated_yield <= 50:
                        st.metric("配当利回り", f"{calculated_yield:.2f}%")
                        UIComponents.render_tip_box(
                            "💡 配当利回りとは：",
                            "株価に対する年間配当金の割合<br>" +
                            "3%以上は一般的に高配当とされます"
                        )
                    else:
                        st.metric("配当利回り", "計算不可")
                else:
                    st.metric("配当利回り", "配当なし")
        except Exception:
            st.metric("配当利回り", "データなし")
    
    def _render_price_range(self, info: Dict[str, Any], currency: str):
        """52週高安値を表示"""
        st.markdown("#### 📊 52週高安値")
        col1, col2 = st.columns(2)
        
        with col1:
            high_52 = info.get('fiftyTwoWeekHigh', 'N/A')
            if high_52 != 'N/A' and high_52 is not None:
                try:
                    high_value = float(high_52)
                    st.metric("52週高値", f"{high_value:,.2f} {currency}")
                except (ValueError, TypeError):
                    st.metric("52週高値", "データ異常")
            else:
                st.metric("52週高値", "データなし")
        
        with col2:
            low_52 = info.get('fiftyTwoWeekLow', 'N/A')
            if low_52 != 'N/A' and low_52 is not None:
                try:
                    low_value = float(low_52)
                    st.metric("52週安値", f"{low_value:,.2f} {currency}")
                except (ValueError, TypeError):
                    st.metric("52週安値", "データ異常")
            else:
                st.metric("52週安値", "データなし")
        
        UIComponents.render_tip_box(
            "💡 52週高安値について",
            "現在の株価が52週間の高値・安値のどの位置にあるかを確認できます"
        )
    
    def _render_additional_metrics(self, info: Dict[str, Any]):
        """追加の財務指標を表示"""
        st.markdown("#### 📈 その他の財務指標")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # ROE（自己資本利益率）
            self._render_roe_metric(info)
        
        with col2:
            # 営業利益率
            self._render_operating_margin(info)
    
    def _render_roe_metric(self, info: Dict[str, Any]):
        """ROE指標を表示"""
        roe = info.get('returnOnEquity')
        if roe is not None:
            try:
                roe_value = float(roe) * 100
                if roe_value > 15:
                    roe_status, roe_color = "優秀", "🟢"
                elif roe_value > 10:
                    roe_status, roe_color = "良好", "🟢"
                elif roe_value > 0:
                    roe_status, roe_color = "標準", "🟡"
                elif roe_value > -5:
                    roe_status, roe_color = "低い", "🟡"
                else:
                    roe_status, roe_color = "赤字", "🔴"
                
                st.markdown(f"""
                <div style="background: white; padding: 1rem; border-radius: 0.5rem; border: 1px solid #ddd;">
                    <div style="color: #666; font-size: 0.9rem;">ROE（自己資本利益率）</div>
                    <div style="font-size: 1.5rem; font-weight: bold; color: #333;">{roe_value:.1f}%</div>
                    <div style="color: {'red' if roe_color == '🔴' else 'orange' if roe_color == '🟡' else 'green'}; font-size: 0.9rem; margin-top: 0.3rem;">
                        {roe_color} {roe_status}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                UIComponents.render_tip_box(
                    "💡 ROEとは：",
                    "株主資本をどれだけ効率的に使って利益を上げているかを示す<br>" +
                    "15%以上は優秀、10%以上は良好とされます<br>" +
                    "マイナスの場合は赤字（最終損失）を意味します"
                )
            except (ValueError, TypeError):
                st.markdown("""
                <div style="background: white; padding: 1rem; border-radius: 0.5rem; border: 1px solid #ddd;">
                    <div style="color: #666; font-size: 0.9rem;">ROE（自己資本利益率）</div>
                    <div style="font-size: 1.5rem; font-weight: bold; color: #333;">データ異常</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background: white; padding: 1rem; border-radius: 0.5rem; border: 1px solid #ddd;">
                <div style="color: #666; font-size: 0.9rem;">ROE（自己資本利益率）</div>
                <div style="font-size: 1.5rem; font-weight: bold; color: #333;">データなし</div>
            </div>
            """, unsafe_allow_html=True)
    
    def _render_operating_margin(self, info: Dict[str, Any]):
        """営業利益率を表示"""
        operating_margin = info.get('operatingMargins')
        if operating_margin is not None:
            try:
                margin_value = float(operating_margin) * 100
                if margin_value > 20:
                    margin_status, margin_color = "高い", "🟢"
                elif margin_value > 10:
                    margin_status, margin_color = "標準", "🟢"
                elif margin_value > 0:
                    margin_status, margin_color = "低い", "🟡"
                else:
                    margin_status, margin_color = "赤字", "🔴"
                
                st.markdown(f"""
                <div style="background: white; padding: 1rem; border-radius: 0.5rem; border: 1px solid #ddd;">
                    <div style="color: #666; font-size: 0.9rem;">営業利益率</div>
                    <div style="font-size: 1.5rem; font-weight: bold; color: #333;">{margin_value:.1f}%</div>
                    <div style="color: {'red' if margin_color == '🔴' else 'orange' if margin_color == '🟡' else 'green'}; font-size: 0.9rem; margin-top: 0.3rem;">
                        {margin_color} {margin_status}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                UIComponents.render_tip_box(
                    "💡 営業利益率とは：",
                    "売上高に対する営業利益の割合<br>" +
                    "会社の本業での稼ぐ力を示します<br>" +
                    "マイナスの場合は営業赤字を意味します"
                )
            except (ValueError, TypeError):
                st.markdown("""
                <div style="background: white; padding: 1rem; border-radius: 0.5rem; border: 1px solid #ddd;">
                    <div style="color: #666; font-size: 0.9rem;">営業利益率</div>
                    <div style="font-size: 1.5rem; font-weight: bold; color: #333;">データ異常</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background: white; padding: 1rem; border-radius: 0.5rem; border: 1px solid #ddd;">
                <div style="color: #666; font-size: 0.9rem;">営業利益率</div>
                <div style="font-size: 1.5rem; font-weight: bold; color: #333;">データなし</div>
            </div>
            """, unsafe_allow_html=True)
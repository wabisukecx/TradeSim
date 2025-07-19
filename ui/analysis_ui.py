# ui/analysis_ui.py - メトリクス色分け修正版
"""
分析結果表示UI（動的重み付け対応・メトリクス色分け修正版）
"""

import streamlit as st
from typing import Dict, Any
import pandas as pd

from config.settings import DISCLAIMERS, RISK_LEVELS, DYNAMIC_WEIGHT_PROFILES
from ui.components import UIComponents
from ui.charts import ChartGenerator
from core.state_manager import StateManager


class AnalysisUI:
    """分析結果表示UI管理クラス（動的重み付け対応・メトリクス色分け修正版）"""
    
    def __init__(self):
        self.chart_generator = ChartGenerator()
    
    def render_analysis_results(self):
        """分析結果を表示（動的重み付け対応）"""
        analysis_data = StateManager.get_analysis_data()
        if not analysis_data:
            return
        
        st.markdown("---")
        company_name = st.session_state.current_company_name
        st.markdown(f"### 📊 {company_name} の分析結果")
        
        # 免責事項
        adaptive_info = StateManager.get_adaptive_info()
        if adaptive_info:
            st.warning(DISCLAIMERS['adaptive_analysis'])
        else:
            st.warning(DISCLAIMERS['analysis'])
        
        st.markdown("---")
        
        # === 新機能：動的重み付け結果表示 ===
        if adaptive_info:
            self._render_adaptive_analysis_results(adaptive_info)
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
    
    def _render_adaptive_analysis_results(self, adaptive_info: Dict[str, Any]):
        """動的重み付け分析結果を表示"""
        st.markdown("### 🎯 相場パターン分析結果（NEW!）")
        
        UIComponents.render_explanation_box(
            "🤖 AI相場パターン検出",
            "最新のAI技術により、現在の相場パターンを自動検出し、最適な分析手法を適用しました。<br>" +
            "これにより、固定的な分析よりも高精度な投資判断支援が可能です。"
        )
        
        # パターン検出結果の表示
        pattern_name = adaptive_info['pattern_name']
        confidence = adaptive_info['confidence']
        risk_level = adaptive_info['risk_level']
        strategy_hint = adaptive_info['strategy_hint']
        
        # 信頼度に基づく表示色の決定
        if confidence > 0.8:
            confidence_level = "高"
            confidence_color = "🟢"
            confidence_bg = "#e8f5e8"
        elif confidence > 0.6:
            confidence_level = "中"
            confidence_color = "🟡"
            confidence_bg = "#fff8e1"
        else:
            confidence_level = "低"
            confidence_color = "🔴"
            confidence_bg = "#ffebee"
        
        # リスクレベルの表示
        risk_info = RISK_LEVELS.get(risk_level, RISK_LEVELS['medium'])
        
        # メインパターン情報表示
        st.markdown(f"""
        <div style="
            background: {confidence_bg}; 
            padding: 1.5rem; 
            border-radius: 1rem; 
            border: 3px solid {risk_info['color']}; 
            margin: 1rem 0;
        ">
            <h4 style="margin: 0 0 1rem 0; color: #333;">
                {risk_info['icon']} 検出パターン: {pattern_name}
            </h4>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1rem;">
                <div>
                    <strong>🎯 検出信頼度:</strong><br>
                    {confidence_color} {confidence_level} ({confidence * 100:.1f}%)
                </div>
                <div>
                    <strong>⚠️ リスクレベル:</strong><br>
                    {risk_info['icon']} {risk_info['name']} ({risk_info['description']})
                </div>
            </div>
            <div style="background: rgba(255, 255, 255, 0.7); padding: 1rem; border-radius: 0.5rem;">
                <strong>📝 推奨戦略:</strong><br>
                {strategy_hint}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # 詳細情報の表示
        display_settings = StateManager.get_adaptive_display_settings()
        
        # 重み付け詳細表示
        if display_settings.get('show_weight_breakdown', True):
            self._render_weight_breakdown(adaptive_info)
        
        # パターン分析詳細
        if display_settings.get('show_pattern_confidence', True):
            self._render_pattern_analysis_details(adaptive_info)
    
    def _render_weight_breakdown(self, adaptive_info: Dict[str, Any]):
        """重み付け詳細を表示"""
        with st.expander("⚖️ 使用された重み付け詳細", expanded=False):
            weights = adaptive_info['weights_used']
            
            UIComponents.render_explanation_box(
                "📊 重み付けの意味",
                "各テクニカル指標にどの程度の重要度が割り当てられたかを示します。<br>" +
                "相場パターンに応じて、最も有効な指標により高い重みが設定されます。"
            )
            
            # 重み付けの可視化
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**📈 重み配分**")
                
                weight_display = []
                indicator_names = {
                    'ma_trend': '📈 移動平均',
                    'rsi': '🌡️ RSI',
                    'bollinger': '📊 ボリンジャーバンド',
                    'macd': '⚡ MACD',
                    'volume': '📦 出来高'
                }
                
                for indicator, weight in weights.items():
                    name = indicator_names.get(indicator, indicator)
                    percentage = weight * 100
                    
                    # プログレスバー風の表示
                    bar_width = int(percentage / 2)  # 50% = 25文字
                    bar = "█" * bar_width + "░" * (25 - bar_width)
                    
                    st.markdown(f"**{name}:** {percentage:.1f}%")
                    st.markdown(f"`{bar}`")
            
            with col2:
                st.markdown("**💡 重み付けの根拠**")
                
                pattern_type = adaptive_info['detected_pattern']
                pattern_profile = DYNAMIC_WEIGHT_PROFILES.get(pattern_type, {})
                
                if pattern_profile:
                    st.markdown(f"**パターン:** {pattern_profile.get('name', pattern_type)}")
                    st.markdown(f"**説明:** {pattern_profile.get('description', '')}")
                    
                    # 重み付けの理由説明
                    weight_reasons = self._get_weight_reasoning(pattern_type, weights)
                    for reason in weight_reasons:
                        st.markdown(f"• {reason}")
    
    def _get_weight_reasoning(self, pattern_type: str, weights: Dict[str, float]) -> list:
        """重み付けの理由を説明"""
        reasons = []
        
        if pattern_type in ['uptrend', 'downtrend']:
            if weights.get('ma_trend', 0) > 0.3:
                reasons.append("移動平均を重視：トレンドの方向性確認のため")
            if weights.get('macd', 0) > 0.25:
                reasons.append("MACDを重視：トレンドの継続性確認のため")
            
        elif pattern_type == 'range':
            if weights.get('rsi', 0) > 0.3:
                reasons.append("RSIを重視：レンジ内での反転ポイント特定のため")
            if weights.get('bollinger', 0) > 0.3:
                reasons.append("ボリンジャーバンドを重視：価格の上下限判定のため")
                
        elif pattern_type == 'transition':
            if weights.get('macd', 0) > 0.4:
                reasons.append("MACDを最重視：転換点の早期検出のため")
                
        elif pattern_type == 'acceleration':
            if weights.get('volume', 0) > 0.2:
                reasons.append("出来高を重視：加速の真正性確認のため")
        
        if not reasons:
            reasons.append("バランス型の重み付けを適用")
        
        return reasons
    
    def _render_pattern_analysis_details(self, adaptive_info: Dict[str, Any]):
        """パターン分析詳細を表示"""
        with st.expander("🔍 パターン分析詳細", expanded=False):
            analysis_details = adaptive_info.get('analysis_details', {})
            pattern_scores = adaptive_info.get('pattern_scores', {})
            
            if analysis_details:
                st.markdown("#### 📊 各要素の分析結果")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # トレンド分析
                    trend = analysis_details.get('trend', {})
                    if trend:
                        st.markdown("**📈 トレンド分析**")
                        direction_icon = "⬆️" if trend.get('direction') == 'up' else "⬇️" if trend.get('direction') == 'down' else "➡️"
                        st.markdown(f"- 方向: {direction_icon} {trend.get('direction', 'N/A')}")
                        st.markdown(f"- 強度: {trend.get('strength', 'N/A')}")
                        st.markdown(f"- 信頼度: {trend.get('confidence', 0):.1%}")
                    
                    # ボラティリティ分析
                    volatility = analysis_details.get('volatility', {})
                    if volatility:
                        st.markdown("**📊 ボラティリティ分析**")
                        state_icon = "📈" if volatility.get('state') == 'expanding' else "📉" if volatility.get('state') == 'contracting' else "➡️"
                        st.markdown(f"- 状態: {state_icon} {volatility.get('state', 'N/A')}")
                        st.markdown(f"- 信頼度: {volatility.get('confidence', 0):.1%}")
                
                with col2:
                    # モメンタム分析
                    momentum = analysis_details.get('momentum', {})
                    if momentum:
                        st.markdown("**⚡ モメンタム分析**")
                        direction_icon = "🚀" if 'up' in momentum.get('direction', '') else "🔻" if 'down' in momentum.get('direction', '') else "⚪"
                        st.markdown(f"- 方向: {direction_icon} {momentum.get('direction', 'N/A')}")
                        st.markdown(f"- 強度: {momentum.get('strength', 0):.2f}")
                        st.markdown(f"- 信頼度: {momentum.get('confidence', 0):.1%}")
                    
                    # 出来高分析
                    volume = analysis_details.get('volume', {})
                    if volume:
                        st.markdown("**📦 出来高分析**")
                        trend_icon = "📈" if volume.get('trend') == 'increasing' else "📉"
                        confirm_icon = "✅" if volume.get('confirmation') else "❌"
                        st.markdown(f"- トレンド: {trend_icon} {volume.get('trend', 'N/A')}")
                        st.markdown(f"- 確認: {confirm_icon} {volume.get('confirmation', False)}")
            
            # パターンスコア
            if pattern_scores:
                st.markdown("#### 🎯 パターン別スコア")
                
                # スコアを降順でソート
                sorted_scores = sorted(pattern_scores.items(), key=lambda x: x[1], reverse=True)
                
                for pattern, score in sorted_scores:
                    pattern_info = DYNAMIC_WEIGHT_PROFILES.get(pattern, {})
                    pattern_name = pattern_info.get('name', pattern)
                    
                    # プログレスバー
                    progress_width = int(score * 100)
                    color = "#4CAF50" if score > 0.7 else "#FF9800" if score > 0.3 else "#F44336"
                    
                    st.markdown(f"""
                    <div style="margin: 0.5rem 0;">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 0.2rem;">
                            <span><strong>{pattern_name}</strong></span>
                            <span>{score:.1%}</span>
                        </div>
                        <div style="background: #e0e0e0; border-radius: 0.5rem; height: 1rem;">
                            <div style="
                                background: {color}; 
                                width: {progress_width}%; 
                                border-radius: 0.5rem; 
                                height: 100%;
                                transition: width 0.3s ease;
                            "></div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
    
    def _render_key_metrics(self, analysis_data: Dict[str, Any]):
        """主要指標を表示（変更なし）"""
        df = analysis_data['df']
        info = analysis_data['info']
        summary = analysis_data['summary']
        
        UIComponents.render_metrics(summary['current_price'], info, df)
    
    def _render_signal_analysis(self, analysis_data: Dict[str, Any]):
        """シグナル分析を表示（動的重み付け対応）"""
        signals = analysis_data['signals']
        signal_explanation = analysis_data['signal_explanation']
        
        st.markdown("### 🎯 テクニカル分析結果（参考情報）")
        
        # 重み付けモードの表示
        weight_mode = StateManager.get_weight_mode()
        weight_mode_names = {
            'fixed': '🔒 固定重み付け',
            'adaptive': '🎯 適応重み付け',
            'manual': '🔧 手動重み付け'
        }
        
        UIComponents.render_explanation_box(
            "🤖 分析結果の見方",
            f"**使用した分析手法:** {weight_mode_names.get(weight_mode, '固定重み付け')}<br>" +
            "コンピューターが色々な指標を見て、テクニカル分析を行いました。<br>" +
            "これは参考情報であり、投資助言ではありません。学習目的でご活用ください。"
        )
        
        # シグナル表示
        signal = signal_explanation['signal']
        buy_score = signal_explanation['buy_score']
        sell_score = signal_explanation['sell_score']
        
        # 動的重み付け情報の追加
        adaptive_context = ""
        if signal_explanation.get('pattern_info'):
            pattern_info = signal_explanation['pattern_info']
            adaptive_context = f"""
            
            **🎯 検出パターン:** {pattern_info['pattern_name']}  
            **📊 信頼度:** {pattern_info['confidence'] * 100:.1f}%  
            **💡 戦略ヒント:** {pattern_info['strategy_hint']}
            """
        
        if signal == 1:
            st.info(f"""
            ### 🟢 買いサインを検出
            **スコア: {buy_score:.1f}点**

            複数の指標が「買いサイン」を示しています。{adaptive_context}
            
            ⚠️ これは参考情報です。投資判断は自己責任でお願いします 🤔
            """)
        elif signal == -1:
            st.info(f"""
            ### 🔴 売りサインを検出  
            **スコア: {sell_score:.1f}点**

            複数の指標が「売りサイン」を示しています。{adaptive_context}
            
            ⚠️ これは参考情報です。実際の取引は慎重にご判断ください ⚠️
            """)
        else:
            st.info(f"""
            ### ⚪ 中立シグナル（様子見）
            **買いスコア: {buy_score:.1f}点 | 売りスコア: {sell_score:.1f}点**

            現在は明確なサインが出ていない状況です。{adaptive_context}
            
            ⚠️ 引き続き注視が必要です 👀
            """)
        
        # 判断根拠
        st.markdown("#### 📋 分析の根拠（詳しい理由）")
        
        # 重み付け情報の表示
        if signal_explanation.get('weights_breakdown'):
            UIComponents.render_explanation_box(
                "⚖️ 使用された重み付け",
                f"**分析手法:** {weight_mode_names.get(weight_mode)}<br>" +
                "各指標の重要度を調整して総合判断を行いました。"
            )
            
            # 重み付けの簡易表示
            weights = signal_explanation['weights_breakdown']
            weight_text = " | ".join([f"{k}: {v:.1%}" for k, v in weights.items()])
            st.code(weight_text)
        
        UIComponents.render_explanation_box(
            "🔍 分析の根拠",
            "以下の要素を総合的に分析しました：<br>" +
            "1. 📈 移動平均：トレンドの方向性<br>" +
            "2. 🌡️ RSI：相対的な強弱<br>" +
            "3. 📊 ボリンジャーバンド：価格の相対的位置<br>" +
            "4. ⚡ MACD：モメンタムの変化<br>" +
            "5. 📦 出来高：取引の活発度"
        )
        
        for reason in signal_explanation['reasons']:
            st.write(reason)
        
        disclaimer_text = DISCLAIMERS.get('simulation', 
        "⚠️ これらは機械的な分析結果であり、将来の価格を予測するものではありません。")
        st.warning(disclaimer_text)
    
    def _render_charts(self, analysis_data: Dict[str, Any]):
        """チャートを表示（変更なし）"""
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
        """バックテスト結果を表示（メトリクス色分け修正版）"""
        with st.expander("💰 取引シミュレーション結果（学習用）"):
            UIComponents.render_explanation_box(
                "🎮 シミュレーションって何？",
                "「もし過去にこのルールで取引していたら、結果はどうなっていた？」を計算しました。<br>" +
                "これは教育目的のシミュレーションであり、実際の投資成果ではありません。<br>" +
                f"**分析手法:** {StateManager.get_weight_mode().upper()}モードを使用"
            )
            
            portfolio_df = analysis_data.get('portfolio')
            trade_log = analysis_data.get('trade_log')
            params = analysis_data.get('parameters', {})
            
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
                
                # ✅ 修正：パフォーマンス指標（正しいメトリクス色分け・小数点丸め対応）
                col1, col2 = st.columns(2)
                with col1:
                    # 仮想最終資産 - デルタ値を数値で渡して正しい色分けを適用
                    st.metric(
                        "💵 仮想最終資産",
                        f"¥{final_value:,.0f}",
                        delta=round(total_return_abs, 1),  # ✅ 小数点第1位まで丸める
                        delta_color="normal"
                    )
                    st.metric(
                        "📉 最大下落幅",
                        f"{max_drawdown:.2f}%"
                    )
                with col2:
                    # 総リターン - プラスは緑、マイナスは赤に
                    st.metric(
                        "📈 総リターン",
                        f"{total_return_pct:.2f}%",
                        delta=None,
                        delta_color="normal" if total_return_pct >= 0 else "inverse"
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
                
                # 動的重み付けの場合、追加情報を表示
                adaptive_info = StateManager.get_adaptive_info()
                if adaptive_info:
                    st.markdown("#### 🎯 動的重み付け分析補足")
                    st.info(f"""
                    **検出パターン:** {adaptive_info['pattern_name']}  
                    **信頼度:** {adaptive_info['confidence'] * 100:.1f}%  
                    **リスクレベル:** {adaptive_info['risk_level']}
                    
                    このパターンに最適化された重み付けで分析を行いました。
                    """)
                
                # 結果の見方説明
                UIComponents.render_tip_box(
                    "🤔 結果の見方",
                    "💵 **仮想最終資産：** 最初の資金がいくらになったか<br>" +
                    "📈 **総リターン：** 何%増えた（減った）か<br>" +
                    "📉 **最大下落幅：** 一番調子が悪い時にどのくらい減ったか<br>" +
                    "⚡ **シャープレシオ：** リスクを考慮した成績（1.0以上なら良好）"
                )
                
                # 取引詳細情報
                if trade_log is not None and not trade_log.empty:
                    try:
                        completed_trades = trade_log[trade_log['Type'] == 'Sell']
                        if not completed_trades.empty:
                            st.markdown("#### 📊 取引統計")
                            
                            col1, col2, col3 = st.columns(3)
                            
                            # 取引回数
                            total_trades = len(completed_trades)
                            winning_trades = completed_trades[completed_trades['PnL'] > 0]
                            win_rate = len(winning_trades) / total_trades * 100 if total_trades > 0 else 0
                            
                            with col1:
                                st.metric("取引回数", f"{total_trades}回")
                            with col2:
                                st.metric("勝率", f"{win_rate:.1f}%")
                            with col3:
                                if len(winning_trades) > 0:
                                    avg_win = winning_trades['PnL'].mean()
                                    st.metric("平均利益", f"¥{avg_win:,.0f}")
                                else:
                                    st.metric("平均利益", "¥0")
                            
                            # 損益分布
                            if total_trades > 0:
                                st.markdown("#### 💹 取引詳細")
                                
                                # 利益確定・損切り回数
                                if 'Exit_Reason' in completed_trades.columns:
                                    exit_reasons = completed_trades['Exit_Reason'].value_counts()
                                    
                                    col1, col2, col3 = st.columns(3)
                                    with col1:
                                        take_profit_count = exit_reasons.get('Take Profit', 0)
                                        st.metric("利益確定", f"{take_profit_count}回")
                                    with col2:
                                        stop_loss_count = exit_reasons.get('Stop Loss', 0)
                                        st.metric("損切り", f"{stop_loss_count}回")
                                    with col3:
                                        signal_sell_count = exit_reasons.get('Sell Signal', 0)
                                        st.metric("シグナル売り", f"{signal_sell_count}回")
                    except Exception as e:
                        st.warning(f"取引統計の表示中にエラーが発生しました: {e}")
                        st.info("取引ログのデータ形式に問題がある可能性があります")
                
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
        """企業情報を表示（変更なし）"""
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
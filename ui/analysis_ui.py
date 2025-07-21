# ui/analysis_ui.py
"""
分析結果表示UI（動的重み付け対応）
"""

import streamlit as st
from typing import Dict, Any
import pandas as pd

from config.settings import DISCLAIMERS, RISK_LEVELS, DYNAMIC_WEIGHT_PROFILES
from ui.components import UIComponents
from ui.charts import ChartGenerator
from core.state_manager import StateManager


class AnalysisUI:
    """分析結果表示UI管理クラス（動的重み付け対応）"""
    
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
        st.markdown("### 🎯 相場パターン分析結果")
        
        UIComponents.render_explanation_box(
            "パターン検出",
            "現在の相場パターンを自動検出し、最適な分析手法を適用しました。<br>" +
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
            pattern_type = adaptive_info['detected_pattern']
            
            # より詳しい説明
            UIComponents.render_explanation_box(
                "📊 重み付けシステムの仕組み",
                "相場パターンを分析し、各テクニカル指標の重要度を自動調整しました。<br>" +
                "💡 <strong>例：上昇トレンドの場合</strong><br>" +
                "　→ 移動平均（トレンド確認）とMACD（勢い判定）の重みを高く設定<br>" +
                "　→ RSI（買われすぎ判定）の重みを低く設定<br><br>" +
                "🎯 <strong>最終判断の計算方法：</strong><br>" +
                "　各指標のシグナル × 重み付け = 総合スコア<br>" +
                "　複数指標の加重平均で「買い」「売り」「様子見」を決定"
            )
            
            # 重み付けの可視化
            col1, col2 = st.columns([1.2, 0.8])
            
            with col1:
                st.markdown("**📈 重み配分の詳細**")
                
                # 重み付けグラフの表示
                weights_df = pd.DataFrame([
                    {'指標': '移動平均', '重み': weights.get('ma_trend', 0)},
                    {'指標': 'RSI', '重み': weights.get('rsi', 0)},
                    {'指標': 'ボリンジャー', '重み': weights.get('bollinger', 0)},
                    {'指標': 'MACD', '重み': weights.get('macd', 0)},
                    {'指標': '出来高', '重み': weights.get('volume', 0)}
                ])
                
                st.bar_chart(weights_df.set_index('指標'))
                
                for index, row in weights_df.iterrows():
                    indicator = row['指標']
                    weight = row['重み']
                    percentage = weight * 100
                    st.markdown(f"- **{indicator}**: {percentage:.1f}%")
            
            with col2:
                # パターン固有の重み付け説明
                pattern_profile = DYNAMIC_WEIGHT_PROFILES.get(pattern_type, {})
                
                if pattern_profile:
                    st.markdown(f"**検出パターン:** {pattern_profile.get('name', pattern_type)}")
                    st.markdown(f"**パターン説明:** {pattern_profile.get('description', '')}")
                    
                    # 重み付けの理由説明
                    weight_reasons = self._get_weight_reasoning(pattern_type, weights)
                    
                    st.markdown("**具体的な根拠:**")
                    for reason in weight_reasons:
                        st.markdown(f"• {reason}")
                        
                    # パターン別の戦略説明
                    strategy_hint = pattern_profile.get('strategy_hint', '')
                    if strategy_hint:
                        st.markdown(f"**📝 推奨戦略:** {strategy_hint}")
                else:
                    # デバッグ情報
                    st.warning(f"パターン情報が見つかりません: {pattern_type}")
                    st.markdown("**検出されたパターンタイプ:**")
                    st.code(pattern_type)
                    
                    # フォールバック説明
                    weight_reasons = self._get_fallback_reasoning(weights)
                    st.markdown("**一般的な重み付け根拠:**")
                    for reason in weight_reasons:
                        st.markdown(f"• {reason}")

    def _get_weight_reasoning(self, pattern_type: str, weights: Dict[str, float]) -> list:
        """重み付けの理由を説明"""
        reasons = []
        
        # パターンタイプの正規化（デバッグ用）
        pattern_type_lower = pattern_type.lower()
        
        # より詳細な条件分岐
        if 'uptrend' in pattern_type_lower or 'up' in pattern_type_lower:
            if weights.get('ma_trend', 0) > 0.25:
                reasons.append("📈 移動平均重視: 上昇トレンドの継続性を確認するため")
            if weights.get('macd', 0) > 0.25:
                reasons.append("⚡ MACD重視: 上昇の勢いと持続性を判定するため")
            if weights.get('bollinger', 0) < 0.2:
                reasons.append("📊 ボリンジャーバンド軽視: トレンド相場では範囲判定の重要度低下")
                
        elif 'downtrend' in pattern_type_lower or 'down' in pattern_type_lower:
            if weights.get('ma_trend', 0) > 0.25:
                reasons.append("📈 移動平均重視: 下降トレンドの確認のため")
            if weights.get('rsi', 0) > 0.2:
                reasons.append("🌡️ RSI重視: 売られすぎからの反転ポイント特定のため")
            if weights.get('macd', 0) > 0.2:
                reasons.append("⚡ MACD重視: 下降の勢い減衰を早期検出するため")
                
        elif 'range' in pattern_type_lower or 'sideways' in pattern_type_lower:
            if weights.get('rsi', 0) > 0.3:
                reasons.append("🌡️ RSI最重視: レンジ内での反転ポイント特定が最重要")
            if weights.get('bollinger', 0) > 0.3:
                reasons.append("📊 ボリンジャーバンド重視: レンジ相場では上下限が有効")
        
        # 一般的な重み付け説明
        high_concentration = max(weights.values()) > 0.4
        if high_concentration:
            reasons.append("🔴 特定指標に重点: 現在の相場で最も有効な指標を重視")
        else:
            reasons.append("🟢 分散型配分: 複数指標をバランスよく活用")
        
        return reasons
    
    def _get_fallback_reasoning(self, weights: Dict[str, float]) -> list:
        """フォールバック重み付け説明"""
        reasons = []
        
        # 各指標の重みに基づく説明
        if weights.get('ma_trend', 0) > 0.3:
            reasons.append("📈 移動平均中心: トレンド方向の確認を重視")
        if weights.get('rsi', 0) > 0.3:
            reasons.append("🌡️ RSI中心: 買われすぎ・売られすぎの判定を重視")
        if weights.get('bollinger', 0) > 0.3:
            reasons.append("📊 ボリンジャーバンド中心: 価格の相対的位置を重視")
        if weights.get('macd', 0) > 0.3:
            reasons.append("⚡ MACD中心: トレンドの勢いと転換点を重視")
        if weights.get('volume', 0) > 0.2:
            reasons.append("📊 出来高重視: 価格変動の信頼性を確認")
        
        return reasons
    
    def _render_pattern_analysis_details(self, adaptive_info: Dict[str, Any]):
        """パターン分析詳細を表示（投資判断への示唆付き）"""
        with st.expander("🔍 パターン分析詳細", expanded=False):
            analysis_details = adaptive_info.get('analysis_details', {})
            pattern_scores = adaptive_info.get('pattern_scores', {})
            
            # 分析結果の要約説明
            UIComponents.render_explanation_box(
                "分析の詳細解説",
                "以下は相場パターン検出した詳細分析です。<br>" +
                "各要素の数値と、それが投資判断にどう影響するかを解説します。"
            )
            
            if analysis_details:
                st.markdown("#### 📊 各要素の分析結果と投資への示唆")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # トレンド分析と解釈
                    trend = analysis_details.get('trend', {})
                    if trend:
                        direction = trend.get('direction', 'N/A')
                        strength = trend.get('strength', 0)
                        confidence = trend.get('confidence', 0)
                        
                        direction_icon = "⬆️" if direction == 'up' else "⬇️" if direction == 'down' else "➡️"
                        
                        st.markdown("**📈 トレンド分析**")
                        st.markdown(f"- 方向: {direction_icon} {direction}")
                        st.markdown(f"- 強度: {strength}")
                        st.markdown(f"- 信頼度: {confidence:.1%}")
                        
                        # トレンド分析の解釈
                        trend_interpretation = self._interpret_trend_analysis(direction, strength, confidence)
                        st.markdown(f"💡 **意味:** {trend_interpretation}")
                    
                    # ボラティリティ分析と解釈
                    volatility = analysis_details.get('volatility', {})
                    if volatility:
                        state = volatility.get('state', 'N/A')
                        vol_confidence = volatility.get('confidence', 0)
                        
                        state_icon = "📈" if state == 'expanding' else "📉" if state == 'contracting' else "➡️"
                        
                        st.markdown("**📊 ボラティリティ分析**")
                        st.markdown(f"- 状態: {state_icon} {state}")
                        st.markdown(f"- 信頼度: {vol_confidence:.1%}")
                
                with col2:
                    # パターンスコア詳細
                    if pattern_scores:
                        st.markdown("**🎯 各パターンの該当度**")
                        for pattern, score in pattern_scores.items():
                            pattern_info = DYNAMIC_WEIGHT_PROFILES.get(pattern, {})
                            pattern_name = pattern_info.get('name', pattern)
                            
                            # スコアを視覚化
                            score_percentage = score * 100
                            if score > 0.7:
                                score_color = "🟢"
                            elif score > 0.4:
                                score_color = "🟡"
                            else:
                                score_color = "🔴"
                            
                            st.markdown(f"- **{pattern_name}**: {score_color} {score_percentage:.1f}%")
                            
                            # パターン別の戦略的含意
                            strategy_implication = self._get_pattern_strategy_implication(pattern, score, pattern_info)
                            st.markdown(f"  {strategy_implication}")
    
    def _interpret_trend_analysis(self, direction: str, strength: float, confidence: float) -> str:
        """トレンド分析の解釈"""
        if direction == 'up':
            if strength > 0.7 and confidence > 0.8:
                return "強い上昇トレンド。継続の可能性が高い"
            elif strength > 0.5:
                return "上昇トレンド。ただし勢いに注意"
            else:
                return "弱い上昇。転換点の可能性"
        elif direction == 'down':
            if strength > 0.7 and confidence > 0.8:
                return "強い下降トレンド。反転のタイミングを待つ"
            elif strength > 0.5:
                return "下降トレンド。底値圏の接近に注意"
            else:
                return "弱い下降。反転の可能性"
        else:
            return "横ばい。ブレイクアウト方向を注視"
    
    def _get_pattern_strategy_implication(self, pattern: str, score: float, pattern_info: Dict[str, Any]) -> str:
        """パターン別の戦略的含意を取得"""
        if score < 0.3:
            return "該当度が低いため、このパターンの戦略は適用しない。"
        
        base_strategy = pattern_info.get('strategy_hint', '')
        risk_level = pattern_info.get('risk_level', 'medium')
        
        # スコアに基づく信頼度調整
        if score > 0.7:
            confidence_prefix = "高い信頼度で"
        elif score > 0.5:
            confidence_prefix = "中程度の信頼度で"
        else:
            confidence_prefix = "低い信頼度で"
        
        # リスクレベルに基づく注意喚起
        risk_warnings = {
            'low': "リスクは比較的低め。",
            'medium': "標準的なリスク管理を適用。",
            'high': "⚠️ 高リスク：慎重な判断と厳格なリスク管理が必要。"
        }
        
        risk_warning = risk_warnings.get(risk_level, "リスク管理を徹底。")
        
        return f"{confidence_prefix}{base_strategy} {risk_warning}"
    
    def _render_key_metrics(self, analysis_data: Dict[str, Any]):
        """主要指標を表示"""
        df = analysis_data['df']
        info = analysis_data['info']
        summary = analysis_data['summary']
        
        UIComponents.render_metrics(summary['current_price'], info, df)
    
    def _render_signal_analysis(self, analysis_data: Dict[str, Any]):
        """シグナル分析を表示（動的重み付け対応）"""
        signals = analysis_data['signals']
        signal_summary = analysis_data['signal_summary']
        
        st.markdown("### 🚦 シグナル分析")
        
        # シグナルサマリーの表示
        UIComponents.render_signal_summary(signal_summary)
        
        # 詳細シグナル情報の表示
        if st.checkbox("📊 詳細シグナル情報を表示", key="show_detailed_signals"):
            st.dataframe(signals.tail(10), use_container_width=True)
    
    def _render_charts(self, analysis_data: Dict[str, Any]):
        """チャート表示"""
        st.markdown("### 📈 チャート分析")
        
        df = analysis_data['df']
        signals = analysis_data['signals']
        
        # メインチャート
        main_chart = self.chart_generator.create_main_chart(df, signals)
        if main_chart:
            st.plotly_chart(main_chart, use_container_width=True)
        
        # テクニカル指標チャート
        tech_chart = self.chart_generator.create_technical_chart(df)
        if tech_chart:
            st.plotly_chart(tech_chart, use_container_width=True)
    
    def _render_backtest_results(self, analysis_data: Dict[str, Any]):
        """バックテスト結果表示"""
        backtest_data = analysis_data.get('backtest')
        if not backtest_data:
            return
        
        st.markdown("### 📊 バックテスト結果")
        
        portfolio_df = backtest_data['portfolio_df']
        trade_log = backtest_data['trade_log']
        performance = backtest_data['performance']
        
        # パフォーマンスサマリー
        UIComponents.render_backtest_performance(performance)
        
        # 詳細結果の表示
        if st.checkbox("📈 詳細バックテスト結果を表示", key="show_detailed_backtest"):
            
            # ポートフォリオ推移チャート
            if not portfolio_df.empty:
                portfolio_chart = self.chart_generator.create_portfolio_chart(portfolio_df)
                if portfolio_chart:
                    st.plotly_chart(portfolio_chart, use_container_width=True)
            
            # 取引履歴
            if not trade_log.empty:
                st.markdown("#### 📝 取引履歴")
                st.dataframe(trade_log, use_container_width=True)
    
    def _render_company_info(self, analysis_data: Dict[str, Any]):
        """企業情報表示"""
        info = analysis_data.get('info')
        if not info:
            return
        
        st.markdown("### 🏢 企業情報")
        UIComponents.render_company_info(info)

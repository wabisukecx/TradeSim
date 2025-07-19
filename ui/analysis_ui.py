# ui/analysis_ui.py - メトリクス色分け修正版・重み付け表示改善版
"""
分析結果表示UI（動的重み付け対応・メトリクス色分け修正版・重み付け表示改善版）
"""

import streamlit as st
from typing import Dict, Any
import pandas as pd

from config.settings import DISCLAIMERS, RISK_LEVELS, DYNAMIC_WEIGHT_PROFILES
from ui.components import UIComponents
from ui.charts import ChartGenerator
from core.state_manager import StateManager


class AnalysisUI:
    """分析結果表示UI管理クラス（動的重み付け対応・メトリクス色分け修正版・重み付け表示改善版）"""
    
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
        """重み付け詳細を表示（改善版）"""
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
                
                indicator_names = {
                    'ma_trend': '📈 移動平均（トレンド方向）',
                    'rsi': '🌡️ RSI（買われすぎ・売られすぎ）',
                    'bollinger': '📊 ボリンジャーバンド（価格位置）',
                    'macd': '⚡ MACD（勢いの変化）',
                    'volume': '📦 出来高（取引の活発さ）'
                }
                
                # 重みを降順でソート
                sorted_weights = sorted(weights.items(), key=lambda x: x[1], reverse=True)
                
                for indicator, weight in sorted_weights:
                    name = indicator_names.get(indicator, indicator)
                    percentage = weight * 100
                    
                    # 重要度に応じた色分け
                    if percentage >= 30:
                        importance = "🔴 最重要"
                        bar_color = "#FF5722"
                    elif percentage >= 20:
                        importance = "🟡 重要"
                        bar_color = "#FF9800"
                    elif percentage >= 10:
                        importance = "🟢 標準"
                        bar_color = "#4CAF50"
                    else:
                        importance = "⚪ 軽微"
                        bar_color = "#9E9E9E"
                    
                    st.markdown(f"""
                    <div style="margin: 0.8rem 0; padding: 0.5rem; background: #f8f9fa; border-radius: 0.5rem;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.3rem;">
                            <strong>{name}</strong>
                            <span style="color: {bar_color}; font-weight: bold;">{importance}</span>
                        </div>
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.3rem;">
                            <span style="font-size: 1.2rem; font-weight: bold;">{percentage:.1f}%</span>
                        </div>
                        <div style="background: #e0e0e0; border-radius: 0.5rem; height: 0.8rem; overflow: hidden;">
                            <div style="
                                background: {bar_color}; 
                                width: {percentage}%; 
                                height: 100%;
                                transition: width 0.5s ease;
                            "></div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("**💡 重み付けの根拠**")
                
                # パターン情報の表示
                pattern_profile = DYNAMIC_WEIGHT_PROFILES.get(pattern_type, {})
                
                if pattern_profile:
                    st.markdown(f"**検出パターン:** {pattern_profile.get('name', pattern_type)}")
                    st.markdown(f"**パターン説明:** {pattern_profile.get('description', '')}")
                    
                    # 重み付けの理由説明（修正版）
                    weight_reasons = self._get_weight_reasoning_improved(pattern_type, weights)
                    
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

    def _get_weight_reasoning_improved(self, pattern_type: str, weights: Dict[str, float]) -> list:
        """重み付けの理由を説明（改善版）"""
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
                reasons.append("📊 ボリンジャーバンド最重視: レンジの上下限判定のため")
            if weights.get('ma_trend', 0) < 0.2:
                reasons.append("📈 移動平均軽視: 明確なトレンドがないため重要度低下")
                
        elif 'transition' in pattern_type_lower or 'change' in pattern_type_lower:
            if weights.get('macd', 0) > 0.4:
                reasons.append("⚡ MACD最重視: トレンド転換の早期検出が最優先")
            if weights.get('rsi', 0) > 0.2:
                reasons.append("🌡️ RSI重視: 転換点での過熱感の確認のため")
                
        elif 'volatile' in pattern_type_lower or 'acceleration' in pattern_type_lower:
            if weights.get('volume', 0) > 0.2:
                reasons.append("📦 出来高重視: 急激な変動の真正性確認のため")
            if weights.get('macd', 0) > 0.3:
                reasons.append("⚡ MACD重視: 加速度の変化を捉えるため")
            if weights.get('bollinger', 0) > 0.2:
                reasons.append("📊 ボリンジャーバンド重視: 異常値の判定のため")
        
        # 追加の一般的な説明
        max_weight_indicator = max(weights.items(), key=lambda x: x[1])[0]
        max_weight_value = weights[max_weight_indicator]
        
        indicator_purposes = {
            'ma_trend': '価格の大局的な方向性判定',
            'rsi': '買われすぎ・売られすぎの状況判定',
            'bollinger': '価格の相対的な高低判定',
            'macd': '価格変動の勢いと方向変化の検出',
            'volume': '価格変動の信頼性確認'
        }
        
        if max_weight_value > 0.3:
            purpose = indicator_purposes.get(max_weight_indicator, '総合判定')
            reasons.append(f"🎯 最重要指標選定: {purpose}が現在の相場で最も重要と判定")
        
        # 理由が見つからない場合のフォールバック
        if not reasons:
            reasons = self._get_fallback_reasoning(weights)
        
        return reasons

    def _get_fallback_reasoning(self, weights: Dict[str, float]) -> list:
        """フォールバック用の重み付け説明"""
        reasons = []
        
        # 最も重い指標を特定
        sorted_weights = sorted(weights.items(), key=lambda x: x[1], reverse=True)
        
        for i, (indicator, weight) in enumerate(sorted_weights[:3]):
            if weight > 0.25:
                if indicator == 'ma_trend':
                    reasons.append("📈 移動平均を重視: 基本的なトレンド判定のため")
                elif indicator == 'macd':
                    reasons.append("⚡ MACDを重視: 価格変動の勢いを重要視")
                elif indicator == 'rsi':
                    reasons.append("🌡️ RSIを重視: 相場の過熱感を重要視")
                elif indicator == 'bollinger':
                    reasons.append("📊 ボリンジャーバンドを重視: 価格の相対位置を重要視")
                elif indicator == 'volume':
                    reasons.append("📦 出来高を重視: 取引の信頼性を重要視")
        
        if not reasons:
            reasons.append("⚖️ バランス型の重み付けを適用")
        
        # 重み配分の特徴説明
        high_concentration = max(weights.values()) > 0.4
        if high_concentration:
            reasons.append("🔴 特定指標に重点: 現在の相場で最も有効な指標を重視")
        else:
            reasons.append("🟢 分散型配分: 複数指標をバランスよく活用")
        
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
                        
                        # ボラティリティ分析の解釈
                        vol_interpretation = self._interpret_volatility_analysis(state, vol_confidence)
                        st.markdown(f"💡 **意味:** {vol_interpretation}")
                
                with col2:
                    # モメンタム分析と解釈
                    momentum = analysis_details.get('momentum', {})
                    if momentum:
                        direction = momentum.get('direction', 'N/A')
                        strength = momentum.get('strength', 0)
                        mom_confidence = momentum.get('confidence', 0)
                        
                        direction_icon = "🚀" if 'bullish' in direction else "🔻" if 'bearish' in direction else "⚪"
                        
                        st.markdown("**⚡ モメンタム分析**")
                        st.markdown(f"- 方向: {direction_icon} {direction}")
                        st.markdown(f"- 強度: {strength:.2f}")
                        st.markdown(f"- 信頼度: {mom_confidence:.1%}")
                        
                        # モメンタム分析の解釈
                        momentum_interpretation = self._interpret_momentum_analysis(direction, strength, mom_confidence)
                        st.markdown(f"💡 **意味:** {momentum_interpretation}")
                    
                    # 出来高分析と解釈
                    volume = analysis_details.get('volume', {})
                    if volume:
                        vol_trend = volume.get('trend', 'N/A')
                        confirmation = volume.get('confirmation', False)
                        
                        trend_icon = "📈" if vol_trend == 'increasing' else "📉"
                        confirm_icon = "✅" if confirmation else "❌"
                        
                        st.markdown("**📦 出来高分析**")
                        st.markdown(f"- トレンド: {trend_icon} {vol_trend}")
                        st.markdown(f"- 確認: {confirm_icon} {confirmation}")
                        
                        # 出来高分析の解釈
                        volume_interpretation = self._interpret_volume_analysis(vol_trend, confirmation)
                        st.markdown(f"💡 **意味:** {volume_interpretation}")
                
                # 総合的な投資判断への示唆
                st.markdown("---")
                st.markdown("#### 🎯 総合的な投資判断への示唆")
                
                overall_interpretation = self._generate_overall_interpretation(analysis_details)
                UIComponents.render_tip_box(
                    "📋 統合分析結果",
                    overall_interpretation
                )
            
            # パターンスコアと戦略的含意
            if pattern_scores:
                st.markdown("#### 🎯 パターン別スコアと戦略的含意")
                
                UIComponents.render_explanation_box(
                    "📈 パターンスコアの見方",
                    "各相場パターンの適合度を0-100%で表示します。<br>" +
                    "高スコアのパターンほど現在の相場状況に適合しており、<br>" +
                    "そのパターン向けの戦略が有効である可能性が高いです。"
                )
                
                # スコアを降順でソート
                sorted_scores = sorted(pattern_scores.items(), key=lambda x: x[1], reverse=True)
                
                # 上位3パターンのみ詳細表示
                for i, (pattern, score) in enumerate(sorted_scores[:3]):
                    pattern_info = DYNAMIC_WEIGHT_PROFILES.get(pattern, {})
                    pattern_name = pattern_info.get('name', pattern)
                    
                    # ランキング表示
                    rank_emoji = "🥇" if i == 0 else "🥈" if i == 1 else "🥉"
                    
                    # プログレスバー
                    progress_width = int(score * 100)
                    if score > 0.7:
                        color = "#4CAF50"
                        confidence_level = "高信頼度"
                    elif score > 0.5:
                        color = "#FF9800"
                        confidence_level = "中信頼度"
                    elif score > 0.3:
                        color = "#FFC107"
                        confidence_level = "低信頼度"
                    else:
                        color = "#F44336"
                        confidence_level = "該当なし"
                    
                    st.markdown(f"""
                    <div style="margin: 1rem 0; padding: 1rem; background: #f8f9fa; border-radius: 0.5rem; border-left: 4px solid {color};">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                            <span style="font-size: 1.1rem; font-weight: bold;">{rank_emoji} {pattern_name}</span>
                            <span style="color: {color}; font-weight: bold; font-size: 1.1rem;">{score:.1%} ({confidence_level})</span>
                        </div>
                        <div style="background: #e0e0e0; border-radius: 0.5rem; height: 0.8rem; margin-bottom: 0.5rem;">
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
                    
                    # パターン別の戦略的含意
                    strategy_implication = self._get_pattern_strategy_implication(pattern, score, pattern_info)
                    if strategy_implication:
                        st.markdown(f"**💡 {pattern_name}の場合の戦略:** {strategy_implication}")
                        st.markdown("---")
                
                # 残りのパターンは簡略表示
                if len(sorted_scores) > 3:
                    st.markdown("**📊 その他のパターンスコア**")
                    with st.container():
                        st.markdown(
                            '<div style="background: #f0f2f6; padding: 1rem; border-radius: 0.5rem; margin: 0.5rem 0;">',
                            unsafe_allow_html=True
                        )
                        for pattern, score in sorted_scores[3:]:
                            pattern_info = DYNAMIC_WEIGHT_PROFILES.get(pattern, {})
                            pattern_name = pattern_info.get('name', pattern)
                            
                            # スコアに応じた色分け
                            if score > 0.3:
                                score_color = "#FF9800"
                                score_icon = "🟡"
                            elif score > 0.1:
                                score_color = "#9E9E9E"
                                score_icon = "⚪"
                            else:
                                score_color = "#F44336"
                                score_icon = "🔴"
                            
                            st.markdown(f"""
                            <div style="display: flex; justify-content: space-between; padding: 0.2rem 0;">
                                <span>{score_icon} <strong>{pattern_name}</strong></span>
                                <span style="color: {score_color}; font-weight: bold;">{score:.1%}</span>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        st.markdown('</div>', unsafe_allow_html=True)

    def _interpret_trend_analysis(self, direction: str, strength: float, confidence: float) -> str:
        """トレンド分析の解釈"""
        if confidence < 0.1:
            return "⚠️ トレンドが不明確で判断困難。様子見が賢明。"
        elif direction == 'up':
            if strength > 0.7:
                return "🚀 強い上昇トレンド。追い風に乗るチャンス。"
            else:
                return "📈 緩やかな上昇傾向。慎重に押し目を狙う。"
        elif direction == 'down':
            if strength > 0.7:
                return "⬇️ 強い下降トレンド。反転まで待つか空売り検討。"
            else:
                return "📉 緩やかな下降傾向。底値圏での反転を注視。"
        else:
            return "➡️ 方向感なし。レンジ取引やブレイクアウト待ち。"

    def _interpret_volatility_analysis(self, state: str, confidence: float) -> str:
        """ボラティリティ分析の解釈"""
        if confidence < 0.3:
            return "❓ ボラティリティの変化が不明確。"
        elif state == 'expanding':
            return "⚡ 値動きが激しくなっている。大きな変化の前兆かリスク上昇。"
        elif state == 'contracting':
            return "🎯 値動きが収束中。大きな動きが近づいている可能性。"
        else:
            return "📊 ボラティリティは安定的。"

    def _interpret_momentum_analysis(self, direction: str, strength: float, confidence: float) -> str:
        """モメンタム分析の解釈"""
        if confidence < 0.5:
            return "❓ 勢いの方向が不明確。"
        elif 'bullish' in direction:
            if strength > 0.8:
                return "🚀 強い買い勢い。上昇の可能性が高い。"
            else:
                return "📈 買い勢いあり。継続性を確認したい。"
        elif 'bearish' in direction:
            if strength > 0.8:
                return "🔻 強い売り勢い。下落圧力が強い。"
            else:
                return "📉 売り勢いあり。反転の兆候を注視。"
        else:
            return "⚪ 勢い中立。どちらに動くか不明。"

    def _interpret_volume_analysis(self, trend: str, confirmation: bool) -> str:
        """出来高分析の解釈"""
        if trend == 'increasing' and confirmation:
            return "✅ 出来高増加で価格変動を後押し。トレンドの信頼性高い。"
        elif trend == 'increasing' and not confirmation:
            return "⚠️ 出来高増加だが価格との整合性に疑問。要注意。"
        elif trend == 'decreasing':
            return "📉 出来高減少。価格変動の信頼性が低下。トレンド継続に疑問。"
        else:
            return "➡️ 出来高に大きな変化なし。"

    def _generate_overall_interpretation(self, analysis_details: Dict[str, Any]) -> str:
        """総合的な解釈を生成"""
        trend = analysis_details.get('trend', {})
        volatility = analysis_details.get('volatility', {})
        momentum = analysis_details.get('momentum', {})
        volume = analysis_details.get('volume', {})
        
        # 主要な要素を抽出
        trend_direction = trend.get('direction', 'neutral')
        trend_confidence = trend.get('confidence', 0)
        vol_state = volatility.get('state', 'normal')
        momentum_direction = momentum.get('direction', 'neutral')
        momentum_confidence = momentum.get('confidence', 0)
        volume_confirmation = volume.get('confirmation', False)
        
        interpretations = []
        
        # トレンドとモメンタムの組み合わせ分析
        if trend_confidence > 0.5 and momentum_confidence > 0.5:
            if 'up' in trend_direction and 'bullish' in momentum_direction:
                interpretations.append("🚀 **強気シナリオ**: トレンドとモメンタムが上向きで一致")
            elif 'down' in trend_direction and 'bearish' in momentum_direction:
                interpretations.append("🔻 **弱気シナリオ**: トレンドとモメンタムが下向きで一致")
            else:
                interpretations.append("⚠️ **注意**: トレンドとモメンタムに矛盾。転換点の可能性")
        
        # ボラティリティからの示唆
        if vol_state == 'contracting':
            interpretations.append("🎯 **ブレイクアウト待ち**: 値動きが収束中。大きな動きが近い可能性")
        elif vol_state == 'expanding':
            interpretations.append("⚡ **高リスク期間**: 値動きが激化。慎重な判断が必要")
        
        # 出来高からの示唆
        if not volume_confirmation:
            interpretations.append("📉 **出来高不足**: 価格変動の信頼性に疑問。トレンドの持続性に注意")
        else:
            interpretations.append("✅ **出来高確認**: 価格変動が出来高に支えられており信頼性高い")
        
        # 投資行動への具体的提案
        if len(interpretations) == 0:
            interpretations.append("❓ **判断困難**: 複数の指標が混在。追加情報の収集を推奨")
        
        # リスク管理の提案
        risk_suggestions = []
        if vol_state == 'expanding':
            risk_suggestions.append("• ポジションサイズを通常より小さくする")
        if not volume_confirmation:
            risk_suggestions.append("• 利益確定と損切りラインを通常より狭く設定")
        if trend_confidence < 0.3:
            risk_suggestions.append("• 短期的な視点での判断を心がける")
        
        result = "<br>".join(interpretations)
        if risk_suggestions:
            result += "<br><br>🛡️ **リスク管理提案:**<br>" + "<br>".join(risk_suggestions)
        
        result += "<br><br>⚠️ **注意**: これらは分析結果であり、投資を保証するものではありません。"
        
        return result

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
            f"使用した分析手法: {weight_mode_names.get(weight_mode, '固定重み付け')} <br>" +
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
            
            🎯 検出パターン: {pattern_info['pattern_name']}  
            📊 信頼度: {pattern_info['confidence'] * 100:.1f}%  
            💡 戦略ヒント: {pattern_info['strategy_hint']}
            """
        
        if signal == 1:
            st.info(f"""
            ### 🟢 買いサインを検出
            スコア: {buy_score:.1f}点

            複数の指標が「買いサイン」を示しています。{adaptive_context}
            
            ⚠️ これは参考情報です。投資判断は自己責任でお願いします 🤔
            """)
        elif signal == -1:
            st.info(f"""
            ### 🔴 売りサインを検出  
            スコア: {sell_score:.1f}点

            複数の指標が「売りサイン」を示しています。{adaptive_context}
            
            ⚠️ これは参考情報です。実際の取引は慎重にご判断ください ⚠️
            """)
        else:
            st.info(f"""
            ### ⚪ 中立シグナル（様子見）
            買いスコア: {buy_score:.1f}点 | 売りスコア: {sell_score:.1f}点

            現在は明確なサインが出ていない状況です。{adaptive_context}
            
            ⚠️ 引き続き注視が必要です 👀
            """)
        
        # 判断根拠
        st.markdown("#### 📋 分析の根拠（詳しい理由）")
        
        # 重み付け情報の表示
        if signal_explanation.get('weights_breakdown'):
            UIComponents.render_explanation_box(
                "⚖️ 使用された重み付け",
                f"分析手法: {weight_mode_names.get(weight_mode)} <br>" +
                "各指標の重要度を調整して総合判断を行いました。"
            )
            
            # 重み付けの簡易表示
            weights = signal_explanation['weights_breakdown']
            weight_text = " | ".join([f"{k}: {v:.1%}" for k, v in weights.items()])
            st.code(weight_text)
        
        UIComponents.render_explanation_box(
            "🔍 分析の根拠",
            "以下の要素を総合的に分析しました：<br><br>" +
            "1. 📈 <strong>移動平均：</strong>株価のトレンド方向性<br>" +
            "　→ 短期線が長期線より上なら上昇トレンド、下なら下降トレンド<br>" +
            "　→ 現在の株価が平均より高いか低いかで勢いを判定<br><br>" +
            
            "2. 🌡️ <strong>RSI：</strong>買われすぎ・売られすぎの判定<br>" +
            "　→ 70%以上で買われすぎ（売り検討）、30%以下で売られすぎ（買い検討）<br>" +
            "　→ 株価の上昇・下降の勢いがどのくらい強いかを0-100%で表示<br><br>" +
            
            "3. 📊 <strong>ボリンジャーバンド：</strong>価格の正常範囲の判定<br>" +
            "　→ 上限を超えると割高、下限を下回ると割安の可能性<br>" +
            "　→ 過去の価格変動から「いつもの範囲」を計算して比較<br><br>" +
            
            "4. ⚡ <strong>MACD：</strong>買い・売りタイミングの変化<br>" +
            "　→ MACDラインがシグナルラインを上抜けで買い、下抜けで売りサイン<br>" +
            "　→ 株価の勢いが強くなっているか弱くなっているかを検出<br><br>" +
            
            "5. 📦 <strong>出来高：</strong>取引の勢いと信頼性<br>" +
            "　→ 出来高が多いとトレンドの信頼性が高い、少ないと不安定<br>" +
            "　→ たくさんの人が売買していると、その動きは本物の可能性が高い<br><br>" +
            
            "💡 <strong>総合判定：</strong>これら5つの指標が同じ方向を示すほど信頼性が高くなります"
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
                f"分析手法: {StateManager.get_weight_mode().upper()}モードを使用"
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
                        delta=f"¥{total_return_abs:,.0f}",  # ✅ 通貨記号付きで表示
                        delta_color="normal"  # 正の値=緑、負の値=赤
                    )
                    st.metric(
                        "📉 最大下落幅",
                        f"{max_drawdown:.2f}%"
                    )
                with col2:
                    # 総リターン - 適切なデルタ値を設定
                    st.metric(
                        "📈 総リターン",
                        f"{total_return_pct:.2f}%",
                        delta=f"{total_return_pct:+.2f}%",  # ✅ パーセント変化を表示
                        delta_color="normal"  # 正の値=緑、負の値=赤
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
                    検出パターン: {adaptive_info['pattern_name']}  
                    信頼度: {adaptive_info['confidence'] * 100:.1f}%  
                    リスクレベル: {adaptive_info['risk_level']}
                    
                    このパターンに最適化された重み付けで分析を行いました。
                    """)
                
                # 結果の見方説明
                UIComponents.render_tip_box(
                    "🤔 結果の見方",
                    "💵 仮想最終資産： 最初の資金がいくらになったか<br>" +
                    "📈 総リターン： 何%増えた（減った）か<br>" +
                    "📉 最大下落幅： 一番調子が悪い時にどのくらい減ったか<br>" +
                    "⚡ シャープレシオ： リスクを考慮した成績（1.0以上なら良好）"
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
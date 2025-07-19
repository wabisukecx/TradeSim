# core/state_manager.py - 動的重み付け状態管理対応版
"""
セッション状態管理（動的重み付け対応）
"""

import streamlit as st
from typing import Dict, Any, Optional, List
from datetime import datetime


class StateManager:
    """セッション状態管理クラス（動的重み付け対応）"""
    
    @staticmethod
    def initialize_session_state():
        """セッション状態を初期化"""
        # 既存の状態初期化
        if 'analysis_data' not in st.session_state:
            st.session_state.analysis_data = None
        
        if 'current_stock_code' not in st.session_state:
            st.session_state.current_stock_code = None
        
        if 'current_company_name' not in st.session_state:
            st.session_state.current_company_name = None
        
        # ポートフォリオ関連
        if 'portfolio' not in st.session_state:
            st.session_state.portfolio = {}
        
        if 'portfolio_history' not in st.session_state:
            st.session_state.portfolio_history = []
        
        # UI状態関連
        if 'auto_run_trigger' not in st.session_state:
            st.session_state.auto_run_trigger = False
        
        if 'last_direct_input' not in st.session_state:
            st.session_state.last_direct_input = ""
        
        if 'direct_input_symbol' not in st.session_state:
            st.session_state.direct_input_symbol = "AAPL"
        
        # 実行制御フラグ
        if 'is_running_analysis' not in st.session_state:
            st.session_state.is_running_analysis = False
        
        # 設定プリセット
        if 'preset_mode' not in st.session_state:
            st.session_state.preset_mode = "balanced"
        
        # 選択状態
        if 'selected_stock_name' not in st.session_state:
            st.session_state.selected_stock_name = None
        
        # === 動的重み付け関連の新規状態 ===
        
        # 重み付けモード
        if 'weight_mode' not in st.session_state:
            st.session_state.weight_mode = 'fixed'  # 'fixed', 'adaptive', 'manual'
        
        # 手動重み付け設定
        if 'manual_weights' not in st.session_state:
            st.session_state.manual_weights = {
                'ma_trend': 0.2,
                'rsi': 0.2,
                'bollinger': 0.3,
                'macd': 0.3,
                'volume': 0.1
            }
        
        # 動的重み付け履歴
        if 'adaptive_analysis_history' not in st.session_state:
            st.session_state.adaptive_analysis_history = []
        
        # パターン検出設定
        if 'pattern_detection_settings' not in st.session_state:
            st.session_state.pattern_detection_settings = {
                'enable_transition_smoothing': True,
                'confidence_threshold': 0.6,
                'pattern_stability_required': False
            }
        
        # 動的重み付け表示設定
        if 'adaptive_display_settings' not in st.session_state:
            st.session_state.adaptive_display_settings = {
                'show_pattern_confidence': True,
                'show_weight_breakdown': True,
                'show_strategy_hints': True,
                'show_risk_level': True,
                'show_pattern_history': False
            }
        
        # 最後に検出されたパターン情報
        if 'last_detected_pattern' not in st.session_state:
            st.session_state.last_detected_pattern = None
        
        # 重み付け学習設定（将来拡張用）
        if 'weight_learning_enabled' not in st.session_state:
            st.session_state.weight_learning_enabled = False
    
    @staticmethod
    def reset_application_state():
        """アプリケーション状態をリセット"""
        keys_to_reset = [
            'analysis_data', 'current_stock_code', 'current_company_name',
            'auto_run_trigger', 'last_direct_input', 'direct_input_symbol',
            'is_running_analysis', 'selected_stock_name',
            # 動的重み付け関連もリセット対象に追加
            'last_detected_pattern', 'adaptive_analysis_history'
        ]
        
        for key in keys_to_reset:
            if key in st.session_state:
                del st.session_state[key]
        
        # 初期値を再設定
        st.session_state.direct_input_symbol = "AAPL"
        st.session_state.auto_run_trigger = False
        st.session_state.is_running_analysis = False
        st.session_state.preset_mode = "balanced"
        
        # 動的重み付け設定は保持（ユーザー設定のため）
        # st.session_state.weight_mode はリセットしない
        # st.session_state.manual_weights はリセットしない
    
    @staticmethod
    def set_analysis_data(df, info, signals, portfolio, trade_log, parameters, 
                         summary, signal_explanation, stock_code, company_name,
                         adaptive_info: Optional[Dict[str, Any]] = None):
        """分析データを保存（動的重み付け情報追加・下位互換性保持）"""
        st.session_state.analysis_data = {
            'df': df,
            'info': info,
            'signals': signals,
            'portfolio': portfolio,
            'trade_log': trade_log,
            'parameters': parameters,
            'summary': summary,
            'signal_explanation': signal_explanation,
            'adaptive_info': adaptive_info  # 新規追加（省略可能）
        }
        st.session_state.current_stock_code = stock_code
        st.session_state.current_company_name = company_name
        
        # 動的重み付け履歴に追加
        if adaptive_info:
            StateManager._add_to_adaptive_history(adaptive_info, stock_code, company_name)
            st.session_state.last_detected_pattern = adaptive_info
    
    @staticmethod
    def _add_to_adaptive_history(adaptive_info: Dict[str, Any], stock_code: str, company_name: str):
        """動的重み付け履歴に追加"""
        history_entry = {
            'timestamp': datetime.now(),
            'stock_code': stock_code,
            'company_name': company_name,
            'detected_pattern': adaptive_info['detected_pattern'],
            'pattern_name': adaptive_info['pattern_name'],
            'confidence': adaptive_info['confidence'],
            'weights_used': adaptive_info['weights_used'],
            'risk_level': adaptive_info['risk_level']
        }
        
        st.session_state.adaptive_analysis_history.append(history_entry)
        
        # 履歴は最新50件まで保持
        if len(st.session_state.adaptive_analysis_history) > 50:
            st.session_state.adaptive_analysis_history = st.session_state.adaptive_analysis_history[-50:]
    
    @staticmethod
    def get_analysis_data() -> Optional[Dict[str, Any]]:
        """分析データを取得"""
        return st.session_state.get('analysis_data')
    
    @staticmethod
    def has_analysis_data() -> bool:
        """分析データが存在するかチェック"""
        return st.session_state.get('analysis_data') is not None
    
    @staticmethod
    def get_adaptive_info() -> Optional[Dict[str, Any]]:
        """動的重み付け情報を取得"""
        analysis_data = StateManager.get_analysis_data()
        if analysis_data:
            return analysis_data.get('adaptive_info')
        return None
    
    @staticmethod
    def has_adaptive_info() -> bool:
        """動的重み付け情報が存在するかチェック"""
        return StateManager.get_adaptive_info() is not None
    
    # === 重み付け設定関連 ===
    
    @staticmethod
    def set_weight_mode(mode: str):
        """重み付けモードを設定"""
        if mode in ['fixed', 'adaptive', 'manual']:
            st.session_state.weight_mode = mode
    
    @staticmethod
    def get_weight_mode() -> str:
        """重み付けモードを取得"""
        return st.session_state.get('weight_mode', 'fixed')
    
    @staticmethod
    def set_manual_weights(weights: Dict[str, float]):
        """手動重み付けを設定"""
        st.session_state.manual_weights = weights.copy()
    
    @staticmethod
    def get_manual_weights() -> Dict[str, float]:
        """手動重み付けを取得"""
        return st.session_state.get('manual_weights', {
            'ma_trend': 0.2,
            'rsi': 0.2,
            'bollinger': 0.3,
            'macd': 0.3,
            'volume': 0.1
        })
    
    @staticmethod
    def update_manual_weight(indicator: str, weight: float):
        """特定の指標の手動重み付けを更新"""
        if 'manual_weights' not in st.session_state:
            StateManager.initialize_session_state()
        
        st.session_state.manual_weights[indicator] = weight
        
        # 重みの正規化
        total = sum(st.session_state.manual_weights.values())
        if total > 0:
            for key in st.session_state.manual_weights:
                st.session_state.manual_weights[key] /= total
    
    # === パターン検出設定 ===
    
    @staticmethod
    def set_pattern_detection_setting(key: str, value: Any):
        """パターン検出設定を更新"""
        if 'pattern_detection_settings' not in st.session_state:
            StateManager.initialize_session_state()
        
        st.session_state.pattern_detection_settings[key] = value
    
    @staticmethod
    def get_pattern_detection_settings() -> Dict[str, Any]:
        """パターン検出設定を取得"""
        return st.session_state.get('pattern_detection_settings', {
            'enable_transition_smoothing': True,
            'confidence_threshold': 0.6,
            'pattern_stability_required': False
        })
    
    # === 表示設定 ===
    
    @staticmethod
    def set_adaptive_display_setting(key: str, value: bool):
        """動的重み付け表示設定を更新"""
        if 'adaptive_display_settings' not in st.session_state:
            StateManager.initialize_session_state()
        
        st.session_state.adaptive_display_settings[key] = value
    
    @staticmethod
    def get_adaptive_display_settings() -> Dict[str, bool]:
        """動的重み付け表示設定を取得"""
        return st.session_state.get('adaptive_display_settings', {
            'show_pattern_confidence': True,
            'show_weight_breakdown': True,
            'show_strategy_hints': True,
            'show_risk_level': True,
            'show_pattern_history': False
        })
    
    # === 履歴管理 ===
    
    @staticmethod
    def get_adaptive_analysis_history() -> List[Dict[str, Any]]:
        """動的重み付け分析履歴を取得"""
        return st.session_state.get('adaptive_analysis_history', [])
    
    @staticmethod
    def clear_adaptive_history():
        """動的重み付け履歴をクリア"""
        st.session_state.adaptive_analysis_history = []
    
    @staticmethod
    def get_last_detected_pattern() -> Optional[Dict[str, Any]]:
        """最後に検出されたパターンを取得"""
        return st.session_state.get('last_detected_pattern')
    
    @staticmethod
    def get_pattern_statistics() -> Dict[str, Any]:
        """パターン統計情報を取得"""
        history = StateManager.get_adaptive_analysis_history()
        
        if not history:
            return {}
        
        # パターン別の出現回数
        pattern_counts = {}
        confidence_sum = {}
        recent_patterns = []
        
        for entry in history:
            pattern = entry['detected_pattern']
            confidence = entry['confidence']
            
            pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1
            confidence_sum[pattern] = confidence_sum.get(pattern, 0) + confidence
            
            # 最新10件のパターン
            if len(recent_patterns) < 10:
                recent_patterns.append(pattern)
        
        # 平均信頼度
        avg_confidence = {}
        for pattern in pattern_counts:
            avg_confidence[pattern] = confidence_sum[pattern] / pattern_counts[pattern]
        
        return {
            'total_analyses': len(history),
            'pattern_counts': pattern_counts,
            'average_confidence': avg_confidence,
            'recent_patterns': recent_patterns,
            'most_common_pattern': max(pattern_counts.items(), key=lambda x: x[1])[0] if pattern_counts else None
        }
    
    # === 既存メソッド（変更なし） ===
    
    @staticmethod
    def set_running_state(is_running: bool):
        """実行状態を設定"""
        st.session_state.is_running_analysis = is_running
    
    @staticmethod
    def is_running() -> bool:
        """実行中かどうかを確認"""
        return st.session_state.get('is_running_analysis', False)
    
    @staticmethod
    def trigger_auto_run():
        """自動実行をトリガー"""
        st.session_state.auto_run_trigger = True
    
    @staticmethod
    def should_auto_run() -> bool:
        """自動実行すべきかどうか"""
        return st.session_state.get('auto_run_trigger', False)
    
    @staticmethod
    def clear_auto_run():
        """自動実行フラグをクリア"""
        st.session_state.auto_run_trigger = False
    
    @staticmethod
    def set_direct_input(symbol: str):
        """直接入力銘柄コードを設定"""
        st.session_state.direct_input_symbol = symbol
    
    @staticmethod
    def get_direct_input() -> str:
        """直接入力銘柄コードを取得"""
        return st.session_state.get('direct_input_symbol', "AAPL")
    
    @staticmethod
    def set_preset_mode(mode: str):
        """プリセットモードを設定"""
        st.session_state.preset_mode = mode
    
    @staticmethod
    def get_preset_mode() -> str:
        """プリセットモードを取得"""
        return st.session_state.get('preset_mode', "balanced")
    
    @staticmethod
    def get_current_stock_info() -> tuple:
        """現在の銘柄情報を取得"""
        return (
            st.session_state.get('current_stock_code'),
            st.session_state.get('current_company_name')
        )
    
    @staticmethod
    def debug_state():
        """デバッグ用：現在の状態を表示"""
        st.write("デバッグ情報:")
        debug_info = {
            'current_stock_code': st.session_state.get('current_stock_code'),
            'current_company_name': st.session_state.get('current_company_name'),
            'has_analysis_data': StateManager.has_analysis_data(),
            'has_adaptive_info': StateManager.has_adaptive_info(),
            'is_running': StateManager.is_running(),
            'auto_run_trigger': StateManager.should_auto_run(),
            'direct_input': StateManager.get_direct_input(),
            'preset_mode': StateManager.get_preset_mode(),
            'weight_mode': StateManager.get_weight_mode(),
            'manual_weights': StateManager.get_manual_weights(),
            'adaptive_history_count': len(StateManager.get_adaptive_analysis_history())
        }
        st.write(debug_info)
    
    @staticmethod
    def export_settings() -> Dict[str, Any]:
        """設定をエクスポート"""
        return {
            'weight_mode': StateManager.get_weight_mode(),
            'manual_weights': StateManager.get_manual_weights(),
            'pattern_detection_settings': StateManager.get_pattern_detection_settings(),
            'adaptive_display_settings': StateManager.get_adaptive_display_settings(),
            'preset_mode': StateManager.get_preset_mode()
        }
    
    @staticmethod
    def import_settings(settings: Dict[str, Any]):
        """設定をインポート"""
        if 'weight_mode' in settings:
            StateManager.set_weight_mode(settings['weight_mode'])
        
        if 'manual_weights' in settings:
            StateManager.set_manual_weights(settings['manual_weights'])
        
        if 'pattern_detection_settings' in settings:
            for key, value in settings['pattern_detection_settings'].items():
                StateManager.set_pattern_detection_setting(key, value)
        
        if 'adaptive_display_settings' in settings:
            for key, value in settings['adaptive_display_settings'].items():
                StateManager.set_adaptive_display_setting(key, value)
        
        if 'preset_mode' in settings:
            StateManager.set_preset_mode(settings['preset_mode'])
# core/state_manager.py
"""
セッション状態管理
"""

import streamlit as st
from typing import Dict, Any, Optional
from datetime import datetime


class StateManager:
    """セッション状態管理クラス"""
    
    @staticmethod
    def initialize_session_state():
        """セッション状態を初期化"""
        # 分析データ関連
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
    
    @staticmethod
    def reset_application_state():
        """アプリケーション状態をリセット"""
        keys_to_reset = [
            'analysis_data', 'current_stock_code', 'current_company_name',
            'auto_run_trigger', 'last_direct_input', 'direct_input_symbol',
            'is_running_analysis', 'selected_stock_name'
        ]
        
        for key in keys_to_reset:
            if key in st.session_state:
                del st.session_state[key]
        
        # 初期値を再設定
        st.session_state.direct_input_symbol = "AAPL"
        st.session_state.auto_run_trigger = False
        st.session_state.is_running_analysis = False
        st.session_state.preset_mode = "balanced"
    
    @staticmethod
    def set_analysis_data(df, info, signals, portfolio, trade_log, parameters, 
                         summary, signal_explanation, stock_code, company_name):
        """分析データを保存"""
        st.session_state.analysis_data = {
            'df': df,
            'info': info,
            'signals': signals,
            'portfolio': portfolio,
            'trade_log': trade_log,
            'parameters': parameters,
            'summary': summary,
            'signal_explanation': signal_explanation
        }
        st.session_state.current_stock_code = stock_code
        st.session_state.current_company_name = company_name
    
    @staticmethod
    def get_analysis_data() -> Optional[Dict[str, Any]]:
        """分析データを取得"""
        return st.session_state.get('analysis_data')
    
    @staticmethod
    def has_analysis_data() -> bool:
        """分析データが存在するかチェック"""
        return st.session_state.get('analysis_data') is not None
    
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
        st.write("**デバッグ情報:**")
        st.write({
            'current_stock_code': st.session_state.get('current_stock_code'),
            'current_company_name': st.session_state.get('current_company_name'),
            'has_analysis_data': StateManager.has_analysis_data(),
            'is_running': StateManager.is_running(),
            'auto_run_trigger': StateManager.should_auto_run(),
            'direct_input': StateManager.get_direct_input(),
            'preset_mode': StateManager.get_preset_mode()
        })
# app.py - 軽量化メインアプリケーション
"""
株価分析学習アプリ - メインアプリケーション（軽量版）
教育・学習目的専用ツール
"""

import streamlit as st
from config.settings import APP_CONFIG
from ui.styles import StyleManager
from ui.components import UIComponents
from ui.settings_ui import SettingsUI
from ui.analysis_ui import AnalysisUI
from ui.portfolio_ui import PortfolioUI
from ui.guide_ui import GuideUI
from core.state_manager import StateManager
from core.app_controller import AppController


# === アプリケーション初期設定 ===
st.set_page_config(
    page_title=APP_CONFIG['page_title'],
    layout=APP_CONFIG['layout'],
    initial_sidebar_state=APP_CONFIG['initial_sidebar_state']
)

# スタイル適用
StyleManager.apply_all_styles()

# === コンポーネント初期化 ===
@st.cache_resource
def get_app_instances():
    """アプリケーションインスタンスを取得（キャッシュ）"""
    return {
        'app_controller': AppController(),
        'settings_ui': SettingsUI(),
        'analysis_ui': AnalysisUI(),
        'portfolio_ui': PortfolioUI(),
        'guide_ui': GuideUI()
    }

components = get_app_instances()

# === メインアプリケーション ===
def main():
    """メインアプリケーション関数"""
    
    # セッション状態初期化
    StateManager.initialize_session_state()
    
    # ヘッダー表示
    UIComponents.render_header()
    
    # 初心者向けガイド
    UIComponents.render_beginner_guide()
    
    # メイン設定エリア
    stock_code, analysis_params = components['settings_ui'].render_main_settings()
    
    # 分析実行ボタンエリア
    render_analysis_buttons(stock_code, analysis_params)
    
    # 分析結果表示
    if StateManager.has_analysis_data():
        components['analysis_ui'].render_analysis_results()
        
        # 分析結果がある場合のみ、ウォッチリスト追加UI表示
        st.markdown("---")
        components['portfolio_ui'].render_quick_portfolio_add()
    
    # ポートフォリオ管理セクション
    components['portfolio_ui'].render_portfolio_section()
    
    # 使い方ガイド
    components['guide_ui'].render_user_guide()
    
    # フッター
    components['guide_ui'].render_footer()


def render_analysis_buttons(stock_code: str, analysis_params: dict):
    """分析実行ボタンエリアを表示"""
    st.markdown("---")
    
    # ボタンエリア
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        manual_run = st.button(
            "🚀 分析開始", 
            type="primary", 
            use_container_width=True,
            disabled=StateManager.is_running()
        )
    
    with col2:
        if st.button("🔄 リセット", help="設定をリセットします"):
            StateManager.reset_application_state()
            st.success("✅ 設定をリセットしました")
            st.rerun()
    
    with col3:
        if st.button("📊 サンプル実行", help="Apple(AAPL)でサンプル分析"):
            StateManager.set_direct_input("AAPL")
            StateManager.trigger_auto_run()
            st.rerun()
    
    # 分析実行判定
    should_run_analysis = (
        manual_run or 
        StateManager.should_auto_run()
    ) and not StateManager.is_running()
    
    if should_run_analysis:
        if stock_code and stock_code.strip():
            # 自動実行フラグをクリア
            StateManager.clear_auto_run()
            
            # 実行前の確認メッセージ
            current_stock, _ = StateManager.get_current_stock_info()
            if stock_code != current_stock:
                st.info(f"📊 {stock_code} の分析を開始します...")
            
            # 分析実行
            success = components['app_controller'].run_analysis(stock_code, analysis_params)
            
            if success:
                st.rerun()  # 結果表示のために再読み込み
        else:
            st.warning("⚠️ 銘柄コードを選択または入力してください")
            StateManager.clear_auto_run()


# === アプリケーション実行 ===
if __name__ == "__main__":
    main()
# ui/styles.py
"""
スタイル・CSS管理機能
"""

import streamlit as st


class StyleManager:
    """スタイル管理クラス"""
    
    @staticmethod
    def apply_main_styles():
        """メインスタイルを適用"""
        st.markdown("""
        <style>
            /* 全体的なテキストの視認性向上 */
            .main-header {
                text-align: center;
                padding: 1.2rem 0;
                background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
                color: white !important;
                margin: -1rem -1rem 2rem -1rem;
                border-radius: 0 0 1rem 1rem;
                font-weight: bold;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }
            
            .metric-card {
                background: #ffffff !important;
                padding: 1.2rem;
                border-radius: 0.8rem;
                margin: 0.8rem 0;
                border: 2px solid #667eea !important;
                color: #000000 !important;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }
            
            /* 解説ボックスの大幅改善 */
            .explanation-box {
                background: #ffffff !important;
                border: 3px solid #2196F3 !important;
                padding: 1.2rem !important;
                border-radius: 1rem !important;
                margin: 1rem 0 !important;
                color: #000000 !important;
                font-weight: 600 !important;
                font-size: 1.05rem !important;
                line-height: 1.6 !important;
                box-shadow: 0 4px 12px rgba(33, 150, 243, 0.15) !important;
            }
            
            .explanation-box strong {
                color: #1565C0 !important;
                font-weight: 700 !important;
                font-size: 1.1rem !important;
            }
            
            .explanation-box span {
                color: #000000 !important;
                font-weight: 500 !important;
            }
            
            /* Tipボックスの大幅改善 */
            .tip-box {
                background: #fff8e1 !important;
                border: 3px solid #ff9800 !important;
                padding: 1.2rem !important;
                border-radius: 1rem !important;
                margin: 1rem 0 !important;
                color: #000000 !important;
                font-weight: 600 !important;
                font-size: 1rem !important;
                line-height: 1.6 !important;
                box-shadow: 0 4px 12px rgba(255, 152, 0, 0.15) !important;
            }
            
            .tip-box strong {
                color: #e65100 !important;
                font-weight: 700 !important;
                font-size: 1.05rem !important;
            }
            
            .tip-box span {
                color: #000000 !important;
                font-weight: 500 !important;
            }
            
            /* 免責事項の強調 */
            .disclaimer-box {
                background: #ffebee !important;
                border: 3px solid #f44336 !important;
                padding: 1.2rem !important;
                border-radius: 1rem !important;
                margin: 1rem 0 !important;
                color: #000000 !important;
                font-weight: 700 !important;
                font-size: 1.1rem !important;
                line-height: 1.6 !important;
                box-shadow: 0 4px 12px rgba(244, 67, 54, 0.15) !important;
            }
            
            /* すべてのテキストを強制的に黒色に */
            .explanation-box *, .tip-box *, .disclaimer-box * {
                color: #000000 !important;
            }
            
            .big-button {
                width: 100%;
                padding: 1.2rem;
                font-size: 1.3rem;
                margin: 1rem 0;
                font-weight: bold;
                border-radius: 0.8rem;
            }
            
            /* ダークモード対応（コントラスト重視） */
            @media (prefers-color-scheme: dark) {
                .explanation-box {
                    background: #1a1a1a !important;
                    border: 3px solid #64b5f6 !important;
                    color: #ffffff !important;
                }
                .explanation-box strong {
                    color: #90caf9 !important;
                }
                .explanation-box *, .explanation-box span {
                    color: #ffffff !important;
                }
                .tip-box {
                    background: #2d2d2d !important;
                    border: 3px solid #ffb74d !important;
                    color: #ffffff !important;
                }
                .tip-box strong {
                    color: #ffcc02 !important;
                }
                .tip-box *, .tip-box span {
                    color: #ffffff !important;
                }
                .disclaimer-box {
                    background: #3d2d2d !important;
                    border: 3px solid #ff6b6b !important;
                    color: #ffffff !important;
                }
                .disclaimer-box * {
                    color: #ffffff !important;
                }
                .metric-card {
                    background: #2d2d2d !important;
                    color: #ffffff !important;
                    border: 2px solid #64b5f6 !important;
                }
            }
            
            /* スマホ向けレスポンシブ */
            @media (max-width: 768px) {
                .explanation-box, .tip-box, .disclaimer-box {
                    font-size: 1rem !important;
                    padding: 1rem !important;
                    margin: 0.8rem 0 !important;
                }
                .main-header h1 {
                    font-size: 1.6rem !important;
                }
                .main-header p {
                    font-size: 1rem !important;
                }
            }
            
            /* Streamlitのデフォルトテキストも改善 */
            .stMarkdown {
                color: inherit !important;
            }
            
            /* エクスパンダー内のテキストも改善 */
            .streamlit-expanderHeader {
                font-weight: bold !important;
            }
        </style>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def apply_portfolio_styles():
        """ポートフォリオ専用スタイルを適用"""
        st.markdown("""
        <style>
            /* ポートフォリオカード */
            .portfolio-card {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 1.5rem;
                border-radius: 1rem;
                margin: 1rem 0;
                color: white;
                box-shadow: 0 8px 16px rgba(0,0,0,0.1);
            }
            
            .portfolio-card h3 {
                margin: 0 0 1rem 0;
                font-size: 1.4rem;
            }
            
            .portfolio-item {
                background: rgba(255, 255, 255, 0.1);
                padding: 1rem;
                border-radius: 0.5rem;
                margin: 0.5rem 0;
                backdrop-filter: blur(10px);
            }
            
            .profit {
                color: #4CAF50 !important;
                font-weight: bold;
            }
            
            .loss {
                color: #F44336 !important;
                font-weight: bold;
            }
            
            .neutral {
                color: #FF9800 !important;
                font-weight: bold;
            }
        </style>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def apply_chart_styles():
        """チャート専用スタイルを適用"""
        st.markdown("""
        <style>
            /* チャートコンテナ */
            .chart-container {
                background: white;
                border-radius: 1rem;
                padding: 1rem;
                margin: 1rem 0;
                box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            }
            
            .chart-title {
                font-size: 1.2rem;
                font-weight: bold;
                color: #333;
                margin-bottom: 1rem;
                text-align: center;
            }
            
            .chart-controls {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 0.5rem;
                background: #f8f9fa;
                border-radius: 0.5rem;
                margin-bottom: 1rem;
            }
            
            /* レスポンシブチャート */
            @media (max-width: 768px) {
                .chart-container {
                    padding: 0.5rem;
                    margin: 0.5rem 0;
                }
                
                .chart-controls {
                    flex-direction: column;
                    gap: 0.5rem;
                }
            }
        </style>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def apply_analysis_styles():
        """分析結果専用スタイルを適用"""
        st.markdown("""
        <style>
            /* シグナルボックス */
            .signal-box {
                padding: 1.5rem;
                border-radius: 1rem;
                margin: 1rem 0;
                text-align: center;
                font-weight: bold;
                box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            }
            
            .signal-buy {
                background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
                color: white;
                border: 3px solid #2E7D32;
            }
            
            .signal-sell {
                background: linear-gradient(135deg, #F44336 0%, #d32f2f 100%);
                color: white;
                border: 3px solid #C62828;
            }
            
            .signal-neutral {
                background: linear-gradient(135deg, #FF9800 0%, #f57c00 100%);
                color: white;
                border: 3px solid #E65100;
            }
            
            .signal-score {
                font-size: 1.5rem;
                margin: 0.5rem 0;
            }
            
            .signal-description {
                font-size: 1.1rem;
                opacity: 0.9;
            }
            
            /* 指標カード */
            .indicator-card {
                background: white;
                border: 2px solid #e0e0e0;
                border-radius: 0.8rem;
                padding: 1rem;
                margin: 0.5rem 0;
                transition: all 0.3s ease;
            }
            
            .indicator-card:hover {
                border-color: #667eea;
                box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            }
            
            .indicator-title {
                font-weight: bold;
                color: #333;
                margin-bottom: 0.5rem;
            }
            
            .indicator-value {
                font-size: 1.2rem;
                font-weight: bold;
                color: #667eea;
            }
        </style>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def apply_performance_styles():
        """パフォーマンス表示専用スタイルを適用"""
        st.markdown("""
        <style>
            /* パフォーマンスグレード */
            .performance-excellent {
                background: linear-gradient(135deg, #4CAF50 0%, #2E7D32 100%);
                color: white;
                padding: 1rem;
                border-radius: 0.8rem;
                text-align: center;
                font-weight: bold;
                margin: 1rem 0;
            }
            
            .performance-good {
                background: linear-gradient(135deg, #2196F3 0%, #1565C0 100%);
                color: white;
                padding: 1rem;
                border-radius: 0.8rem;
                text-align: center;
                font-weight: bold;
                margin: 1rem 0;
            }
            
            .performance-poor {
                background: linear-gradient(135deg, #FF9800 0%, #E65100 100%);
                color: white;
                padding: 1rem;
                border-radius: 0.8rem;
                text-align: center;
                font-weight: bold;
                margin: 1rem 0;
            }
            
            /* メトリクステーブル */
            .metrics-table {
                width: 100%;
                border-collapse: collapse;
                margin: 1rem 0;
                background: white;
                border-radius: 0.8rem;
                overflow: hidden;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }
            
            .metrics-table th {
                background: #667eea;
                color: white;
                padding: 1rem;
                font-weight: bold;
                text-align: left;
            }
            
            .metrics-table td {
                padding: 0.8rem 1rem;
                border-bottom: 1px solid #e0e0e0;
            }
            
            .metrics-table tr:nth-child(even) {
                background: #f8f9fa;
            }
            
            .metrics-table tr:hover {
                background: #e3f2fd;
            }
        </style>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def apply_mobile_optimizations():
        """モバイル最適化スタイルを追加適用"""
        st.markdown("""
        <style>
            /* モバイル最適化 */
            @media (max-width: 768px) {
                /* ボタンサイズの調整 */
                .stButton > button {
                    width: 100%;
                    padding: 0.8rem 1rem;
                    font-size: 1rem;
                    margin: 0.5rem 0;
                }
                
                /* セレクトボックスの調整 */
                .stSelectbox > div {
                    font-size: 1rem;
                }
                
                /* スライダーの調整 */
                .stSlider > div {
                    padding: 0.5rem 0;
                }
                
                /* メトリクスカードの調整 */
                .metric-card {
                    padding: 0.8rem;
                    margin: 0.5rem 0;
                }
                
                /* テキスト入力の調整 */
                .stTextInput > div > div > input {
                    font-size: 1rem;
                    padding: 0.5rem;
                }
                
                /* エクスパンダーの調整 */
                .streamlit-expanderHeader {
                    font-size: 1rem;
                    padding: 0.5rem;
                }
                
                /* カラムの調整 */
                .stColumns > div {
                    padding: 0.25rem;
                }
            }
            
            /* タブレット向け調整 */
            @media (min-width: 769px) and (max-width: 1024px) {
                .explanation-box, .tip-box, .disclaimer-box {
                    font-size: 1.05rem;
                    padding: 1.1rem;
                }
                
                .main-header h1 {
                    font-size: 1.8rem;
                }
            }
        </style>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def apply_accessibility_styles():
        """アクセシビリティ向上スタイルを適用"""
        st.markdown("""
        <style>
            /* アクセシビリティ向上 */
            
            /* フォーカス表示の改善 */
            .stButton > button:focus,
            .stSelectbox > div:focus,
            .stTextInput > div > div > input:focus,
            .stSlider > div:focus {
                outline: 3px solid #667eea !important;
                outline-offset: 2px !important;
            }
            
            /* 高コントラストモード */
            @media (prefers-contrast: high) {
                .explanation-box {
                    border-width: 4px !important;
                    background: #ffffff !important;
                    color: #000000 !important;
                }
                
                .tip-box {
                    border-width: 4px !important;
                    background: #fffbf0 !important;
                    color: #000000 !important;
                }
                
                .disclaimer-box {
                    border-width: 4px !important;
                    background: #fff5f5 !important;
                    color: #000000 !important;
                }
            }
            
            /* 動きを減らす設定への対応 */
            @media (prefers-reduced-motion: reduce) {
                * {
                    animation-duration: 0.01ms !important;
                    animation-iteration-count: 1 !important;
                    transition-duration: 0.01ms !important;
                }
            }
            
            /* スクリーンリーダー専用テキスト */
            .sr-only {
                position: absolute;
                width: 1px;
                height: 1px;
                padding: 0;
                margin: -1px;
                overflow: hidden;
                clip: rect(0, 0, 0, 0);
                white-space: nowrap;
                border: 0;
            }
        </style>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def apply_all_styles():
        """すべてのスタイルを一括適用"""
        StyleManager.apply_main_styles()
        StyleManager.apply_portfolio_styles()
        StyleManager.apply_chart_styles()
        StyleManager.apply_analysis_styles()
        StyleManager.apply_performance_styles()
        StyleManager.apply_mobile_optimizations()
        StyleManager.apply_accessibility_styles()
    
    @staticmethod
    def get_color_scheme() -> dict:
        """カラースキームを取得"""
        return {
            'primary': '#667eea',
            'secondary': '#764ba2',
            'success': '#4CAF50',
            'warning': '#FF9800',
            'danger': '#F44336',
            'info': '#2196F3',
            'light': '#f8f9fa',
            'dark': '#343a40',
            'white': '#ffffff',
            'black': '#000000'
        }
    
    @staticmethod
    def create_custom_metric_card(title: str, value: str, delta: str = None, 
                                delta_color: str = "normal") -> str:
        """
        カスタムメトリクスカードのHTMLを生成
        
        Args:
            title: タイトル
            value: 値
            delta: 変動値
            delta_color: 変動色（normal, inverse）
            
        Returns:
            str: HTMLコード
        """
        delta_html = ""
        if delta:
            color = "green" if delta_color == "normal" else "red"
            if delta.startswith("-"):
                color = "red" if delta_color == "normal" else "green"
            
            delta_html = f'<div style="color: {color}; font-size: 0.9rem; margin-top: 0.5rem;">{delta}</div>'
        
        return f"""
        <div class="metric-card">
            <div style="font-size: 0.9rem; color: #666; margin-bottom: 0.5rem;">{title}</div>
            <div style="font-size: 1.8rem; font-weight: bold; color: #333;">{value}</div>
            {delta_html}
        </div>
        """
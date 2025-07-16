# core/app_controller.py
"""
アプリケーションコントローラー - メイン業務ロジック
"""

import streamlit as st
from typing import Dict, Any, Tuple
from datetime import datetime, timedelta

from data.cache_manager import cache_stock_data
from analysis import TechnicalAnalyzer, SignalGenerator, BacktestEngine
from .state_manager import StateManager


class AppController:
    """アプリケーション制御クラス"""
    
    def __init__(self):
        self.technical_analyzer = TechnicalAnalyzer()
        self.signal_generator = SignalGenerator()
        self.backtest_engine = BacktestEngine()
    
    def run_analysis(self, stock_code: str, params: Dict[str, Any]) -> bool:
        """
        分析を実行
        
        Args:
            stock_code: 銘柄コード
            params: 分析パラメータ
            
        Returns:
            bool: 成功/失敗
        """
        # 実行中フラグを設定
        StateManager.set_running_state(True)
        
        try:
            with st.spinner("📊 データを分析中...少し時間がかかります"):
                
                # データ取得
                df, info = cache_stock_data(
                    stock_code, 
                    params['start_date'], 
                    params['end_date']
                )
                
                if df is not None and len(df) > 0:
                    
                    # テクニカル分析
                    df = self.technical_analyzer.calculate_indicators(df, **params)
                    
                    # シグナル生成
                    signals = self.signal_generator.generate_signals_advanced(df)
                    
                    # バックテスト実行
                    portfolio, trade_log = self.backtest_engine.backtest_realistic(
                        df, signals, **params
                    )
                    
                    # 結果を保存
                    summary = self.technical_analyzer.get_indicator_summary(df)
                    signal_explanation = self.signal_generator.get_signal_explanation(
                        signals, df
                    )
                    
                    company_name = info.get('longName', stock_code)
                    
                    StateManager.set_analysis_data(
                        df, info, signals, portfolio, trade_log, 
                        params, summary, signal_explanation, 
                        stock_code, company_name
                    )
                    
                    st.success("✅ 分析が完了しました！")
                    return True
                
                else:
                    st.error("""
                    ❌ **データを取得できませんでした**

                    以下を確認してください：
                    - 銘柄コードが正しいか
                    - インターネットに接続されているか
                    - 市場が開いているか（平日の取引時間）
                    - データが十分にあるか
                    """)
                    return False
        
        except Exception as e:
            st.error(f"❌ 分析中にエラーが発生しました: {e}")
            st.info("🔄 リセットボタンを押して再試行してください")
            return False
        
        finally:
            # 実行中フラグをリセット
            StateManager.set_running_state(False)
            StateManager.clear_auto_run()
    
    def get_analysis_parameters(self, selected_period: str, 
                               technical_params: Dict[str, int],
                               backtest_params: Dict[str, float]) -> Dict[str, Any]:
        """分析パラメータを構築"""
        from config.settings import PERIOD_OPTIONS
        
        days = PERIOD_OPTIONS[selected_period]
        start_date = datetime.now() - timedelta(days=days)
        end_date = datetime.now()
        
        return {
            'start_date': start_date,
            'end_date': end_date,
            'period_name': selected_period,
            **technical_params,
            **backtest_params
        }
    
    def get_preset_settings(self, preset_type: str) -> Tuple[Dict[str, int], Dict[str, float]]:
        """プリセット設定を取得"""
        presets = {
            "beginner": {
                "technical": {
                    'short_ma': 25, 'long_ma': 60, 'rsi_period': 16, 'bb_period': 25
                },
                "backtest": {
                    'initial_capital': 1000000, 'risk_per_trade': 1.0,
                    'stop_loss_pct': 3.0, 'take_profit_pct': 10.0, 'trade_cost_rate': 0.1
                }
            },
            "balanced": {
                "technical": {
                    'short_ma': 20, 'long_ma': 50, 'rsi_period': 14, 'bb_period': 20
                },
                "backtest": {
                    'initial_capital': 1000000, 'risk_per_trade': 2.0,
                    'stop_loss_pct': 5.0, 'take_profit_pct': 15.0, 'trade_cost_rate': 0.1
                }
            },
            "aggressive": {
                "technical": {
                    'short_ma': 10, 'long_ma': 30, 'rsi_period': 10, 'bb_period': 15
                },
                "backtest": {
                    'initial_capital': 1000000, 'risk_per_trade': 5.0,
                    'stop_loss_pct': 8.0, 'take_profit_pct': 25.0, 'trade_cost_rate': 0.1
                }
            }
        }
        
        preset = presets.get(preset_type, presets["balanced"])
        return preset["technical"], preset["backtest"]
    
    def validate_stock_symbol(self, symbol: str) -> Tuple[bool, str, str]:
        """
        銘柄コードを検証
        
        Returns:
            Tuple[bool, str, str]: (有効性, メッセージ, 企業情報)
        """
        if not symbol or not symbol.strip():
            return False, "銘柄コードを入力してください", ""
        
        symbol = symbol.strip().upper()
        
        # 基本的なフォーマットチェック
        if len(symbol) < 1 or len(symbol) > 10:
            return False, "銘柄コードの長さが正しくありません", ""
        
        # 日本株のフォーマット（例: 7203.T）
        if symbol.endswith('.T'):
            code_part = symbol[:-2]
            if code_part.isdigit() and len(code_part) == 4:
                company_info = self._get_japanese_company_info(symbol)
                return True, f"日本株として認識されました: {symbol}", company_info
            else:
                return False, "日本株の形式が正しくありません（例: 7203.T）", ""
        
        # 米国株のフォーマット（例: AAPL）
        if symbol.isalpha() and 1 <= len(symbol) <= 5:
            company_info = self._get_us_company_info(symbol)
            return True, f"米国株として認識されました: {symbol}", company_info
        
        # その他の市場
        if symbol.replace('.', '').replace('-', '').isalnum():
            return True, f"銘柄コードとして認識されました: {symbol}", "※ 詳細は分析実行時に取得されます"
        
        return False, "銘柄コードの形式が正しくありません", ""
    
    def _get_japanese_company_info(self, symbol: str) -> str:
        """日本企業の簡易情報を取得"""
        japanese_companies = {
            "7203.T": "トヨタ自動車 - 世界最大の自動車メーカー",
            "6758.T": "ソニーグループ - エンターテインメント・テクノロジー企業",
            "7974.T": "任天堂 - ゲーム・娯楽機器メーカー",
            "9984.T": "ソフトバンクグループ - 投資・通信企業",
            "6861.T": "キーエンス - 自動化機器メーカー",
            "4755.T": "楽天グループ - インターネットサービス",
            "9983.T": "ファーストリテイリング - 衣料品企業（ユニクロ）",
            "7267.T": "ホンダ - 自動車・バイクメーカー",
            "7201.T": "日産自動車 - 自動車メーカー"
        }
        return japanese_companies.get(symbol, "日本の上場企業")
    
    def _get_us_company_info(self, symbol: str) -> str:
        """米国企業の簡易情報を取得"""
        us_companies = {
            "AAPL": "Apple Inc. - iPhone・Mac等を製造するテクノロジー企業",
            "MSFT": "Microsoft Corporation - Windows・Office等のソフトウェア企業",
            "GOOGL": "Alphabet Inc. - Google検索・YouTube等を運営",
            "AMZN": "Amazon.com Inc. - 電子商取引・クラウドサービス企業",
            "TSLA": "Tesla Inc. - 電気自動車・エネルギー企業",
            "NVDA": "NVIDIA Corporation - GPU・AI半導体メーカー",
            "META": "Meta Platforms Inc. - Facebook・Instagram等を運営",
            "NFLX": "Netflix Inc. - 動画配信サービス",
            "DIS": "The Walt Disney Company - エンターテインメント企業",
            "NKE": "Nike Inc. - スポーツ用品メーカー"
        }
        return us_companies.get(symbol, "米国の上場企業")
# core/app_controller.py - JQuants API対応・validate_stock_symbol更新版
"""
アプリケーションコントローラー - メイン業務ロジック（JQuants API対応・validate_stock_symbol更新版）
"""

import streamlit as st
from typing import Dict, Any, Tuple, Optional
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

from data.cache_manager import cache_stock_data
from analysis import TechnicalAnalyzer, SignalGenerator, BacktestEngine
from .state_manager import StateManager
from config.settings import WEIGHT_MODES, DYNAMIC_WEIGHT_PROFILES


class AppController:
    """アプリケーション制御クラス（JQuants API対応・validate_stock_symbol更新版）"""
    
    def __init__(self):
        self.technical_analyzer = TechnicalAnalyzer()
        self.signal_generator = SignalGenerator()
        self.backtest_engine = BacktestEngine()
    
    def run_analysis(self, stock_code: str, params: Dict[str, Any]) -> bool:
        """
        分析を実行（動的重み付け対応・バックテスト修正版）
        
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
                    
                    # 動的重み付け設定の適用
                    self._configure_signal_generator(params)
                    
                    # シグナル生成
                    signals = self.signal_generator.generate_signals_advanced(df)
                    
                    # バックテスト実行（改良版エラー処理）
                    portfolio, trade_log = self._execute_backtest_with_fallback(df, signals, params)
                    
                    # 結果を保存
                    summary = self.technical_analyzer.get_indicator_summary(df)
                    signal_explanation = self.signal_generator.get_signal_explanation(
                        signals, df
                    )
                    
                    # 動的重み付け情報の取得
                    adaptive_info = self._get_adaptive_analysis_info()
                    
                    company_name = info.get('longName', stock_code)
                    
                    # データ保存（下位互換性を保持）
                    if adaptive_info:
                        StateManager.set_analysis_data(
                            df, info, signals, portfolio, trade_log, 
                            params, summary, signal_explanation, 
                            stock_code, company_name, adaptive_info
                        )
                    else:
                        StateManager.set_analysis_data(
                            df, info, signals, portfolio, trade_log, 
                            params, summary, signal_explanation, 
                            stock_code, company_name
                        )
                    
                    st.success("✅ 分析が完了しました！")
                    
                    # 動的重み付けの場合は結果を表示
                    if params.get('weight_mode') == 'adaptive' and adaptive_info:
                        self._show_adaptive_results(adaptive_info)
                    
                    return True
                
                else:
                    st.error("""
                    ❌ データを取得できませんでした

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
            import traceback
            st.error(f"詳細エラー: {traceback.format_exc()}")
            return False
        
        finally:
            # 実行中フラグをリセット
            StateManager.set_running_state(False)
            StateManager.clear_auto_run()
    
    def _execute_backtest_with_fallback(self, df: pd.DataFrame, signals: pd.DataFrame, 
                                       params: Dict[str, Any]) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        バックテスト実行（フォールバック機能付き）
        
        Args:
            df: 株価データ
            signals: シグナルデータ
            params: パラメータ
            
        Returns:
            Tuple[DataFrame, DataFrame]: ポートフォリオと取引ログ
        """
        try:
            # 通常のバックテスト実行
            portfolio, trade_log = self.backtest_engine.backtest_realistic(
                df, signals, **params
            )
            
            # 結果の検証
            if portfolio is not None and not portfolio.empty and len(portfolio) > 0:
                # 正常なデータの場合
                if 'Total' in portfolio.columns and portfolio['Total'].notna().any():
                    st.success(f"✅ バックテスト完了: {len(portfolio)}日分のデータ")
                    
                    if trade_log is not None and not trade_log.empty:
                        st.info(f"📊 取引ログ: {len(trade_log)}件の取引")
                    else:
                        st.info("📊 取引ログ: 取引が発生しませんでした")
                    
                    return portfolio, trade_log
                else:
                    # ポートフォリオデータが異常な場合
                    raise ValueError("ポートフォリオデータに異常があります")
            else:
                # ポートフォリオが空の場合
                raise ValueError("バックテストでデータが生成されませんでした")
                
        except Exception as backtest_error:
            # エラー時の詳細ログ
            st.warning(f"⚠️ バックテスト実行エラー: {backtest_error}")
            st.info("💡 フォールバックモードでシミュレーションを生成します")
            
            # フォールバック用の改良されたダミーデータ生成
            return self._create_fallback_backtest_data(df, signals, params)
    
    def _create_fallback_backtest_data(self, df: pd.DataFrame, signals: pd.DataFrame, 
                                     params: Dict[str, Any]) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        フォールバック用のバックテストデータを生成
        
        Args:
            df: 株価データ
            signals: シグナルデータ
            params: パラメータ
            
        Returns:
            Tuple[DataFrame, DataFrame]: ポートフォリオと取引ログ
        """
        initial_capital = params.get('initial_capital', 1000000)
        
        # シンプルなBuy&Holdベンチマークを作成
        start_price = df['Close'].iloc[0]
        end_price = df['Close'].iloc[-1]
        shares = initial_capital / start_price
        
        # ポートフォリオ価値の推移を計算
        portfolio_values = []
        returns = []
        
        for i in range(len(df)):
            current_price = df['Close'].iloc[i]
            portfolio_value = shares * current_price
            portfolio_values.append(portfolio_value)
            
            # リターン計算
            if i == 0:
                returns.append(0.0)
            else:
                prev_value = portfolio_values[i-1]
                daily_return = (portfolio_value / prev_value - 1) if prev_value != 0 else 0.0
                returns.append(daily_return)
        
        # ポートフォリオDataFrame作成
        portfolio_df = pd.DataFrame({
            'Total': portfolio_values,
            'Returns': returns
        }, index=df.index)
        
        # 簡単な取引ログ作成（開始と終了のみ）
        trade_log = pd.DataFrame([
            {
                'Date': df.index[0],
                'Type': 'Buy',
                'Price': start_price,
                'Shares': shares,
                'Portfolio': initial_capital,
                'Entry_Price': start_price,
                'PnL': 0,
                'Exit_Reason': 'Initial Purchase'
            },
            {
                'Date': df.index[-1],
                'Type': 'Hold',
                'Price': end_price,
                'Shares': shares,
                'Portfolio': portfolio_values[-1],
                'Entry_Price': start_price,
                'PnL': portfolio_values[-1] - initial_capital,
                'Exit_Reason': 'End of Period'
            }
        ])
        
        # フォールバック使用の通知
        total_return = (portfolio_values[-1] / initial_capital - 1) * 100
        st.info(f"""
        📈 フォールバックモード結果
        - Buy&Hold戦略をシミュレーション
        - 総リターン: {total_return:.2f}%
        - これは参考値です。実際の戦略結果ではありません。
        """)
        
        return portfolio_df, trade_log
    
    def _configure_signal_generator(self, params: Dict[str, Any]):
        """シグナル生成器の設定"""
        weight_mode = params.get('weight_mode', 'fixed')
        manual_weights = params.get('manual_weights', None)
        
        self.signal_generator.set_weight_mode(weight_mode, manual_weights)
    
    def _get_adaptive_analysis_info(self) -> Optional[Dict[str, Any]]:
        """動的重み付け分析情報を取得"""
        if hasattr(self.signal_generator, 'current_pattern_info') and self.signal_generator.current_pattern_info:
            pattern_info = self.signal_generator.current_pattern_info
            
            return {
                'detected_pattern': pattern_info['pattern'],
                'pattern_name': pattern_info['pattern_info']['name'],
                'pattern_description': pattern_info['pattern_info']['description'],
                'confidence': pattern_info['confidence'],
                'weights_used': pattern_info['weights'],
                'strategy_hint': pattern_info['pattern_info']['strategy_hint'],
                'risk_level': pattern_info['pattern_info']['risk_level'],
                'analysis_details': pattern_info.get('analysis_details', {}),
                'pattern_scores': pattern_info.get('pattern_scores', {}),
                'detection_timestamp': pattern_info['detection_timestamp']
            }
        
        return None
    
    def _show_adaptive_results(self, adaptive_info: Dict[str, Any]):
        """動的重み付け結果の表示"""
        pattern_name = adaptive_info['pattern_name']
        confidence = adaptive_info['confidence']
        
        # パターン検出結果の表示
        confidence_pct = confidence * 100
        
        if confidence > 0.8:
            confidence_level = "高"
            confidence_color = "🟢"
        elif confidence > 0.6:
            confidence_level = "中"
            confidence_color = "🟡"
        else:
            confidence_level = "低"
            confidence_color = "🔴"
        
        st.info(f"""
        🎯 相場パターン検出結果
        
        検出パターン: {pattern_name}  
        信頼度: {confidence_color} {confidence_level} ({confidence_pct:.1f}%)  
        戦略ヒント: {adaptive_info['strategy_hint']}
        """)
    
    def get_analysis_parameters(self, selected_period: str, 
                               technical_params: Dict[str, int],
                               backtest_params: Dict[str, float],
                               adaptive_params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """分析パラメータを構築（動的重み付け対応）"""
        from config.settings import PERIOD_OPTIONS
        
        days = PERIOD_OPTIONS[selected_period]
        start_date = datetime.now() - timedelta(days=days)
        end_date = datetime.now()
        
        params = {
            'start_date': start_date,
            'end_date': end_date,
            'period_name': selected_period,
            **technical_params,
            **backtest_params
        }
        
        # 動的重み付けパラメータの追加
        if adaptive_params:
            params.update(adaptive_params)
        else:
            # デフォルトは固定重み付け
            params['weight_mode'] = 'fixed'
        
        return params
    
    def get_preset_settings(self, preset_type: str) -> Tuple[Dict[str, int], Dict[str, float]]:
        """プリセット設定を取得（変更なし）"""
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
    
    def get_adaptive_preset_settings(self, preset_type: str) -> Dict[str, Any]:
        """動的重み付け用プリセット設定を取得"""
        adaptive_presets = {
            "beginner": {
                'weight_mode': 'fixed',  # 初心者は固定重み付け
                'manual_weights': None
            },
            "balanced": {
                'weight_mode': 'adaptive',  # バランス型は動的重み付け
                'manual_weights': None
            },
            "aggressive": {
                'weight_mode': 'adaptive',  # 積極型も動的重み付け
                'manual_weights': None
            }
        }
        
        return adaptive_presets.get(preset_type, adaptive_presets["balanced"])
    
    def get_weight_mode_info(self) -> Dict[str, Any]:
        """重み付けモード情報を取得"""
        return WEIGHT_MODES
    
    def get_available_patterns(self) -> Dict[str, Any]:
        """利用可能なパターン情報を取得"""
        return DYNAMIC_WEIGHT_PROFILES
    
    def create_manual_weights(self, ma_weight: float, rsi_weight: float, 
                            bollinger_weight: float, macd_weight: float, 
                            volume_weight: float) -> Dict[str, float]:
        """手動重み付けを作成"""
        weights = {
            'ma_trend': ma_weight,
            'rsi': rsi_weight,
            'bollinger': bollinger_weight,
            'macd': macd_weight,
            'volume': volume_weight
        }
        
        # 正規化
        total = sum(weights.values())
        if total > 0:
            weights = {k: v / total for k, v in weights.items()}
        
        return weights
    
    def get_pattern_analysis_preview(self, stock_code: str, period_days: int = 30) -> Optional[Dict[str, Any]]:
        """パターン分析のプレビューを取得"""
        try:
            # 簡易データ取得
            start_date = datetime.now() - timedelta(days=period_days)
            end_date = datetime.now()
            
            df, _ = cache_stock_data(stock_code, start_date, end_date)
            
            if df is None or len(df) < 10:
                return None
            
            # テクニカル指標を計算
            df = self.technical_analyzer.calculate_indicators(df)
            
            # パターン検出のみ実行
            from analysis.pattern_detector import MarketPatternDetector
            detector = MarketPatternDetector()
            pattern_info = detector.detect_market_pattern(df)
            
            return {
                'pattern': pattern_info['pattern'],
                'pattern_name': pattern_info['pattern_info']['name'],
                'confidence': pattern_info['confidence'],
                'strategy_hint': pattern_info['pattern_info']['strategy_hint'],
                'risk_level': pattern_info['pattern_info']['risk_level']
            }
            
        except Exception as e:
            return None
    
    def validate_stock_symbol(self, symbol: str) -> Tuple[bool, str, Dict[str, str]]:
        """
        銘柄コードの検証（JQuants API対応・市場情報付き）
        
        Args:
            symbol: 銘柄コード
            
        Returns:
            Tuple[bool, str, Dict]: (有効性, メッセージ, 市場情報)
        """
        try:
            # 新しい検証機能を使用
            from data.stock_fetcher import validate_stock_symbol
            is_valid, message, market_info = validate_stock_symbol(symbol)
            return is_valid, message, market_info
            
        except ImportError:
            # フォールバック：従来の基本検証
            return self._validate_stock_symbol_fallback(symbol)
        except Exception:
            # エラー時のフォールバック
            return False, "検証中にエラーが発生しました", {}
    
    def _validate_stock_symbol_fallback(self, symbol: str) -> Tuple[bool, str, Dict[str, str]]:
        """
        銘柄コード検証のフォールバック（基本検証）
        
        Args:
            symbol: 銘柄コード
            
        Returns:
            Tuple[bool, str, Dict]: (有効性, メッセージ, 市場情報)
        """
        if not symbol or not symbol.strip():
            return False, "銘柄コードを入力してください", {}
        
        symbol = symbol.strip().upper()
        
        # 基本的なフォーマットチェック
        if len(symbol) < 1 or len(symbol) > 10:
            return False, "銘柄コードの長さが正しくありません", {}
        
        # 日本株のフォーマット（例: 7203.T）
        if symbol.endswith('.T'):
            code_part = symbol[:-2]
            if code_part.isdigit() and len(code_part) == 4:
                market_info = {
                    'market': '東京証券取引所',
                    'exchange': 'Tokyo Stock Exchange',
                    'currency': 'JPY',
                    'region': 'Japan',
                    'suffix': '.T'
                }
                return True, f"日本株として認識されました: {symbol}", market_info
            else:
                return False, "日本株の形式が正しくありません（例: 7203.T）", {}
        
        # 米国株のフォーマット（例: AAPL）
        if symbol.isalpha() and 1 <= len(symbol) <= 5:
            market_info = {
                'market': 'US Stock Market',
                'exchange': 'NASDAQ/NYSE',
                'currency': 'USD',
                'region': 'United States',
                'suffix': ''
            }
            return True, f"米国株として認識されました: {symbol}", market_info
        
        # その他の市場
        if symbol.replace('.', '').replace('-', '').isalnum():
            market_info = {
                'market': 'Unknown Market',
                'exchange': 'Unknown Exchange',
                'currency': 'Unknown',
                'region': 'Unknown',
                'suffix': ''
            }
            return True, f"銘柄コードとして認識されました: {symbol}", market_info
        
        return False, "銘柄コードの形式が正しくありません", {}
# ui/charts.py
"""
チャート生成機能
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import streamlit as st
from typing import Dict, Any, Optional


class ChartGenerator:
    """チャート生成クラス"""
    
    def __init__(self):
        self.color_scheme = {
            'bullish': 'green',
            'bearish': 'red', 
            'neutral': 'blue',
            'ma_short': 'orange',
            'ma_long': 'blue',
            'rsi': 'purple',
            'bb_band': 'gray',
            'macd': 'blue',
            'macd_signal': 'red',
            'volume': 'lightblue'
        }
    
    def create_technical_chart(self, df: pd.DataFrame, signals: pd.DataFrame, 
                             symbol: str, params: Dict[str, int]) -> go.Figure:
        """
        テクニカル分析チャートを作成
        
        Args:
            df: 株価データ
            signals: シグナルデータ
            symbol: 銘柄コード
            params: テクニカル指標パラメータ
            
        Returns:
            go.Figure: Plotlyフィギュア
        """
        # サブプロット作成
        fig = make_subplots(
            rows=3, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.08,
            row_heights=[0.6, 0.2, 0.2],
            subplot_titles=(
                '📈 株価・移動平均・ボリンジャーバンド', 
                '🌡️ RSI（相対力指数）', 
                '⚡ MACD（移動平均収束拡散）'
            )
        )
        
        # メイン価格チャート
        self._add_candlestick_chart(fig, df, row=1, col=1)
        self._add_moving_averages(fig, df, params, row=1, col=1)
        self._add_bollinger_bands(fig, df, row=1, col=1)
        self._add_trading_signals(fig, df, signals, row=1, col=1)
        
        # RSIチャート
        self._add_rsi_chart(fig, df, row=2, col=1)
        
        # MACDチャート
        self._add_macd_chart(fig, df, row=3, col=1)
        
        # レイアウト設定
        self._configure_layout(fig, symbol)
        
        return fig
    
    def _add_candlestick_chart(self, fig: go.Figure, df: pd.DataFrame, row: int, col: int):
        """ローソク足チャートを追加"""
        fig.add_trace(
            go.Candlestick(
                x=df.index,
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close'],
                name='株価',
                increasing_line_color=self.color_scheme['bullish'],
                decreasing_line_color=self.color_scheme['bearish']
            ),
            row=row, col=col
        )
    
    def _add_moving_averages(self, fig: go.Figure, df: pd.DataFrame, 
                           params: Dict[str, int], row: int, col: int):
        """移動平均線を追加"""
        if 'MA_short' in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df['MA_short'],
                    name=f'短期平均({params.get("short_ma", 20)}日)',
                    line=dict(color=self.color_scheme['ma_short'], width=2),
                    opacity=0.8
                ),
                row=row, col=col
            )
        
        if 'MA_long' in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df['MA_long'],
                    name=f'長期平均({params.get("long_ma", 50)}日)',
                    line=dict(color=self.color_scheme['ma_long'], width=2),
                    opacity=0.8
                ),
                row=row, col=col
            )
    
    def _add_bollinger_bands(self, fig: go.Figure, df: pd.DataFrame, row: int, col: int):
        """ボリンジャーバンドを追加"""
        if all(col in df.columns for col in ['BB_upper', 'BB_lower']):
            # 上限線
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df['BB_upper'],
                    name='上限ライン',
                    line=dict(color=self.color_scheme['bb_band'], dash='dash', width=1),
                    opacity=0.6
                ),
                row=row, col=col
            )
            
            # 下限線
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df['BB_lower'],
                    name='下限ライン',
                    line=dict(color=self.color_scheme['bb_band'], dash='dash', width=1),
                    opacity=0.6,
                    fill='tonexty',
                    fillcolor='rgba(128, 128, 128, 0.1)'
                ),
                row=row, col=col
            )
    
    def _add_trading_signals(self, fig: go.Figure, df: pd.DataFrame, 
                           signals: pd.DataFrame, row: int, col: int):
        """売買シグナルを追加"""
        buy_signals = df.index[signals['signal'] == 1]
        sell_signals = df.index[signals['signal'] == -1]
        
        if len(buy_signals) > 0:
            fig.add_trace(
                go.Scatter(
                    x=buy_signals,
                    y=df.loc[buy_signals, 'Low'] * 0.98,
                    mode='markers',
                    name='🟢買いサイン',
                    marker=dict(
                        symbol='triangle-up',
                        size=12,
                        color=self.color_scheme['bullish'],
                        line=dict(color='white', width=1)
                    )
                ),
                row=row, col=col
            )
        
        if len(sell_signals) > 0:
            fig.add_trace(
                go.Scatter(
                    x=sell_signals,
                    y=df.loc[sell_signals, 'High'] * 1.02,
                    mode='markers',
                    name='🔴売りサイン',
                    marker=dict(
                        symbol='triangle-down',
                        size=12,
                        color=self.color_scheme['bearish'],
                        line=dict(color='white', width=1)
                    )
                ),
                row=row, col=col
            )
    
    def _add_rsi_chart(self, fig: go.Figure, df: pd.DataFrame, row: int, col: int):
        """RSIチャートを追加"""
        if 'RSI' in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df['RSI'],
                    name='RSI',
                    line=dict(color=self.color_scheme['rsi'], width=2)
                ),
                row=row, col=col
            )
            
            # RSI基準線
            fig.add_hline(y=70, line_dash="dash", line_color="red", 
                         annotation_text="買われすぎ", row=row, col=col)
            fig.add_hline(y=30, line_dash="dash", line_color="green", 
                         annotation_text="売られすぎ", row=row, col=col)
            fig.add_hline(y=50, line_dash="dot", line_color="gray", 
                         annotation_text="中立", row=row, col=col)
    
    def _add_macd_chart(self, fig: go.Figure, df: pd.DataFrame, row: int, col: int):
        """MACDチャートを追加"""
        if 'MACD' in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df['MACD'],
                    name='MACD',
                    line=dict(color=self.color_scheme['macd'], width=2)
                ),
                row=row, col=col
            )
        
        if 'MACD_signal' in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df['MACD_signal'],
                    name='シグナル',
                    line=dict(color=self.color_scheme['macd_signal'], width=2)
                ),
                row=row, col=col
            )
        
        # MACDヒストグラム
        if 'MACD_diff' in df.columns:
            colors = ['green' if val >= 0 else 'red' for val in df['MACD_diff']]
            fig.add_trace(
                go.Bar(
                    x=df.index,
                    y=df['MACD_diff'],
                    name='MACD差分',
                    marker_color=colors,
                    opacity=0.6
                ),
                row=row, col=col
            )
        
        # ゼロライン
        fig.add_hline(y=0, line_dash="dash", line_color="gray", row=row, col=col)
    
    def _configure_layout(self, fig: go.Figure, symbol: str):
        """レイアウトを設定"""
        fig.update_layout(
            title=f"{symbol} のテクニカル分析チャート",
            height=700,
            xaxis_rangeslider_visible=False,
            showlegend=False,
            margin=dict(l=10, r=10, t=50, b=10),
            font=dict(size=12),
            plot_bgcolor='white',
            paper_bgcolor='white'
        )
        
        # Y軸ラベル設定
        fig.update_yaxes(title_text="株価", row=1, col=1, gridcolor='lightgray')
        fig.update_yaxes(title_text="RSI", row=2, col=1, range=[0, 100], gridcolor='lightgray')
        fig.update_yaxes(title_text="MACD", row=3, col=1, gridcolor='lightgray')
        
        # X軸設定
        fig.update_xaxes(gridcolor='lightgray')
    
    def create_portfolio_chart(self, portfolio_df: pd.DataFrame, initial_capital: float) -> go.Figure:
        """
        ポートフォリオ推移チャートを作成
        
        Args:
            portfolio_df: ポートフォリオデータ
            initial_capital: 初期資金
            
        Returns:
            go.Figure: Plotlyフィギュア
        """
        fig = go.Figure()
        
        # ポートフォリオ価値の推移
        colors = ['green' if val >= initial_capital else 'red' 
                 for val in portfolio_df['Total']]
        
        fig.add_trace(
            go.Scatter(
                x=portfolio_df.index,
                y=portfolio_df['Total'],
                mode='lines',
                name='仮想資産の変化',
                line=dict(color='blue', width=3),
                fill='tonexty',
                fillcolor='rgba(0, 100, 200, 0.1)'
            )
        )
        
        # 初期資金ライン
        fig.add_hline(
            y=initial_capital,
            line_dash="dash",
            line_color="red",
            annotation_text="初期資金",
            annotation_position="top right"
        )
        
        # レイアウト設定
        fig.update_layout(
            title="シミュレーション期間中の仮想資産変化",
            height=400,
            showlegend=False,
            margin=dict(l=10, r=10, t=50, b=10),
            xaxis_title="日付",
            yaxis_title="資産価値（円）",
            plot_bgcolor='white',
            paper_bgcolor='white'
        )
        
        fig.update_xaxes(gridcolor='lightgray')
        fig.update_yaxes(gridcolor='lightgray')
        
        return fig
    
    def create_performance_comparison_chart(self, portfolio_returns: pd.Series, 
                                          benchmark_returns: pd.Series) -> go.Figure:
        """
        パフォーマンス比較チャートを作成
        
        Args:
            portfolio_returns: ポートフォリオリターン
            benchmark_returns: ベンチマークリターン
            
        Returns:
            go.Figure: Plotlyフィギュア
        """
        # 累積リターン計算
        portfolio_cumret = (1 + portfolio_returns).cumprod()
        benchmark_cumret = (1 + benchmark_returns).cumprod()
        
        fig = go.Figure()
        
        # ポートフォリオ
        fig.add_trace(
            go.Scatter(
                x=portfolio_cumret.index,
                y=portfolio_cumret,
                name='投資戦略',
                line=dict(color='blue', width=2)
            )
        )
        
        # ベンチマーク
        fig.add_trace(
            go.Scatter(
                x=benchmark_cumret.index,
                y=benchmark_cumret,
                name='ベンチマーク',
                line=dict(color='red', width=2, dash='dash')
            )
        )
        
        fig.update_layout(
            title="投資戦略 vs ベンチマーク比較",
            height=400,
            xaxis_title="日付",
            yaxis_title="累積リターン",
            plot_bgcolor='white',
            paper_bgcolor='white'
        )
        
        return fig
    
    def create_risk_return_scatter(self, returns_data: Dict[str, pd.Series]) -> go.Figure:
        """
        リスク・リターン散布図を作成
        
        Args:
            returns_data: リターンデータの辞書
            
        Returns:
            go.Figure: Plotlyフィギュア
        """
        fig = go.Figure()
        
        for name, returns in returns_data.items():
            if returns.empty:
                continue
                
            annual_return = returns.mean() * 252 * 100  # 年率リターン
            annual_vol = returns.std() * (252 ** 0.5) * 100  # 年率ボラティリティ
            
            fig.add_trace(
                go.Scatter(
                    x=[annual_vol],
                    y=[annual_return],
                    mode='markers',
                    name=name,
                    marker=dict(size=15),
                    text=f'{name}<br>リターン: {annual_return:.2f}%<br>リスク: {annual_vol:.2f}%',
                    textposition='top center'
                )
            )
        
        fig.update_layout(
            title="リスク・リターン分析",
            height=400,
            xaxis_title="年率ボラティリティ (%)",
            yaxis_title="年率リターン (%)",
            plot_bgcolor='white',
            paper_bgcolor='white'
        )
        
        # リスクフリーレートライン（仮定：1%）
        fig.add_hline(y=1, line_dash="dot", line_color="gray", 
                     annotation_text="リスクフリーレート")
        
        return fig
    
    def create_drawdown_chart(self, portfolio_df: pd.DataFrame) -> go.Figure:
        """
        ドローダウンチャートを作成
        
        Args:
            portfolio_df: ポートフォリオデータ
            
        Returns:
            go.Figure: Plotlyフィギュア
        """
        portfolio_values = portfolio_df['Total']
        peak = portfolio_values.expanding().max()
        drawdown = (portfolio_values / peak - 1) * 100
        
        fig = go.Figure()
        
        fig.add_trace(
            go.Scatter(
                x=drawdown.index,
                y=drawdown,
                mode='lines',
                name='ドローダウン',
                line=dict(color='red', width=2),
                fill='tonexty',
                fillcolor='rgba(255, 0, 0, 0.3)'
            )
        )
        
        fig.update_layout(
            title="ドローダウン分析",
            height=300,
            xaxis_title="日付",
            yaxis_title="ドローダウン (%)",
            plot_bgcolor='white',
            paper_bgcolor='white'
        )
        
        fig.update_yaxes(range=[drawdown.min() * 1.1, 0])
        
        return fig
    
    def create_volume_chart(self, df: pd.DataFrame) -> go.Figure:
        """
        出来高チャートを作成
        
        Args:
            df: 株価データ
            
        Returns:
            go.Figure: Plotlyフィギュア
        """
        fig = go.Figure()
        
        # 出来高バー
        colors = ['green' if close >= open_price else 'red' 
                 for close, open_price in zip(df['Close'], df['Open'])]
        
        fig.add_trace(
            go.Bar(
                x=df.index,
                y=df['Volume'],
                name='出来高',
                marker_color=colors,
                opacity=0.7
            )
        )
        
        # 出来高移動平均
        if 'Volume_MA' in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df['Volume_MA'],
                    name='出来高平均',
                    line=dict(color='orange', width=2)
                )
            )
        
        fig.update_layout(
            title="出来高分析",
            height=300,
            xaxis_title="日付",
            yaxis_title="出来高",
            plot_bgcolor='white',
            paper_bgcolor='white'
        )
        
        return fig
    
    def display_chart_with_controls(self, fig: go.Figure, chart_key: str):
        """
        チャートをコントロール付きで表示
        
        Args:
            fig: Plotlyフィギュア
            chart_key: チャートの識別キー
        """
        # チャート表示
        st.plotly_chart(fig, use_container_width=True, key=f"chart_{chart_key}")
        
        # チャートコントロール
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📥 チャートをダウンロード", key=f"download_{chart_key}"):
                st.info("チャート上で右クリック → 'Download plot as a png' を選択してください")
        
        with col2:
            zoom_options = ["全期間", "直近30日", "直近90日"]
            selected_zoom = st.selectbox("🔍 表示期間", zoom_options, key=f"zoom_{chart_key}")
            
            if selected_zoom != "全期間":
                days = 30 if selected_zoom == "直近30日" else 90
                st.info(f"直近{days}日間にズームしてください（チャート上でドラッグ）")
        
        with col3:
            if st.button("🔄 チャートをリセット", key=f"reset_{chart_key}"):
                st.rerun()
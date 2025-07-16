# analysis/backtest.py
"""
バックテスト機能
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any
from datetime import datetime

from config.settings import BACKTEST_DEFAULTS, PERFORMANCE_CRITERIA


class BacktestEngine:
    """バックテストエンジンクラス"""
    
    def __init__(self):
        self.trade_log = []
        self.performance_metrics = {}
    
    def backtest_realistic(self, df: pd.DataFrame, signals: pd.DataFrame, **params) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        リアリスティックバックテスト実行
        
        Args:
            df: 株価データ
            signals: シグナルデータ
            **params: バックテストパラメータ
            
        Returns:
            Tuple[DataFrame, DataFrame]: ポートフォリオ価値推移と取引ログ
        """
        # パラメータ設定
        initial_capital = params.get('initial_capital', BACKTEST_DEFAULTS['initial_capital'])
        risk_pct = params.get('risk_per_trade', BACKTEST_DEFAULTS['risk_per_trade'])
        stop_loss_pct = params.get('stop_loss_pct', BACKTEST_DEFAULTS['stop_loss_pct'])
        take_profit_pct = params.get('take_profit_pct', BACKTEST_DEFAULTS['take_profit_pct'])
        cost_pct = params.get('trade_cost_rate', BACKTEST_DEFAULTS['trade_cost_rate'])
        
        # 初期化
        cash = initial_capital
        position = 0
        entry_price = 0
        portfolio_values = []
        trade_log = []
        
        cost_rate = cost_pct / 100.0
        
        # バックテスト実行
        for i in range(len(df)):
            current_price = df['Close'].iloc[i]
            signal = signals['signal'].iloc[i]
            current_date = df.index[i]
            
            # ポジション保有中の処理
            if position > 0:
                stop_loss_price = entry_price * (1 - stop_loss_pct / 100.0)
                take_profit_price = entry_price * (1 + take_profit_pct / 100.0)
                
                # 損切り・利益確定・売りシグナルによる決済
                should_exit = (
                    current_price <= stop_loss_price or 
                    current_price >= take_profit_price or 
                    signal == -1
                )
                
                if should_exit:
                    # 決済処理
                    revenue = position * current_price * (1 - cost_rate)
                    cash += revenue
                    
                    # 取引ログ記録
                    exit_reason = self._get_exit_reason(
                        current_price, stop_loss_price, take_profit_price, signal
                    )
                    
                    trade_log.append({
                        'Date': current_date,
                        'Type': 'Sell',
                        'Price': current_price,
                        'Shares': position,
                        'Portfolio': cash,
                        'Entry_Price': entry_price,
                        'PnL': revenue - (position * entry_price * (1 + cost_rate)),
                        'Exit_Reason': exit_reason
                    })
                    
                    position = 0
                    entry_price = 0
            
            # 新規買いシグナルの処理
            if position == 0 and signal == 1:
                # リスクベースポジションサイジング
                risk_per_share = current_price - (current_price * (1 - stop_loss_pct / 100.0))
                
                if risk_per_share > 0:
                    capital_at_risk = cash * (risk_pct / 100.0)
                    shares_to_buy = int(capital_at_risk / risk_per_share)
                    cost = shares_to_buy * current_price * (1 + cost_rate)
                    
                    if shares_to_buy > 0 and cash >= cost:
                        position = shares_to_buy
                        entry_price = current_price
                        cash -= cost
                        
                        # 取引ログ記録
                        trade_log.append({
                            'Date': current_date,
                            'Type': 'Buy',
                            'Price': current_price,
                            'Shares': position,
                            'Portfolio': cash + position * current_price,
                            'Entry_Price': entry_price,
                            'PnL': 0,
                            'Exit_Reason': 'Entry'
                        })
            
            # ポートフォリオ価値計算
            portfolio_value = cash + (position * current_price)
            portfolio_values.append(portfolio_value)
        
        # 結果をDataFrameに変換
        portfolio_df = pd.DataFrame({'Total': portfolio_values}, index=df.index)
        portfolio_df['Returns'] = portfolio_df['Total'].pct_change()
        
        trade_df = pd.DataFrame(trade_log) if trade_log else pd.DataFrame()
        
        # パフォーマンス指標計算
        self.performance_metrics = self._calculate_performance_metrics(
            portfolio_df, initial_capital, trade_df
        )
        
        return portfolio_df, trade_df
    
    def _get_exit_reason(self, current_price: float, stop_loss: float, 
                        take_profit: float, signal: int) -> str:
        """決済理由を取得"""
        if current_price <= stop_loss:
            return 'Stop Loss'
        elif current_price >= take_profit:
            return 'Take Profit'
        elif signal == -1:
            return 'Sell Signal'
        else:
            return 'Other'
    
    def _calculate_performance_metrics(self, portfolio_df: pd.DataFrame, 
                                     initial_capital: float, trade_df: pd.DataFrame) -> Dict[str, Any]:
        """パフォーマンス指標を計算"""
        if portfolio_df.empty:
            return {}
        
        final_value = portfolio_df['Total'].iloc[-1]
        total_return = (final_value / initial_capital - 1) * 100
        
        returns = portfolio_df['Returns'].dropna()
        
        metrics = {
            'initial_capital': initial_capital,
            'final_value': final_value,
            'total_return_pct': total_return,
            'total_return_abs': final_value - initial_capital,
        }
        
        # リターン関連指標
        if len(returns) > 0:
            metrics.update({
                'volatility': returns.std() * np.sqrt(252) * 100,  # 年率ボラティリティ
                'sharpe_ratio': (returns.mean() / returns.std()) * np.sqrt(252) if returns.std() > 0 else 0,
                'max_drawdown': self._calculate_max_drawdown(portfolio_df),
                'best_day': returns.max() * 100,
                'worst_day': returns.min() * 100,
            })
        
        # 取引関連指標
        if not trade_df.empty:
            completed_trades = trade_df[trade_df['Type'] == 'Sell']
            if not completed_trades.empty:
                winning_trades = completed_trades[completed_trades['PnL'] > 0]
                
                metrics.update({
                    'total_trades': len(completed_trades),
                    'winning_trades': len(winning_trades),
                    'losing_trades': len(completed_trades) - len(winning_trades),
                    'win_rate': len(winning_trades) / len(completed_trades) * 100,
                    'avg_win': winning_trades['PnL'].mean() if len(winning_trades) > 0 else 0,
                    'avg_loss': completed_trades[completed_trades['PnL'] <= 0]['PnL'].mean() if len(completed_trades[completed_trades['PnL'] <= 0]) > 0 else 0,
                    'profit_factor': abs(winning_trades['PnL'].sum() / completed_trades[completed_trades['PnL'] <= 0]['PnL'].sum()) if len(completed_trades[completed_trades['PnL'] <= 0]) > 0 and completed_trades[completed_trades['PnL'] <= 0]['PnL'].sum() != 0 else float('inf'),
                })
        
        return metrics
    
    def _calculate_max_drawdown(self, portfolio_df: pd.DataFrame) -> float:
        """最大ドローダウンを計算"""
        portfolio_values = portfolio_df['Total']
        peak = portfolio_values.expanding().max()
        drawdown = (portfolio_values / peak - 1) * 100
        return drawdown.min()
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """パフォーマンスサマリーを取得"""
        if not self.performance_metrics:
            return {}
        
        metrics = self.performance_metrics
        
        # パフォーマンス評価
        total_return = metrics.get('total_return_pct', 0)
        sharpe_ratio = metrics.get('sharpe_ratio', 0)
        
        if total_return > PERFORMANCE_CRITERIA['excellent']:
            performance_grade = '🎉 優秀'
            performance_comment = '素晴らしい成績です！'
        elif total_return > PERFORMANCE_CRITERIA['good']:
            performance_grade = '👍 良好'
            performance_comment = 'まずまずの成績です'
        else:
            performance_grade = '📚 要改善'
            performance_comment = '改善が必要です'
        
        return {
            'performance_grade': performance_grade,
            'performance_comment': performance_comment,
            'metrics': metrics,
            'risk_adjusted_return': sharpe_ratio > PERFORMANCE_CRITERIA['sharpe_good']
        }
    
    def analyze_trades(self, trade_df: pd.DataFrame) -> Dict[str, Any]:
        """取引分析を実行"""
        if trade_df.empty:
            return {}
        
        completed_trades = trade_df[trade_df['Type'] == 'Sell']
        
        if completed_trades.empty:
            return {'message': '完了した取引がありません'}
        
        analysis = {
            'exit_reasons': completed_trades['Exit_Reason'].value_counts().to_dict(),
            'monthly_performance': self._analyze_monthly_performance(completed_trades),
            'trade_duration': self._analyze_trade_duration(trade_df),
            'position_size_analysis': self._analyze_position_sizes(completed_trades)
        }
        
        return analysis
    
    def _analyze_monthly_performance(self, completed_trades: pd.DataFrame) -> Dict[str, float]:
        """月次パフォーマンス分析"""
        if completed_trades.empty:
            return {}
        
        completed_trades['Month'] = pd.to_datetime(completed_trades['Date']).dt.to_period('M')
        monthly_pnl = completed_trades.groupby('Month')['PnL'].sum()
        
        return {
            'best_month': monthly_pnl.max(),
            'worst_month': monthly_pnl.min(),
            'avg_monthly': monthly_pnl.mean(),
            'monthly_consistency': (monthly_pnl > 0).sum() / len(monthly_pnl) * 100 if len(monthly_pnl) > 0 else 0
        }
    
    def _analyze_trade_duration(self, trade_df: pd.DataFrame) -> Dict[str, Any]:
        """取引期間分析"""
        if trade_df.empty:
            return {}
        
        # 買いと売りをペアリング
        buy_trades = trade_df[trade_df['Type'] == 'Buy'].copy()
        sell_trades = trade_df[trade_df['Type'] == 'Sell'].copy()
        
        if buy_trades.empty or sell_trades.empty:
            return {}
        
        durations = []
        for _, sell_trade in sell_trades.iterrows():
            # 対応する買い取引を見つける（直前の買い取引）
            corresponding_buys = buy_trades[buy_trades['Date'] < sell_trade['Date']]
            if not corresponding_buys.empty:
                last_buy = corresponding_buys.iloc[-1]
                duration = (sell_trade['Date'] - last_buy['Date']).days
                durations.append(duration)
        
        if durations:
            return {
                'avg_duration_days': np.mean(durations),
                'min_duration_days': min(durations),
                'max_duration_days': max(durations),
                'median_duration_days': np.median(durations)
            }
        
        return {}
    
    def _analyze_position_sizes(self, completed_trades: pd.DataFrame) -> Dict[str, Any]:
        """ポジションサイズ分析"""
        if completed_trades.empty:
            return {}
        
        position_values = completed_trades['Shares'] * completed_trades['Entry_Price']
        
        return {
            'avg_position_value': position_values.mean(),
            'min_position_value': position_values.min(),
            'max_position_value': position_values.max(),
            'position_value_std': position_values.std()
        }
    
    def compare_with_benchmark(self, portfolio_df: pd.DataFrame, 
                             benchmark_returns: pd.Series) -> Dict[str, Any]:
        """ベンチマークとの比較"""
        if portfolio_df.empty or benchmark_returns.empty:
            return {}
        
        portfolio_returns = portfolio_df['Returns'].dropna()
        
        # 期間を合わせる
        common_dates = portfolio_returns.index.intersection(benchmark_returns.index)
        if len(common_dates) == 0:
            return {}
        
        portfolio_aligned = portfolio_returns.loc[common_dates]
        benchmark_aligned = benchmark_returns.loc[common_dates]
        
        # 累積リターン比較
        portfolio_cumret = (1 + portfolio_aligned).cumprod().iloc[-1] - 1
        benchmark_cumret = (1 + benchmark_aligned).cumprod().iloc[-1] - 1
        
        # 相関係数
        correlation = portfolio_aligned.corr(benchmark_aligned)
        
        # ベータ値
        beta = portfolio_aligned.cov(benchmark_aligned) / benchmark_aligned.var() if benchmark_aligned.var() > 0 else 0
        
        # アルファ値（CAPM）
        risk_free_rate = 0.01 / 252  # 仮定：年率1%のリスクフリーレート
        alpha = portfolio_aligned.mean() - (risk_free_rate + beta * (benchmark_aligned.mean() - risk_free_rate))
        
        return {
            'portfolio_return': portfolio_cumret * 100,
            'benchmark_return': benchmark_cumret * 100,
            'excess_return': (portfolio_cumret - benchmark_cumret) * 100,
            'correlation': correlation,
            'beta': beta,
            'alpha_daily': alpha,
            'information_ratio': (portfolio_aligned - benchmark_aligned).mean() / (portfolio_aligned - benchmark_aligned).std() if (portfolio_aligned - benchmark_aligned).std() > 0 else 0
        }
    
    def generate_backtest_report(self, portfolio_df: pd.DataFrame, 
                               trade_df: pd.DataFrame) -> str:
        """バックテストレポートを生成"""
        performance = self.get_performance_summary()
        trade_analysis = self.analyze_trades(trade_df)
        
        report = f"""
        📊 バックテストレポート
        ========================
        
        🎯 総合評価: {performance.get('performance_grade', 'N/A')}
        💬 コメント: {performance.get('performance_comment', 'N/A')}
        
        📈 基本指標:
        - 初期資金: ¥{performance['metrics'].get('initial_capital', 0):,.0f}
        - 最終資産: ¥{performance['metrics'].get('final_value', 0):,.0f}
        - 総リターン: {performance['metrics'].get('total_return_pct', 0):.2f}%
        - シャープレシオ: {performance['metrics'].get('sharpe_ratio', 0):.2f}
        - 最大ドローダウン: {performance['metrics'].get('max_drawdown', 0):.2f}%
        
        🔄 取引統計:
        - 総取引数: {performance['metrics'].get('total_trades', 0)}回
        - 勝率: {performance['metrics'].get('win_rate', 0):.1f}%
        - 平均利益: ¥{performance['metrics'].get('avg_win', 0):.0f}
        - 平均損失: ¥{performance['metrics'].get('avg_loss', 0):.0f}
        """
        
        return report
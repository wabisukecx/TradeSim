import 'dart:math';
import '../models/analysis_result.dart';
import '../models/backtest_result.dart';
import '../models/performance_metrics.dart';
import '../models/portfolio_value.dart';
import '../models/trade_record.dart';

/// バックテストエンジン (analysis/backtest.py の移植)
class BacktestEngine {
  static const double _defaultInitialCapital = 1000000;
  static const double _defaultRiskPerTrade = 2.0;
  static const double _defaultStopLossPct = 5.0;
  static const double _defaultTakeProfitPct = 10.0;
  static const double _defaultTradeCostRate = 0.1;

  BacktestResult run(
    AnalysisResult analysis, {
    double initialCapital = _defaultInitialCapital,
    double riskPerTrade = _defaultRiskPerTrade,
    double stopLossPct = _defaultStopLossPct,
    double takeProfitPct = _defaultTakeProfitPct,
    double tradeCostRate = _defaultTradeCostRate,
  }) {
    final candles = analysis.candles;
    final signals = analysis.signals;
    final n = candles.length;

    double cash = initialCapital;
    int position = 0;
    double entryPrice = 0;
    final portfolioValues = <PortfolioValue>[];
    final trades = <TradeRecord>[];

    final costRate = tradeCostRate / 100.0;

    for (int i = 0; i < n; i++) {
      final currentPrice = candles[i].close;
      final signal = signals[i];
      final date = candles[i].date;

      // ポジション保有中の処理
      if (position > 0) {
        final stopLossPrice = entryPrice * (1 - stopLossPct / 100.0);
        final takeProfitPrice = entryPrice * (1 + takeProfitPct / 100.0);

        final shouldExit = currentPrice <= stopLossPrice ||
            currentPrice >= takeProfitPrice ||
            signal == -1;

        if (shouldExit) {
          final revenue = position * currentPrice * (1 - costRate);
          cash += revenue;

          final exitReason =
              _getExitReason(currentPrice, stopLossPrice, takeProfitPrice, signal);
          final pnl =
              revenue - (position * entryPrice * (1 + costRate));

          trades.add(TradeRecord(
            date: date,
            type: 'Sell',
            price: currentPrice,
            shares: position,
            pnl: pnl,
            exitReason: exitReason,
          ));

          position = 0;
          entryPrice = 0;
        }
      }

      // 新規買いシグナル
      if (position == 0 && signal == 1) {
        final riskPerShare =
            currentPrice - currentPrice * (1 - stopLossPct / 100.0);
        if (riskPerShare > 0) {
          final capitalAtRisk = cash * (riskPerTrade / 100.0);
          final sharesToBuy = (capitalAtRisk / riskPerShare).floor();
          final cost = sharesToBuy * currentPrice * (1 + costRate);

          if (sharesToBuy > 0 && cash >= cost) {
            position = sharesToBuy;
            entryPrice = currentPrice;
            cash -= cost;

            trades.add(TradeRecord(
              date: date,
              type: 'Buy',
              price: currentPrice,
              shares: position,
              pnl: 0,
              exitReason: 'Entry',
            ));
          }
          // 株価が高額すぎてリスクベースサイジングで1株も買えないケース。
          // sharesToBuy == 0 は計算上は正常だが取引が発生しないため、
          // UI 側で「初期資金不足」として案内する（_zeroSharesOccurred フラグ相当）。
        }
      }

      portfolioValues.add(PortfolioValue(
        date: date,
        total: cash + position * currentPrice,
      ));
    }

    final metrics = _calculateMetrics(
      portfolioValues,
      trades,
      initialCapital,
    );

    return BacktestResult(
      portfolioValues: portfolioValues,
      trades: trades,
      metrics: metrics,
    );
  }

  String _getExitReason(
    double currentPrice,
    double stopLoss,
    double takeProfit,
    int signal,
  ) {
    if (currentPrice <= stopLoss) return 'Stop Loss';
    if (currentPrice >= takeProfit) return 'Take Profit';
    if (signal == -1) return 'Sell Signal';
    return 'Other';
  }

  PerformanceMetrics _calculateMetrics(
    List<PortfolioValue> portfolioValues,
    List<TradeRecord> trades,
    double initialCapital,
  ) {
    if (portfolioValues.isEmpty) return PerformanceMetrics.empty();

    final finalValue = portfolioValues.last.total;
    final totalReturnPct = (finalValue / initialCapital - 1) * 100;

    // 日次リターン計算
    final returns = <double>[];
    for (int i = 1; i < portfolioValues.length; i++) {
      final prev = portfolioValues[i - 1].total;
      if (prev != 0) {
        returns.add((portfolioValues[i].total - prev) / prev);
      }
    }

    // シャープレシオ: (meanReturn / stdReturn) * sqrt(252)
    // 分散は標本分散（N-1除算）を使用 - Python版と同じ金融計算標準
    double sharpeRatio = 0;
    if (returns.length > 1) {
      final mean = returns.reduce((a, b) => a + b) / returns.length;
      final variance =
          returns.map((r) => (r - mean) * (r - mean)).reduce((a, b) => a + b) /
              (returns.length - 1); // N-1除算（標本分散）
      final std = sqrt(variance);
      if (std > 0) {
        sharpeRatio = (mean / std) * sqrt(252);
      }
    }

    // 最大ドローダウン
    final maxDrawdown = _calcMaxDrawdown(portfolioValues);

    // 勝率と取引数
    final sellTrades = trades.where((t) => t.type == 'Sell').toList();
    final winTrades = sellTrades.where((t) => t.pnl > 0).length;
    final winRate =
        sellTrades.isNotEmpty ? winTrades / sellTrades.length * 100 : 0.0;

    return PerformanceMetrics(
      totalReturnPct: totalReturnPct,
      sharpeRatio: sharpeRatio,
      maxDrawdown: maxDrawdown,
      winRate: winRate,
      totalTrades: sellTrades.length,
      initialCapital: initialCapital,
      finalValue: finalValue,
    );
  }

  double _calcMaxDrawdown(List<PortfolioValue> values) {
    double peak = values.first.total;
    double maxDD = 0;
    for (final pv in values) {
      if (pv.total > peak) peak = pv.total;
      final dd = (pv.total / peak - 1) * 100;
      if (dd < maxDD) maxDD = dd;
    }
    return maxDD;
  }
}

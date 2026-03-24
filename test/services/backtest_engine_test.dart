// T4: BacktestEngine テスト
import 'package:flutter_test/flutter_test.dart';
import 'package:trade_sim_flutter/models/analysis_result.dart';
import 'package:trade_sim_flutter/models/stock_candle.dart';
import 'package:trade_sim_flutter/services/backtest_engine.dart';

void main() {
  group('T4: BacktestEngine', () {
    /// 買い1回・売り1回のシンプルなシナリオを構築する。
    /// 日付0: signal=1 (買い), price=100
    /// 日付1〜9: signal=0 (ホールド)
    /// 日付10: signal=-1 (売り), price=110
    AnalysisResult _buildSimpleAnalysis() {
      const n = 11;
      final base = DateTime(2024, 1, 1);
      final candles = List.generate(
        n,
        (i) => StockCandle(
          date: base.add(Duration(days: i)),
          open: 100 + i.toDouble(),
          high: 105 + i.toDouble(),
          low: 95 + i.toDouble(),
          close: 100 + i.toDouble(), // 線形上昇
          volume: 100000,
        ),
      );

      final signals = List.filled(n, 0);
      signals[0] = 1;  // 買いシグナル
      signals[10] = -1; // 売りシグナル

      final nullList = List<double?>.filled(n, null);

      return AnalysisResult(
        candles: candles,
        maShort: nullList,
        maLong: nullList,
        rsi: nullList,
        bbUpper: nullList,
        bbMiddle: nullList,
        bbLower: nullList,
        macd: nullList,
        macdSignal: nullList,
        signals: signals,
      );
    }

    test('買い1回・売り1回で TradeRecord が Buy + Sell の2件生成される', () {
      final analysis = _buildSimpleAnalysis();
      final engine = BacktestEngine();
      final result = engine.run(
        analysis,
        initialCapital: 1000000,
        riskPerTrade: 2.0,
        stopLossPct: 5.0,
        takeProfitPct: 20.0, // 10 step では take profit に届かない
        tradeCostRate: 0.1,
      );

      final buyCount = result.trades.where((t) => t.type == 'Buy').length;
      final sellCount = result.trades.where((t) => t.type == 'Sell').length;
      expect(buyCount, equals(1));
      expect(sellCount, equals(1));
    });

    test('PnL 計算が Python 版と誤差 0.01% 以内', () {
      final analysis = _buildSimpleAnalysis();
      final engine = BacktestEngine();
      const initialCapital = 1000000.0;
      const riskPerTrade = 2.0;
      const stopLossPct = 5.0;
      const takeProfitPct = 20.0;
      const tradeCostRate = 0.1;

      final result = engine.run(
        analysis,
        initialCapital: initialCapital,
        riskPerTrade: riskPerTrade,
        stopLossPct: stopLossPct,
        takeProfitPct: takeProfitPct,
        tradeCostRate: tradeCostRate,
      );

      // Python版と同一計算式を Dart で再現:
      // entryPrice = 100 (index=0)
      // riskPerShare = 100 * stopLoss/100 = 5.0
      // capitalAtRisk = 1000000 * 2/100 = 20000
      // shares = floor(20000 / 5.0) = 4000
      // buyCost = 4000 * 100 * 1.001 = 400400
      // sellRevenue = 4000 * 110 * 0.999 = 439560
      // pnl = sellRevenue - buyCost = 39160
      const expectedPnl = 39160.0;

      final sellTrade = result.trades.firstWhere((t) => t.type == 'Sell');
      final tolerance = expectedPnl.abs() * 0.0001;
      expect(sellTrade.pnl, closeTo(expectedPnl, tolerance.clamp(1.0, 100.0)));
    });

    test('portfolioValues の長さが candles の長さと一致する', () {
      final analysis = _buildSimpleAnalysis();
      final result = BacktestEngine().run(analysis);
      expect(result.portfolioValues.length, analysis.candles.length);
    });

    test('PerformanceMetrics が計算される', () {
      final analysis = _buildSimpleAnalysis();
      final result = BacktestEngine().run(analysis);
      expect(result.metrics.initialCapital, equals(1000000.0));
      expect(result.metrics.totalTrades, greaterThanOrEqualTo(0));
    });
  });
}

import 'portfolio_value.dart';
import 'trade_record.dart';
import 'performance_metrics.dart';

class BacktestResult {
  final List<PortfolioValue> portfolioValues;
  final List<TradeRecord> trades;
  final PerformanceMetrics metrics;

  const BacktestResult({
    required this.portfolioValues,
    required this.trades,
    required this.metrics,
  });
}

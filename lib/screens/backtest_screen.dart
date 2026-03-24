import 'package:fl_chart/fl_chart.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';

import '../models/backtest_result.dart';
import '../models/performance_metrics.dart';
import '../models/portfolio_value.dart';
import '../providers/providers.dart';

class BacktestScreen extends ConsumerWidget {
  final String symbol;
  final String range;

  const BacktestScreen({
    super.key,
    required this.symbol,
    required this.range,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final analysisParams = AnalysisParams(symbol: symbol, range: range);
    final backtestParams = const BacktestParams();
    final familyParam = (
      analysisParams: analysisParams,
      backtestParams: backtestParams,
    );

    final backtestAsync = ref.watch(backtestNotifierProvider(familyParam));

    return Scaffold(
      appBar: AppBar(title: Text('$symbol バックテスト')),
      body: backtestAsync.when(
        loading: () => const Center(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              CircularProgressIndicator(),
              SizedBox(height: 16),
              Text('バックテスト実行中...'),
            ],
          ),
        ),
        error: (e, _) => Center(
          child: Padding(
            padding: const EdgeInsets.all(24),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                const Icon(Icons.error_outline, color: Colors.red, size: 48),
                const SizedBox(height: 16),
                Text('エラー: $e',
                    textAlign: TextAlign.center,
                    style: const TextStyle(color: Colors.red)),
                const SizedBox(height: 16),
                FilledButton(
                  onPressed: () =>
                      ref.invalidate(backtestNotifierProvider(familyParam)),
                  child: const Text('再試行'),
                ),
              ],
            ),
          ),
        ),
        data: (result) => _BacktestBody(result: result, symbol: symbol),
      ),
    );
  }
}

class _BacktestBody extends StatelessWidget {
  final BacktestResult result;
  final String symbol;

  const _BacktestBody({required this.result, required this.symbol});

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          _PerformanceCard(metrics: result.metrics),
          const SizedBox(height: 16),
          _PortfolioChart(portfolioValues: result.portfolioValues),
          const SizedBox(height: 16),
          _TradeStats(result: result),
          const SizedBox(height: 24),
        ],
      ),
    );
  }
}

// ===== パフォーマンスカード =====
class _PerformanceCard extends StatelessWidget {
  final PerformanceMetrics metrics;
  const _PerformanceCard({required this.metrics});

  Color _returnColor(double v) =>
      v >= 0 ? Colors.green : Colors.red;

  @override
  Widget build(BuildContext context) {
    final fmt = NumberFormat('#,##0.00');

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('パフォーマンス指標',
                style: Theme.of(context).textTheme.titleMedium),
            const SizedBox(height: 12),
            _MetricRow(
              label: '総リターン',
              value: '${fmt.format(metrics.totalReturnPct)}%',
              valueColor: _returnColor(metrics.totalReturnPct),
            ),
            _MetricRow(
              label: 'シャープレシオ ⓘ',
              value: fmt.format(metrics.sharpeRatio),
              tooltip: 'リスクフリーレート=0として計算（簡易版）',
            ),
            _MetricRow(
              label: '最大ドローダウン',
              value: '${fmt.format(metrics.maxDrawdown)}%',
              valueColor: Colors.red,
            ),
            _MetricRow(
              label: '勝率',
              value: '${fmt.format(metrics.winRate)}%',
            ),
            _MetricRow(
              label: '総取引数',
              value: '${metrics.totalTrades}回',
            ),
            const Divider(),
            _MetricRow(
              label: '初期資金',
              value: '¥${NumberFormat('#,##0').format(metrics.initialCapital)}',
            ),
            _MetricRow(
              label: '最終資産',
              value: '¥${NumberFormat('#,##0').format(metrics.finalValue)}',
              valueColor: _returnColor(
                  metrics.finalValue - metrics.initialCapital),
            ),
          ],
        ),
      ),
    );
  }
}

class _MetricRow extends StatelessWidget {
  final String label;
  final String value;
  final Color? valueColor;
  final String? tooltip;

  const _MetricRow({
    required this.label,
    required this.value,
    this.valueColor,
    this.tooltip,
  });

  @override
  Widget build(BuildContext context) {
    Widget labelWidget = Text(label, style: const TextStyle(color: Colors.grey));
    if (tooltip != null) {
      labelWidget = Tooltip(
        message: tooltip!,
        child: labelWidget,
      );
    }
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          labelWidget,
          Text(
            value,
            style: TextStyle(
              fontWeight: FontWeight.bold,
              color: valueColor,
            ),
          ),
        ],
      ),
    );
  }
}

// ===== ポートフォリオ推移グラフ =====
class _PortfolioChart extends StatelessWidget {
  final List<PortfolioValue> portfolioValues;
  const _PortfolioChart({required this.portfolioValues});

  @override
  Widget build(BuildContext context) {
    if (portfolioValues.isEmpty) return const SizedBox();

    final spots = <FlSpot>[];
    for (int i = 0; i < portfolioValues.length; i++) {
      spots.add(FlSpot(i.toDouble(), portfolioValues[i].total));
    }

    final minY = portfolioValues
        .map((v) => v.total)
        .reduce((a, b) => a < b ? a : b)
        .toDouble();
    final maxY = portfolioValues
        .map((v) => v.total)
        .reduce((a, b) => a > b ? a : b)
        .toDouble();

    final yPad = (maxY - minY) * 0.05;

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('ポートフォリオ推移',
                style: Theme.of(context).textTheme.titleMedium),
            const SizedBox(height: 16),
            SizedBox(
              height: 200,
              child: LineChart(
                LineChartData(
                  minY: minY - yPad,
                  maxY: maxY + yPad,
                  gridData: const FlGridData(show: true),
                  borderData: FlBorderData(show: true),
                  titlesData: FlTitlesData(
                    leftTitles: AxisTitles(
                      sideTitles: SideTitles(
                        showTitles: true,
                        getTitlesWidget: (v, _) => Text(
                          '${(v / 10000).toStringAsFixed(0)}万',
                          style: const TextStyle(fontSize: 9),
                        ),
                        reservedSize: 40,
                      ),
                    ),
                    bottomTitles: const AxisTitles(
                        sideTitles: SideTitles(showTitles: false)),
                    topTitles: const AxisTitles(
                        sideTitles: SideTitles(showTitles: false)),
                    rightTitles: const AxisTitles(
                        sideTitles: SideTitles(showTitles: false)),
                  ),
                  lineBarsData: [
                    LineChartBarData(
                      spots: spots,
                      isCurved: true,
                      color: const Color(0xFF1565C0),
                      barWidth: 2,
                      dotData: const FlDotData(show: false),
                      belowBarData: BarAreaData(
                        show: true,
                        color: const Color(0xFF1565C0).withValues(alpha: 0.1),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

// ===== 取引統計 =====
class _TradeStats extends StatelessWidget {
  final BacktestResult result;
  const _TradeStats({required this.result});

  @override
  Widget build(BuildContext context) {
    final sells = result.trades.where((t) => t.type == 'Sell').toList();
    if (sells.isEmpty) {
      return const Card(
        child: Padding(
          padding: EdgeInsets.all(16),
          child: Column(children: [
            Icon(Icons.info_outline, color: Colors.orange),
            SizedBox(height: 8),
            Text('売買取引が発生しませんでした',
                style: TextStyle(fontWeight: FontWeight.bold)),
            SizedBox(height: 4),
            Text(
              '株価に対して初期資金が少ない場合、リスクベースの\nポジションサイジングで1株も購入できないことがあります。\n分析期間を短くするか、別の銘柄で試してください。',
              textAlign: TextAlign.center,
              style: TextStyle(fontSize: 12, color: Colors.grey),
            ),
          ]),
        ),
      );
    }

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('取引一覧 (直近20件)',
                style: Theme.of(context).textTheme.titleMedium),
            const SizedBox(height: 8),
            SingleChildScrollView(
              scrollDirection: Axis.horizontal,
              child: DataTable(
                columnSpacing: 12,
                headingRowHeight: 32,
                dataRowMinHeight: 28,
                dataRowMaxHeight: 36,
                columns: const [
                  DataColumn(label: Text('日付', style: TextStyle(fontSize: 11))),
                  DataColumn(label: Text('種別', style: TextStyle(fontSize: 11))),
                  DataColumn(label: Text('価格', style: TextStyle(fontSize: 11))),
                  DataColumn(label: Text('株数', style: TextStyle(fontSize: 11))),
                  DataColumn(label: Text('損益', style: TextStyle(fontSize: 11))),
                  DataColumn(
                      label: Text('決済理由', style: TextStyle(fontSize: 11))),
                ],
                rows: sells.reversed
                    .take(20)
                    .map((t) => DataRow(cells: [
                          DataCell(Text(
                              DateFormat('yy/MM/dd').format(t.date),
                              style: const TextStyle(fontSize: 11))),
                          DataCell(Text(t.type,
                              style: const TextStyle(fontSize: 11))),
                          DataCell(Text(
                              NumberFormat('#,##0').format(t.price),
                              style: const TextStyle(fontSize: 11))),
                          DataCell(Text(t.shares.toString(),
                              style: const TextStyle(fontSize: 11))),
                          DataCell(Text(
                            NumberFormat('#,##0').format(t.pnl),
                            style: TextStyle(
                              fontSize: 11,
                              color: t.pnl >= 0 ? Colors.green : Colors.red,
                              fontWeight: FontWeight.bold,
                            ),
                          )),
                          DataCell(Text(t.exitReason,
                              style: const TextStyle(fontSize: 11))),
                        ]))
                    .toList(),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

import 'package:candlesticks/candlesticks.dart';
import 'package:fl_chart/fl_chart.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:intl/intl.dart';

import '../models/analysis_result.dart';
import '../models/stock_candle.dart';
import '../providers/providers.dart';

class AnalysisScreen extends ConsumerWidget {
  final String symbol;
  final String range;

  const AnalysisScreen({
    super.key,
    required this.symbol,
    required this.range,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final params = AnalysisParams(symbol: symbol, range: range);
    final analysisAsync = ref.watch(analysisNotifierProvider(params));

    return Scaffold(
      appBar: AppBar(
        title: Text('$symbol 分析'),
        actions: [
          IconButton(
            icon: const Icon(Icons.bar_chart),
            tooltip: 'バックテスト',
            onPressed: () => context.push(
              '/backtest/$symbol',
              extra: {'range': range},
            ),
          ),
        ],
      ),
      body: analysisAsync.when(
        loading: () => const Center(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              CircularProgressIndicator(),
              SizedBox(height: 16),
              Text('データ取得・分析中...'),
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
                  onPressed: () => ref.invalidate(analysisNotifierProvider(params)),
                  child: const Text('再試行'),
                ),
              ],
            ),
          ),
        ),
        data: (result) => _AnalysisBody(
          symbol: symbol,
          range: range,
          result: result,
        ),
      ),
    );
  }
}

class _AnalysisBody extends StatelessWidget {
  final String symbol;
  final String range;
  final AnalysisResult result;

  const _AnalysisBody({
    required this.symbol,
    required this.range,
    required this.result,
  });

  @override
  Widget build(BuildContext context) {
    final candles = result.candles;
    if (candles.isEmpty) {
      return const Center(child: Text('データが取得できませんでした'));
    }
    final latestIdx = candles.length - 1;
    final latestSignal = result.signals.isNotEmpty ? result.signals.last : 0;

    return SingleChildScrollView(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          // シグナルバッジ
          _SignalBadge(signal: latestSignal),

          // パターン情報（動的重み付け結果）
          if (result.patternResult != null)
            _PatternInfoCard(pattern: result.patternResult!),

          // シグナル判断理由
          if (result.signalExplanation.isNotEmpty)
            _SignalReasonCard(reasons: result.signalExplanation),

          // 最新指標サマリ
          _MetricsSummary(result: result, idx: latestIdx),

          // ローソク足チャート
          _CandleChart(candles: candles),

          // RSIチャート
          _RsiChart(rsi: result.rsi, candles: candles),

          // MACDチャート
          _MacdChart(
            macd: result.macd,
            macdSignal: result.macdSignal,
            candles: candles,
          ),

          const SizedBox(height: 80),
        ],
      ),
    );
  }
}

// ===== シグナルバッジ =====
class _SignalBadge extends StatelessWidget {
  final int signal;
  const _SignalBadge({required this.signal});

  @override
  Widget build(BuildContext context) {
    final (label, color, icon) = switch (signal) {
      1 => ('買いシグナル', Colors.green, Icons.trending_up),
      -1 => ('売りシグナル', Colors.red, Icons.trending_down),
      _ => ('中立', Colors.grey, Icons.trending_flat),
    };

    return Padding(
      padding: const EdgeInsets.fromLTRB(16, 12, 16, 0),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        decoration: BoxDecoration(
          color: color.withValues(alpha: 0.1),
          border: Border.all(color: color),
          borderRadius: BorderRadius.circular(24),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(icon, color: color, size: 18),
            const SizedBox(width: 6),
            Text(
              '最新シグナル: $label',
              style: TextStyle(
                color: color,
                fontWeight: FontWeight.bold,
                fontSize: 14,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

// ===== 指標サマリ =====
class _MetricsSummary extends StatelessWidget {
  final AnalysisResult result;
  final int idx;
  const _MetricsSummary({required this.result, required this.idx});

  String _fmt(double? v) =>
      v != null ? NumberFormat('#,##0.00').format(v) : '---';

  @override
  Widget build(BuildContext context) {
    final items = [
      ('終値 (${result.currency})', _fmt(result.candles[idx].close), Icons.attach_money),
      ('RSI (14)', _fmt(result.rsi[idx]), Icons.show_chart),
      ('MA短期 (20)', _fmt(result.maShort[idx]), Icons.trending_up),
      ('MA長期 (50)', _fmt(result.maLong[idx]), Icons.trending_up),
      ('BB上限 (${result.currency})', _fmt(result.bbUpper[idx]), Icons.arrow_upward),
      ('BB下限 (${result.currency})', _fmt(result.bbLower[idx]), Icons.arrow_downward),
    ];

    return Padding(
      padding: const EdgeInsets.fromLTRB(16, 8, 16, 0),
      child: Card(
        elevation: 1,
        child: Padding(
          padding: const EdgeInsets.all(12),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text('最新指標', style: Theme.of(context).textTheme.titleSmall),
              const SizedBox(height: 8),
              GridView.count(
                crossAxisCount: 2,
                shrinkWrap: true,
                physics: const NeverScrollableScrollPhysics(),
                childAspectRatio: 2.4,
                mainAxisSpacing: 6,
                crossAxisSpacing: 8,
                children: items
                    .map((e) => _MetricTile(label: e.$1, value: e.$2, icon: e.$3))
                    .toList(),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _MetricTile extends StatelessWidget {
  final String label;
  final String value;
  final IconData icon;
  const _MetricTile({required this.label, required this.value, required this.icon});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: Colors.blue[50],
        borderRadius: BorderRadius.circular(8),
      ),
      child: Row(
        children: [
          Icon(icon, size: 16, color: Colors.blue[700]),
          const SizedBox(width: 6),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Text(label,
                    style: TextStyle(
                        fontSize: 11,
                        color: Colors.grey[600],
                        fontWeight: FontWeight.w500)),
                Text(value,
                    style: const TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.bold),
                    overflow: TextOverflow.ellipsis),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

// ===== ローソク足チャート =====
class _CandleChart extends StatelessWidget {
  final List<StockCandle> candles;
  const _CandleChart({required this.candles});

  @override
  Widget build(BuildContext context) {
    final candleData = candles
        .map((c) => Candle(
              date: c.date,
              high: c.high,
              low: c.low,
              open: c.open,
              close: c.close,
              volume: c.volume,
            ))
        .toList()
        .reversed
        .toList();

    return Padding(
      padding: const EdgeInsets.fromLTRB(16, 16, 16, 0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('株価チャート',
              style: Theme.of(context).textTheme.titleMedium),
          const SizedBox(height: 8),
          SizedBox(
            height: 300,
            child: Candlesticks(candles: candleData),
          ),
        ],
      ),
    );
  }
}

// ===== RSIチャート =====
class _RsiChart extends StatelessWidget {
  final List<double?> rsi;
  final List<StockCandle> candles;

  const _RsiChart({required this.rsi, required this.candles});

  @override
  Widget build(BuildContext context) {
    final spots = <FlSpot>[];
    for (int i = 0; i < rsi.length; i++) {
      final v = rsi[i];
      if (v != null) spots.add(FlSpot(i.toDouble(), v));
    }
    if (spots.isEmpty) return const SizedBox();

    return Padding(
      padding: const EdgeInsets.fromLTRB(16, 16, 16, 0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // タイトル + 凡例行
          Row(
            children: [
              Text('RSI (14)', style: Theme.of(context).textTheme.titleMedium),
              const Spacer(),
              Container(width: 16, height: 2, color: Colors.purple),
              const SizedBox(width: 4),
              const Text('RSI', style: TextStyle(fontSize: 11)),
              const SizedBox(width: 12),
              Container(width: 12, height: 2, color: Colors.green),
              const SizedBox(width: 4),
              const Text('売られすぎ(35)', style: TextStyle(fontSize: 11, color: Colors.green)),
              const SizedBox(width: 8),
              Container(width: 12, height: 2, color: Colors.red),
              const SizedBox(width: 4),
              const Text('買われすぎ(65)', style: TextStyle(fontSize: 11, color: Colors.red)),
            ],
          ),
          const SizedBox(height: 8),
          SizedBox(
            height: 200,
            child: LineChart(
              LineChartData(
                minY: 0,
                maxY: 100,
                gridData: const FlGridData(show: false),
                borderData: FlBorderData(show: true),
                titlesData: FlTitlesData(
                  leftTitles: AxisTitles(
                    sideTitles: SideTitles(
                      showTitles: true,
                      getTitlesWidget: (v, _) =>
                          Text(v.toInt().toString(),
                              style: const TextStyle(fontSize: 10)),
                      reservedSize: 28,
                    ),
                  ),
                  bottomTitles:
                      const AxisTitles(sideTitles: SideTitles(showTitles: false)),
                  topTitles:
                      const AxisTitles(sideTitles: SideTitles(showTitles: false)),
                  rightTitles:
                      const AxisTitles(sideTitles: SideTitles(showTitles: false)),
                ),
                extraLinesData: ExtraLinesData(horizontalLines: [
                  HorizontalLine(y: 35, color: Colors.green, strokeWidth: 1,
                      dashArray: [4, 4]),
                  HorizontalLine(y: 65, color: Colors.red, strokeWidth: 1,
                      dashArray: [4, 4]),
                ]),
                lineTouchData: LineTouchData(
                  touchTooltipData: LineTouchTooltipData(
                    getTooltipColor: (_) => Colors.purple[900]!,
                    getTooltipItems: (spots) => spots.map((s) =>
                      LineTooltipItem(
                        'RSI: ${s.y.toStringAsFixed(1)}',
                        const TextStyle(
                          color: Colors.white,
                          fontWeight: FontWeight.bold,
                          fontSize: 12,
                        ),
                      ),
                    ).toList(),
                  ),
                ),
                lineBarsData: [
                  LineChartBarData(
                    spots: spots,
                    isCurved: true,
                    color: Colors.purple,
                    barWidth: 1.5,
                    dotData: const FlDotData(show: false),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}

// ===== パターン情報カード =====
class _PatternInfoCard extends StatelessWidget {
  final PatternResult pattern;
  const _PatternInfoCard({required this.pattern});

  Color get _riskColor => switch (pattern.riskLevel) {
    'high' => Colors.red,
    'low'  => Colors.green,
    _      => Colors.orange,
  };

  @override
  Widget build(BuildContext context) {
    final conf = (pattern.confidence * 100).toStringAsFixed(0);
    final w = pattern.weights;
    return Padding(
      padding: const EdgeInsets.fromLTRB(16, 12, 16, 0),
      child: Card(
        elevation: 1,
        child: Padding(
          padding: const EdgeInsets.all(12),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(children: [
                Icon(Icons.auto_graph, size: 18, color: _riskColor),
                const SizedBox(width: 6),
                Text(
                  '市場パターン: ${pattern.name}',
                  style: Theme.of(context).textTheme.titleSmall
                      ?.copyWith(fontWeight: FontWeight.bold),
                ),
                const Spacer(),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                  decoration: BoxDecoration(
                    color: _riskColor.withValues(alpha: 0.1),
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(color: _riskColor),
                  ),
                  child: Text(
                    '信頼度 $conf%',
                    style: TextStyle(fontSize: 11, color: _riskColor),
                  ),
                ),
              ]),
              const SizedBox(height: 6),
              Text(
                pattern.strategyHint,
                style: TextStyle(fontSize: 12, color: Colors.grey[700]),
              ),
              const SizedBox(height: 10),
              Text('重み付け', style: Theme.of(context).textTheme.labelSmall),
              const SizedBox(height: 4),
              _WeightBar(label: 'MA',   value: w.maTrend,   color: Colors.blue),
              _WeightBar(label: 'MACD', value: w.macd,      color: Colors.indigo),
              _WeightBar(label: 'RSI',  value: w.rsi,       color: Colors.purple),
              _WeightBar(label: 'BB',   value: w.bollinger, color: Colors.teal),
              _WeightBar(label: 'Vol',  value: w.volume,    color: Colors.orange),
            ],
          ),
        ),
      ),
    );
  }
}

class _WeightBar extends StatelessWidget {
  final String label;
  final double value;  // 0.0 ~ 0.5 程度
  final Color color;
  const _WeightBar({required this.label, required this.value, required this.color});

  @override
  Widget build(BuildContext context) {
    final pct = (value * 100).toStringAsFixed(0);
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 2),
      child: Row(children: [
        SizedBox(
          width: 32,
          child: Text(label, style: const TextStyle(fontSize: 11)),
        ),
        Expanded(
          child: ClipRRect(
            borderRadius: BorderRadius.circular(4),
            child: LinearProgressIndicator(
              value: value / 0.5, // 最大 0.5 を 100% とする
              backgroundColor: Colors.grey[200],
              color: color,
              minHeight: 8,
            ),
          ),
        ),
        const SizedBox(width: 6),
        Text('$pct%', style: const TextStyle(fontSize: 11)),
      ]),
    );
  }
}

// ===== シグナル理由カード =====
class _SignalReasonCard extends StatelessWidget {
  final List<String> reasons;
  const _SignalReasonCard({required this.reasons});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(16, 8, 16, 0),
      child: Card(
        elevation: 1,
        child: Padding(
          padding: const EdgeInsets.all(12),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(children: [
                const Icon(Icons.info_outline, size: 16, color: Colors.blue),
                const SizedBox(width: 6),
                Text('シグナル判断理由',
                    style: Theme.of(context).textTheme.titleSmall),
              ]),
              const SizedBox(height: 8),
              ...reasons.map((r) => Padding(
                padding: const EdgeInsets.symmetric(vertical: 2),
                child: Text(r, style: const TextStyle(fontSize: 12)),
              )),
            ],
          ),
        ),
      ),
    );
  }
}

// ===== MACDチャート =====
class _MacdChart extends StatelessWidget {
  final List<double?> macd;
  final List<double?> macdSignal;
  final List<StockCandle> candles;

  const _MacdChart({
    required this.macd,
    required this.macdSignal,
    required this.candles,
  });

  @override
  Widget build(BuildContext context) {
    final macdSpots = <FlSpot>[];
    final signalSpots = <FlSpot>[];

    for (int i = 0; i < macd.length; i++) {
      final m = macd[i];
      final s = macdSignal[i];
      if (m != null) macdSpots.add(FlSpot(i.toDouble(), m));
      if (s != null) signalSpots.add(FlSpot(i.toDouble(), s));
    }
    if (macdSpots.isEmpty) return const SizedBox();

    return Padding(
      padding: const EdgeInsets.fromLTRB(16, 16, 16, 0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // タイトル + 凡例行
          Row(
            children: [
              Text('MACD', style: Theme.of(context).textTheme.titleMedium),
              const Spacer(),
              Container(width: 16, height: 2, color: Colors.blue),
              const SizedBox(width: 4),
              const Text('MACD', style: TextStyle(fontSize: 11)),
              const SizedBox(width: 12),
              Row(
                children: [
                  Container(width: 6, height: 2, color: Colors.orange),
                  const SizedBox(width: 2),
                  Container(width: 6, height: 2, color: Colors.orange),
                  const SizedBox(width: 4),
                  const Text('シグナル', style: TextStyle(fontSize: 11)),
                ],
              ),
            ],
          ),
          const SizedBox(height: 8),
          SizedBox(
            height: 200,
            child: LineChart(
              LineChartData(
                gridData: const FlGridData(show: false),
                borderData: FlBorderData(show: true),
                titlesData: FlTitlesData(
                  leftTitles: AxisTitles(
                    sideTitles: SideTitles(
                      showTitles: true,
                      getTitlesWidget: (v, _) =>
                          Text(v.toStringAsFixed(0),
                              style: const TextStyle(fontSize: 9)),
                      reservedSize: 36,
                    ),
                  ),
                  bottomTitles:
                      const AxisTitles(sideTitles: SideTitles(showTitles: false)),
                  topTitles:
                      const AxisTitles(sideTitles: SideTitles(showTitles: false)),
                  rightTitles:
                      const AxisTitles(sideTitles: SideTitles(showTitles: false)),
                ),
                extraLinesData: ExtraLinesData(horizontalLines: [
                  HorizontalLine(y: 0, color: Colors.grey, strokeWidth: 1),
                ]),
                lineTouchData: LineTouchData(
                  touchTooltipData: LineTouchTooltipData(
                    getTooltipColor: (_) => Colors.blue[900]!,
                    getTooltipItems: (touchedSpots) {
                      return touchedSpots.map((s) {
                        final isSignal = s.barIndex == 1;
                        return LineTooltipItem(
                          '${isSignal ? 'Signal' : 'MACD'}: ${s.y.toStringAsFixed(2)}',
                          TextStyle(
                            color: isSignal ? Colors.orange[200] : Colors.white,
                            fontWeight: FontWeight.bold,
                            fontSize: 12,
                          ),
                        );
                      }).toList();
                    },
                  ),
                ),
                lineBarsData: [
                  LineChartBarData(
                    spots: macdSpots,
                    isCurved: false,
                    color: Colors.blue,
                    barWidth: 1.5,
                    dotData: const FlDotData(show: false),
                  ),
                  if (signalSpots.isNotEmpty)
                    LineChartBarData(
                      spots: signalSpots,
                      isCurved: false,
                      color: Colors.orange,
                      barWidth: 1.5,
                      dotData: const FlDotData(show: false),
                      dashArray: [4, 4],
                    ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}

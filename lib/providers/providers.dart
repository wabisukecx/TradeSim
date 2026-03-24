import 'dart:convert';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../models/analysis_result.dart';
import '../models/backtest_result.dart';
import '../models/portfolio_item.dart';
import '../repositories/jquants_repository.dart';
import '../repositories/stock_repository.dart' show StockRepository, StockData, StockRepositoryException;
import '../services/backtest_engine.dart';
import '../services/signal_generator.dart';
import '../services/technical_analyzer.dart';

// ===== SharedPreferences provider =====
final sharedPreferencesProvider = Provider<SharedPreferences>((ref) {
  throw UnimplementedError('SharedPreferences must be overridden');
});

// ===== Repositories =====

final stockRepositoryProvider = Provider<StockRepository>((ref) {
  return StockRepository();
});

/// JQuants API V2 リポジトリ (APIキー認証方式)
/// SharedPreferences を渡すことで銘柄マスターの TTL 1時間キャッシュが有効になる。
final jquantsRepositoryProvider = Provider<JQuantsRepository>((ref) {
  final prefs = ref.watch(sharedPreferencesProvider);
  return JQuantsRepository(prefs: prefs);
});

// ===== Analysis params =====

class AnalysisParams {
  final String symbol;
  final String range;
  final int shortMa;
  final int longMa;
  final String weightMode;            // 'fixed' | 'adaptive' | 'manual'
  final WeightProfile? manualWeights; // weightMode == 'manual' のときのみ使用

  const AnalysisParams({
    required this.symbol,
    required this.range,
    this.shortMa = 20,
    this.longMa  = 50,
    this.weightMode    = 'adaptive',
    this.manualWeights,
  });

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is AnalysisParams &&
          symbol        == other.symbol &&
          range         == other.range &&
          shortMa       == other.shortMa &&
          longMa        == other.longMa &&
          weightMode    == other.weightMode &&
          manualWeights == other.manualWeights;

  @override
  int get hashCode =>
      Object.hash(symbol, range, shortMa, longMa, weightMode, manualWeights);
}

// ===== Analysis Notifier =====

final analysisNotifierProvider = AsyncNotifierProviderFamily<
    AnalysisNotifier, AnalysisResult, AnalysisParams>(
  AnalysisNotifier.new,
);

class AnalysisNotifier
    extends FamilyAsyncNotifier<AnalysisResult, AnalysisParams> {
  @override
  Future<AnalysisResult> build(AnalysisParams arg) async {
    final repo = ref.watch(stockRepositoryProvider);
    final stockData = await repo.fetchCandlesWithCurrency(arg.symbol, range: arg.range);
    final candles = stockData.candles;
    final currency = stockData.currency;

    final closes = candles.map((c) => c.close).toList();
    final volumes = candles.map((c) => c.volume).toList();
    final n = candles.length;

    final maShort = TechnicalAnalyzer.calculateSMA(closes, arg.shortMa);
    final maLong = TechnicalAnalyzer.calculateSMA(closes, arg.longMa);
    final rsi = TechnicalAnalyzer.calculateRSI(closes);
    final bb = TechnicalAnalyzer.calculateBollingerBands(closes);
    final macdResult = TechnicalAnalyzer.calculateMACD(closes);
    final volumeMA = TechnicalAnalyzer.calculateVolumeMA(volumes);

    final generatorResult = SignalGenerator().generateWithMode(
      n: n,
      maShort: maShort,
      maLong: maLong,
      rsi: rsi,
      bbUpper: bb.upper,
      bbLower: bb.lower,
      close: closes,
      macd: macdResult.macd,
      macdSignal: macdResult.signal,
      volume: volumes,
      volumeMA: volumeMA,
      weightMode: arg.weightMode,
      manualWeights: arg.manualWeights,
    );

    return AnalysisResult(
      candles: candles,
      maShort: maShort,
      maLong: maLong,
      rsi: rsi,
      bbUpper: bb.upper,
      bbMiddle: bb.middle,
      bbLower: bb.lower,
      macd: macdResult.macd,
      macdSignal: macdResult.signal,
      signals: generatorResult.signals,
      currency: currency,
      patternResult: generatorResult.patternResult,
      signalExplanation: generatorResult.signalExplanation,
    );
  }
}

// ===== Backtest params =====

class BacktestParams {
  final double initialCapital;
  final double riskPerTrade;
  final double stopLossPct;
  final double takeProfitPct;
  final double tradeCostRate;

  const BacktestParams({
    this.initialCapital = 1000000,
    this.riskPerTrade = 2.0,
    this.stopLossPct = 5.0,
    this.takeProfitPct = 10.0,
    this.tradeCostRate = 0.1,
  });

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is BacktestParams &&
          initialCapital == other.initialCapital &&
          riskPerTrade == other.riskPerTrade &&
          stopLossPct == other.stopLossPct &&
          takeProfitPct == other.takeProfitPct &&
          tradeCostRate == other.tradeCostRate;

  @override
  int get hashCode => Object.hash(
        initialCapital,
        riskPerTrade,
        stopLossPct,
        takeProfitPct,
        tradeCostRate,
      );
}

// ===== Backtest Notifier =====

typedef BacktestFamilyParam = ({
  AnalysisParams analysisParams,
  BacktestParams backtestParams,
});

final backtestNotifierProvider = AsyncNotifierProviderFamily<
    BacktestNotifier, BacktestResult, BacktestFamilyParam>(
  BacktestNotifier.new,
);

class BacktestNotifier
    extends FamilyAsyncNotifier<BacktestResult, BacktestFamilyParam> {
  @override
  Future<BacktestResult> build(BacktestFamilyParam arg) async {
    final analysis = await ref.watch(
      analysisNotifierProvider(arg.analysisParams).future,
    );

    final engine = BacktestEngine();
    return engine.run(
      analysis,
      initialCapital: arg.backtestParams.initialCapital,
      riskPerTrade: arg.backtestParams.riskPerTrade,
      stopLossPct: arg.backtestParams.stopLossPct,
      takeProfitPct: arg.backtestParams.takeProfitPct,
      tradeCostRate: arg.backtestParams.tradeCostRate,
    );
  }
}

// ===== Portfolio Notifier（SharedPreferences永続化）=====

const _kPortfolioKey = 'watchlist_v1';

class PortfolioNotifier extends Notifier<List<PortfolioItem>> {
  static const _key = _kPortfolioKey;

  @override
  List<PortfolioItem> build() {
    // 起動時にSharedPreferencesから読み込む
    final prefs = ref.watch(sharedPreferencesProvider);
    final raw = prefs.getString(_key);
    if (raw == null) return [];
    try {
      final list = jsonDecode(raw) as List<dynamic>;
      return list
          .map((e) => PortfolioItem.fromJson(e as Map<String, dynamic>))
          .toList();
    } catch (_) {
      return [];
    }
  }

  Future<void> _save(List<PortfolioItem> items) async {
    final prefs = ref.read(sharedPreferencesProvider);
    await prefs.setString(_key, jsonEncode(items.map((e) => e.toJson()).toList()));
  }

  void add(String symbol, {String? name}) {
    if (state.any((item) => item.symbol == symbol)) return;
    final next = [
      ...state,
      PortfolioItem(symbol: symbol, name: name, addedAt: DateTime.now()),
    ];
    state = next;
    _save(next);
  }

  void remove(String symbol) {
    final next = state.where((item) => item.symbol != symbol).toList();
    state = next;
    _save(next);
  }
}

final portfolioProvider =
    NotifierProvider<PortfolioNotifier, List<PortfolioItem>>(
  PortfolioNotifier.new,
);

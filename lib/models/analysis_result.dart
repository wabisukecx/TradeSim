import 'stock_candle.dart';

// ===== WeightProfile =====
/// Python版 DYNAMIC_WEIGHT_PROFILES の各エントリに対応する不変データクラス
class WeightProfile {
  final String patternKey;
  final String name;
  final String description;
  final String strategyHint;
  final String riskLevel;
  final double maTrend;
  final double rsi;
  final double bollinger;
  final double macd;
  final double volume;

  const WeightProfile({
    required this.patternKey,
    required this.name,
    required this.description,
    required this.strategyHint,
    required this.riskLevel,
    this.maTrend   = 0.2,
    this.rsi       = 0.2,
    this.bollinger = 0.3,
    this.macd      = 0.3,
    this.volume    = 0.1,
  });
}

// ===== PatternResult =====
/// MarketPatternDetector.detect() の戻り値
class PatternResult {
  final String patternKey;   // 'uptrend' | 'downtrend' | 'range' | 'transition' | 'acceleration' | 'balanced'
  final String name;         // 日本語名
  final String description;
  final String strategyHint;
  final String riskLevel;
  final double confidence;   // 0.0 ~ 1.0
  final WeightProfile weights;

  const PatternResult({
    required this.patternKey,
    required this.name,
    required this.description,
    required this.strategyHint,
    required this.riskLevel,
    required this.confidence,
    required this.weights,
  });
}

// ===== AnalysisResult =====
class AnalysisResult {
  final List<StockCandle> candles;
  final List<double?> maShort;
  final List<double?> maLong;
  final List<double?> rsi;
  final List<double?> bbUpper;
  final List<double?> bbMiddle;
  final List<double?> bbLower;
  final List<double?> macd;
  final List<double?> macdSignal;
  final List<int> signals;
  final String currency;

  // --- v3.0 追加フィールド（nullable: 既存呼び出し元への影響なし）---
  final PatternResult? patternResult;
  final List<String> signalExplanation;

  const AnalysisResult({
    required this.candles,
    required this.maShort,
    required this.maLong,
    required this.rsi,
    required this.bbUpper,
    required this.bbMiddle,
    required this.bbLower,
    required this.macd,
    required this.macdSignal,
    required this.signals,
    this.currency = 'JPY',
    this.patternResult,
    this.signalExplanation = const [],
  });

  factory AnalysisResult.fromJson(Map<String, dynamic> json) {
    return AnalysisResult(
      candles: (json['candles'] as List)
          .map((e) => StockCandle.fromJson(e as Map<String, dynamic>))
          .toList(),
      maShort:    (json['maShort']    as List).map((e) => e as double?).toList(),
      maLong:     (json['maLong']     as List).map((e) => e as double?).toList(),
      rsi:        (json['rsi']        as List).map((e) => e as double?).toList(),
      bbUpper:    (json['bbUpper']    as List).map((e) => e as double?).toList(),
      bbMiddle:   (json['bbMiddle']   as List).map((e) => e as double?).toList(),
      bbLower:    (json['bbLower']    as List).map((e) => e as double?).toList(),
      macd:       (json['macd']       as List).map((e) => e as double?).toList(),
      macdSignal: (json['macdSignal'] as List).map((e) => e as double?).toList(),
      signals:    (json['signals']    as List).map((e) => e as int).toList(),
    );
  }

  Map<String, dynamic> toJson() => {
    'candles':    candles.map((c) => c.toJson()).toList(),
    'maShort':    maShort,
    'maLong':     maLong,
    'rsi':        rsi,
    'bbUpper':    bbUpper,
    'bbMiddle':   bbMiddle,
    'bbLower':    bbLower,
    'macd':       macd,
    'macdSignal': macdSignal,
    'signals':    signals,
  };
}

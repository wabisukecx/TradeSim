import 'market_pattern_detector.dart';
import '../models/analysis_result.dart';

/// シグナル生成サービス
/// Python版 analysis/signals.py の移植（動的重み付け対応）
class SignalGenerator {
  // --- 重み付け定数（固定モード / Python版 default_signal_weights）---
  static const double _defaultMaTrend = 1.0;
  static const double _defaultRsi     = 1.0;
  static const double _defaultBoll    = 1.5;
  static const double _defaultMacd    = 1.5;
  static const double _defaultVolume  = 0.5;

  static const double _rsiOversold   = 35;
  static const double _rsiOverbought = 65;
  static const double _buyThreshold  = 2.5;
  static const double _sellThreshold = 2.5;

  // ===== 後方互換 静的API =====
  /// 既存コードとの互換性維持。固定重み付けでシグナルを生成する。
  static List<int> generate({
    required int n,
    required List<double?> maShort,
    required List<double?> maLong,
    required List<double?> rsi,
    required List<double?> bbUpper,
    required List<double?> bbLower,
    required List<double> close,
    required List<double?> macd,
    required List<double?> macdSignal,
    required List<double> volume,
    required List<double?> volumeMA,
  }) {
    return SignalGenerator()._generateInternal(
      n: n, maShort: maShort, maLong: maLong, rsi: rsi,
      bbUpper: bbUpper, bbLower: bbLower, close: close,
      macd: macd, macdSignal: macdSignal, volume: volume,
      volumeMA: volumeMA,
      weights: _fixedWeightsProfile(),
    );
  }

  // ===== 新API（重み付けモード対応）=====
  /// 重み付けモードを指定してシグナルを生成する。
  /// [weightMode]: 'fixed' | 'adaptive' | 'manual'
  /// [manualWeights]: weightMode == 'manual' の場合に使用する WeightProfile
  SignalGeneratorResult generateWithMode({
    required int n,
    required List<double?> maShort,
    required List<double?> maLong,
    required List<double?> rsi,
    required List<double?> bbUpper,
    required List<double?> bbLower,
    required List<double> close,
    required List<double?> macd,
    required List<double?> macdSignal,
    required List<double> volume,
    required List<double?> volumeMA,
    String weightMode = 'fixed',
    WeightProfile? manualWeights,
  }) {
    WeightProfile weights;
    PatternResult? detectedPattern;

    switch (weightMode) {
      case 'adaptive':
        final detector = MarketPatternDetector();
        detectedPattern = detector.detect(
          maShort: maShort, maLong: maLong, rsi: rsi,
          macd: macd, macdSignal: macdSignal, close: close,
          volume: volume, n: n,
        );
        // 信頼度が 0.6 以上の場合のみ動的重みを使用
        weights = detectedPattern.confidence >= 0.6
            ? detectedPattern.weights
            : _fixedWeightsProfile();
      case 'manual' when manualWeights != null:
        weights = manualWeights;
      default: // 'fixed'
        weights = _fixedWeightsProfile();
    }

    final signals = _generateInternal(
      n: n, maShort: maShort, maLong: maLong, rsi: rsi,
      bbUpper: bbUpper, bbLower: bbLower, close: close,
      macd: macd, macdSignal: macdSignal, volume: volume,
      volumeMA: volumeMA, weights: weights,
    );

    final explanation = _buildExplanation(
      signals: signals, n: n, maShort: maShort, maLong: maLong,
      rsi: rsi, bbUpper: bbUpper, bbLower: bbLower,
      close: close, macd: macd, macdSignal: macdSignal,
      weights: weights,
    );

    return SignalGeneratorResult(
      signals: signals,
      patternResult: detectedPattern,
      signalExplanation: explanation,
      usedWeights: weights,
    );
  }

  // ===== 内部実装 =====

  static WeightProfile _fixedWeightsProfile() => const WeightProfile(
    patternKey: 'fixed', name: '固定重み付け', description: '',
    strategyHint: '', riskLevel: 'medium',
    maTrend:   _defaultMaTrend,
    rsi:       _defaultRsi,
    bollinger: _defaultBoll,
    macd:      _defaultMacd,
    volume:    _defaultVolume,
  );

  List<int> _generateInternal({
    required int n,
    required List<double?> maShort,
    required List<double?> maLong,
    required List<double?> rsi,
    required List<double?> bbUpper,
    required List<double?> bbLower,
    required List<double> close,
    required List<double?> macd,
    required List<double?> macdSignal,
    required List<double> volume,
    required List<double?> volumeMA,
    required WeightProfile weights,
  }) {
    final buyScores  = List<double>.filled(n, 0.0);
    final sellScores = List<double>.filled(n, 0.0);

    // MA
    for (int i = 0; i < n; i++) {
      final s = maShort[i];
      final l = maLong[i];
      if (s == null || l == null) continue;
      if (s > l) { buyScores[i] += weights.maTrend; }
      else if (s < l) { sellScores[i] += weights.maTrend; }
    }
    // RSI
    for (int i = 0; i < n; i++) {
      final r = rsi[i];
      if (r == null) continue;
      if (r < _rsiOversold) { buyScores[i] += weights.rsi; }
      else if (r > _rsiOverbought) { sellScores[i] += weights.rsi; }
    }
    // Bollinger
    for (int i = 0; i < n; i++) {
      final u = bbUpper[i];
      final l = bbLower[i];
      if (u == null || l == null) continue;
      if (close[i] < l) { buyScores[i] += weights.bollinger; }
      else if (close[i] > u) { sellScores[i] += weights.bollinger; }
    }
    // MACD（状態ベース）
    for (int i = 0; i < n; i++) {
      final m = macd[i];
      final s = macdSignal[i];
      if (m == null || s == null) continue;
      if (m > s) { buyScores[i] += weights.macd; }
      else if (m < s) { sellScores[i] += weights.macd; }
    }
    // Volume
    for (int i = 0; i < n; i++) {
      final vma = volumeMA[i];
      if (vma == null) continue;
      if (volume[i] > vma) {
        buyScores[i]  += weights.volume;
        sellScores[i] += weights.volume;
      }
    }

    final signals = List<int>.filled(n, 0);
    for (int i = 0; i < n; i++) {
      if (buyScores[i] >= _buyThreshold) { signals[i] = 1; }
      else if (sellScores[i] >= _sellThreshold) { signals[i] = -1; }
    }
    return signals;
  }

  /// シグナル理由説明テキストを生成（最新インデックスの説明）
  /// Python版 get_signal_explanation() に相当
  List<String> _buildExplanation({
    required List<int> signals,
    required int n,
    required List<double?> maShort,
    required List<double?> maLong,
    required List<double?> rsi,
    required List<double?> bbUpper,
    required List<double?> bbLower,
    required List<double> close,
    required List<double?> macd,
    required List<double?> macdSignal,
    required WeightProfile weights,
  }) {
    if (n == 0) return [];
    final idx = n - 1;
    final reasons = <String>[];

    // MA
    final ms = maShort[idx]; final ml = maLong[idx];
    if (ms != null && ml != null) {
      final w = weights.maTrend.toStringAsFixed(1);
      if (ms > ml) { reasons.add('✅ 上昇トレンド - 短期平均 > 長期平均 (重み: $w)'); }
      else { reasons.add('❌ 下降トレンド - 短期平均 < 長期平均 (重み: $w)'); }
    }
    // RSI
    final r = rsi[idx];
    if (r != null) {
      final w = weights.rsi.toStringAsFixed(1);
      if (r < _rsiOversold) {
        reasons.add('✅ RSI低水準 - RSI = ${r.toStringAsFixed(1)} (重み: $w)');
      } else if (r > _rsiOverbought) {
        reasons.add('❌ RSI高水準 - RSI = ${r.toStringAsFixed(1)} (重み: $w)');
      } else {
        reasons.add('⚪ RSI中程度 - RSI = ${r.toStringAsFixed(1)} (重み: $w)');
      }
    }
    // Bollinger
    final bu = bbUpper[idx]; final bl = bbLower[idx];
    if (bu != null && bl != null) {
      final w = weights.bollinger.toStringAsFixed(1);
      if (close[idx] < bl) {
        reasons.add('✅ 下側バンド突破 - ボリンジャーバンド下限を下回る (重み: $w)');
      } else if (close[idx] > bu) {
        reasons.add('❌ 上側バンド突破 - ボリンジャーバンド上限を上回る (重み: $w)');
      }
    }
    // MACD
    final m = macd[idx]; final ms2 = macdSignal[idx];
    if (m != null && ms2 != null) {
      final w = weights.macd.toStringAsFixed(1);
      if (m > ms2) { reasons.add('✅ MACD上向き - 買い勢いを示唆 (重み: $w)'); }
      else { reasons.add('❌ MACD下向き - 売り勢いを示唆 (重み: $w)'); }
    }

    return reasons;
  }
}

/// SignalGenerator.generateWithMode() の戻り値
class SignalGeneratorResult {
  final List<int> signals;
  final PatternResult? patternResult;
  final List<String> signalExplanation;
  final WeightProfile usedWeights;

  const SignalGeneratorResult({
    required this.signals,
    required this.patternResult,
    required this.signalExplanation,
    required this.usedWeights,
  });
}

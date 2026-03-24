import '../models/analysis_result.dart';

/// Python版 analysis/pattern_detector.py の移植
/// MarketPatternDetector クラスに相当
class MarketPatternDetector {
  // --- パターン別重み付けプロファイル ---
  // Python版 DYNAMIC_WEIGHT_PROFILES と同一の値
  static const _profiles = {
    'uptrend': WeightProfile(
      patternKey: 'uptrend',
      name: '上昇トレンド',
      description: '価格が持続的に上昇している状態',
      strategyHint: '移動平均とMACDを重視し、トレンドフォローを基本とする',
      riskLevel: 'medium',
      maTrend: 0.35, macd: 0.30, bollinger: 0.15, rsi: 0.15, volume: 0.05,
    ),
    'downtrend': WeightProfile(
      patternKey: 'downtrend',
      name: '下降トレンド',
      description: '価格が持続的に下降している状態',
      strategyHint: '移動平均とMACDを重視し、反転ポイントを慎重に判断',
      riskLevel: 'high',
      maTrend: 0.35, macd: 0.30, rsi: 0.20, bollinger: 0.10, volume: 0.05,
    ),
    'range': WeightProfile(
      patternKey: 'range',
      name: 'レンジ相場',
      description: '価格が一定の範囲内で上下している状態',
      strategyHint: 'RSIとボリンジャーバンドを重視し、反転を狙う',
      riskLevel: 'low',
      rsi: 0.35, bollinger: 0.35, maTrend: 0.15, macd: 0.10, volume: 0.05,
    ),
    'transition': WeightProfile(
      patternKey: 'transition',
      name: '転換期',
      description: 'トレンドが変化している可能性がある状態',
      strategyHint: 'MACDを最重視し、転換点の早期検出を図る',
      riskLevel: 'high',
      macd: 0.45, rsi: 0.25, bollinger: 0.15, maTrend: 0.10, volume: 0.05,
    ),
    'acceleration': WeightProfile(
      patternKey: 'acceleration',
      name: '加速相場',
      description: '価格変動が急激に拡大している状態',
      strategyHint: '出来高を重視し、加速の持続性を判断',
      riskLevel: 'high',
      volume: 0.25, macd: 0.30, bollinger: 0.20, maTrend: 0.15, rsi: 0.10,
    ),
  };

  static PatternResult get _defaultPattern => const PatternResult(
    patternKey: 'balanced',
    name: 'バランス型',
    description: 'バランスの取れた重み付け',
    strategyHint: '全指標をバランスよく活用',
    riskLevel: 'medium',
    confidence: 0.5,
    weights: WeightProfile(
      patternKey: 'balanced', name: '', description: '', strategyHint: '',
      riskLevel: 'medium',
      maTrend: 0.2, rsi: 0.2, bollinger: 0.3, macd: 0.3, volume: 0.1,
    ),
  );

  /// 市場パターンを検出して PatternResult を返す
  /// Python版 detect_market_pattern() に相当
  PatternResult detect({
    required List<double?> maShort,
    required List<double?> maLong,
    required List<double?> rsi,
    required List<double?> macd,
    required List<double?> macdSignal,
    required List<double> close,
    required List<double> volume,
    required int n,
  }) {
    if (n < 20) return _defaultPattern;
    try {
      final trend      = _analyzeTrend(maShort, maLong, n);
      final volatility = _analyzeVolatility(close, n);
      final momentum   = _analyzeMomentum(macd, macdSignal, rsi, n);
      final vol        = _analyzeVolume(volume, n);

      final scores = {
        'uptrend':      _uptrendScore(trend, momentum, vol),
        'downtrend':    _downtrendScore(trend, momentum, vol),
        'range':        _rangeScore(trend, volatility, momentum),
        'transition':   _transitionScore(momentum, volatility),
        'acceleration': _accelerationScore(volatility, vol, momentum),
      };

      final best = scores.entries.reduce((a, b) => a.value > b.value ? a : b);
      if (best.value < 0.3) return _defaultPattern;

      final profile = _profiles[best.key]!;
      return PatternResult(
        patternKey:   best.key,
        name:         profile.name,
        description:  profile.description,
        strategyHint: profile.strategyHint,
        riskLevel:    profile.riskLevel,
        confidence:   best.value,
        weights:      profile,
      );
    } catch (_) {
      return _defaultPattern;
    }
  }

  // --- 内部分析メソッド ---

  /// トレンド分析: 'up' / 'down' / 'neutral' と信頼度を返す
  _TrendAnalysis _analyzeTrend(List<double?> maShort, List<double?> maLong, int n) {
    final validShort = maShort.whereType<double>().toList();
    final validLong  = maLong.whereType<double>().toList();
    if (validShort.length < 10 || validLong.length < 10) {
      return _TrendAnalysis('neutral', 0.5, 0.0);
    }

    final recentShort = validShort.sublist(validShort.length - 5)
        .fold(0.0, (a, b) => a + b) / 5;
    final recentLong = validLong.sublist(validLong.length - 5)
        .fold(0.0, (a, b) => a + b) / 5;
    final shortSlope = (validShort.last - validShort[validShort.length - 5]) / 5;

    String direction;
    double strength;
    if (recentShort > recentLong && shortSlope > 0) {
      direction = 'up';
      strength  = (shortSlope.abs() / validShort.last * 100).clamp(0.0, 1.0);
    } else if (recentShort < recentLong && shortSlope < 0) {
      direction = 'down';
      strength  = (shortSlope.abs() / validShort.last * 100).clamp(0.0, 1.0);
    } else {
      direction = 'neutral';
      strength  = 0.5;
    }

    final confidence = recentLong != 0
        ? ((recentShort - recentLong).abs() / recentLong).clamp(0.0, 1.0)
        : 0.0;
    return _TrendAnalysis(direction, strength, confidence);
  }

  /// ボラティリティ分析: 'expanding' / 'contracting' / 'normal'
  _VolatilityAnalysis _analyzeVolatility(List<double> close, int n) {
    if (close.length < 20) return _VolatilityAnalysis('normal', 0.5, 0.0);

    final returns = <double>[];
    for (int i = 1; i < close.length; i++) {
      if (close[i - 1] != 0) {
        returns.add((close[i] - close[i - 1]) / close[i - 1]);
      }
    }
    if (returns.length < 20) return _VolatilityAnalysis('normal', 0.5, 0.0);

    double mean(List<double> xs) => xs.fold(0.0, (a, b) => a + b) / xs.length;
    double std(List<double> xs) {
      final m = mean(xs);
      return xs.fold(0.0, (a, b) => a + (b - m) * (b - m)) / xs.length;
    }

    final recent      = returns.sublist(returns.length - 10);
    final recentVol   = std(recent);
    final historicalVol = std(returns);

    if (historicalVol == 0) return _VolatilityAnalysis('normal', 0.5, 0.0);

    final ratio = recentVol / historicalVol;
    String state;
    double level;
    if (ratio > 1.3) {
      state = 'expanding';
      level = (ratio - 1.0).clamp(0.0, 1.0);
    } else if (ratio < 0.7) {
      state = 'contracting';
      level = (1.0 - ratio).clamp(0.0, 1.0);
    } else {
      state = 'normal';
      level = 0.5;
    }
    return _VolatilityAnalysis(state, level, (ratio - 1.0).abs().clamp(0.0, 1.0));
  }

  /// モメンタム分析: MACDの方向と信頼度
  _MomentumAnalysis _analyzeMomentum(
    List<double?> macd, List<double?> macdSignal, List<double?> rsi, int n,
  ) {
    final validMacd   = <double>[];
    final validSignal = <double>[];
    for (int i = 0; i < n; i++) {
      final m = macd[i];
      final s = macdSignal[i];
      if (m != null && s != null) {
        validMacd.add(m);
        validSignal.add(s);
      }
    }
    if (validMacd.length < 5) return _MomentumAnalysis('neutral', 0.5, 0.0);

    final lastMacd   = validMacd.last;
    final lastSignal = validSignal.last;
    final direction  = lastMacd > lastSignal ? 'bullish_momentum' : 'bearish_momentum';
    final strength   = lastSignal != 0
        ? ((lastMacd - lastSignal).abs() / lastSignal.abs()).clamp(0.0, 1.0)
        : 0.0;
    return _MomentumAnalysis(direction, strength, 0.7);
  }

  /// 出来高分析
  _VolumeAnalysis _analyzeVolume(List<double> volume, int n) {
    if (volume.length < 10) return _VolumeAnalysis('normal', false, 0.0);

    final recent     = volume.sublist(volume.length - 5)
        .fold(0.0, (a, b) => a + b) / 5;
    final historical = volume.fold(0.0, (a, b) => a + b) / volume.length;
    if (historical == 0) return _VolumeAnalysis('normal', false, 0.0);

    final ratio = recent / historical;
    String trend;
    bool confirmation;
    if (ratio > 1.2) {
      trend = 'increasing'; confirmation = true;
    } else if (ratio < 0.8) {
      trend = 'decreasing'; confirmation = false;
    } else {
      trend = 'normal'; confirmation = true;
    }
    return _VolumeAnalysis(trend, confirmation, (ratio - 1.0).abs().clamp(0.0, 1.0));
  }

  // --- スコア計算メソッド ---

  double _uptrendScore(_TrendAnalysis t, _MomentumAnalysis m, _VolumeAnalysis v) {
    double s = 0;
    if (t.direction == 'up') s += 0.4 * t.confidence;
    if (m.direction == 'bullish_momentum') s += 0.3 * m.confidence;
    if (v.confirmation && v.trend == 'increasing') s += 0.3 * v.confidence;
    return s.clamp(0.0, 1.0);
  }

  double _downtrendScore(_TrendAnalysis t, _MomentumAnalysis m, _VolumeAnalysis v) {
    double s = 0;
    if (t.direction == 'down') s += 0.4 * t.confidence;
    if (m.direction == 'bearish_momentum') s += 0.3 * m.confidence;
    if (v.trend == 'increasing') s += 0.3 * v.confidence;
    return s.clamp(0.0, 1.0);
  }

  double _rangeScore(_TrendAnalysis t, _VolatilityAnalysis vol, _MomentumAnalysis m) {
    double s = 0;
    if (t.direction == 'neutral') s += 0.4;
    if (vol.state == 'contracting') s += 0.3 * vol.confidence;
    if (m.direction == 'neutral') s += 0.3;
    return s.clamp(0.0, 1.0);
  }

  double _transitionScore(_MomentumAnalysis m, _VolatilityAnalysis vol) {
    double s = 0;
    if (m.confidence > 0.5) s += 0.5 * m.confidence;
    if (vol.state == 'expanding') s += 0.5 * vol.confidence;
    return s.clamp(0.0, 1.0);
  }

  double _accelerationScore(_VolatilityAnalysis vol, _VolumeAnalysis v, _MomentumAnalysis m) {
    double s = 0;
    if (vol.state == 'expanding') s += 0.4 * vol.confidence;
    if (v.trend == 'increasing') s += 0.4 * v.confidence;
    if (m.strength > 0.7) s += 0.2;
    return s.clamp(0.0, 1.0);
  }
}

// --- 内部データクラス（ファイルスコープ） ---

class _TrendAnalysis {
  final String direction;
  final double strength;
  final double confidence;
  const _TrendAnalysis(this.direction, this.strength, this.confidence);
}

class _VolatilityAnalysis {
  final String state;
  final double level;
  final double confidence;
  const _VolatilityAnalysis(this.state, this.level, this.confidence);
}

class _MomentumAnalysis {
  final String direction;
  final double strength;
  final double confidence;
  const _MomentumAnalysis(this.direction, this.strength, this.confidence);
}

class _VolumeAnalysis {
  final String trend;
  final bool confirmation;
  final double confidence;
  const _VolumeAnalysis(this.trend, this.confirmation, this.confidence);
}

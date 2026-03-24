import 'dart:math';
import '../models/stock_candle.dart';

/// テクニカル分析サービス (analysis/technical.py の移植)
class TechnicalAnalyzer {
  // ===== SMA =====
  /// 単純移動平均を計算する。periodに満たないインデックスはnullを返す。
  static List<double?> calculateSMA(List<double> prices, int period) {
    final result = List<double?>.filled(prices.length, null);
    for (int i = period - 1; i < prices.length; i++) {
      double sum = 0;
      for (int j = i - period + 1; j <= i; j++) {
        sum += prices[j];
      }
      result[i] = sum / period;
    }
    return result;
  }

  // ===== RSI =====
  /// RSIを計算する (period=14)。
  static List<double?> calculateRSI(List<double> prices, {int period = 14}) {
    final result = List<double?>.filled(prices.length, null);
    if (prices.length <= period) return result;

    // 最初のperiod日の平均上昇/下落
    double avgGain = 0;
    double avgLoss = 0;
    for (int i = 1; i <= period; i++) {
      final change = prices[i] - prices[i - 1];
      if (change > 0) {
        avgGain += change;
      } else {
        avgLoss += -change;
      }
    }
    avgGain /= period;
    avgLoss /= period;

    if (avgLoss == 0) {
      result[period] = 100;
    } else {
      final rs = avgGain / avgLoss;
      result[period] = 100 - (100 / (1 + rs));
    }

    // Wilder's smoothing
    for (int i = period + 1; i < prices.length; i++) {
      final change = prices[i] - prices[i - 1];
      final gain = change > 0 ? change : 0.0;
      final loss = change < 0 ? -change : 0.0;

      avgGain = (avgGain * (period - 1) + gain) / period;
      avgLoss = (avgLoss * (period - 1) + loss) / period;

      if (avgLoss == 0) {
        result[i] = 100;
      } else {
        final rs = avgGain / avgLoss;
        result[i] = 100 - (100 / (1 + rs));
      }
    }
    return result;
  }

  // ===== Bollinger Bands =====
  /// ボリンジャーバンドを計算する (period=20, stdDev=2.0)。
  static ({
    List<double?> upper,
    List<double?> middle,
    List<double?> lower,
  }) calculateBollingerBands(
    List<double> prices, {
    int period = 20,
    double stdDev = 2.0,
  }) {
    final middle = calculateSMA(prices, period);
    final upper = List<double?>.filled(prices.length, null);
    final lower = List<double?>.filled(prices.length, null);

    for (int i = period - 1; i < prices.length; i++) {
      final ma = middle[i]!;
      double variance = 0;
      for (int j = i - period + 1; j <= i; j++) {
        final diff = prices[j] - ma;
        variance += diff * diff;
      }
      // ta ライブラリ（Python版）は標本標準偏差（N-1除算）を使用
      final std = sqrt(variance / (period - 1));
      upper[i] = ma + stdDev * std;
      lower[i] = ma - stdDev * std;
    }

    return (upper: upper, middle: middle, lower: lower);
  }

  // ===== MACD =====
  /// MACDラインとシグナルラインを計算する (fast=12, slow=26, signal=9)。
  static ({List<double?> macd, List<double?> signal}) calculateMACD(
    List<double> prices, {
    int fast = 12,
    int slow = 26,
    int signal = 9,
  }) {
    final emaFast = _calculateEMA(prices, fast);
    final emaSlow = _calculateEMA(prices, slow);

    final macdLine = List<double?>.filled(prices.length, null);
    for (int i = 0; i < prices.length; i++) {
      if (emaFast[i] != null && emaSlow[i] != null) {
        macdLine[i] = emaFast[i]! - emaSlow[i]!;
      }
    }

    // MACDシグナル: MACDラインのEMA
    final signalLine = List<double?>.filled(prices.length, null);
    // 最初の有効なMACD値のインデックスを探す
    int firstValid = -1;
    for (int i = 0; i < macdLine.length; i++) {
      if (macdLine[i] != null) {
        firstValid = i;
        break;
      }
    }
    if (firstValid == -1) return (macd: macdLine, signal: signalLine);

    // シグナルラインのEMAをMACDの有効部分で計算
    final validMacd = <double>[];
    for (int i = firstValid; i < macdLine.length; i++) {
      validMacd.add(macdLine[i]!);
    }
    final signalEma = _calculateEMA(validMacd, signal);
    for (int i = 0; i < signalEma.length; i++) {
      if (signalEma[i] != null) {
        signalLine[firstValid + i] = signalEma[i];
      }
    }

    return (macd: macdLine, signal: signalLine);
  }

  // ===== ATR =====
  /// ATR (Average True Range) を計算する (period=14)。
  static List<double?> calculateATR(
      List<StockCandle> candles, {
      int period = 14,
    }) {
    final result = List<double?>.filled(candles.length, null);
    if (candles.length < 2) return result;

    final trueRanges = <double>[];
    trueRanges.add(candles[0].high - candles[0].low);
    for (int i = 1; i < candles.length; i++) {
      final hl = candles[i].high - candles[i].low;
      final hc = (candles[i].high - candles[i - 1].close).abs();
      final lc = (candles[i].low - candles[i - 1].close).abs();
      trueRanges.add([hl, hc, lc].reduce((a, b) => a > b ? a : b));
    }

    // Wilder's smoothing ATR
    if (trueRanges.length < period) return result;
    double atr = 0;
    for (int i = 0; i < period; i++) {
      atr += trueRanges[i];
    }
    atr /= period;
    result[period - 1] = atr;

    for (int i = period; i < trueRanges.length; i++) {
      atr = (atr * (period - 1) + trueRanges[i]) / period;
      result[i] = atr;
    }
    return result;
  }

  // ===== Volume MA =====
  /// 出来高移動平均を計算する (period=20)。
  static List<double?> calculateVolumeMA(
      List<double> volumes, {
      int period = 20,
    }) {
    return calculateSMA(volumes, period);
  }

  // ===== EMA (内部ヘルパー) =====
  static List<double?> _calculateEMA(List<double> prices, int period) {
    final result = List<double?>.filled(prices.length, null);
    if (prices.length < period) return result;

    double sum = 0;
    for (int i = 0; i < period; i++) {
      sum += prices[i];
    }
    result[period - 1] = sum / period;

    final multiplier = 2.0 / (period + 1);
    for (int i = period; i < prices.length; i++) {
      result[i] = (prices[i] - result[i - 1]!) * multiplier + result[i - 1]!;
    }
    return result;
  }
}

// T3: SignalGenerator テスト
import 'package:flutter_test/flutter_test.dart';
import 'package:trade_sim_flutter/services/signal_generator.dart';
import 'package:trade_sim_flutter/services/technical_analyzer.dart';

void main() {
  group('T3: SignalGenerator', () {
    test('MA_short > MA_long かつ RSI < 35 で buy signal=1 が返る', () {
      const n = 60;
      // 上昇トレンドで short > long になる価格列
      final closes = List.generate(n, (i) => 100.0 + i * 1.0);
      // 最後の要素の出来高を大きくして Volume シグナル (+0.5) を発火させる
      final volumes = List.filled(n, 1000000.0);
      volumes[n - 1] = 5000000.0; // VolumeMA を大きく超える出来高

      final maShort = TechnicalAnalyzer.calculateSMA(closes, 5);
      final maLong = TechnicalAnalyzer.calculateSMA(closes, 20);
      final rsiRaw = TechnicalAnalyzer.calculateRSI(closes);
      final bb = TechnicalAnalyzer.calculateBollingerBands(closes);
      final macdResult = TechnicalAnalyzer.calculateMACD(closes);
      final volumeMA = TechnicalAnalyzer.calculateVolumeMA(volumes);

      // 最後のインデックスで手動オーバーライド: RSI を 30 に近い値にする
      // (実際には急激な下落でRSIが下がるため、テスト用に RSI リストをモック)
      final mockRsi = List<double?>.from(rsiRaw);
      // 最後の有効なインデックスを 30 未満の値に上書き
      for (int i = n - 1; i >= 0; i--) {
        if (mockRsi[i] != null) {
          mockRsi[i] = 30.0; // oversold (< 35)
          break;
        }
      }

      final signals = SignalGenerator.generate(
        n: n,
        maShort: maShort,
        maLong: maLong,
        rsi: mockRsi,
        bbUpper: bb.upper,
        bbLower: bb.lower,
        close: closes,
        macd: macdResult.macd,
        macdSignal: macdResult.signal,
        volume: volumes,
        volumeMA: volumeMA,
      );

      // MA(1.0) + RSI(1.0) + Volume(0.5) = 2.5 >= threshold(2.5) → signal=1
      expect(signals.last, equals(1));
    });

    test('all signals are -1, 0, or 1', () {
      const n = 40;
      final closes = List.generate(n, (i) => 100.0 + (i % 10) * 2.0 - 10.0);
      final volumes = List.filled(n, 500000.0);

      final maShort = TechnicalAnalyzer.calculateSMA(closes, 5);
      final maLong = TechnicalAnalyzer.calculateSMA(closes, 20);
      final rsi = TechnicalAnalyzer.calculateRSI(closes);
      final bb = TechnicalAnalyzer.calculateBollingerBands(closes);
      final macdResult = TechnicalAnalyzer.calculateMACD(closes);
      final volumeMA = TechnicalAnalyzer.calculateVolumeMA(volumes);

      final signals = SignalGenerator.generate(
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
      );

      for (final s in signals) {
        expect([-1, 0, 1].contains(s), isTrue);
      }
    });
  });
}

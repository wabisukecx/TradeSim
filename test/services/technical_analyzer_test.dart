// T1: SMA テスト
// T2: RSI テスト
import 'package:flutter_test/flutter_test.dart';
import 'package:trade_sim_flutter/services/technical_analyzer.dart';

void main() {
  group('T1: TechnicalAnalyzer - SMA', () {
    test('SMA period=3 on [100,110,120,130,140] → [null,null,110,120,130]',
        () {
      final prices = [100.0, 110.0, 120.0, 130.0, 140.0];
      final result = TechnicalAnalyzer.calculateSMA(prices, 3);
      expect(result.length, 5);
      expect(result[0], isNull);
      expect(result[1], isNull);
      expect(result[2], closeTo(110.0, 0.001));
      expect(result[3], closeTo(120.0, 0.001));
      expect(result[4], closeTo(130.0, 0.001));
    });

    test('SMA with period > list length returns all null', () {
      final result = TechnicalAnalyzer.calculateSMA([100.0, 200.0], 5);
      expect(result.every((v) => v == null), isTrue);
    });

    test('SMA period=1 returns same values', () {
      final prices = [10.0, 20.0, 30.0];
      final result = TechnicalAnalyzer.calculateSMA(prices, 1);
      expect(result[0], closeTo(10.0, 0.001));
      expect(result[1], closeTo(20.0, 0.001));
      expect(result[2], closeTo(30.0, 0.001));
    });
  });

  group('T2: TechnicalAnalyzer - RSI', () {
    // 十分な長さのデータを生成
    List<double> _generatePrices(int n) {
      final prices = <double>[100.0];
      for (int i = 1; i < n; i++) {
        // 上昇・下落を交互に繰り返す
        prices.add(prices.last + (i % 3 == 0 ? -5 : 3));
      }
      return prices;
    }

    test('RSI is in range [0, 100]', () {
      final prices = _generatePrices(50);
      final rsi = TechnicalAnalyzer.calculateRSI(prices);
      for (final v in rsi) {
        if (v != null) {
          expect(v, greaterThanOrEqualTo(0));
          expect(v, lessThanOrEqualTo(100));
        }
      }
    });

    test('RSI returns null for first 14 entries', () {
      final prices = _generatePrices(30);
      final rsi = TechnicalAnalyzer.calculateRSI(prices, period: 14);
      for (int i = 0; i < 14; i++) {
        expect(rsi[i], isNull);
      }
    });

    test('Steadily rising prices produce RSI near 100', () {
      final prices = List.generate(30, (i) => 100.0 + i * 5);
      final rsi = TechnicalAnalyzer.calculateRSI(prices);
      final last = rsi.last;
      expect(last, isNotNull);
      expect(last!, greaterThan(90));
    });

    test('Steadily falling prices produce RSI near 0', () {
      final prices = List.generate(30, (i) => 200.0 - i * 5);
      final rsi = TechnicalAnalyzer.calculateRSI(prices);
      final last = rsi.last;
      expect(last, isNotNull);
      expect(last!, lessThan(10));
    });
  });

  group('T2: TechnicalAnalyzer - Bollinger Bands', () {
    test('BB upper >= middle >= lower', () {
      final prices = List.generate(30, (i) => 100.0 + (i % 5) * 3.0);
      final bb = TechnicalAnalyzer.calculateBollingerBands(prices, period: 20);
      for (int i = 19; i < prices.length; i++) {
        final u = bb.upper[i]!;
        final m = bb.middle[i]!;
        final l = bb.lower[i]!;
        expect(u, greaterThanOrEqualTo(m));
        expect(m, greaterThanOrEqualTo(l));
      }
    });
  });

  group('T2: TechnicalAnalyzer - MACD', () {
    test('MACD returns same length lists', () {
      final prices = List.generate(50, (i) => 100.0 + i * 1.5);
      final macd = TechnicalAnalyzer.calculateMACD(prices);
      expect(macd.macd.length, prices.length);
      expect(macd.signal.length, prices.length);
    });
  });
}

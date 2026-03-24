// T5a: StockRepository テスト
// Yahoo Finance v8 API のレスポンスパースを MockClient でテストする
import 'dart:convert';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:trade_sim_flutter/repositories/stock_repository.dart';

// ===== テスト用 Yahoo Finance v8 モックレスポンス =====

/// 正常レスポンス: 3件の OHLCV データ
String _validResponse(String symbol) => jsonEncode({
      'chart': {
        'error': null,
        'result': [
          {
            'meta': {'symbol': symbol, 'currency': 'JPY'},
            'timestamp': [1700000000, 1700086400, 1700172800],
            'indicators': {
              'quote': [
                {
                  'open': [1000.0, 1010.0, 1020.0],
                  'high': [1050.0, 1060.0, 1070.0],
                  'low': [990.0, 1000.0, 1010.0],
                  'close': [1030.0, 1040.0, 1050.0],
                  'volume': [100000.0, 110000.0, 120000.0],
                }
              ]
            }
          }
        ]
      }
    });

/// null 値混じりレスポンス: 一部の行が null
String _responseWithNulls() => jsonEncode({
      'chart': {
        'error': null,
        'result': [
          {
            'meta': {'symbol': 'TEST'},
            'timestamp': [1700000000, 1700086400, 1700172800],
            'indicators': {
              'quote': [
                {
                  'open': [1000.0, null, 1020.0],
                  'high': [1050.0, null, 1070.0],
                  'low': [990.0, null, 1010.0],
                  'close': [1030.0, null, 1050.0],
                  'volume': [100000.0, null, 120000.0],
                }
              ]
            }
          }
        ]
      }
    });

/// API エラーレスポンス
String _apiErrorResponse() => jsonEncode({
      'chart': {
        'error': {'code': 'Not Found', 'description': 'No fundamentals data'},
        'result': null,
      }
    });

/// result が空のレスポンス
String _emptyResultResponse() => jsonEncode({
      'chart': {
        'error': null,
        'result': null,
      }
    });

void main() {
  group('T5a: StockRepository - fetchCandles', () {
    // ===== 正常系 =====

    test('正常レスポンスで StockCandle リストが返される', () async {
      final client = MockClient((request) async {
        return http.Response(_validResponse('7203.T'), 200);
      });
      final repo = StockRepository(client: client);

      final candles = await repo.fetchCandles('7203.T');

      expect(candles.length, 3);
      expect(candles[0].open, closeTo(1000.0, 0.01));
      expect(candles[0].high, closeTo(1050.0, 0.01));
      expect(candles[0].low, closeTo(990.0, 0.01));
      expect(candles[0].close, closeTo(1030.0, 0.01));
      expect(candles[0].volume, closeTo(100000.0, 0.01));
    });

    test('タイムスタンプが UTC の DateTime に正しく変換される', () async {
      final client = MockClient((request) async {
        return http.Response(_validResponse('AAPL'), 200);
      });
      final repo = StockRepository(client: client);

      final candles = await repo.fetchCandles('AAPL');

      expect(candles[0].date.isUtc, isTrue);
      expect(
        candles[0].date,
        DateTime.fromMillisecondsSinceEpoch(1700000000 * 1000, isUtc: true),
      );
    });

    test('null 値の行はスキップされ有効データのみ返される', () async {
      final client = MockClient((request) async {
        return http.Response(_responseWithNulls(), 200);
      });
      final repo = StockRepository(client: client);

      final candles = await repo.fetchCandles('TEST');

      // index=1 は null なのでスキップ → 2件
      expect(candles.length, 2);
      expect(candles[0].close, closeTo(1030.0, 0.01));
      expect(candles[1].close, closeTo(1050.0, 0.01));
    });

    test('range パラメータが URL に含まれる', () async {
      Uri? capturedUri;
      final client = MockClient((request) async {
        capturedUri = request.url;
        return http.Response(_validResponse('7203.T'), 200);
      });
      final repo = StockRepository(client: client);

      await repo.fetchCandles('7203.T', range: '6mo');

      expect(capturedUri?.queryParameters['range'], '6mo');
      expect(capturedUri?.queryParameters['interval'], '1d');
    });

    // ===== 異常系 =====
    // 非同期Futureの例外には expectLater + throwsA を使用

    test('HTTP 404 で StockRepositoryException（銘柄が見つかりません）が投げられる', () async {
      final client = MockClient((request) async {
        return http.Response('Not Found', 404);
      });
      final repo = StockRepository(client: client);

      await expectLater(
        repo.fetchCandles('INVALID'),
        throwsA(predicate((e) =>
            e is StockRepositoryException &&
            e.message.contains('銘柄が見つかりません'))),
      );
    });

    test('HTTP 500 で StockRepositoryException（HTTPエラー）が投げられる', () async {
      final client = MockClient((request) async {
        return http.Response('Server Error', 500);
      });
      final repo = StockRepository(client: client);

      await expectLater(
        repo.fetchCandles('7203.T'),
        throwsA(predicate((e) =>
            e is StockRepositoryException && e.message.contains('HTTPエラー'))),
      );
    });

    test('API error フィールドがある場合 StockRepositoryException が投げられる', () async {
      final client = MockClient((request) async {
        return http.Response(_apiErrorResponse(), 200);
      });
      final repo = StockRepository(client: client);

      await expectLater(
        repo.fetchCandles('UNKNOWN'),
        throwsA(predicate((e) =>
            e is StockRepositoryException && e.message.contains('API エラー'))),
      );
    });

    test('result が null の場合 StockRepositoryException（データなし）が投げられる', () async {
      final client = MockClient((request) async {
        return http.Response(_emptyResultResponse(), 200);
      });
      final repo = StockRepository(client: client);

      await expectLater(
        repo.fetchCandles('EMPTY'),
        throwsA(predicate((e) =>
            e is StockRepositoryException && e.message.contains('データなし'))),
      );
    });

    test('不正 JSON で StockRepositoryException（JSONパースエラー）が投げられる', () async {
      final client = MockClient((request) async {
        return http.Response('not json', 200);
      });
      final repo = StockRepository(client: client);

      await expectLater(
        repo.fetchCandles('7203.T'),
        throwsA(isA<StockRepositoryException>()),
      );
    });

    test('ネットワーク例外で StockRepositoryException（ネットワークエラー）が投げられる', () async {
      final client = MockClient((request) async {
        throw Exception('Connection refused');
      });
      final repo = StockRepository(client: client);

      await expectLater(
        repo.fetchCandles('7203.T'),
        throwsA(predicate((e) =>
            e is StockRepositoryException &&
            e.message.contains('ネットワークエラー'))),
      );
    });
  });
}

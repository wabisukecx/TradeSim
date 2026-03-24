import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/stock_candle.dart';

class StockRepositoryException implements Exception {
  final String message;
  const StockRepositoryException(this.message);
  @override
  String toString() => 'StockRepositoryException: $message';
}

class StockData {
  final List<StockCandle> candles;
  final String currency;
  const StockData({required this.candles, required this.currency});
}

/// Yahoo Finance v8 API を使った株価データ取得リポジトリ
class StockRepository {
  final http.Client _client;

  StockRepository({http.Client? client}) : _client = client ?? http.Client();

  static const String _baseUrl =
      'https://query1.finance.yahoo.com/v8/finance/chart';

  /// [symbol] の株価データを取得する。
  /// [range] は '3mo', '6mo', '1y', '2y' のいずれか。
  /// [symbol] の株価データと通貨情報を取得する。
  Future<StockData> fetchCandlesWithCurrency(
    String symbol, {
    String range = '1y',
  }) async {
    final uri = Uri.parse('$_baseUrl/$symbol?interval=1d&range=$range');

    late http.Response response;
    try {
      response = await _client.get(uri, headers: {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) '
            'AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148',
      });
    } catch (e) {
      throw StockRepositoryException('ネットワークエラー: $e');
    }

    if (response.statusCode == 404) {
      throw StockRepositoryException('銘柄が見つかりません: $symbol');
    }
    if (response.statusCode >= 400) {
      throw StockRepositoryException(
          'HTTPエラー ${response.statusCode}: $symbol');
    }

    Map<String, dynamic> json;
    try {
      json = jsonDecode(response.body) as Map<String, dynamic>;
    } catch (e) {
      throw StockRepositoryException('JSONパースエラー: $e');
    }

    try {
      final chart = json['chart'] as Map<String, dynamic>;
      final error = chart['error'];
      if (error != null) {
        throw StockRepositoryException(
            'API エラー: ${(error as Map)['description'] ?? error}');
      }

      // Yahoo Finance v8 API は通常 result[0] に目的のデータを返す。
      // 複数市場重複上場銘柄で複数 result が返るケースがあるが、
      // このアプリでは主要上場市場の最初のデータのみを使用する（設計上の制約）。
      final result = (chart['result'] as List?)?.first as Map<String, dynamic>?;
      if (result == null) {
        throw StockRepositoryException('データなし: $symbol');
      }

      final timestamps = result['timestamp'] as List?;
      if (timestamps == null || timestamps.isEmpty) {
        throw StockRepositoryException('価格データが0件: $symbol');
      }

      final indicators = result['indicators'] as Map<String, dynamic>;
      final quote =
          (indicators['quote'] as List).first as Map<String, dynamic>;

      final opens = quote['open'] as List;
      final highs = quote['high'] as List;
      final lows = quote['low'] as List;
      final closes = quote['close'] as List;
      final volumes = quote['volume'] as List;

      final candles = <StockCandle>[];
      for (int i = 0; i < timestamps.length; i++) {
        final o = (opens[i] as num?)?.toDouble();
        final h = (highs[i] as num?)?.toDouble();
        final l = (lows[i] as num?)?.toDouble();
        final c = (closes[i] as num?)?.toDouble();
        final v = (volumes[i] as num?)?.toDouble();

        // null値をスキップ
        if (o == null || h == null || l == null || c == null || v == null) {
          continue;
        }

        final date = DateTime.fromMillisecondsSinceEpoch(
          (timestamps[i] as int) * 1000,
          isUtc: true,
        );

        candles.add(StockCandle(
          date: date,
          open: o,
          high: h,
          low: l,
          close: c,
          volume: v,
        ));
      }

      if (candles.isEmpty) {
        throw StockRepositoryException('有効な価格データが0件: $symbol');
      }

      // meta から通貨情報を取得（例: 'JPY', 'USD'）
      final meta = result['meta'] as Map<String, dynamic>?;
      final currency = (meta?['currency'] as String?) ?? 'JPY';

      return StockData(candles: candles, currency: currency);
    } on StockRepositoryException {
      rethrow;
    } catch (e) {
      throw StockRepositoryException('データ解析エラー: $e');
    }
  }
}

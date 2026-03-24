import 'dart:convert';
import 'dart:isolate';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

class JQuantsException implements Exception {
  final String message;
  const JQuantsException(this.message);
  @override
  String toString() => 'JQuantsException: $message';
}

class StockInfo {
  final String symbol;
  final String name;
  final String nameEn;
  final String market;
  final String matchType;

  const StockInfo({
    required this.symbol,
    required this.name,
    required this.nameEn,
    required this.market,
    required this.matchType,
  });
}

/// JQuants API V2 リポジトリ
/// 認証方式: ダッシュボードから発行する API キー (x-api-key ヘッダー)
/// 2025/12/22以降登録のアカウントは V2 のみ対応
class JQuantsRepository {
  final http.Client _client;
  final FlutterSecureStorage _storage;
  final SharedPreferences? _prefs;

  static const String _baseUrl = 'https://api.jquants.com/v2';
  static const String _keyApiKey = 'jquants_api_key';

  // 銘柄マスターキャッシュ用キー
  static const String _keyCacheBody = 'jquants_master_cache_body';
  static const String _keyCacheTs = 'jquants_master_cache_ts';
  // キャッシュ有効期間: 1時間
  static const int _cacheTtlMs = 60 * 60 * 1000;

  // V2 エンドポイント (公式仕様: https://jpx-jquants.com/ja/spec/migration-v1-v2)
  // 上場銘柄一覧: /v2/equities/master  (V1: /v1/listed/info から変更)
  // 株価四本値:   /v2/equities/bars/daily (V1: /v1/prices/daily_quotes から変更)
  static const String _endpointMaster = '/equities/master';

  JQuantsRepository({
    http.Client? client,
    FlutterSecureStorage? storage,
    SharedPreferences? prefs,
  })  : _client = client ?? http.Client(),
        _storage = storage ?? const FlutterSecureStorage(),
        _prefs = prefs;

  // ===== API キーの保存・読み込み・削除 =====

  Future<void> saveApiKey(String apiKey) async {
    await _storage.write(key: _keyApiKey, value: apiKey);
  }

  Future<String?> loadApiKey() async {
    return _storage.read(key: _keyApiKey);
  }

  Future<void> clearApiKey() async {
    await _storage.delete(key: _keyApiKey);
  }

  /// 保存済み API キーの有無を確認する
  Future<bool> hasApiKey() async {
    final key = await loadApiKey();
    return key != null && key.isNotEmpty;
  }

  // ===== 接続テスト =====

  /// API キーが有効かどうかを検証する (銘柄マスター 1件取得で確認)
  Future<void> verifyApiKey(String apiKey) async {
    final response = await _client.get(
      Uri.parse('$_baseUrl$_endpointMaster?code=72030'),
      headers: {'x-api-key': apiKey},
    );
    if (response.statusCode == 401 || response.statusCode == 403) {
      throw const JQuantsException('API キーが無効です。ダッシュボードで発行したキーを確認してください');
    }
    if (response.statusCode != 200) {
      throw JQuantsException('接続エラー: ${response.statusCode}');
    }
  }

  // ===== 銘柄検索 =====

  /// [keyword] で日本株を検索する
  /// [apiKey] が指定されなければストレージから読み込む
  Future<List<StockInfo>> search(
    String keyword, {
    String? apiKey,
  }) async {
    final key = apiKey ?? await loadApiKey();
    if (key == null || key.isEmpty) {
      throw const JQuantsException('API キーが設定されていません');
    }

    // 銘柄マスター全件取得 (V2エンドポイント: /v2/equities/master)
    // キャッシュヒット確認（TTL: 1時間）
    String? responseBody = _loadCachedMaster();
    if (responseBody == null) {
      // キャッシュなし / 期限切れ → API 取得
      final response = await _client.get(
        Uri.parse('$_baseUrl$_endpointMaster'),
        headers: {'x-api-key': key},
      );

      if (response.statusCode == 401 || response.statusCode == 403) {
        throw const JQuantsException(
            'API キーが無効または期限切れです。ダッシュボードで新しいキーを発行してください');
      }
      if (response.statusCode == 429) {
        throw const JQuantsException(
            'リクエスト制限に達しました（Free プラン: 5回/分）。\n少し待ってから再検索してください。');
      }
      if (response.statusCode != 200) {
        throw JQuantsException('銘柄マスター取得エラー: ${response.statusCode}');
      }

      responseBody = response.body;
      _saveCachedMaster(responseBody);
    }

    // JSONデコードを isolate で実行 (4000社超のJSON処理)
    // V2レスポンス形式: { "data": [ {...}, ... ] } (V1は "info" キーだったが V2 は "data" キーに統一)
    final body = responseBody;
    final companies = await Isolate.run(() {
      final data = jsonDecode(body) as Map<String, dynamic>;
      return (data['data'] as List).cast<Map<String, dynamic>>();
    });

    // キーワードフィルタリング (Python版と同一ロジック)
    final keywordLower = keyword.toLowerCase();
    final results = <({StockInfo info, int score})>[];

    for (final company in companies) {
      // V2 カラム名 (公式: https://github.com/J-Quants/jquants-api-client-python)
      // V1: CompanyName / CompanyNameEnglish / MarketCode
      // V2: CoName      / CoNameEn            / Mkt
      final rawSymbol = (company['Code'] ?? '') as String;
      final nameJp = (company['CoName'] ?? '') as String;
      final nameEn = (company['CoNameEn'] ?? '') as String;
      // V2: Mkt=市場コード数値, MktNm=市場名文字列（「東証プライム」等）
      final marketName = (company['MktNm'] ?? '') as String;

      int score = 0;
      String matchType = '';

      if (nameJp.toLowerCase().contains(keywordLower)) {
        score = 3;
        matchType = 'JQuants(日本語社名)';
      } else if (nameEn.toLowerCase().contains(keywordLower)) {
        score = 2;
        matchType = 'JQuants(英語社名)';
      } else if (rawSymbol.toLowerCase().contains(keywordLower)) {
        score = 1;
        matchType = 'JQuants(銘柄コード)';
      }

      if (score == 0) continue;

      // 銘柄コード正規化 (5桁→4桁, .T付与)
      String symbolNormalized;
      if (rawSymbol.isNotEmpty && RegExp(r'^\d+$').hasMatch(rawSymbol)) {
        final code = rawSymbol.length == 5
            ? rawSymbol.substring(0, 4)
            : rawSymbol.length == 4
                ? rawSymbol
                : rawSymbol.length > 4
                    ? rawSymbol.substring(0, 4)
                    : rawSymbol.padLeft(4, '0');
        symbolNormalized = '$code.T';
      } else {
        symbolNormalized = rawSymbol;
      }

      results.add((
        info: StockInfo(
          symbol: symbolNormalized,
          name: nameJp,
          nameEn: nameEn.isEmpty ? 'N/A' : nameEn,
          market: marketName.isEmpty ? '東証' : marketName,
          matchType: matchType,
        ),
        score: score,
      ));
    }

    // スコア順ソートして上位5件
    results.sort((a, b) => b.score.compareTo(a.score));
    return results.take(5).map((r) => r.info).toList();
  }

  // ===== 銘柄マスターキャッシュ =====

  /// キャッシュが有効な場合はレスポンスボディを返す。期限切れ・未設定は null。
  String? _loadCachedMaster() {
    if (_prefs == null) return null;
    final ts = _prefs.getInt(_keyCacheTs);
    if (ts == null) return null;
    final now = DateTime.now().millisecondsSinceEpoch;
    if (now - ts > _cacheTtlMs) return null;
    return _prefs.getString(_keyCacheBody);
  }

  /// レスポンスボディと取得タイムスタンプを SharedPreferences に保存する。
  void _saveCachedMaster(String body) {
    if (_prefs == null) return;
    _prefs.setString(_keyCacheBody, body);
    _prefs.setInt(_keyCacheTs, DateTime.now().millisecondsSinceEpoch);
  }

  /// キャッシュを手動でクリアする（APIキー変更時などに利用）。
  Future<void> clearMasterCache() async {
    await _prefs?.remove(_keyCacheBody);
    await _prefs?.remove(_keyCacheTs);
  }
}

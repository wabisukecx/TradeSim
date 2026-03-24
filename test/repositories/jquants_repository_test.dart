// T5b: JQuantsRepository テスト
// - APIキーの保存・読み込み（FlutterSecureStorageモック使用）
// - キャッシュロジック（SharedPreferencesインメモリ使用）
// - 銘柄検索フィルタリング（MockClient使用）
// - エラーハンドリング（4xx/429レスポンス）
//
// 注意: JQuantsRepository.search() は内部で Isolate.run() を使用しているため
//       テストは flutter_test の isolate サポートに依存する。
//       Isolate.run() を回避するためモックレスポンスはキャッシュ経由で渡す設計。
import 'dart:convert';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:trade_sim_flutter/repositories/jquants_repository.dart';

// http.Response は Latin-1 がデフォルトのため、日本語を含むレスポンスは
// utf8 エンコード済みバイト列 + headers: {'content-type': 'application/json; charset=utf-8'}
// で生成する必要がある。
http.Response _utf8Response(String body, int statusCode) {
  return http.Response.bytes(
    utf8.encode(body),
    statusCode,
    headers: {'content-type': 'application/json; charset=utf-8'},
  );
}

// ===== FlutterSecureStorage インメモリモック =====

class _MockSecureStorage extends FlutterSecureStorage {
  final Map<String, String> _store = {};

  @override
  Future<void> write({
    required String key,
    required String? value,
    IOSOptions? iOptions,
    AndroidOptions? aOptions,
    LinuxOptions? lOptions,
    WebOptions? webOptions,
    MacOsOptions? mOptions,
    WindowsOptions? wOptions,
  }) async {
    if (value == null) {
      _store.remove(key);
    } else {
      _store[key] = value;
    }
  }

  @override
  Future<String?> read({
    required String key,
    IOSOptions? iOptions,
    AndroidOptions? aOptions,
    LinuxOptions? lOptions,
    WebOptions? webOptions,
    MacOsOptions? mOptions,
    WindowsOptions? wOptions,
  }) async =>
      _store[key];

  @override
  Future<void> delete({
    required String key,
    IOSOptions? iOptions,
    AndroidOptions? aOptions,
    LinuxOptions? lOptions,
    WebOptions? webOptions,
    MacOsOptions? mOptions,
    WindowsOptions? wOptions,
  }) async {
    _store.remove(key);
  }
}

// ===== テスト用 JQuants V2 モックレスポンス =====

/// 正常レスポンス: 複数銘柄の銘柄マスター（V2形式）
String _masterResponse() => jsonEncode({
      'data': [
        {
          'Code': '72030',
          'CoName': 'トヨタ自動車',
          'CoNameEn': 'Toyota Motor Corp',
          'Mkt': '0101',
          'MktNm': '東証プライム',
        },
        {
          'Code': '67580',
          'CoName': 'ソニーグループ',
          'CoNameEn': 'Sony Group Corp',
          'Mkt': '0101',
          'MktNm': '東証プライム',
        },
        {
          'Code': '99840',
          'CoName': '任天堂',
          'CoNameEn': 'Nintendo Co Ltd',
          'Mkt': '0101',
          'MktNm': '東証プライム',
        },
        {
          'Code': '00010',
          'CoName': 'テスト短コード',
          'CoNameEn': 'Test Short Code',
          'Mkt': '0103',
          'MktNm': '東証グロース',
        },
      ]
    });

// ===== ヘルパー =====

/// JQuants リポジトリを生成する
Future<(JQuantsRepository, SharedPreferences)> _buildRepo(
  http.Client client,
) async {
  SharedPreferences.setMockInitialValues({});
  final prefs = await SharedPreferences.getInstance();
  final storage = _MockSecureStorage();
  final repo = JQuantsRepository(
    client: client,
    storage: storage,
    prefs: prefs,
  );
  return (repo, prefs);
}

/// SharedPreferences にキャッシュを直接書き込む（Isolate.run() 経由を避けるため）
/// search() 初回呼び出しで API → Isolate.run() が走るので、
/// 検索テストはすべて API 経由（Isolate.run()）で正しく動作することを検証する。
void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  // ===== APIキー管理 =====

  group('T5b: JQuantsRepository - APIキー管理', () {
    test('saveApiKey → loadApiKey で保存した値が取得できる', () async {
      final (repo, _) = await _buildRepo(
          MockClient((_) async => http.Response('', 200)));

      await repo.saveApiKey('test-api-key-123');
      final loaded = await repo.loadApiKey();

      expect(loaded, 'test-api-key-123');
    });

    test('clearApiKey 後は loadApiKey が null を返す', () async {
      final (repo, _) = await _buildRepo(
          MockClient((_) async => http.Response('', 200)));

      await repo.saveApiKey('test-api-key-123');
      await repo.clearApiKey();
      final loaded = await repo.loadApiKey();

      expect(loaded, isNull);
    });

    test('hasApiKey: キーあり → true', () async {
      final (repo, _) = await _buildRepo(
          MockClient((_) async => http.Response('', 200)));

      await repo.saveApiKey('valid-key');
      expect(await repo.hasApiKey(), isTrue);
    });

    test('hasApiKey: キーなし → false', () async {
      final (repo, _) = await _buildRepo(
          MockClient((_) async => http.Response('', 200)));

      expect(await repo.hasApiKey(), isFalse);
    });
  });

  // ===== verifyApiKey =====

  group('T5b: JQuantsRepository - verifyApiKey', () {
    test('200 OK でエラーが投げられない（completes）', () async {
      final (repo, _) = await _buildRepo(MockClient((_) async =>
          _utf8Response(_masterResponse(), 200)));

      // Future<void> なので completes マッチャーを使用
      await expectLater(repo.verifyApiKey('valid-key'), completes);
    });

    test('401 で JQuantsException（キー無効）が投げられる', () async {
      final (repo, _) = await _buildRepo(
          MockClient((_) async => http.Response('Unauthorized', 401)));

      await expectLater(
        repo.verifyApiKey('bad-key'),
        throwsA(predicate((e) =>
            e is JQuantsException && e.message.contains('API キーが無効'))),
      );
    });

    test('403 で JQuantsException が投げられる', () async {
      final (repo, _) = await _buildRepo(
          MockClient((_) async => http.Response('Forbidden', 403)));

      await expectLater(
        repo.verifyApiKey('bad-key'),
        throwsA(isA<JQuantsException>()),
      );
    });
  });

  // ===== search 正常系 =====

  group('T5b: JQuantsRepository - search 正常系', () {
    test('日本語社名で検索: トヨタ → 7203.T が最上位に返る', () async {
      final (repo, _) = await _buildRepo(MockClient((_) async =>
          _utf8Response(_masterResponse(), 200)));

      final results = await repo.search('トヨタ', apiKey: 'test-key');

      expect(results, isNotEmpty);
      expect(results.first.symbol, '7203.T');
      expect(results.first.name, 'トヨタ自動車');
      expect(results.first.market, '東証プライム');
    });

    test('英語社名で検索: Sony → ソニーグループが返る（symbol: 6758.T）', () async {
      final (repo, _) = await _buildRepo(MockClient((_) async =>
          _utf8Response(_masterResponse(), 200)));

      final results = await repo.search('Sony', apiKey: 'test-key');

      expect(results, isNotEmpty);
      expect(results.first.symbol, '6758.T');
    });

    test('コードで検索: 9984 → 99840（任天堂）がヒットする', () async {
      final (repo, _) = await _buildRepo(MockClient((_) async =>
          _utf8Response(_masterResponse(), 200)));

      final results = await repo.search('9984', apiKey: 'test-key');

      // '9984' は '99840'（任天堂のコード）に含まれるのでヒットする
      expect(results, isNotEmpty);
      expect(results.first.symbol, '9984.T');
    });

    test('ヒットなしキーワードで空リストが返る', () async {
      final (repo, _) = await _buildRepo(MockClient((_) async =>
          _utf8Response(_masterResponse(), 200)));

      final results = await repo.search('XYZNOTEXIST', apiKey: 'test-key');

      expect(results, isEmpty);
    });

    test('10件ヒットしても最大5件に制限される', () async {
      // CoName に日本語を含まないASCIIのみのデータで生成（Latin-1対応のため）
      final bigMaster = jsonEncode({
        'data': List.generate(
          10,
          (i) => {
            'Code': '${10000 + i}',
            'CoName': 'TestCorp$i',
            'CoNameEn': 'Test Corp $i',
            'Mkt': '0101',
            'MktNm': 'Prime',
          },
        ),
      });
      // ASCII のみなので通常の http.Response でも可
      final (repo, _) = await _buildRepo(MockClient((_) async =>
          http.Response(bigMaster, 200)));

      final results = await repo.search('TestCorp', apiKey: 'test-key');

      expect(results.length, lessThanOrEqualTo(5));
    });
  });

  // ===== 銘柄コード正規化 =====

  group('T5b: JQuantsRepository - 銘柄コード正規化', () {
    test('5桁コード(72030) → 4桁 + .T (7203.T) に正規化される', () async {
      final (repo, _) = await _buildRepo(MockClient((_) async =>
          _utf8Response(_masterResponse(), 200)));

      final results = await repo.search('トヨタ', apiKey: 'test-key');

      expect(results.first.symbol, '7203.T');
    });

    test('4桁コード(0001) → そのまま .T を付与 (0001.T) になる', () async {
      // ASCII のみのマスターで確認（Latin-1対応）
      final shortMaster = jsonEncode({
        'data': [
          {
            'Code': '0001',
            'CoName': 'ShortCodeTest',
            'CoNameEn': 'Short Code Test',
            'Mkt': '0101',
            'MktNm': 'Prime',
          }
        ]
      });
      final (repo, _) = await _buildRepo(MockClient((_) async =>
          http.Response(shortMaster, 200)));

      final results = await repo.search('ShortCodeTest', apiKey: 'test-key');

      expect(results.first.symbol, '0001.T');
    });
  });

  // ===== キャッシュ =====

  group('T5b: JQuantsRepository - キャッシュ', () {
    test('1回目はAPIを呼び、2回目はキャッシュから返す（API呼び出し回数=1）', () async {
      int callCount = 0;
      final (repo, _) = await _buildRepo(MockClient((_) async {
        callCount++;
        return _utf8Response(_masterResponse(), 200);
      }));

      await repo.search('トヨタ', apiKey: 'test-key'); // 1回目: API 呼び出し
      await repo.search('ソニー', apiKey: 'test-key'); // 2回目: キャッシュヒット

      expect(callCount, 1);
    });

    test('clearMasterCache 後は再度 API を呼ぶ（API呼び出し回数=2）', () async {
      int callCount = 0;
      final (repo, _) = await _buildRepo(MockClient((_) async {
        callCount++;
        return _utf8Response(_masterResponse(), 200);
      }));

      await repo.search('トヨタ', apiKey: 'test-key');
      await repo.clearMasterCache();
      await repo.search('ソニー', apiKey: 'test-key');

      expect(callCount, 2);
    });
  });

  // ===== エラーハンドリング =====

  group('T5b: JQuantsRepository - エラーハンドリング', () {
    test('APIキー未設定で JQuantsException（API キーが設定されていません）が投げられる', () async {
      final (repo, _) = await _buildRepo(
          MockClient((_) async => http.Response('', 200)));

      await expectLater(
        repo.search('トヨタ'), // apiKey 引数なし・ストレージにも未保存
        throwsA(predicate((e) =>
            e is JQuantsException &&
            e.message.contains('API キーが設定されていません'))),
      );
    });

    test('401 で JQuantsException（API キーが無効または期限切れ）が投げられる', () async {
      final (repo, _) = await _buildRepo(
          MockClient((_) async => http.Response('Unauthorized', 401)));

      await expectLater(
        repo.search('トヨタ', apiKey: 'bad-key'),
        throwsA(predicate((e) =>
            e is JQuantsException && e.message.contains('API キーが無効'))),
      );
    });

    test('429 で JQuantsException（リクエスト制限）が投げられる', () async {
      final (repo, _) = await _buildRepo(
          MockClient((_) async => http.Response('Too Many Requests', 429)));

      await expectLater(
        repo.search('トヨタ', apiKey: 'valid-key'),
        throwsA(predicate((e) =>
            e is JQuantsException && e.message.contains('リクエスト制限'))),
      );
    });

    test('500 で JQuantsException（銘柄マスター取得エラー）が投げられる', () async {
      final (repo, _) = await _buildRepo(
          MockClient((_) async => http.Response('Server Error', 500)));

      await expectLater(
        repo.search('トヨタ', apiKey: 'valid-key'),
        throwsA(predicate((e) =>
            e is JQuantsException && e.message.contains('銘柄マスター取得エラー'))),
      );
    });
  });
}

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:url_launcher/url_launcher.dart';

import '../providers/providers.dart';
import '../repositories/jquants_repository.dart';

class SearchScreen extends ConsumerStatefulWidget {
  const SearchScreen({super.key});

  @override
  ConsumerState<SearchScreen> createState() => _SearchScreenState();
}

class _SearchScreenState extends ConsumerState<SearchScreen> {
  final _apiKeyController = TextEditingController();
  final _keywordController = TextEditingController();

  bool _obscureApiKey = true;
  bool _isSearching = false;
  bool _isSaving = false;
  bool _hasStoredKey = false;
  String? _error;
  String? _saveMessage;
  List<StockInfo> _results = [];

  @override
  void initState() {
    super.initState();
    _loadApiKey();
  }

  Future<void> _loadApiKey() async {
    final repo = ref.read(jquantsRepositoryProvider);
    final key = await repo.loadApiKey();
    if (mounted) {
      setState(() {
        _hasStoredKey = key != null && key.isNotEmpty;
        if (key != null) _apiKeyController.text = key;
      });
    }
  }

  Future<void> _saveApiKey() async {
    final key = _apiKeyController.text.trim();
    if (key.isEmpty) return;

    setState(() {
      _isSaving = true;
      _error = null;
      _saveMessage = null;
    });

    try {
      final repo = ref.read(jquantsRepositoryProvider);
      // 接続テストを行ってから保存
      await repo.verifyApiKey(key);
      await repo.saveApiKey(key);
      if (mounted) {
        setState(() {
          _isSaving = false;
          _hasStoredKey = true;
          _saveMessage = '✅ API キーを保存しました';
        });
      }
    } on JQuantsException catch (e) {
      if (mounted) {
        setState(() {
          _isSaving = false;
          _error = e.message;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _isSaving = false;
          _error = e.toString();
        });
      }
    }
  }

  Future<void> _clearApiKey() async {
    final repo = ref.read(jquantsRepositoryProvider);
    await repo.clearApiKey();
    if (mounted) {
      setState(() {
        _apiKeyController.clear();
        _hasStoredKey = false;
        _saveMessage = null;
        _results = [];
      });
    }
  }

  Future<void> _search() async {
    final keyword = _keywordController.text.trim();
    if (keyword.isEmpty) return;

    // APIキー未設定の場合はエラー表示
    if (!_hasStoredKey) {
      setState(() {
        _error = 'API キーが未設定です。上の「API キー設定」から保存してください';
      });
      return;
    }

    setState(() {
      _isSearching = true;
      _error = null;
      _results = [];
    });

    try {
      final repo = ref.read(jquantsRepositoryProvider);
      // コントローラのキーを直接渡す（ストレージの読み込みに失敗しても動ぐ）
      final apiKey = _apiKeyController.text.trim();
      final results = await repo.search(keyword, apiKey: apiKey.isNotEmpty ? apiKey : null);
      if (mounted) {
        setState(() {
          _results = results;
          _isSearching = false;
        });
      }
    } on JQuantsException catch (e) {
      if (mounted) {
        setState(() {
          _error = e.message;
          _isSearching = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _error = e.toString();
          _isSearching = false;
        });
      }
    }
  }

  Future<void> _openJQuantsSignup() async {
    final uri = Uri.parse('https://jpx-jquants.com/');
    if (await canLaunchUrl(uri)) {
      await launchUrl(uri, mode: LaunchMode.externalApplication);
    }
  }

  Future<void> _openJQuantsDashboard() async {
    final uri = Uri.parse('https://jpx-jquants.com/dashboard/');
    if (await canLaunchUrl(uri)) {
      await launchUrl(uri, mode: LaunchMode.externalApplication);
    }
  }

  @override
  void dispose() {
    _apiKeyController.dispose();
    _keywordController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('銘柄検索 (JQuants)')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // ===== J-Quants 案内バナー（APIキー未設定時のみ表示）=====
            if (!_hasStoredKey) ...[  
              _JQuantsInfoBanner(
                onSignup: _openJQuantsSignup,
                onDashboard: _openJQuantsDashboard,
              ),
              const SizedBox(height: 16),
            ],

            // ===== API キー設定カード =====
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        const Icon(Icons.vpn_key,
                            size: 18, color: Color(0xFF1565C0)),
                        const SizedBox(width: 6),
                        Text('API キー設定',
                            style: Theme.of(context).textTheme.titleMedium),
                        const Spacer(),
                        if (_hasStoredKey)
                          Chip(
                            label: const Text('設定済み',
                                style: TextStyle(fontSize: 11)),
                            backgroundColor: Colors.green[50],
                            side: BorderSide(color: Colors.green[300]!),
                          ),
                      ],
                    ),
                    const SizedBox(height: 12),
                    TextField(
                      controller: _apiKeyController,
                      decoration: InputDecoration(
                        labelText: 'API キー',
                        hintText: 'ダッシュボードで発行した API キーを入力',
                        prefixIcon: const Icon(Icons.key),
                        border: const OutlineInputBorder(),
                        suffixIcon: Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            IconButton(
                              icon: Icon(_obscureApiKey
                                  ? Icons.visibility
                                  : Icons.visibility_off),
                              onPressed: () => setState(
                                  () => _obscureApiKey = !_obscureApiKey),
                              tooltip: '表示/非表示',
                            ),
                            if (_apiKeyController.text.isNotEmpty)
                              IconButton(
                                icon: const Icon(Icons.copy, size: 18),
                                onPressed: () {
                                  Clipboard.setData(ClipboardData(
                                      text: _apiKeyController.text));
                                  ScaffoldMessenger.of(context).showSnackBar(
                                    const SnackBar(
                                        content: Text('コピーしました'),
                                        duration: Duration(seconds: 1)),
                                  );
                                },
                                tooltip: 'コピー',
                              ),
                          ],
                        ),
                      ),
                      obscureText: _obscureApiKey,
                      onChanged: (_) => setState(() {}),
                    ),
                    const SizedBox(height: 12),
                    Row(
                      children: [
                        Expanded(
                          child: FilledButton.icon(
                            onPressed: _isSaving ||
                                    _apiKeyController.text.trim().isEmpty
                                ? null
                                : _saveApiKey,
                            icon: _isSaving
                                ? const SizedBox(
                                    width: 16,
                                    height: 16,
                                    child: CircularProgressIndicator(
                                        color: Colors.white, strokeWidth: 2))
                                : const Icon(Icons.save),
                            label:
                                Text(_isSaving ? '確認中...' : '保存・接続テスト'),
                          ),
                        ),
                        if (_hasStoredKey) ...[
                          const SizedBox(width: 8),
                          OutlinedButton.icon(
                            onPressed: _clearApiKey,
                            icon: const Icon(Icons.delete_outline,
                                color: Colors.red),
                            label: const Text('削除',
                                style: TextStyle(color: Colors.red)),
                            style: OutlinedButton.styleFrom(
                                side: const BorderSide(color: Colors.red)),
                          ),
                        ],
                      ],
                    ),
                    if (_saveMessage != null) ...[
                      const SizedBox(height: 8),
                      Text(_saveMessage!,
                          style: const TextStyle(color: Colors.green)),
                    ],
                  ],
                ),
              ),
            ),
            const SizedBox(height: 16),

            // ===== エラー表示 =====
            if (_error != null) ...[
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.red[50],
                  border: Border.all(color: Colors.red[200]!),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Row(
                  children: [
                    const Icon(Icons.error_outline,
                        color: Colors.red, size: 18),
                    const SizedBox(width: 8),
                    Expanded(
                        child: Text(_error!,
                            style: const TextStyle(color: Colors.red))),
                  ],
                ),
              ),
              const SizedBox(height: 12),
            ],

            // ===== 検索フォーム =====
            Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _keywordController,
                    decoration: const InputDecoration(
                      labelText: '銘柄名・コードで検索',
                      hintText: '例: トヨタ, 7203',
                      prefixIcon: Icon(Icons.search),
                      border: OutlineInputBorder(),
                    ),
                    onSubmitted: (_) => _search(),
                  ),
                ),
                const SizedBox(width: 12),
                FilledButton(
                  onPressed: _isSearching ? null : _search,
                  child: _isSearching
                      ? const SizedBox(
                          width: 20,
                          height: 20,
                          child: CircularProgressIndicator(
                              color: Colors.white, strokeWidth: 2),
                        )
                      : const Text('検索'),
                ),
              ],
            ),
            const SizedBox(height: 16),

            // ===== 検索結果 =====
            if (_results.isNotEmpty) ...[
              Text('検索結果 (${_results.length}件)',
                  style: Theme.of(context).textTheme.titleMedium),
              const SizedBox(height: 8),
              ListView.separated(
                shrinkWrap: true,
                physics: const NeverScrollableScrollPhysics(),
                itemCount: _results.length,
                separatorBuilder: (_, __) => const Divider(height: 1),
                itemBuilder: (context, index) {
                  final info = _results[index];
                  return ListTile(
                    leading: CircleAvatar(
                      backgroundColor: const Color(0xFF1565C0),
                      child: Text(
                        info.symbol.substring(0, 1),
                        style: const TextStyle(color: Colors.white),
                      ),
                    ),
                    title: Text(info.name,
                        style: const TextStyle(fontWeight: FontWeight.w600)),
                    subtitle: Text(
                        '${info.symbol}  ${info.market}  ${info.matchType}'),
                    trailing: const Icon(Icons.chevron_right),
                    onTap: () => context.pop(info.symbol),
                  );
                },
              ),
            ] else if (!_isSearching &&
                _keywordController.text.isNotEmpty &&
                _error == null) ...[
              const Center(
                child: Padding(
                  padding: EdgeInsets.all(32),
                  child: Text('検索結果が見つかりませんでした',
                      style: TextStyle(color: Colors.grey)),
                ),
              ),
            ],
            const SizedBox(height: 80),
          ],
        ),
      ),
    );
  }
}

// ===== J-Quants 案内バナー =====
class _JQuantsInfoBanner extends StatelessWidget {
  final VoidCallback onSignup;
  final VoidCallback onDashboard;

  const _JQuantsInfoBanner({
    required this.onSignup,
    required this.onDashboard,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [Colors.blue[700]!, Colors.blue[900]!],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(12),
      ),
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // ヘッダー
          Row(
            children: [
              Container(
                padding:
                    const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                decoration: BoxDecoration(
                  color: Colors.white.withValues(alpha: 0.2),
                  borderRadius: BorderRadius.circular(4),
                ),
                child: const Text(
                  '外部サービス',
                  style: TextStyle(
                      color: Colors.white,
                      fontSize: 10,
                      fontWeight: FontWeight.w600),
                ),
              ),
              const SizedBox(width: 8),
              const Text(
                'J-Quants API',
                style: TextStyle(
                    color: Colors.white,
                    fontSize: 16,
                    fontWeight: FontWeight.bold),
              ),
            ],
          ),
          const SizedBox(height: 8),
          // 説明文
          const Text(
            '日本取引所グループ（JPX）が提供する公式株式データサービスです。'
            'TradeSim とは別のサービスのため、別途アカウント登録が必要です。',
            style: TextStyle(
                color: Colors.white, fontSize: 12, height: 1.5),
          ),
          const SizedBox(height: 6),
          // 特徴 (公式仕様: https://jpx-jquants.com/ja/spec/data-spec)
          const _FeatureRow(
              icon: Icons.check_circle_outline,
              text: '無料プランで全上場銘柄（約4,000社）の銘柄情報を取得可能'),
          const _FeatureRow(
              icon: Icons.info_outline,
              text: '株価データの取得範囲は「12週間前〜2年前」。直近3ヶ月は有料プランのみ'),
          const _FeatureRow(
              icon: Icons.info_outline,
              text: 'APIキーはダッシュボードから発行。レートリミットは5リクエスト/分'),
          const SizedBox(height: 12),
          // ボタン行
          Row(
            children: [
              Expanded(
                child: OutlinedButton.icon(
                  onPressed: onSignup,
                  icon: const Icon(Icons.person_add,
                      size: 16, color: Colors.white),
                  label: const Text('無料アカウント登録',
                      style:
                          TextStyle(color: Colors.white, fontSize: 12)),
                  style: OutlinedButton.styleFrom(
                    side: const BorderSide(color: Colors.white60),
                    padding: const EdgeInsets.symmetric(vertical: 8),
                  ),
                ),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: OutlinedButton.icon(
                  onPressed: onDashboard,
                  icon: const Icon(Icons.open_in_new,
                      size: 16, color: Colors.white),
                  label: const Text('APIキー発行(ダッシュボード)',
                      style:
                          TextStyle(color: Colors.white, fontSize: 11)),
                  style: OutlinedButton.styleFrom(
                    side: const BorderSide(color: Colors.white60),
                    padding: const EdgeInsets.symmetric(vertical: 8),
                  ),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}

class _FeatureRow extends StatelessWidget {
  final IconData icon;
  final String text;
  const _FeatureRow({required this.icon, required this.text});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 4),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(icon, size: 14, color: Colors.white70),
          const SizedBox(width: 6),
          Expanded(
            child: Text(text,
                style: const TextStyle(
                    color: Colors.white70, fontSize: 11, height: 1.4)),
          ),
        ],
      ),
    );
  }
}

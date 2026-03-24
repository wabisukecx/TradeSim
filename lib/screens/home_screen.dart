import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:shared_preferences/shared_preferences.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final _symbolController = TextEditingController();
  String _selectedRange = '1y';

  static const _ranges = ['3mo', '6mo', '1y', '2y'];
  static const _rangeLabels = {
    '3mo': '3ヶ月',
    '6mo': '6ヶ月',
    '1y': '1年',
    '2y': '2年',
  };

  // SegmentedButton に収まるよう短縮表記を使用
  static const _rangeShortLabels = {
    '3mo': '3M',
    '6mo': '6M',
    '1y': '1年',
    '2y': '2年',
  };

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) => _showDisclaimerIfNeeded());
  }

  Future<void> _showDisclaimerIfNeeded() async {
    final prefs = await SharedPreferences.getInstance();
    final agreed = prefs.getBool('disclaimer_agreed') ?? false;
    if (agreed || !mounted) return;

    final result = await showDialog<bool>(
      context: context,
      barrierDismissible: false,
      builder: (ctx) => AlertDialog(
        title: const Text('⚠️ ご利用前にお読みください'),
        content: const SingleChildScrollView(
          child: Text(
            'このアプリは株価テクニカル分析の学習・教育を目的としています。\n\n'
            '表示される分析結果・シグナル・バックテスト結果は、実際の投資判断の根拠とならないことをご理解ください。\n\n'
            '株式投資にはリスクが伴います。実際の投資は自己責任で行ってください。\n\n'
            '使用している株価データは非公式APIから取得しており、精度を保証するものではありません。',
          ),
        ),
        actions: [
          FilledButton(
            onPressed: () => Navigator.pop(ctx, true),
            child: const Text('同意して始める'),
          ),
        ],
      ),
    );

    if (result == true) {
      await prefs.setBool('disclaimer_agreed', true);
    }
  }

  @override
  void dispose() {
    _symbolController.dispose();
    super.dispose();
  }

  void _startAnalysis() {
    final symbol = _symbolController.text.trim().toUpperCase();
    if (symbol.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('銘柄コードを入力してください')),
      );
      return;
    }
    context.push(
      '/analysis/$symbol',
      extra: {'range': _selectedRange},
    );
  }

  void _reset() {
    setState(() {
      _symbolController.clear();
      _selectedRange = '1y';
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('TradeSim'),
        actions: [
          IconButton(
            icon: const Icon(Icons.search),
            tooltip: '銘柄検索',
            onPressed: () async {
              final result = await context.push<String>('/search');
              if (result != null && mounted) {
                _symbolController.text = result;
              }
            },
          ),
          IconButton(
            icon: const Icon(Icons.folder),
            tooltip: 'ポートフォリオ',
            onPressed: () => context.push('/portfolio'),
          ),
          IconButton(
            icon: const Icon(Icons.menu_book),
            tooltip: '用語説明',
            onPressed: () => context.push('/glossary'),
          ),
        ],
      ),
      body: Center(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24),
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 480),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                const Icon(Icons.candlestick_chart,
                    size: 72, color: Color(0xFF1565C0)),
                const SizedBox(height: 16),
                Text(
                  '株価テクニカル分析',
                  style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 8),
                Text(
                  '銘柄コードを入力して分析を開始してください',
                  style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                        color: Colors.grey[600],
                      ),
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 32),
                TextField(
                  controller: _symbolController,
                  decoration: InputDecoration(
                    labelText: '銘柄コード',
                    hintText: '例: 7203.T, AAPL',
                    prefixIcon: const Icon(Icons.business),
                    border: const OutlineInputBorder(),
                    suffixIcon: IconButton(
                      icon: const Icon(Icons.search),
                      onPressed: () async {
                        final result =
                            await context.push<String>('/search');
                        if (result != null && mounted) {
                          _symbolController.text = result;
                        }
                      },
                    ),
                  ),
                  textCapitalization: TextCapitalization.characters,
                  onSubmitted: (_) => _startAnalysis(),
                ),
                const SizedBox(height: 20),
                Text(
                  '分析期間',
                  style: Theme.of(context).textTheme.titleSmall,
                ),
                const SizedBox(height: 8),
                SegmentedButton<String>(
                  segments: _ranges
                      .map((r) => ButtonSegment<String>(
                            value: r,
                            label: Text(_rangeLabels[r]!),
                          ))
                      .toList(),
                  selected: {_selectedRange},
                  onSelectionChanged: (v) =>
                      setState(() => _selectedRange = v.first),
                  // チェックアイコンを非表示にして幅を確保
                  showSelectedIcon: false,
                ),
                const SizedBox(height: 32),
                FilledButton.icon(
                  onPressed: _startAnalysis,
                  icon: const Icon(Icons.analytics),
                  label: const Text('分析開始'),
                  style: FilledButton.styleFrom(
                    padding: const EdgeInsets.symmetric(vertical: 16),
                  ),
                ),
                const SizedBox(height: 12),
                OutlinedButton.icon(
                  onPressed: _reset,
                  icon: const Icon(Icons.refresh),
                  label: const Text('リセット'),
                ),
                const SizedBox(height: 24),
                Card(
                  color: Colors.amber[50],
                  child: const Padding(
                    padding: EdgeInsets.all(12),
                    child: Text(
                      '⚠️ この分析結果は教育・学習目的のみです。実際の投資判断は専門家にご相談ください。',
                      style: TextStyle(fontSize: 12),
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

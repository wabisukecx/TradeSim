import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:intl/intl.dart';

import '../providers/providers.dart';

class PortfolioScreen extends ConsumerWidget {
  const PortfolioScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final items = ref.watch(portfolioProvider);
    final notifier = ref.read(portfolioProvider.notifier);

    return Scaffold(
      appBar: AppBar(
        title: const Text('ウォッチリスト'),
        actions: [
          IconButton(
            icon: const Icon(Icons.add),
            tooltip: '銘柄追加',
            onPressed: () => _showAddDialog(context, notifier),
          ),
        ],
      ),
      body: items.isEmpty
          ? Center(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  const Icon(Icons.folder_open,
                      size: 72, color: Colors.grey),
                  const SizedBox(height: 16),
                  const Text('ウォッチリストが空です',
                      style: TextStyle(color: Colors.grey)),
                  const SizedBox(height: 16),
                  FilledButton.icon(
                    icon: const Icon(Icons.add),
                    label: const Text('銘柄を追加'),
                    onPressed: () => _showAddDialog(context, notifier),
                  ),
                ],
              ),
            )
          : ListView.separated(
              itemCount: items.length,
              separatorBuilder: (_, __) => const Divider(height: 1),
              itemBuilder: (context, index) {
                final item = items[index];
                return ListTile(
                  leading: const CircleAvatar(
                    backgroundColor: Color(0xFF1565C0),
                    child: Icon(Icons.show_chart, color: Colors.white, size: 20),
                  ),
                  title: Text(item.symbol,
                      style: const TextStyle(fontWeight: FontWeight.bold)),
                  subtitle: Text(
                    item.name ?? '追加日: ${DateFormat('yyyy/MM/dd').format(item.addedAt)}',
                  ),
                  trailing: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      IconButton(
                        icon: const Icon(Icons.analytics_outlined),
                        tooltip: '分析',
                        onPressed: () =>
                            _showRangeDialog(context, item.symbol),
                      ),
                      IconButton(
                        icon: const Icon(Icons.delete_outline),
                        tooltip: '削除',
                        onPressed: () => notifier.remove(item.symbol),
                        color: Colors.red,
                      ),
                    ],
                  ),
                );
              },
            ),
    );
  }

  Future<void> _showRangeDialog(BuildContext context, String symbol) async {
    const ranges = [
      ('3ヶ月', '3mo'),
      ('6ヶ月', '6mo'),
      ('1年', '1y'),
      ('2年', '2y'),
    ];

    final range = await showDialog<String>(
      context: context,
      builder: (ctx) => SimpleDialog(
        title: Text('$symbol の分析期間'),
        children: ranges
            .map((r) => SimpleDialogOption(
                  onPressed: () => Navigator.pop(ctx, r.$2),
                  child: Padding(
                    padding: const EdgeInsets.symmetric(vertical: 4),
                    child: Text(
                      r.$1,
                      style: const TextStyle(fontSize: 16),
                    ),
                  ),
                ))
            .toList(),
      ),
    );

    if (range != null && context.mounted) {
      context.push('/analysis/$symbol', extra: {'range': range});
    }
  }

  Future<void> _showAddDialog(
    BuildContext context,
    PortfolioNotifier notifier,
  ) async {
    // TextEditingController のライフサイクルを StatefulWidget に委ねることで
    // ダイアログ退場アニメーション中の _dependents.isEmpty アサーションを回避する
    final result = await showDialog<String>(
      context: context,
      builder: (ctx) => const _AddSymbolDialog(),
    );

    if (result != null && result.isNotEmpty) {
      notifier.add(result);
    }
  }
}

// -----------------------------------------------------------------------
// ダイアログ専用 StatefulWidget
// State.dispose() でコントローラーを安全に破棄する
// -----------------------------------------------------------------------
class _AddSymbolDialog extends StatefulWidget {
  const _AddSymbolDialog();

  @override
  State<_AddSymbolDialog> createState() => _AddSymbolDialogState();
}

class _AddSymbolDialogState extends State<_AddSymbolDialog> {
  final _controller = TextEditingController();

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: const Text('銘柄追加'),
      content: TextField(
        controller: _controller,
        decoration: const InputDecoration(
          labelText: '銘柄コード',
          hintText: '例: 7203.T, AAPL',
          border: OutlineInputBorder(),
        ),
        textCapitalization: TextCapitalization.characters,
        autofocus: true,
        onSubmitted: (v) =>
            Navigator.pop(context, v.trim().toUpperCase()),
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.pop(context),
          child: const Text('キャンセル'),
        ),
        FilledButton(
          onPressed: () =>
              Navigator.pop(context, _controller.text.trim().toUpperCase()),
          child: const Text('追加'),
        ),
      ],
    );
  }
}

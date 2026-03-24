import 'package:flutter/material.dart';

class GlossaryScreen extends StatelessWidget {
  const GlossaryScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('用語説明')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: const [
          _SectionHeader('テクニカル指標'),
          _TermCard(
            term: '移動平均線 (MA)',
            abbr: 'MA短期 (20日) / MA長期 (50日)',
            description:
                '過去N日間の終値の平均を線で繋いだもの。短期線が長期線を上抜ける「ゴールデンクロス」は買いサイン、下抜ける「デッドクロス」は売りサインとされます。',
            example: 'MA短期 > MA長期 → 上昇トレンドの可能性',
            color: Colors.blue,
            icon: Icons.trending_up,
          ),
          _TermCard(
            term: 'RSI（相対力指数）',
            abbr: 'Relative Strength Index',
            description:
                '価格の上昇・下落の勢いを0〜100の数値で表す指標。35以下は「売られすぎ（反発の可能性）」、65以上は「買われすぎ（調整の可能性）」を示します。',
            example: 'RSI = 22 → 売られすぎ圏。反発を示唆',
            color: Colors.purple,
            icon: Icons.speed,
          ),
          _TermCard(
            term: 'ボリンジャーバンド',
            abbr: 'BB上限 / BB下限',
            description:
                '移動平均線を中心に、価格の変動幅（標準偏差×2）で上下のバンドを描きます。価格がBB下限を下回ると売られすぎ、BB上限を上回ると買われすぎのサインです。',
            example: '終値 < BB下限 → 買いシグナルの可能性',
            color: Colors.teal,
            icon: Icons.bar_chart,
          ),
          _TermCard(
            term: 'MACD',
            abbr: 'Moving Average Convergence Divergence',
            description:
                '短期EMA（12日）と長期EMA（26日）の差（MACDライン）と、そのシグナルライン（9日EMA）の位置関係を見る指標。MACDがシグナルを上抜けると買い、下抜けると売りとされます。',
            example: 'MACDライン > シグナルライン → 上昇の勢い',
            color: Colors.orange,
            icon: Icons.show_chart,
          ),
          SizedBox(height: 16),
          _SectionHeader('シグナル'),
          _TermCard(
            term: '買いシグナル',
            abbr: 'signal = +1',
            description:
                '複数のテクニカル指標の買いスコア合計が閾値を超えた場合に発生します。MA・RSI・BB・MACDの重み付きスコアで判定されます。',
            example: 'buy_score ≥ 閾値 → 🟢 買いシグナル',
            color: Colors.green,
            icon: Icons.arrow_upward,
          ),
          _TermCard(
            term: '売りシグナル',
            abbr: 'signal = -1',
            description:
                '複数のテクニカル指標の売りスコア合計が閾値を超えた場合に発生します。',
            example: 'sell_score ≥ 閾値 → 🔴 売りシグナル',
            color: Colors.red,
            icon: Icons.arrow_downward,
          ),
          _TermCard(
            term: '中立',
            abbr: 'signal = 0',
            description: '買い・売りのいずれの閾値も超えていない状態。様子見の局面です。',
            example: '明確なトレンドなし → ⚪ 中立',
            color: Colors.grey,
            icon: Icons.remove,
          ),
          SizedBox(height: 16),
          _SectionHeader('バックテスト指標'),
          _TermCard(
            term: '総リターン',
            abbr: 'Total Return (%)',
            description:
                '初期資金に対する最終資産の増減率。プラスなら利益、マイナスなら損失を意味します。',
            example: '初期100万円 → 最終108万円 = +8%',
            color: Colors.blue,
            icon: Icons.percent,
          ),
          _TermCard(
            term: 'シャープレシオ',
            abbr: 'Sharpe Ratio',
            description:
                'リスク（価格変動の激しさ）に対してどれだけ効率よくリターンを得られたかを示す指標。1.0以上が良好、2.0以上が優秀とされます。',
            example: 'シャープレシオ 1.5 → リスクに見合ったリターン',
            color: Colors.indigo,
            icon: Icons.equalizer,
          ),
          _TermCard(
            term: '最大ドローダウン',
            abbr: 'Max Drawdown (%)',
            description:
                'バックテスト期間中に資産がピークから最大でどれだけ下落したかを示します。数値が大きいほどリスクが高い戦略です。',
            example: 'MDD -15% → 最悪時に資産が15%減少した',
            color: Colors.red,
            icon: Icons.trending_down,
          ),
          _TermCard(
            term: '勝率',
            abbr: 'Win Rate (%)',
            description:
                '決済した取引のうち、利益が出た取引の割合。60%以上あれば良好とされますが、損益比率（平均利益/平均損失）とセットで判断することが重要です。',
            example: '勝率60% × 利益2万 vs 敗率40% × 損失1万 → 期待値プラス',
            color: Colors.green,
            icon: Icons.sports_score,
          ),
          _TermCard(
            term: 'ストップロス / テイクプロフィット',
            abbr: 'Stop Loss / Take Profit',
            description:
                'ストップロスは損失を一定水準（デフォルト-5%）で自動的に確定させる設定。テイクプロフィットは利益を一定水準（デフォルト+10%）で自動的に確定させる設定です。',
            example: '買値1,000円 × SL-5% → 950円で自動損切り',
            color: Colors.orange,
            icon: Icons.shield,
          ),
          SizedBox(height: 32),
          _DisclaimerBox(),
          SizedBox(height: 16),
        ],
      ),
    );
  }
}

class _SectionHeader extends StatelessWidget {
  final String title;
  const _SectionHeader(this.title);

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(top: 8, bottom: 12),
      child: Row(
        children: [
          Container(
            width: 4,
            height: 20,
            decoration: BoxDecoration(
              color: const Color(0xFF1565C0),
              borderRadius: BorderRadius.circular(2),
            ),
          ),
          const SizedBox(width: 8),
          Text(title,
              style: const TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                  color: Color(0xFF1565C0))),
        ],
      ),
    );
  }
}

class _TermCard extends StatelessWidget {
  final String term;
  final String abbr;
  final String description;
  final String example;
  final Color color;
  final IconData icon;

  const _TermCard({
    required this.term,
    required this.abbr,
    required this.description,
    required this.example,
    required this.color,
    required this.icon,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      elevation: 1,
      child: Padding(
        padding: const EdgeInsets.all(14),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                CircleAvatar(
                  radius: 16,
                  backgroundColor: color.withValues(alpha: 0.15),
                  child: Icon(icon, size: 16, color: color),
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(term,
                          style: const TextStyle(
                              fontWeight: FontWeight.bold, fontSize: 15)),
                      Text(abbr,
                          style: TextStyle(
                              fontSize: 11, color: Colors.grey[600])),
                    ],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 10),
            Text(description,
                style: const TextStyle(fontSize: 13, height: 1.5)),
            const SizedBox(height: 8),
            Container(
              padding:
                  const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
              decoration: BoxDecoration(
                color: color.withValues(alpha: 0.07),
                borderRadius: BorderRadius.circular(6),
                border: Border.all(color: color.withValues(alpha: 0.3)),
              ),
              child: Row(
                children: [
                  Icon(Icons.lightbulb_outline, size: 13, color: color),
                  const SizedBox(width: 6),
                  Expanded(
                    child: Text(example,
                        style: TextStyle(
                            fontSize: 12,
                            color: color,
                            fontWeight: FontWeight.w500)),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _DisclaimerBox extends StatelessWidget {
  const _DisclaimerBox();

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: Colors.amber[50],
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.amber[300]!),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(Icons.warning_amber_rounded,
              color: Colors.amber[700], size: 20),
          const SizedBox(width: 10),
          const Expanded(
            child: Text(
              'このアプリの分析結果は教育・学習目的のみです。実際の投資判断は専門家にご相談ください。',
              style: TextStyle(fontSize: 12, height: 1.5),
            ),
          ),
        ],
      ),
    );
  }
}

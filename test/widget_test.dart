import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:trade_sim_flutter/main.dart';

void main() {
  testWidgets('App smoke test - HomeScreen loads', (WidgetTester tester) async {
    await tester.pumpWidget(const ProviderScope(child: TradeSimApp()));
    await tester.pumpAndSettle();
    // HomeScreen に TradeSim タイトルが表示されること
    expect(find.text('TradeSim'), findsOneWidget);
  });
}

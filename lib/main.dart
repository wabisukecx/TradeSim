import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'providers/providers.dart';
import 'screens/home_screen.dart';
import 'screens/search_screen.dart';
import 'screens/analysis_screen.dart';
import 'screens/backtest_screen.dart';
import 'screens/portfolio_screen.dart';
import 'screens/glossary_screen.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  late SharedPreferences prefs;
  try {
    prefs = await SharedPreferences.getInstance();
  } catch (e) {
    // SharedPreferences 初期化失敗時はメモリオンリーのフォールバックは困難なため
    // エラー画面を表示してアプリを安全に停止する
    runApp(MaterialApp(
      home: Scaffold(
        body: Center(
          child: Text('初期化エラー: ストレージにアクセスできません\n$e',
              textAlign: TextAlign.center),
        ),
      ),
    ));
    return;
  }
  runApp(
    ProviderScope(
      overrides: [
        sharedPreferencesProvider.overrideWithValue(prefs),
      ],
      child: const TradeSimApp(),
    ),
  );
}

final _router = GoRouter(
  routes: [
    GoRoute(
      path: '/',
      builder: (context, state) => const HomeScreen(),
    ),
    GoRoute(
      path: '/search',
      builder: (context, state) => const SearchScreen(),
    ),
    GoRoute(
      path: '/analysis/:symbol',
      builder: (context, state) {
        final symbol = state.pathParameters['symbol']!;
        final range =
            (state.extra as Map<String, dynamic>?)?['range'] as String? ?? '1y';
        return AnalysisScreen(symbol: symbol, range: range);
      },
    ),
    GoRoute(
      path: '/backtest/:symbol',
      builder: (context, state) {
        final symbol = state.pathParameters['symbol']!;
        final range =
            (state.extra as Map<String, dynamic>?)?['range'] as String? ?? '1y';
        return BacktestScreen(symbol: symbol, range: range);
      },
    ),
    GoRoute(
      path: '/portfolio',
      builder: (context, state) => const PortfolioScreen(),
    ),
    GoRoute(
      path: '/glossary',
      builder: (context, state) => const GlossaryScreen(),
    ),
  ],
);

class TradeSimApp extends StatelessWidget {
  const TradeSimApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp.router(
      title: 'TradeSim',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF1565C0),
          brightness: Brightness.light,
        ),
        useMaterial3: true,
        appBarTheme: const AppBarTheme(
          backgroundColor: Color(0xFF1565C0),
          foregroundColor: Colors.white,
          elevation: 2,
        ),
      ),
      routerConfig: _router,
    );
  }
}

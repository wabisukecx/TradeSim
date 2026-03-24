class PerformanceMetrics {
  final double totalReturnPct;
  final double sharpeRatio;
  final double maxDrawdown;
  final double winRate;
  final int totalTrades;
  final double initialCapital;
  final double finalValue;

  const PerformanceMetrics({
    required this.totalReturnPct,
    required this.sharpeRatio,
    required this.maxDrawdown,
    required this.winRate,
    required this.totalTrades,
    required this.initialCapital,
    required this.finalValue,
  });

  factory PerformanceMetrics.empty() {
    return const PerformanceMetrics(
      totalReturnPct: 0,
      sharpeRatio: 0,
      maxDrawdown: 0,
      winRate: 0,
      totalTrades: 0,
      initialCapital: 0,
      finalValue: 0,
    );
  }

  factory PerformanceMetrics.fromJson(Map<String, dynamic> json) {
    return PerformanceMetrics(
      totalReturnPct: (json['totalReturnPct'] as num).toDouble(),
      sharpeRatio: (json['sharpeRatio'] as num).toDouble(),
      maxDrawdown: (json['maxDrawdown'] as num).toDouble(),
      winRate: (json['winRate'] as num).toDouble(),
      totalTrades: json['totalTrades'] as int,
      initialCapital: (json['initialCapital'] as num).toDouble(),
      finalValue: (json['finalValue'] as num).toDouble(),
    );
  }

  Map<String, dynamic> toJson() => {
        'totalReturnPct': totalReturnPct,
        'sharpeRatio': sharpeRatio,
        'maxDrawdown': maxDrawdown,
        'winRate': winRate,
        'totalTrades': totalTrades,
        'initialCapital': initialCapital,
        'finalValue': finalValue,
      };
}

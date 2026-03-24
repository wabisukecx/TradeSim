class PortfolioValue {
  final DateTime date;
  final double total;

  const PortfolioValue({
    required this.date,
    required this.total,
  });

  factory PortfolioValue.fromJson(Map<String, dynamic> json) {
    return PortfolioValue(
      date: DateTime.parse(json['date'] as String),
      total: (json['total'] as num).toDouble(),
    );
  }

  Map<String, dynamic> toJson() => {
        'date': date.toIso8601String(),
        'total': total,
      };
}

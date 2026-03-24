class PortfolioItem {
  final String symbol;
  final String? name;
  final DateTime addedAt;

  const PortfolioItem({
    required this.symbol,
    this.name,
    required this.addedAt,
  });

  factory PortfolioItem.fromJson(Map<String, dynamic> json) {
    return PortfolioItem(
      symbol: json['symbol'] as String,
      name: json['name'] as String?,
      addedAt: DateTime.parse(json['addedAt'] as String),
    );
  }

  Map<String, dynamic> toJson() => {
        'symbol': symbol,
        'name': name,
        'addedAt': addedAt.toIso8601String(),
      };
}

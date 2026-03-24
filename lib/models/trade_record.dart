class TradeRecord {
  final DateTime date;
  final String type; // 'Buy' or 'Sell'
  final double price;
  final int shares;
  final double pnl;
  final String exitReason;

  const TradeRecord({
    required this.date,
    required this.type,
    required this.price,
    required this.shares,
    required this.pnl,
    required this.exitReason,
  });

  factory TradeRecord.fromJson(Map<String, dynamic> json) {
    return TradeRecord(
      date: DateTime.parse(json['date'] as String),
      type: json['type'] as String,
      price: (json['price'] as num).toDouble(),
      shares: json['shares'] as int,
      pnl: (json['pnl'] as num).toDouble(),
      exitReason: json['exitReason'] as String,
    );
  }

  Map<String, dynamic> toJson() => {
        'date': date.toIso8601String(),
        'type': type,
        'price': price,
        'shares': shares,
        'pnl': pnl,
        'exitReason': exitReason,
      };
}

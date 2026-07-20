class DailyLog {
  final String id;
  final DateTime date;
  final double startKm;
  final double endKm;
  final double totalKm;
  final double cost;
  final String notes;

  DailyLog({
    required this.id,
    required this.date,
    required this.startKm,
    required this.endKm,
    required this.totalKm,
    required this.cost,
    this.notes = '',
  });

  factory DailyLog.fromMap(Map<String, dynamic> map) {
    return DailyLog(
      id: map['id'] as String? ?? '',
      date: DateTime.fromMillisecondsSinceEpoch(map['date'] as int),
      startKm: (map['startKm'] as num).toDouble(),
      endKm: (map['endKm'] as num).toDouble(),
      totalKm: (map['totalKm'] as num).toDouble(),
      cost: (map['cost'] as num).toDouble(),
      notes: map['notes'] as String? ?? '',
    );
  }

  Map<String, dynamic> toMap() {
    return {
      'id': id,
      'date': date.millisecondsSinceEpoch,
      'startKm': startKm,
      'endKm': endKm,
      'totalKm': totalKm,
      'cost': cost,
      'notes': notes,
    };
  }

  DailyLog copyWith({
    String? id,
    DateTime? date,
    double? startKm,
    double? endKm,
    double? totalKm,
    double? cost,
    String? notes,
  }) {
    return DailyLog(
      id: id ?? this.id,
      date: date ?? this.date,
      startKm: startKm ?? this.startKm,
      endKm: endKm ?? this.endKm,
      totalKm: totalKm ?? this.totalKm,
      cost: cost ?? this.cost,
      notes: notes ?? this.notes,
    );
  }
}

class PlacePin {
  final String id;
  final double lat;
  final double lng;
  final DateTime timestamp;
  final String label;

  PlacePin({
    required this.id,
    required this.lat,
    required this.lng,
    required this.timestamp,
    this.label = '',
  });

  factory PlacePin.fromMap(Map<String, dynamic> map) {
    return PlacePin(
      id: map['id'] as String? ?? '',
      lat: (map['lat'] as num).toDouble(),
      lng: (map['lng'] as num).toDouble(),
      timestamp: DateTime.fromMillisecondsSinceEpoch(map['timestamp'] as int),
      label: map['label'] as String? ?? '',
    );
  }

  Map<String, dynamic> toMap() {
    return {
      'id': id,
      'lat': lat,
      'lng': lng,
      'timestamp': timestamp.millisecondsSinceEpoch,
      'label': label,
    };
  }

  PlacePin copyWith({
    String? id,
    double? lat,
    double? lng,
    DateTime? timestamp,
    String? label,
  }) {
    return PlacePin(
      id: id ?? this.id,
      lat: lat ?? this.lat,
      lng: lng ?? this.lng,
      timestamp: timestamp ?? this.timestamp,
      label: label ?? this.label,
    );
  }
}

class DailyLog {
  final String id;
  final DateTime date;
  final double startKm;
  final double endKm;
  final double totalKm;
  final double cost;
  final String notes;
  final List<PlacePin> pins;

  DailyLog({
    required this.id,
    required this.date,
    required this.startKm,
    required this.endKm,
    required this.totalKm,
    required this.cost,
    this.notes = '',
    this.pins = const [],
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
      pins: ((map['pins'] as List?)?.cast<Map<String, dynamic>>()
              .map(PlacePin.fromMap)
              .toList()) ??
          const [],
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
      'pins': pins.map((p) => p.toMap()).toList(),
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
    List<PlacePin>? pins,
  }) {
    return DailyLog(
      id: id ?? this.id,
      date: date ?? this.date,
      startKm: startKm ?? this.startKm,
      endKm: endKm ?? this.endKm,
      totalKm: totalKm ?? this.totalKm,
      cost: cost ?? this.cost,
      notes: notes ?? this.notes,
      pins: pins ?? this.pins,
    );
  }
}

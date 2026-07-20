class PlacePin {
  final String id;
  final double lat;
  final double lng;
  final DateTime timestamp;
  final String label;

  const PlacePin({
    required this.id,
    required this.lat,
    required this.lng,
    required this.timestamp,
    this.label = '',
  });

  factory PlacePin.fromMap(Map<String, dynamic> m) => PlacePin(
        id: m['id'] as String? ?? '',
        lat: (m['lat'] as num).toDouble(),
        lng: (m['lng'] as num).toDouble(),
        timestamp: DateTime.fromMillisecondsSinceEpoch(m['timestamp'] as int),
        label: m['label'] as String? ?? '',
      );

  Map<String, dynamic> toMap() => {
        'id': id,
        'lat': lat,
        'lng': lng,
        'timestamp': timestamp.millisecondsSinceEpoch,
        'label': label,
      };

  PlacePin copyWith({String? id, double? lat, double? lng, DateTime? timestamp, String? label}) =>
      PlacePin(
        id: id ?? this.id,
        lat: lat ?? this.lat,
        lng: lng ?? this.lng,
        timestamp: timestamp ?? this.timestamp,
        label: label ?? this.label,
      );
}

class DailyLog {
  final String id;
  final DateTime date;
  final double startKm;
  final double endKm;
  final double totalKm;
  /// DEPRECATED: cost is no longer tracked on the daily log. The day's total
  /// spending is the sum of all Service entries on that calendar day, exposed
  /// via `LogProvider.dailyCostForDate`. This field stays for backward
  /// compatibility with existing Firestore documents; new writes omit it.
  final double cost;
  final String notes;
  final List<PlacePin> pins;

  DailyLog({
    required this.id,
    required this.date,
    required this.startKm,
    required this.endKm,
    required this.totalKm,
    this.cost = 0,
    this.notes = '',
    this.pins = const [],
  });

  factory DailyLog.fromMap(Map<String, dynamic> map) {
    final pinsRaw = map['pins'];
    final pins = pinsRaw is List
        ? pinsRaw.cast<Map<String, dynamic>>().map(PlacePin.fromMap).toList()
        : <PlacePin>[];
    final costRaw = map['cost'];
    return DailyLog(
      id: map['id'] as String? ?? '',
      date: DateTime.fromMillisecondsSinceEpoch(map['date'] as int),
      startKm: (map['startKm'] as num).toDouble(),
      endKm: (map['endKm'] as num).toDouble(),
      totalKm: (map['totalKm'] as num).toDouble(),
      cost: costRaw is num ? costRaw.toDouble() : 0,
      notes: map['notes'] as String? ?? '',
      pins: pins,
    );
  }

  Map<String, dynamic> toMap() => {
        'id': id,
        'date': date.millisecondsSinceEpoch,
        'startKm': startKm,
        'endKm': endKm,
        'totalKm': totalKm,
        // cost deliberately omitted: derived from services at display time.
        'notes': notes,
        'pins': pins.map((p) => p.toMap()).toList(),
      };

  DailyLog copyWith({
    String? id,
    DateTime? date,
    double? startKm,
    double? endKm,
    double? totalKm,
    double? cost,
    String? notes,
    List<PlacePin>? pins,
  }) =>
      DailyLog(
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

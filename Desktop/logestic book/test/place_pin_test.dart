import 'package:flutter_test/flutter_test.dart';
import 'package:logestic_app/models/daily_log.dart';

PlacePin _pin({String id = 'p1', double lat = 25.2, double lng = 55.3, String label = 'Start'}) =>
    PlacePin(
      id: id,
      lat: lat,
      lng: lng,
      timestamp: DateTime.fromMillisecondsSinceEpoch(1700000000000),
      label: label,
    );

DailyLog _log({List<PlacePin>? pins}) => DailyLog(
      id: 'log1',
      date: DateTime(2026, 7, 19),
      startKm: 12000,
      endKm: 12500,
      totalKm: 500,
      cost: 100,
      pins: pins ?? const [],
    );

void main() {
  test('PlacePin round-trip', () {
    final p = _pin();
    final m = p.toMap();
    final p2 = PlacePin.fromMap(m);
    expect(p2.id, p.id);
    expect(p2.lat, p.lat);
    expect(p2.lng, p.lng);
    expect(p2.timestamp, p.timestamp);
    expect(p2.label, p.label);
  });

  test('DailyLog round-trip with pins', () {
    final log = _log(pins: [_pin(), _pin(id: 'p2', lat: 25.3, lng: 55.4)]);
    final m = log.toMap();
    final log2 = DailyLog.fromMap(m);
    expect(log2.pins.length, 2);
    expect(log2.pins[0].id, 'p1');
    expect(log2.pins[1].lat, 25.3);
  });

  test('DailyLog.fromMap with no pins key returns empty list', () {
    final m = _log().toMap();
    m.remove('pins');
    final log2 = DailyLog.fromMap(m);
    expect(log2.pins, isEmpty);
  });

  test('DailyLog.copyWith(pins: ...) replaces', () {
    final log = _log();
    final log2 = log.copyWith(pins: [_pin()]);
    expect(log2.pins.length, 1);
    expect(log.pins, isEmpty);
  });

  test('DailyLog.copyWith() preserves pins', () {
    final log = _log(pins: [_pin()]);
    final log2 = log.copyWith(cost: 200);
    expect(log2.pins.length, 1);
    expect(log2.cost, 200);
  });
}

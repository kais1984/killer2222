import 'package:flutter_test/flutter_test.dart';
import 'package:logestic_app/models/daily_log.dart';

void main() {
  group('PlacePin', () {
    test('round-trips through toMap and fromMap', () {
      final pin = PlacePin(
        id: 'p1',
        lat: 25.2,
        lng: 55.3,
        timestamp: DateTime.fromMillisecondsSinceEpoch(1700000000000),
        label: 'Start',
      );
      final log = DailyLog(
        id: 'log1',
        date: DateTime(2026, 7, 20),
        startKm: 100,
        endKm: 200,
        totalKm: 100,
        cost: 50,
        notes: '',
        pins: [pin],
      );
      final restored = DailyLog.fromMap(log.toMap());
      expect(restored.pins.length, 1);
      expect(restored.pins.first.id, 'p1');
      expect(restored.pins.first.lat, 25.2);
      expect(restored.pins.first.lng, 55.3);
      expect(restored.pins.first.timestamp.millisecondsSinceEpoch,
          1700000000000);
      expect(restored.pins.first.label, 'Start');
    });

    test('fromMap of an old document without pins key returns empty list', () {
      final log = DailyLog.fromMap({
        'id': 'old',
        'date': DateTime(2026, 7, 20).millisecondsSinceEpoch,
        'startKm': 100,
        'endKm': 200,
        'totalKm': 100,
        'cost': 50,
        'notes': '',
      });
      expect(log.pins, isEmpty);
    });

    test('copyWith(pins: [...]) replaces pins', () {
      final log = DailyLog(
        id: 'log1',
        date: DateTime(2026, 7, 20),
        startKm: 100,
        endKm: 200,
        totalKm: 100,
        cost: 50,
        notes: '',
        pins: [
          PlacePin(
            id: 'p1',
            lat: 1.0,
            lng: 2.0,
            timestamp: DateTime(2026, 7, 20, 8),
            label: 'A',
          ),
        ],
      );
      final newPin = PlacePin(
        id: 'p2',
        lat: 3.0,
        lng: 4.0,
        timestamp: DateTime(2026, 7, 20, 17),
        label: 'B',
      );
      final updated = log.copyWith(pins: [newPin]);
      expect(updated.pins.length, 1);
      expect(updated.pins.first.id, 'p2');
    });

    test('copyWith() without pins preserves existing pins', () {
      final log = DailyLog(
        id: 'log1',
        date: DateTime(2026, 7, 20),
        startKm: 100,
        endKm: 200,
        totalKm: 100,
        cost: 50,
        notes: '',
        pins: [
          PlacePin(
            id: 'p1',
            lat: 1.0,
            lng: 2.0,
            timestamp: DateTime(2026, 7, 20, 8),
            label: 'A',
          ),
        ],
      );
      final updated = log.copyWith(notes: 'changed');
      expect(updated.pins.length, 1);
      expect(updated.pins.first.id, 'p1');
      expect(updated.notes, 'changed');
    });

    test('default pins is an empty list', () {
      final log = DailyLog(
        id: 'log1',
        date: DateTime(2026, 7, 20),
        startKm: 100,
        endKm: 200,
        totalKm: 100,
        cost: 50,
      );
      expect(log.pins, isEmpty);
    });
  });
}

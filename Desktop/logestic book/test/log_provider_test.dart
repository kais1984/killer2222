import 'package:flutter/foundation.dart' show visibleForTesting;
import 'package:flutter_test/flutter_test.dart';
import 'package:logestic_app/models/daily_log.dart';
import 'package:logestic_app/providers/log_provider.dart';

DailyLog _log(DateTime date, double endKm) => DailyLog(
      id: '${date.millisecondsSinceEpoch}',
      date: date,
      startKm: 0,
      endKm: endKm,
      totalKm: endKm,
      cost: 0,
      notes: '',
    );

void main() {
  late LogProvider provider;
  setUp(() {
    provider = LogProvider();
    // Suppress Firestore attempt; we won't call startListening().
  });

  test('returns null when dailyLogs is empty', () {
    provider.setDailyLogsForTest([]);
    expect(provider.previousEndKmForDate(DateTime(2026, 7, 19)), isNull);
  });

  test('returns endKm of the single earlier log', () {
    provider.setDailyLogsForTest([
      _log(DateTime(2026, 7, 18), 12345),
    ]);
    expect(provider.previousEndKmForDate(DateTime(2026, 7, 19)), 12345);
  });

  test('picks the latest earlier date when multiple exist', () {
    provider.setDailyLogsForTest([
      _log(DateTime(2026, 7, 10), 10000),
      _log(DateTime(2026, 7, 17), 11000),
      _log(DateTime(2026, 7, 18), 12000),
    ]);
    expect(provider.previousEndKmForDate(DateTime(2026, 7, 19)), 12000);
  });

  test('tie-breaks same-date logs by larger endKm', () {
    provider.setDailyLogsForTest([
      _log(DateTime(2026, 7, 18), 11000),
      _log(DateTime(2026, 7, 18), 12000),
    ]);
    expect(provider.previousEndKmForDate(DateTime(2026, 7, 19)), 12000);
  });

  test('ignores same-day and later logs', () {
    provider.setDailyLogsForTest([
      _log(DateTime(2026, 7, 19, 8, 0), 9999),  // same day as query
      _log(DateTime(2026, 7, 20), 13000),       // later
    ]);
    expect(provider.previousEndKmForDate(DateTime(2026, 7, 19)), isNull);
  });

  test('ignores logs strictly after the chosen date', () {
    provider.setDailyLogsForTest([
      _log(DateTime(2026, 8, 1), 99999),
    ]);
    expect(provider.previousEndKmForDate(DateTime(2026, 7, 19)), isNull);
  });

  test('back-dating: respects chosen date, not today', () {
    provider.setDailyLogsForTest([
      _log(DateTime(2026, 7, 5), 9000),
      _log(DateTime(2026, 7, 18), 12000),
    ]);
    expect(provider.previousEndKmForDate(DateTime(2026, 7, 6)), 9000);
  });
}
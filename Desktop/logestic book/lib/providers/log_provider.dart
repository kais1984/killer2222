import 'package:flutter/foundation.dart';
import 'package:logestic_app/models/daily_log.dart';
import 'package:logestic_app/models/service_log.dart';
import 'package:logestic_app/services/firestore_service.dart';

class LogProvider extends ChangeNotifier {
  final FirestoreService _firestore = FirestoreService();

  List<DailyLog> _dailyLogs = [];
  List<ServiceLog> _services = [];

  List<DailyLog> get dailyLogs => _dailyLogs;
  List<ServiceLog> get services => _services;

  DailyLog? getTodayLog() {
    final now = DateTime.now();
    final today = DateTime(now.year, now.month, now.day);
    try {
      return _dailyLogs.firstWhere(
        (log) =>
            log.date.year == today.year &&
            log.date.month == today.month &&
            log.date.day == today.day,
      );
    } catch (_) {
      return null;
    }
  }

  void startListening() {
    _firestore.getDailyLogs().listen((logs) {
      _dailyLogs = logs;
      notifyListeners();
    });
    _firestore.getServices().listen((svcs) {
      _services = svcs;
      notifyListeners();
    });
  }

  Future<void> addDailyLog(DailyLog log) async {
    await _firestore.addDailyLog(log);
  }

  Future<void> updateDailyLog(DailyLog log) async {
    await _firestore.updateDailyLog(log);
  }

  Future<void> deleteDailyLog(String id) async {
    await _firestore.deleteDailyLog(id);
  }

  Future<void> addService(ServiceLog log) async {
    await _firestore.addService(log);
  }

  Future<void> updateService(ServiceLog log) async {
    await _firestore.updateService(log);
  }

  Future<void> deleteService(String id) async {
    await _firestore.deleteService(id);
  }

  Future<List<DailyLog>> getDailyLogsForMonth(int year, int month) async {
    return _firestore.getDailyLogsForMonth(year, month);
  }

  Future<List<ServiceLog>> getServicesForMonth(int year, int month) async {
    return _firestore.getServicesForMonth(year, month);
  }

  /// Returns the endKm of the most recent daily log strictly earlier than
  /// [date] (compared at day granularity). When multiple logs share that
  /// latest earlier date, the one with the largest endKm wins.
  /// Returns null when no qualifying log exists.
  double? previousEndKmForDate(DateTime date) {
    final dayStart = DateTime(date.year, date.month, date.day);
    DailyLog? latest;
    for (final l in _dailyLogs) {
      if (!l.date.isBefore(dayStart)) continue;
      if (latest == null ||
          l.date.isAfter(latest.date) ||
          (l.date.isAtSameMomentAs(latest.date) && l.endKm > latest.endKm)) {
        latest = l;
      }
    }
    return latest?.endKm;
  }

  @visibleForTesting
  void setDailyLogsForTest(List<DailyLog> logs) {
    _dailyLogs = logs;
  }
}

import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:logestic_app/models/daily_log.dart';
import 'package:logestic_app/models/service_log.dart';

class FirestoreService {
  FirebaseFirestore? _dbInstance;
  FirebaseFirestore get _db => _dbInstance ??= FirebaseFirestore.instance;

  Stream<List<DailyLog>> getDailyLogs() {
    return _db
        .collection('dailyLogs')
        .orderBy('date', descending: true)
        .snapshots()
        .map((snapshot) =>
            snapshot.docs.map((doc) => DailyLog.fromMap(doc.data())).toList());
  }

  Future<List<DailyLog>> getDailyLogsForMonth(int year, int month) async {
    final start = DateTime(year, month, 1);
    final end = DateTime(year, month + 1, 1);
    final snapshot = await _db
        .collection('dailyLogs')
        .where('date',
            isGreaterThanOrEqualTo: start.millisecondsSinceEpoch)
        .where('date', isLessThan: end.millisecondsSinceEpoch)
        .get();
    return snapshot.docs
        .map((doc) => DailyLog.fromMap(doc.data()))
        .toList();
  }

  Future<void> addDailyLog(DailyLog log) async {
    final docRef = _db.collection('dailyLogs').doc();
    await docRef.set(log.copyWith(id: docRef.id).toMap());
  }

  Future<void> updateDailyLog(DailyLog log) async {
    await _db.collection('dailyLogs').doc(log.id).update(log.toMap());
  }

  Future<void> deleteDailyLog(String id) async {
    await _db.collection('dailyLogs').doc(id).delete();
  }

  Stream<List<ServiceLog>> getServices() {
    return _db
        .collection('services')
        .orderBy('date', descending: true)
        .snapshots()
        .map((snapshot) =>
            snapshot.docs.map((doc) => ServiceLog.fromMap(doc.data())).toList());
  }

  Future<List<ServiceLog>> getServicesForMonth(int year, int month) async {
    final start = DateTime(year, month, 1);
    final end = DateTime(year, month + 1, 1);
    final snapshot = await _db
        .collection('services')
        .where('date',
            isGreaterThanOrEqualTo: start.millisecondsSinceEpoch)
        .where('date', isLessThan: end.millisecondsSinceEpoch)
        .get();
    return snapshot.docs
        .map((doc) => ServiceLog.fromMap(doc.data()))
        .toList();
  }

  Future<void> addService(ServiceLog log) async {
    final docRef = _db.collection('services').doc();
    await docRef.set(log.copyWith(id: docRef.id).toMap());
  }

  Future<void> updateService(ServiceLog log) async {
    await _db.collection('services').doc(log.id).update(log.toMap());
  }

  Future<void> deleteService(String id) async {
    await _db.collection('services').doc(id).delete();
  }
}

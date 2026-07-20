import 'dart:io';
import 'package:excel/excel.dart';
import 'package:path_provider/path_provider.dart';
import 'package:share_plus/share_plus.dart';
import 'package:intl/intl.dart';
import 'package:logestic_app/models/daily_log.dart';
import 'package:logestic_app/models/service_log.dart';

class ExportService {
  Future<void> exportToExcel({
    required List<DailyLog> dailyLogs,
    required List<ServiceLog> services,
    required int year,
    required int month,
  }) async {
    final excel = Excel.createExcel();
    final monthName = DateFormat('MMMM yyyy').format(DateTime(year, month));

    final dailySheet = excel['Daily Log'];
    dailySheet.appendRow([
      TextCellValue('Date'),
      TextCellValue('Start KM'),
      TextCellValue('End KM'),
      TextCellValue('Total KM'),
      TextCellValue('Spent (AED)'),
      TextCellValue('Notes'),
    ]);

    double totalSpent = 0;
    double totalKm = 0;
    for (final log in dailyLogs) {
      final dayCost = services
          .where((s) =>
              s.date.year == log.date.year &&
              s.date.month == log.date.month &&
              s.date.day == log.date.day)
          .fold<double>(0, (sum, s) => sum + s.cost);
      dailySheet.appendRow([
        TextCellValue(DateFormat('yyyy-MM-dd').format(log.date)),
        TextCellValue(log.startKm.toStringAsFixed(0)),
        TextCellValue(log.endKm.toStringAsFixed(0)),
        TextCellValue(log.totalKm.toStringAsFixed(0)),
        TextCellValue(dayCost.toStringAsFixed(2)),
        TextCellValue(log.notes),
      ]);
      totalSpent += dayCost;
      totalKm += log.totalKm;
    }

    final svcSheet = excel['Services'];
    svcSheet.appendRow([
      TextCellValue('Date'),
      TextCellValue('KM Reading'),
      TextCellValue('Service Type'),
      TextCellValue('Cost (AED)'),
      TextCellValue('Notes'),
    ]);

    for (final svc in services) {
      svcSheet.appendRow([
        TextCellValue(DateFormat('yyyy-MM-dd').format(svc.date)),
        TextCellValue(svc.kmReading.toStringAsFixed(0)),
        TextCellValue(ServiceLog.displayName(svc.serviceType)),
        TextCellValue(svc.cost.toStringAsFixed(2)),
        TextCellValue(svc.notes),
      ]);
    }

    final summarySheet = excel['Summary'];
    summarySheet.appendRow([TextCellValue('Driver Log Book - $monthName')]);
    summarySheet.appendRow([]);
    summarySheet.appendRow([
      TextCellValue('Total KM Driven'),
      TextCellValue(totalKm.toStringAsFixed(0)),
    ]);
    summarySheet.appendRow([
      TextCellValue('Total Spent'),
      TextCellValue('${totalSpent.toStringAsFixed(2)} AED'),
    ]);
    summarySheet.appendRow([
      TextCellValue('Total Services'),
      TextCellValue(services.length.toString()),
    ]);

    final dir = await getTemporaryDirectory();
    final fileName =
        'driver_log_${year}_${month.toString().padLeft(2, '0')}.xlsx';
    final file = File('${dir.path}/$fileName');
    await file.writeAsBytes(excel.encode()!);

    await Share.shareXFiles(
      [XFile(file.path)],
      text: 'Driver Log - $monthName',
    );
  }
}

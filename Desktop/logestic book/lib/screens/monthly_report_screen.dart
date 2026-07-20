import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:intl/intl.dart';
import 'package:logestic_app/models/daily_log.dart';
import 'package:logestic_app/models/service_log.dart';
import 'package:logestic_app/providers/log_provider.dart';
import 'package:logestic_app/services/export_service.dart';
import 'package:logestic_app/theme/app_theme.dart';

class MonthlyReportScreen extends StatefulWidget {
  const MonthlyReportScreen({super.key});

  @override
  State<MonthlyReportScreen> createState() => _MonthlyReportScreenState();
}

class _MonthlyReportScreenState extends State<MonthlyReportScreen> {
  late int _selectedYear;
  late int _selectedMonth;
  List<DailyLog> _dailyLogs = [];
  List<ServiceLog> _services = [];
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    final now = DateTime.now();
    _selectedYear = now.year;
    _selectedMonth = now.month;
    _loadData();
  }

  Future<void> _loadData() async {
    setState(() => _loading = true);
    final provider = context.read<LogProvider>();
    final dailyLogs =
        await provider.getDailyLogsForMonth(_selectedYear, _selectedMonth);
    final services =
        await provider.getServicesForMonth(_selectedYear, _selectedMonth);
    if (mounted) {
      setState(() {
        _dailyLogs = dailyLogs;
        _services = services;
        _loading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final totalKm =
        _dailyLogs.fold<double>(0, (sum, l) => sum + l.totalKm);
    final dailyCost =
        _dailyLogs.fold<double>(0, (sum, l) => sum + l.cost);
    final svcCost = _services.fold<double>(0, (sum, s) => sum + s.cost);
    final grandTotal = dailyCost + svcCost;

    return Scaffold(
      appBar: AppBar(
        title: Text(DateFormat('MMMM yyyy')
            .format(DateTime(_selectedYear, _selectedMonth))),
        actions: [
          IconButton(
            icon: const Icon(Icons.navigate_before),
            onPressed: () {
              setState(() {
                if (_selectedMonth == 1) {
                  _selectedMonth = 12;
                  _selectedYear--;
                } else {
                  _selectedMonth--;
                }
              });
              _loadData();
            },
          ),
          IconButton(
            icon: const Icon(Icons.navigate_next),
            onPressed: () {
              setState(() {
                if (_selectedMonth == 12) {
                  _selectedMonth = 1;
                  _selectedYear++;
                } else {
                  _selectedMonth++;
                }
              });
              _loadData();
            },
          ),
          IconButton(
            icon: const Icon(Icons.file_download),
            onPressed: _loading
                ? null
                : () async {
                    await ExportService().exportToExcel(
                      dailyLogs: _dailyLogs,
                      services: _services,
                      year: _selectedYear,
                      month: _selectedMonth,
                    );
                  },
            tooltip: 'Export to Excel',
          ),
        ],
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : SingleChildScrollView(
              padding: const EdgeInsets.fromLTRB(20, 20, 20, 32),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  _buildSummaryGrid(
                      totalKm, dailyCost, svcCost, grandTotal),
                  const SizedBox(height: 24),
                  _buildSectionHeader('Daily Trips',
                      '${_dailyLogs.length} entries'),
                  const SizedBox(height: 10),
                  if (_dailyLogs.isEmpty)
                    _buildEmptyState('No daily trips this month')
                  else
                    ..._dailyLogs.map((l) => _buildDailyRow(l)),
                  const SizedBox(height: 24),
                  _buildSectionHeader('Services',
                      '${_services.length} records'),
                  const SizedBox(height: 10),
                  if (_services.isEmpty)
                    _buildEmptyState('No services this month')
                  else
                    ..._services.map((s) => _buildServiceRow(s)),
                ],
              ),
            ),
    );
  }

  Widget _buildSummaryGrid(
      double totalKm, double dailyCost, double svcCost, double grandTotal) {
    return Column(
      children: [
        Row(
          children: [
            Expanded(
                child: _buildStatCard(
                    'Total KM', totalKm.toStringAsFixed(0),
                    Icons.speed, AppTheme.primaryGradient)),
            const SizedBox(width: 12),
            Expanded(
                child: _buildStatCard(
                    'Working Days', '${_dailyLogs.length}',
                    Icons.calendar_month, AppTheme.secondaryGradient)),
          ],
        ),
        const SizedBox(height: 12),
        Row(
          children: [
            Expanded(
                child: _buildStatCard(
                    'Trip Costs', '${dailyCost.toStringAsFixed(0)} AED',
                    Icons.directions_car, AppTheme.accentGradient)),
            const SizedBox(width: 12),
            Expanded(
                child: _buildStatCard(
                    'Service Costs', '${svcCost.toStringAsFixed(0)} AED',
                    Icons.build, AppTheme.secondaryGradient)),
          ],
        ),
        const SizedBox(height: 12),
        Container(
          width: double.infinity,
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            gradient: const LinearGradient(
                colors: AppTheme.primaryGradient,
                begin: Alignment.centerLeft,
                end: Alignment.centerRight),
            borderRadius: BorderRadius.circular(16),
            boxShadow: [
              BoxShadow(
                color: AppTheme.primary.withValues(alpha: 0.3),
                blurRadius: 12,
                offset: const Offset(0, 4),
              ),
            ],
          ),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('Grand Total',
                      style: TextStyle(
                          color: Colors.white70, fontSize: 12)),
                  SizedBox(height: 4),
                  Text('All Costs Combined',
                      style: TextStyle(
                          color: Colors.white60, fontSize: 10)),
                ],
              ),
              Text(
                '${grandTotal.toStringAsFixed(0)} AED',
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 24,
                  fontWeight: FontWeight.w800,
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildStatCard(
      String label, String value, IconData icon, List<Color> gradient) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(16),
        gradient: LinearGradient(colors: gradient),
        boxShadow: [
          BoxShadow(
            color: gradient.first.withValues(alpha: 0.3),
            blurRadius: 10,
            offset: const Offset(0, 3),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(label,
                  style: const TextStyle(
                      color: Colors.white70,
                      fontSize: 11,
                      fontWeight: FontWeight.w500)),
              Icon(icon, color: Colors.white60, size: 16),
            ],
          ),
          const SizedBox(height: 6),
          Text(value,
              style: const TextStyle(
                  color: Colors.white,
                  fontSize: 18,
                  fontWeight: FontWeight.w800)),
        ],
      ),
    );
  }

  Widget _buildSectionHeader(String title, String subtitle) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(title,
            style: const TextStyle(
              color: AppTheme.darkText,
              fontSize: 16,
              fontWeight: FontWeight.w700,
            )),
        Text(subtitle,
            style: const TextStyle(
              color: AppTheme.mediumText,
              fontSize: 13,
            )),
      ],
    );
  }

  Widget _buildEmptyState(String message) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(vertical: 24),
      child: Text(
        message,
        textAlign: TextAlign.center,
        style: TextStyle(
            color: AppTheme.mediumText.withValues(alpha: 0.6),
            fontSize: 14),
      ),
    );
  }

  Widget _buildDailyRow(DailyLog log) {
    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        children: [
          Text(
            DateFormat('MMM d').format(log.date),
            style: const TextStyle(
              color: AppTheme.darkText,
              fontSize: 14,
              fontWeight: FontWeight.w600,
              letterSpacing: 0.3,
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Text(
              '${log.startKm.toStringAsFixed(0)} \u2192 ${log.endKm.toStringAsFixed(0)}',
              style: const TextStyle(
                color: AppTheme.mediumText,
                fontSize: 13,
              ),
            ),
          ),
          Text(
            '${log.totalKm.toStringAsFixed(0)} KM',
            style: const TextStyle(
              color: AppTheme.accent,
              fontSize: 13,
              fontWeight: FontWeight.w700,
            ),
          ),
          const SizedBox(width: 12),
          SizedBox(
            width: 70,
            child: Text(
              '${log.cost.toStringAsFixed(0)} AED',
              textAlign: TextAlign.right,
              style: const TextStyle(
                color: AppTheme.darkText,
                fontSize: 13,
                fontWeight: FontWeight.w600,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildServiceRow(ServiceLog svc) {
    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        children: [
          Text(
            DateFormat('MMM d').format(svc.date),
            style: const TextStyle(
              color: AppTheme.darkText,
              fontSize: 14,
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Text(
              ServiceLog.displayName(svc.serviceType),
              style: const TextStyle(
                color: AppTheme.mediumText,
                fontSize: 13,
              ),
            ),
          ),
          Text(
            '${svc.cost.toStringAsFixed(0)} AED',
            style: const TextStyle(
              color: AppTheme.darkText,
              fontSize: 13,
              fontWeight: FontWeight.w600,
            ),
          ),
        ],
      ),
    );
  }
}

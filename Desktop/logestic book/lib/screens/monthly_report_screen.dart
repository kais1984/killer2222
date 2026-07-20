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
    final provider = context.read<LogProvider>();
    final totalKm =
        _dailyLogs.fold<double>(0, (sum, l) => sum + l.totalKm);
    // The cost of the month is the sum of all Service entries in it.
    // The DailyLog no longer carries a cost (it would double-count the
    // services that produced it). One source of truth: services.
    final svcCost = _services.fold<double>(0, (sum, s) => sum + s.cost);
    final grandTotal = svcCost;

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
                    _buildSummaryGrid(totalKm, grandTotal),
                  const SizedBox(height: 24),
                  _buildSectionHeader('Daily Trips',
                      '${_dailyLogs.length} entries'),
                  const SizedBox(height: 10),
                  if (_dailyLogs.isEmpty)
                    _buildEmptyState('No daily trips this month')
                  else
                    ..._dailyLogs.map((l) => _buildDailyRow(l, provider.dailyCostForDate(l.date))),
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
      double totalKm, double grandTotal) {
    return Column(
      children: [
        Row(
          children: [
            Expanded(child: _StatBlock(label: 'TOTAL KM', value: totalKm.toStringAsFixed(0), accent: AppTheme.primaryLight)),
            const SizedBox(width: 8),
            Expanded(child: _StatBlock(label: 'WORKING DAYS', value: _dailyLogs.length.toString(), accent: AppTheme.secondary)),
          ],
        ),
        const SizedBox(height: 8),
        _GrandTotalBlock(amount: '${grandTotal.toStringAsFixed(0)} AED'),
      ],
    );
  }

  Widget _buildSectionHeader(String title, String subtitle) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(title, style: AppTheme.sectionLabel),
        Text(subtitle, style: AppTheme.caption),
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
        style: AppTheme.caption,
      ),
    );
  }

  Widget _buildDailyRow(DailyLog log, double dayCost) {
    return Container(
      margin: const EdgeInsets.only(bottom: 4),
      padding: const EdgeInsets.fromLTRB(12, 10, 12, 10),
      decoration: BoxDecoration(
        color: AppTheme.bezel,
        border: Border(
          top: BorderSide(color: AppTheme.bezelEdge),
          bottom: BorderSide(color: AppTheme.bezelEdge),
        ),
      ),
      child: Row(
        children: [
          Text(
            DateFormat('MMM d').format(log.date).toUpperCase(),
            style: AppTheme.smallNumber.copyWith(color: AppTheme.displayDim, fontSize: 11),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Text(
              '${log.startKm.toStringAsFixed(0)} \u2192 ${log.endKm.toStringAsFixed(0)}',
              style: AppTheme.smallNumber,
            ),
          ),
          Text(
            '${log.totalKm.toStringAsFixed(0)} KM',
            style: AppTheme.smallNumber.copyWith(color: AppTheme.accentBright),
          ),
          const SizedBox(width: 12),
          Text(
            dayCost.toStringAsFixed(0),
            style: AppTheme.smallNumber,
          ),
        ],
      ),
    );
  }

  Widget _buildServiceRow(ServiceLog svc) {
    return Container(
      margin: const EdgeInsets.only(bottom: 4),
      padding: const EdgeInsets.fromLTRB(12, 10, 12, 10),
      decoration: BoxDecoration(
        color: AppTheme.bezel,
        border: Border(
          top: BorderSide(color: AppTheme.bezelEdge),
          bottom: BorderSide(color: AppTheme.bezelEdge),
        ),
      ),
      child: Row(
        children: [
          Text(
            DateFormat('MMM d').format(svc.date).toUpperCase(),
            style: AppTheme.smallNumber.copyWith(color: AppTheme.displayDim, fontSize: 11),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Text(
              ServiceLog.displayName(svc.serviceType),
              style: AppTheme.smallNumber,
            ),
          ),
          Text(
            '${svc.cost.toStringAsFixed(0)} AED',
            style: AppTheme.smallNumber,
          ),
        ],
      ),
    );
  }
}

class _StatBlock extends StatelessWidget {
  final String label;
  final String value;
  final Color accent;
  const _StatBlock({required this.label, required this.value, required this.accent});
  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.fromLTRB(12, 12, 12, 14),
      decoration: BoxDecoration(
        color: AppTheme.bezel,
        border: Border.all(color: AppTheme.bezelEdge),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(width: 4, height: 4, color: accent),
              const SizedBox(width: 8),
              Text(label, style: AppTheme.sectionLabel.copyWith(color: accent)),
            ],
          ),
          const SizedBox(height: 6),
          Text(value, style: AppTheme.bigNumber.copyWith(color: AppTheme.displayBright)),
        ],
      ),
    );
  }
}

class _GrandTotalBlock extends StatelessWidget {
  final String amount;
  const _GrandTotalBlock({required this.amount});
  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.fromLTRB(16, 16, 16, 16),
      decoration: BoxDecoration(
        color: const Color(0xFF0B1220),
        border: Border.all(color: AppTheme.accent),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(width: 4, height: 4, color: AppTheme.accent),
              const SizedBox(width: 8),
              Text('GRAND TOTAL', style: AppTheme.sectionLabel.copyWith(color: AppTheme.accent)),
            ],
          ),
          const SizedBox(height: 6),
          Text(amount, style: AppTheme.hugeNumber.copyWith(color: AppTheme.accentBright)),
          const SizedBox(height: 2),
          Text('ALL COSTS COMBINED', style: AppTheme.sectionLabel),
        ],
      ),
    );
  }
}

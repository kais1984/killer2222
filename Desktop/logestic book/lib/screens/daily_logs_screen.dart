import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:intl/intl.dart';
import 'package:logestic_app/providers/log_provider.dart';
import 'package:logestic_app/screens/daily_log_form_screen.dart';
import 'package:logestic_app/theme/app_theme.dart';

class DailyLogsScreen extends StatelessWidget {
  const DailyLogsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Daily Logs')),
      body: Consumer<LogProvider>(
        builder: (context, provider, _) {
          final logs = provider.dailyLogs;
          if (logs.isEmpty) {
            return Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(Icons.directions_car_outlined,
                      size: 64, color: AppTheme.mediumText.withValues(alpha: 0.4)),
                  const SizedBox(height: 16),
                  const Text('No daily entries yet',
                      style: TextStyle(color: AppTheme.mediumText, fontSize: 16)),
                  const SizedBox(height: 8),
                  const Text('Tap + to add your first trip',
                      style: TextStyle(color: AppTheme.mediumText, fontSize: 13)),
                ],
              ),
            );
          }
          return ListView.builder(
            padding: const EdgeInsets.fromLTRB(16, 8, 16, 80),
            itemCount: logs.length,
            itemBuilder: (context, index) {
              final log = logs[index];
              final dateStr = DateFormat('MMM d, yyyy').format(log.date);
              final dayName = DateFormat('EEEE').format(log.date);

              return Padding(
                padding: const EdgeInsets.only(bottom: 10),
                child: Material(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(16),
                  child: InkWell(
                    borderRadius: BorderRadius.circular(16),
                    onTap: () => Navigator.push(
                      context,
                      MaterialPageRoute(
                        builder: (_) => DailyLogFormScreen(existingLog: log),
                      ),
                    ),
                    child: Container(
                      decoration: BoxDecoration(
                        borderRadius: BorderRadius.circular(16),
                        border: Border(
                          left: BorderSide(
                            color: AppTheme.primaryLight.withValues(alpha: 0.3),
                            width: 4,
                          ),
                        ),
                      ),
                      padding: const EdgeInsets.all(16),
                      child: Row(
                        children: [
                          Container(
                            width: 48,
                            height: 48,
                            decoration: BoxDecoration(
                              color: AppTheme.primaryLight.withValues(alpha: 0.1),
                              borderRadius: BorderRadius.circular(12),
                            ),
                            child: Center(
                              child: Text(
                                log.date.day.toString(),
                                style: const TextStyle(
                                  color: AppTheme.primary,
                                  fontSize: 20,
                                  fontWeight: FontWeight.w800,
                                ),
                              ),
                            ),
                          ),
                          const SizedBox(width: 14),
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  dateStr,
                                  style: const TextStyle(
                                    color: AppTheme.darkText,
                                    fontSize: 15,
                                    fontWeight: FontWeight.w600,
                                  ),
                                ),
                                const SizedBox(height: 4),
                                Text(
                                  '$dayName  |  ${log.startKm.toStringAsFixed(0)} \u2192 ${log.endKm.toStringAsFixed(0)} KM',
                                  style: const TextStyle(
                                    color: AppTheme.mediumText,
                                    fontSize: 12,
                                  ),
                                ),
                              ],
                            ),
                          ),
                          Column(
                            crossAxisAlignment: CrossAxisAlignment.end,
                            children: [
                              Container(
                                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                                decoration: BoxDecoration(
                                  color: AppTheme.accent.withValues(alpha: 0.1),
                                  borderRadius: BorderRadius.circular(8),
                                ),
                                child: Text(
                                  '${log.totalKm.toStringAsFixed(0)} KM',
                                  style: const TextStyle(
                                    color: AppTheme.accent,
                                    fontSize: 12,
                                    fontWeight: FontWeight.w700,
                                  ),
                                ),
                              ),
                              const SizedBox(height: 4),
                              Text(
                                '${log.cost.toStringAsFixed(0)} AED',
                                style: const TextStyle(
                                  color: AppTheme.darkText,
                                  fontSize: 13,
                                  fontWeight: FontWeight.w600,
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(width: 4),
                          Icon(Icons.chevron_right,
                              color: AppTheme.mediumText.withValues(alpha: 0.5),
                              size: 18),
                        ],
                      ),
                    ),
                  ),
                ),
              );
            },
          );
        },
      ),
      floatingActionButton: FloatingActionButton(
        child: const Icon(Icons.add),
        onPressed: () => Navigator.push(
          context,
          MaterialPageRoute(builder: (_) => const DailyLogFormScreen()),
        ),
      ),
    );
  }
}

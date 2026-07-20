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
      appBar: AppBar(title: const Text('DAILY LOGS')),
      body: Consumer<LogProvider>(
        builder: (context, provider, _) {
          final logs = provider.dailyLogs;
          if (logs.isEmpty) {
            return Center(
              child: Padding(
                padding: const EdgeInsets.symmetric(horizontal: 32),
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Icon(Icons.directions_car_outlined,
                        size: 56, color: AppTheme.tickDim),
                    const SizedBox(height: 16),
                    Text('NO ENTRIES', style: AppTheme.bigLabel),
                    const SizedBox(height: 6),
                    Text('Tap the + button to log your first trip.',
                        textAlign: TextAlign.center, style: AppTheme.caption),
                  ],
                ),
              ),
            );
          }
          return ListView.builder(
            padding: const EdgeInsets.fromLTRB(16, 8, 16, 80),
            itemCount: logs.length,
            itemBuilder: (context, index) {
              final log = logs[index];
              final dateStr = DateFormat('EEE · MMM d').format(log.date).toUpperCase();
              final dayName = DateFormat('EEEE').format(log.date);
              final isToday = log.date.year == DateTime.now().year &&
                  log.date.month == DateTime.now().month &&
                  log.date.day == DateTime.now().day;

              return Padding(
                padding: const EdgeInsets.only(bottom: 6),
                child: InkWell(
                  onTap: () => Navigator.push(
                    context,
                    MaterialPageRoute(builder: (_) => DailyLogFormScreen(existingLog: log)),
                  ),
                  child: Container(
                    padding: const EdgeInsets.fromLTRB(14, 14, 14, 14),
                    decoration: BoxDecoration(
                      color: AppTheme.bezel,
                      border: Border(
                        left: BorderSide(
                          color: isToday ? AppTheme.accent : AppTheme.bezelEdge,
                          width: 3,
                        ),
                        top: BorderSide(color: AppTheme.bezelEdge),
                        bottom: BorderSide(color: AppTheme.bezelEdge),
                        right: BorderSide(color: AppTheme.bezelEdge),
                      ),
                    ),
                    child: Row(
                      children: [
                        Column(
                          crossAxisAlignment: CrossAxisAlignment.center,
                          children: [
                            Text(log.date.day.toString().padLeft(2, '0'),
                                style: AppTheme.bigNumber.copyWith(color: isToday ? AppTheme.accentBright : AppTheme.displayBright)),
                            Text(DateFormat('MMM').format(log.date).toUpperCase(),
                                style: AppTheme.sectionLabel),
                          ],
                        ),
                        Container(
                          width: 1,
                          height: 36,
                          margin: const EdgeInsets.symmetric(horizontal: 14),
                          color: AppTheme.bezelEdge,
                        ),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(dateStr, style: AppTheme.bigLabel),
                              const SizedBox(height: 4),
                              Text(
                                '$dayName  ·  ${log.startKm.toStringAsFixed(0)} → ${log.endKm.toStringAsFixed(0)}',
                                style: AppTheme.caption,
                              ),
                            ],
                          ),
                        ),
                        Column(
                          crossAxisAlignment: CrossAxisAlignment.end,
                          children: [
                            Text(log.totalKm.toStringAsFixed(0),
                                style: AppTheme.bigNumber.copyWith(color: AppTheme.accentBright, fontSize: 22)),
                            Text('KM', style: AppTheme.sectionLabel),
                            const SizedBox(height: 4),
                            Text('${log.cost.toStringAsFixed(0)} AED', style: AppTheme.caption),
                          ],
                        ),
                      ],
                    ),
                  ),
                ),
              );
            },
          );
        },
      ),
      floatingActionButton: FloatingActionButton(
        child: const Icon(Icons.add, color: Color(0xFF1A0F00)),
        onPressed: () => Navigator.push(
          context,
          MaterialPageRoute(builder: (_) => const DailyLogFormScreen()),
        ),
      ),
    );
  }
}

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:intl/intl.dart';
import 'package:logestic_app/providers/log_provider.dart';
import 'package:logestic_app/models/service_log.dart';
import 'package:logestic_app/screens/service_form_screen.dart';
import 'package:logestic_app/theme/app_theme.dart';

class ServicesScreen extends StatelessWidget {
  const ServicesScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Services')),
      body: Consumer<LogProvider>(
        builder: (context, provider, _) {
          final services = provider.services;
          if (services.isEmpty) {
            return Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(Icons.build_outlined,
                      size: 64, color: AppTheme.mediumText.withValues(alpha: 0.4)),
                  const SizedBox(height: 16),
                  const Text('No services recorded yet',
                      style: TextStyle(color: AppTheme.mediumText, fontSize: 16)),
                  const SizedBox(height: 8),
                  const Text('Tap + to add a service record',
                      style: TextStyle(color: AppTheme.mediumText, fontSize: 13)),
                ],
              ),
            );
          }
          return ListView.builder(
            padding: const EdgeInsets.fromLTRB(16, 8, 16, 80),
            itemCount: services.length,
            itemBuilder: (context, index) {
              final svc = services[index];
              final dateStr = DateFormat('MMM d, yyyy').format(svc.date);
              final typeColor = ServiceLog.colorFor(svc.serviceType);
              final typeIcon = ServiceLog.iconFor(svc.serviceType);

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
                        builder: (_) =>
                            ServiceFormScreen(existingService: svc),
                      ),
                    ),
                    child: Container(
                      decoration: BoxDecoration(
                        borderRadius: BorderRadius.circular(16),
                        border: Border(
                          left: BorderSide(color: typeColor, width: 4),
                        ),
                      ),
                      padding: const EdgeInsets.all(16),
                      child: Row(
                        children: [
                          Container(
                            width: 48,
                            height: 48,
                            decoration: BoxDecoration(
                              color: typeColor.withValues(alpha: 0.1),
                              borderRadius: BorderRadius.circular(12),
                            ),
                            child: Icon(typeIcon, color: typeColor, size: 24),
                          ),
                          const SizedBox(width: 14),
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  ServiceLog.displayName(svc.serviceType),
                                  style: const TextStyle(
                                    color: AppTheme.darkText,
                                    fontSize: 15,
                                    fontWeight: FontWeight.w600,
                                  ),
                                ),
                                const SizedBox(height: 4),
                                Text(
                                  dateStr,
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
                                padding: const EdgeInsets.symmetric(
                                    horizontal: 8, vertical: 3),
                                decoration: BoxDecoration(
                                  color: typeColor.withValues(alpha: 0.1),
                                  borderRadius: BorderRadius.circular(8),
                                ),
                                child: Text(
                                  '${svc.kmReading.toStringAsFixed(0)} KM',
                                  style: TextStyle(
                                    color: typeColor,
                                    fontSize: 12,
                                    fontWeight: FontWeight.w700,
                                  ),
                                ),
                              ),
                              const SizedBox(height: 4),
                              Text(
                                '${svc.cost.toStringAsFixed(0)} DZD',
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
          MaterialPageRoute(builder: (_) => const ServiceFormScreen()),
        ),
      ),
    );
  }
}

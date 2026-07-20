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
      appBar: AppBar(title: const Text('SERVICES')),
      body: Consumer<LogProvider>(
        builder: (context, provider, _) {
          final services = provider.services;
          if (services.isEmpty) {
            return Center(
              child: Padding(
                padding: const EdgeInsets.symmetric(horizontal: 32),
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Icon(Icons.build_outlined, size: 56, color: AppTheme.tickDim),
                    const SizedBox(height: 16),
                    Text('NO SERVICES', style: AppTheme.bigLabel),
                    const SizedBox(height: 6),
                    Text('Tap the + button to log a service.',
                        textAlign: TextAlign.center, style: AppTheme.caption),
                  ],
                ),
              ),
            );
          }
          return ListView.builder(
            padding: const EdgeInsets.fromLTRB(16, 8, 16, 80),
            itemCount: services.length,
            itemBuilder: (context, index) {
              final svc = services[index];
              final dateStr = DateFormat('EEE · MMM d').format(svc.date).toUpperCase();
              final typeColor = ServiceLog.colorFor(svc.serviceType);
              final typeIcon = ServiceLog.iconFor(svc.serviceType);

              return Padding(
                padding: const EdgeInsets.only(bottom: 6),
                child: InkWell(
                  onTap: () => Navigator.push(
                    context,
                    MaterialPageRoute(builder: (_) => ServiceFormScreen(existingService: svc)),
                  ),
                  child: Container(
                    padding: const EdgeInsets.all(14),
                    decoration: BoxDecoration(
                      color: AppTheme.bezel,
                      border: Border(
                        left: BorderSide(color: typeColor, width: 3),
                        top: BorderSide(color: AppTheme.bezelEdge),
                        bottom: BorderSide(color: AppTheme.bezelEdge),
                        right: BorderSide(color: AppTheme.bezelEdge),
                      ),
                    ),
                    child: Row(
                      children: [
                        Container(
                          width: 40,
                          height: 40,
                          decoration: BoxDecoration(
                            color: typeColor.withValues(alpha: 0.15),
                            border: Border.all(color: typeColor.withValues(alpha: 0.4)),
                          ),
                          child: Icon(typeIcon, color: typeColor, size: 20),
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(ServiceLog.displayName(svc.serviceType).toUpperCase(),
                                  style: AppTheme.bigLabel),
                              const SizedBox(height: 4),
                              Text(dateStr, style: AppTheme.caption),
                            ],
                          ),
                        ),
                        Column(
                          crossAxisAlignment: CrossAxisAlignment.end,
                          children: [
                            Text(svc.kmReading.toStringAsFixed(0),
                                style: AppTheme.bigNumber.copyWith(fontSize: 20)),
                            Text('KM', style: AppTheme.sectionLabel),
                            const SizedBox(height: 4),
                            Text('${svc.cost.toStringAsFixed(0)} AED', style: AppTheme.caption),
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
          MaterialPageRoute(builder: (_) => const ServiceFormScreen()),
        ),
      ),
    );
  }
}

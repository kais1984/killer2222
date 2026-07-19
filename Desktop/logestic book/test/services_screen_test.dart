import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:provider/provider.dart';
import 'package:logestic_app/models/service_log.dart';
import 'package:logestic_app/providers/log_provider.dart';
import 'package:logestic_app/screens/services_screen.dart';

ServiceLog _svc(String type) => ServiceLog(
      id: type,
      date: DateTime(2026, 7, 18),
      kmReading: 12000,
      serviceType: type,
      cost: 500,
      notes: '',
    );

void main() {
  testWidgets('row shows the icon returned by ServiceLog.iconFor for each type',
      (tester) async {
    final provider = LogProvider();
    provider.setServicesForTest([
      _svc('oil_change'),
      _svc('petrol_refill'),
      _svc('wash'),
      _svc('unknown_blah'),
    ]);

    await tester.pumpWidget(
      ChangeNotifierProvider<LogProvider>.value(
        value: provider,
        child: const MaterialApp(home: ServicesScreen()),
      ),
    );
    await tester.pump();

    expect(find.byIcon(ServiceLog.iconFor('oil_change')), findsOneWidget);
    expect(find.byIcon(ServiceLog.iconFor('petrol_refill')), findsOneWidget);
    expect(find.byIcon(ServiceLog.iconFor('wash')), findsOneWidget);
    expect(find.byIcon(ServiceLog.iconFor('unknown_blah')), findsOneWidget);
  });
}
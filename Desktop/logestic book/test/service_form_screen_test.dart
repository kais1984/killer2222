import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:provider/provider.dart';
import 'package:logestic_app/models/service_log.dart';
import 'package:logestic_app/providers/log_provider.dart';
import 'package:logestic_app/screens/service_form_screen.dart';

void main() {
  testWidgets('each dropdown item shows its ServiceLog.iconFor icon',
      (tester) async {
    final provider = LogProvider();
    await tester.pumpWidget(
      ChangeNotifierProvider<LogProvider>.value(
        value: provider,
        child: const MaterialApp(home: ServiceFormScreen()),
      ),
    );
    await tester.pump();
    await tester.tap(find.byType(DropdownButtonFormField<String>));
    await tester.pumpAndSettle();

    for (final k in ServiceLog.serviceTypes) {
      expect(find.byIcon(ServiceLog.iconFor(k)),
          findsWidgets,
          reason: 'missing icon for $k');
    }
  });

  testWidgets('default prefixIcon mirrors oil_change', (tester) async {
    final provider = LogProvider();
    await tester.pumpWidget(
      ChangeNotifierProvider<LogProvider>.value(
        value: provider,
        child: const MaterialApp(home: ServiceFormScreen()),
      ),
    );
    await tester.pump();
    expect(find.byIcon(ServiceLog.iconFor('oil_change')), findsWidgets);
  });
}

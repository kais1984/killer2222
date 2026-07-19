import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:provider/provider.dart';
import 'package:logestic_app/models/daily_log.dart';
import 'package:logestic_app/providers/log_provider.dart';
import 'package:logestic_app/screens/daily_log_form_screen.dart';

DailyLog _log(DateTime date, double startKm, double endKm) => DailyLog(
      id: date.millisecondsSinceEpoch.toString(),
      date: date,
      startKm: startKm,
      endKm: endKm,
      totalKm: endKm - startKm,
      cost: 100,
      notes: '',
    );

Widget _wrap(Widget child, {required LogProvider provider}) =>
    ChangeNotifierProvider<LogProvider>.value(
      value: provider,
      child: MaterialApp(home: child),
    );

void main() {
  testWidgets('create mode pre-fills startKm and shows badge when prior log exists',
      (tester) async {
    final provider = LogProvider();
    provider.setDailyLogsForTest([
      _log(DateTime(2026, 7, 18), 12000, 12500),
    ]);
    await tester.pumpWidget(_wrap(const DailyLogFormScreen(), provider: provider));
    await tester.pump();

    final startKmText = find.byType(TextFormField).at(0);

    expect(
      tester.widget<TextFormField>(startKmText).controller!.text,
      '12500',
    );
    expect(find.byIcon(Icons.auto_fix_high), findsOneWidget);
  });

  testWidgets('create mode shows helper hint when no prior log exists', (tester) async {
    final provider = LogProvider();
    provider.setDailyLogsForTest([]);
    await tester.pumpWidget(_wrap(const DailyLogFormScreen(), provider: provider));
    await tester.pump();

    expect(find.text('No previous entry — enter the start odometer manually'),
        findsOneWidget);
    expect(find.byIcon(Icons.auto_fix_high), findsNothing);
  });

  testWidgets('create mode badge hides once the driver types over the value',
      (tester) async {
    final provider = LogProvider();
    provider.setDailyLogsForTest([_log(DateTime(2026, 7, 18), 12000, 12500)]);
    await tester.pumpWidget(_wrap(const DailyLogFormScreen(), provider: provider));
    await tester.pump();

    final startKmText = find.byType(TextFormField).at(0);

    await tester.enterText(startKmText, '99');
    await tester.pump();

    expect(find.byIcon(Icons.auto_fix_high), findsNothing);
  });

  testWidgets('edit mode never auto-fills and shows no badge', (tester) async {
    final provider = LogProvider();
    provider.setDailyLogsForTest([_log(DateTime(2026, 7, 18), 12000, 12500)]);
    final existing = _log(DateTime(2026, 7, 19), 13000, 14000);
    await tester.pumpWidget(
      _wrap(DailyLogFormScreen(existingLog: existing), provider: provider),
    );
    await tester.pump();

    final startKmText = find.byType(TextFormField).at(0);
    expect(tester.widget<TextFormField>(startKmText).controller!.text, '13000');
    expect(find.byIcon(Icons.auto_fix_high), findsNothing);
    expect(find.text('No previous entry — enter the start odometer manually'),
        findsNothing);
  });
}

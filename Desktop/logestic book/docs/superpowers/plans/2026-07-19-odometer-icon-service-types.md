# Odometer Continuity + App Icon & Expanded Service Types — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** (1) Pre-fill the New Daily Entry form's `Start KM` from the previous daily log's `End KM`. (2) Replace the default Flutter launcher icon with a custom "car + odometer" design. (3) Expand the Service Type dropdown from 5 to 15 maintenance categories, each with its own icon and color.

**Architecture:** Pure-Dart model changes (no Firestore schema changes) plus UI wiring. The launcher icon is produced by a procedural Dart generator (`tool/gen_icon.dart`) and fanned out to Android + iOS via `flutter_launcher_icons`. TDD throughout for logic; manual visual verification for the icon.

**Tech Stack:** Flutter 3.x / Dart, `provider`, `cloud_firestore`, `intl`, `image` (dev), `flutter_launcher_icons` (dev).

**Specs:**
- `docs/superpowers/specs/2026-07-19-odometer-continuity-design.md`
- `docs/superpowers/specs/2026-07-19-icon-and-service-types-design.md`

---

## File Structure

```
logestic book/
├── lib/
│   ├── models/
│   │   └── service_log.dart          # MODIFY: extend types, add iconFor/colorFor
│   ├── providers/
│   │   └── log_provider.dart         # MODIFY: add previousEndKmForDate + test seam
│   ├── screens/
│   │   ├── daily_log_form_screen.dart # MODIFY: auto-fill startKm, helperText, badge
│   │   ├── service_form_screen.dart  # MODIFY: per-type icons in dropdown, reactive prefixIcon
│   │   └── services_screen.dart      # MODIFY: delegate to ServiceLog.iconFor/colorFor
├── test/
│   ├── log_provider_test.dart        # CREATE
│   ├── service_log_test.dart         # CREATE
│   ├── daily_log_form_screen_test.dart # CREATE
│   └── service_form_screen_test.dart # CREATE
├── tool/
│   └── gen_icon.dart                 # CREATE
├── assets/
│   └── icon.png                      # CREATE (generated)
├── flutter_launcher_icons.yaml       # CREATE
└── pubspec.yaml                      # MODIFY: add dev deps, assets entry
```

---

## Task 1: `LogProvider.previousEndKmForDate` — failing tests

**Files:**
- Create: `test/log_provider_test.dart`
- Modify: `lib/providers/log_provider.dart` (add `@visibleForTesting` setter — see Task 2)

- [ ] **Step 1: Write the failing test file**

`test/log_provider_test.dart`:

```dart
import 'package:flutter/foundation.dart' show visibleForTesting;
import 'package:flutter_test/flutter_test.dart';
import 'package:logestic_app/models/daily_log.dart';
import 'package:logestic_app/providers/log_provider.dart';

DailyLog _log(DateTime date, double endKm) => DailyLog(
      id: '${date.millisecondsSinceEpoch}',
      date: date,
      startKm: 0,
      endKm: endKm,
      totalKm: endKm,
      cost: 0,
      notes: '',
    );

void main() {
  late LogProvider provider;
  setUp(() {
    provider = LogProvider();
    // Suppress Firestore attempt; we won't call startListening().
  });

  test('returns null when dailyLogs is empty', () {
    provider.setDailyLogsForTest([]);
    expect(provider.previousEndKmForDate(DateTime(2026, 7, 19)), isNull);
  });

  test('returns endKm of the single earlier log', () {
    provider.setDailyLogsForTest([
      _log(DateTime(2026, 7, 18), 12345),
    ]);
    expect(provider.previousEndKmForDate(DateTime(2026, 7, 19)), 12345);
  });

  test('picks the latest earlier date when multiple exist', () {
    provider.setDailyLogsForTest([
      _log(DateTime(2026, 7, 10), 10000),
      _log(DateTime(2026, 7, 17), 11000),
      _log(DateTime(2026, 7, 18), 12000),
    ]);
    expect(provider.previousEndKmForDate(DateTime(2026, 7, 19)), 12000);
  });

  test('tie-breaks same-date logs by larger endKm', () {
    provider.setDailyLogsForTest([
      _log(DateTime(2026, 7, 18), 11000),
      _log(DateTime(2026, 7, 18), 12000),
    ]);
    expect(provider.previousEndKmForDate(DateTime(2026, 7, 19)), 12000);
  });

  test('ignores same-day and later logs', () {
    provider.setDailyLogsForTest([
      _log(DateTime(2026, 7, 19, 8, 0), 9999),  // same day as query
      _log(DateTime(2026, 7, 20), 13000),       // later
    ]);
    expect(provider.previousEndKmForDate(DateTime(2026, 7, 19)), isNull);
  });

  test('ignores logs strictly after the chosen date', () {
    provider.setDailyLogsForTest([
      _log(DateTime(2026, 8, 1), 99999),
    ]);
    expect(provider.previousEndKmForDate(DateTime(2026, 7, 19)), isNull);
  });

  test('back-dating: respects chosen date, not today', () {
    provider.setDailyLogsForTest([
      _log(DateTime(2026, 7, 5), 9000),
      _log(DateTime(2026, 7, 18), 12000),
    ]);
    expect(provider.previousEndKmForDate(DateTime(2026, 7, 6)), 9000);
  });
}
```

- [ ] **Step 2: Run to verify it fails to compile**

Run: `flutter test test/log_provider_test.dart`
Expected: FAIL — `setDailyLogsForTest` and `previousEndKmForDate` are undefined.

---

## Task 2: Implement `previousEndKmForDate` + test seam

**Files:**
- Modify: `lib/providers/log_provider.dart`

- [ ] **Step 1: Add imports and the test seam + method**

Replace the top of `lib/providers/log_provider.dart`:

```dart
import 'package:flutter/foundation.dart';
import 'package:logestic_app/models/daily_log.dart';
import 'package:logestic_app/models/service_log.dart';
import 'package:logestic_app/services/firestore_service.dart';
```

Add `import 'package:flutter/foundation.dart' show visibleForTesting;` is already covered by the existing import.

Just before the closing `}` of `class LogProvider`, append:

```dart
  /// Returns the endKm of the most recent daily log strictly earlier than
  /// [date] (compared at day granularity). When multiple logs share that
  /// latest earlier date, the one with the largest endKm wins.
  /// Returns null when no qualifying log exists.
  double? previousEndKmForDate(DateTime date) {
    final dayStart = DateTime(date.year, date.month, date.day);
    DailyLog? latest;
    for (final l in _dailyLogs) {
      if (!l.date.isBefore(dayStart)) continue;
      if (latest == null ||
          l.date.isAfter(latest.date) ||
          (l.date.isAtSameMomentAs(latest.date) && l.endKm > latest.endKm)) {
        latest = l;
      }
    }
    return latest?.endKm;
  }

  @visibleForTesting
  void setDailyLogsForTest(List<DailyLog> logs) {
    _dailyLogs = logs;
  }
```

- [ ] **Step 2: Run the tests to verify they pass**

Run: `flutter test test/log_provider_test.dart`
Expected: All 7 tests PASS.

If a Firestore initialization error appears, it's because `LogProvider()` constructs `FirestoreService()` which calls `FirebaseFirestore.instance`. That only triggers when `startListening()` is called, not on construction. If construction itself fails, switch the test seam to inject a nullable `FirestoreService`:

```dart
LogProvider({FirestoreService? firestore})
    : _firestore = firestore ?? FirestoreService();
```

Then update tests: `LogProvider(firestore: _FakeFirestore())` is NOT needed unless construction fails; the simpler path above is preferred.

- [ ] **Step 3: Commit**

```bash
git add lib/providers/log_provider.dart test/log_provider_test.dart
git commit -m "feat(logs): add LogProvider.previousEndKmForDate with tests"
```

---

## Task 3: Wire auto-fill into `DailyLogFormScreen`

**Files:**
- Modify: `lib/screens/daily_log_form_screen.dart`
- Create: `test/daily_log_form_screen_test.dart`

- [ ] **Step 1: Write the failing widget test**

`test/daily_log_form_screen_test.dart`:

```dart
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

    final startField = find.widgetWithText(TextFormField, '').first;
    // Find the Start KM TextFormField by its label via an ancestor DecoratedBox.
    final startKmText = find.ancestor(
      of: find.text('Start KM'),
      matching: find.byType(TextFormField),
    );

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

    final startKmText = find.ancestor(
      of: find.text('Start KM'),
      matching: find.byType(TextFormField),
    );

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

    final startKmText = find.ancestor(
      of: find.text('Start KM'),
      matching: find.byType(TextFormField),
    );
    expect(tester.widget<TextFormField>(startKmText).controller!.text, '13000');
    expect(find.byIcon(Icons.auto_fix_high), findsNothing);
    expect(find.text('No previous entry — enter the start odometer manually'),
        findsNothing);
  });
}
```

- [ ] **Step 2: Run to verify it fails to compile**

Run: `flutter test test/daily_log_form_screen_test.dart`
Expected: FAIL — `_wrap` not finding previous entry (start field empty), badge absent.

- [ ] **Step 3: Modify `lib/screens/daily_log_form_screen.dart`**

3a. Add the `provider` import (already present — confirm).

3b. Update `_DailyLogFormScreenState`:

Replace:
```dart
class _DailyLogFormScreenState extends State<DailyLogFormScreen> {
  final _formKey = GlobalKey<FormState>();
  late TextEditingController _startKmCtrl;
  late TextEditingController _endKmCtrl;
  late TextEditingController _costCtrl;
  late TextEditingController _notesCtrl;
  late DateTime _selectedDate;
  bool _isEditing = false;

  @override
  void initState() {
    super.initState();
    _isEditing = widget.existingLog != null;
    _selectedDate = widget.existingLog?.date ?? DateTime.now();
    _startKmCtrl = TextEditingController(
        text: widget.existingLog?.startKm.toStringAsFixed(0) ?? '');
    _endKmCtrl = TextEditingController(
        text: widget.existingLog?.endKm.toStringAsFixed(0) ?? '');
    _costCtrl = TextEditingController(
        text: widget.existingLog?.cost.toStringAsFixed(2) ?? '');
    _notesCtrl =
        TextEditingController(text: widget.existingLog?.notes ?? '');
  }
```

with:

```dart
class _DailyLogFormScreenState extends State<DailyLogFormScreen> {
  final _formKey = GlobalKey<FormState>();
  late TextEditingController _startKmCtrl;
  late TextEditingController _endKmCtrl;
  late TextEditingController _costCtrl;
  late TextEditingController _notesCtrl;
  late DateTime _selectedDate;
  bool _isEditing = false;
  double? _autoFilledKm;
  bool _didPrefill = false;

  @override
  void initState() {
    super.initState();
    _isEditing = widget.existingLog != null;
    _selectedDate = widget.existingLog?.date ?? DateTime.now();
    _startKmCtrl = TextEditingController(
        text: widget.existingLog?.startKm.toStringAsFixed(0) ?? '');
    _endKmCtrl = TextEditingController(
        text: widget.existingLog?.endKm.toStringAsFixed(0) ?? '');
    _costCtrl = TextEditingController(
        text: widget.existingLog?.cost.toStringAsFixed(2) ?? '');
    _notesCtrl =
        TextEditingController(text: widget.existingLog?.notes ?? '');
  }

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    if (_didPrefill || _isEditing) {
      _didPrefill = true;
      return;
    }
    _didPrefill = true;
    final prev =
        Provider.of<LogProvider>(context, listen: false)
            .previousEndKmForDate(_selectedDate);
    if (prev != null) {
      _autoFilledKm = prev;
      _startKmCtrl.text = prev.toStringAsFixed(0);
    } else {
      _autoFilledKm = null;
    }
  }
```

3c. Update `_buildKmSection` so the Start KM field uses `helperText` and a suffix `auto_fix_high` icon. Replace the `Expanded(child: _buildTextField(...'Start KM'...))` block with:

```dart
              Expanded(
                child: _buildTextField(
                  controller: _startKmCtrl,
                  label: 'Start KM',
                  icon: Icons.trip_origin,
                  keyboardType: TextInputType.number,
                  validator: (v) =>
                      v == null || v.isEmpty ? 'Required' : null,
                  helperText: (_autoFilledKm == null && _startKmCtrl.text.isEmpty)
                      ? 'No previous entry — enter the start odometer manually'
                      : null,
                  suffixIcon: _showsAutoFillBadge()
                      ? const Icon(Icons.auto_fix_high,
                          size: 18, color: AppTheme.primaryLight)
                      : null,
                ),
              ),
```

Then extend `_buildTextField` to accept the two new optional params. Replace:
```dart
  Widget _buildTextField({
    required TextEditingController controller,
    required String label,
    required IconData icon,
    TextInputType? keyboardType,
    String? Function(String?)? validator,
    int maxLines = 1,
  }) {
    return TextFormField(
      controller: controller,
      decoration: InputDecoration(
        labelText: label,
        prefixIcon: Icon(icon),
      ),
      keyboardType: keyboardType,
      validator: validator,
      maxLines: maxLines,
    );
  }
```

with:

```dart
  Widget _buildTextField({
    required TextEditingController controller,
    required String label,
    required IconData icon,
    TextInputType? keyboardType,
    String? Function(String?)? validator,
    int maxLines = 1,
    String? helperText,
    Widget? suffixIcon,
  }) {
    return TextFormField(
      controller: controller,
      decoration: InputDecoration(
        labelText: label,
        prefixIcon: Icon(icon),
        helperText: helperText,
        suffixIcon: suffixIcon,
      ),
      keyboardType: keyboardType,
      validator: validator,
      maxLines: maxLines,
      onChanged: (_) => setState(() {}),
    );
  }
```

Note: the existing `_buildTextField` for `End KM`, `Cost`, and `Notes` calls do not pass `onChanged` today; End KM's `onChanged: (_) => setState(() {})` is currently on the field itself in the existing build — actually re-check: the existing `_buildTextField` does NOT set `onChanged` at all, yet the totalKm computation in `build()` reads `_startKmCtrl.text`. Looking at the existing code: there is already `onChanged: (_) => setState(() {}),` in the `TextFormField` returned by `_buildTextField` already. Keep that unchanged. The Start KM with the new suffix param will now also have `onChanged` -> `setState` which causes `_showsAutoFillBadge()` to recompute and hide the badge once text differs from the auto-filled value.

Add the helper method near `_confirmDelete`:

```dart
  bool _showsAutoFillBadge() {
    if (_autoFilledKm == null) return false;
    return _startKmCtrl.text == _autoFilledKm!.toStringAsFixed(0);
  }
```

- [ ] **Step 4: Run the widget tests to verify they pass**

Run: `flutter test test/daily_log_form_screen_test.dart`
Expected: All 4 tests PASS.

If `find.ancestor(of: find.text('Start KM'))` fails because the label isn't a separate Text widget, switch the test to find the TextFormField by index using `find.byType(TextFormField).at(0)`:

```dart
final startKmText = find.byType(TextFormField).at(0);
```

(Start KM is the first TextFormField in the form.)

- [ ] **Step 5: Commit**

```bash
git add lib/screens/daily_log_form_screen.dart test/daily_log_form_screen_test.dart
git commit -m "feat(daily): auto-fill startKm from previous entry endKm"
```

---

## Task 4: Extend `ServiceLog` types + icon/color helpers — tests first

**Files:**
- Create: `test/service_log_test.dart`
- Modify: `lib/models/service_log.dart`

- [ ] **Step 1: Write the failing test**

`test/service_log_test.dart`:

```dart
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:logestic_app/models/service_log.dart';
import 'package:logestic_app/theme/app_theme.dart';

void main() {
  test('serviceTypes contains 15 entries', () {
    expect(ServiceLog.serviceTypes.length, 15);
  });

  test('original 5 keys are preserved', () {
    const original = [
      'oil_change', 'repair', 'painting', 'part_replacement', 'other',
    ];
    for (final k in original) {
      expect(ServiceLog.serviceTypes, contains(k));
    }
  });

  test('new 10 keys are present', () {
    const added = [
      'petrol_refill', 'tyre', 'brake_service', 'battery', 'filter_change',
      'fluids_topup', 'wash', 'inspection', 'insurance_registration',
      'accessories',
    ];
    for (final k in added) {
      expect(ServiceLog.serviceTypes, contains(k));
    }
  });

  test('displayName returns a non-empty label for every known key', () {
    for (final k in ServiceLog.serviceTypes) {
      final label = ServiceLog.displayName(k);
      expect(label, isNotEmpty);
      expect(label[0], matches(RegExp(r'[A-Z]')));
    }
  });

  test('iconFor returns a non-null IconData for every known key', () {
    for (final k in ServiceLog.serviceTypes) {
      expect(ServiceLog.iconFor(k), isNotNull);
    }
  });

  test('colorFor returns a non-null Color for every known key', () {
    for (final k in ServiceLog.serviceTypes) {
      expect(ServiceLog.colorFor(k), isA<Color>());
    }
  });

  test('unknown type falls back gracefully', () {
    expect(ServiceLog.displayName('foobar'), 'foobar');
    expect(ServiceLog.iconFor('foobar'), Icons.build);
    expect(ServiceLog.colorFor('foobar'), AppTheme.mediumText);
  });

  test('oil_change keeps existing icon/color (regression)', () {
    expect(ServiceLog.iconFor('oil_change'), Icons.oil_barrel);
    expect(ServiceLog.colorFor('oil_change'), AppTheme.primaryLight);
  });

  test('repair keeps existing icon/color', () {
    expect(ServiceLog.iconFor('repair'), Icons.build);
    expect(ServiceLog.colorFor('repair'), AppTheme.error);
  });

  test('painting keeps existing icon/color', () {
    expect(ServiceLog.iconFor('painting'), Icons.format_paint);
    expect(ServiceLog.colorFor('painting'), const Color(0xFF8B5CF6));
  });

  test('part_replacement keeps existing icon/color', () {
    expect(ServiceLog.iconFor('part_replacement'), Icons.settings);
    expect(ServiceLog.colorFor('part_replacement'), AppTheme.secondary);
  });

  test('other keeps existing icon/color', () {
    expect(ServiceLog.iconFor('other'), Icons.more_horiz);
    expect(ServiceLog.colorFor('other'), AppTheme.accent);
  });
}
```

- [ ] **Step 2: Run to verify it fails**

Run: `flutter test test/service_log_test.dart`
Expected: FAIL — keys `petrol_refill`, etc. don't exist; `iconFor`/`colorFor` undefined.

- [ ] **Step 3: Modify `lib/models/service_log.dart`**

Add at top of file (above `class ServiceLog {`):

```dart
import 'package:flutter/material.dart' show Color, IconData, Icons;
import 'package:logestic_app/theme/app_theme.dart' show AppTheme;
```

Replace the existing `serviceTypes` const and `displayName` switch:

```dart
  static const List<String> serviceTypes = [
    'oil_change',
    'repair',
    'painting',
    'part_replacement',
    'petrol_refill',
    'tyre',
    'brake_service',
    'battery',
    'filter_change',
    'fluids_topup',
    'wash',
    'inspection',
    'insurance_registration',
    'accessories',
    'other',
  ];

  static String displayName(String type) {
    switch (type) {
      case 'oil_change':               return 'Oil Change';
      case 'repair':                   return 'Repair';
      case 'painting':                 return 'Painting';
      case 'part_replacement':         return 'Part Replacement';
      case 'petrol_refill':            return 'Petrol Refill';
      case 'tyre':                     return 'Tyre Replacement / Rotation';
      case 'brake_service':            return 'Brake Service';
      case 'battery':                  return 'Battery';
      case 'filter_change':            return 'Filter Change (Air / AC / Fuel)';
      case 'fluids_topup':             return 'Fluids Top-up';
      case 'wash':                     return 'Wash / Cleaning';
      case 'inspection':               return 'Inspection / Diagnosis';
      case 'insurance_registration':   return 'Insurance / Registration';
      case 'accessories':              return 'Accessories';
      case 'other':                    return 'Other';
      default:                         return type;
    }
  }

  static IconData iconFor(String type) {
    switch (type) {
      case 'oil_change':             return Icons.oil_barrel;
      case 'repair':                 return Icons.build;
      case 'painting':               return Icons.format_paint;
      case 'part_replacement':       return Icons.settings;
      case 'petrol_refill':          return Icons.local_gas_station;
      case 'tyre':                   return Icons.trip_origin;
      case 'brake_service':          return Icons.disc_full;
      case 'battery':                return Icons.battery_charging_full;
      case 'filter_change':          return Icons.air;
      case 'fluids_topup':           return Icons.water_drop;
      case 'wash':                   return Icons.local_car_wash;
      case 'inspection':             return Icons.fact_check;
      case 'insurance_registration': return Icons.assignment;
      case 'accessories':            return Icons.extension;
      case 'other':                  return Icons.more_horiz;
      default:                       return Icons.build;
    }
  }

  static Color colorFor(String type) {
    switch (type) {
      case 'oil_change':             return AppTheme.primaryLight;
      case 'repair':                 return AppTheme.error;
      case 'painting':               return const Color(0xFF8B5CF6);
      case 'part_replacement':       return AppTheme.secondary;
      case 'petrol_refill':          return const Color(0xFFEF4444);
      case 'tyre':                   return const Color(0xFF1F2937);
      case 'brake_service':          return const Color(0xFFDC2626);
      case 'battery':                return const Color(0xFF16A34A);
      case 'filter_change':          return const Color(0xFF0EA5E9);
      case 'fluids_topup':           return const Color(0xFF0891B2);
      case 'wash':                   return const Color(0xFF38BDF8);
      case 'inspection':             return AppTheme.accent;
      case 'insurance_registration': return const Color(0xFF6366F1);
      case 'accessories':            return const Color(0xFFEC4899);
      case 'other':                  return AppTheme.accent;
      default:                      return AppTheme.mediumText;
    }
  }
```

- [ ] **Step 4: Run the tests**

Run: `flutter test test/service_log_test.dart`
Expected: All 13 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add lib/models/service_log.dart test/service_log_test.dart
git commit -m "feat(services): expand service types and add iconFor/colorFor"
```

---

## Task 5: Delegate `services_screen.dart` to model helpers — tests first

**Files:**
- Modify: `lib/screens/services_screen.dart`
- Create: `test/services_screen_test.dart`

- [ ] **Step 1: Write the failing widget test**

`test/services_screen_test.dart`:

```dart
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
```

Note: this requires a second test seam — `setServicesForTest` — which we add to `LogProvider` alongside `setDailyLogsForTest` in this task.

- [ ] **Step 2: Run to verify it fails to compile**

Run: `flutter test test/services_screen_test.dart`
Expected: FAIL — `setServicesForTest` undefined; `_typeIcon` still private overrides the icon.

- [ ] **Step 3: Add `setServicesForTest` seam to `LogProvider`**

In `lib/providers/log_provider.dart`, after the existing `setDailyLogsForTest`, add:

```dart
  @visibleForTesting
  void setServicesForTest(List<ServiceLog> svcs) {
    _services = svcs;
  }
```

- [ ] **Step 4: Delete private helpers and delegate to the model**

In `lib/screens/services_screen.dart`, replace:

```dart
              final typeColor = _typeColor(svc.serviceType);
              final typeIcon = _typeIcon(svc.serviceType);
```

with:

```dart
              final typeColor = ServiceLog.colorFor(svc.serviceType);
              final typeIcon = ServiceLog.iconFor(svc.serviceType);
```

Then delete the private helpers `_typeColor` and `_typeIcon` (the two switch functions at the bottom of the file). The remaining imports are sufficient because `ServiceLog` is already imported.

- [ ] **Step 5: Run the test**

Run: `flutter test test/services_screen_test.dart`
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add lib/providers/log_provider.dart lib/screens/services_screen.dart test/services_screen_test.dart
git commit -m "refactor(services): use ServiceLog.iconFor/colorFor in list rows"
```

---

## Task 6: Wire per-type icons into the service form dropdown — test first

**Files:**
- Modify: `lib/screens/service_form_screen.dart`
- Create: `test/service_form_screen_test.dart`

- [ ] **Step 1: Write the failing widget test**

`test/service_form_screen_test.dart`:

```dart
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:provider/provider.dart';
import 'package:logestic_app/models/service_log.dart';
import 'package:logestic_app/providers/log_provider.dart';
import 'package:logestic_app/screens/service_form_screen.dart';

void main() {
  testWidgets('dropdown shows all 15 types each with an icon',
      (tester) async {
    final provider = LogProvider();

    await tester.pumpWidget(
      ChangeNotifierProvider<LogProvider>.value(
        value: provider,
        child: const MaterialApp(home: ServiceFormScreen()),
      ),
    );
    await tester.pump();

    final dropdown = find.byType(DropdownButtonFormField<String>);
    expect(dropdown, findsOneWidget);
    await tester.tap(dropdown);
    await tester.pumpAndSettle();

    for (final k in ServiceLog.serviceTypes) {
      expect(find.text(ServiceLog.displayName(k)), findsWidgets);
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
```

- [ ] **Step 2: Run to verify the first assertion fails (icons may or may not be present; the prefixIcon will default)**

Run: `flutter test test/service_form_screen_test.dart`
Expected: FAIL — `find.byIcon(Icons.local_gas_station)` may be missing because only the first item is rendered until the dropdown opens. The test opens the dropdown, so all 15 labels appear. The assertion that should fail before changes: the dropdown's per-item icons do not exist yet (`DropdownMenuItem` body is plain `Text`).

Tighten the test before continuing:

```dart
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
```

Replace the previously written first test's body with this stronger version.

- [ ] **Step 3: Modify `lib/screens/service_form_screen.dart`**

Replace the `_buildTypeDropdown` method:

```dart
  Widget _buildTypeDropdown() {
    return DropdownButtonFormField<String>(
      initialValue: _selectedType,
      decoration: InputDecoration(
        labelText: 'Service Type',
        prefixIcon: Icon(
          ServiceLog.iconFor(_selectedType),
          color: ServiceLog.colorFor(_selectedType),
        ),
      ),
      items: ServiceLog.serviceTypes.map((type) {
        return DropdownMenuItem(
          value: type,
          child: Row(
            children: [
              Icon(ServiceLog.iconFor(type),
                  size: 20, color: ServiceLog.colorFor(type)),
              const SizedBox(width: 10),
              Expanded(child: Text(ServiceLog.displayName(type))),
            ],
          ),
        );
      }).toList(),
      onChanged: (v) {
        if (v != null) setState(() => _selectedType = v);
      },
    );
  }
```

- [ ] **Step 4: Run the widget tests**

Run: `flutter test test/service_form_screen_test.dart`
Expected: All tests PASS.

- [ ] **Step 5: Commit**

```bash
git add lib/screens/service_form_screen.dart test/service_form_screen_test.dart
git commit -m "feat(service-form): per-type icons in dropdown + reactive prefixIcon"
```

---

## Task 7: Add `flutter_launcher_icons` + `image` dev deps and the YAML

**Files:**
- Modify: `pubspec.yaml`
- Create: `flutter_launcher_icons.yaml`

- [ ] **Step 1: Add dev dependencies**

Open `pubspec.yaml`. Under `dev_dependencies:` add (keep `flutter_test` and `flutter_lints` entries intact):

```yaml
  flutter_launcher_icons: ^0.14.4
```

Under `dependencies:`, the `excel` and others entries already use `image` indirectly — but our `tool/gen_icon.dart` script imports `package:image/image.dart`. Confirm `image: ^4.0.0` is *not* currently a runtime dependency. Looking at the pubspec: it is *not* listed. Add it under `dev_dependencies:` as well (it's a codegen tool, not used by the app):

```yaml
  image: ^4.0.0
```

Final `dev_dependencies` block:

```yaml
dev_dependencies:
  flutter_test:
    sdk: flutter
  flutter_lints: ^6.0.0
  flutter_launcher_icons: ^0.14.4
  image: ^4.0.0
```

Under `flutter:` at the bottom, add an `assets:` block:

```yaml
  assets:
    - assets/icon.png
```

- [ ] **Step 2: Run `flutter pub get`**

Run: `flutter pub get`
Expected: resolves.

- [ ] **Step 3: Create `flutter_launcher_icons.yaml`**

```yaml
flutter_launcher_icons:
  android: true
  ios: true
  image_path: assets/icon.png
  min_sdk_android: 21
  remove_alpha_ios: true
  background_color_ios: "#1E40AF"
  web:
    generate: true
    image_path: assets/icon.png
    background_color: "#1E40AF"
    theme_color: "#1E40AF"
```

- [ ] **Step 4: Commit (assets entry works as soon as assets/icon.png exists; we add it next)**

Defer commit to Task 9 after the asset exists.

---

## Task 8: Write `tool/gen_icon.dart` and generate `assets/icon.png`

**Files:**
- Create: `assets/` (directory)
- Create: `tool/gen_icon.dart`
- Create: `assets/icon.png` (binary output)

- [ ] **Step 1: Create the `tool` directory and the generator script**

`tool/gen_icon.dart`:

```dart
// Generates assets/icon.png (1024x1024) for the driver log book app icon.
// Run from project root:  dart run tool/gen_icon.dart

import 'dart:io';
import 'dart:math' as math;
import 'dart:typed_data';
import 'package:image/image.dart' as img;

const int kSize = 1024;
const int kRadius = 220;

const int kPrimary = 0xFF1E40AF;
const int kPrimaryLight = 0xFF3B82F6;
const int kDarkText = 0xFF1E293B;
const int kAmber = 0xFFF59E0B;
const int kAmber2 = 0xFFF97316;
const int kWhite = 0xFFFFFFFF;

int lerpColor(int a, int b, double t) {
  int la = (a >> 16) & 0xff, lra = (a >> 8) & 0xff, lba = a & 0xff;
  int lb = (b >> 16) & 0xff, lrb = (b >> 8) & 0xff, lbb = b & 0xff;
  int r = (la + (lb - la) * t).round();
  int g = (lra + (lrb - lra) * t).round();
  int bl = (lba + (lbb - lba) * t).round();
  return (0xff << 24) | (r << 16) | (g << 8) | bl;
}

void fillRoundRect(img.Image im, int x0, int y0, int x1, int y1, int radius) {
  for (int y = y0; y < y1; y++) {
    for (int x = x0; x < x1; x++) {
      bool inside = true;
      // corner checks
      int dxLeft = x0 + radius - x;
      int dyTop = y0 + radius - y;
      int dxRight = x - (x1 - radius - 1);
      int dyBot = y - (y1 - radius - 1);
      if (x < x0 + radius && y < y0 + radius) {
        inside = dxLeft * dxLeft + dyTop * dyTop <= radius * radius;
      } else if (x >= x1 - radius && y < y0 + radius) {
        inside = dxRight * dxRight + dyTop * dyTop <= radius * radius;
      } else if (x < x0 + radius && y >= y1 - radius) {
        inside = dxLeft * dxLeft + dyBot * dyBot <= radius * radius;
      } else if (x >= x1 - radius && y >= y1 - radius) {
        inside = dxRight * dxRight + dyBot * dyBot <= radius * radius;
      }
      if (inside) {
        img.drawPixel(im, x, y, kWhite);
      }
    }
  }
}

void fillCircle(img.Image im, int cx, int cy, int r, int color,
    {bool cover = true}) {
  for (int y = -r; y <= r; y++) {
    for (int x = -r; x <= r; x++) {
      if (x * x + y * y <= r * r) {
        img.drawPixel(im, cx + x, cy + y, color, cover);
      }
    }
  }
}

void fillRoundRectGradient(img.Image im, int x0, int y0, int x1, int y1,
    int radius, int top, int bottom) {
  for (int y = y0; y < y1; y++) {
    final t = (y - y0) / (y1 - y0 - 1);
    final col = lerpColor(top, bottom, t);
    for (int x = x0; x < x1; x++) {
      bool inside = true;
      int dxLeft = x0 + radius - x;
      int dyTop = y0 + radius - y;
      int dxRight = x - (x1 - radius - 1);
      int dyBot = y - (y1 - radius - 1);
      if (x < x0 + radius && y < y0 + radius) {
        inside = dxLeft * dxLeft + dyTop * dyTop <= radius * radius;
      } else if (x >= x1 - radius && y < y0 + radius) {
        inside = dxRight * dxRight + dyTop * dyTop <= radius * radius;
      } else if (x < x0 + radius && y >= y1 - radius) {
        inside = dxLeft * dxLeft + dyBot * dyBot <= radius * radius;
      } else if (x >= x1 - radius && y >= y1 - radius) {
        inside = dxRight * dxRight + dyBot * dyBot <= radius * radius;
      }
      if (inside) {
        img.drawPixel(im, x, y, col, true);
      }
    }
  }
}

/// Filled polygon given list of (x,y) integer vertices.
void fillPolygon(img.Image im, List<List<int>> pts, int color) {
  final ys = pts.map((p) => p[1]).toList();
  int ymin = ys.reduce(math.min), ymax = ys.reduce(math.max);
  for (int y = ymin; y <= ymax; y++) {
    final xs = <int>[];
    for (int i = 0; i < pts.length; i++) {
      final p1 = pts[i];
      final p2 = pts[(i + 1) % pts.length];
      if ((p1[1] <= y && p2[1] > y) || (p2[1] <= y && p1[1] > y)) {
        final x = p1[0] + (y - p1[1]) * (p2[0] - p1[0]) / (p2[1] - p1[1]);
        xs.add(x.round());
      }
    }
    xs.sort();
    for (int i = 0; i + 1 < xs.length; i += 2) {
      for (int x = xs[i]; x <= xs[i + 1]; x++) {
        img.drawPixel(im, x, y, color, true);
      }
    }
  }
}

void drawAALine(img.Image im, int x0, int y0, int x1, int y1, int color,
    [double thickness = 4]) {
  img.drawLine(im, x0, y0, x1, y1, color, thickness.round());
}

void main() {
  final im = img.Image(kSize, kSize);

  // 1) Rounded-rect background with vertical gradient.
  fillRoundRectGradient(im, 0, 0, kSize, kSize, kRadius, kPrimary, kPrimaryLight);

  // 2) Car body — rounded rectangle, centered. white.
  const carBodyX0 = 230, carBodyY0 = 480, carBodyX1 = 794, carBodyY1 = 660;
  fillRoundRect(im, carBodyX0, carBodyY0, carBodyX1, carBodyY1, 60, kWhite);

  // 3) Cabin — trapezoid above the body, white.
  fillPolygon(im, [
    [340, 380],
    [684, 380],
    [744, 480],
    [280, 480],
  ], kWhite);

  // 4) Wheels — dark blue circles.
  fillCircle(im, 360, 660, 56, kDarkText);
  fillCircle(im, 664, 660, 56, kDarkText);

  // 5) Speedometer badge — amber arc in the top-right.
  // Approximate as a thick ring segment drawn as a filled outer minus inner
  // disc, masked into a 120-degree arc opening downward.
  const gaugeCx = 760, gaugeCy = 250;
  const outerR = 130, innerR = 92;
  // Draw outer amber disk.
  fillCircle(im, gaugeCx, gaugeCy, outerR, kAmber);
  // Cut inner hole (paint background gradient back). Re-draw the same gradient
  // pixels within the inner disc by re-evaluating the gradient color.
  {
    for (int y = -innerR; y <= innerR; y++) {
      for (int x = -innerR; x <= innerR; x++) {
        if (x * x + y * y > innerR * innerR) continue;
        final px = gaugeCx + x, py = gaugeCy + y;
        if (px < 0 || px >= kSize || py < 0 || py >= kSize) continue;
        // Only paint pixels in the upper 240 degrees of the gauge (the open
        // part is at the bottom). For the inner hole, we want to remove the
        // bottom ~120deg so the gauge reads as an arc.
        final ang = math.atan2(y, x); // -pi..pi, 0 = east, increases CCW
        // Open at bottom: skip pixels whose angle points toward bottom.
        if (ang > math.pi * 0.10 && ang < math.pi * 0.90) {
          // re-apply gradient
          final t = py / (kSize - 1);
          img.drawPixel(im, px, py, lerpColor(kPrimary, kPrimaryLight, t), true);
        }
      }
    }
  }

  // Also cut the bottom of the outer ring to make it a 120-degree-arc open at
  // the bottom rather than a full disk.
  {
    for (int y = -outerR; y <= outerR; y++) {
      for (int x = -outerR; x <= outerR; x++) {
        if (x * x + y * y > outerR * outerR) continue;
        final ang = math.atan2(y, x);
        // Open at bottom: if within ~60deg around straight-down, restore bg.
        if (ang > math.pi * 0.10 && ang < math.pi * 0.90) {
          final px = gaugeCx + x, py = gaugeCy + y;
          if (px < 0 || px >= kSize || py < 0 || py >= kSize) continue;
          final t = py / (kSize - 1);
          img.drawPixel(im, px, py, lerpColor(kPrimary, kPrimaryLight, t), true);
        }
      }
    }
  }

  // 6) Thin white inner ring inside the gauge.
  final ringR = (outerR + innerR) ~/ 2;
  for (double a = -math.pi * 0.6; a <= math.pi * 0.6; a += 0.01) {
    // Skip the bottom open part.
    if (a > 0.1 * math.pi && a < 0.9 * math.pi) continue;
    final px = gaugeCx + ringR * math.cos(a);
    final py = gaugeCy - ringR * math.sin(a);
    img.drawPixel(im, px.round(), py.round(), kWhite, true);
  }

  // 7) Needle — from hub to ~3 o'clock.
  drawAALine(im, gaugeCx, gaugeCy,
      gaugeCx + (outerR - 14), gaugeCy - 8, kWhite, 6);

  // 8) Hub dot — amber2 accent.
  fillCircle(im, gaugeCx, gaugeCy, 12, kAmber2);

  // Encode and save.
  final png = img.encodePng(im);
  final file = File('assets/icon.png');
  file.createSync(recursive: true);
  file.writeAsBytesSync(png);
  stdout.writeln('Wrote assets/icon.png (\${png.length} bytes)');
}
```

- [ ] **Step 2: Create the `assets` directory**

Run: `mkdir assets` (or `New-Item -ItemType Directory -Path assets`)

- [ ] **Step 3: Run the generator**

Run: `dart run tool/gen_icon.dart`
Expected: prints `Wrote assets/icon.png (<size> bytes)`. The PNG is created at `assets/icon.png`.

- [ ] **Step 4: Manual visual check**

Open `assets/icon.png` in an image viewer. Confirm:
- Rounded blue gradient square (~220 px corner radius).
- White car shape centered (rounded body, trapezoid cabin, two dark-blue wheels).
- Amber gauge arc at top-right, opening downward, with a white needle pointing right and a small darker amber hub dot.

If the composition looks off (e.g. cabin overlaps body too much, wheels stick out below body), adjust the constants in the script: `carBodyY0`, `carBodyY1`, the cabin polygon points, wheel centers (360, 664 vs body edges), gauge position. Re-run Step 3 after each change and re-open the PNG.

- [ ] **Step 5: Commit the script and the generated asset**

```bash
git add tool/gen_icon.dart assets/icon.png
git commit -m "build(icon): add procedural icon generator and 1024px source PNG"
```

---

## Task 9: Run `flutter_launcher_icons` to fan out the icon

**Files:**
- Modifies (regenerates): `android/app/src/main/res/mipmap-*` and `mipmap-anydpi-v26/*`, `ios/Runner/Assets.xcassets/AppIcon.appiconset/*.png`, `web/favicon.png` (and related).

- [ ] **Step 1: Ensure Flutter can resolve config**

Run: `flutter pub get`
Expected: resolves cleanly with no errors about missing launcher icons config.

- [ ] **Step 2: Run `flutter_launcher_icons`**

Run: `dart run flutter_launcher_icons`
Expected: Prints lines like:
```
Android launcher icon generated
iOS launcher icon generated
Web launcher icon generated
```
No errors. The `mipmap-*` PNGs and `iOS AppIcon.appiconset` PNGs are rewritten; `mipmap-anydpi-v26/ic_launcher.xml` and `ic_launcher_round.xml` are created/updated; `web/favicon.png` and `web/icons/*` regenerate.

- [ ] **Step 3: Manual sanity check**

Open `android/app/src/main/res/mipmap-xxxhdpi/ic_launcher.png` in an image viewer. Confirm it visually matches `assets/icon.png` at smaller scale. Repeat for one iOS size, e.g. `ios/Runner/Assets.xcassets/AppIcon.appiconset/Icon-App-1024x1024@1x.png`.

- [ ] **Step 4: Commit all regenerated assets**

```bash
git add android/app/src/main/res ios/Runner/Assets.xcassets/AppIcon.appiconset web
git commit -m "build(icon): regenerate android/ios/web launcher icons from source PNG"
```

---

## Task 10: Full test pass + smoke build

- [ ] **Step 1: Run all tests**

Run: `flutter test`
Expected: All tests in `test/` PASS (including the default `widget_test.dart`).

- [ ] **Step 2: Static analysis**

Run: `flutter analyze`
Expected: no errors. Info-level warnings OK to keep; fix anything `warning`-level or above introduced by our edits.

- [ ] **Step 3: Build (Android debug)**

Run: `flutter build apk --debug`
Expected: succeeds; launcher icon reported in the APK is the new one.

- [ ] **Step 4: Build (iOS debug, no codesign — if on macOS)**

Run: `flutter build ios --debug --no-codesign`
Expected: succeeds if on macOS host. On Windows, skip this step and note iOS build requires macOS.

- [ ] **Step 5: Final commit (if anything was touched during analysis fixes)**

```bash
git add -A
git commit -m "chore: pass full test suite and analyzer after icon + service-type changes" --allow-empty
```

Skip if there's nothing to commit.

---

## Self-Review (per writing-plans skill)

**Spec coverage check:**
- Odometer spec — Method `previousEndKmForDate` (Task 2). Form wiring with suffix badge + helperText (Task 3). Tests for both. Edit-mode non-fill and back-dating cases covered. ✓
- Icon spec — `tool/gen_icon.dart` (Task 8). `flutter_launcher_icons.yaml` + run (Task 9). Brand colors, rounded-rect gradient, car, gauge all covered. ✓
- Service types spec — `serviceTypes` extended to 15; `displayName`, `iconFor`, `colorFor` (Task 4). Dropdown items show icons + reactive prefixIcon (Task 6). Services list delegates to model helpers (Task 5). Compat for old entries preserved. ✓
- Tests for both new helpers and both screens. ✓
- Manual verification for icon visuals is captured. ✓

**Placeholder scan:**
- No "TBD/TODO/implement later". All code blocks are complete.
- The single "adjust the constants" guidance in Task 8 Step 4 is intentional — visual iteration is inherent to icon design and cannot be eliminated programmatically without a near-arbitrary test assertion that would be more brittle than helpful.
- No missing imports in tasks: each file edit names its imports.

**Type/method consistency:**
- `previousEndKmForDate(DateTime) -> double?` — used identically in Task 2 (def) and Task 3 (call). ✓
- `setDailyLogsForTest(List<DailyLog>)` — used in Task 1 (test), Task 2 (def), Task 3 (test). ✓
- `setServicesForTest(List<ServiceLog>)` — used in Task 5 (def + test). ✓
- `ServiceLog.iconFor(String) -> IconData` and `ServiceLog.colorFor(String) -> Color` — used identically in Task 4 (def) and Tasks 5, 6 (call). ✓
- `_autoFilledKm`, `_didPrefill`, `_showsAutoFillBadge()` — consistent in Task 3. ✓
- Icon names: `Icons.oil_barrel`, `Icons.settings`, `Icons.format_paint`, `Icons.more_horiz` (kept from the existing code); `Icons.local_gas_station`, `Icons.trip_origin`, `Icons.disc_full`, `Icons.battery_charging_full`, `Icons.air`, `Icons.water_drop`, `Icons.local_car_wash`, `Icons.fact_check`, `Icons.assignment`, `Icons.extension` for the new types — all are real Material icons available in Flutter 3.x. ✓
- Color hex constants: `0xFF8B5CF6`, `0xFFEF4444`, `0xFF1F2937`, `0xFFDC2626`, `0xFF16A34A`, `0xFF0EA5E9`, `0xFF0891B2`, `0xFF38BDF8`, `0xFF6366F1`, `0xFFEC4899` — all valid 0xAARRGGBB values. ✓

No issues found.
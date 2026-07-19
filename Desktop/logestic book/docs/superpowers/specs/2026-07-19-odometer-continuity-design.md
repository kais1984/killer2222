# Odometer Continuity for Daily Log — Design

## Overview
When the driver opens the **New Daily Entry** form, the `Start KM` field is automatically pre-filled with the `End KM` of the most recent previous daily log. This carries the odometer reading forward from one day to the next so the driver does not have to re-type it. If no previous entry exists, the field stays empty and a helper hint tells the driver to enter the value manually.

## Scope

### In scope
- Pre-fill `startKm` on the New Daily Entry form using the previous entry's `endKm`.
- Selection rule: most recent daily log whose date is *strictly earlier* than the form's selected date.
- Empty + helper hint when no previous log exists.
- The field remains fully editable by the driver.

### Out of scope (explicitly decided)
- No recompute on date change. Pre-fill happens only once, when the form opens in create mode.
- No auto-fill on the edit form. Editing an existing entry keeps loading its stored `startKm` as today.
- No locking / read-only enforcement of the field.
- No fallback to a service log's `kmReading` when no previous daily log exists.
- No changes to Home, Daily Logs list, Monthly Report, or Firestore schema.

## Behavior

### Trigger
Only on opening `DailyLogFormScreen` in *create* mode (`widget.existingLog == null`), exactly once.

### Selection rule
Given the form's currently selected date (default = today), find among `LogProvider.dailyLogs` the entries whose date is strictly earlier than the start of the selected day (`DateTime(date.year, date.month, date.day)`). If the resulting set is non-empty, pick the entry with the latest date; if multiple entries share that latest date, pick the one with the largest `endKm`. Return its `endKm`. Otherwise return null.

### UI behavior
- The `Start KM` `TextFormField` is initialized with the returned value (formatted with `toStringAsFixed(0)`).
- The field is fully editable; the driver may overwrite the value at any time.
- A subtle suffix `'auto_fix_high'` icon with the tooltip `'Auto-filled from previous entry's End KM'` is shown next to the Start KM field while the field still equals the auto-filled value. The icon disappears as soon as the driver types anything (i.e., when the field text no longer matches the auto-filled value).
- If null is returned, the `Start KM` field stays empty and its `helperText` shows `'No previous entry — enter the start odometer manually.'`.
- The `Total KM` read-only computation already in the form reacts to the pre-filled value the same way it reacts to any user-typed value.

### Edge cases
| Case | Result |
|------|--------|
| No daily logs at all (first ever entry) | Empty start field + helper hint |
| Only same-date log(s) exist for the chosen date | Empty start field + helper hint (selection is strictly-earlier only) |
| Multiple logs exist on the latest earlier date | The one with the largest `endKm` is used |
| User back-dates an entry (picks an earlier date than today) | Pre-fill uses the most recent log strictly earlier than that chosen date |
| Edit mode (`existingLog != null`) | No auto-fill; existing `startKm` is loaded as today |
| Provider list is empty due to Firestore not yet loaded | Empty start field + helper hint (no blocking await) |

## Components

### 1. `LogProvider` — `lib/providers/log_provider.dart`
Add one pure, synchronous method (no Firestore calls; reuses the in-memory `_dailyLogs` kept fresh by `startListening()`):

```dart
/// Returns the endKm of the most recent daily log strictly earlier than
/// [date] (compared at day granularity). When multiple logs share that
/// latest earlier date, the one with the largest endKm wins.
/// Returns null when no qualifying log exists.
double? previousEndKmForDate(DateTime date) {
  final dayStart = DateTime(date.year, date.month, date.day);
  final candidates = _dailyLogs.where((l) => l.date.isBefore(dayStart));
  if (candidates.isEmpty) return null;
  DailyLog latest = candidates.first;
  for (final l in candidates) {
    if (l.date.isAfter(latest.date) ||
        (l.date.isAtSameMomentAs(latest.date) && l.endKm > latest.endKm)) {
      latest = l;
    }
  }
  return latest.endKm;
}
```

Notes:
- Comparison is at day granularity via a normalized `dayStart` so that a log whose `date` has a non-midnight time component still compares correctly.
- `isAtSameMomentAs` is only reached between two logs whose `date` field equals `dayStart - epsilon`; in practice daily logs are stored with the chosen day's local midnight (see `_save()` in the form, which passes the date-picker's `DateTime`), so this is a defensive tiebreaker.

### 2. `DailyLogFormScreen` — `lib/screens/daily_log_form_screen.dart`
Modifications:

- Add a state field `double? _autoFilledKm;` — the value that was auto-filled (or null when no previous log was found).
- Move the pre-fill of `_startKmCtrl` from `initState` into `didChangeDependencies`, guarded by a `bool _didPrefill = false;` flag so it only runs once. Using `didChangeDependencies` (rather than `initState`) lets us safely access `Provider.of<LogProvider>(context, listen: false)` for the in-memory list.
- The pre-fill block runs only when `widget.existingLog == null`:
  - Calls `LogProvider.previousEndKmForDate(_selectedDate)`.
  - If a non-null value is returned, sets `_startKmCtrl.text = value.toStringAsFixed(0)` and stores it in `_autoFilledKm`.
  - If null, leaves `_startKmCtrl.text` empty and sets `_autoFilledKm = null`.
- `_buildTextField` for the Start KM field gets:
  - `helperText: _autoFilledKm == null && _startKmCtrl.text.isEmpty ? 'No previous entry — enter the start odometer manually' : null`
  - a `suffixIcon: _showsAutoFillBadge() ? Icon(Icons.auto_fix_high, size: 18, color: AppTheme.primaryLight) : null`
  - where `_showsAutoFillBadge()` returns `_autoFilledKm != null && (_startKmCtrl.text == _autoFilledKm!.toStringAsFixed(0))`.
- The existing `onChanged: (_) => setState(() {})` on the field already triggers re-render, so the badge will vanish as soon as the driver edits the field.
- The existing `_save()`, `_confirmDelete()`, `_pickDate()`, and validation are unchanged.

Because pre-fill happens only once in `didChangeDependencies`, changing the date after the form is open will NOT recompute the start KM — matching the agreed behavior.

### 3. Other screens
- `home_screen.dart` and `daily_logs_screen.dart` already navigate to `const DailyLogFormScreen()` for new entries, so the auto-fill kicks in automatically. No change needed.

## Data Flow
```
[Open DailyLogFormScreen (create mode)]
   └─ didChangeDependencies (once, guarded by _didPrefill)
        ├─ prev = LogProvider.previousEndKmForDate(_selectedDate)
        │     (synchronous; reads in-memory list)
        ├─ prev != null → _startKmCtrl.text = prev.toStringAsFixed(0)
        │                 _autoFilledKm = prev
        │                 suffixIcon = auto_fix_high badge
        └─ prev == null → _startKmCtrl.text = ''
                          _autoFilledKm = null
                          helperText = 'No previous entry — enter the start odometer manually'
[Driver types/deletes/edits as usual]
   └─ onChanged → setState → badge hidden once text != auto-filled value
[_save() unchanged]
   └─ Reads _startKmCtrl.text as today
```

## Testing

### Unit tests — `LogProvider.previousEndKmForDate`
Located in `test/log_provider_test.dart` (new file). Cases:
1. Empty `_dailyLogs` → returns null.
2. One log strictly earlier than `date` → returns its `endKm`.
3. Multiple logs on different earlier dates → returns the endKm of the latest date.
4. Multiple logs on the same latest earlier date with different `endKm` → returns the larger endKm.
5. A log on the same day as `date` (different time) → ignored; returns null if it was the only candidate, or the next-earlier day's endKm otherwise.
6. A log strictly after `date` → ignored.

`LogProvider` is constructed by injecting a fake `FirestoreService` (or by directly populating `_dailyLogs` via a test seam). The method is pure and synchronous, so no Firestore interaction is required. If testing without a Firestore stub proves awkward, add a small `@visibleForTesting` setter on `LogProvider` that assigns `_dailyLogs` directly.

### Widget tests — `DailyLogFormScreen`
Located in `test/daily_log_form_screen_test.dart` (new file). Cases:
1. Create mode, provider has one earlier log → Start KM field shows that log's endKm, badge visible.
2. Create mode, provider has no logs → Start KM field empty, helper text shown, no badge.
3. Create mode, provider has an earlier log, then the tester types over the value → badge disappears.
4. Edit mode (`existingLog` supplied) → Start KM shows the existing log's `startKm`, no auto-fill, no badge regardless of provider state.

Tests wrap the screen in `ChangeNotifierProvider<LogProvider>` with a controlled instance.

## Risks / Trade-offs
- **Stale in-memory list:** if Firestore hasn't synced the previous day's log yet on first open of a brand-new install, the field will be empty + hint rather than blocking. This matches the agreed "no blocking awaits" behavior. The previous entry will be present on subsequent opens once the stream has emitted.
- **No recompute on date change:** agreed. If the driver picks an earlier date after opening, the start KM will not update. Acceptable per brainstorming decision; can be revisited as a follow-up if desired.
- **Tiebreaker on same date:** rarely reached because the form persists `date` at local midnight from the date picker, but is defensively handled by choosing the larger `endKm`.

## Non-functional
- No new dependencies.
- No Firestore schema change.
- No new permissions.
- Performance: O(n) scan over `_dailyLogs` on form open — trivial for a single-driver app.
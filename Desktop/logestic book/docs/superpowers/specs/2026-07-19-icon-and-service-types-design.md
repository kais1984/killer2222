# Custom App Icon + Expanded Service Types — Design

## Overview
Two polish enhancements to the Driver Log Book app:
1. Replace the default Flutter launcher icon with a purpose-fit "car + odometer" design using the app's brand colors.
2. Expand the Service Type dropdown from 5 to 15 maintenance-related categories (adding Petrol Refill, Tyre, Brake, Battery, Filters, Fluids, Wash, Inspection, Insurance/Registration, Accessories). Each type gets its own icon and color, surfaced in the dropdown, the Services list rows, and (where relevant) the home-screen service quick action. The service-icon/color lookup is moved into the `ServiceLog` model so the form, the list, and any future screens share a single source of truth.

## Scope

### In scope
- A custom 1024×1024 source PNG icon at `assets/icon.png`.
- Regeneration of Android launcher icons (`mipmap-*`, plus adaptive `mipmap-anydpi-v26`) and iOS `AppIcon.appiconset` from that source, plus web favicon.
- Editorial pipeline: a Dart tool that draws the icon programmatically, and a `flutter_launcher_icons` invocation that fans it out to all platforms.
- Add 10 new service type entries to `ServiceLog.serviceTypes`, with display names.
- Move the per-type icon lookup (currently a private `_typeIcon` in `services_screen.dart` for the original 5 types) into `ServiceLog.iconFor(type)` as the single source of truth, extended to all 15 types.
- Move the per-type color lookup (currently a private `_typeColor` in `services_screen.dart` for the original 5 types) into `ServiceLog.colorFor(type)` as the single source of truth, extended to all 15 types.
- Show the type's icon inside each dropdown item row in the Service form.
- Replace the private `_typeIcon` / `_typeColor` in `services_screen.dart` with delegation to the new model helpers; the row visual style is unchanged for the 5 existing types, new types get derived colors.

### Out of scope
- Per-type container shape or position theming (rows keep the existing left-bar+badge layout).
- Service-type grouping, filtering, search, or categories.
- Splitting daily fuel cost out of the daily log (daily `cost` field stays; "Petrol Refill" as a Service entry is optional, for drivers who want a refill record at a specific odometer).
- App-store submission, signed builds, screen icons vs launcher icons.

## Part A — App Launcher Icon

### Icon design (1024×1024 source PNG)
- **Background:** rounded rectangle (corner radius ≈ 220 px) filled with a vertical linear gradient from `#1E40AF` (top) to `#3B82F6` (bottom), matching `AppTheme.primary` / `AppTheme.primaryLight` so the icon and in-app header share a visual identity.
- **Car silhouette (white):** centered, body as a rounded rectangle ≈ 540 × 180 px with a trapezoidal cabin on top. Two dark-blue (`#1E293B`) circular wheels of radius ≈ 60 px positioned at the lower front and lower rear of the body.
- **Speedometer badge (top-right):** an amber (`#F59E0B`) arc of ~120° (open at the bottom), a thin white (`#FFFFFF`) needle pinned just below the arc swung to ~"3 o'clock", and a small `#F97316` accent dot at the hub.
- **Inner stroke:** a subtle white ring inside the arc to lift the speedometer off the car body visually.
- **No text** on the icon (cleaner at small sizes; avoids i18n issues).

### Generation pipeline

#### Files added
- `tool/gen_icon.dart` — pure-Dart generator using `package:image` (added as a `dev_dependency`).
- `assets/icon.png` — the 1024×1024 source PNG produced by the script (committed; the script can be re-run to regenerate).
- `flutter_launcher_icons.yaml` at project root — configuration for the fan-out step.

#### `tool/gen_icon.dart` responsibilities
- Create an `Image(1024, 1024)` from `package:image`.
- Fill the rounded-rect background with the blue gradient row-by-row (`fillRect` per scanline with interpolated color).
- Draw simple shapes using `package:image` drawing utilities:
  - `drawCircle` for wheels, the speedometer hub, and the inner white ring.
  - Antialiased line drawing (`drawLine` with `antialias: true`) for the needle.
  - A parametric arc rasterized by drawing short antialiased segments around the gauge center; alternatively use `drawCircle` strokes approximated as filled rings.
  - A helper `fillRoundRect(image, rect, radius, color)` built on scanline fills (clip against corner circles).
- Serialize the `Image` with `PngEncoder` from `package:image` to a `Uint8List` and write to `assets/icon.png` via `dart:io`.
- Print a confirmation line and exit 0.

Run via: `dart run tool/gen_icon.dart` from the project root (no Flutter runtime required).

#### `flutter_launcher_icons.yaml`
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

Run via: `dart run flutter_launcher_icons` (after `flutter pub get`). This regenerates all `android/app/src/main/res/mipmap-*/ic_launcher.png` files, creates `mipmap-anydpi-v26/ic_launcher.xml` and `ic_launcher_round.xml` for adaptive icons if `adaptive_icon_background`/`adaptive_icon_foreground` are provided (we set only background — the foreground defaults to the source image), and refreshes the iOS `AppIcon.appiconset` PNGs and `Contents.json`.

### dev_dependencies added (pubspec.yaml)
- `flutter_launcher_icons:` — latest published major compatible with the Flutter SDK in `pubspec.yaml` (^3.12.2 env). Pinned exactly at implementation time and recorded in `pubspec.lock`.
- `image: ^4.0.0` — already in `dependencies`; reused from there (no duplication needed). If pubspec visibility from dev-only `tool/` scripts is awkward, also list it under `dev_dependencies`.

### Edge cases / notes
- `flutter_launcher_icons` requires `assets/icon.png` to exist at fan-out time. We commit the generated PNG so the build never depends on the tool being re-run; the tool is for editing the source design.
- iOS rejects transparent icons — `remove_alpha_ios: true` flattens our PNG onto `#1E40AF`, which is fine because the design's gradient already covers the full canvas with no alpha.
- Existing Android `AndroidManifest.xml` references `@mipmap/ic_launcher` — `flutter_launcher_icons` writes to that exact path and naming, so no manifest change is required.
- If `mipmap-anydpi-v26` already exists, the tool overwrites it. If absent, the tool creates it; both behaviors are fine.

## Part B — Service Types

### `ServiceLog` (`lib/models/service_log.dart`)

Replace the existing `serviceTypes` list with the expanded set of 15 keys (preserving the original 5 keys):

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
```

Extend `displayName` to cover all new keys, with the existing default branch preserved for forward compatibility:

```dart
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
```

Add two new helpers — `iconFor` and `colorFor` — that consolidate the icon and the brand color for each type. The icon choices for the original 5 types *match what `services_screen.dart` currently uses* so we do not regress existing visual identity in the Services list:

```dart
import 'package:flutter/material.dart' show Icons, IconData, Color;
import 'package:logestic_app/theme/app_theme.dart' show AppTheme;

static IconData iconFor(String type) {
  switch (type) {
    case 'oil_change':             return Icons.oil_barrel;            // existing
    case 'repair':                 return Icons.build;                // existing
    case 'painting':               return Icons.format_paint;         // existing
    case 'part_replacement':       return Icons.settings;             // existing
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
    case 'other':                  return Icons.more_horiz;           // existing
    default:                       return Icons.build;
  }
}

static Color colorFor(String type) {
  switch (type) {
    case 'oil_change':             return AppTheme.primaryLight;            // existing
    case 'repair':                 return AppTheme.error;                   // existing
    case 'painting':               return const Color(0xFF8B5CF6);           // existing purple
    case 'part_replacement':       return AppTheme.secondary;               // existing teal
    case 'petrol_refill':          return const Color(0xFFEF4444);          // red — fuel
    case 'tyre':                   return const Color(0xFF1F2937);          // dark slate — rubber
    case 'brake_service':          return const Color(0xFFDC2626);          // red — safety
    case 'battery':                return const Color(0xFF16A34A);          // green — electrical
    case 'filter_change':          return const Color(0xFF0EA5E9);          // sky blue — air
    case 'fluids_topup':           return const Color(0xFF0891B2);          // cyan — fluids
    case 'wash':                   return const Color(0xFF38BDF8);          // light blue — water
    case 'inspection':             return AppTheme.accent;                  // amber — caution
    case 'insurance_registration': return const Color(0xFF6366F1);          // indigo — paperwork
    case 'accessories':            return const Color(0xFFEC4899);          // pink — extras
    case 'other':                  return AppTheme.accent;                  // existing
    default:                      return AppTheme.mediumText;
  }
}
```

The `import 'package:flutter/material.dart'` at the top of `service_log.dart` is fine; the model already lives inside a Flutter package and `Color`/`IconData` are lightweight Dart types from `dart:ui`/`flutter/widgets`.

### Service form (`lib/screens/service_form_screen.dart`)
- `_buildTypeDropdown` items now show a leading icon per type. Replace the existing `DropdownMenuItem` body with:
  ```dart
  DropdownMenuItem(
    value: type,
    child: Row(
      children: [
        Icon(ServiceLog.iconFor(type), size: 20, color: ServiceLog.colorFor(type)),
        const SizedBox(width: 10),
        Expanded(child: Text(ServiceLog.displayName(type))),
      ],
    ),
  ),
  ```
- Make the dropdown's static `prefixIcon` reactive: set it to `Icon(ServiceLog.iconFor(_selectedType), color: ServiceLog.colorFor(_selectedType))` so it mirrors the currently-selected type. Update it on `onChanged`.
- The default `_selectedType` when creating a new service remains `'oil_change'` so the dropdown always opens on a valid value.

### Services list (`lib/screens/services_screen.dart`)
The file currently defines two private helpers, `_typeIcon(String)` and `_typeColor(String)`, each switching over the original 5 types. After the refactor:
- Delete `_typeIcon` and `_typeColor`.
- Replace the two `final typeColor = _typeColor(svc.serviceType);` and `final typeIcon = _typeIcon(svc.serviceType);` reads with the new model calls:
  ```dart
  final typeColor = ServiceLog.colorFor(svc.serviceType);
  final typeIcon = ServiceLog.iconFor(svc.serviceType);
  ```
- The empty-state icon (`Icons.build_outlined`) and the trailing `chevron_right` are unchanged.
- The "left border" stripe on each row uses `typeColor` (already does today). With the new color set, this means each new service type gets a small but recognizable color identity in the list.

### Data & compat
- Existing Firestore documents with `serviceType` in `{oil_change, repair, painting, part_replacement, other}` are unchanged and continue to render with their existing labels. Because `iconFor` and `colorFor` use the *same* icon/color choices for those 5 types as the private helpers in `services_screen.dart` do today, the row visuals for historical entries are pixel-identical.
- Old entries that carry an unrecognized `serviceType` string still don't crash — the default branches of `displayName`, `iconFor`, and `colorFor` handle the fallback (returns `Icons.build`, `AppTheme.mediumText` respectively).

## Testing

### Unit tests (`test/service_log_test.dart`, new file)
1. `serviceTypes.length == 15` and contains the 5 original keys plus the 10 new keys.
2. For each key in `serviceTypes`, `displayName(key)` returns a non-empty string starting with an uppercase letter.
3. For each key in `serviceTypes`, `iconFor(key)` returns a non-null `IconData` and `colorFor(key)` returns a non-null `Color`.
4. Unknown type string `'foobar'` → `displayName` returns `'foobar'`; `iconFor` returns `Icons.build`; `colorFor` returns `AppTheme.mediumText`.

### Widget test (`test/service_form_screen_test.dart`, new file)
- Pump `ServiceFormScreen` wrapped in `ChangeNotifierProvider<LogProvider>`.
- Open the dropdown; assert that 15 `DropdownMenuItem`s render, each containing a `Row` with an `Icon` and a `Text` whose value matches `ServiceLog.displayName` for that key.

### Manual tests
- Run `dart run tool/gen_icon.dart`, confirm `assets/icon.png` is rewritten and visually matches the spec (rounded blue gradient, white car, amber gauge).
- Run `flutter pub get` then `dart run flutter_launcher_icons`, confirm:
  - All `mipmap-*` PNGs are replaced.
  - `mipmap-anydpi-v26` exists (or is overwritten).
  - iOS `AppIcon.appiconset` `Contents.json` unchanged structurally; PNGs replaced.
- `flutter build apk --debug` and visually inspect the launcher icon on an emulator/device.
- `flutter build ios --debug --no-codesign` and visually inspect on the iOS simulator.

## Risks / Trade-offs
- **Hand-drawn icon:** programmatic generation via `package:image` keeps the design reproducible from source and avoids external tool dependencies on the user's machine (no Photoshop/Inkscape/Figma needed). The trade-off is that the art is procedural — fine for a developer tool, acceptable for a single-driver private app.
- **Icon file commit size:** each PNG in `mipmap-*` and the AppIcon set is small. The 1024×1024 source PNG at `assets/icon.png` is the only meaningful addition (~100 KB). Acceptable.
- **`flutter_launcher_icons` version drift:** pin to a tested version; if a newer major release changes config keys, the YAML may need a small update at that time.
- **15-item dropdown:** long but standard; no usability concerns on mobile. Per-row icons make scanning faster.
- **Per-type colors:** giving each new type its own color makes the Services list more varied. The 5 original types keep their existing colors to avoid visual regression; the 10 new colors are picked to be intuitive (red for fuel, slate for tyres, etc.). All colors are tested against white-brand background containers; the row uses 10 % opacity tints per the existing `_typeColor.withValues(alpha: 0.1)` usage.
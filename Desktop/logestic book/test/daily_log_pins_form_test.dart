import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:logestic_app/models/daily_log.dart';
import 'package:logestic_app/services/place_pin_service.dart';
import 'package:logestic_app/widgets/pinned_places_card.dart';

PlacePin _pin(double lat, double lng, {String id = '', String label = ''}) {
  return PlacePin(
    id: id.isEmpty ? 'p-$lat-$lng' : id,
    lat: lat,
    lng: lng,
    timestamp: DateTime(2026, 7, 20, 8),
    label: label,
  );
}

Widget _wrap(Widget child) {
  return MaterialApp(
    home: Scaffold(
      body: SizedBox(
        width: 400,
        height: 800,
        child: child,
      ),
    ),
  );
}

Future<({double lat, double lng})> _okFetcher() async => (lat: 25.2, lng: 55.3);

void main() {
  testWidgets('empty pins shows empty state with Add button', (tester) async {
    await tester.pumpWidget(_wrap(PinnedPlacesCard(
      pins: const [],
      onChanged: (_) {},
      locationFetcher: _okFetcher,
    )));
    await tester.pump();

    expect(find.text('No pins yet'), findsOneWidget);
    expect(find.text('Add current location'), findsOneWidget);
    expect(find.byType(FlutterMap), findsNothing);
  });

  testWidgets('with pins shows the map, total distance, and pin chips',
      (tester) async {
    final pins = [
      _pin(51.5074, -0.1278, id: 'a', label: 'Pin 1'),
      _pin(48.8566, 2.3522, id: 'b', label: 'Pin 2'),
    ];
    await tester.pumpWidget(_wrap(PinnedPlacesCard(
      pins: pins,
      onChanged: (_) {},
      locationFetcher: _okFetcher,
    )));
    await tester.pump();

    expect(find.byType(FlutterMap), findsOneWidget);
    expect(find.text('Pin 1'), findsOneWidget);
    expect(find.text('Pin 2'), findsOneWidget);
    expect(find.textContaining('Pin-to-pin total:'), findsOneWidget);
  });

  testWidgets(
      'tapping Add current location appends a new pin via onChanged',
      (tester) async {
    List<PlacePin>? captured;
    await tester.pumpWidget(_wrap(PinnedPlacesCard(
      pins: const [],
      onChanged: (p) => captured = p,
      locationFetcher: () async => (lat: 25.2, lng: 55.3),
    )));
    await tester.pump();

    await tester.tap(find.text('Add current location'));
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 100));

    expect(captured, isNotNull);
    expect(captured!.length, 1);
    expect(captured!.first.lat, 25.2);
    expect(captured!.first.lng, 55.3);
    expect(captured!.first.label, 'Pin 1');
  });

  testWidgets('fetcher throws PlacePinLocationDenied does not crash, no pin added',
      (tester) async {
    List<PlacePin>? captured;
    await tester.pumpWidget(_wrap(PinnedPlacesCard(
      pins: const [],
      onChanged: (p) => captured = p,
      locationFetcher: () async => throw PlacePinLocationDenied(),
    )));
    await tester.pump();

    await tester.tap(find.text('Add current location'));
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 100));

    expect(captured, isNull);
    expect(find.text('No pins yet'), findsOneWidget);
  });

  testWidgets('fetcher throws PlacePinLocationFailed shows error and no pin',
      (tester) async {
    List<PlacePin>? captured;
    await tester.pumpWidget(_wrap(PinnedPlacesCard(
      pins: const [],
      onChanged: (p) => captured = p,
      locationFetcher: () async => throw PlacePinLocationFailed('boom'),
    )));
    await tester.pump();

    await tester.tap(find.text('Add current location'));
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 100));

    expect(captured, isNull);
    expect(find.text('boom'), findsOneWidget);
  });

  testWidgets('total distance matches sumConsecutiveDistances for 3 known pins',
      (tester) async {
    final pins = [
      _pin(51.5074, -0.1278),
      _pin(48.8566, 2.3522),
      _pin(41.9028, 12.4964),
    ];

    await tester.pumpWidget(_wrap(PinnedPlacesCard(
      pins: pins,
      onChanged: (_) {},
      locationFetcher: _okFetcher,
    )));
    await tester.pump();

    // London→Paris ≈ 343.5km + Paris→Rome ≈ 1105km ≈ 1448.8km. Display 1dp.
    expect(find.textContaining('Pin-to-pin total: 144'), findsOneWidget);
  });

  testWidgets('removing a pin calls onChanged with the remaining pins',
      (tester) async {
    final pins = [
      _pin(25.2, 55.3, id: 'a', label: 'Pin 1'),
      _pin(25.3, 55.4, id: 'b', label: 'Pin 2'),
    ];
    List<PlacePin>? captured;
    await tester.pumpWidget(_wrap(PinnedPlacesCard(
      pins: pins,
      onChanged: (p) => captured = p,
      locationFetcher: _okFetcher,
    )));
    await tester.pump();

    final closeIcons = find.byIcon(Icons.close);
    expect(closeIcons.evaluate().length, greaterThanOrEqualTo(2));
    await tester.tap(closeIcons.first);
    await tester.pump();

    expect(captured, isNotNull);
    expect(captured!.length, 1);
    expect(captured!.first.id, 'b');
  });
}

import 'package:flutter_test/flutter_test.dart';
import 'package:logestic_app/utils/geo.dart';

void main() {
  group('haversineMeters', () {
    test('zero distance for identical points', () {
      expect(haversineMeters(0, 0, 0, 0), 0.0);
    });

    test('London to Paris is approximately 343.5 km', () {
      final distance = haversineMeters(51.5074, -0.1278, 48.8566, 2.3522);
      expect(distance, closeTo(343500, 1000));
    });
  });

  group('sumConsecutiveDistances', () {
    test('empty list returns 0', () {
      expect(sumConsecutiveDistances(const []), 0.0);
    });

    test('single point returns 0', () {
      expect(
        sumConsecutiveDistances([
          (lat: 25.2, lng: 55.3),
        ]),
        0.0,
      );
    });

    test('two points equals haversine of the pair', () {
      const a = (lat: 51.5074, lng: -0.1278);
      const b = (lat: 48.8566, lng: 2.3522);
      expect(sumConsecutiveDistances([a, b]), haversineMeters(a.lat, a.lng, b.lat, b.lng));
    });

    test('three points equals sum of two haversine pairs', () {
      const a = (lat: 51.5074, lng: -0.1278);
      const b = (lat: 48.8566, lng: 2.3522);
      const c = (lat: 41.9028, lng: 12.4964);
      final expected = haversineMeters(a.lat, a.lng, b.lat, b.lng) +
          haversineMeters(b.lat, b.lng, c.lat, c.lng);
      expect(sumConsecutiveDistances([a, b, c]), expected);
    });
  });
}

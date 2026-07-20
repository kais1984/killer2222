import 'package:flutter_test/flutter_test.dart';
import 'package:logestic_app/utils/geo.dart';

void main() {
  group('haversineMeters', () {
    test('zero distance for same point', () {
      expect(haversineMeters(0, 0, 0, 0), 0.0);
    });

    test('London to Paris ~ 343 km', () {
      final d = haversineMeters(51.5074, -0.1278, 48.8566, 2.3522);
      expect(d, closeTo(343500, 1000));
    });

    test('symmetric', () {
      final a = haversineMeters(40.7128, -74.0060, 34.0522, -118.2437);
      final b = haversineMeters(34.0522, -118.2437, 40.7128, -74.0060);
      expect(a, closeTo(b, 0.001));
    });
  });

  group('sumConsecutiveDistances', () {
    test('empty list returns 0', () {
      expect(sumConsecutiveDistances([]), 0.0);
    });

    test('single point returns 0', () {
      expect(sumConsecutiveDistances([(lat: 1.0, lng: 2.0)]), 0.0);
    });

    test('two points equals single haversine', () {
      final pts = [(lat: 51.5074, lng: -0.1278), (lat: 48.8566, lng: 2.3522)];
      expect(sumConsecutiveDistances(pts),
          closeTo(haversineMeters(pts[0].lat, pts[0].lng, pts[1].lat, pts[1].lng), 0.001));
    });

    test('three points is sum of two pairs', () {
      final a = (lat: 0.0, lng: 0.0);
      final b = (lat: 0.0, lng: 1.0);
      final c = (lat: 1.0, lng: 1.0);
      final total = sumConsecutiveDistances([a, b, c]);
      final expected =
          haversineMeters(a.lat, a.lng, b.lat, b.lng) + haversineMeters(b.lat, b.lng, c.lat, c.lng);
      expect(total, closeTo(expected, 0.001));
    });
  });
}

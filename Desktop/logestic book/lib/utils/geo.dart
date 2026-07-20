import 'dart:math' as math;

const double _earthRadiusMeters = 6371000.0;

double haversineMeters(double lat1, double lng1, double lat2, double lng2) {
  final dLat = _toRadians(lat2 - lat1);
  final dLng = _toRadians(lng2 - lng1);
  final a = math.sin(dLat / 2) * math.sin(dLat / 2) +
      math.cos(_toRadians(lat1)) *
          math.cos(_toRadians(lat2)) *
          math.sin(dLng / 2) *
          math.sin(dLng / 2);
  final c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a));
  return _earthRadiusMeters * c;
}

double sumConsecutiveDistances(
  List<({double lat, double lng})> points,
) {
  if (points.length < 2) return 0.0;
  var total = 0.0;
  for (var i = 1; i < points.length; i++) {
    final prev = points[i - 1];
    final curr = points[i];
    total += haversineMeters(prev.lat, prev.lng, curr.lat, curr.lng);
  }
  return total;
}

double _toRadians(double degrees) => degrees * math.pi / 180.0;

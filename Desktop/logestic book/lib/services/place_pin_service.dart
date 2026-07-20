import 'package:geolocator/geolocator.dart';

class PlacePinLocationDenied implements Exception {
  final String message;
  PlacePinLocationDenied([this.message = 'Location permission denied']);
  @override
  String toString() => message;
}

class PlacePinLocationFailed implements Exception {
  final String message;
  PlacePinLocationFailed(this.message);
  @override
  String toString() => message;
}

class PlacePinService {
  Future<({double lat, double lng})> getCurrentLocation() async {
    final serviceEnabled = await Geolocator.isLocationServiceEnabled();
    if (!serviceEnabled) {
      throw PlacePinLocationFailed('Location services are off');
    }
    var perm = await Geolocator.checkPermission();
    if (perm == LocationPermission.denied) {
      perm = await Geolocator.requestPermission();
    }
    if (perm == LocationPermission.denied ||
        perm == LocationPermission.deniedForever) {
      throw PlacePinLocationDenied();
    }
    try {
      final pos = await Geolocator.getCurrentPosition(
        locationSettings: const LocationSettings(
          accuracy: LocationAccuracy.high,
        ),
      );
      return (lat: pos.latitude, lng: pos.longitude);
    } catch (e) {
      throw PlacePinLocationFailed(e.toString());
    }
  }
}

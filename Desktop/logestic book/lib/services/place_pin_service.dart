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

typedef PlacePinLocation = ({double lat, double lng});

class PlacePinService {
  Future<PlacePinLocation> getCurrentLocation() async {
    final serviceEnabled = await Geolocator.isLocationServiceEnabled();
    if (!serviceEnabled) {
      throw PlacePinLocationFailed('Location services are off');
    }

    var permission = await Geolocator.checkPermission();
    if (permission == LocationPermission.denied) {
      permission = await Geolocator.requestPermission();
    }
    if (permission == LocationPermission.denied ||
        permission == LocationPermission.deniedForever) {
      throw PlacePinLocationDenied();
    }

    try {
      final position = await Geolocator.getCurrentPosition(
        locationSettings: const LocationSettings(
          accuracy: LocationAccuracy.high,
        ),
      );
      return (lat: position.latitude, lng: position.longitude);
    } catch (e) {
      throw PlacePinLocationFailed(e.toString());
    }
  }
}

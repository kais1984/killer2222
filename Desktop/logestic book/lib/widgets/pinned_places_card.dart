import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';
import 'package:logestic_app/models/daily_log.dart';
import 'package:logestic_app/services/place_pin_service.dart';
import 'package:logestic_app/theme/app_theme.dart';
import 'package:logestic_app/utils/geo.dart';

typedef PlacePinFetcher = Future<({double lat, double lng})> Function();

class PinnedPlacesCard extends StatefulWidget {
  final List<PlacePin> pins;
  final ValueChanged<List<PlacePin>> onChanged;
  final PlacePinFetcher locationFetcher;

  const PinnedPlacesCard({
    super.key,
    required this.pins,
    required this.onChanged,
    PlacePinFetcher? locationFetcher,
  }) : locationFetcher = locationFetcher ?? _defaultFetcher;

  static Future<({double lat, double lng})> _defaultFetcher() {
    return PlacePinService().getCurrentLocation();
  }

  @override
  State<PinnedPlacesCard> createState() => _PinnedPlacesCardState();
}

class _PinnedPlacesCardState extends State<PinnedPlacesCard> {
  final GlobalKey _mapKey = GlobalKey();
  bool _isFetching = false;

  double get _totalMeters => sumConsecutiveDistances(
        widget.pins
            .map((p) => (lat: p.lat, lng: p.lng))
            .toList(growable: false),
      );

  Future<void> _addCurrentLocation() async {
    if (_isFetching) return;
    setState(() => _isFetching = true);
    try {
      final loc = await widget.locationFetcher();
      final newPin = PlacePin(
        id: DateTime.now().microsecondsSinceEpoch.toString(),
        lat: loc.lat,
        lng: loc.lng,
        timestamp: DateTime.now(),
        label: 'Pin ${widget.pins.length + 1}',
      );
      widget.onChanged([...widget.pins, newPin]);
    } on PlacePinLocationDenied {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Location permission denied. Enable it in Settings.'),
        ),
      );
    } on PlacePinLocationFailed catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(e.message)),
      );
    } finally {
      if (mounted) {
        setState(() => _isFetching = false);
      }
    }
  }

  void _removePin(int index) {
    final next = [...widget.pins]..removeAt(index);
    widget.onChanged(next);
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: const Color(0xFFE2E8F0)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: AppTheme.primaryLight.withValues(alpha: 0.1),
                  borderRadius: BorderRadius.circular(10),
                ),
                child: const Icon(Icons.location_on,
                    color: AppTheme.primaryLight, size: 20),
              ),
              const SizedBox(width: 12),
              const Text(
                'Pinned Places',
                style: TextStyle(
                  fontSize: 15,
                  fontWeight: FontWeight.w700,
                  color: AppTheme.darkText,
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          if (widget.pins.isEmpty)
            _buildEmptyState()
          else
            _buildPinsView(),
          const SizedBox(height: 12),
          _buildAddButton(),
        ],
      ),
    );
  }

  Widget _buildEmptyState() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(vertical: 20, horizontal: 12),
      decoration: BoxDecoration(
        color: AppTheme.background,
        borderRadius: BorderRadius.circular(12),
      ),
      child: const Center(
        child: Text(
          'No pins yet',
          style: TextStyle(color: AppTheme.mediumText, fontSize: 14),
        ),
      ),
    );
  }

  Widget _buildPinsView() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        LayoutBuilder(
          builder: (context, constraints) {
            final mapWidth = constraints.maxWidth.isFinite
                ? constraints.maxWidth
                : 400.0;
            return SizedBox(
              key: _mapKey,
              width: mapWidth,
              height: 200,
              child: ClipRRect(
                borderRadius: BorderRadius.circular(12),
                child: FlutterMap(
                  options: MapOptions(
                    initialCenter: _mapCenter(),
                    initialZoom: 12,
                    interactionOptions: const InteractionOptions(
                      flags: InteractiveFlag.pinchZoom |
                          InteractiveFlag.drag |
                          InteractiveFlag.doubleTapZoom,
                    ),
                  ),
                  children: [
                    TileLayer(
                      urlTemplate:
                          'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
                      userAgentPackageName: 'com.example.logestic_app',
                      maxNativeZoom: 19,
                    ),
                    PolylineLayer(
                      polylines: [
                        Polyline(
                          points: widget.pins
                              .map((p) => LatLng(p.lat, p.lng))
                              .toList(growable: false),
                          strokeWidth: 3,
                          color: AppTheme.primary,
                        ),
                      ],
                    ),
                    MarkerLayer(
                      markers: [
                        for (var i = 0; i < widget.pins.length; i++)
                          Marker(
                            point: LatLng(
                              widget.pins[i].lat,
                              widget.pins[i].lng,
                            ),
                            width: 36,
                            height: 36,
                            child: _NumberedPin(label: '${i + 1}'),
                          ),
                      ],
                    ),
                  ],
                ),
              ),
            );
          },
        ),
        const SizedBox(height: 10),
        Container(
          width: double.infinity,
          padding: const EdgeInsets.symmetric(vertical: 8, horizontal: 12),
          decoration: BoxDecoration(
            gradient: const LinearGradient(colors: AppTheme.primaryGradient),
            borderRadius: BorderRadius.circular(10),
          ),
          child: Text(
            'Pin-to-pin total: ${(_totalMeters / 1000).toStringAsFixed(1)} km',
            textAlign: TextAlign.center,
            style: const TextStyle(
              color: Colors.white,
              fontSize: 14,
              fontWeight: FontWeight.w700,
            ),
          ),
        ),
        const SizedBox(height: 10),
        Wrap(
          spacing: 8,
          runSpacing: 8,
          children: [
            for (var i = 0; i < widget.pins.length; i++)
              _PinChip(
                pin: widget.pins[i],
                index: i,
                onRemove: () => _removePin(i),
              ),
          ],
        ),
      ],
    );
  }

  LatLng _mapCenter() {
    if (widget.pins.isEmpty) {
      return const LatLng(0, 0);
    }
    final lats = widget.pins.map((p) => p.lat).toList();
    final lngs = widget.pins.map((p) => p.lng).toList();
    final avgLat = lats.reduce((a, b) => a + b) / lats.length;
    final avgLng = lngs.reduce((a, b) => a + b) / lngs.length;
    return LatLng(avgLat, avgLng);
  }

  Widget _buildAddButton() {
    return SizedBox(
      height: 44,
      child: OutlinedButton.icon(
        onPressed: _isFetching ? null : _addCurrentLocation,
        icon: _isFetching
            ? const SizedBox(
                width: 16,
                height: 16,
                child: CircularProgressIndicator(strokeWidth: 2),
              )
            : const Icon(Icons.my_location, size: 18),
        label: Text(_isFetching ? 'Fetching…' : 'Add current location'),
        style: OutlinedButton.styleFrom(
          foregroundColor: AppTheme.primary,
          side: const BorderSide(color: AppTheme.primaryLight, width: 1.5),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
        ),
      ),
    );
  }
}

class _NumberedPin extends StatelessWidget {
  final String label;
  const _NumberedPin({required this.label});
  @override
  Widget build(BuildContext context) {
    return DecoratedBox(
      decoration: BoxDecoration(
        color: AppTheme.primary,
        shape: BoxShape.circle,
        border: Border.all(color: Colors.white, width: 2),
        boxShadow: const [
          BoxShadow(color: Color(0x33000000), blurRadius: 3, offset: Offset(0, 1)),
        ],
      ),
      child: Center(
        child: Text(
          label,
          style: const TextStyle(
            color: Colors.white,
            fontSize: 13,
            fontWeight: FontWeight.w800,
          ),
        ),
      ),
    );
  }
}

class _PinChip extends StatelessWidget {
  final PlacePin pin;
  final int index;
  final VoidCallback onRemove;
  const _PinChip({
    required this.pin,
    required this.index,
    required this.onRemove,
  });
  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.fromLTRB(10, 6, 6, 6),
      decoration: BoxDecoration(
        color: AppTheme.primaryLight.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(
          color: AppTheme.primaryLight.withValues(alpha: 0.4),
          width: 1,
        ),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Text(
            pin.label.isEmpty ? 'Pin ${index + 1}' : pin.label,
            style: const TextStyle(
              color: AppTheme.primary,
              fontSize: 12,
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(width: 4),
          InkWell(
            onTap: onRemove,
            customBorder: const CircleBorder(),
            child: const Padding(
              padding: EdgeInsets.all(4),
              child: Icon(Icons.close, size: 14, color: AppTheme.primary),
            ),
          ),
        ],
      ),
    );
  }
}

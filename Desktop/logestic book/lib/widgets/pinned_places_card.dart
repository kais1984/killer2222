import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';
import 'package:logestic_app/models/daily_log.dart';
import 'package:logestic_app/services/place_pin_service.dart';
import 'package:logestic_app/theme/app_theme.dart';
import 'package:logestic_app/utils/geo.dart';

typedef LocationFetcher = Future<({double lat, double lng})> Function();

class PinnedPlacesCard extends StatefulWidget {
  final List<PlacePin> pins;
  final ValueChanged<List<PlacePin>> onChanged;
  final LocationFetcher? locationFetcher;

  const PinnedPlacesCard({
    super.key,
    required this.pins,
    required this.onChanged,
    this.locationFetcher,
  });

  @override
  State<PinnedPlacesCard> createState() => _PinnedPlacesCardState();
}

class _PinnedPlacesCardState extends State<PinnedPlacesCard> {
  bool _fetching = false;

  Future<void> _addCurrent() async {
    if (_fetching) return;
    setState(() => _fetching = true);
    try {
      final fetcher = widget.locationFetcher ?? PlacePinService().getCurrentLocation;
      final loc = await fetcher();
      final pin = PlacePin(
        id: 'pin_${DateTime.now().microsecondsSinceEpoch}',
        lat: loc.lat,
        lng: loc.lng,
        timestamp: DateTime.now(),
        label: 'Pin ${widget.pins.length + 1}',
      );
      widget.onChanged([...widget.pins, pin]);
    } on PlacePinLocationDenied catch (e) {
      _showSnack(e.message);
    } on PlacePinLocationFailed catch (e) {
      _showSnack(e.message);
    } finally {
      if (mounted) setState(() => _fetching = false);
    }
  }

  void _removePin(String id) {
    widget.onChanged(widget.pins.where((p) => p.id != id).toList());
  }

  void _showSnack(String message) {
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(message)),
    );
  }

  @override
  Widget build(BuildContext context) {
    final hasPins = widget.pins.isNotEmpty;
    final totalMeters = sumConsecutiveDistances(
      widget.pins.map((p) => (lat: p.lat, lng: p.lng)).toList(),
    );
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: const Color(0xFFE2E8F0)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
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
              const SizedBox(width: 14),
              const Text('Pinned Places',
                  style: TextStyle(
                      color: AppTheme.darkText,
                      fontSize: 15,
                      fontWeight: FontWeight.w600)),
            ],
          ),
          const SizedBox(height: 12),
          if (!hasPins)
            const Padding(
              padding: EdgeInsets.symmetric(vertical: 12),
              child: Text('No pins yet',
                  style: TextStyle(color: AppTheme.mediumText, fontSize: 13)),
            )
          else
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                SizedBox(
                  height: 180,
                  child: ClipRRect(
                    borderRadius: BorderRadius.circular(12),
                    child: FlutterMap(
                      options: MapOptions(
                        initialCenter: LatLng(
                          widget.pins.first.lat,
                          widget.pins.first.lng,
                        ),
                        initialZoom: 14,
                      ),
                      children: [
                        TileLayer(
                          urlTemplate:
                              'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
                          userAgentPackageName: 'com.riman.driverjournal',
                        ),
                        PolylineLayer(
                          polylines: [
                            Polyline(
                              points: widget.pins
                                  .map((p) => LatLng(p.lat, p.lng))
                                  .toList(),
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
                                width: 32,
                                height: 32,
                                child: Container(
                                  decoration: BoxDecoration(
                                    color: AppTheme.primary,
                                    shape: BoxShape.circle,
                                    border: Border.all(
                                        color: Colors.white, width: 2),
                                  ),
                                  alignment: Alignment.center,
                                  child: Text(
                                    '${i + 1}',
                                    style: const TextStyle(
                                      color: Colors.white,
                                      fontSize: 12,
                                      fontWeight: FontWeight.w800,
                                    ),
                                  ),
                                ),
                              ),
                          ],
                        ),
                      ],
                    ),
                  ),
                ),
                const SizedBox(height: 10),
                Text(
                  'Pin-to-pin total: ${(totalMeters / 1000).toStringAsFixed(1)} km',
                  style: const TextStyle(
                      color: AppTheme.darkText,
                      fontSize: 13,
                      fontWeight: FontWeight.w600),
                ),
                const SizedBox(height: 10),
                Wrap(
                  spacing: 8,
                  runSpacing: 8,
                  children: [
                    for (final p in widget.pins)
                      InputChip(
                        label: Text(p.label),
                        onDeleted: () => _removePin(p.id),
                      ),
                  ],
                ),
              ],
            ),
          const SizedBox(height: 12),
          SizedBox(
            height: 48,
            child: ElevatedButton.icon(
              onPressed: _fetching ? null : _addCurrent,
              icon: _fetching
                  ? const SizedBox(
                      width: 18,
                      height: 18,
                      child: CircularProgressIndicator(
                          strokeWidth: 2, color: Colors.white),
                    )
                  : const Icon(Icons.add_location_alt, size: 18),
              label: Text(_fetching ? 'Getting location…' : 'Add current location'),
              style: ElevatedButton.styleFrom(
                backgroundColor: AppTheme.primaryLight,
                foregroundColor: Colors.white,
              ),
            ),
          ),
        ],
      ),
    );
  }
}

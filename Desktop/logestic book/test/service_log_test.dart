import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:logestic_app/models/service_log.dart';
import 'package:logestic_app/theme/app_theme.dart';

void main() {
  test('serviceTypes contains 15 entries', () {
    expect(ServiceLog.serviceTypes.length, 15);
  });

  test('original 5 keys are preserved', () {
    const original = [
      'oil_change', 'repair', 'painting', 'part_replacement', 'other',
    ];
    for (final k in original) {
      expect(ServiceLog.serviceTypes, contains(k));
    }
  });

  test('new 10 keys are present', () {
    const added = [
      'petrol_refill', 'tyre', 'brake_service', 'battery', 'filter_change',
      'fluids_topup', 'wash', 'inspection', 'insurance_registration',
      'accessories',
    ];
    for (final k in added) {
      expect(ServiceLog.serviceTypes, contains(k));
    }
  });

  test('displayName returns a non-empty label for every known key', () {
    for (final k in ServiceLog.serviceTypes) {
      final label = ServiceLog.displayName(k);
      expect(label, isNotEmpty);
      expect(label[0], matches(RegExp(r'[A-Z]')));
    }
  });

  test('iconFor returns a non-null IconData for every known key', () {
    for (final k in ServiceLog.serviceTypes) {
      expect(ServiceLog.iconFor(k), isNotNull);
    }
  });

  test('colorFor returns a non-null Color for every known key', () {
    for (final k in ServiceLog.serviceTypes) {
      expect(ServiceLog.colorFor(k), isA<Color>());
    }
  });

  test('unknown type falls back gracefully', () {
    expect(ServiceLog.displayName('foobar'), 'foobar');
    expect(ServiceLog.iconFor('foobar'), Icons.build);
    expect(ServiceLog.colorFor('foobar'), AppTheme.mediumText);
  });

  test('oil_change keeps existing icon/color (regression)', () {
    expect(ServiceLog.iconFor('oil_change'), Icons.oil_barrel);
    expect(ServiceLog.colorFor('oil_change'), AppTheme.primaryLight);
  });

  test('repair keeps existing icon/color', () {
    expect(ServiceLog.iconFor('repair'), Icons.build);
    expect(ServiceLog.colorFor('repair'), AppTheme.error);
  });

  test('painting keeps existing icon/color', () {
    expect(ServiceLog.iconFor('painting'), Icons.format_paint);
    expect(ServiceLog.colorFor('painting'), const Color(0xFF8B5CF6));
  });

  test('part_replacement keeps existing icon/color', () {
    expect(ServiceLog.iconFor('part_replacement'), Icons.settings);
    expect(ServiceLog.colorFor('part_replacement'), AppTheme.secondary);
  });

  test('other keeps existing icon/color', () {
    expect(ServiceLog.iconFor('other'), Icons.more_horiz);
    expect(ServiceLog.colorFor('other'), AppTheme.accent);
  });
}
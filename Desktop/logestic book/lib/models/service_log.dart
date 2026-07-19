import 'package:flutter/material.dart' show Color, IconData, Icons;
import 'package:logestic_app/theme/app_theme.dart' show AppTheme;

class ServiceLog {
  final String id;
  final DateTime date;
  final double kmReading;
  final String serviceType;
  final double cost;
  final String notes;

  ServiceLog({
    required this.id,
    required this.date,
    required this.kmReading,
    required this.serviceType,
    required this.cost,
    this.notes = '',
  });

  factory ServiceLog.fromMap(Map<String, dynamic> map) {
    return ServiceLog(
      id: map['id'] as String? ?? '',
      date: DateTime.fromMillisecondsSinceEpoch(map['date'] as int),
      kmReading: (map['kmReading'] as num).toDouble(),
      serviceType: map['serviceType'] as String? ?? '',
      cost: (map['cost'] as num).toDouble(),
      notes: map['notes'] as String? ?? '',
    );
  }

  Map<String, dynamic> toMap() {
    return {
      'id': id,
      'date': date.millisecondsSinceEpoch,
      'kmReading': kmReading,
      'serviceType': serviceType,
      'cost': cost,
      'notes': notes,
    };
  }

  ServiceLog copyWith({
    String? id,
    DateTime? date,
    double? kmReading,
    String? serviceType,
    double? cost,
    String? notes,
  }) {
    return ServiceLog(
      id: id ?? this.id,
      date: date ?? this.date,
      kmReading: kmReading ?? this.kmReading,
      serviceType: serviceType ?? this.serviceType,
      cost: cost ?? this.cost,
      notes: notes ?? this.notes,
    );
  }

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

  static IconData iconFor(String type) {
    switch (type) {
      case 'oil_change':             return Icons.oil_barrel;
      case 'repair':                 return Icons.build;
      case 'painting':               return Icons.format_paint;
      case 'part_replacement':       return Icons.settings;
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
      case 'other':                  return Icons.more_horiz;
      default:                       return Icons.build;
    }
  }

  static Color colorFor(String type) {
    switch (type) {
      case 'oil_change':             return AppTheme.primaryLight;
      case 'repair':                 return AppTheme.error;
      case 'painting':               return const Color(0xFF8B5CF6);
      case 'part_replacement':       return AppTheme.secondary;
      case 'petrol_refill':          return const Color(0xFFEF4444);
      case 'tyre':                   return const Color(0xFF1F2937);
      case 'brake_service':          return const Color(0xFFDC2626);
      case 'battery':                return const Color(0xFF16A34A);
      case 'filter_change':          return const Color(0xFF0EA5E9);
      case 'fluids_topup':           return const Color(0xFF0891B2);
      case 'wash':                   return const Color(0xFF38BDF8);
      case 'inspection':             return AppTheme.accent;
      case 'insurance_registration': return const Color(0xFF6366F1);
      case 'accessories':            return const Color(0xFFEC4899);
      case 'other':                  return AppTheme.accent;
      default:                      return AppTheme.mediumText;
    }
  }
}

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:logestic_app/providers/log_provider.dart';
import 'package:logestic_app/screens/daily_logs_screen.dart';
import 'package:logestic_app/screens/daily_log_form_screen.dart';
import 'package:logestic_app/screens/services_screen.dart';
import 'package:logestic_app/screens/service_form_screen.dart';
import 'package:logestic_app/screens/monthly_report_screen.dart';
import 'package:logestic_app/theme/app_theme.dart';
import 'package:intl/intl.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Consumer<LogProvider>(
        builder: (context, provider, _) {
          final todayLog = provider.getTodayLog();
          final now = DateTime.now();
          final dateStr = DateFormat('EEE  ·  MMM d').format(now).toUpperCase();
          final timeStr = DateFormat('HH:mm').format(now);

          return Stack(
            children: [
              // Subtle radial glow behind the hero, like dashboard backlight.
              const Positioned(
                top: -120,
                left: -80,
                right: -80,
                child: _Glow(),
              ),
              SafeArea(
                child: ListView(
                  padding: const EdgeInsets.fromLTRB(16, 16, 16, 24),
                  children: [
                    _TopBar(timeStr: timeStr, dateStr: dateStr, hasLog: todayLog != null),
                    const SizedBox(height: 24),
                    if (todayLog != null) ...[
                      _OdometerCluster(log: todayLog),
                      const SizedBox(height: 24),
                    ] else
                      _NoEntryCluster(onNew: () {
                        Navigator.push(context,
                            MaterialPageRoute(builder: (_) => const DailyLogFormScreen()));
                      }),
                    const SizedBox(height: 24),
                    _QuickActionsRow(),
                    const SizedBox(height: 24),
                    _ViewRecordsSection(),
                  ],
                ),
              ),
            ],
          );
        },
      ),
    );
  }
}

class _Glow extends StatelessWidget {
  const _Glow();
  @override
  Widget build(BuildContext context) {
    return IgnorePointer(
      child: Container(
        height: 380,
        decoration: BoxDecoration(
          shape: BoxShape.circle,
          gradient: RadialGradient(
            colors: [
              AppTheme.primaryLight.withValues(alpha: 0.18),
              AppTheme.primaryLight.withValues(alpha: 0.0),
            ],
          ),
        ),
      ),
    );
  }
}

class _TopBar extends StatelessWidget {
  final String timeStr;
  final String dateStr;
  final bool hasLog;
  const _TopBar({required this.timeStr, required this.dateStr, required this.hasLog});

  @override
  Widget build(BuildContext context) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.end,
      children: [
        Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(timeStr, style: AppTheme.hugeNumber),
            const SizedBox(height: 2),
            Text(dateStr, style: AppTheme.sectionLabel),
          ],
        ),
        const Spacer(),
        _StatusLight(armed: hasLog),
      ],
    );
  }
}

class _StatusLight extends StatelessWidget {
  final bool armed;
  const _StatusLight({required this.armed});
  @override
  Widget build(BuildContext context) {
    final color = armed ? AppTheme.accentBright : AppTheme.tickDim;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.end,
      children: [
        Container(
          width: 12,
          height: 12,
          decoration: BoxDecoration(
            shape: BoxShape.circle,
            color: color,
            boxShadow: armed
                ? [BoxShadow(color: color.withValues(alpha: 0.6), blurRadius: 12)]
                : null,
          ),
        ),
        const SizedBox(height: 6),
        Text(armed ? 'TRIP LOGGED' : 'NO ENTRY',
            style: AppTheme.sectionLabel.copyWith(
              color: armed ? AppTheme.accentBright : AppTheme.displayDim,
            )),
      ],
    );
  }
}

class _OdometerCluster extends StatelessWidget {
  final dynamic log;
  const _OdometerCluster({required this.log});

  @override
  Widget build(BuildContext context) {
    final start = log.startKm.toStringAsFixed(0);
    final end = log.endKm.toStringAsFixed(0);
    final total = log.totalKm.toStringAsFixed(0);
    final cost = log.cost.toStringAsFixed(0);

    return _Bezel(
      label: 'TODAY · ODOMETER',
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          const SizedBox(height: 8),
          // Odometer triple: START | TOTAL | END, like a real cluster.
          Row(
            children: [
              Expanded(
                child: _OdoReadout(
                  label: 'START',
                  value: start,
                  color: AppTheme.displayDim,
                ),
              ),
              Expanded(
                child: _OdoReadout(
                  label: 'TOTAL',
                  value: total,
                  color: AppTheme.accentBright,
                  big: true,
                ),
              ),
              Expanded(
                child: _OdoReadout(
                  label: 'END',
                  value: end,
                  color: AppTheme.displayBright,
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          // Cost bar.
          Row(
            children: [
              Text('FUEL · COST', style: AppTheme.sectionLabel),
              const Spacer(),
              Text('$cost AED', style: AppTheme.bigNumber.copyWith(color: AppTheme.accentBright)),
            ],
          ),
          const SizedBox(height: 12),
        ],
      ),
    );
  }
}

class _OdoReadout extends StatelessWidget {
  final String label;
  final String value;
  final Color color;
  final bool big;
  const _OdoReadout({required this.label, required this.value, required this.color, this.big = false});

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Text(label, style: AppTheme.sectionLabel),
        const SizedBox(height: 4),
        Text(
          value,
          style: big ? AppTheme.hugeNumber.copyWith(color: color) : AppTheme.bigNumber.copyWith(color: color),
        ),
      ],
    );
  }
}

class _NoEntryCluster extends StatelessWidget {
  final VoidCallback onNew;
  const _NoEntryCluster({required this.onNew});
  @override
  Widget build(BuildContext context) {
    return _Bezel(
      label: 'TODAY · NO ENTRY',
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          const SizedBox(height: 4),
          Text('READY TO LOG', style: AppTheme.sectionLabel),
          const SizedBox(height: 8),
          Text('000000', style: AppTheme.hugeNumber.copyWith(color: AppTheme.tickDim)),
          const SizedBox(height: 12),
          Text(
            'Tap to record today\'s Start KM, End KM, and Cost.',
            style: AppTheme.bodyText.copyWith(color: AppTheme.displayDim),
          ),
          const SizedBox(height: 16),
          ElevatedButton(
            onPressed: onNew,
            style: ElevatedButton.styleFrom(
              backgroundColor: AppTheme.accent,
              foregroundColor: const Color(0xFF1A0F00),
            ),
            child: Text('START TRIP LOG', style: AppTheme.bigLabel.copyWith(color: const Color(0xFF1A0F00))),
          ),
        ],
      ),
    );
  }
}

class _QuickActionsRow extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Expanded(child: _ActionTile(
          label: 'DAILY ENTRY',
          sub: 'New trip log',
          icon: Icons.add_road,
          accent: AppTheme.primaryLight,
          onTap: () => Navigator.push(context,
              MaterialPageRoute(builder: (_) => const DailyLogFormScreen())),
        )),
        const SizedBox(width: 10),
        Expanded(child: _ActionTile(
          label: 'SERVICE',
          sub: 'Log a service',
          icon: Icons.build_outlined,
          accent: AppTheme.secondary,
          onTap: () => Navigator.push(context,
              MaterialPageRoute(builder: (_) => const ServiceFormScreen())),
        )),
      ],
    );
  }
}

class _ActionTile extends StatelessWidget {
  final String label;
  final String sub;
  final IconData icon;
  final Color accent;
  final VoidCallback onTap;
  const _ActionTile({required this.label, required this.sub, required this.icon, required this.accent, required this.onTap});
  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(6),
      child: Container(
        padding: const EdgeInsets.all(14),
        decoration: BoxDecoration(
          color: AppTheme.bezel,
          borderRadius: BorderRadius.circular(6),
          border: Border.all(color: AppTheme.bezelEdge),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Icon(icon, color: accent, size: 22),
            const SizedBox(height: 14),
            Text(label, style: AppTheme.bigLabel),
            const SizedBox(height: 2),
            Text(sub, style: AppTheme.caption),
          ],
        ),
      ),
    );
  }
}

class _ViewRecordsSection extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('RECORDS', style: AppTheme.sectionLabel),
        const SizedBox(height: 10),
        _ViewRow(
          label: 'All Daily Logs',
          sub: 'Trip entries',
          icon: Icons.list_alt,
          onTap: () => Navigator.push(context,
              MaterialPageRoute(builder: (_) => const DailyLogsScreen())),
        ),
        const SizedBox(height: 6),
        _ViewRow(
          label: 'All Services',
          sub: 'Service history',
          icon: Icons.build_circle,
          onTap: () => Navigator.push(context,
              MaterialPageRoute(builder: (_) => const ServicesScreen())),
        ),
        const SizedBox(height: 6),
        _ViewRow(
          label: 'Monthly Report',
          sub: 'Summaries · Excel export',
          icon: Icons.assessment,
          onTap: () => Navigator.push(context,
              MaterialPageRoute(builder: (_) => const MonthlyReportScreen())),
        ),
      ],
    );
  }
}

class _ViewRow extends StatelessWidget {
  final String label;
  final String sub;
  final IconData icon;
  final VoidCallback onTap;
  const _ViewRow({required this.label, required this.sub, required this.icon, required this.onTap});
  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 14),
        decoration: BoxDecoration(
          color: AppTheme.bezel,
          border: Border(
            top: BorderSide(color: AppTheme.bezelEdge, width: 1),
            bottom: BorderSide(color: AppTheme.bezelEdge, width: 1),
          ),
        ),
        child: Row(
          children: [
            Icon(icon, color: AppTheme.displayDim, size: 20),
            const SizedBox(width: 14),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(label, style: AppTheme.bigLabel),
                  const SizedBox(height: 2),
                  Text(sub, style: AppTheme.caption),
                ],
              ),
            ),
            Icon(Icons.chevron_right, color: AppTheme.displayDim, size: 18),
          ],
        ),
      ),
    );
  }
}

/// The "bezel" — a card with a thin 1px border and a top-left section label,
/// like an etched label on a physical gauge cluster panel.
class _Bezel extends StatelessWidget {
  final String label;
  final Widget child;
  const _Bezel({required this.label, required this.child});
  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.fromLTRB(16, 12, 16, 16),
      decoration: BoxDecoration(
        color: AppTheme.bezel,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: AppTheme.bezelEdge),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Row(
            children: [
              Container(width: 4, height: 4, color: AppTheme.accent),
              const SizedBox(width: 8),
              Text(label, style: AppTheme.sectionLabel.copyWith(color: AppTheme.accent)),
            ],
          ),
          const SizedBox(height: 8),
          child,
        ],
      ),
    );
  }
}

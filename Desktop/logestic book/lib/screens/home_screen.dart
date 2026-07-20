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
          final dateStr = DateFormat('EEEE, MMMM d').format(now);
          final greeting = _greeting(now.hour);

          return SafeArea(
            child: Column(
              children: [
                _buildHeroHeader(context, greeting, dateStr, todayLog != null),
                Expanded(
                  child: SingleChildScrollView(
                    padding: const EdgeInsets.fromLTRB(20, 24, 20, 24),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        if (todayLog != null) _buildTodayMetrics(context, todayLog),
                        if (todayLog != null) const SizedBox(height: 24),
                        _buildSectionTitle(context, 'Quick Actions'),
                        const SizedBox(height: 12),
                        _buildActionCards(context),
                        const SizedBox(height: 24),
                        _buildSectionTitle(context, 'View Records'),
                        const SizedBox(height: 12),
                        _buildViewButtons(context),
                      ],
                    ),
                  ),
                ),
              ],
            ),
          );
        },
      ),
    );
  }

  String _greeting(int hour) {
    if (hour < 12) return 'Good Morning';
    if (hour < 17) return 'Good Afternoon';
    return 'Good Evening';
  }

  Widget _buildHeroHeader(
      BuildContext context, String greeting, String dateStr, bool hasLog) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.fromLTRB(24, 20, 24, 32),
      decoration: const BoxDecoration(
        gradient: LinearGradient(
          colors: AppTheme.primaryGradient,
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.only(
          bottomLeft: Radius.circular(32),
          bottomRight: Radius.circular(32),
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    greeting,
                    style: const TextStyle(
                      color: Colors.white70,
                      fontSize: 14,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                  const SizedBox(height: 2),
                  Text(
                    dateStr,
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 20,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                ],
              ),
              Container(
                padding: const EdgeInsets.all(10),
                decoration: BoxDecoration(
                  color: Colors.white.withValues(alpha: 0.2),
                  borderRadius: BorderRadius.circular(14),
                ),
                child: const Icon(Icons.directions_car, color: Colors.white, size: 28),
              ),
            ],
          ),
          const SizedBox(height: 20),
          Row(
            children: [
              Icon(
                hasLog ? Icons.check_circle : Icons.radio_button_unchecked,
                color: hasLog ? Colors.greenAccent : Colors.white70,
                size: 20,
              ),
              const SizedBox(width: 8),
              Text(
                hasLog ? "Today's trip logged" : 'No entry for today',
                style: TextStyle(
                  color: hasLog ? Colors.greenAccent : Colors.white70,
                  fontSize: 14,
                  fontWeight: FontWeight.w500,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildTodayMetrics(BuildContext context, dynamic todayLog) {
    final metrics = [
      _MetricData('Start KM', '${todayLog.startKm.toStringAsFixed(0)}', Icons.trip_origin, AppTheme.secondaryGradient),
      _MetricData('End KM', '${todayLog.endKm.toStringAsFixed(0)}', Icons.location_on, AppTheme.primaryGradient),
      _MetricData('Total KM', '${todayLog.totalKm.toStringAsFixed(0)}', Icons.speed, AppTheme.accentGradient),
      _MetricData('Cost', '${todayLog.cost.toStringAsFixed(0)} AED', Icons.monetization_on, AppTheme.secondaryGradient),
    ];

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _buildSectionTitle(context, "Today's Summary"),
        const SizedBox(height: 12),
        GridView.builder(
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
            crossAxisCount: 2,
            childAspectRatio: 1.4,
            crossAxisSpacing: 12,
            mainAxisSpacing: 12,
          ),
          itemCount: 4,
          itemBuilder: (_, i) => _buildMetricCard(metrics[i]),
        ),
      ],
    );
  }

  Widget _buildMetricCard(_MetricData data) {
    return Container(
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(16),
        gradient: LinearGradient(
          colors: data.gradient,
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        boxShadow: [
          BoxShadow(
            color: data.gradient.first.withValues(alpha: 0.3),
            blurRadius: 12,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  data.label,
                  style: const TextStyle(
                    color: Colors.white70,
                    fontSize: 12,
                    fontWeight: FontWeight.w500,
                  ),
                ),
                Icon(data.icon, color: Colors.white70, size: 18),
              ],
            ),
            Text(
              data.value,
              style: const TextStyle(
                color: Colors.white,
                fontSize: 20,
                fontWeight: FontWeight.w800,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSectionTitle(BuildContext context, String title) {
    return Text(
      title,
      style: const TextStyle(
        color: AppTheme.darkText,
        fontSize: 16,
        fontWeight: FontWeight.w700,
      ),
    );
  }

  Widget _buildActionCards(BuildContext context) {
    return Row(
      children: [
        Expanded(
          child: _ActionCard(
            icon: Icons.add_road,
            label: 'New Daily Entry',
            color: AppTheme.primaryLight,
            onTap: () => Navigator.push(
              context,
              MaterialPageRoute(builder: (_) => const DailyLogFormScreen()),
            ),
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: _ActionCard(
            icon: Icons.build,
            label: 'New Service',
            color: AppTheme.secondary,
            onTap: () => Navigator.push(
              context,
              MaterialPageRoute(builder: (_) => const ServiceFormScreen()),
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildViewButtons(BuildContext context) {
    return Column(
      children: [
        _ViewRow(
          icon: Icons.list_alt,
          label: 'All Daily Logs',
          subtitle: 'View and manage trip entries',
          color: AppTheme.primaryLight,
          onTap: () => Navigator.push(
            context,
            MaterialPageRoute(builder: (_) => const DailyLogsScreen()),
          ),
        ),
        const SizedBox(height: 10),
        _ViewRow(
          icon: Icons.build_circle,
          label: 'All Services',
          subtitle: 'View and manage service records',
          color: AppTheme.secondary,
          onTap: () => Navigator.push(
            context,
            MaterialPageRoute(builder: (_) => const ServicesScreen()),
          ),
        ),
        const SizedBox(height: 10),
        _ViewRow(
          icon: Icons.assessment,
          label: 'Monthly Report',
          subtitle: 'View summaries and export to Excel',
          color: AppTheme.accent,
          onTap: () => Navigator.push(
            context,
            MaterialPageRoute(builder: (_) => const MonthlyReportScreen()),
          ),
        ),
      ],
    );
  }
}

class _MetricData {
  final String label;
  final String value;
  final IconData icon;
  final List<Color> gradient;
  _MetricData(this.label, this.value, this.icon, this.gradient);
}

class _ActionCard extends StatelessWidget {
  final IconData icon;
  final String label;
  final Color color;
  final VoidCallback onTap;

  const _ActionCard({
    required this.icon,
    required this.label,
    required this.color,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.all(20),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(16),
          boxShadow: [
            BoxShadow(
              color: color.withValues(alpha: 0.15),
              blurRadius: 12,
              offset: const Offset(0, 4),
            ),
          ],
        ),
        child: Column(
          children: [
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: color.withValues(alpha: 0.1),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Icon(icon, color: color, size: 28),
            ),
            const SizedBox(height: 12),
            Text(
              label,
              textAlign: TextAlign.center,
              style: const TextStyle(
                color: AppTheme.darkText,
                fontSize: 13,
                fontWeight: FontWeight.w600,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _ViewRow extends StatelessWidget {
  final IconData icon;
  final String label;
  final String subtitle;
  final Color color;
  final VoidCallback onTap;

  const _ViewRow({
    required this.icon,
    required this.label,
    required this.subtitle,
    required this.color,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Material(
      color: Colors.white,
      borderRadius: BorderRadius.circular(16),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(16),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Row(
            children: [
              Container(
                padding: const EdgeInsets.all(10),
                decoration: BoxDecoration(
                  color: color.withValues(alpha: 0.1),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Icon(icon, color: color, size: 24),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      label,
                      style: const TextStyle(
                        color: AppTheme.darkText,
                        fontSize: 15,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                    const SizedBox(height: 2),
                    Text(
                      subtitle,
                      style: const TextStyle(
                        color: AppTheme.mediumText,
                        fontSize: 12,
                      ),
                    ),
                  ],
                ),
              ),
              Icon(Icons.chevron_right, color: AppTheme.mediumText, size: 20),
            ],
          ),
        ),
      ),
    );
  }
}

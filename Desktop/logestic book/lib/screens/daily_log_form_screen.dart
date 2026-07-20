import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:intl/intl.dart';
import 'package:logestic_app/models/daily_log.dart';
import 'package:logestic_app/providers/log_provider.dart';
import 'package:logestic_app/theme/app_theme.dart';
import 'package:logestic_app/widgets/pinned_places_card.dart';

class DailyLogFormScreen extends StatefulWidget {
  final DailyLog? existingLog;
  const DailyLogFormScreen({super.key, this.existingLog});

  @override
  State<DailyLogFormScreen> createState() => _DailyLogFormScreenState();
}

class _DailyLogFormScreenState extends State<DailyLogFormScreen> {
  final _formKey = GlobalKey<FormState>();
  late TextEditingController _startKmCtrl;
  late TextEditingController _endKmCtrl;
  late TextEditingController _costCtrl;
  late TextEditingController _notesCtrl;
  late DateTime _selectedDate;
  bool _isEditing = false;
  double? _autoFilledKm;
  bool _didPrefill = false;
  late List<PlacePin> _pins;

  @override
  void initState() {
    super.initState();
    _isEditing = widget.existingLog != null;
    _selectedDate = widget.existingLog?.date ?? DateTime.now();
    _startKmCtrl = TextEditingController(
        text: widget.existingLog?.startKm.toStringAsFixed(0) ?? '');
    _endKmCtrl = TextEditingController(
        text: widget.existingLog?.endKm.toStringAsFixed(0) ?? '');
    _costCtrl = TextEditingController(
        text: widget.existingLog?.cost.toStringAsFixed(2) ?? '');
    _notesCtrl =
        TextEditingController(text: widget.existingLog?.notes ?? '');
    _pins = widget.existingLog?.pins.toList() ?? [];
  }

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    if (_didPrefill || _isEditing) {
      _didPrefill = true;
      return;
    }
    _didPrefill = true;
    final prev =
        Provider.of<LogProvider>(context, listen: false)
            .previousEndKmForDate(_selectedDate);
    if (prev != null) {
      _autoFilledKm = prev;
      _startKmCtrl.text = prev.toStringAsFixed(0);
    } else {
      _autoFilledKm = null;
    }
  }

  @override
  void dispose() {
    _startKmCtrl.dispose();
    _endKmCtrl.dispose();
    _costCtrl.dispose();
    _notesCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final totalKm = (_startKmCtrl.text.isNotEmpty &&
            _endKmCtrl.text.isNotEmpty)
        ? (double.tryParse(_endKmCtrl.text) ?? 0) -
            (double.tryParse(_startKmCtrl.text) ?? 0)
        : 0.0;

    return Scaffold(
      appBar: AppBar(
        title: Text(_isEditing ? 'Edit Daily Entry' : 'New Daily Entry'),
        actions: _isEditing
            ? [
                IconButton(
                  icon: const Icon(Icons.delete_outline),
                  onPressed: _confirmDelete,
                  tooltip: 'Delete',
                ),
              ]
            : null,
      ),
      body: Form(
        key: _formKey,
        child: ListView(
          padding: const EdgeInsets.fromLTRB(20, 12, 20, 32),
          children: [
            _buildDatePicker(context),
            const SizedBox(height: 20),
            _buildKmSection(totalKm),
            const SizedBox(height: 16),
            _buildTextField(
              controller: _costCtrl,
              label: 'Cost (AED)',
              icon: Icons.monetization_on,
              keyboardType: TextInputType.number,
              validator: (v) => v == null || v.isEmpty ? 'Required' : null,
            ),
            const SizedBox(height: 16),
            PinnedPlacesCard(
              pins: _pins,
              onChanged: (newPins) => setState(() => _pins = newPins),
            ),
            const SizedBox(height: 16),
            _buildTextField(
              controller: _notesCtrl,
              label: 'Notes',
              icon: Icons.notes,
              maxLines: 3,
            ),
            const SizedBox(height: 32),
            SizedBox(
              height: 52,
              child: ElevatedButton(
                onPressed: _save,
                style: ElevatedButton.styleFrom(
                  backgroundColor: AppTheme.primary,
                  foregroundColor: Colors.white,
                ),
                child: Text(
                  _isEditing ? 'Update Entry' : 'Save Entry',
                  style: const TextStyle(fontSize: 16),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildDatePicker(BuildContext context) {
    return InkWell(
      onTap: _pickDate,
      borderRadius: BorderRadius.circular(16),
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: const Color(0xFFE2E8F0)),
        ),
        child: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: AppTheme.primaryLight.withValues(alpha: 0.1),
                borderRadius: BorderRadius.circular(10),
              ),
              child: const Icon(Icons.calendar_today,
                  color: AppTheme.primaryLight, size: 20),
            ),
            const SizedBox(width: 14),
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text('Date',
                    style: TextStyle(
                        color: AppTheme.mediumText, fontSize: 12)),
                const SizedBox(height: 2),
                Text(
                  DateFormat('EEEE, MMMM d, yyyy').format(_selectedDate),
                  style: const TextStyle(
                    color: AppTheme.darkText,
                    fontSize: 15,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ],
            ),
            const Spacer(),
            const Icon(Icons.edit_calendar,
                color: AppTheme.mediumText, size: 20),
          ],
        ),
      ),
    );
  }

  Widget _buildKmSection(double totalKm) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: const Color(0xFFE2E8F0)),
      ),
      child: Column(
        children: [
          Row(
            children: [
              Expanded(
                child: _buildTextField(
                  controller: _startKmCtrl,
                  label: 'Start KM',
                  icon: Icons.trip_origin,
                  keyboardType: TextInputType.number,
                  validator: (v) =>
                      v == null || v.isEmpty ? 'Required' : null,
                  helperText: (_autoFilledKm == null && _startKmCtrl.text.isEmpty)
                      ? 'No previous entry — enter the start odometer manually'
                      : null,
                  suffixIcon: _showsAutoFillBadge()
                      ? const Icon(Icons.auto_fix_high,
                          size: 18, color: AppTheme.primaryLight)
                      : null,
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: _buildTextField(
                  controller: _endKmCtrl,
                  label: 'End KM',
                  icon: Icons.location_on,
                  keyboardType: TextInputType.number,
                  validator: (v) =>
                      v == null || v.isEmpty ? 'Required' : null,
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Container(
            width: double.infinity,
            padding: const EdgeInsets.symmetric(vertical: 10, horizontal: 16),
            decoration: BoxDecoration(
              gradient: const LinearGradient(
                  colors: AppTheme.accentGradient),
              borderRadius: BorderRadius.circular(10),
            ),
            child: Text(
              'Total: ${totalKm.toStringAsFixed(0)} KM',
              textAlign: TextAlign.center,
              style: const TextStyle(
                color: Colors.white,
                fontSize: 15,
                fontWeight: FontWeight.w700,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildTextField({
    required TextEditingController controller,
    required String label,
    required IconData icon,
    TextInputType? keyboardType,
    String? Function(String?)? validator,
    int maxLines = 1,
    String? helperText,
    Widget? suffixIcon,
  }) {
    return TextFormField(
      controller: controller,
      decoration: InputDecoration(
        labelText: label,
        prefixIcon: Icon(icon),
        helperText: helperText,
        suffixIcon: suffixIcon,
      ),
      keyboardType: keyboardType,
      validator: validator,
      maxLines: maxLines,
      onChanged: (_) => setState(() {}),
    );
  }

  Future<void> _pickDate() async {
    final picked = await showDatePicker(
      context: context,
      initialDate: _selectedDate,
      firstDate: DateTime(2020),
      lastDate: DateTime(2030),
    );
    if (picked != null && mounted) {
      setState(() => _selectedDate = picked);
    }
  }

  void _save() {
    if (!_formKey.currentState!.validate()) return;

    final startKm = double.parse(_startKmCtrl.text);
    final endKm = double.parse(_endKmCtrl.text);
    final totalKm = endKm - startKm;
    final cost = double.parse(_costCtrl.text);
    final provider = context.read<LogProvider>();

    final log = DailyLog(
      id: widget.existingLog?.id ?? '',
      date: _selectedDate,
      startKm: startKm,
      endKm: endKm,
      totalKm: totalKm,
      cost: cost,
      notes: _notesCtrl.text,
      pins: _pins,
    );

    if (_isEditing) {
      provider.updateDailyLog(log);
    } else {
      provider.addDailyLog(log);
    }
    Navigator.pop(context);
  }

  bool _showsAutoFillBadge() {
    if (_autoFilledKm == null) return false;
    return _startKmCtrl.text == _autoFilledKm!.toStringAsFixed(0);
  }

  void _confirmDelete() {

    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Delete Entry?'),
        content: const Text('This cannot be undone'),
        actions: [
          TextButton(
              onPressed: () => Navigator.pop(ctx),
              child: const Text('Cancel')),
          TextButton(
            onPressed: () {
              context
                  .read<LogProvider>()
                  .deleteDailyLog(widget.existingLog!.id);
              Navigator.pop(ctx);
              Navigator.pop(context);
            },
            child:
                const Text('Delete', style: TextStyle(color: Colors.red)),
          ),
        ],
      ),
    );
  }
}

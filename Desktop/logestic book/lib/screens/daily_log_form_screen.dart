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
        title: const Text('DAILY ENTRY'),
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
          padding: const EdgeInsets.fromLTRB(16, 12, 16, 32),
          children: [
            _buildDatePicker(context),
            const SizedBox(height: 16),
            _buildKmSection(totalKm),
            const SizedBox(height: 12),
            _buildCostField(),
            const SizedBox(height: 12),
            PinnedPlacesCard(
              pins: _pins,
              onChanged: (newPins) => setState(() => _pins = newPins),
            ),
            const SizedBox(height: 12),
            _buildNotesField(),
            const SizedBox(height: 28),
            SizedBox(
              height: 56,
              child: ElevatedButton(
                onPressed: _save,
                style: ElevatedButton.styleFrom(
                  backgroundColor: AppTheme.accent,
                  foregroundColor: const Color(0xFF1A0F00),
                ),
                child: Text(
                  _isEditing ? 'UPDATE ENTRY' : 'SAVE ENTRY',
                  style: AppTheme.bigLabel.copyWith(color: const Color(0xFF1A0F00)),
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
      child: Container(
        padding: const EdgeInsets.fromLTRB(16, 14, 16, 14),
        decoration: BoxDecoration(
          color: AppTheme.bezel,
          border: Border.all(color: AppTheme.bezelEdge),
        ),
        child: Row(
          children: [
            Container(width: 4, height: 4, color: AppTheme.accent),
            const SizedBox(width: 10),
            Text('DATE', style: AppTheme.sectionLabel.copyWith(color: AppTheme.accent)),
            const SizedBox(width: 12),
            Text(
              DateFormat('EEE · MMM d, yyyy').format(_selectedDate).toUpperCase(),
              style: AppTheme.bigLabel,
            ),
            const Spacer(),
            Icon(Icons.edit_calendar, color: AppTheme.displayDim, size: 18),
          ],
        ),
      ),
    );
  }

  Widget _buildKmSection(double totalKm) {
    return Container(
      padding: const EdgeInsets.fromLTRB(16, 16, 16, 16),
      decoration: BoxDecoration(
        color: AppTheme.bezel,
        border: Border.all(color: AppTheme.bezelEdge),
      ),
      child: Column(
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text('ODOMETER', style: AppTheme.sectionLabel),
              if (_showsAutoFillBadge())
                Row(
                  children: [
                    Icon(Icons.auto_fix_high, color: AppTheme.primaryLight, size: 14),
                    const SizedBox(width: 4),
                    Text('AUTO-FILLED', style: AppTheme.sectionLabel.copyWith(color: AppTheme.primaryLight)),
                  ],
                ),
            ],
          ),
          const SizedBox(height: 12),
          Row(
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [
              Expanded(
                child: _OdoField(
                  controller: _startKmCtrl,
                  label: 'START',
                  onChanged: (_) => setState(() {}),
                ),
              ),
              const SizedBox(width: 10),
              Icon(Icons.arrow_forward, color: AppTheme.displayDim, size: 18),
              const SizedBox(width: 10),
              Expanded(
                child: _OdoField(
                  controller: _endKmCtrl,
                  label: 'END',
                  onChanged: (_) => setState(() {}),
                ),
              ),
            ],
          ),
          if (_autoFilledKm == null && _startKmCtrl.text.isEmpty)
            Padding(
              padding: const EdgeInsets.only(top: 8),
              child: Text(
                'No previous entry — enter the start odometer manually',
                style: AppTheme.caption,
              ),
            ),
          const SizedBox(height: 16),
          Container(
            width: double.infinity,
            padding: const EdgeInsets.symmetric(vertical: 10, horizontal: 16),
            decoration: BoxDecoration(
              color: const Color(0xFF0B1220),
              border: Border.all(color: AppTheme.accent.withValues(alpha: 0.4)),
            ),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Text('TOTAL  ', style: AppTheme.sectionLabel.copyWith(color: AppTheme.accent)),
                Text(totalKm.toStringAsFixed(0),
                    style: AppTheme.hugeNumber.copyWith(color: AppTheme.accentBright, fontSize: 32)),
                Text('  KM', style: AppTheme.sectionLabel.copyWith(color: AppTheme.accent)),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildCostField() {
    return Container(
      padding: const EdgeInsets.fromLTRB(16, 12, 16, 12),
      decoration: BoxDecoration(
        color: AppTheme.bezel,
        border: Border.all(color: AppTheme.bezelEdge),
      ),
      child: Row(
        children: [
          Container(width: 4, height: 4, color: AppTheme.accent),
          const SizedBox(width: 10),
          Text('COST', style: AppTheme.sectionLabel.copyWith(color: AppTheme.accent)),
          const SizedBox(width: 14),
          Expanded(
            child: TextFormField(
              controller: _costCtrl,
              keyboardType: TextInputType.number,
              style: AppTheme.bigNumber,
              decoration: const InputDecoration(
                border: InputBorder.none,
                enabledBorder: InputBorder.none,
                focusedBorder: InputBorder.none,
                filled: false,
                hintText: '0',
                hintStyle: TextStyle(color: AppTheme.tickDim),
                isDense: true,
                contentPadding: EdgeInsets.zero,
              ),
              validator: (v) => v == null || v.isEmpty ? 'Required' : null,
              onChanged: (_) => setState(() {}),
            ),
          ),
          Text('AED', style: AppTheme.sectionLabel),
        ],
      ),
    );
  }

  Widget _buildNotesField() {
    return Container(
      padding: const EdgeInsets.fromLTRB(16, 12, 16, 12),
      decoration: BoxDecoration(
        color: AppTheme.bezel,
        border: Border.all(color: AppTheme.bezelEdge),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(width: 4, height: 4, color: AppTheme.displayDim),
              const SizedBox(width: 10),
              Text('NOTES', style: AppTheme.sectionLabel),
            ],
          ),
          const SizedBox(height: 6),
          TextFormField(
            controller: _notesCtrl,
            maxLines: 3,
            style: AppTheme.bodyText,
            decoration: const InputDecoration(
              border: InputBorder.none,
              enabledBorder: InputBorder.none,
              focusedBorder: InputBorder.none,
              filled: false,
              isDense: true,
              contentPadding: EdgeInsets.zero,
              hintText: 'Optional...',
              hintStyle: TextStyle(color: AppTheme.tickDim),
            ),
          ),
        ],
      ),
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

/// Big monospaced odometer-style text field.
class _OdoField extends StatelessWidget {
  final TextEditingController controller;
  final String label;
  final ValueChanged<String>? onChanged;
  const _OdoField({required this.controller, required this.label, this.onChanged});
  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.fromLTRB(12, 8, 12, 8),
      decoration: BoxDecoration(
        color: const Color(0xFF0B1220),
        border: Border.all(color: AppTheme.bezelEdge),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(label, style: AppTheme.sectionLabel),
          const SizedBox(height: 2),
          TextFormField(
            controller: controller,
            keyboardType: TextInputType.number,
            style: AppTheme.hugeNumber.copyWith(fontSize: 28),
            decoration: const InputDecoration(
              border: InputBorder.none,
              enabledBorder: InputBorder.none,
              focusedBorder: InputBorder.none,
              filled: false,
              isDense: true,
              contentPadding: EdgeInsets.zero,
              hintText: '000000',
              hintStyle: TextStyle(color: AppTheme.tickDim, fontSize: 28),
            ),
            validator: (v) => v == null || v.isEmpty ? 'Required' : null,
            onChanged: onChanged,
          ),
        ],
      ),
    );
  }
}

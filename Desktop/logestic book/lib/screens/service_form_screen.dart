import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:intl/intl.dart';
import 'package:logestic_app/models/service_log.dart';
import 'package:logestic_app/providers/log_provider.dart';
import 'package:logestic_app/theme/app_theme.dart';

class ServiceFormScreen extends StatefulWidget {
  final ServiceLog? existingService;
  const ServiceFormScreen({super.key, this.existingService});

  @override
  State<ServiceFormScreen> createState() => _ServiceFormScreenState();
}

class _ServiceFormScreenState extends State<ServiceFormScreen> {
  final _formKey = GlobalKey<FormState>();
  late TextEditingController _kmReadingCtrl;
  late TextEditingController _costCtrl;
  late TextEditingController _notesCtrl;
  late DateTime _selectedDate;
  late String _selectedType;
  bool _isEditing = false;

  @override
  void initState() {
    super.initState();
    _isEditing = widget.existingService != null;
    _selectedDate = widget.existingService?.date ?? DateTime.now();
    _selectedType =
        widget.existingService?.serviceType ?? 'oil_change';
    _kmReadingCtrl = TextEditingController(
        text: widget.existingService?.kmReading.toStringAsFixed(0) ?? '');
    _costCtrl = TextEditingController(
        text: widget.existingService?.cost.toStringAsFixed(2) ?? '');
    _notesCtrl =
        TextEditingController(text: widget.existingService?.notes ?? '');
  }

  @override
  void dispose() {
    _kmReadingCtrl.dispose();
    _costCtrl.dispose();
    _notesCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(_isEditing ? 'Edit Service' : 'New Service'),
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
            _buildTextField(
              controller: _kmReadingCtrl,
              label: 'KM Reading',
              icon: Icons.speed,
              keyboardType: TextInputType.number,
              validator: (v) =>
                  v == null || v.isEmpty ? 'Required' : null,
            ),
            const SizedBox(height: 16),
            _buildTypeDropdown(),
            const SizedBox(height: 16),
            _buildTextField(
              controller: _costCtrl,
              label: 'Cost (DZD)',
              icon: Icons.monetization_on,
              keyboardType: TextInputType.number,
              validator: (v) =>
                  v == null || v.isEmpty ? 'Required' : null,
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
                  _isEditing ? 'Update Service' : 'Save Service',
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

  Widget _buildTypeDropdown() {
    return DropdownButtonFormField<String>(
      initialValue: _selectedType,
      decoration: InputDecoration(
        labelText: 'Service Type',
        prefixIcon: Icon(
          ServiceLog.iconFor(_selectedType),
          color: ServiceLog.colorFor(_selectedType),
        ),
      ),
      items: ServiceLog.serviceTypes.map((type) {
        return DropdownMenuItem(
          value: type,
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(ServiceLog.iconFor(type),
                  size: 20, color: ServiceLog.colorFor(type)),
              const SizedBox(width: 10),
              Flexible(child: Text(ServiceLog.displayName(type))),
            ],
          ),
        );
      }).toList(),
      onChanged: (v) {
        if (v != null) setState(() => _selectedType = v);
      },
    );
  }

  Widget _buildTextField({
    required TextEditingController controller,
    required String label,
    required IconData icon,
    TextInputType? keyboardType,
    String? Function(String?)? validator,
    int maxLines = 1,
  }) {
    return TextFormField(
      controller: controller,
      decoration: InputDecoration(
        labelText: label,
        prefixIcon: Icon(icon),
      ),
      keyboardType: keyboardType,
      validator: validator,
      maxLines: maxLines,
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

    final provider = context.read<LogProvider>();
    final svc = ServiceLog(
      id: widget.existingService?.id ?? '',
      date: _selectedDate,
      kmReading: double.parse(_kmReadingCtrl.text),
      serviceType: _selectedType,
      cost: double.parse(_costCtrl.text),
      notes: _notesCtrl.text,
    );

    if (_isEditing) {
      provider.updateService(svc);
    } else {
      provider.addService(svc);
    }
    Navigator.pop(context);
  }

  void _confirmDelete() {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Delete Service?'),
        content: const Text('This cannot be undone'),
        actions: [
          TextButton(
              onPressed: () => Navigator.pop(ctx),
              child: const Text('Cancel')),
          TextButton(
            onPressed: () {
              context
                  .read<LogProvider>()
                  .deleteService(widget.existingService!.id);
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

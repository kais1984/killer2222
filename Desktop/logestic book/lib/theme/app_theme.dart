import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

class AppTheme {
  // Brand colors (kept for use outside of ColorScheme).
  static const Color primary = Color(0xFF1E40AF);
  static const Color primaryLight = Color(0xFF3B82F6);
  static const Color secondary = Color(0xFF14B8A6);
  static const Color accent = Color(0xFFF59E0B);
  static const Color accentBright = Color(0xFFFBBF24);
  static const Color error = Color(0xFFEF4444);

  // Instrument-cluster palette.
  static const Color clusterBg = Color(0xFF0B1220); // deeper than scaffold
  static const Color clusterBgGlow = Color(0xFF142036); // halo behind hero
  static const Color bezel = Color(0xFF1E2A44); // card surface
  static const Color bezelEdge = Color(0xFF2A3858); // 1px card border
  static const Color tickDim = Color(0xFF334155);
  static const Color displayDim = Color(0xFF64748B);
  static const Color displayBright = Color(0xFFE2E8F0);
  static const Color displayCritical = Color(0xFFF8FAFC);

  static const List<Color> primaryGradient = [Color(0xFF1E40AF), Color(0xFF3B82F6)];
  static const List<Color> secondaryGradient = [Color(0xFF0D9488), Color(0xFF14B8A6)];
  static const List<Color> accentGradient = [Color(0xFFF59E0B), Color(0xFFF97316)];

  // Legacy aliases (kept so existing screens compile).
  static const Color darkText = displayCritical;
  static const Color mediumText = displayDim;
  static const Color surface = bezel;
  static const Color background = clusterBg;

  // Typography.
  static TextStyle _display(double size, FontWeight weight, Color color) =>
      GoogleFonts.jetBrainsMono(
        fontSize: size,
        fontWeight: weight,
        color: color,
        letterSpacing: -0.5,
        height: 1.05,
      );

  static TextStyle _label(double size, FontWeight weight, Color color) =>
      GoogleFonts.spaceGrotesk(
        fontSize: size,
        fontWeight: weight,
        color: color,
        letterSpacing: 1.4,
      );

  // Reusable styles.
  static TextStyle get hugeNumber => _display(48, FontWeight.w800, displayCritical);
  static TextStyle get bigNumber => _display(28, FontWeight.w700, displayBright);
  static TextStyle get mediumNumber => _display(20, FontWeight.w600, displayBright);
  static TextStyle get smallNumber => _display(13, FontWeight.w500, displayDim);
  static TextStyle get sectionLabel => _label(11, FontWeight.w600, displayDim);
  static TextStyle get chipLabel => _label(10, FontWeight.w700, displayBright);
  static TextStyle get bigLabel => _label(14, FontWeight.w700, displayBright);
  static TextStyle get appBarTitle => _label(16, FontWeight.w700, displayCritical);
  static TextStyle get bodyText => GoogleFonts.inter(fontSize: 13, color: displayBright, height: 1.4);
  static TextStyle get caption => GoogleFonts.inter(fontSize: 11, color: displayDim);

  static ThemeData get theme {
    const colorScheme = ColorScheme.dark(
      primary: primaryLight,
      onPrimary: Colors.white,
      secondary: secondary,
      onSecondary: Colors.white,
      tertiary: accent,
      onTertiary: Color(0xFF1A0F00),
      error: error,
      onError: Colors.white,
      surface: bezel,
      onSurface: displayBright,
      surfaceContainerHighest: Color(0xFF243154),
      outline: bezelEdge,
      outlineVariant: tickDim,
    );

    return ThemeData(
      useMaterial3: true,
      brightness: Brightness.dark,
      colorScheme: colorScheme,
      scaffoldBackgroundColor: clusterBg,
      canvasColor: clusterBg,
      appBarTheme: AppBarTheme(
        backgroundColor: clusterBg,
        foregroundColor: displayCritical,
        elevation: 0,
        scrolledUnderElevation: 0,
        centerTitle: true,
        titleTextStyle: appBarTitle,
        iconTheme: const IconThemeData(color: displayBright),
      ),
      cardTheme: CardThemeData(
        elevation: 0,
        color: bezel,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(8),
          side: const BorderSide(color: bezelEdge, width: 1),
        ),
        margin: EdgeInsets.zero,
      ),
      dividerColor: bezelEdge,
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          elevation: 0,
          backgroundColor: primaryLight,
          foregroundColor: Colors.white,
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 14),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(6),
          ),
          textStyle: _label(13, FontWeight.w700, Colors.white),
        ),
      ),
      outlinedButtonTheme: OutlinedButtonThemeData(
        style: OutlinedButton.styleFrom(
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 14),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(6),
          ),
          side: const BorderSide(color: primaryLight, width: 1),
          foregroundColor: primaryLight,
          textStyle: _label(12, FontWeight.w700, primaryLight),
        ),
      ),
      textButtonTheme: TextButtonThemeData(
        style: TextButton.styleFrom(
          foregroundColor: primaryLight,
          textStyle: _label(12, FontWeight.w700, primaryLight),
        ),
      ),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: const Color(0xFF0E1A30),
        labelStyle: _label(11, FontWeight.w600, displayDim),
        floatingLabelStyle: _label(11, FontWeight.w700, primaryLight),
        hintStyle: GoogleFonts.inter(fontSize: 14, color: displayDim),
        helperStyle: GoogleFonts.inter(fontSize: 11, color: displayDim),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(6),
          borderSide: const BorderSide(color: bezelEdge, width: 1),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(6),
          borderSide: const BorderSide(color: bezelEdge, width: 1),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(6),
          borderSide: const BorderSide(color: primaryLight, width: 1.5),
        ),
        errorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(6),
          borderSide: const BorderSide(color: error, width: 1),
        ),
        contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 14),
        prefixIconColor: displayDim,
        suffixIconColor: displayDim,
      ),
      floatingActionButtonTheme: FloatingActionButtonThemeData(
        backgroundColor: accent,
        foregroundColor: const Color(0xFF1A0F00),
        elevation: 0,
        focusElevation: 0,
        hoverElevation: 0,
        highlightElevation: 0,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(8),
        ),
      ),
      chipTheme: ChipThemeData(
        backgroundColor: const Color(0xFF1A2540),
        labelStyle: chipLabel,
        side: const BorderSide(color: bezelEdge),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(4),
          side: const BorderSide(color: bezelEdge),
        ),
        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
        deleteIconColor: displayDim,
      ),
      snackBarTheme: SnackBarThemeData(
        backgroundColor: bezel,
        contentTextStyle: bodyText,
        behavior: SnackBarBehavior.floating,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(6),
          side: const BorderSide(color: bezelEdge),
        ),
      ),
      dialogTheme: DialogThemeData(
        backgroundColor: bezel,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(8),
          side: const BorderSide(color: bezelEdge),
        ),
        titleTextStyle: appBarTitle,
        contentTextStyle: bodyText,
      ),
      iconTheme: const IconThemeData(color: displayBright),
      textTheme: TextTheme(
        bodySmall: GoogleFonts.inter(fontSize: 12, color: displayDim),
        bodyMedium: GoogleFonts.inter(fontSize: 13, color: displayBright),
        bodyLarge: GoogleFonts.inter(fontSize: 14, color: displayBright),
        titleSmall: _label(12, FontWeight.w700, displayBright),
        titleMedium: _label(14, FontWeight.w700, displayBright),
        titleLarge: _label(16, FontWeight.w700, displayCritical),
      ),
    );
  }
}

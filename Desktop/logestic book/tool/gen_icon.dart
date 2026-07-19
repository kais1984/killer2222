// Generates assets/icon.png (1024x1024) for the driver log book app icon.
// Run from project root:  dart run tool/gen_icon.dart

import 'dart:io';
import 'dart:math' as math;
import 'package:image/image.dart' as img;

const int kSize = 1024;
const int kRadius = 220;

const int kPrimary = 0xFF1E40AF;
const int kPrimaryLight = 0xFF3B82F6;
const int kDarkText = 0xFF1E293B;
const int kAmber = 0xFFF59E0B;
const int kAmber2 = 0xFFF97316;
const int kWhite = 0xFFFFFFFF;

int lerpColor(int a, int b, double t) {
  int la = (a >> 16) & 0xff, lra = (a >> 8) & 0xff, lba = a & 0xff;
  int lb = (b >> 16) & 0xff, lrb = (b >> 8) & 0xff, lbb = b & 0xff;
  int r = (la + (lb - la) * t).round();
  int g = (lra + (lrb - lra) * t).round();
  int bl = (lba + (lbb - lba) * t).round();
  return (0xff << 24) | (r << 16) | (g << 8) | bl;
}

void setPx(img.Image im, int x, int y, int argb) {
  im.setPixelRgb(
      x, y, (argb >> 16) & 0xff, (argb >> 8) & 0xff, argb & 0xff);
}

img.Color rgbFromInt(int argb) =>
    img.ColorRgb8((argb >> 16) & 0xff, (argb >> 8) & 0xff, argb & 0xff);

void fillCircle(img.Image im, int cx, int cy, int r, int color) {
  for (int y = -r; y <= r; y++) {
    for (int x = -r; x <= r; x++) {
      if (x * x + y * y <= r * r) {
        setPx(im, cx + x, cy + y, color);
      }
    }
  }
}

void fillRoundRectGradient(img.Image im, int x0, int y0, int x1, int y1,
    int radius, int top, int bottom) {
  for (int y = y0; y < y1; y++) {
    final t = (y - y0) / (y1 - y0 - 1);
    final col = lerpColor(top, bottom, t);
    for (int x = x0; x < x1; x++) {
      bool inside = true;
      int dxLeft = x0 + radius - x;
      int dyTop = y0 + radius - y;
      int dxRight = x - (x1 - radius - 1);
      int dyBot = y - (y1 - radius - 1);
      if (x < x0 + radius && y < y0 + radius) {
        inside = dxLeft * dxLeft + dyTop * dyTop <= radius * radius;
      } else if (x >= x1 - radius && y < y0 + radius) {
        inside = dxRight * dxRight + dyTop * dyTop <= radius * radius;
      } else if (x < x0 + radius && y >= y1 - radius) {
        inside = dxLeft * dxLeft + dyBot * dyBot <= radius * radius;
      } else if (x >= x1 - radius && y >= y1 - radius) {
        inside = dxRight * dxRight + dyBot * dyBot <= radius * radius;
      }
      if (inside) {
        setPx(im, x, y, col);
      }
    }
  }
}

void fillPolygon(img.Image im, List<List<int>> pts, int color) {
  final ys = pts.map((p) => p[1]).toList();
  int ymin = ys.reduce(math.min), ymax = ys.reduce(math.max);
  for (int y = ymin; y <= ymax; y++) {
    final xs = <int>[];
    for (int i = 0; i < pts.length; i++) {
      final p1 = pts[i];
      final p2 = pts[(i + 1) % pts.length];
      if ((p1[1] <= y && p2[1] > y) || (p2[1] <= y && p1[1] > y)) {
        final x = p1[0] + (y - p1[1]) * (p2[0] - p1[0]) / (p2[1] - p1[1]);
        xs.add(x.round());
      }
    }
    xs.sort();
    for (int i = 0; i + 1 < xs.length; i += 2) {
      for (int x = xs[i]; x <= xs[i + 1]; x++) {
        setPx(im, x, y, color);
      }
    }
  }
}

void main() {
  final im = img.Image(width: kSize, height: kSize);

  // 1) Rounded-rect background with vertical gradient.
  fillRoundRectGradient(im, 0, 0, kSize, kSize, kRadius, kPrimary, kPrimaryLight);

  // 2) Car body — rounded rectangle, centered. white.
  const carBodyX0 = 230, carBodyY0 = 480, carBodyX1 = 794, carBodyY1 = 660;
  for (int y = carBodyY0; y < carBodyY1; y++) {
    for (int x = carBodyX0; x < carBodyX1; x++) {
      bool inside = true;
      int radius = 60;
      int dxLeft = carBodyX0 + radius - x;
      int dyTop = carBodyY0 + radius - y;
      int dxRight = x - (carBodyX1 - radius - 1);
      int dyBot = y - (carBodyY1 - radius - 1);
      if (x < carBodyX0 + radius && y < carBodyY0 + radius) {
        inside = dxLeft * dxLeft + dyTop * dyTop <= radius * radius;
      } else if (x >= carBodyX1 - radius && y < carBodyY0 + radius) {
        inside = dxRight * dxRight + dyTop * dyTop <= radius * radius;
      } else if (x < carBodyX0 + radius && y >= carBodyY1 - radius) {
        inside = dxLeft * dxLeft + dyBot * dyBot <= radius * radius;
      } else if (x >= carBodyX1 - radius && y >= carBodyY1 - radius) {
        inside = dxRight * dxRight + dyBot * dyBot <= radius * radius;
      }
      if (inside) {
        setPx(im, x, y, kWhite);
      }
    }
  }

  // 3) Cabin — trapezoid above the body, white.
  fillPolygon(im, [
    [340, 380],
    [684, 380],
    [744, 480],
    [280, 480],
  ], kWhite);

  // 4) Wheels — dark blue circles.
  fillCircle(im, 360, 660, 56, kDarkText);
  fillCircle(im, 664, 660, 56, kDarkText);

  // 5) Speedometer badge — amber arc in the top-right.
  const gaugeCx = 760, gaugeCy = 250;
  const outerR = 130, innerR = 92;
  // Draw outer amber disk.
  fillCircle(im, gaugeCx, gaugeCy, outerR, kAmber);
  // Cut the inner hole and open the bottom 120° of both rings.
  for (int y = -outerR; y <= outerR; y++) {
    for (int x = -outerR; x <= outerR; x++) {
      if (x * x + y * y > outerR * outerR) continue;
      final ang = math.atan2(y, x);
      // Open at bottom: skip pixels whose angle points toward bottom (~0.1π to ~0.9π).
      if (ang > math.pi * 0.10 && ang < math.pi * 0.90) {
        final px = gaugeCx + x, py = gaugeCy + y;
        if (px < 0 || px >= kSize || py < 0 || py >= kSize) continue;
        final t = py / (kSize - 1);
        setPx(im, px, py, lerpColor(kPrimary, kPrimaryLight, t));
      }
    }
  }
  // Cut the inner hole to background gradient color.
  for (int y = -innerR; y <= innerR; y++) {
    for (int x = -innerR; x <= innerR; x++) {
      if (x * x + y * y > innerR * innerR) continue;
      final px = gaugeCx + x, py = gaugeCy + y;
      if (px < 0 || px >= kSize || py < 0 || py >= kSize) continue;
      final t = py / (kSize - 1);
      setPx(im, px, py, lerpColor(kPrimary, kPrimaryLight, t));
    }
  }

  // 6) Thin white inner ring inside the gauge.
  final ringR = (outerR + innerR) ~/ 2;
  for (double a = -math.pi * 0.6; a <= math.pi * 0.6; a += 0.01) {
    if (a > 0.1 * math.pi && a < 0.9 * math.pi) continue;
    final px = gaugeCx + ringR * math.cos(a);
    final py = gaugeCy - ringR * math.sin(a);
    setPx(im, px.round(), py.round(), kWhite);
  }

  // 7) Needle — from hub to ~3 o'clock.
  img.drawLine(im,
      x1: gaugeCx,
      y1: gaugeCy,
      x2: gaugeCx + (outerR - 14),
      y2: gaugeCy - 8,
      color: rgbFromInt(kWhite),
      thickness: 6);

  // 8) Hub dot — amber2 accent.
  fillCircle(im, gaugeCx, gaugeCy, 12, kAmber2);

  // Encode and save.
  final png = img.encodePng(im);
  final file = File('assets/icon.png');
  file.createSync(recursive: true);
  file.writeAsBytesSync(png);
  stdout.writeln('Wrote assets/icon.png (${png.length} bytes)');
}

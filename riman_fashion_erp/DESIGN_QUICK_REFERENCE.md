# Premium ERP Design System - Quick Reference

## 🎨 Color System

| Name | Value | Usage |
|------|-------|-------|
| Primary | #3D4A5D | Links, borders, primary actions |
| Secondary | #4F8CFF | Highlights, accents |
| Success | #10B981 | Positive actions, status |
| Warning | #F59E0B | Caution, alerts |
| Danger | #EF4444 | Destructive actions |
| Background | #F6F7F9 | Page background |
| Gray-50 to 900 | Scale | Neutral elements |

## 📏 Spacing Scale

```
--space-xs   = 0.25rem (4px)
--space-sm   = 0.5rem (8px)
--space-md   = 1rem (16px)
--space-lg   = 1.5rem (24px)
--space-xl   = 2rem (32px)
--space-2xl  = 2.5rem (40px)
--space-3xl  = 3rem (48px)
```

## 🔤 Typography

| Element | Font | Size | Weight |
|---------|------|------|--------|
| H1 | Inter | 2rem | 700 |
| H2 | Inter | 1.5rem | 600 |
| H3 | Inter | 1.25rem | 600 |
| Body | Inter | 0.9375rem | 400 |
| Label | Inter | 0.9375rem | 600 |
| Small | Inter | 0.875rem | 400 |

## 🎯 Component Classes

### Navigation
```html
<a href="/" class="sidebar-link active">
<a href="/" class="nav-link">
```

### Cards
```html
<div class="card hover-lift">
<div class="card-header">Title</div>
<div class="card-body">Content</div>
```

### KPIs
```html
<div class="kpi-grid">
  <div class="kpi-card hover-lift">
    <div class="kpi-icon"><i data-feather="icon"></i></div>
    <div class="kpi-value">1,234</div>
    <div class="kpi-label">Label</div>
  </div>
</div>
```

### Buttons
```html
<button class="btn btn-primary">Primary</button>
<button class="btn btn-outline">Outline</button>
<button class="btn btn-icon"><i data-feather="icon"></i></button>
<button class="btn btn-success/warning/danger">Colored</button>
```

### Forms
```html
<div class="form-group">
  <label class="form-label">Field Label</label>
  <input type="text" class="form-control">
</div>

<div class="form-check">
  <input type="checkbox" class="form-check-input">
  <label class="form-check-label">Checkbox</label>
</div>
```

### Badges
```html
<span class="badge badge-primary">Primary</span>
<span class="badge badge-success">Success</span>
<span class="badge badge-warning">Warning</span>
```

### Alerts
```html
<div class="alert alert-success">Success message</div>
<div class="alert alert-danger">Error message</div>
<div class="alert alert-warning">Warning message</div>
```

### Tables
```html
<div class="table-container">
  <table class="table">
    <thead>
      <tr><th>Column</th></tr>
    </thead>
    <tbody>
      <tr><td>Data</td></tr>
    </tbody>
  </table>
</div>
```

### Lists
```html
<div class="list-group">
  <a href="/" class="list-group-item hover-lift">
    <h6>Item Title</h6>
    <small>Description</small>
  </a>
</div>
```

## 🎬 Animations

| Animation | Duration | Usage |
|-----------|----------|-------|
| fadeIn | 0.4s | Page load, element appear |
| slideInLeft | 0.4s | Sidebar items |
| slideInRight | 0.4s | Modals |
| hover-lift | 0.2s | Card hover (translateY -4px) |
| pulse | 2s | Status indicators |

## 📱 Responsive Breakpoints

```
Mobile:   < 768px   (Full width, collapsed sidebar)
Tablet:   768-1199px (Adjusted spacing)
Desktop:  1200px+   (Full sidebar + content)
```

## 🎯 Layout Structure

```html
<nav class="navbar"><!-- Top navigation --></nav>

<div class="app-layout">
  <aside class="app-sidebar"><!-- Left nav --></aside>
  <main class="app-content"><!-- Page content --></main>
</div>

<footer><!-- Footer --></footer>
```

## 🔗 Icon Integration

Using **Feather Icons**:
```html
<i data-feather="icon-name"></i>

<!-- Common icons -->
home, shopping-cart, package, users, bar-chart-2
settings, file-text, plus, check-circle, alert-circle
trending-up, trending-down, chevron-right, menu
```

## ✨ Hover Effects

- **Cards**: Lift + shadow (0.2s)
- **Buttons**: Background fade + scale (0.15s)
- **Links**: Color change + underline
- **Form inputs**: Focus glow (3px box-shadow)
- **List items**: Slide right + background (0.2s)

## 📊 Shadow System

| Level | Value | Usage |
|-------|-------|-------|
| xs | 0 1px 2px rgba(0,0,0,0.04) | Subtle borders |
| sm | 0 2px 4px rgba(0,0,0,0.06) | Cards default |
| md | 0 4px 12px rgba(0,0,0,0.08) | Hover cards |
| lg | 0 8px 20px rgba(0,0,0,0.1) | Modals |
| xl | 0 12px 32px rgba(0,0,0,0.12) | Dropdowns |

## 🎨 Border Radius

```
--radius-sm   = 6px   (Small elements)
--radius-md   = 8px   (Buttons, inputs)
--radius-lg   = 12px  (Cards)
--radius-xl   = 16px  (Modals)
--radius-2xl  = 20px  (Large containers)
--radius-full = 9999px (Pills, circles)
```

## 📐 Utility Classes

```
.text-primary       /* Color text */
.text-center        /* Center align */
.text-bold          /* font-weight: 700 */
.bg-light           /* Light background */
.border             /* 1px border */
.shadow-md          /* Medium shadow */
.rounded            /* border-radius-lg */
.hover-lift         /* Lift on hover */
.page-transition    /* Fade in animation */
.d-flex             /* display: flex */
.gap-3              /* gap: var(--space-lg) */
.mb-4               /* margin-bottom */
```

## 🚀 Quick Start Template

```html
{% extends "base.html" %}
{% load static %}

{% block title %}Page Title{% endblock %}

{% block content %}
<div class="page-transition">
  <!-- Page Header -->
  <div class="page-header mb-5">
    <h1><i data-feather="icon-name"></i> Page Title</h1>
    <p>Subtitle or description</p>
  </div>

  <!-- KPI Cards (if needed) -->
  <div class="kpi-grid mb-5">
    <div class="kpi-card hover-lift">
      <div class="kpi-icon"><i data-feather="icon"></i></div>
      <div class="kpi-value">123</div>
      <div class="kpi-label">Metric</div>
    </div>
  </div>

  <!-- Content Grid -->
  <div class="row">
    <div class="col-lg-6">
      <div class="card">
        <div class="card-header">
          <i data-feather="icon"></i> Section Title
        </div>
        <div class="card-body">
          <!-- Card content -->
        </div>
      </div>
    </div>
  </div>
</div>
{% endblock %}
```

## 🔧 Customization Guide

### Change Primary Color
```css
:root {
  --primary-600: #your-color;
  --primary-700: #darker-shade;
}
```

### Add Custom Component
```css
.custom-component {
  background: var(--gray-50);
  border: 1px solid var(--gray-200);
  border-radius: var(--radius-lg);
  padding: var(--space-lg);
  transition: all var(--transition-base);
}

.custom-component:hover {
  box-shadow: var(--shadow-md);
}
```

### Responsive Text
```css
@media (max-width: 768px) {
  h1 { font-size: 1.5rem; }
  .card { margin-bottom: var(--space-lg); }
}
```

## 📚 Resources

- **Base Template**: `templates/base.html`
- **CSS System**: `static/css/premium-erp.css`
- **Components**: `static/css/components-library.css`
- **Documentation**: `PREMIUM_DESIGN_SYSTEM.md`
- **Icons**: Feather Icons (vendored at `static/vendor/feather.min.js`)

## ✅ Verification Checklist

Before deploying:
- [ ] All pages inherit from new base.html
- [ ] Feather icons render correctly
- [ ] Color scheme is consistent
- [ ] Spacing follows 8px grid
- [ ] Responsive design tested on mobile
- [ ] Button hover effects smooth
- [ ] Forms have focus states
- [ ] No remnants of old styling
- [ ] Page transitions work smoothly
- [ ] Sidebar navigation active states correct

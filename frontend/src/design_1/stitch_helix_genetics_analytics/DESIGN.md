---
name: Locus Precision
colors:
  surface: '#fbf8ff'
  surface-dim: '#dad9e3'
  surface-bright: '#fbf8ff'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f4f2fc'
  surface-container: '#eeedf7'
  surface-container-high: '#e8e7f1'
  surface-container-highest: '#e3e1eb'
  on-surface: '#1a1b22'
  on-surface-variant: '#444653'
  inverse-surface: '#2f3037'
  inverse-on-surface: '#f1f0fa'
  outline: '#757684'
  outline-variant: '#c4c5d5'
  surface-tint: '#3755c3'
  primary: '#00288e'
  on-primary: '#ffffff'
  primary-container: '#1e40af'
  on-primary-container: '#a8b8ff'
  inverse-primary: '#b8c4ff'
  secondary: '#006a61'
  on-secondary: '#ffffff'
  secondary-container: '#86f2e4'
  on-secondary-container: '#006f66'
  tertiary: '#5e006c'
  on-tertiary: '#ffffff'
  tertiary-container: '#830096'
  on-tertiary-container: '#f799ff'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#dde1ff'
  primary-fixed-dim: '#b8c4ff'
  on-primary-fixed: '#001453'
  on-primary-fixed-variant: '#173bab'
  secondary-fixed: '#89f5e7'
  secondary-fixed-dim: '#6bd8cb'
  on-secondary-fixed: '#00201d'
  on-secondary-fixed-variant: '#005049'
  tertiary-fixed: '#ffd6fd'
  tertiary-fixed-dim: '#fbabff'
  on-tertiary-fixed: '#36003e'
  on-tertiary-fixed-variant: '#7c008e'
  background: '#fbf8ff'
  on-background: '#1a1b22'
  surface-variant: '#e3e1eb'
typography:
  display-lg:
    fontFamily: Geist
    fontSize: 48px
    fontWeight: '700'
    lineHeight: 56px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Geist
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 40px
    letterSpacing: -0.01em
  headline-md:
    fontFamily: Geist
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  headline-sm:
    fontFamily: Geist
    fontSize: 20px
    fontWeight: '500'
    lineHeight: 28px
  body-lg:
    fontFamily: Geist
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-md:
    fontFamily: Geist
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  data-mono:
    fontFamily: JetBrains Mono
    fontSize: 13px
    fontWeight: '500'
    lineHeight: 18px
  label-caps:
    fontFamily: Geist
    fontSize: 11px
    fontWeight: '700'
    lineHeight: 16px
    letterSpacing: 0.05em
  headline-lg-mobile:
    fontFamily: Geist
    fontSize: 28px
    fontWeight: '600'
    lineHeight: 36px
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  unit: 4px
  gutter: 16px
  margin-mobile: 16px
  margin-desktop: 32px
  container-max: 1440px
---

## Brand & Style

The design system is engineered for high-throughput genetic analysis, blending the sterile precision of a modern laboratory with the vibrant complexity of molecular biology. The aesthetic departs from the "dark mode" tech trope, instead utilizing a "Medical-White" foundation that prioritizes clarity, trust, and long-session legibility.

The style is **Corporate / Modern** with a **Tactile-Tech** edge. It treats data density as a feature rather than a hurdle, using hyper-organized layouts and microscopic detailing to evoke an environment of scientific rigor. The emotional response is one of empowered discovery—professional enough for clinical use, yet colorful enough to reflect the inherent "code of life" found in genomic sequences.

Key visual principles:
- **Chromatic Functionalism:** Colors are not decorative; they categorize data types and nucleotide clusters.
- **Instrumental Clarity:** UI elements should feel like physical laboratory equipment—precise, responsive, and durable.
- **Data-Density Harmony:** High information density is managed through a strict mathematical grid and subtle tonal layering.

## Colors

The palette is derived from the four DNA nucleotides and the iridescent qualities of protein crystallization. The background is a "Medical-White" (#F8FAFC), which provides a high-contrast canvas that reduces eye strain compared to pure white.

- **Deep Cobalt (Cytosine):** Used for primary structural elements, headers, and authoritative actions.
- **Bright Teal (Guanine):** Represents growth and stability; used for success states and primary data visualizations.
- **Soft Magenta (Thymine):** An analytical accent used for mutations, highlights, and secondary insights.
- **Amber (Adenine):** Used for warnings, kinetic energy, and active selections within a sequence.
- **Neutral Grays:** A cool-toned scale (Blue-Grays) used to differentiate UI layers without introducing visual heat.

Avoid pure black (#000000). Use Deep Cobalt mixed with Gray (#0F172A) for the darkest text to maintain a sophisticated, laboratory-grade appearance.

## Typography

Geist is the cornerstone of this design system, chosen for its grotesque-inspired precision and technical neutrality. It provides the legibility required for complex scientific nomenclature.

For raw genomic sequences and coordinate data, the system integrates **JetBrains Mono**. This ensures that nucleotide strings (A, T, C, G) are perfectly aligned, making pattern recognition easier for the researcher.

**Hierarchy Rules:**
- Use `label-caps` for table headers and metadata categories to create a clear visual distinction from dynamic data.
- Maintain tight tracking on larger headlines to emphasize the "engineered" feel of the interface.
- Body text should default to `body-md` to allow for high data density without compromising readability.

## Layout & Spacing

This design system utilizes a **Fixed-Fluid Hybrid Grid**. Main dashboard containers adhere to a 12-column grid on desktop, while data workbenches use a fluid model to maximize the horizontal space required for sequence alignment viewers.

**The 4px Rhythm:** All spacing (padding, margins, component heights) must be multiples of 4px. This microscopic grid ensures that even the densest data tables feel mathematically structured.

**Responsive Behavior:**
- **Desktop:** 12 columns, 32px margins, 16px gutters.
- **Tablet:** 8 columns, 24px margins, 16px gutters.
- **Mobile:** 4 columns, 16px margins, 12px gutters.

Large data visualizations should be contained within cards that can expand to "Full-Screen Focus Mode," stripping away secondary navigation to allow the researcher to immerse themselves in the data.

## Elevation & Depth

To maintain a clean, clinical look, this design system avoids heavy shadows. Instead, it uses **Tonal Layering** and **Low-Contrast Outlines** to define hierarchy.

- **Base Level:** The "Medical-White" foundation (#F8FAFC).
- **Surface Level:** Cards and primary containers use a pure white background (#FFFFFF) with a subtle 1px border in a light blue-gray (#E2E8F0).
- **Active Level:** Elements that require focus (active inputs, open modals) utilize a "Cyan-Tinted" ambient shadow—a very soft, diffused glow that mimics the backlight of a laboratory microscope.
- **Backdrop Blurs:** Use subtle blurs (8px - 12px) for overlays and side panels to maintain context of the underlying data while providing a focused interaction layer.

Depth is communicated through the "stacking" of borders rather than the "casting" of shadows.

## Shapes

The shape language is **Soft (0.25rem)**. This subtle rounding prevents the UI from feeling sharp and aggressive while maintaining a sense of modular, industrial design.

- **Standard Components:** 4px (0.25rem) corner radius for buttons, inputs, and small chips.
- **Containers:** 8px (0.5rem) for cards and main content areas to provide a clear frame for data.
- **Interactive States:** Use a transition to 0px (sharp) only for sequence selectors to imply "clipping" into a specific data point.
- **Nucleotide Tags:** Use a semi-pill shape (12px) for status indicators to make them easily glanceable against the more rectangular data grid.

## Components

### Buttons
Primary buttons use a **Deep Cobalt** fill with white text. Secondary buttons use a **Medical-White** fill with a 1px Blue-Gray border. Ghost buttons are reserved for low-priority actions in toolbars.

### Nucleotide Chips
Small, high-contrast badges used to identify DNA bases.
- **A:** Amber background, Dark Amber text.
- **T:** Magenta background, Dark Magenta text.
- **C:** Cobalt background, White text.
- **G:** Teal background, Dark Teal text.

### Data Tables
Tables are the heart of the system. Use alternating row highlights (Zebra-striping) in an ultra-faint gray (#F1F5F9). Headers are sticky with a 2px Deep Cobalt bottom border. Cells containing numeric data use **JetBrains Mono** for tabular alignment.

### Input Fields
Fields feature a "Micro-Label" that floats within the top border. On focus, the border shifts from Gray to **Bright Teal** with a faint 2px outer glow.

### Sequence Viewers
A custom component designed for scrolling through long strings of DNA. Bases should be displayed in a monospaced grid with 2px gaps. Hovering over a base should trigger a tooltip with protein structure metadata and quality scores.

### Analytical Cards
Used to house charts and heatmaps. Each card must include a "Technical Header" containing the data source, timestamp, and a "Full-Screen" icon.
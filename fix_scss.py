#!/usr/bin/env python3
"""Fix dashboard_modern.scss by adding missing SCSS variables"""

scss_variables = """// ============================================================================
// OSUS Dashboard - SCSS Variables & Design Tokens
// ============================================================================

// Color Palette - Primary & Accents
$primary-accent: #1e3a8a;      // Deep blue for primary actions
$secondary: #6366f1;           // Indigo for secondary elements
$success: #10b981;             // Green for success states
$warning: #f59e0b;             // Amber for warnings
$danger: #ef4444;              // Red for errors/danger
$info: #06b6d4;                // Cyan for informational

// Text Colors
$text-dark: #1f2937;           // Primary text color
$text-muted: #6b7280;          // Secondary/muted text
$text-light: #9ca3af;          // Lighter text for hints

// Background Colors
$bg-light: #f9fafb;            // Light background
$bg-lighter: #f3f4f6;          // Even lighter background
$white: #ffffff;               // Pure white

// Border & Dividers
$border: #e5e7eb;              // Standard border color
$border-light: #f3f4f6;        // Light border

// Shadows - Material Design inspired
$shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
$shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
$shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
$shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);

// Transitions
$transition-fast: all 0.15s ease-in-out;
$transition-base: all 0.3s ease-in-out;
$transition-smooth: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);

// Border Radius
$radius-sm: 6px;
$radius-md: 8px;
$radius-lg: 12px;
$radius-xl: 16px;

// Spacing (multipliers of 4px base)
$space-1: 4px;
$space-2: 8px;
$space-3: 12px;
$space-4: 16px;
$space-5: 20px;
$space-6: 24px;
$space-8: 32px;
$space-10: 40px;

"""

# Read current SCSS file
scss_file = '/var/odoo/osusproperties/extra-addons/odoo17_final.git-6880b7fcd4844/osus_sales_invoicing_dashboard/static/src/scss/dashboard_modern.scss'

try:
    with open(scss_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Prepend variables
    new_content = scss_variables + '\n' + content

    # Write back
    with open(scss_file, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print('✅ SCSS variables added to dashboard_modern.scss')
    print(f'📊 File size: {len(new_content):,} bytes')
    print(f'📈 Variables added: {scss_variables.count("$")} variables')
    
except Exception as e:
    print(f'❌ Error: {e}')
    exit(1)

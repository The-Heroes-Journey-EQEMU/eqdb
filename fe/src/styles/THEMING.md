# CSS Theming System

This document explains the CSS theming system implemented in the EQDB frontend application.

## Overview

The theming system is built around CSS custom properties (variables) that are defined in `base.css` and used throughout the application. This allows for easy theme switching and consistent styling across all components.

## File Structure

- `base.css` - Contains all CSS custom properties and theme definitions
- `globals.css` - Imports base.css and provides component-specific styles using the variables
- `THEMING.md` - This documentation file

## Theme Variables

### Color System

The color system is based on semantic naming and supports both light and dark themes:

#### Primary Colors
- `--primary` - Main brand color
- `--primary-foreground` - Text color on primary background
- `--secondary` - Secondary brand color
- `--secondary-foreground` - Text color on secondary background

#### Semantic Colors
- `--success` - Success/positive actions
- `--success-foreground` - Text on success background
- `--success-light` - Light success background
- `--warning` - Warning/caution actions
- `--warning-foreground` - Text on warning background
- `--warning-light` - Light warning background
- `--error` - Error/destructive actions
- `--error-foreground` - Text on error background
- `--error-light` - Light error background
- `--info` - Informational actions
- `--info-foreground` - Text on info background
- `--info-light` - Light info background

#### Background Colors
- `--background` - Main page background
- `--card` - Card component background
- `--card-foreground` - Text on card background
- `--popover` - Popover/dropdown background
- `--popover-foreground` - Text on popover background
- `--muted` - Muted/subsidiary background
- `--muted-foreground` - Text on muted background

#### Text Colors
- `--foreground` - Primary text color
- `--destructive` - Destructive action color
- `--destructive-foreground` - Text on destructive background

#### Border and Input Colors
- `--border` - Border color
- `--input` - Input field background
- `--ring` - Focus ring color

#### Gray Scale
- `--gray-50` through `--gray-900` - Gray scale for component compatibility

### Typography

#### Font Families
- `--font-sans` - Primary sans-serif font (Inter)
- `--font-serif` - Serif font (Merriweather)
- `--font-mono` - Monospace font (JetBrains Mono)

#### Font Sizes
- `--font-size-xs` - 0.75rem
- `--font-size-sm` - 0.875rem
- `--font-size-base` - 1rem
- `--font-size-lg` - 1.125rem
- `--font-size-xl` - 1.25rem
- `--font-size-2xl` - 1.5rem
- `--font-size-3xl` - 1.875rem

#### Font Weights
- `--font-weight-normal` - 400
- `--font-weight-medium` - 500
- `--font-weight-semibold` - 600
- `--font-weight-bold` - 700

#### Line Heights
- `--line-height-tight` - 1.25
- `--line-height-normal` - 1.5
- `--line-height-relaxed` - 1.75

### Spacing

- `--spacing-xs` - 0.25rem
- `--spacing-sm` - 0.5rem
- `--spacing-md` - 1rem
- `--spacing-lg` - 1.5rem
- `--spacing-xl` - 2rem
- `--spacing-2xl` - 3rem

### Border Radius

- `--radius-sm` - Small radius
- `--radius-md` - Medium radius
- `--radius-lg` - Large radius
- `--radius-xl` - Extra large radius
- `--radius-2xl` - 2xl radius
- `--radius-full` - Full radius (9999px)

### Shadows

- `--shadow-2xs` - Extra extra small shadow
- `--shadow-xs` - Extra small shadow
- `--shadow-sm` - Small shadow
- `--shadow` - Default shadow
- `--shadow-md` - Medium shadow
- `--shadow-lg` - Large shadow
- `--shadow-xl` - Extra large shadow
- `--shadow-2xl` - Extra extra large shadow

### Transitions

- `--transition-fast` - 150ms ease-in-out
- `--transition-normal` - 200ms ease-in-out
- `--transition-slow` - 300ms ease-in-out

### Z-Index

- `--z-dropdown` - 1000
- `--z-sticky` - 1020
- `--z-fixed` - 1030
- `--z-modal-backdrop` - 1040
- `--z-modal` - 1050
- `--z-popover` - 1060
- `--z-tooltip` - 1070
- `--z-toast` - 1080

### Letter Spacing

- `--tracking-tighter` - Tighter letter spacing
- `--tracking-tight` - Tight letter spacing
- `--tracking-normal` - Normal letter spacing
- `--tracking-wide` - Wide letter spacing
- `--tracking-wider` - Wider letter spacing
- `--tracking-widest` - Widest letter spacing

## Usage

### In CSS

```css
.my-component {
  background-color: var(--background);
  color: var(--foreground);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  padding: var(--spacing-md);
  font-family: var(--font-sans);
  font-size: var(--font-size-base);
  box-shadow: var(--shadow-sm);
}
```

### In React Components

```tsx
const MyComponent = () => {
  return (
    <div
      style={{
        backgroundColor: 'var(--background)',
        color: 'var(--foreground)',
        border: '1px solid var(--border)',
        borderRadius: 'var(--radius-md)',
        padding: 'var(--spacing-md)',
        fontFamily: 'var(--font-sans)',
        fontSize: 'var(--font-size-base)',
        boxShadow: 'var(--shadow-sm)'
      }}
    >
      Content
    </div>
  );
};
```

### With Tailwind CSS

The variables are also available through Tailwind's CSS variable system:

```tsx
<div className="bg-[var(--background)] text-[var(--foreground)] border-[var(--border)] rounded-[var(--radius-md)] p-[var(--spacing-md)] font-[var(--font-sans)] text-[var(--font-size-base)] shadow-[var(--shadow-sm)]">
  Content
</div>
```

## Theme Switching

To switch themes, simply add or remove the `.dark` class on the root element:

```javascript
// Enable dark theme
document.documentElement.classList.add('dark');

// Disable dark theme
document.documentElement.classList.remove('dark');
```

## Creating New Themes

To create a new theme:

1. Add a new CSS class (e.g., `.custom-theme`) in `base.css`
2. Define all the necessary variables within that class
3. Apply the class to the root element to activate the theme

Example:

```css
.custom-theme {
  --background: oklch(0.1 0.02 280);
  --foreground: oklch(0.9 0 0);
  --primary: oklch(0.6 0.2 280);
  /* ... other variables */
}
```

## Best Practices

1. **Always use semantic variable names** - Use `--primary` instead of `--blue-500`
2. **Don't hardcode colors** - Always reference variables
3. **Test in both light and dark themes** - Ensure all components work in both themes
4. **Use the provided spacing and typography scales** - Maintain consistency
5. **Document new variables** - Add new variables to this documentation

## Component Guidelines

When creating new components:

1. Use the provided CSS variables for all styling
2. Follow the established naming conventions
3. Ensure the component works in both light and dark themes
4. Use the appropriate semantic colors for different states
5. Test with different font sizes and spacing

## Migration Guide

To migrate existing components to use the theming system:

1. Replace hardcoded colors with CSS variables
2. Replace hardcoded spacing with spacing variables
3. Replace hardcoded typography with typography variables
4. Test in both light and dark themes
5. Update any component documentation

Example migration:

```css
/* Before */
.old-component {
  background-color: #ffffff;
  color: #000000;
  padding: 16px;
  border-radius: 8px;
}

/* After */
.new-component {
  background-color: var(--background);
  color: var(--foreground);
  padding: var(--spacing-md);
  border-radius: var(--radius-md);
}
``` 
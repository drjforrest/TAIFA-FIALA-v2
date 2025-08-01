# TAIFA-FIALA Theme Implementation Guide

## Overview
This guide shows you how to implement your new theme colors across your Next.js application. Your theme uses:

- **Primary**: Cyan (#06b6d4 - cyan-500)
- **Secondary**: Gray (#374151 - gray-700) 
- **Accent**: Purple (#3b0764 - purple-950)
- **Info**: Cyan Dark (#0e7490 - cyan-700)
- **Base**: Green (#f0fdf4 - green-50)

## 1. CSS Custom Properties (Already Done)

Your `globals.css` now includes all theme colors as CSS custom properties:

```css
:root {
  --color-primary: var(--color-cyan-500);     /* #06b6d4 */
  --color-secondary: var(--color-gray-700);   /* #374151 */
  --color-accent: var(--color-purple-950);    /* #3b0764 */
  --color-info: var(--color-cyan-700);        /* #0e7490 */
  --color-background: var(--color-green-50);  /* #f0fdf4 */
}
```

## 2. Implementation Methods

### Method 1: Inline Styles (Direct CSS Variables)

```tsx
// Primary button
<button
  style={{
    backgroundColor: "var(--color-primary)",
    color: "var(--color-primary-foreground)",
  }}
  onMouseEnter={(e) => {
    e.currentTarget.style.backgroundColor = "var(--color-primary-hover)";
  }}
  onMouseLeave={(e) => {
    e.currentTarget.style.backgroundColor = "var(--color-primary)";
  }}
>
  Primary Action
</button>

// Secondary elements
<div style={{ color: "var(--color-secondary)" }}>
  Secondary text
</div>

// Accent highlights
<span style={{ color: "var(--color-accent)" }}>
  Featured content
</span>
```

### Method 2: Tailwind CSS Classes

Update your `tailwind.config.js` to include theme colors:

```js
module.exports = {
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#06b6d4',
          hover: '#0891b2',
          foreground: '#ffffff',
        },
        secondary: {
          DEFAULT: '#374151',
          hover: '#1f2937',
          foreground: '#ffffff',
        },
        accent: {
          DEFAULT: '#3b0764',
          hover: '#581c87',
          foreground: '#ffffff',
        },
        info: {
          DEFAULT: '#0e7490',
          hover: '#155e75',
          foreground: '#ffffff',
        },
      },
    },
  },
}
```

Then use Tailwind classes:

```tsx
<button className="bg-primary text-primary-foreground hover:bg-primary-hover">
  Primary Button
</button>

<div className="text-secondary">
  Secondary text
</div>

<span className="text-accent">
  Accent text
</span>
```

### Method 3: Component Props with Theme Colors

```tsx
// Button component with theme variants
interface ButtonProps {
  variant?: 'primary' | 'secondary' | 'accent' | 'info';
  children: React.ReactNode;
}

const ThemedButton: React.FC<ButtonProps> = ({ variant = 'primary', children }) => {
  const getVariantStyles = () => {
    switch (variant) {
      case 'primary':
        return {
          backgroundColor: 'var(--color-primary)',
          color: 'var(--color-primary-foreground)',
        };
      case 'secondary':
        return {
          backgroundColor: 'var(--color-secondary)',
          color: 'var(--color-secondary-foreground)',
        };
      case 'accent':
        return {
          backgroundColor: 'var(--color-accent)',
          color: 'var(--color-accent-foreground)',
        };
      case 'info':
        return {
          backgroundColor: 'var(--color-info)',
          color: 'var(--color-info-foreground)',
        };
    }
  };

  return (
    <button style={getVariantStyles()}>
      {children}
    </button>
  );
};

// Usage
<ThemedButton variant="primary">Primary Action</ThemedButton>
<ThemedButton variant="accent">Featured Action</ThemedButton>
```

## 3. Practical Examples for Your Page.tsx

### Hero Section

```tsx
<section className="px-4 py-20">
  <div className="text-center">
    <h1 style={{ color: "var(--color-primary)" }}>
      TAIFA-FIALA
    </h1>
    <p className="text-muted-foreground">
      Your subtitle here
    </p>
    
    {/* Primary CTA */}
    <button
      style={{
        backgroundColor: "var(--color-primary)",
        color: "var(--color-primary-foreground)",
        padding: "12px 24px",
        borderRadius: "8px",
        border: "none",
        fontSize: "16px",
        fontWeight: "600",
      }}
    >
      Get Started
    </button>
  </div>
</section>
```

### Statistics Cards

```tsx
<div className="grid md:grid-cols-3 gap-6">
  {/* Primary stat */}
  <div
    style={{
      backgroundColor: "var(--color-primary)",
      color: "white",
      padding: "24px",
      borderRadius: "12px",
      textAlign: "center",
    }}
  >
    <div style={{ fontSize: "32px", fontWeight: "bold" }}>$130B+</div>
    <div style={{ opacity: 0.9 }}>Total Funding</div>
  </div>

  {/* Info stat */}
  <div
    style={{
      backgroundColor: "var(--color-info)",
      color: "white",
      padding: "24px",
      borderRadius: "12px",
      textAlign: "center",
    }}
  >
    <div style={{ fontSize: "32px", fontWeight: "bold" }}>54</div>
    <div style={{ opacity: 0.9 }}>Countries</div>
  </div>

  {/* Accent stat */}
  <div
    style={{
      backgroundColor: "var(--color-accent)",
      color: "white",
      padding: "24px",
      borderRadius: "12px",
      textAlign: "center",
    }}
  >
    <div style={{ fontSize: "32px", fontWeight: "bold" }}>1,200+</div>
    <div style={{ opacity: 0.9 }}>Innovations</div>
  </div>
</div>
```

### Alert/Info Boxes

```tsx
{/* Info alert */}
<div
  style={{
    backgroundColor: "rgba(14, 116, 144, 0.1)",
    borderLeft: "4px solid var(--color-info)",
    padding: "16px",
    borderRadius: "0 8px 8px 0",
    marginBottom: "24px",
  }}
>
  <div style={{ display: "flex", alignItems: "center" }}>
    <InfoIcon style={{ color: "var(--color-info)", marginRight: "12px" }} />
    <div>
      <p style={{ color: "var(--color-info)", fontWeight: "600" }}>
        Important Information
      </p>
      <p style={{ color: "var(--color-muted-foreground)" }}>
        Your message content here
      </p>
    </div>
  </div>
</div>

{/* Accent alert */}
<div
  style={{
    backgroundColor: "rgba(59, 7, 100, 0.1)",
    borderLeft: "4px solid var(--color-accent)",
    padding: "16px",
    borderRadius: "0 8px 8px 0",
  }}
>
  <p style={{ color: "var(--color-accent)", fontWeight: "600" }}>
    Featured Content
  </p>
</div>
```

### Navigation Links

```tsx
<nav>
  <a
    href="/research"
    style={{ color: "var(--color-primary)" }}
    onMouseEnter={(e) => {
      e.currentTarget.style.color = "var(--color-primary-hover)";
    }}
    onMouseLeave={(e) => {
      e.currentTarget.style.color = "var(--color-primary)";
    }}
  >
    Research
  </a>
  
  <a
    href="/community"
    style={{ color: "var(--color-info)" }}
  >
    Community
  </a>
  
  <a
    href="/about"
    style={{ color: "var(--color-secondary)" }}
  >
    About
  </a>
</nav>
```

### Gradient Backgrounds

```tsx
{/* Primary to Accent gradient */}
<section
  style={{
    background: `linear-gradient(135deg, var(--color-primary), var(--color-accent))`,
    color: "white",
    padding: "80px 20px",
    textAlign: "center",
  }}
>
  <h2>Call to Action Section</h2>
  <p>Your content here</p>
</section>

{/* Info to Secondary gradient */}
<div
  style={{
    background: `linear-gradient(90deg, var(--color-info), var(--color-secondary))`,
    padding: "40px",
    borderRadius: "12px",
  }}
>
  Content with gradient background
</div>
```

## 4. Best Practices

### Color Usage Guidelines

1. **Primary (Cyan)**: Use for main CTAs, primary navigation, key buttons
2. **Secondary (Gray)**: Use for secondary buttons, neutral content, supporting text
3. **Accent (Purple)**: Use sparingly for highlights, special features, important alerts
4. **Info (Cyan-700)**: Use for informational content, tips, secondary navigation
5. **Base (Green-50)**: Already set as background color in your CSS

### Accessibility Considerations

```tsx
{/* Ensure sufficient contrast */}
<button
  style={{
    backgroundColor: "var(--color-primary)",
    color: "var(--color-primary-foreground)", // White text for contrast
    border: "none",
    padding: "12px 24px",
  }}
  aria-label="Submit form"
>
  Submit
</button>

{/* Focus states */}
<button
  style={{
    backgroundColor: "var(--color-accent)",
    color: "white",
  }}
  onFocus={(e) => {
    e.currentTarget.style.outline = "2px solid var(--color-accent)";
    e.currentTarget.style.outlineOffset = "2px";
  }}
>
  Accessible Button
</button>
```

### Responsive Design

```tsx
{/* Mobile-first approach */}
<div
  style={{
    backgroundColor: "var(--color-primary)",
    padding: "16px",
    // Use CSS media queries in your stylesheet for responsive adjustments
  }}
  className="mobile:p-4 tablet:p-6 desktop:p-8"
>
  Responsive content
</div>
```

## 5. Quick Implementation Checklist

- [ ] Update hero section with primary color
- [ ] Style main CTAs with primary background
- [ ] Use secondary color for supporting elements
- [ ] Add accent color for highlights and special content
- [ ] Implement info color for informational elements
- [ ] Test color contrast for accessibility
- [ ] Add hover states for interactive elements
- [ ] Ensure consistent spacing and typography
- [ ] Test on mobile devices
- [ ] Verify dark mode compatibility

## 6. Common Patterns

### Card Components

```tsx
const ThemeCard = ({ title, children, variant = 'default' }) => {
  const getCardStyles = () => {
    switch (variant) {
      case 'primary':
        return {
          border: `2px solid var(--color-primary)`,
          backgroundColor: 'rgba(6, 182, 212, 0.05)',
        };
      case 'accent':
        return {
          border: `2px solid var(--color-accent)`,
          backgroundColor: 'rgba(59, 7, 100, 0.05)',
        };
      default:
        return {
          border: `1px solid var(--color-border)`,
          backgroundColor: 'var(--color-card)',
        };
    }
  };

  return (
    <div
      style={{
        ...getCardStyles(),
        borderRadius: '12px',
        padding: '24px',
        marginBottom: '16px',
      }}
    >
      <h3 style={{ color: 'var(--color-foreground)', marginBottom: '12px' }}>
        {title}
      </h3>
      {children}
    </div>
  );
};
```

### Status Indicators

```tsx
const StatusBadge = ({ status, children }) => {
  const getStatusColor = () => {
    switch (status) {
      case 'active':
        return 'var(--color-primary)';
      case 'pending':
        return 'var(--color-info)';
      case 'featured':
        return 'var(--color-accent)';
      default:
        return 'var(--color-secondary)';
    }
  };

  return (
    <span
      style={{
        backgroundColor: getStatusColor(),
        color: 'white',
        padding: '4px 12px',
        borderRadius: '16px',
        fontSize: '12px',
        fontWeight: '600',
      }}
    >
      {children}
    </span>
  );
};
```

Remember: Your CSS custom properties automatically handle light/dark mode switching, so these implementations will work in both themes!
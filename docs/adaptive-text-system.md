# Adaptive Text System for Gradient Backgrounds

## Overview

The TAIFA-FIALA adaptive text system automatically adjusts text colors based on the background section to maintain optimal contrast and readability across your gradient background design. As your background transitions from dark (Section 1) to light (Section 4), the text colors adapt accordingly.

## Background Gradient System

Your website uses a 4-section gradient system:

- **Section 1**: Darkest background (`--color-gray-800`) → Lightest text
- **Section 2**: Dark background (`--color-gray-700`) → Light text  
- **Section 3**: Medium background (`--color-gray-600`) → Medium text
- **Section 4**: Lightest background (`--color-gray-500`) → Darkest text
- **Footer**: Dark background (`--color-gray-800`) → Same as Section 1

## CSS Variables

### Background Colors
```css
--color-background-section-1: var(--color-gray-800);  /* Darkest */
--color-background-section-2: var(--color-gray-700);  /* Dark */
--color-background-section-3: var(--color-gray-600);  /* Medium */
--color-background-section-4: var(--color-gray-500);  /* Lightest */
```

### Text Colors
```css
/* Heading Colors */
--color-text-section-1: var(--color-gray-100);  /* Lightest text for darkest bg */
--color-text-section-2: var(--color-gray-200);  /* Light text for dark bg */
--color-text-section-3: var(--color-gray-300);  /* Medium light text */
--color-text-section-4: var(--color-gray-700);  /* Dark text for light bg */

/* Paragraph Colors */
--color-text-paragraph-section-1: var(--color-gray-300);  /* Light paragraph text */
--color-text-paragraph-section-2: var(--color-gray-300);  /* Light paragraph text */
--color-text-paragraph-section-3: var(--color-gray-600);  /* Medium paragraph text */
--color-text-paragraph-section-4: var(--color-gray-700);  /* Dark paragraph text */
```

## Usage Methods

### 1. React Components (Recommended)

Import and use the adaptive text components:

```tsx
import {
  Section1Text,
  Section2Text,
  Section3Text,
  Section4Text,
} from "@/components/ui/adaptive-text";

// Usage examples
<Section1Text as="h1" className="text-4xl font-bold">
  Your Heading
</Section1Text>

<Section1Text as="p" variant="paragraph" className="text-lg">
  Your paragraph text
</Section1Text>
```

**Props:**
- `as`: HTML element to render (`h1`, `h2`, `h3`, `p`, `span`, `div`, etc.)
- `variant`: `'heading'` (default) or `'paragraph'`
- `className`: Additional CSS classes
- `children`: Content to render

### 2. CSS Utility Classes

Use the provided utility classes directly:

```tsx
<h1 className="text-4xl font-bold adaptive-heading-1">
  Your Heading
</h1>

<p className="adaptive-paragraph-1">
  Your paragraph text
</p>
```

**Available Classes:**
- `adaptive-heading-1` through `adaptive-heading-4`
- `adaptive-paragraph-1` through `adaptive-paragraph-4`
- `text-section-1` through `text-section-4` (with `!important`)
- `text-paragraph-section-1` through `text-paragraph-section-4` (with `!important`)

### 3. CSS Variables (Direct)

Use the CSS variables directly in inline styles:

```tsx
<h1 style={{ color: "var(--color-text-section-1)" }}>
  Your Heading
</h1>

<p style={{ color: "var(--color-text-paragraph-section-1)" }}>
  Your paragraph text
</p>
```

### 4. useAdaptiveColors Hook

For programmatic access to colors:

```tsx
import { useAdaptiveColors } from "@/components/ui/adaptive-text";

const MyComponent = () => {
  const colors = useAdaptiveColors(2); // Section 2 colors
  
  return (
    <div>
      <h1 style={{ color: colors.heading }}>Heading</h1>
      <p style={{ color: colors.paragraph }}>Paragraph</p>
    </div>
  );
};
```

**Returns:**
```typescript
{
  heading: string;    // CSS variable for headings
  paragraph: string;  // CSS variable for paragraphs
  background: string; // CSS variable for background
}
```

## Footer Styling

The footer uses the same dark background as Section 1, so it uses the same text colors:

```tsx
<footer style={{ backgroundColor: "var(--color-background-section-1)" }}>
  <ul className="adaptive-paragraph-1">
    <li>Footer content</li>
  </ul>
</footer>
```

**Footer-specific classes:**
- `footer-heading`: Same as `adaptive-heading-1`
- `footer-text`: Same as `adaptive-paragraph-1`
- `footer-link`: With hover effects

## Section Layout Example

```tsx
export default function MyPage() {
  return (
    <div>
      {/* Section 1 - Hero (Darkest background) */}
      <section style={{ backgroundColor: "var(--color-background-section-1)" }}>
        <Section1Text as="h1" className="text-6xl font-bold">
          Hero Title
        </Section1Text>
        <Section1Text as="p" variant="paragraph" className="text-xl">
          Hero description with optimal contrast
        </Section1Text>
      </section>

      {/* Section 2 - Features (Dark background) */}
      <section style={{ backgroundColor: "var(--color-background-section-2)" }}>
        <Section2Text as="h2" className="text-4xl font-bold">
          Features
        </Section2Text>
        <Section2Text as="p" variant="paragraph">
          Feature descriptions
        </Section2Text>
      </section>

      {/* Section 3 - Content (Medium background) */}
      <section style={{ backgroundColor: "var(--color-background-section-3)" }}>
        <Section3Text as="h2" className="text-4xl font-bold">
          Content Section
        </Section3Text>
        <Section3Text as="p" variant="paragraph">
          Main content with medium contrast
        </Section3Text>
      </section>

      {/* Section 4 - CTA (Lightest background) */}
      <section style={{ backgroundColor: "var(--color-background-section-4)" }}>
        <Section4Text as="h2" className="text-4xl font-bold">
          Call to Action
        </Section4Text>
        <Section4Text as="p" variant="paragraph">
          CTA description with dark text on light background
        </Section4Text>
      </section>

      {/* Footer (Back to dark) */}
      <footer style={{ backgroundColor: "var(--color-background-section-1)" }}>
        <Section1Text as="p" variant="paragraph">
          Footer content
        </Section1Text>
      </footer>
    </div>
  );
}
```

## Cards and Components

Cards with white/light backgrounds maintain their original text colors since they're not part of the gradient:

```tsx
{/* This card keeps its original colors regardless of section */}
<div className="bg-white p-6 rounded-lg shadow-lg">
  <h3 className="text-xl font-bold text-gray-900">Card Title</h3>
  <p className="text-gray-700">Card content</p>
</div>

{/* Semi-transparent cards may need adjustment */}
<div className="bg-white/90 backdrop-blur p-6 rounded-lg">
  <h3 className="text-xl font-bold text-gray-900">Semi-transparent Card</h3>
  <p className="text-gray-700">Content</p>
</div>
```

## Best Practices

1. **Use React Components**: The `Section*Text` components are the cleanest approach
2. **Semantic Elements**: Always specify the correct HTML element with the `as` prop
3. **Consistent Hierarchy**: Use heading variants for headings, paragraph for body text
4. **Test Contrast**: Verify readability across all sections
5. **Card Content**: Don't apply adaptive colors to content inside white/light cards
6. **Footer Consistency**: Footer should match Section 1 styling

## Light Mode Considerations

The system currently focuses on dark backgrounds with light cards. For light mode, you may need to adjust the CSS variables in the `@media (prefers-color-scheme: light)` section.

## Troubleshooting

**Text not visible**: Check that you're using the correct section number for your background
**Poor contrast**: Verify the CSS variables are properly defined and the gradient is working
**Inconsistent colors**: Make sure you're not mixing approaches (e.g., using both adaptive classes and hardcoded colors)

## Demo

Visit `/adaptive-text-demo` to see all approaches in action across the full gradient.
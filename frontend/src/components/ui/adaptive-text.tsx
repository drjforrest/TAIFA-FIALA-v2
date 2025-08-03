import React from "react";

interface AdaptiveTextProps extends React.HTMLAttributes<HTMLElement> {
  section: 1 | 2 | 3 | 4;
  variant?: "heading" | "paragraph";
  className?: string;
  children: React.ReactNode;
  as?: React.ElementType;
}

/**
 * AdaptiveText component that automatically applies the correct text color
 * based on the section's gradient background (1-4, darkest to lightest)
 */
export function AdaptiveText({
  section,
  variant = "heading",
  className = "",
  children,
  as = "div",
  ...props
}: AdaptiveTextProps) {
  const Component = as as React.ElementType;

  const getColorVariable = () => {
    if (variant === "paragraph") {
      return `var(--color-text-paragraph-section-${section})`;
    }
    return `var(--color-text-section-${section})`;
  };

  return (
    <Component
      {...props}
      className={className}
      style={{ color: getColorVariable(), ...props.style }}
    >
      {children}
    </Component>
  );
}

// Convenience components for specific sections
export function Section1Text({
  variant = "heading",
  className = "",
  children,
  as = "div",
  ...props
}: Omit<AdaptiveTextProps, "section">) {
  return (
    <AdaptiveText
      section={1}
      variant={variant}
      className={className}
      as={as}
      {...props}
    >
      {children}
    </AdaptiveText>
  );
}

export function Section2Text({
  variant = "heading",
  className = "",
  children,
  as = "div",
  ...props
}: Omit<AdaptiveTextProps, "section">) {
  return (
    <AdaptiveText
      section={2}
      variant={variant}
      className={className}
      as={as}
      {...props}
    >
      {children}
    </AdaptiveText>
  );
}

export function Section3Text({
  variant = "heading",
  className = "",
  children,
  as = "div",
  ...props
}: Omit<AdaptiveTextProps, "section">) {
  return (
    <AdaptiveText
      section={3}
      variant={variant}
      className={className}
      as={as}
      {...props}
    >
      {children}
    </AdaptiveText>
  );
}

export function Section4Text({
  variant = "heading",
  className = "",
  children,
  as = "div",
  ...props
}: Omit<AdaptiveTextProps, "section">) {
  return (
    <AdaptiveText
      section={4}
      variant={variant}
      className={className}
      as={as}
      {...props}
    >
      {children}
    </AdaptiveText>
  );
}

// Hook for getting adaptive colors programmatically
export function useAdaptiveColors(section: 1 | 2 | 3 | 4) {
  return {
    heading: `var(--color-text-section-${section})`,
    paragraph: `var(--color-text-paragraph-section-${section})`,
    background: `var(--color-background-section-${section})`,
  };
}

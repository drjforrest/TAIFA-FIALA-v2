"use client";

import { HTMLAttributes, forwardRef } from "react";

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  variant?: "default" | "outlined" | "elevated";
  children: React.ReactNode;
}

const Card = forwardRef<HTMLDivElement, CardProps>(
  ({ variant = "default", className = "", children, style, ...props }, ref) => {
    const baseStyles = {
      borderRadius: "var(--radius-lg)",
      transition: "all 0.2s ease-in-out",
    };

    const getVariantStyles = () => {
      switch (variant) {
        case "outlined":
          return {
            backgroundColor: "var(--color-card)",
            color: "var(--color-card-foreground)",
            border: "1px solid var(--color-border)",
          };
        case "elevated":
          return {
            backgroundColor: "var(--color-card)",
            color: "var(--color-card-foreground)",
            boxShadow: "var(--shadow-md)",
          };
        case "default":
        default:
          return {
            backgroundColor: "var(--color-card)",
            color: "var(--color-card-foreground)",
            boxShadow: "var(--shadow-sm)",
          };
      }
    };

    const combinedStyles = {
      ...baseStyles,
      ...getVariantStyles(),
      ...style,
    };

    return (
      <div ref={ref} className={className} style={combinedStyles} {...props}>
        {children}
      </div>
    );
  },
);

Card.displayName = "Card";

interface CardHeaderProps extends HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
}

const CardHeader = forwardRef<HTMLDivElement, CardHeaderProps>(
  ({ className = "", children, style, ...props }, ref) => {
    const headerStyles = {
      padding: "var(--spacing-lg)",
      paddingBottom: "var(--spacing-md)",
      ...style,
    };

    return (
      <div ref={ref} className={className} style={headerStyles} {...props}>
        {children}
      </div>
    );
  },
);

CardHeader.displayName = "CardHeader";

interface CardContentProps extends HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
}

const CardContent = forwardRef<HTMLDivElement, CardContentProps>(
  ({ className = "", children, style, ...props }, ref) => {
    const contentStyles = {
      padding: "var(--spacing-lg)",
      paddingTop: "0",
      ...style,
    };

    return (
      <div ref={ref} className={className} style={contentStyles} {...props}>
        {children}
      </div>
    );
  },
);

CardContent.displayName = "CardContent";

interface CardTitleProps extends HTMLAttributes<HTMLHeadingElement> {
  children: React.ReactNode;
}

const CardTitle = forwardRef<HTMLHeadingElement, CardTitleProps>(
  ({ className = "", children, style, ...props }, ref) => {
    const titleStyles = {
      fontSize: "1.25rem",
      fontWeight: "600",
      lineHeight: "1.6",
      color: "var(--color-card-foreground)",
      marginBottom: "var(--spacing-sm)",
      ...style,
    };

    return (
      <h3 ref={ref} className={className} style={titleStyles} {...props}>
        {children}
      </h3>
    );
  },
);

CardTitle.displayName = "CardTitle";

interface CardDescriptionProps extends HTMLAttributes<HTMLParagraphElement> {
  children: React.ReactNode;
}

const CardDescription = forwardRef<HTMLParagraphElement, CardDescriptionProps>(
  ({ className = "", children, style, ...props }, ref) => {
    const descriptionStyles = {
      fontSize: "0.875rem",
      color: "var(--color-muted-foreground)",
      lineHeight: "1.5",
      ...style,
    };

    return (
      <p ref={ref} className={className} style={descriptionStyles} {...props}>
        {children}
      </p>
    );
  },
);

CardDescription.displayName = "CardDescription";

export default Card;
export { CardHeader, CardContent, CardTitle, CardDescription };

'use client';

import { ButtonHTMLAttributes, forwardRef } from 'react';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  children: React.ReactNode;
}

const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ variant = 'primary', size = 'md', className = '', children, style, onMouseEnter, onMouseLeave, ...props }, ref) => {
    const baseStyles = {
      fontWeight: '600',
      borderRadius: 'var(--radius-md)',
      transition: 'all 0.2s ease-in-out',
      cursor: 'pointer',
      border: 'none',
      display: 'inline-flex',
      alignItems: 'center',
      justifyContent: 'center',
      gap: 'var(--spacing-sm)',
    };

    const sizeStyles = {
      sm: {
        padding: 'var(--spacing-sm) var(--spacing-md)',
        fontSize: '0.875rem',
        height: '2rem',
      },
      md: {
        padding: 'var(--spacing-md) var(--spacing-lg)',
        fontSize: '1rem',
        height: '2.5rem',
      },
      lg: {
        padding: 'var(--spacing-lg) var(--spacing-xl)',
        fontSize: '1.125rem',
        height: '3rem',
      },
    };

    const getVariantStyles = (isHover = false) => {
      switch (variant) {
        case 'primary':
          return {
            backgroundColor: isHover ? 'var(--color-primary-hover)' : 'var(--color-primary)',
            color: 'var(--color-primary-foreground)',
          };
        case 'secondary':
          return {
            backgroundColor: isHover ? 'var(--color-secondary-hover)' : 'var(--color-secondary)',
            color: 'var(--color-secondary-foreground)',
          };
        case 'outline':
          return {
            backgroundColor: isHover ? 'var(--color-muted)' : 'transparent',
            color: 'var(--color-foreground)',
            border: '1px solid var(--color-border)',
          };
        case 'ghost':
          return {
            backgroundColor: isHover ? 'var(--color-muted)' : 'transparent',
            color: 'var(--color-foreground)',
          };
        default:
          return {};
      }
    };

    const handleMouseEnter = (e: React.MouseEvent<HTMLButtonElement>) => {
      const hoverStyles = getVariantStyles(true);
      Object.assign(e.currentTarget.style, hoverStyles);
      onMouseEnter?.(e);
    };

    const handleMouseLeave = (e: React.MouseEvent<HTMLButtonElement>) => {
      const normalStyles = getVariantStyles(false);
      Object.assign(e.currentTarget.style, normalStyles);
      onMouseLeave?.(e);
    };

    const combinedStyles = {
      ...baseStyles,
      ...sizeStyles[size],
      ...getVariantStyles(false),
      ...style,
    };

    return (
      <button
        ref={ref}
        className={className}
        style={combinedStyles}
        onMouseEnter={handleMouseEnter}
        onMouseLeave={handleMouseLeave}
        {...props}
      >
        {children}
      </button>
    );
  }
);

Button.displayName = 'Button';

export default Button;
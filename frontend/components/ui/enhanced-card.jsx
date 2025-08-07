import React from 'react';
// Simple className utility to replace cn function
const cn = (...classes) => classes.filter(Boolean).join(' ');

// Enhanced Card with gradient support and hover effects
export function EnhancedCard({ 
  className, 
  variant = 'default',
  hover = true,
  ...props 
}) {
  const variants = {
    default: 'bg-card border shadow-sm',
    gradient: 'bg-ai-gradient border-0 shadow-md',
    'gradient-subtle': 'bg-ai-gradient-subtle border-0 shadow-md',
    'gradient-header': 'bg-gradient-to-r from-ai-purple to-white border-0 shadow-md',
  };

  const hoverEffects = hover ? 'hover:shadow-lg hover:scale-[1.01] transition-all duration-200' : '';

  return (
    <div 
      className={cn(
        'rounded-md text-card-foreground p-6',
        variants[variant],
        hoverEffects,
        className
      )} 
      {...props} 
    />
  );
}

// Enhanced Card Header with gradient support
export function EnhancedCardHeader({ 
  className, 
  variant = 'default',
  ...props 
}) {
  const variants = {
    default: '',
    gradient: 'bg-ai-gradient rounded-t-md -m-6 mb-4 p-6',
    'gradient-subtle': 'bg-ai-gradient-subtle rounded-t-md -m-6 mb-4 p-6',
  };

  return (
    <div 
      className={cn(
        'flex flex-col space-y-1.5',
        variants[variant],
        className
      )} 
      {...props} 
    />
  );
}

// Enhanced Card Title with better typography
export function EnhancedCardTitle({ 
  className, 
  size = 'default',
  ...props 
}) {
  const sizes = {
    sm: 'text-lg font-semibold',
    default: 'text-xl font-semibold',
    lg: 'text-2xl font-semibold',
  };

  return (
    <h3 
      className={cn(
        'leading-none tracking-tight text-card-foreground',
        sizes[size],
        className
      )} 
      {...props} 
    />
  );
}

// Enhanced Card Description
export function EnhancedCardDescription({ className, ...props }) {
  return (
    <p 
      className={cn(
        'text-sm text-muted-foreground leading-relaxed', 
        className
      )} 
      {...props} 
    />
  );
}

// Enhanced Card Content with better spacing
export function EnhancedCardContent({ 
  className, 
  spacing = 'default',
  ...props 
}) {
  const spacings = {
    none: '',
    sm: 'pt-2',
    default: 'pt-4',
    lg: 'pt-6',
  };

  return (
    <div 
      className={cn(
        spacings[spacing],
        className
      )} 
      {...props} 
    />
  );
}

// Enhanced Card Footer
export function EnhancedCardFooter({ 
  className, 
  justify = 'start',
  ...props 
}) {
  const justifications = {
    start: 'justify-start',
    center: 'justify-center',
    end: 'justify-end',
    between: 'justify-between',
  };

  return (
    <div 
      className={cn(
        'flex items-center pt-4',
        justifications[justify],
        className
      )} 
      {...props} 
    />
  );
}

// Specialized gradient cards for specific use cases
export function GradientHeaderCard({ children, className, ...props }) {
  return (
    <EnhancedCard 
      variant="default" 
      className={cn('overflow-hidden', className)}
      {...props}
    >
      <EnhancedCardHeader variant="gradient">
        {children}
      </EnhancedCardHeader>
    </EnhancedCard>
  );
}

export function SubtleGradientCard({ children, className, ...props }) {
  return (
    <EnhancedCard 
      variant="gradient-subtle" 
      className={className}
      {...props}
    >
      {children}
    </EnhancedCard>
  );
}

// Export all components for easy importing
export {
  EnhancedCard as Card,
  EnhancedCardHeader as CardHeader,
  EnhancedCardTitle as CardTitle,
  EnhancedCardDescription as CardDescription,
  EnhancedCardContent as CardContent,
  EnhancedCardFooter as CardFooter,
};
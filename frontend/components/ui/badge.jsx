import React from 'react';
// Simple className utility to replace cn function
const cn = (...classes) => classes.filter(Boolean).join(' ');

export function Badge({ 
  children, 
  variant = 'default', 
  className,
  ...props 
}) {
  const variantClasses = {
    default: 'border-transparent bg-primary text-primary-foreground hover:bg-primary/80',
    secondary: 'border-transparent bg-secondary text-secondary-foreground hover:bg-secondary/80',
    destructive: 'border-transparent bg-destructive text-destructive-foreground hover:bg-destructive/80',
    outline: 'text-foreground',
    pro: 'border-transparent bg-ai-gradient text-white shadow-md',
    free: 'border-transparent bg-gray-100 text-gray-800'
  };

  return (
    <div
      className={cn(
        'inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2',
        variantClasses[variant],
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
}
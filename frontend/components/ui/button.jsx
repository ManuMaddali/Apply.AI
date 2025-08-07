import React from 'react';
// Simple className utility to replace cn function
const cn = (...classes) => classes.filter(Boolean).join(' ');

export function Button({ children, variant = 'default', size = 'default', className = '', ...props }) {
  const baseClasses = 'inline-flex items-center justify-center rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50';
  
  const variantClasses = {
    default: 'bg-primary text-primary-foreground hover:bg-primary/90',
    destructive: 'bg-destructive text-destructive-foreground hover:bg-destructive/90',
    outline: 'border border-input bg-background hover:bg-accent hover:text-accent-foreground',
    secondary: 'bg-secondary text-secondary-foreground hover:bg-secondary/80',
    ghost: 'hover:bg-accent hover:text-accent-foreground',
    link: 'text-primary underline-offset-4 hover:underline',
    ai: 'bg-ai-gradient text-white hover:shadow-lg hover:scale-105 transition-all duration-200'
  };

  const sizeClasses = {
    default: 'h-10 px-4 py-2',
    sm: 'h-9 rounded-md px-3',
    lg: 'h-11 rounded-md px-8',
    icon: 'h-10 w-10'
  };

  return (
    <button 
      className={cn(baseClasses, variantClasses[variant], sizeClasses[size], className)} 
      {...props}
    >
      {children}
    </button>
  );
} 
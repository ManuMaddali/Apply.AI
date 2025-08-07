import React from 'react';
import { motion } from 'framer-motion';

// Simple className utility to replace cn function
const cn = (...classes) => classes.filter(Boolean).join(' ');

export function Progress({ 
  value = 0, 
  max = 100, 
  className,
  showLabel = false,
  variant = 'default',
  ...props 
}) {
  const percentage = Math.min(Math.max((value / max) * 100, 0), 100);
  
  const variantClasses = {
    default: 'bg-ai-purple',
    success: 'bg-green-500',
    warning: 'bg-yellow-500',
    danger: 'bg-red-500'
  };

  return (
    <div className={cn('relative', className)} {...props}>
      <div className="w-full bg-secondary rounded-full h-2 overflow-hidden">
        <motion.div
          className={cn('h-full rounded-full', variantClasses[variant])}
          initial={{ width: 0 }}
          animate={{ width: `${percentage}%` }}
          transition={{ duration: 0.5, ease: 'easeOut' }}
        />
      </div>
      {showLabel && (
        <div className="flex justify-between text-sm text-muted-foreground mt-1">
          <span>{value}</span>
          <span>{max}</span>
        </div>
      )}
    </div>
  );
}

// Circular progress component for donut charts
export function CircularProgress({ 
  value = 0, 
  max = 100, 
  size = 120,
  strokeWidth = 8,
  className,
  children,
  ...props 
}) {
  const percentage = Math.min(Math.max((value / max) * 100, 0), 100);
  const radius = (size - strokeWidth) / 2;
  const circumference = radius * 2 * Math.PI;
  const strokeDasharray = circumference;
  const strokeDashoffset = circumference - (percentage / 100) * circumference;

  return (
    <div className={cn('relative inline-flex items-center justify-center', className)} {...props}>
      <svg
        width={size}
        height={size}
        className="transform -rotate-90"
      >
        {/* Background circle */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke="currentColor"
          strokeWidth={strokeWidth}
          fill="transparent"
          className="text-muted"
        />
        {/* Progress circle */}
        <motion.circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke="#A78BFA"
          strokeWidth={strokeWidth}
          fill="transparent"
          strokeLinecap="round"
          strokeDasharray={strokeDasharray}
          initial={{ strokeDashoffset: circumference }}
          animate={{ strokeDashoffset }}
          transition={{ duration: 1, ease: 'easeOut' }}
        />
      </svg>
      {children && (
        <div className="absolute inset-0 flex items-center justify-center">
          {children}
        </div>
      )}
    </div>
  );
}
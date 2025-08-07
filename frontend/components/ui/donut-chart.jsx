import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
// Simple className utility to replace cn function
const cn = (...classes) => classes.filter(Boolean).join(' ');

// DonutChart component for usage visualization
export function DonutChart({
  value = 0,
  max = 100,
  size = 120,
  strokeWidth = 8,
  className,
  showLabel = true,
  showPercentage = true,
  label = "Usage",
  color = "#A78BFA", // ai-purple
  backgroundColor = "#E5E7EB", // gray-200
  animated = true,
  duration = 1.5,
  ...props
}) {
  const [animatedValue, setAnimatedValue] = useState(0);
  const percentage = Math.min((value / max) * 100, 100);
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const strokeDasharray = circumference;
  const strokeDashoffset = circumference - (animatedValue / 100) * circumference;

  // Animate the value change
  useEffect(() => {
    if (animated) {
      const timer = setTimeout(() => {
        setAnimatedValue(percentage);
      }, 100);
      return () => clearTimeout(timer);
    } else {
      setAnimatedValue(percentage);
    }
  }, [percentage, animated]);

  return (
    <div 
      className={cn(
        'relative inline-flex items-center justify-center',
        className
      )}
      {...props}
    >
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
          stroke={backgroundColor}
          strokeWidth={strokeWidth}
          fill="transparent"
        />
        
        {/* Progress circle */}
        <motion.circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke={color}
          strokeWidth={strokeWidth}
          fill="transparent"
          strokeLinecap="round"
          strokeDasharray={strokeDasharray}
          initial={{ strokeDashoffset: circumference }}
          animate={{ 
            strokeDashoffset: animated ? strokeDashoffset : circumference - (percentage / 100) * circumference 
          }}
          transition={{ 
            duration: animated ? duration : 0,
            ease: "easeInOut"
          }}
        />
      </svg>
      
      {/* Center content */}
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        {showPercentage && (
          <motion.span
            className="text-lg font-bold text-gray-900"
            initial={{ opacity: 0, scale: 0.5 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: animated ? duration * 0.5 : 0, duration: 0.3 }}
          >
            {Math.round(percentage)}%
          </motion.span>
        )}
        {showLabel && (
          <motion.span
            className="text-xs text-gray-600 mt-1"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: animated ? duration * 0.7 : 0, duration: 0.3 }}
          >
            {label}
          </motion.span>
        )}
      </div>
    </div>
  );
}

// Usage-specific donut chart with hover effects
export function UsageDonutChart({
  used = 0,
  limit = 5,
  className,
  size = 80,
  strokeWidth = 6,
  showHoverDetails = true,
  resetDate,
  ...props
}) {
  const [isHovered, setIsHovered] = useState(false);
  const percentage = (used / limit) * 100;
  
  // Color based on usage percentage
  const getColor = () => {
    if (percentage >= 90) return "#EF4444"; // red-500
    if (percentage >= 70) return "#F59E0B"; // amber-500
    return "#A78BFA"; // ai-purple
  };

  const formatResetDate = (date) => {
    if (!date) return "Next week";
    return new Intl.DateTimeFormat('en-US', { 
      month: 'short', 
      day: 'numeric' 
    }).format(new Date(date));
  };

  return (
    <div 
      className={cn("relative", className)}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <DonutChart
        value={used}
        max={limit}
        size={size}
        strokeWidth={strokeWidth}
        color={getColor()}
        showLabel={false}
        showPercentage={false}
        {...props}
      />
      
      {/* Center content */}
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="text-sm font-bold text-gray-900">
          {used}/{limit}
        </span>
        <span className="text-xs text-gray-600">
          sessions
        </span>
      </div>

      {/* Hover tooltip */}
      {showHoverDetails && isHovered && (
        <motion.div
          className="absolute -top-16 left-1/2 transform -translate-x-1/2 bg-gray-900 text-white text-xs rounded-lg px-3 py-2 whitespace-nowrap z-10"
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: 10 }}
        >
          <div className="text-center">
            <div className="font-medium">{used} of {limit} sessions used</div>
            <div className="text-gray-300">Resets {formatResetDate(resetDate)}</div>
          </div>
          {/* Arrow */}
          <div className="absolute top-full left-1/2 transform -translate-x-1/2 w-0 h-0 border-l-4 border-r-4 border-t-4 border-transparent border-t-gray-900"></div>
        </motion.div>
      )}
    </div>
  );
}

// Compact usage ring for header/navigation
export function UsageRing({
  used = 0,
  limit = 5,
  size = 24,
  strokeWidth = 3,
  className,
  ...props
}) {
  const percentage = (used / limit) * 100;
  
  const getColor = () => {
    if (percentage >= 90) return "#EF4444";
    if (percentage >= 70) return "#F59E0B";
    return "#A78BFA";
  };

  return (
    <div className={cn("relative", className)}>
      <DonutChart
        value={used}
        max={limit}
        size={size}
        strokeWidth={strokeWidth}
        color={getColor()}
        backgroundColor="#E5E7EB"
        showLabel={false}
        showPercentage={false}
        animated={false}
        {...props}
      />
      
      {/* Small indicator dot */}
      <div className="absolute inset-0 flex items-center justify-center">
        <div 
          className="w-1.5 h-1.5 rounded-full"
          style={{ backgroundColor: getColor() }}
        />
      </div>
    </div>
  );
}

// Progress donut with custom content
export function ProgressDonut({
  children,
  value = 0,
  max = 100,
  size = 100,
  strokeWidth = 8,
  color = "#A78BFA",
  className,
  ...props
}) {
  return (
    <div className={cn("relative", className)}>
      <DonutChart
        value={value}
        max={max}
        size={size}
        strokeWidth={strokeWidth}
        color={color}
        showLabel={false}
        showPercentage={false}
        {...props}
      />
      
      {/* Custom center content */}
      <div className="absolute inset-0 flex items-center justify-center">
        {children}
      </div>
    </div>
  );
}

export default DonutChart;
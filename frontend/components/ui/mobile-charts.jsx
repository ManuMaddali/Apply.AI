/**
 * Mobile-Optimized Charts and Data Visualization Components
 * Provides touch-friendly, responsive charts optimized for mobile devices
 */

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  TrendingUp, 
  TrendingDown, 
  BarChart3, 
  PieChart, 
  Activity,
  Target,
  Zap,
  Info,
  Maximize2,
  Minimize2
} from 'lucide-react';
import { useMobileOptimizations } from '../../hooks/useMobileOptimizations';

/**
 * MobileProgressRing Component
 * Animated circular progress indicator optimized for mobile
 */
export function MobileProgressRing({
  value = 0,
  maxValue = 100,
  size = 120,
  strokeWidth = 8,
  color = '#3b82f6',
  backgroundColor = '#e5e7eb',
  showValue = true,
  label,
  animated = true,
  className = ''
}) {
  const { shouldReduceAnimations, animationDuration } = useMobileOptimizations();
  const [displayValue, setDisplayValue] = useState(0);
  
  const radius = (size - strokeWidth) / 2;
  const circumference = radius * 2 * Math.PI;
  const percentage = Math.min(value / maxValue, 1);
  const strokeDashoffset = circumference - (percentage * circumference);

  useEffect(() => {
    if (animated && !shouldReduceAnimations) {
      let start = 0;
      const duration = animationDuration * 1000;
      const startTime = Date.now();
      
      const animate = () => {
        const elapsed = Date.now() - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const easeOutQuart = 1 - Math.pow(1 - progress, 4);
        
        setDisplayValue(Math.round(value * easeOutQuart));
        
        if (progress < 1) {
          requestAnimationFrame(animate);
        }
      };
      
      requestAnimationFrame(animate);
    } else {
      setDisplayValue(value);
    }
  }, [value, animated, shouldReduceAnimations, animationDuration]);

  return (
    <div className={`relative inline-flex items-center justify-center ${className}`}>
      <svg
        width={size}
        height={size}
        className="transform -rotate-90"
        style={{ filter: 'drop-shadow(0 2px 4px rgba(0,0,0,0.1))' }}
      >
        {/* Background circle */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke={backgroundColor}
          strokeWidth={strokeWidth}
          fill="none"
        />
        
        {/* Progress circle */}
        <motion.circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke={color}
          strokeWidth={strokeWidth}
          fill="none"
          strokeLinecap="round"
          strokeDasharray={circumference}
          initial={{ strokeDashoffset: circumference }}
          animate={{ 
            strokeDashoffset: shouldReduceAnimations ? strokeDashoffset : circumference
          }}
          transition={{
            duration: shouldReduceAnimations ? 0 : animationDuration,
            ease: 'easeOut',
            delay: shouldReduceAnimations ? 0 : 0.2
          }}
          style={{
            strokeDashoffset: shouldReduceAnimations ? strokeDashoffset : undefined
          }}
        />
      </svg>
      
      {/* Center content */}
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        {showValue && (
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ delay: shouldReduceAnimations ? 0 : 0.5, duration: animationDuration }}
            className="text-center"
          >
            <div className="text-2xl font-bold" style={{ color }}>
              {displayValue}
            </div>
            {label && (
              <div className="text-xs text-gray-600 mt-1">
                {label}
              </div>
            )}
          </motion.div>
        )}
      </div>
    </div>
  );
}

/**
 * MobileBarChart Component
 * Touch-friendly horizontal bar chart for mobile devices
 */
export function MobileBarChart({
  data = [],
  maxValue,
  height = 200,
  showValues = true,
  showLabels = true,
  color = '#3b82f6',
  backgroundColor = '#f3f4f6',
  animated = true,
  onBarPress,
  className = ''
}) {
  const { shouldReduceAnimations, animationDuration, haptic } = useMobileOptimizations();
  const [selectedBar, setSelectedBar] = useState(null);
  
  const calculatedMaxValue = maxValue || Math.max(...data.map(d => d.value));
  const barHeight = Math.max(24, (height - (data.length - 1) * 8) / data.length);

  const handleBarPress = useCallback((item, index) => {
    haptic?.triggerHaptic('light');
    setSelectedBar(index);
    onBarPress?.(item, index);
    
    // Auto-deselect after 2 seconds
    setTimeout(() => setSelectedBar(null), 2000);
  }, [haptic, onBarPress]);

  return (
    <div className={`w-full ${className}`} style={{ height }}>
      <div className="space-y-2">
        {data.map((item, index) => {
          const percentage = (item.value / calculatedMaxValue) * 100;
          const isSelected = selectedBar === index;
          
          return (
            <motion.div
              key={item.label || index}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ 
                delay: shouldReduceAnimations ? 0 : index * 0.1,
                duration: animationDuration
              }}
              className="relative"
            >
              <div className="flex items-center gap-3">
                {/* Label */}
                {showLabels && (
                  <div className="w-20 text-sm text-gray-700 text-right flex-shrink-0">
                    {item.label}
                  </div>
                )}
                
                {/* Bar container */}
                <div className="flex-1 relative">
                  <div
                    className="w-full rounded-full"
                    style={{ 
                      height: barHeight,
                      backgroundColor 
                    }}
                  >
                    <motion.div
                      className={`
                        h-full rounded-full cursor-pointer transition-all duration-200
                        ${isSelected ? 'shadow-lg' : 'shadow-sm'}
                      `}
                      style={{ 
                        backgroundColor: Array.isArray(color) ? color[index % color.length] : color,
                        transform: isSelected ? 'scale(1.02)' : 'scale(1)'
                      }}
                      initial={{ width: 0 }}
                      animate={{ width: `${percentage}%` }}
                      transition={{
                        duration: shouldReduceAnimations ? 0 : animationDuration,
                        delay: shouldReduceAnimations ? 0 : index * 0.1,
                        ease: 'easeOut'
                      }}
                      onClick={() => handleBarPress(item, index)}
                      whileTap={{ scale: 0.98 }}
                    />
                  </div>
                  
                  {/* Value label */}
                  {showValues && (
                    <motion.div
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      transition={{ 
                        delay: shouldReduceAnimations ? 0 : (index * 0.1) + 0.3,
                        duration: animationDuration
                      }}
                      className="absolute right-2 top-1/2 transform -translate-y-1/2"
                    >
                      <span className="text-xs font-medium text-white bg-black bg-opacity-20 px-2 py-1 rounded">
                        {item.value}
                      </span>
                    </motion.div>
                  )}
                </div>
              </div>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}

/**
 * MobileDonutChart Component
 * Interactive donut chart optimized for touch interaction
 */
export function MobileDonutChart({
  data = [],
  size = 200,
  innerRadius = 0.6,
  colors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'],
  showLabels = true,
  showValues = true,
  showLegend = true,
  animated = true,
  onSegmentPress,
  className = ''
}) {
  const { shouldReduceAnimations, animationDuration, haptic } = useMobileOptimizations();
  const [selectedSegment, setSelectedSegment] = useState(null);
  const [hoveredSegment, setHoveredSegment] = useState(null);
  
  const total = data.reduce((sum, item) => sum + item.value, 0);
  const radius = size / 2;
  const innerRadiusPixels = radius * innerRadius;
  
  let cumulativePercentage = 0;
  const segments = data.map((item, index) => {
    const percentage = (item.value / total) * 100;
    const startAngle = (cumulativePercentage / 100) * 360;
    const endAngle = ((cumulativePercentage + percentage) / 100) * 360;
    
    cumulativePercentage += percentage;
    
    return {
      ...item,
      percentage,
      startAngle,
      endAngle,
      color: colors[index % colors.length]
    };
  });

  const createArcPath = (startAngle, endAngle, outerRadius, innerRadius) => {
    const startAngleRad = (startAngle - 90) * (Math.PI / 180);
    const endAngleRad = (endAngle - 90) * (Math.PI / 180);
    
    const x1 = radius + outerRadius * Math.cos(startAngleRad);
    const y1 = radius + outerRadius * Math.sin(startAngleRad);
    const x2 = radius + outerRadius * Math.cos(endAngleRad);
    const y2 = radius + outerRadius * Math.sin(endAngleRad);
    
    const x3 = radius + innerRadius * Math.cos(endAngleRad);
    const y3 = radius + innerRadius * Math.sin(endAngleRad);
    const x4 = radius + innerRadius * Math.cos(startAngleRad);
    const y4 = radius + innerRadius * Math.sin(startAngleRad);
    
    const largeArcFlag = endAngle - startAngle <= 180 ? '0' : '1';
    
    return [
      'M', x1, y1,
      'A', outerRadius, outerRadius, 0, largeArcFlag, 1, x2, y2,
      'L', x3, y3,
      'A', innerRadius, innerRadius, 0, largeArcFlag, 0, x4, y4,
      'Z'
    ].join(' ');
  };

  const handleSegmentPress = useCallback((segment, index) => {
    haptic?.triggerHaptic('light');
    setSelectedSegment(index === selectedSegment ? null : index);
    onSegmentPress?.(segment, index);
  }, [haptic, onSegmentPress, selectedSegment]);

  return (
    <div className={`flex flex-col items-center ${className}`}>
      <div className="relative">
        <svg width={size} height={size} className="drop-shadow-sm">
          {segments.map((segment, index) => {
            const isSelected = selectedSegment === index;
            const isHovered = hoveredSegment === index;
            const scale = isSelected ? 1.05 : isHovered ? 1.02 : 1;
            
            return (
              <motion.g key={index}>
                <motion.path
                  d={createArcPath(
                    segment.startAngle,
                    segment.endAngle,
                    radius - 10,
                    innerRadiusPixels
                  )}
                  fill={segment.color}
                  stroke="white"
                  strokeWidth="2"
                  className="cursor-pointer"
                  initial={{ opacity: 0, scale: 0 }}
                  animate={{ 
                    opacity: 1, 
                    scale: shouldReduceAnimations ? scale : 1
                  }}
                  transition={{
                    duration: shouldReduceAnimations ? 0 : animationDuration,
                    delay: shouldReduceAnimations ? 0 : index * 0.1,
                    ease: 'easeOut'
                  }}
                  whileTap={{ scale: 0.95 }}
                  style={{
                    transform: shouldReduceAnimations ? `scale(${scale})` : undefined,
                    transformOrigin: `${radius}px ${radius}px`
                  }}
                  onClick={() => handleSegmentPress(segment, index)}
                  onMouseEnter={() => setHoveredSegment(index)}
                  onMouseLeave={() => setHoveredSegment(null)}
                />
                
                {/* Segment labels */}
                {showLabels && segment.percentage > 5 && (
                  <motion.text
                    x={radius + (radius - innerRadiusPixels) / 2 * Math.cos(((segment.startAngle + segment.endAngle) / 2 - 90) * Math.PI / 180)}
                    y={radius + (radius - innerRadiusPixels) / 2 * Math.sin(((segment.startAngle + segment.endAngle) / 2 - 90) * Math.PI / 180)}
                    textAnchor="middle"
                    dominantBaseline="middle"
                    className="text-xs font-medium fill-white pointer-events-none"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{
                      delay: shouldReduceAnimations ? 0 : (index * 0.1) + 0.3,
                      duration: animationDuration
                    }}
                  >
                    {Math.round(segment.percentage)}%
                  </motion.text>
                )}
              </motion.g>
            );
          })}
        </svg>
        
        {/* Center content */}
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="text-center">
            <div className="text-2xl font-bold text-gray-900">{total}</div>
            <div className="text-sm text-gray-600">Total</div>
          </div>
        </div>
      </div>
      
      {/* Legend */}
      {showLegend && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ 
            delay: shouldReduceAnimations ? 0 : 0.5,
            duration: animationDuration
          }}
          className="mt-4 grid grid-cols-2 gap-2 w-full max-w-xs"
        >
          {segments.map((segment, index) => (
            <motion.div
              key={index}
              className={`
                flex items-center gap-2 p-2 rounded-lg cursor-pointer transition-all
                ${selectedSegment === index ? 'bg-gray-100 shadow-sm' : 'hover:bg-gray-50'}
              `}
              whileTap={{ scale: 0.98 }}
              onClick={() => handleSegmentPress(segment, index)}
            >
              <div
                className="w-3 h-3 rounded-full flex-shrink-0"
                style={{ backgroundColor: segment.color }}
              />
              <div className="flex-1 min-w-0">
                <div className="text-sm font-medium text-gray-900 truncate">
                  {segment.label}
                </div>
                {showValues && (
                  <div className="text-xs text-gray-600">
                    {segment.value} ({Math.round(segment.percentage)}%)
                  </div>
                )}
              </div>
            </motion.div>
          ))}
        </motion.div>
      )}
    </div>
  );
}

/**
 * MobileSparkline Component
 * Compact line chart for showing trends in small spaces
 */
export function MobileSparkline({
  data = [],
  width = 100,
  height = 30,
  color = '#3b82f6',
  strokeWidth = 2,
  showDots = false,
  showTrend = true,
  animated = true,
  className = ''
}) {
  const { shouldReduceAnimations, animationDuration } = useMobileOptimizations();
  
  if (data.length < 2) return null;
  
  const minValue = Math.min(...data);
  const maxValue = Math.max(...data);
  const range = maxValue - minValue || 1;
  
  const points = data.map((value, index) => {
    const x = (index / (data.length - 1)) * width;
    const y = height - ((value - minValue) / range) * height;
    return { x, y, value };
  });
  
  const pathData = points.reduce((path, point, index) => {
    const command = index === 0 ? 'M' : 'L';
    return `${path} ${command} ${point.x} ${point.y}`;
  }, '');
  
  const trend = data[data.length - 1] > data[0] ? 'up' : 'down';
  const trendPercentage = Math.abs(((data[data.length - 1] - data[0]) / data[0]) * 100);

  return (
    <div className={`flex items-center gap-2 ${className}`}>
      <svg width={width} height={height} className="overflow-visible">
        <motion.path
          d={pathData}
          fill="none"
          stroke={color}
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          strokeLinejoin="round"
          initial={{ pathLength: 0 }}
          animate={{ pathLength: 1 }}
          transition={{
            duration: shouldReduceAnimations ? 0 : animationDuration,
            ease: 'easeOut'
          }}
        />
        
        {showDots && points.map((point, index) => (
          <motion.circle
            key={index}
            cx={point.x}
            cy={point.y}
            r={2}
            fill={color}
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{
              delay: shouldReduceAnimations ? 0 : index * 0.05,
              duration: animationDuration
            }}
          />
        ))}
      </svg>
      
      {showTrend && (
        <div className="flex items-center gap-1">
          {trend === 'up' ? (
            <TrendingUp className="w-4 h-4 text-green-500" />
          ) : (
            <TrendingDown className="w-4 h-4 text-red-500" />
          )}
          <span className={`text-sm font-medium ${
            trend === 'up' ? 'text-green-600' : 'text-red-600'
          }`}>
            {trendPercentage.toFixed(1)}%
          </span>
        </div>
      )}
    </div>
  );
}

/**
 * MobileMetricCard Component
 * Compact card for displaying key metrics with optional charts
 */
export function MobileMetricCard({
  title,
  value,
  previousValue,
  unit = '',
  icon: Icon,
  color = '#3b82f6',
  trend,
  sparklineData,
  onClick,
  className = ''
}) {
  const { haptic } = useMobileOptimizations();
  
  const trendValue = previousValue ? ((value - previousValue) / previousValue) * 100 : 0;
  const trendDirection = trendValue > 0 ? 'up' : trendValue < 0 ? 'down' : 'neutral';
  
  const handleClick = useCallback(() => {
    haptic?.triggerHaptic('light');
    onClick?.();
  }, [haptic, onClick]);

  return (
    <motion.div
      className={`
        bg-white rounded-xl p-4 border border-gray-200 shadow-sm
        ${onClick ? 'cursor-pointer hover:shadow-md active:scale-98' : ''}
        ${className}
      `}
      whileTap={onClick ? { scale: 0.98 } : {}}
      onClick={handleClick}
    >
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-2">
          {Icon && (
            <div 
              className="p-2 rounded-lg"
              style={{ backgroundColor: `${color}20`, color }}
            >
              <Icon className="w-4 h-4" />
            </div>
          )}
          <div>
            <h3 className="text-sm font-medium text-gray-700">{title}</h3>
          </div>
        </div>
        
        {trendDirection !== 'neutral' && (
          <div className={`flex items-center gap-1 ${
            trendDirection === 'up' ? 'text-green-600' : 'text-red-600'
          }`}>
            {trendDirection === 'up' ? (
              <TrendingUp className="w-3 h-3" />
            ) : (
              <TrendingDown className="w-3 h-3" />
            )}
            <span className="text-xs font-medium">
              {Math.abs(trendValue).toFixed(1)}%
            </span>
          </div>
        )}
      </div>
      
      <div className="flex items-end justify-between">
        <div>
          <div className="text-2xl font-bold text-gray-900">
            {typeof value === 'number' ? value.toLocaleString() : value}
            {unit && <span className="text-lg text-gray-600 ml-1">{unit}</span>}
          </div>
          {previousValue && (
            <div className="text-xs text-gray-500">
              vs {previousValue.toLocaleString()}{unit} last period
            </div>
          )}
        </div>
        
        {sparklineData && sparklineData.length > 1 && (
          <MobileSparkline
            data={sparklineData}
            width={60}
            height={20}
            color={color}
            showTrend={false}
          />
        )}
      </div>
    </motion.div>
  );
}

/**
 * MobileStatsGrid Component
 * Responsive grid layout for metric cards
 */
export function MobileStatsGrid({
  metrics = [],
  columns = 2,
  gap = 4,
  className = ''
}) {
  return (
    <div 
      className={`grid gap-${gap} ${className}`}
      style={{
        gridTemplateColumns: `repeat(${columns}, 1fr)`
      }}
    >
      {metrics.map((metric, index) => (
        <MobileMetricCard
          key={metric.id || index}
          {...metric}
        />
      ))}
    </div>
  );
}

export {
  MobileProgressRing,
  MobileBarChart,
  MobileDonutChart,
  MobileSparkline,
  MobileMetricCard,
  MobileStatsGrid
};
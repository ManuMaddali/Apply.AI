import React from 'react';
import { motion } from 'framer-motion';
import { Zap } from 'lucide-react';
// Simple className utility to replace cn function
const cn = (...classes) => classes.filter(Boolean).join(' ');

// Animation variants for the lightning icon
const lightningVariants = {
  idle: { 
    scale: 1,
    opacity: 1,
  },
  pulse: { 
    scale: [1, 1.2, 1], 
    opacity: [1, 0.8, 1],
    transition: { 
      repeat: Infinity, 
      duration: 2,
      ease: "easeInOut"
    } 
  },
  glow: {
    scale: [1, 1.1, 1],
    filter: [
      "drop-shadow(0 0 0px #A78BFA)",
      "drop-shadow(0 0 8px #A78BFA)",
      "drop-shadow(0 0 0px #A78BFA)"
    ],
    transition: {
      repeat: Infinity,
      duration: 2.5,
      ease: "easeInOut"
    }
  },
  bounce: {
    y: [0, -4, 0],
    transition: {
      repeat: Infinity,
      duration: 1.5,
      ease: "easeInOut"
    }
  }
};

// Main Lightning Icon component
export function LightningIcon({ 
  className,
  size = 16,
  color = 'currentColor',
  animation = 'pulse',
  isActive = true,
  ...props 
}) {
  const MotionZap = motion(Zap);

  return (
    <MotionZap
      size={size}
      color={color}
      className={cn(
        'inline-block',
        animation === 'pulse' && 'text-ai-purple',
        animation === 'glow' && 'text-ai-purple',
        className
      )}
      variants={lightningVariants}
      animate={isActive ? animation : 'idle'}
      {...props}
    />
  );
}

// Specialized variants for different use cases
export function PulseLightningIcon({ className, ...props }) {
  return (
    <LightningIcon 
      animation="pulse"
      className={cn('text-ai-purple', className)}
      {...props}
    />
  );
}

export function GlowLightningIcon({ className, ...props }) {
  return (
    <LightningIcon 
      animation="glow"
      className={cn('text-ai-purple', className)}
      {...props}
    />
  );
}

export function BounceLightningIcon({ className, ...props }) {
  return (
    <LightningIcon 
      animation="bounce"
      className={cn('text-ai-purple', className)}
      {...props}
    />
  );
}

// AI Action Indicator - combines lightning with text
export function AIActionIndicator({ 
  children, 
  isActive = true, 
  className,
  iconSize = 16,
  ...props 
}) {
  return (
    <motion.div
      className={cn(
        'flex items-center gap-2',
        className
      )}
      initial={{ opacity: 0, x: -10 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.3 }}
      {...props}
    >
      <LightningIcon 
        size={iconSize}
        animation="pulse"
        isActive={isActive}
      />
      {children && (
        <span className="text-sm font-medium text-ai-purple">
          {children}
        </span>
      )}
    </motion.div>
  );
}

// Processing indicator with lightning
export function ProcessingIndicator({ 
  text = "Processing...", 
  className,
  ...props 
}) {
  return (
    <motion.div
      className={cn(
        'flex items-center gap-2 text-ai-purple',
        className
      )}
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      {...props}
    >
      <LightningIcon 
        size={20}
        animation="glow"
        isActive={true}
      />
      <motion.span
        className="text-sm font-medium"
        animate={{ opacity: [1, 0.5, 1] }}
        transition={{ repeat: Infinity, duration: 1.5 }}
      >
        {text}
      </motion.span>
    </motion.div>
  );
}

// Success indicator with lightning
export function SuccessIndicator({ 
  text = "Complete!", 
  className,
  showCheckmark = true,
  ...props 
}) {
  return (
    <motion.div
      className={cn(
        'flex items-center gap-2 text-green-600',
        className
      )}
      initial={{ opacity: 0, scale: 0.8 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.4, ease: "backOut" }}
      {...props}
    >
      <LightningIcon 
        size={16}
        animation="bounce"
        isActive={true}
        color="#16a34a"
      />
      {showCheckmark && (
        <motion.div
          className="w-4 h-4 bg-green-600 rounded-full flex items-center justify-center"
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ delay: 0.2, duration: 0.3 }}
        >
          <svg 
            className="w-2.5 h-2.5 text-white" 
            fill="none" 
            stroke="currentColor" 
            viewBox="0 0 24 24"
          >
            <path 
              strokeLinecap="round" 
              strokeLinejoin="round" 
              strokeWidth={3} 
              d="M5 13l4 4L19 7" 
            />
          </svg>
        </motion.div>
      )}
      <span className="text-sm font-medium">
        {text}
      </span>
    </motion.div>
  );
}

export default LightningIcon;
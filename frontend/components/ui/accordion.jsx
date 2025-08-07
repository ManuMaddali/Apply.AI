import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronDown } from 'lucide-react';
// Simple className utility to replace cn function
const cn = (...classes) => classes.filter(Boolean).join(' ');

export function Accordion({ children, type = 'single', collapsible = true, className, ...props }) {
  return (
    <div className={cn('space-y-2', className)} {...props}>
      {children}
    </div>
  );
}

export function AccordionItem({ children, value, className, ...props }) {
  return (
    <div className={cn('border rounded-lg', className)} {...props}>
      {children}
    </div>
  );
}

export function AccordionTrigger({ 
  children, 
  className, 
  isOpen, 
  onToggle,
  ...props 
}) {
  return (
    <button
      className={cn(
        'flex flex-1 items-center justify-between py-4 px-4 font-medium transition-all hover:bg-muted/50 text-left',
        className
      )}
      onClick={onToggle}
      {...props}
    >
      {children}
      <motion.div
        animate={{ rotate: isOpen ? 180 : 0 }}
        transition={{ duration: 0.2 }}
      >
        <ChevronDown className="h-4 w-4 shrink-0 transition-transform duration-200" />
      </motion.div>
    </button>
  );
}

export function AccordionContent({ 
  children, 
  className, 
  isOpen,
  ...props 
}) {
  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ height: 0, opacity: 0 }}
          animate={{ height: 'auto', opacity: 1 }}
          exit={{ height: 0, opacity: 0 }}
          transition={{ duration: 0.3, ease: 'easeInOut' }}
          className="overflow-hidden"
        >
          <div className={cn('pb-4 px-4 pt-0', className)} {...props}>
            {children}
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}

// Simple accordion hook for managing state
export function useAccordion(defaultOpen = false) {
  const [isOpen, setIsOpen] = useState(defaultOpen);
  
  const toggle = () => setIsOpen(!isOpen);
  
  return { isOpen, toggle };
}
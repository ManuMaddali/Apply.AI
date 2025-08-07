import React from 'react';
// Simple className utility to replace cn function
const cn = (...classes) => classes.filter(Boolean).join(' ');
import { 
  EnhancedCard, 
  EnhancedCardHeader, 
  EnhancedCardTitle, 
  EnhancedCardDescription, 
  EnhancedCardContent 
} from './enhanced-card';

/**
 * SectionCard - A standardized card component for section organization
 * 
 * This component provides consistent styling for all section cards in the app
 * with gradient headers, proper spacing, and shadows.
 */
export function SectionCard({ 
  title, 
  description, 
  children, 
  className, 
  headerClassName,
  contentClassName,
  icon,
  gradient = true,
  hover = true,
  ...props 
}) {
  return (
    <EnhancedCard 
      className={cn("overflow-hidden", className)} 
      hover={hover}
      {...props}
    >
      <EnhancedCardHeader 
        className={cn(
          gradient ? "bg-ai-gradient-subtle rounded-t-md -m-6 mb-4 p-6" : "",
          headerClassName
        )}
      >
        <div className="flex items-center gap-3">
          {icon && (
            <div className="flex-shrink-0">
              {icon}
            </div>
          )}
          <div>
            <EnhancedCardTitle>{title}</EnhancedCardTitle>
            {description && (
              <EnhancedCardDescription className="mt-1">
                {description}
              </EnhancedCardDescription>
            )}
          </div>
        </div>
      </EnhancedCardHeader>
      <EnhancedCardContent className={cn("pt-0", contentClassName)}>
        {children}
      </EnhancedCardContent>
    </EnhancedCard>
  );
}

/**
 * ResultSectionCard - A specialized card for displaying results
 * 
 * This component provides styling specific to result sections with
 * success indicators and download options.
 */
export function ResultSectionCard({
  title,
  description,
  children,
  status = 'default', // 'default', 'success', 'processing', 'error'
  ...props
}) {
  const statusIcons = {
    default: null,
    success: (
      <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
        <svg className="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
        </svg>
      </div>
    ),
    processing: (
      <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
        <svg className="w-5 h-5 text-blue-600 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
        </svg>
      </div>
    ),
    error: (
      <div className="w-8 h-8 bg-red-100 rounded-full flex items-center justify-center">
        <svg className="w-5 h-5 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
        </svg>
      </div>
    )
  };

  return (
    <SectionCard
      title={title}
      description={description}
      icon={statusIcons[status]}
      gradient={status !== 'success'}
      className={cn(
        status === 'success' && "border-green-200 bg-green-50",
        status === 'error' && "border-red-200 bg-red-50"
      )}
      {...props}
    >
      {children}
    </SectionCard>
  );
}

/**
 * SidebarCard - A specialized card for sidebar content
 * 
 * This component provides styling specific to sidebar sections with
 * compact design and subtle backgrounds.
 */
export function SidebarCard({
  title,
  description,
  children,
  icon,
  variant = 'default', // 'default', 'highlight', 'upgrade'
  ...props
}) {
  const variants = {
    default: "",
    highlight: "bg-blue-50 border-blue-100",
    upgrade: "bg-gradient-to-r from-blue-50 to-purple-50 border-purple-100"
  };

  return (
    <EnhancedCard
      className={cn(
        "overflow-hidden",
        variants[variant]
      )}
      {...props}
    >
      <EnhancedCardHeader>
        <div className="flex items-center gap-3">
          {icon && (
            <div className="flex-shrink-0">
              {icon}
            </div>
          )}
          <div>
            <EnhancedCardTitle>{title}</EnhancedCardTitle>
            {description && (
              <EnhancedCardDescription className="mt-1">
                {description}
              </EnhancedCardDescription>
            )}
          </div>
        </div>
      </EnhancedCardHeader>
      <EnhancedCardContent>
        {children}
      </EnhancedCardContent>
    </EnhancedCard>
  );
}
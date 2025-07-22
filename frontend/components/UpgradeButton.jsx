import React, { useState } from 'react';
import UpgradeModal from './UpgradeModal';

const UpgradeButton = ({ 
  feature = null,
  variant = 'primary',
  size = 'medium',
  children,
  className = '',
  ...props 
}) => {
  const [showUpgradeModal, setShowUpgradeModal] = useState(false);

  const getButtonStyles = () => {
    const baseStyles = 'font-semibold transition-all duration-200 rounded-lg flex items-center justify-center gap-2';
    
    const variants = {
      primary: 'bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white shadow-lg hover:shadow-xl',
      secondary: 'bg-white border-2 border-purple-600 text-purple-600 hover:bg-purple-50',
      outline: 'border border-purple-600 text-purple-600 hover:bg-purple-600 hover:text-white',
      ghost: 'text-purple-600 hover:bg-purple-100'
    };

    const sizes = {
      small: 'px-3 py-1.5 text-sm',
      medium: 'px-4 py-2 text-sm',
      large: 'px-6 py-3 text-base'
    };

    return `${baseStyles} ${variants[variant]} ${sizes[size]}`;
  };

  return (
    <>
      <button
        onClick={() => setShowUpgradeModal(true)}
        className={`${getButtonStyles()} ${className}`}
        {...props}
      >
        {children || (
          <>
            <span>🚀</span>
            <span>Upgrade to Pro</span>
          </>
        )}
      </button>

      <UpgradeModal
        isOpen={showUpgradeModal}
        onClose={() => setShowUpgradeModal(false)}
        feature={feature}
      />
    </>
  );
};

// Specific upgrade button variants
export const ProUpgradeButton = ({ className = '', ...props }) => (
  <UpgradeButton
    variant="primary"
    size="medium"
    className={className}
    {...props}
  >
    <span>🚀</span>
    <span>Upgrade to Pro - $9.99/month</span>
  </UpgradeButton>
);

export const CompactUpgradeButton = ({ className = '', ...props }) => (
  <UpgradeButton
    variant="secondary"
    size="small"
    className={className}
    {...props}
  >
    <span>Upgrade</span>
  </UpgradeButton>
);

export const FeatureUpgradeButton = ({ feature, featureName, className = '', ...props }) => (
  <UpgradeButton
    variant="outline"
    size="medium"
    feature={feature}
    className={className}
    {...props}
  >
    <span>🔓</span>
    <span>Unlock {featureName}</span>
  </UpgradeButton>
);

export default UpgradeButton;
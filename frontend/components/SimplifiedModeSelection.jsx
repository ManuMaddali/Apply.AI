/**
 * SimplifiedModeSelection Component
 * A simplified version of the mode selection interface that works with existing state management
 * Task 15.1: Integration component that bridges old and new UX patterns
 */

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Zap,
  Settings,
  Clock,
  Target,
  CheckCircle,
  ArrowRight,
  Crown,
  Star,
  TrendingUp,
  BarChart3,
  Sparkles
} from 'lucide-react';
import { Button } from './ui/button';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from './ui/card';
import UpgradePrompt from './UpgradePrompt';

function ModeCard({
  mode,
  title,
  subtitle,
  description,
  icon: Icon,
  features,
  estimatedTime,
  useCase,
  available,
  proOnly,
  recommended,
  onSelect,
  onUpgradeClick,
  isSelected,
  tier
}) {
  return (
    <motion.div
      whileHover={{ y: -4, scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      transition={{ duration: 0.2 }}
      className={`relative ${!available ? 'opacity-60' : ''}`}
    >
      <Card className={`h-full cursor-pointer transition-all duration-300 ${
        isSelected 
          ? 'ring-2 ring-blue-500 shadow-lg' 
          : 'hover:shadow-lg hover:border-blue-200'
      } ${
        recommended ? 'border-blue-300 bg-blue-50/50' : ''
      }`}>
        {recommended && (
          <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
            <div className="bg-blue-600 text-white px-3 py-1 rounded-full text-xs font-medium flex items-center gap-1">
              <Star className="h-3 w-3" />
              Recommended
            </div>
          </div>
        )}
        
        {proOnly && (
          <div className="absolute -top-2 -right-2">
            <div className="bg-gradient-to-r from-purple-600 to-blue-600 text-white p-2 rounded-full">
              <Crown className="h-4 w-4" />
            </div>
          </div>
        )}

        <CardHeader className="text-center pb-4">
          <div className={`mx-auto w-16 h-16 rounded-full flex items-center justify-center mb-4 ${
            mode === 'batch' 
              ? 'bg-blue-100 text-blue-600' 
              : 'bg-purple-100 text-purple-600'
          }`}>
            <Icon className="h-8 w-8" />
          </div>
          
          <CardTitle className="text-xl font-bold">{title}</CardTitle>
          <CardDescription className="text-sm text-gray-600 font-medium">
            {subtitle}
          </CardDescription>
          <p className="text-sm text-gray-500 mt-2">{description}</p>
        </CardHeader>

        <CardContent className="space-y-4">
          <div className="space-y-2">
            {features.map((feature, index) => (
              <div key={index} className="flex items-center gap-2 text-sm">
                <CheckCircle className="h-4 w-4 text-green-500 flex-shrink-0" />
                <span className={proOnly && !available ? 'text-gray-400' : 'text-gray-700'}>
                  {feature}
                </span>
              </div>
            ))}
          </div>

          <div className="pt-2 border-t border-gray-100">
            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-500">Estimated time:</span>
              <span className="font-medium text-gray-700">{estimatedTime}</span>
            </div>
            <div className="flex items-center justify-between text-sm mt-1">
              <span className="text-gray-500">Best for:</span>
              <span className="font-medium text-gray-700">{useCase}</span>
            </div>
          </div>
        </CardContent>

        <CardFooter>
          {available ? (
            <Button
              onClick={() => onSelect(mode)}
              className={`w-full ${
                mode === 'batch'
                  ? 'bg-blue-600 hover:bg-blue-700'
                  : 'bg-purple-600 hover:bg-purple-700'
              }`}
            >
              Select {title}
              <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
          ) : (
            <Button
              onClick={onUpgradeClick}
              variant="outline"
              className="w-full border-purple-200 text-purple-600 hover:bg-purple-50"
            >
              <Crown className="mr-2 h-4 w-4" />
              Upgrade for {title}
            </Button>
          )}
        </CardFooter>
      </Card>
    </motion.div>
  );
}

export default function SimplifiedModeSelection({
  onModeSelect,
  isProUser = false,
  weeklyUsage = 0,
  weeklyLimit = 5,
  onUpgradeClick
}) {
  const [selectedMode, setSelectedMode] = useState(null);
  const [showUpgradePrompt, setShowUpgradePrompt] = useState(false);

  const handleModeSelect = (mode) => {
    setSelectedMode(mode);
    onModeSelect(mode);
  };

  const handleUpgradeClick = () => {
    setShowUpgradePrompt(true);
    if (onUpgradeClick) onUpgradeClick();
  };

  const modes = [
    {
      mode: 'batch',
      title: 'Batch Mode',
      subtitle: 'Speed & Efficiency',
      description: 'Process multiple jobs quickly with global settings',
      icon: Zap,
      features: [
        'Process up to 10 jobs simultaneously',
        'Global enhancement settings',
        'Bulk download options',
        'Live progress tracking',
        'Aggregate analytics'
      ],
      estimatedTime: '30 seconds per job',
      useCase: 'Multiple applications',
      available: true,
      proOnly: false,
      recommended: !isProUser
    },
    {
      mode: 'precision',
      title: 'Precision Mode',
      subtitle: 'Control & Customization',
      description: 'Fine-tune each resume with job-specific optimizations',
      icon: Target,
      features: [
        'Job-by-job customization',
        'Real-time ATS score preview',
        'Advanced keyword optimization',
        'Section-by-section control',
        'Detailed analytics dashboard'
      ],
      estimatedTime: '2-3 minutes per job',
      useCase: 'High-priority roles',
      available: isProUser,
      proOnly: true,
      recommended: isProUser
    }
  ];

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      {/* Header Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="text-center mb-12 relative z-10"
      >
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          Choose Your Processing Mode
        </h1>
        <p className="text-xl text-gray-600 max-w-3xl mx-auto">
          Select the approach that best fits your application strategy. 
          Speed for volume, precision for priority roles.
        </p>
        
        {/* Usage Stats */}
        <div className="mt-6 flex items-center justify-center gap-6 text-sm text-gray-500">
          <div className="flex items-center gap-2">
            <BarChart3 className="h-4 w-4" />
            <span>Weekly Usage: {weeklyUsage}/{weeklyLimit}</span>
          </div>
          <div className="flex items-center gap-2">
            <Crown className="h-4 w-4" />
            <span>{isProUser ? 'Pro User' : 'Free User'}</span>
          </div>
        </div>
      </motion.div>

      {/* Mode Selection Cards */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.2 }}
        className="grid md:grid-cols-2 gap-8 mb-12"
      >
        {modes.map((mode) => (
          <ModeCard
            key={mode.mode}
            {...mode}
            onSelect={handleModeSelect}
            onUpgradeClick={handleUpgradeClick}
            isSelected={selectedMode === mode.mode}
          />
        ))}
      </motion.div>

      {/* Comparison Table */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.4 }}
        className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden"
      >
        <div className="px-6 py-4 bg-gray-50 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">Feature Comparison</h3>
        </div>
        
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Feature
                </th>
                <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Batch Mode
                </th>
                <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Precision Mode
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {[
                ['Processing Speed', 'Fast', 'Thorough'],
                ['Job Limit', '10 jobs', 'Unlimited'],
                ['Customization Level', 'Global settings', 'Per-job control'],
                ['ATS Score Preview', 'Post-processing', 'Real-time'],
                ['Analytics Dashboard', 'Basic', 'Advanced'],
                ['Tier Requirement', 'Free & Pro', 'Pro only']
              ].map(([feature, batch, precision], index) => (
                <tr key={index}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {feature}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700 text-center">
                    {batch}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700 text-center">
                    {precision}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </motion.div>

      {/* Upgrade Prompt Modal */}
      {showUpgradePrompt && (
        <UpgradePrompt
          isOpen={showUpgradePrompt}
          onClose={() => setShowUpgradePrompt(false)}
          feature="Precision Mode"
          description="Unlock advanced customization and analytics"
        />
      )}
    </div>
  );
}

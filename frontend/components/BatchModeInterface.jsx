/**
 * BatchModeInterface Component
 * Implements fast processing with global settings and live visualization
 * Handles tier-based limitations and batch results overview
 */

import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Zap,
  Settings,
  Clock,
  CheckCircle,
  AlertCircle,
  Play,
  Pause,
  Download,
  BarChart3,
  TrendingUp,
  Crown,
  Star,
  ArrowRight,
  RefreshCw,
  FileText,
  Target,
  Sparkles,
  Users,
  Award
} from 'lucide-react';
import { Button } from './ui/button';
import { EnhancedCard, EnhancedCardHeader, EnhancedCardTitle, EnhancedCardDescription, EnhancedCardContent, EnhancedCardFooter } from './ui/enhanced-card';
import { TierBadge } from './ui/tier-badge';
import { UpgradePrompt } from './UpgradePrompt';
import { useUserStore, useProcessingStore, useUIStore, useAnalyticsStore } from '../lib/store';
import { fadeInUp, staggerContainer, staggerItem, hoverLift, scaleIn } from '../lib/motion';




/**
 * TierBasedBatchLimitations Component
 * Subtask 4.4: Tier-based batch limitations with graceful handling
 */
function TierBasedBatchLimitations({
  jobCount,
  maxJobs,
  isProUser,
  weeklyUsage,
  weeklyLimit,
  onUpgradeClick,
  onBackToModeSelection,
  onStartProcessing,
  canProcess
}) {
  const [showUpgradeDetails, setShowUpgradeDetails] = useState(false);
  
  // Calculate usage statistics
  const usagePercentage = (weeklyUsage / weeklyLimit) * 100;
  const remainingUsage = weeklyLimit - weeklyUsage;
  const isNearLimit = usagePercentage >= 80;
  const isAtLimit = weeklyUsage >= weeklyLimit;
  
  // Determine limitation type
  const limitationType = (() => {
    if (isAtLimit) return 'usage-limit';
    if (jobCount > maxJobs) return 'job-limit';
    if (!isProUser && jobCount > 1) return 'tier-limit';
    return 'none';
  })();

  const getLimitationMessage = () => {
    switch (limitationType) {
      case 'usage-limit':
        return {
          type: 'error',
          title: 'Weekly Usage Limit Reached',
          message: `You've used all ${weeklyLimit} of your weekly processing credits. ${isProUser ? 'Your limit resets weekly.' : 'Upgrade to Pro for higher limits.'}`,
          action: isProUser ? null : 'upgrade'
        };
      case 'job-limit':
        return {
          type: 'warning',
          title: 'Job Limit Exceeded',
          message: isProUser 
            ? `Pro users can process up to ${maxJobs} jobs at once. Please reduce your selection to ${maxJobs} jobs.`
            : `You've selected ${jobCount} jobs, but free users can only process 1 job at a time.`,
          action: isProUser ? 'reduce' : 'upgrade'
        };
      case 'tier-limit':
        return {
          type: 'info',
          title: 'Batch Processing Available with Pro',
          message: `You've selected ${jobCount} jobs. Free users can process 1 job at a time, while Pro users can batch process up to 25 jobs.`,
          action: 'upgrade'
        };
      default:
        return null;
    }
  };

  const limitation = getLimitationMessage();

  const getEstimatedTime = () => {
    const jobsToProcess = Math.min(jobCount, maxJobs);
    const timePerJob = 45; // seconds
    const totalSeconds = jobsToProcess * timePerJob;
    const minutes = Math.floor(totalSeconds / 60);
    const seconds = totalSeconds % 60;
    return minutes > 0 ? `${minutes}:${seconds.toString().padStart(2, '0')} min` : `${seconds}s`;
  };

  const getProBenefits = () => [
    `Process up to 25 jobs simultaneously (vs 1 for free)`,
    `Advanced analytics and comparison tools`,
    `Priority processing with faster speeds`,
    `Bulk download options and export formats`,
    `Weekly limit of 100 jobs (vs 5 for free)`,
    `Cover letter generation included`
  ];

  return (
    <motion.div variants={staggerItem}>
      <EnhancedCard>
        <EnhancedCardHeader>
          <div className="flex items-center justify-between">
            <div>
              <EnhancedCardTitle className="flex items-center gap-2">
                <Users className="w-5 h-5" />
                Batch Configuration
                {!isProUser && (
                  <TierBadge tier="free" size="sm" />
                )}
              </EnhancedCardTitle>
              <EnhancedCardDescription>
                Processing {jobCount} job{jobCount !== 1 ? 's' : ''} with current settings
              </EnhancedCardDescription>
            </div>
            {!isProUser && (
              <Button
                variant="outline"
                size="sm"
                onClick={() => setShowUpgradeDetails(!showUpgradeDetails)}
                className="text-purple-600 border-purple-300 hover:bg-purple-50"
              >
                <Crown className="w-4 h-4 mr-2" />
                See Pro Benefits
              </Button>
            )}
          </div>
        </EnhancedCardHeader>
        
        <EnhancedCardContent>
          {/* Configuration Overview */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <div className="text-center p-4 bg-blue-50 rounded-lg">
              <div className="text-2xl font-bold text-blue-600">{jobCount}</div>
              <div className="text-sm text-gray-600">Jobs Selected</div>
            </div>
            <div className={`text-center p-4 rounded-lg ${
              limitationType === 'job-limit' ? 'bg-red-50' : 'bg-green-50'
            }`}>
              <div className={`text-2xl font-bold ${
                limitationType === 'job-limit' ? 'text-red-600' : 'text-green-600'
              }`}>
                {maxJobs}
              </div>
              <div className="text-sm text-gray-600">Max Allowed</div>
            </div>
            <div className="text-center p-4 bg-purple-50 rounded-lg">
              <div className="text-2xl font-bold text-purple-600">{getEstimatedTime()}</div>
              <div className="text-sm text-gray-600">Est. Time</div>
            </div>
            <div className={`text-center p-4 rounded-lg ${
              isNearLimit ? 'bg-amber-50' : isAtLimit ? 'bg-red-50' : 'bg-gray-50'
            }`}>
              <div className={`text-2xl font-bold ${
                isAtLimit ? 'text-red-600' : isNearLimit ? 'text-amber-600' : 'text-gray-600'
              }`}>
                {remainingUsage}
              </div>
              <div className="text-sm text-gray-600">Credits Left</div>
            </div>
          </div>

          {/* Usage Progress Bar */}
          <div className="mb-6">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-gray-700">Weekly Usage</span>
              <span className="text-sm text-gray-600">{weeklyUsage} / {weeklyLimit}</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <motion.div
                className={`h-2 rounded-full ${
                  isAtLimit ? 'bg-red-500' : 
                  isNearLimit ? 'bg-amber-500' : 
                  'bg-green-500'
                }`}
                initial={{ width: 0 }}
                animate={{ width: `${Math.min(usagePercentage, 100)}%` }}
                transition={{ duration: 0.8, delay: 0.2 }}
              />
            </div>
            {isNearLimit && !isAtLimit && (
              <p className="text-xs text-amber-600 mt-1">
                You're approaching your weekly limit. Consider upgrading for higher limits.
              </p>
            )}
          </div>

          {/* Limitation Messages */}
          {limitation && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className={`p-4 rounded-lg border mb-6 ${
                limitation.type === 'error' ? 'bg-red-50 border-red-200' :
                limitation.type === 'warning' ? 'bg-amber-50 border-amber-200' :
                'bg-blue-50 border-blue-200'
              }`}
            >
              <div className="flex items-start gap-3">
                <div className={`flex-shrink-0 mt-0.5 ${
                  limitation.type === 'error' ? 'text-red-600' :
                  limitation.type === 'warning' ? 'text-amber-600' :
                  'text-blue-600'
                }`}>
                  {limitation.type === 'error' ? (
                    <AlertCircle className="w-5 h-5" />
                  ) : limitation.type === 'warning' ? (
                    <AlertCircle className="w-5 h-5" />
                  ) : (
                    <Crown className="w-5 h-5" />
                  )}
                </div>
                <div className="flex-1">
                  <h4 className={`font-medium ${
                    limitation.type === 'error' ? 'text-red-800' :
                    limitation.type === 'warning' ? 'text-amber-800' :
                    'text-blue-800'
                  }`}>
                    {limitation.title}
                  </h4>
                  <p className={`text-sm mt-1 ${
                    limitation.type === 'error' ? 'text-red-700' :
                    limitation.type === 'warning' ? 'text-amber-700' :
                    'text-blue-700'
                  }`}>
                    {limitation.message}
                  </p>
                  
                  {limitation.action === 'upgrade' && (
                    <div className="mt-3 flex items-center gap-2">
                      <Button
                        size="sm"
                        onClick={onUpgradeClick}
                        className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white"
                      >
                        <Crown className="w-4 h-4 mr-2" />
                        Upgrade to Pro
                      </Button>
                      {!isProUser && (
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => setShowUpgradeDetails(!showUpgradeDetails)}
                          className="text-purple-600 border-purple-300"
                        >
                          See Benefits
                        </Button>
                      )}
                    </div>
                  )}
                </div>
              </div>
            </motion.div>
          )}

          {/* Pro Benefits Expansion */}
          <AnimatePresence>
            {showUpgradeDetails && !isProUser && (
              <motion.div
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: 'auto', opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                transition={{ duration: 0.3 }}
                className="mb-6 overflow-hidden"
              >
                <div className="bg-gradient-to-r from-purple-50 to-pink-50 rounded-lg p-6 border border-purple-200">
                  <div className="flex items-center gap-3 mb-4">
                    <div className="p-2 bg-purple-100 rounded-lg">
                      <Crown className="w-6 h-6 text-purple-600" />
                    </div>
                    <div>
                      <h3 className="text-lg font-semibold text-purple-900">Pro Features</h3>
                      <p className="text-sm text-purple-700">Unlock the full power of batch processing</p>
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    {getProBenefits().map((benefit, index) => (
                      <motion.div
                        key={index}
                        initial={{ opacity: 0, x: -10 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: index * 0.1 }}
                        className="flex items-start gap-2"
                      >
                        <CheckCircle className="w-4 h-4 text-purple-600 flex-shrink-0 mt-0.5" />
                        <span className="text-sm text-purple-800">{benefit}</span>
                      </motion.div>
                    ))}
                  </div>
                  
                  <div className="mt-4 pt-4 border-t border-purple-200">
                    <div className="flex items-center justify-between">
                      <div>
                        <div className="text-sm text-purple-700">
                          Process <strong>{jobCount} jobs</strong> instead of just 1
                        </div>
                        <div className="text-xs text-purple-600">
                          Save {Math.max(0, (jobCount - 1) * 45)} seconds with batch processing
                        </div>
                      </div>
                      <Button
                        onClick={onUpgradeClick}
                        className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white"
                      >
                        <Crown className="w-4 h-4 mr-2" />
                        Upgrade Now
                      </Button>
                    </div>
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Free User Single Job Processing */}
          {!isProUser && jobCount > 1 && limitationType !== 'usage-limit' && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-gray-50 rounded-lg p-4 border border-gray-200 mb-6"
            >
              <div className="flex items-center justify-between">
                <div>
                  <h4 className="font-medium text-gray-900">Process First Job Only</h4>
                  <p className="text-sm text-gray-600">
                    We'll process your first job now. Upgrade to Pro to process all {jobCount} jobs simultaneously.
                  </p>
                </div>
                <div className="text-right">
                  <div className="text-lg font-bold text-blue-600">1 job</div>
                  <div className="text-xs text-gray-500">~45 seconds</div>
                </div>
              </div>
            </motion.div>
          )}
        </EnhancedCardContent>
        
        <EnhancedCardFooter>
          <div className="flex items-center justify-between w-full">
            <Button
              variant="outline"
              onClick={onBackToModeSelection}
            >
              Back to Mode Selection
            </Button>
            
            <div className="flex items-center gap-3">
              {limitationType === 'job-limit' && isProUser && (
                <span className="text-sm text-gray-600">
                  Please reduce to {maxJobs} jobs
                </span>
              )}
              
              <Button
                onClick={onStartProcessing}
                disabled={!canProcess && limitationType !== 'tier-limit'}
                className={`${
                  canProcess || limitationType === 'tier-limit'
                    ? 'bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white'
                    : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                }`}
              >
                <Play className="w-4 h-4 mr-2" />
                {limitationType === 'tier-limit' 
                  ? 'Process First Job' 
                  : limitationType === 'usage-limit'
                  ? 'Limit Reached'
                  : 'Start Processing'
                }
              </Button>
            </div>
          </div>
        </EnhancedCardFooter>
      </EnhancedCard>
    </motion.div>
  );
}

/**
 * BatchResultsOverview Component
 * Subtask 4.3: Display aggregate analytics and batch download options
 */
function BatchResultsOverview({
  completedJobs = [],
  onDownloadAll,
  onDownloadIndividual,
  onStartNewBatch,
  onBackToSettings,
  isProUser = false
}) {
  const [selectedJobs, setSelectedJobs] = useState(new Set());
  const [showComparison, setShowComparison] = useState(false);
  const [sortBy, setSortBy] = useState('score'); // 'score', 'improvement', 'title'

  // Calculate aggregate analytics
  const aggregateAnalytics = useMemo(() => {
    if (completedJobs.length === 0) return null;

    const totalJobs = completedJobs.length;
    const avgOriginalScore = completedJobs.reduce((sum, job) => sum + (job.originalScore || 0), 0) / totalJobs;
    const avgFinalScore = completedJobs.reduce((sum, job) => sum + (job.finalScore || 0), 0) / totalJobs;
    const avgImprovement = avgFinalScore - avgOriginalScore;
    const totalKeywordsAdded = completedJobs.reduce((sum, job) => sum + (job.keywordsAdded || 0), 0);
    const totalProcessingTime = completedJobs.reduce((sum, job) => sum + (job.processingTime || 0), 0);

    return {
      totalJobs,
      avgOriginalScore: Math.round(avgOriginalScore),
      avgFinalScore: Math.round(avgFinalScore),
      avgImprovement: Math.round(avgImprovement),
      totalKeywordsAdded,
      avgProcessingTime: Math.round(totalProcessingTime / totalJobs),
      successRate: Math.round((completedJobs.filter(job => job.status === 'completed').length / totalJobs) * 100)
    };
  }, [completedJobs]);

  // Sort jobs based on selected criteria
  const sortedJobs = useMemo(() => {
    return [...completedJobs].sort((a, b) => {
      switch (sortBy) {
        case 'score':
          return (b.finalScore || 0) - (a.finalScore || 0);
        case 'improvement':
          return ((b.finalScore || 0) - (b.originalScore || 0)) - ((a.finalScore || 0) - (a.originalScore || 0));
        case 'title':
          return (a.jobTitle || '').localeCompare(b.jobTitle || '');
        default:
          return 0;
      }
    });
  }, [completedJobs, sortBy]);

  const handleJobSelection = (jobId) => {
    const newSelected = new Set(selectedJobs);
    if (newSelected.has(jobId)) {
      newSelected.delete(jobId);
    } else {
      newSelected.add(jobId);
    }
    setSelectedJobs(newSelected);
  };

  const handleSelectAll = () => {
    if (selectedJobs.size === completedJobs.length) {
      setSelectedJobs(new Set());
    } else {
      setSelectedJobs(new Set(completedJobs.map(job => job.id)));
    }
  };

  const getScoreColor = (score) => {
    if (score >= 90) return 'text-green-600 bg-green-100';
    if (score >= 75) return 'text-blue-600 bg-blue-100';
    if (score >= 60) return 'text-yellow-600 bg-yellow-100';
    return 'text-red-600 bg-red-100';
  };

  const getImprovementColor = (improvement) => {
    if (improvement >= 20) return 'text-green-600';
    if (improvement >= 10) return 'text-blue-600';
    if (improvement >= 5) return 'text-yellow-600';
    return 'text-gray-600';
  };

  return (
    <motion.div
      variants={staggerContainer}
      initial="hidden"
      animate="visible"
      className="space-y-6"
    >
      {/* Success Animation */}
      <motion.div
        variants={scaleIn}
        className="text-center py-8"
      >
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ delay: 0.2, type: 'spring', stiffness: 200 }}
          className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4"
        >
          <CheckCircle className="w-12 h-12 text-green-600" />
        </motion.div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Batch Processing Complete!</h2>
        <p className="text-gray-600">
          Successfully processed {completedJobs.length} job{completedJobs.length !== 1 ? 's' : ''} 
          {aggregateAnalytics && ` with an average improvement of +${aggregateAnalytics.avgImprovement} points`}
        </p>
      </motion.div>

      {/* Aggregate Analytics */}
      {aggregateAnalytics && (
        <motion.div variants={staggerItem}>
          <EnhancedCard>
            <EnhancedCardHeader>
              <EnhancedCardTitle className="flex items-center gap-2">
                <BarChart3 className="w-5 h-5" />
                Batch Analytics Overview
              </EnhancedCardTitle>
              <EnhancedCardDescription>
                Aggregate performance across all processed jobs
              </EnhancedCardDescription>
            </EnhancedCardHeader>
            <EnhancedCardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                <div className="text-center p-4 bg-blue-50 rounded-lg">
                  <div className="text-2xl font-bold text-blue-600">{aggregateAnalytics.avgFinalScore}</div>
                  <div className="text-sm text-gray-600">Avg Final Score</div>
                  <div className="text-xs text-gray-500">was {aggregateAnalytics.avgOriginalScore}</div>
                </div>
                <div className="text-center p-4 bg-green-50 rounded-lg">
                  <div className="text-2xl font-bold text-green-600">+{aggregateAnalytics.avgImprovement}</div>
                  <div className="text-sm text-gray-600">Avg Improvement</div>
                  <div className="text-xs text-gray-500">points gained</div>
                </div>
                <div className="text-center p-4 bg-purple-50 rounded-lg">
                  <div className="text-2xl font-bold text-purple-600">{aggregateAnalytics.totalKeywordsAdded}</div>
                  <div className="text-sm text-gray-600">Keywords Added</div>
                  <div className="text-xs text-gray-500">across all jobs</div>
                </div>
                <div className="text-center p-4 bg-orange-50 rounded-lg">
                  <div className="text-2xl font-bold text-orange-600">{aggregateAnalytics.successRate}%</div>
                  <div className="text-sm text-gray-600">Success Rate</div>
                  <div className="text-xs text-gray-500">{aggregateAnalytics.avgProcessingTime}s avg time</div>
                </div>
              </div>

              {/* Score Distribution Chart */}
              <div className="bg-gray-50 rounded-lg p-4">
                <h4 className="font-medium text-gray-900 mb-3">Score Distribution</h4>
                <div className="space-y-2">
                  {['90-100', '75-89', '60-74', '0-59'].map((range, index) => {
                    const [min, max] = range.split('-').map(Number);
                    const count = completedJobs.filter(job => {
                      const score = job.finalScore || 0;
                      return score >= min && (max ? score <= max : score >= min);
                    }).length;
                    const percentage = (count / completedJobs.length) * 100;
                    const colors = ['bg-green-500', 'bg-blue-500', 'bg-yellow-500', 'bg-red-500'];

                    return (
                      <div key={range} className="flex items-center gap-3">
                        <div className="w-16 text-sm text-gray-600">{range}</div>
                        <div className="flex-1 bg-gray-200 rounded-full h-2">
                          <motion.div
                            className={`h-2 rounded-full ${colors[index]}`}
                            initial={{ width: 0 }}
                            animate={{ width: `${percentage}%` }}
                            transition={{ delay: 0.5 + (index * 0.1), duration: 0.8 }}
                          />
                        </div>
                        <div className="w-12 text-sm text-gray-600 text-right">{count}</div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </EnhancedCardContent>
          </EnhancedCard>
        </motion.div>
      )}

      {/* Job Results Table */}
      <motion.div variants={staggerItem}>
        <EnhancedCard>
          <EnhancedCardHeader>
            <div className="flex items-center justify-between">
              <div>
                <EnhancedCardTitle className="flex items-center gap-2">
                  <FileText className="w-5 h-5" />
                  Individual Job Results
                </EnhancedCardTitle>
                <EnhancedCardDescription>
                  Detailed results for each processed job
                </EnhancedCardDescription>
              </div>
              <div className="flex items-center gap-2">
                <select
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value)}
                  className="text-sm border border-gray-300 rounded-md px-3 py-1"
                >
                  <option value="score">Sort by Final Score</option>
                  <option value="improvement">Sort by Improvement</option>
                  <option value="title">Sort by Job Title</option>
                </select>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setShowComparison(!showComparison)}
                >
                  {showComparison ? 'Hide' : 'Show'} Comparison
                </Button>
              </div>
            </div>
          </EnhancedCardHeader>
          <EnhancedCardContent>
            {/* Bulk Actions */}
            <div className="flex items-center justify-between mb-4 p-3 bg-gray-50 rounded-lg">
              <div className="flex items-center gap-3">
                <input
                  type="checkbox"
                  checked={selectedJobs.size === completedJobs.length}
                  onChange={handleSelectAll}
                  className="rounded border-gray-300"
                />
                <span className="text-sm text-gray-600">
                  {selectedJobs.size > 0 ? `${selectedJobs.size} selected` : 'Select all'}
                </span>
              </div>
              {selectedJobs.size > 0 && (
                <div className="flex items-center gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => onDownloadIndividual?.(Array.from(selectedJobs))}
                  >
                    <Download className="w-4 h-4 mr-2" />
                    Download Selected
                  </Button>
                </div>
              )}
            </div>

            {/* Jobs List */}
            <div className="space-y-3">
              {sortedJobs.map((job, index) => {
                const isSelected = selectedJobs.has(job.id);
                const improvement = (job.finalScore || 0) - (job.originalScore || 0);

                return (
                  <motion.div
                    key={job.id}
                    variants={staggerItem}
                    className={`
                      border border-gray-200 rounded-lg p-4 transition-all
                      ${isSelected ? 'border-blue-500 bg-blue-50' : 'hover:border-gray-300'}
                    `}
                  >
                    <div className="flex items-center gap-4">
                      <input
                        type="checkbox"
                        checked={isSelected}
                        onChange={() => handleJobSelection(job.id)}
                        className="rounded border-gray-300"
                      />
                      
                      <div className="flex-1 grid grid-cols-1 md:grid-cols-4 gap-4">
                        <div>
                          <h4 className="font-medium text-gray-900">{job.jobTitle}</h4>
                          <p className="text-sm text-gray-600">{job.jobCompany}</p>
                        </div>
                        
                        <div className="text-center">
                          <div className={`inline-flex items-center px-2 py-1 rounded-full text-sm font-medium ${getScoreColor(job.finalScore || 0)}`}>
                            {job.finalScore || 0}
                          </div>
                          <div className="text-xs text-gray-500 mt-1">Final Score</div>
                        </div>
                        
                        <div className="text-center">
                          <div className={`text-lg font-bold ${getImprovementColor(improvement)}`}>
                            +{improvement}
                          </div>
                          <div className="text-xs text-gray-500">Improvement</div>
                        </div>
                        
                        <div className="text-center">
                          <div className="text-sm text-gray-600">{job.keywordsAdded || 0} keywords</div>
                          <div className="text-xs text-gray-500">{job.processingTime || 0}s processing</div>
                        </div>
                      </div>
                      
                      <div className="flex items-center gap-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => onDownloadIndividual?.([job.id])}
                        >
                          <Download className="w-4 h-4" />
                        </Button>
                        {showComparison && (
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => {/* Show comparison modal */}}
                          >
                            Compare
                          </Button>
                        )}
                      </div>
                    </div>

                    {/* Expanded Details */}
                    {showComparison && (
                      <motion.div
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: 'auto', opacity: 1 }}
                        className="mt-4 pt-4 border-t border-gray-200"
                      >
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                          <div>
                            <h5 className="font-medium text-gray-900 mb-2">Before Enhancement</h5>
                            <div className="bg-red-50 p-3 rounded border border-red-200">
                              <div className="text-red-800">Score: {job.originalScore || 0}</div>
                              <div className="text-red-600 text-xs mt-1">
                                Missing keywords, weak language, formatting issues
                              </div>
                            </div>
                          </div>
                          <div>
                            <h5 className="font-medium text-gray-900 mb-2">After Enhancement</h5>
                            <div className="bg-green-50 p-3 rounded border border-green-200">
                              <div className="text-green-800">Score: {job.finalScore || 0}</div>
                              <div className="text-green-600 text-xs mt-1">
                                +{job.keywordsAdded || 0} keywords, enhanced language, optimized format
                              </div>
                            </div>
                          </div>
                        </div>
                      </motion.div>
                    )}
                  </motion.div>
                );
              })}
            </div>
          </EnhancedCardContent>
          <EnhancedCardFooter>
            <div className="flex items-center justify-between w-full">
              <div className="flex items-center gap-2">
                <Button
                  variant="outline"
                  onClick={onBackToSettings}
                >
                  Back to Settings
                </Button>
                <Button
                  variant="outline"
                  onClick={onStartNewBatch}
                >
                  Start New Batch
                </Button>
              </div>
              <Button
                onClick={onDownloadAll}
                className="bg-gradient-to-r from-green-600 to-blue-600 hover:from-green-700 hover:to-blue-700 text-white"
              >
                <Download className="w-4 h-4 mr-2" />
                Download All ({completedJobs.length})
              </Button>
            </div>
          </EnhancedCardFooter>
        </EnhancedCard>
      </motion.div>

      {/* Pro Features Highlight */}
      {isProUser && (
        <motion.div
          variants={fadeInUp}
          className="bg-gradient-to-r from-purple-50 to-pink-50 rounded-lg p-6 border border-purple-200"
        >
          <div className="flex items-center gap-3 mb-4">
            <Crown className="w-6 h-6 text-purple-600" />
            <h3 className="text-lg font-semibold text-purple-900">Pro Features Active</h3>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="flex items-center gap-2">
              <Award className="w-5 h-5 text-purple-600" />
              <span className="text-sm text-purple-700">Advanced Analytics</span>
            </div>
            <div className="flex items-center gap-2">
              <Download className="w-5 h-5 text-purple-600" />
              <span className="text-sm text-purple-700">Bulk Download Options</span>
            </div>
            <div className="flex items-center gap-2">
              <BarChart3 className="w-5 h-5 text-purple-600" />
              <span className="text-sm text-purple-700">Detailed Comparisons</span>
            </div>
          </div>
        </motion.div>
      )}

      {/* Free User Upgrade Prompt in Results */}
      {!isProUser && (
        <motion.div
          variants={fadeInUp}
          className="bg-gradient-to-r from-purple-50 to-pink-50 rounded-lg p-6 border border-purple-200"
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-purple-100 rounded-lg">
                <Crown className="w-6 h-6 text-purple-600" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-purple-900">Want to Process More Jobs?</h3>
                <p className="text-sm text-purple-700">
                  You processed 1 job successfully. Upgrade to Pro to process up to 25 jobs simultaneously.
                </p>
              </div>
            </div>
            <div className="text-right">
              <Button
                onClick={() => {
                  // This would trigger upgrade flow
                  console.log('Upgrade clicked from results');
                }}
                className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white"
              >
                <Crown className="w-4 h-4 mr-2" />
                Upgrade to Pro
              </Button>
              <div className="text-xs text-purple-600 mt-1">
                Process all your jobs at once
              </div>
            </div>
          </div>
          
          <div className="mt-4 pt-4 border-t border-purple-200">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="flex items-center gap-2">
                <Users className="w-4 h-4 text-purple-600" />
                <span className="text-sm text-purple-700">25 jobs per batch</span>
              </div>
              <div className="flex items-center gap-2">
                <BarChart3 className="w-4 h-4 text-purple-600" />
                <span className="text-sm text-purple-700">Advanced analytics</span>
              </div>
              <div className="flex items-center gap-2">
                <Download className="w-4 h-4 text-purple-600" />
                <span className="text-sm text-purple-700">Bulk downloads</span>
              </div>
            </div>
          </div>
        </motion.div>
      )}
    </motion.div>
  );
}

/**
 * LiveProcessingVisualization Component
 * Subtask 4.2: Job-by-job progress tracking with real-time updates
 */
function LiveProcessingVisualization({
  jobs = [],
  currentProgress = 0,
  onPause,
  onResume,
  onCancel,
  isPaused = false,
  estimatedTimeRemaining = 0
}) {
  const [expandedJobs, setExpandedJobs] = useState(new Set());
  const [processingStats, setProcessingStats] = useState({
    completed: 0,
    failed: 0,
    inProgress: 0,
    queued: 0
  });

  // Processing steps configuration
  const processingSteps = [
    { id: 'analyzing', name: 'Analyzing job requirements', icon: Target, duration: 2000 },
    { id: 'enhancing', name: 'Enhancing experience section', icon: Sparkles, duration: 4000 },
    { id: 'optimizing', name: 'Optimizing keywords', icon: TrendingUp, duration: 1500 },
    { id: 'generating', name: 'Generating final resume', icon: FileText, duration: 2500 }
  ];

  useEffect(() => {
    // Calculate processing statistics
    const stats = jobs.reduce((acc, job) => {
      switch (job.status) {
        case 'completed':
          acc.completed++;
          break;
        case 'failed':
          acc.failed++;
          break;
        case 'processing':
          acc.inProgress++;
          break;
        case 'queued':
          acc.queued++;
          break;
      }
      return acc;
    }, { completed: 0, failed: 0, inProgress: 0, queued: 0 });
    
    setProcessingStats(stats);
  }, [jobs]);

  const toggleJobExpansion = (jobId) => {
    const newExpanded = new Set(expandedJobs);
    if (newExpanded.has(jobId)) {
      newExpanded.delete(jobId);
    } else {
      newExpanded.add(jobId);
    }
    setExpandedJobs(newExpanded);
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return 'text-green-600 bg-green-100';
      case 'failed': return 'text-red-600 bg-red-100';
      case 'processing': return 'text-blue-600 bg-blue-100';
      case 'queued': return 'text-gray-600 bg-gray-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getStepStatus = (job, stepId) => {
    const currentStepIndex = processingSteps.findIndex(step => step.id === job.currentStep);
    const stepIndex = processingSteps.findIndex(step => step.id === stepId);
    
    if (job.status === 'completed') return 'completed';
    if (job.status === 'failed') return stepIndex <= currentStepIndex ? 'failed' : 'pending';
    if (stepIndex < currentStepIndex) return 'completed';
    if (stepIndex === currentStepIndex) return 'active';
    return 'pending';
  };

  return (
    <motion.div
      variants={staggerContainer}
      initial="hidden"
      animate="visible"
      className="space-y-6"
    >
      {/* Processing Overview */}
      <motion.div variants={staggerItem}>
        <EnhancedCard>
          <EnhancedCardHeader>
            <div className="flex items-center justify-between">
              <div>
                <EnhancedCardTitle className="flex items-center gap-2">
                  <BarChart3 className="w-5 h-5" />
                  Processing Overview
                </EnhancedCardTitle>
                <EnhancedCardDescription>
                  Real-time progress across all jobs
                </EnhancedCardDescription>
              </div>
              <div className="flex items-center gap-2">
                {!isPaused ? (
                  <Button variant="outline" size="sm" onClick={onPause}>
                    <Pause className="w-4 h-4 mr-2" />
                    Pause
                  </Button>
                ) : (
                  <Button variant="outline" size="sm" onClick={onResume}>
                    <Play className="w-4 h-4 mr-2" />
                    Resume
                  </Button>
                )}
                <Button variant="outline" size="sm" onClick={onCancel}>
                  Cancel
                </Button>
              </div>
            </div>
          </EnhancedCardHeader>
          <EnhancedCardContent>
            {/* Progress Bar */}
            <div className="mb-6">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-gray-700">Overall Progress</span>
                <span className="text-sm text-gray-600">{Math.round(currentProgress)}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-3">
                <motion.div
                  className="bg-gradient-to-r from-blue-500 to-purple-500 h-3 rounded-full"
                  initial={{ width: 0 }}
                  animate={{ width: `${currentProgress}%` }}
                  transition={{ duration: 0.5 }}
                />
              </div>
              <div className="flex items-center justify-between mt-2 text-sm text-gray-600">
                <span>{processingStats.completed + processingStats.failed} of {jobs.length} jobs processed</span>
                <span>Est. {formatTime(estimatedTimeRemaining)} remaining</span>
              </div>
            </div>

            {/* Statistics Grid */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center p-3 bg-green-50 rounded-lg">
                <div className="text-2xl font-bold text-green-600">{processingStats.completed}</div>
                <div className="text-sm text-gray-600">Completed</div>
              </div>
              <div className="text-center p-3 bg-blue-50 rounded-lg">
                <div className="text-2xl font-bold text-blue-600">{processingStats.inProgress}</div>
                <div className="text-sm text-gray-600">In Progress</div>
              </div>
              <div className="text-center p-3 bg-gray-50 rounded-lg">
                <div className="text-2xl font-bold text-gray-600">{processingStats.queued}</div>
                <div className="text-sm text-gray-600">Queued</div>
              </div>
              <div className="text-center p-3 bg-red-50 rounded-lg">
                <div className="text-2xl font-bold text-red-600">{processingStats.failed}</div>
                <div className="text-sm text-gray-600">Failed</div>
              </div>
            </div>
          </EnhancedCardContent>
        </EnhancedCard>
      </motion.div>

      {/* Job Processing Queue */}
      <motion.div variants={staggerItem}>
        <EnhancedCard>
          <EnhancedCardHeader>
            <EnhancedCardTitle className="flex items-center gap-2">
              <Clock className="w-5 h-5" />
              Processing Queue
            </EnhancedCardTitle>
            <EnhancedCardDescription>
              Detailed progress for each job
            </EnhancedCardDescription>
          </EnhancedCardHeader>
          <EnhancedCardContent>
            <div className="space-y-4">
              {jobs.map((job, index) => {
                const isExpanded = expandedJobs.has(job.id);
                const statusColor = getStatusColor(job.status);

                return (
                  <motion.div
                    key={job.id}
                    variants={staggerItem}
                    className="border border-gray-200 rounded-lg overflow-hidden"
                  >
                    {/* Job Header */}
                    <div
                      className="p-4 cursor-pointer hover:bg-gray-50 transition-colors"
                      onClick={() => toggleJobExpansion(job.id)}
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <div className="flex-shrink-0">
                            <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center text-sm font-medium text-blue-600">
                              {index + 1}
                            </div>
                          </div>
                          <div>
                            <h4 className="font-medium text-gray-900">{job.jobTitle}</h4>
                            <p className="text-sm text-gray-600">{job.jobCompany}</p>
                          </div>
                        </div>
                        
                        <div className="flex items-center gap-3">
                          <div className={`px-2 py-1 rounded-full text-xs font-medium ${statusColor}`}>
                            {job.status.charAt(0).toUpperCase() + job.status.slice(1)}
                          </div>
                          
                          {job.status === 'processing' && (
                            <div className="flex items-center gap-2">
                              <div className="w-4 h-4">
                                <motion.div
                                  className="w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full"
                                  animate={{ rotate: 360 }}
                                  transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                                />
                              </div>
                              <span className="text-sm text-gray-600">
                                {formatTime(job.timeRemaining || 0)}
                              </span>
                            </div>
                          )}
                          
                          {job.status === 'completed' && (
                            <div className="flex items-center gap-2 text-green-600">
                              <CheckCircle className="w-4 h-4" />
                              <span className="text-sm">{formatTime(job.actualTime || 0)}</span>
                            </div>
                          )}
                          
                          <motion.div
                            animate={{ rotate: isExpanded ? 180 : 0 }}
                            transition={{ duration: 0.2 }}
                          >
                            <ArrowRight className="w-4 h-4 text-gray-400" />
                          </motion.div>
                        </div>
                      </div>
                      
                      {/* Job Progress Bar */}
                      {job.status === 'processing' && (
                        <div className="mt-3">
                          <div className="w-full bg-gray-200 rounded-full h-2">
                            <motion.div
                              className="bg-blue-500 h-2 rounded-full"
                              initial={{ width: 0 }}
                              animate={{ width: `${job.progress || 0}%` }}
                              transition={{ duration: 0.3 }}
                            />
                          </div>
                        </div>
                      )}
                    </div>

                    {/* Expanded Job Details */}
                    <AnimatePresence>
                      {isExpanded && (
                        <motion.div
                          initial={{ height: 0, opacity: 0 }}
                          animate={{ height: 'auto', opacity: 1 }}
                          exit={{ height: 0, opacity: 0 }}
                          transition={{ duration: 0.3 }}
                          className="border-t border-gray-200 bg-gray-50"
                        >
                          <div className="p-4">
                            <h5 className="font-medium text-gray-900 mb-3">Processing Steps</h5>
                            <div className="space-y-3">
                              {processingSteps.map((step, stepIndex) => {
                                const StepIcon = step.icon;
                                const stepStatus = getStepStatus(job, step.id);
                                
                                return (
                                  <div key={step.id} className="flex items-center gap-3">
                                    <div className={`
                                      w-8 h-8 rounded-full flex items-center justify-center
                                      ${stepStatus === 'completed' ? 'bg-green-100 text-green-600' :
                                        stepStatus === 'active' ? 'bg-blue-100 text-blue-600' :
                                        stepStatus === 'failed' ? 'bg-red-100 text-red-600' :
                                        'bg-gray-100 text-gray-400'}
                                    `}>
                                      {stepStatus === 'completed' ? (
                                        <CheckCircle className="w-4 h-4" />
                                      ) : stepStatus === 'active' ? (
                                        <motion.div
                                          animate={{ rotate: 360 }}
                                          transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                                        >
                                          <RefreshCw className="w-4 h-4" />
                                        </motion.div>
                                      ) : stepStatus === 'failed' ? (
                                        <AlertCircle className="w-4 h-4" />
                                      ) : (
                                        <StepIcon className="w-4 h-4" />
                                      )}
                                    </div>
                                    
                                    <div className="flex-1">
                                      <div className="text-sm font-medium text-gray-900">{step.name}</div>
                                      {stepStatus === 'active' && (
                                        <div className="text-xs text-blue-600">Processing...</div>
                                      )}
                                      {stepStatus === 'completed' && job.stepDetails?.[step.id] && (
                                        <div className="text-xs text-gray-600">{job.stepDetails[step.id]}</div>
                                      )}
                                    </div>
                                    
                                    {stepStatus === 'completed' && job.stepTimes?.[step.id] && (
                                      <div className="text-xs text-gray-500">
                                        {(job.stepTimes[step.id] / 1000).toFixed(1)}s
                                      </div>
                                    )}
                                  </div>
                                );
                              })}
                            </div>
                          </div>
                        </motion.div>
                      )}
                    </AnimatePresence>
                  </motion.div>
                );
              })}
            </div>
          </EnhancedCardContent>
        </EnhancedCard>
      </motion.div>

      {/* Encouraging Messages */}
      {processingStats.inProgress > 0 && (
        <motion.div
          variants={fadeInUp}
          className="text-center p-4 bg-blue-50 rounded-lg border border-blue-200"
        >
          <div className="flex items-center justify-center gap-2 text-blue-700">
            <Sparkles className="w-5 h-5" />
            <span className="font-medium">
              {estimatedTimeRemaining > 60 
                ? "Great things take time! We're optimizing your resumes for maximum impact."
                : "Almost done! Your enhanced resumes will be ready shortly."
              }
            </span>
          </div>
        </motion.div>
      )}

      {/* Free User Upgrade Context During Processing */}
      {!isProUser && jobs.length === 1 && processingStats.inProgress > 0 && (
        <motion.div
          variants={fadeInUp}
          className="bg-gradient-to-r from-purple-50 to-pink-50 rounded-lg p-4 border border-purple-200"
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Crown className="w-5 h-5 text-purple-600" />
              <div>
                <h4 className="font-medium text-purple-900">Processing 1 of your jobs</h4>
                <p className="text-sm text-purple-700">
                  Upgrade to Pro to process all your jobs simultaneously and save time
                </p>
              </div>
            </div>
            <Button
              variant="outline"
              size="sm"
              className="text-purple-600 border-purple-300 hover:bg-purple-100"
              onClick={() => {
                // This would trigger upgrade flow
                console.log('Upgrade clicked during processing');
              }}
            >
              <Crown className="w-4 h-4 mr-2" />
              Upgrade
            </Button>
          </div>
        </motion.div>
      )}
    </motion.div>
  );
}

/**
 * Main BatchModeInterface Component
 * Entry point for batch mode processing
 */
export function BatchModeInterface({
  resumeData,
  jobUrls = [],
  onProcessingStart,
  onProcessingComplete,
  onBackToModeSelection,
  className = ''
}) {
  const { user, tier, weeklyUsage, weeklyLimit } = useUserStore();
  const { batchSettings, updateBatchSettings, activeJobs, currentProgress, isProcessing } = useProcessingStore();
  const { updateProcessingUI } = useUIStore();
  
  const [currentStep, setCurrentStep] = useState('settings'); // 'settings', 'processing', 'results'
  const [showUpgradePrompt, setShowUpgradePrompt] = useState(false);
  const [processingJobs, setProcessingJobs] = useState([]);
  const [isPaused, setIsPaused] = useState(false);
  const [estimatedTimeRemaining, setEstimatedTimeRemaining] = useState(0);

  const isProUser = tier === 'pro';
  const jobCount = jobUrls.length;
  const maxJobs = isProUser ? 25 : 1;
  const canProcess = jobCount <= maxJobs && weeklyUsage < weeklyLimit;

  const handleSettingsChange = useCallback((newSettings) => {
    updateBatchSettings(newSettings);
  }, [updateBatchSettings]);

  const handleStartProcessing = useCallback(() => {
    // Check usage limits first
    if (weeklyUsage >= weeklyLimit) {
      setShowUpgradePrompt(true);
      return;
    }

    // Determine how many jobs to process based on tier
    const jobsToProcess = isProUser ? Math.min(jobCount, maxJobs) : 1;
    const jobsToProcessUrls = jobUrls.slice(0, jobsToProcess);

    // Show upgrade prompt if user is trying to process more than their limit allows
    if (!isProUser && jobCount > 1) {
      // For free users, we'll process the first job but show upgrade context
      console.log(`Free user processing 1 of ${jobCount} jobs. Upgrade available for batch processing.`);
    } else if (isProUser && jobCount > maxJobs) {
      // Pro users exceeding the batch limit should reduce their selection
      return;
    }

    // Initialize processing jobs
    const initialJobs = jobsToProcessUrls.map((url, index) => ({
      id: `job-${index}`,
      jobTitle: `Job ${index + 1}`, // This would come from actual job data
      jobCompany: 'Company Name', // This would come from actual job data
      status: 'queued',
      progress: 0,
      currentStep: null,
      timeRemaining: 0,
      actualTime: 0,
      stepDetails: {},
      stepTimes: {}
    }));

    setProcessingJobs(initialJobs);
    setCurrentStep('processing');
    setEstimatedTimeRemaining(jobsToProcess * 45); // 45 seconds per job estimate
    
    onProcessingStart?.(batchSettings);
    
    // Simulate processing (in real implementation, this would be handled by WebSocket/API)
    simulateProcessing(initialJobs);
  }, [weeklyUsage, weeklyLimit, isProUser, jobCount, maxJobs, jobUrls, batchSettings, onProcessingStart]);

  const simulateProcessing = useCallback(async (jobs) => {
    const processingSteps = ['analyzing', 'enhancing', 'optimizing', 'generating'];
    const stepDurations = [2000, 4000, 1500, 2500]; // milliseconds
    
    for (let i = 0; i < jobs.length; i++) {
      const job = jobs[i];
      
      // Update job status to processing
      setProcessingJobs(prev => prev.map(j => 
        j.id === job.id ? { ...j, status: 'processing', currentStep: processingSteps[0] } : j
      ));
      
      // Process each step
      for (let stepIndex = 0; stepIndex < processingSteps.length; stepIndex++) {
        const step = processingSteps[stepIndex];
        const duration = stepDurations[stepIndex];
        
        // Update current step
        setProcessingJobs(prev => prev.map(j => 
          j.id === job.id ? { 
            ...j, 
            currentStep: step,
            progress: ((stepIndex + 1) / processingSteps.length) * 100
          } : j
        ));
        
        // Simulate step processing time
        await new Promise(resolve => setTimeout(resolve, duration));
        
        // Mark step as completed
        setProcessingJobs(prev => prev.map(j => 
          j.id === job.id ? { 
            ...j,
            stepDetails: { ...j.stepDetails, [step]: `${step} completed successfully` },
            stepTimes: { ...j.stepTimes, [step]: duration }
          } : j
        ));
      }
      
      // Mark job as completed with mock results
      const mockResults = {
        originalScore: Math.floor(Math.random() * 30) + 40, // 40-70
        finalScore: Math.floor(Math.random() * 25) + 75, // 75-100
        keywordsAdded: Math.floor(Math.random() * 15) + 5, // 5-20
        processingTime: stepDurations.reduce((a, b) => a + b, 0) / 1000
      };
      
      setProcessingJobs(prev => prev.map(j => 
        j.id === job.id ? { 
          ...j, 
          status: 'completed',
          progress: 100,
          actualTime: mockResults.processingTime,
          ...mockResults
        } : j
      ));
      
      // Update estimated time remaining
      setEstimatedTimeRemaining(prev => Math.max(0, prev - 45));
    }
    
    // All jobs completed, move to results
    setTimeout(() => {
      setCurrentStep('results');
      onProcessingComplete?.();
    }, 1000);
  }, [onProcessingComplete]);

  const handlePauseProcessing = useCallback(() => {
    setIsPaused(true);
    // In real implementation, this would pause the actual processing
  }, []);

  const handleResumeProcessing = useCallback(() => {
    setIsPaused(false);
    // In real implementation, this would resume the actual processing
  }, []);

  const handleCancelProcessing = useCallback(() => {
    setCurrentStep('settings');
    setProcessingJobs([]);
    setIsPaused(false);
    setEstimatedTimeRemaining(0);
    // In real implementation, this would cancel the actual processing
  }, []);

  const handleUpgradeClick = useCallback(() => {
    setShowUpgradePrompt(true);
  }, []);

  // Calculate overall progress
  const calculateOverallProgress = useCallback(() => {
    if (processingJobs.length === 0) return 0;
    
    const totalProgress = processingJobs.reduce((sum, job) => sum + (job.progress || 0), 0);
    return totalProgress / processingJobs.length;
  }, [processingJobs]);

  // Render different steps
  const renderCurrentStep = () => {
    switch (currentStep) {
      case 'settings':
        return (
          <div className="space-y-6">
            {/* Job Count and Limitations */}
            <TierBasedBatchLimitations
              jobCount={jobCount}
              maxJobs={maxJobs}
              isProUser={isProUser}
              weeklyUsage={weeklyUsage}
              weeklyLimit={weeklyLimit}
              onUpgradeClick={handleUpgradeClick}
              onBackToModeSelection={onBackToModeSelection}
              onStartProcessing={handleStartProcessing}
              canProcess={canProcess}
            />
          </div>
        );
      
      case 'processing':
        return (
          <LiveProcessingVisualization
            jobs={processingJobs}
            currentProgress={calculateOverallProgress()}
            onPause={handlePauseProcessing}
            onResume={handleResumeProcessing}
            onCancel={handleCancelProcessing}
            isPaused={isPaused}
            estimatedTimeRemaining={estimatedTimeRemaining}
          />
        );
      
      case 'results':
        return (
          <BatchResultsOverview
            completedJobs={processingJobs.filter(job => job.status === 'completed')}
            onDownloadAll={() => {
              // Handle download all logic
              console.log('Downloading all results');
            }}
            onDownloadIndividual={(jobIds) => {
              // Handle download individual logic
              console.log('Downloading jobs:', jobIds);
            }}
            onStartNewBatch={() => {
              setCurrentStep('settings');
              setProcessingJobs([]);
              setIsPaused(false);
              setEstimatedTimeRemaining(0);
            }}
            onBackToSettings={() => {
              setCurrentStep('settings');
            }}
            isProUser={isProUser}
          />
        );
      
      default:
        return null;
    }
  };

  return (
    <div className={`max-w-6xl mx-auto p-6 ${className}`}>
      {/* Header */}
      <motion.div
        variants={fadeInUp}
        initial="hidden"
        animate="visible"
        className="text-center mb-8"
      >
        <div className="flex items-center justify-center gap-3 mb-4">
          <div className="p-3 bg-blue-100 rounded-xl">
            <Zap className="w-8 h-8 text-blue-600" />
          </div>
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Batch Mode</h1>
            <p className="text-gray-600">Fast & reliable processing for multiple jobs</p>
          </div>
        </div>
        
        {!isProUser && (
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-purple-50 border border-purple-200 rounded-full text-sm text-purple-700">
            <Crown className="w-4 h-4" />
            <span>Limited to 1 job - Upgrade for batch processing</span>
          </div>
        )}
      </motion.div>

      {/* Main Content */}
      {renderCurrentStep()}

      {/* Upgrade Prompt Modal */}
      <AnimatePresence>
        {showUpgradePrompt && (
          <UpgradePrompt
            context="batch-mode"
            onClose={() => setShowUpgradePrompt(false)}
            onUpgrade={() => {
              // Handle upgrade logic
              setShowUpgradePrompt(false);
            }}
          />
        )}
      </AnimatePresence>
    </div>
  );
}

export default BatchModeInterface;
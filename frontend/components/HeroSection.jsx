import React from 'react'
import { motion } from 'framer-motion'
import { useAccessibility } from '../hooks/useAccessibility'
// Simple animation variants to replace lib/animations imports
const fadeInVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0 }
}

const cardVariants = {
  hidden: { opacity: 0, scale: 0.95 },
  visible: { opacity: 1, scale: 1 }
}

const lightningVariants = {
  hidden: { opacity: 0, scale: 0.8 },
  visible: { opacity: 1, scale: 1 }
}

const HeroSection = ({ showSuccessBanner = false, transformationScore = 0 }) => {
  const {
    getAnimationProps,
    getContrastClass,
    shouldReduceMotion
  } = useAccessibility()

  return (
    <motion.div 
      className={`relative bg-white/80 backdrop-blur-sm border-b border-white/50 shadow-sm ${getContrastClass()}`}
      {...getAnimationProps({
        initial: "hidden",
        animate: "visible",
        variants: fadeInVariants
      })}
    >
      {/* Gradient Background */}
      <div className="absolute inset-0 bg-gradient-to-r from-purple-600/10 via-blue-600/5 to-purple-600/10"></div>
      <div className="absolute inset-0 bg-gradient-to-br from-slate-50/50 via-blue-50/30 to-indigo-50/50"></div>
      
      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 lg:py-16">
        <div className="text-center">
          {/* Logo and Brand */}
          <motion.div 
            className="flex items-center justify-center gap-3 mb-6"
            initial="hidden"
            animate="visible"
            variants={cardVariants}
            transition={{ delay: 0.2 }}
          >
            <div className="relative">
              <div className="w-16 h-16 bg-gradient-to-r from-purple-600 to-blue-600 rounded-2xl flex items-center justify-center shadow-lg">
                <motion.svg 
                  className="w-9 h-9 text-white" 
                  fill="none" 
                  stroke="currentColor" 
                  viewBox="0 0 24 24"
                  variants={lightningVariants}
                  initial="idle"
                  animate={shouldReduceMotion ? "idle" : "pulse"}
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </motion.svg>
              </div>
              <div className="absolute -top-1 -right-1 w-5 h-5 bg-green-500 rounded-full border-2 border-white shadow-sm"></div>
            </div>
            <h1 className="text-5xl lg:text-6xl font-bold bg-gradient-to-r from-gray-900 via-purple-800 to-blue-800 bg-clip-text text-transparent">
              Apply.AI
            </h1>
          </motion.div>

          {/* Main Tagline */}
          <motion.div
            className="mb-8"
            initial="hidden"
            animate="visible"
            variants={cardVariants}
            transition={{ delay: 0.4 }}
          >
            <h2 className="text-2xl lg:text-3xl font-semibold text-gray-900 mb-4 leading-tight">
              Transform Your Resume for Every Opportunity
            </h2>
            <p className="text-lg lg:text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed">
              Our AI analyzes job descriptions and intelligently tailors your resume to match what employers are looking for. 
              Stand out from the crowd with personalized, optimized applications.
            </p>
          </motion.div>

          {/* Resume Morph Illustration */}
          <motion.div
            className="mb-8"
            initial="hidden"
            animate="visible"
            variants={cardVariants}
            transition={{ delay: 0.6 }}
          >
            <div className="flex items-center justify-center gap-8 max-w-4xl mx-auto">
              {/* Original Resume */}
              <div className="flex-1 max-w-xs">
                <div className="bg-white rounded-lg shadow-md p-4 border border-gray-200">
                  <div className="space-y-2">
                    <div className="h-3 bg-gray-300 rounded w-3/4"></div>
                    <div className="h-2 bg-gray-200 rounded w-full"></div>
                    <div className="h-2 bg-gray-200 rounded w-5/6"></div>
                    <div className="h-2 bg-gray-200 rounded w-4/5"></div>
                    <div className="space-y-1 mt-3">
                      <div className="h-2 bg-gray-200 rounded w-2/3"></div>
                      <div className="h-2 bg-gray-200 rounded w-3/4"></div>
                      <div className="h-2 bg-gray-200 rounded w-1/2"></div>
                    </div>
                  </div>
                  <div className="text-xs text-gray-500 mt-3 text-center">Original Resume</div>
                </div>
              </div>

              {/* Transformation Arrow */}
              <div className="flex flex-col items-center">
                <motion.div
                  className="w-12 h-12 bg-gradient-to-r from-purple-600 to-blue-600 rounded-full flex items-center justify-center shadow-lg mb-2"
                  variants={lightningVariants}
                  initial="idle"
                  animate={shouldReduceMotion ? "idle" : "pulse"}
                >
                  <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                </motion.div>
                <div className="hidden sm:block">
                  <svg className="w-8 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
                  </svg>
                </div>
              </div>

              {/* Tailored Resume */}
              <div className="flex-1 max-w-xs">
                <div className="bg-white rounded-lg shadow-lg p-4 border-2 border-purple-200 relative overflow-hidden">
                  <div className="absolute inset-0 bg-gradient-to-br from-purple-50/50 to-blue-50/50"></div>
                  <div className="relative space-y-2">
                    <div className="h-3 bg-gradient-to-r from-purple-400 to-blue-400 rounded w-3/4"></div>
                    <div className="h-2 bg-purple-200 rounded w-full"></div>
                    <div className="h-2 bg-blue-200 rounded w-5/6"></div>
                    <div className="h-2 bg-purple-200 rounded w-4/5"></div>
                    <div className="space-y-1 mt-3">
                      <div className="h-2 bg-blue-200 rounded w-2/3"></div>
                      <div className="h-2 bg-purple-200 rounded w-3/4"></div>
                      <div className="h-2 bg-blue-200 rounded w-1/2"></div>
                    </div>
                  </div>
                  <div className="relative text-xs text-purple-700 mt-3 text-center font-medium">Tailored Resume</div>
                  <div className="absolute top-2 right-2">
                    <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
                  </div>
                </div>
              </div>
            </div>
          </motion.div>

          {/* Key Benefits */}
          <motion.div
            className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl mx-auto"
            initial="hidden"
            animate="visible"
            variants={cardVariants}
            transition={{ delay: 0.8 }}
          >
            <div className="text-center">
              <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mx-auto mb-3">
                <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">Smart Keyword Matching</h3>
              <p className="text-sm text-gray-600">Automatically identifies and incorporates relevant keywords from job descriptions</p>
            </div>
            
            <div className="text-center">
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mx-auto mb-3">
                <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">AI-Powered Analysis</h3>
              <p className="text-sm text-gray-600">Advanced algorithms analyze job requirements and optimize your resume accordingly</p>
            </div>
            
            <div className="text-center">
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mx-auto mb-3">
                <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">Instant Results</h3>
              <p className="text-sm text-gray-600">Get your tailored resume in seconds, ready for immediate application</p>
            </div>
          </motion.div>
        </div>
      </div>

      {/* Success Banner - shown after processing */}
      {showSuccessBanner && (
        <motion.div
          className="absolute bottom-0 left-0 right-0 bg-gradient-to-r from-green-500 to-emerald-500 text-white py-3 px-4 shadow-lg"
          initial={{ opacity: 0, y: 50 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: 50 }}
          transition={{ duration: 0.5 }}
        >
          <div className="max-w-7xl mx-auto flex items-center justify-center gap-3">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span className="font-medium">
              Resume transformation complete! 
              {transformationScore > 0 && (
                <span className="ml-2 px-2 py-1 bg-white/20 rounded-full text-sm">
                  Transformation Score: {transformationScore}%
                </span>
              )}
            </span>
          </div>
        </motion.div>
      )}
    </motion.div>
  )
}

export default HeroSection
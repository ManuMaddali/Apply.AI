import React, { useState, useRef, useEffect, useCallback } from 'react'
import { motion } from 'framer-motion'
import { Zap, FileText, Lightbulb, GraduationCap, Info, Sparkles } from 'lucide-react'
import { Switch } from './ui/switch'
import { Accordion, AccordionItem, AccordionTrigger, AccordionContent, useAccordion } from './ui/accordion'
import { createKeyboardHandler, FocusManager, announceToScreenReader } from '../utils/keyboardNavigation'

const EnhanceResumeCard = ({ 
  tailoringMode, 
  onModeChange, 
  optionalSections = {}, 
  onOptionalSectionsChange, 
  coverLetterOptions = {}, 
  onCoverLetterOptionsChange, 
  isProUser = false,
  jobData = [] 
}) => {
  const [showEducationForm, setShowEducationForm] = useState(optionalSections.includeEducation || false)
  const [smartSuggestAll, setSmartSuggestAll] = useState(false)
  
  // Accordion state management
  const basicEnhancements = useAccordion(true) // Open by default
  const advancedOptions = useAccordion(false)
  
  // Refs for keyboard navigation
  const cardRef = useRef(null)
  const smartSuggestRef = useRef(null)
  const enhancementSwitchesRef = useRef(null)

  const handleEducationToggle = (checked) => {
    setShowEducationForm(checked)
    if (!checked) {
      // Clear education data when unchecked
      onOptionalSectionsChange({
        ...optionalSections,
        includeEducation: false,
        educationDetails: {
          degree: '',
          institution: '',
          year: '',
          gpa: ''
        }
      })
    } else {
      onOptionalSectionsChange({
        ...optionalSections,
        includeEducation: true
      })
    }
  }

  const handleEducationChange = (field, value) => {
    onOptionalSectionsChange({
      ...optionalSections,
      educationDetails: {
        ...optionalSections.educationDetails,
        [field]: value
      }
    })
  }

  // Smart suggest logic based on job data analysis
  const handleSmartSuggestAll = useCallback((checked) => {
    setSmartSuggestAll(checked)
    
    if (checked) {
      // Auto-select based on job data analysis
      const suggestedOptions = {
        includeSummary: true, // Always suggest summary
        includeSkills: true,  // Always suggest skills
        includeEducation: jobData.some(job => 
          job.description?.toLowerCase().includes('degree') || 
          job.description?.toLowerCase().includes('education') ||
          job.description?.toLowerCase().includes('bachelor') ||
          job.description?.toLowerCase().includes('master')
        )
      }
      
      onOptionalSectionsChange({
        ...optionalSections,
        ...suggestedOptions
      })
      
      setShowEducationForm(suggestedOptions.includeEducation)
      
      const selectedCount = Object.values(suggestedOptions).filter(Boolean).length
      announceToScreenReader(`Smart suggestions applied. ${selectedCount} enhancements selected.`)
    } else {
      announceToScreenReader('Smart suggestions cleared')
    }
  }, [optionalSections, onOptionalSectionsChange, jobData])

  // Keyboard navigation setup
  useEffect(() => {
    const handleKeyDown = createKeyboardHandler({
      'a': () => {
        // Toggle smart suggest all
        handleSmartSuggestAll(!smartSuggestAll)
      },
      '1': () => {
        // Toggle first enhancement (summary)
        const newValue = !optionalSections.includeSummary
        onOptionalSectionsChange({ ...optionalSections, includeSummary: newValue })
        announceToScreenReader(`Professional summary ${newValue ? 'enabled' : 'disabled'}`)
      },
      '2': () => {
        // Toggle second enhancement (skills)
        const newValue = !optionalSections.includeSkills
        onOptionalSectionsChange({ ...optionalSections, includeSkills: newValue })
        announceToScreenReader(`Skills section ${newValue ? 'enabled' : 'disabled'}`)
      },
      '3': () => {
        // Toggle education
        const newValue = !optionalSections.includeEducation
        setShowEducationForm(newValue)
        onOptionalSectionsChange({ ...optionalSections, includeEducation: newValue })
        announceToScreenReader(`Education section ${newValue ? 'enabled' : 'disabled'}`)
      }
    }, { preventDefault: false })

    const cardElement = cardRef.current
    if (cardElement) {
      cardElement.addEventListener('keydown', handleKeyDown)
      return () => cardElement.removeEventListener('keydown', handleKeyDown)
    }
  }, [smartSuggestAll, optionalSections, handleSmartSuggestAll, onOptionalSectionsChange])

  const enhancementOptions = [
    {
      key: 'includeSummary',
      title: 'Professional Summary',
      description: 'Enhance existing summary or create new one with job-specific keywords',
      icon: FileText,
      color: 'text-ai-purple',
      bgColor: 'bg-purple-50/50',
      borderColor: 'border-purple-200/50',
      hoverBorderColor: 'hover:border-purple-300/50',
      tooltip: 'Example: "Results-driven software engineer with 5+ years of experience in full-stack development, specializing in React and Node.js..."'
    },
    {
      key: 'includeSkills',
      title: 'Skills Section',
      description: 'Optimize existing skills section or add new one with job-relevant abilities',
      icon: Zap,
      color: 'text-blue-600',
      bgColor: 'bg-blue-50/50',
      borderColor: 'border-blue-200/50',
      hoverBorderColor: 'hover:border-blue-300/50',
      tooltip: 'Example: Technical skills like "JavaScript, React, Python, AWS" or soft skills like "Leadership, Problem-solving"'
    }
  ]

  return (
    <motion.div 
      ref={cardRef}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg border border-white/50 p-8 transition-all duration-300 hover:shadow-xl hover:bg-white/90"
      role="region"
      aria-label="Resume enhancement options"
      tabIndex={-1}
    >
      {/* Header */}
      <div className="flex items-center gap-4 mb-6">
        <motion.div 
          className="p-4 bg-gradient-to-r from-ai-purple to-purple-600 rounded-xl shadow-lg"
          whileHover={{ scale: 1.05 }}
          transition={{ duration: 0.2 }}
        >
          <Sparkles className="w-6 h-6 text-white" />
        </motion.div>
        <div>
          <h2 className="text-xl font-bold text-gray-900">Enhance Your Resume</h2>
          <p className="text-sm text-gray-600 mt-1">✨ Smart enhancement - improves existing sections or adds new ones</p>
        </div>
      </div>

      {/* Smart Suggest All Toggle */}
      <div className="mb-6 p-4 rounded-xl bg-gradient-to-r from-ai-purple/10 to-purple-100/50 border border-ai-purple/20">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <motion.div
              animate={{ rotate: smartSuggestAll ? 360 : 0 }}
              transition={{ duration: 0.5 }}
            >
              <Lightbulb className="w-5 h-5 text-ai-purple" />
            </motion.div>
            <div>
              <label htmlFor="smart-suggest-switch" className="font-semibold text-gray-900">
                Smart Suggest All
              </label>
              <div className="text-sm text-gray-600">Auto-select enhancements based on job analysis</div>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Switch
              id="smart-suggest-switch"
              ref={smartSuggestRef}
              checked={smartSuggestAll}
              onCheckedChange={handleSmartSuggestAll}
              className="data-[state=checked]:bg-ai-purple"
              aria-describedby="smart-suggest-help"
            />
            <div className="group relative">
              <Info 
                className="w-4 h-4 text-gray-400 cursor-help" 
                role="button"
                tabIndex={0}
                aria-label="Smart suggest information"
                onKeyDown={(e) => {
                  if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault()
                    announceToScreenReader('Smart suggest analyzes your job descriptions to automatically suggest the most relevant enhancements for your resume.')
                  }
                }}
              />
              <div 
                id="smart-suggest-help"
                className="absolute right-0 top-6 w-64 p-3 bg-gray-900 text-white text-xs rounded-lg opacity-0 group-hover:opacity-100 transition-opacity duration-200 z-10"
                role="tooltip"
              >
                Analyzes your job descriptions to automatically suggest the most relevant enhancements for your resume.
              </div>
            </div>
          </div>
        </div>
        <div className="text-xs text-gray-500 mt-2">
          Press 'A' to toggle smart suggestions
        </div>
      </div>

      <Accordion className="space-y-4">
        {/* Basic Enhancements Accordion */}
        <AccordionItem className="border border-gray-200/50 rounded-xl overflow-hidden">
          <AccordionTrigger
            isOpen={basicEnhancements.isOpen}
            onToggle={basicEnhancements.toggle}
            className="bg-gradient-to-r from-gray-50/50 to-white/50 hover:from-gray-100/50 hover:to-white/70"
          >
            <div className="flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-ai-purple" />
              <span className="font-semibold">Basic Enhancements</span>
              <span className="text-sm text-gray-500">({enhancementOptions.filter(opt => optionalSections[opt.key]).length}/{enhancementOptions.length} selected)</span>
            </div>
          </AccordionTrigger>
          
          <AccordionContent isOpen={basicEnhancements.isOpen}>
            <div className="space-y-4" ref={enhancementSwitchesRef}>
              {enhancementOptions.map((enhancement, index) => {
                const IconComponent = enhancement.icon
                const shortcutKey = (index + 1).toString()
                return (
                  <motion.div
                    key={enhancement.key}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.3 }}
                    className={`p-4 rounded-xl ${enhancement.bgColor} border ${enhancement.borderColor} ${enhancement.hoverBorderColor} transition-all duration-200 group`}
                    role="group"
                    aria-labelledby={`enhancement-${enhancement.key}-title`}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-start gap-4 flex-1">
                        <motion.div
                          animate={{ 
                            scale: optionalSections[enhancement.key] ? [1, 1.2, 1] : 1,
                            rotate: optionalSections[enhancement.key] ? [0, 10, -10, 0] : 0
                          }}
                          transition={{ duration: 0.5 }}
                        >
                          <IconComponent className={`w-5 h-5 ${enhancement.color} mt-0.5`} />
                        </motion.div>
                        <div className="flex-1">
                          <div 
                            id={`enhancement-${enhancement.key}-title`}
                            className="font-semibold text-gray-900 flex items-center gap-2"
                          >
                            {enhancement.title}
                            <span className="text-xs bg-gray-200 text-gray-600 px-1.5 py-0.5 rounded">
                              {shortcutKey}
                            </span>
                          </div>
                          <div className="text-sm text-gray-600 mt-1">
                            {enhancement.description}
                          </div>
                        </div>
                      </div>
                      
                      <div className="flex items-center gap-2">
                        <Switch
                          id={`enhancement-${enhancement.key}-switch`}
                          checked={optionalSections[enhancement.key]}
                          onCheckedChange={(checked) => {
                            onOptionalSectionsChange({
                              ...optionalSections,
                              [enhancement.key]: checked
                            })
                            announceToScreenReader(`${enhancement.title} ${checked ? 'enabled' : 'disabled'}`)
                          }}
                          className="data-[state=checked]:bg-ai-purple"
                          aria-describedby={`enhancement-${enhancement.key}-description`}
                        />
                        <div className="group/tooltip relative">
                          <Info 
                            className="w-4 h-4 text-gray-400 cursor-help" 
                            role="button"
                            tabIndex={0}
                            aria-label={`Information about ${enhancement.title}`}
                            onKeyDown={(e) => {
                              if (e.key === 'Enter' || e.key === ' ') {
                                e.preventDefault()
                                announceToScreenReader(enhancement.tooltip)
                              }
                            }}
                          />
                          <div 
                            id={`enhancement-${enhancement.key}-description`}
                            className="absolute right-0 top-6 w-72 p-3 bg-gray-900 text-white text-xs rounded-lg opacity-0 group-hover/tooltip:opacity-100 transition-opacity duration-200 z-10"
                            role="tooltip"
                          >
                            {enhancement.tooltip}
                          </div>
                        </div>
                      </div>
                    </div>
                  </motion.div>
                )
              })}
              <div className="text-xs text-gray-500 mt-4 p-2 bg-gray-50 rounded">
                <strong>Keyboard shortcuts:</strong> Press 1 for Summary, 2 for Skills, 3 for Education
              </div>
            </div>
          </AccordionContent>
        </AccordionItem>

        {/* Advanced Options Accordion */}
        <AccordionItem className="border border-gray-200/50 rounded-xl overflow-hidden">
          <AccordionTrigger
            isOpen={advancedOptions.isOpen}
            onToggle={advancedOptions.toggle}
            className="bg-gradient-to-r from-gray-50/50 to-white/50 hover:from-gray-100/50 hover:to-white/70"
          >
            <div className="flex items-center gap-2">
              <GraduationCap className="w-4 h-4 text-green-600" />
              <span className="font-semibold">Advanced Options</span>
              <span className="text-sm text-gray-500">({optionalSections.includeEducation ? '1' : '0'}/1 selected)</span>
            </div>
          </AccordionTrigger>
          
          <AccordionContent isOpen={advancedOptions.isOpen}>
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.3 }}
              className="p-4 rounded-xl bg-gradient-to-r from-green-50/50 to-teal-50/50 border border-green-200/50 hover:border-green-300/50 transition-all duration-200"
            >
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-start gap-4 flex-1">
                  <motion.div
                    animate={{ 
                      scale: optionalSections.includeEducation ? [1, 1.2, 1] : 1,
                      rotate: optionalSections.includeEducation ? [0, 10, -10, 0] : 0
                    }}
                    transition={{ duration: 0.5 }}
                  >
                    <GraduationCap className="w-5 h-5 text-green-600 mt-0.5" />
                  </motion.div>
                  <div className="flex-1">
                    <div className="font-semibold text-gray-900">Education Section</div>
                    <div className="text-sm text-gray-600 mt-1">
                      Improve existing education section or add new one with provided details
                    </div>
                  </div>
                </div>
                
                <div className="flex items-center gap-2">
                  <Switch
                    checked={optionalSections.includeEducation}
                    onCheckedChange={handleEducationToggle}
                    className="data-[state=checked]:bg-green-600"
                  />
                  <div className="group/tooltip relative">
                    <Info className="w-4 h-4 text-gray-400 cursor-help" />
                    <div className="absolute right-0 top-6 w-72 p-3 bg-gray-900 text-white text-xs rounded-lg opacity-0 group-hover/tooltip:opacity-100 transition-opacity duration-200 z-10">
                      Example: "Bachelor of Science in Computer Science, Georgia Tech, 2020, GPA: 3.8/4.0"
                    </div>
                  </div>
                </div>
              </div>

              {/* Education Form */}
              {showEducationForm && (
                <motion.div
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: 'auto', opacity: 1 }}
                  exit={{ height: 0, opacity: 0 }}
                  transition={{ duration: 0.3, ease: 'easeInOut' }}
                  className="mt-6 space-y-4 p-6 bg-white/70 backdrop-blur-sm rounded-xl border border-white/50"
                >
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Degree
                      </label>
                      <input
                        type="text"
                        value={optionalSections.educationDetails?.degree || ''}
                        onChange={(e) => handleEducationChange('degree', e.target.value)}
                        placeholder="e.g., Bachelor of Science"
                        className="w-full px-4 py-3 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent text-sm bg-white/80 backdrop-blur-sm transition-all duration-200"
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Institution
                      </label>
                      <input
                        type="text"
                        value={optionalSections.educationDetails?.institution || ''}
                        onChange={(e) => handleEducationChange('institution', e.target.value)}
                        placeholder="e.g., Georgia Tech"
                        className="w-full px-4 py-3 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent text-sm bg-white/80 backdrop-blur-sm transition-all duration-200"
                      />
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Graduation Year
                      </label>
                      <input
                        type="text"
                        value={optionalSections.educationDetails?.year || ''}
                        onChange={(e) => handleEducationChange('year', e.target.value)}
                        placeholder="e.g., 2020"
                        className="w-full px-4 py-3 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent text-sm bg-white/80 backdrop-blur-sm transition-all duration-200"
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        GPA <span className="text-gray-400">(optional)</span>
                      </label>
                      <input
                        type="text"
                        value={optionalSections.educationDetails?.gpa || ''}
                        onChange={(e) => handleEducationChange('gpa', e.target.value)}
                        placeholder="e.g., 3.8/4.0"
                        className="w-full px-4 py-3 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent text-sm bg-white/80 backdrop-blur-sm transition-all duration-200"
                      />
                    </div>
                  </div>
                </motion.div>
              )}
            </motion.div>
          </AccordionContent>
        </AccordionItem>
      </Accordion>

      {/* Helpful Info Note */}
      <motion.div 
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.5, duration: 0.3 }}
        className="mt-6 p-4 bg-blue-50/50 border border-blue-200/50 rounded-lg"
      >
        <div className="flex items-start gap-3">
          <Info className="w-4 h-4 text-blue-600 mt-0.5 flex-shrink-0" />
          <div className="text-sm text-blue-700">
            <strong>Smart Enhancement:</strong> Toggle any section to improve it! The AI automatically detects what's already in your resume and enhances existing content or adds missing sections.
          </div>
        </div>
      </motion.div>
    </motion.div>
  )
}

export default EnhanceResumeCard
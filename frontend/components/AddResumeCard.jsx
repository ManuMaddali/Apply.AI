import React, { useState, useCallback, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Upload, FileText, Check } from 'lucide-react';
import { 
  EnhancedCard, 
  EnhancedCardHeader, 
  EnhancedCardTitle, 
  EnhancedCardDescription,
  EnhancedCardContent 
} from './ui/enhanced-card';
import { LightningIcon, SuccessIndicator, AIActionIndicator } from './ui/lightning-icon';
import { Button } from './ui/button';
// Simple animation variants to replace lib/animations imports
const cardVariants = {
  hidden: { opacity: 0, scale: 0.95 },
  visible: { opacity: 1, scale: 1 }
}

const dropZoneVariants = {
  idle: { scale: 1, borderColor: '#e5e7eb' },
  hover: { scale: 1.02, borderColor: '#3b82f6' },
  active: { scale: 0.98, borderColor: '#1d4ed8' }
}
// Simple keyboard navigation utilities to replace gitignored imports
const createKeyboardHandler = (callback) => (event) => {
  if (event.key === 'Enter' || event.key === ' ') {
    event.preventDefault();
    callback(event);
  }
};

const FocusManager = {
  trapFocus: (element) => {
    // Simple focus trap implementation
    const focusableElements = element.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    if (focusableElements.length > 0) {
      focusableElements[0].focus();
    }
  }
};

const announceToScreenReader = (message) => {
  // Simple screen reader announcement
  const announcement = document.createElement('div');
  announcement.setAttribute('aria-live', 'polite');
  announcement.setAttribute('aria-atomic', 'true');
  announcement.className = 'sr-only';
  announcement.textContent = message;
  document.body.appendChild(announcement);
  setTimeout(() => document.body.removeChild(announcement), 1000);
};

const AddResumeCard = ({ 
  file, 
  onFileUpload, 
  resumeText, 
  onTextChange,
  loading,
  className 
}) => {
  const [dragActive, setDragActive] = useState(false);
  const [activeTab, setActiveTab] = useState('file');
  const [showPreview, setShowPreview] = useState(false);
  const [scanResults, setScanResults] = useState(null);
  const [isScanning, setIsScanning] = useState(false);
  const [isLoadingPreview, setIsLoadingPreview] = useState(false);
  const [previewText, setPreviewText] = useState('');
  
  // Refs for keyboard navigation
  const cardRef = useRef(null);
  const fileInputRef = useRef(null);
  const textareaRef = useRef(null);
  const scanButtonRef = useRef(null);
  const tabButtonsRef = useRef(null);

  // Generate preview from uploaded file - MOVED UP to fix hoisting issue
  const generatePreview = useCallback(async (file) => {
    setIsLoadingPreview(true);
    setShowPreview(true);
    
    try {
      if (file.type === 'text/plain') {
        // For text files, read directly
        const text = await file.text();
        setPreviewText(text.substring(0, 500));
      } else {
        // For PDF/DOCX files, show file info and simulate extraction
        setPreviewText(`File: ${file.name}\nSize: ${(file.size / 1024).toFixed(1)} KB\nType: ${file.type}\n\nProcessing file content...`);
        
        // Simulate file processing delay
        setTimeout(() => {
          setPreviewText(`File: ${file.name}\nSize: ${(file.size / 1024).toFixed(1)} KB\nType: ${file.type}\n\n[Preview will be available after processing]\n\nThis file will be processed when you submit your resume for tailoring.`);
          setIsLoadingPreview(false);
        }, 1500);
        return;
      }
    } catch (error) {
      console.error('Error generating preview:', error);
      setPreviewText(`Error reading file: ${file.name}`);
    }
    
    setIsLoadingPreview(false);
  }, []);

  // Drag and drop handlers
  const handleDragEnter = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(true);
  }, []);

  const handleDragLeave = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
  }, []);

  const handleDragOver = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
  }, []);

  const handleDrop = useCallback(async (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile && (
      droppedFile.type === 'application/pdf' || 
      droppedFile.type === 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' ||
      droppedFile.type === 'text/plain'
    )) {
      onFileUpload({ target: { files: [droppedFile] } });
      await generatePreview(droppedFile);
    }
  }, [onFileUpload, generatePreview]);

  const handleFileSelect = useCallback(async (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      onFileUpload(e);
      await generatePreview(selectedFile);
    }
  }, [onFileUpload, generatePreview]);

  const handleTextChange = useCallback((e) => {
    onTextChange(e.target.value);
    if (e.target.value.trim()) {
      setPreviewText(e.target.value.trim());
      setShowPreview(true);
    } else {
      setShowPreview(false);
    }
  }, [onTextChange]);

  // Mock scan for issues functionality
  const handleScanForIssues = useCallback(async () => {
    if (!file && !resumeText?.trim()) return;
    
    setIsScanning(true);
    announceToScreenReader('Starting resume scan analysis');
    
    // Simulate AI scanning with delay
    setTimeout(() => {
      const mockResults = {
        score: Math.floor(Math.random() * 20) + 80, // Random score between 80-100
        strengths: [
          'Professional formatting detected',
          'Contact information is complete',
          'Work experience section is well-structured',
          'Education section is properly formatted'
        ],
        improvements: [
          'Add more quantified achievements (e.g., "Increased sales by 25%")',
          'Include industry-specific keywords',
          'Consider adding a professional summary',
          'Optimize for ATS compatibility'
        ],
        keywords: [
          'leadership', 'project management', 'data analysis', 
          'communication', 'problem-solving', 'teamwork'
        ],
        atsCompatibility: 'Good'
      };
      
      setScanResults(mockResults);
      setIsScanning(false);
      announceToScreenReader(`Resume scan complete. Score: ${mockResults.score} out of 100`);
    }, 2500);
  }, [file, resumeText]);

  // Keyboard navigation handlers
  const handleKeyDown = useCallback(createKeyboardHandler({
    'u': () => {
      if (activeTab === 'file') {
        fileInputRef.current?.click();
        announceToScreenReader('File upload dialog opened');
      }
    },
    's': () => {
      if ((file || resumeText?.trim()) && !isScanning) {
        handleScanForIssues();
      }
    },
    'Tab': (e) => {
      // Let default tab behavior work, but announce context
      const focusableElements = FocusManager.getFocusableElements(cardRef.current);
      const currentIndex = focusableElements.indexOf(document.activeElement);
      if (currentIndex >= 0) {
        const nextElement = focusableElements[currentIndex + (e.shiftKey ? -1 : 1)];
        if (nextElement) {
          announceToScreenReader(`Focused on ${nextElement.getAttribute('aria-label') || nextElement.textContent || 'interactive element'}`);
        }
      }
    }
  }, { preventDefault: false }), [activeTab, file, resumeText, isScanning, handleScanForIssues]);

  // Set up keyboard event listeners
  useEffect(() => {
    const cardElement = cardRef.current;
    if (cardElement) {
      cardElement.addEventListener('keydown', handleKeyDown);
      return () => cardElement.removeEventListener('keydown', handleKeyDown);
    }
  }, [handleKeyDown]);

  // Tab switching with keyboard support
  const handleTabSwitch = useCallback((tab, event) => {
    setActiveTab(tab);
    announceToScreenReader(`Switched to ${tab === 'file' ? 'file upload' : 'text input'} tab`);
    
    // Focus appropriate element after tab switch
    setTimeout(() => {
      if (tab === 'file') {
        const dropZone = cardRef.current?.querySelector('[data-dropzone]');
        dropZone?.focus();
      } else {
        textareaRef.current?.focus();
      }
    }, 100);
  }, []);

  const getFilePreview = () => {
    if (previewText) {
      return previewText;
    }
    if (file) {
      return `${file.name} (${(file.size / 1024).toFixed(1)} KB)`;
    }
    if (resumeText?.trim()) {
      return resumeText.trim().substring(0, 500) + (resumeText.trim().length > 500 ? '...' : '');
    }
    return null;
  };

  return (
    <motion.div
      ref={cardRef}
      variants={cardVariants}
      initial="hidden"
      animate="visible"
      whileHover="hover"
      className={className}
      role="region"
      aria-label="Resume upload section"
      tabIndex={-1}
    >
      <EnhancedCard variant="gradient-subtle" className="overflow-hidden">
        <EnhancedCardHeader>
          <div className="flex items-center gap-3">
            <div className="p-2 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg">
              <Upload className="h-5 w-5 text-white" />
            </div>
            <div>
              <EnhancedCardTitle size="default">Add Resume</EnhancedCardTitle>
              <EnhancedCardDescription>
                Upload a file or paste your resume text
              </EnhancedCardDescription>
            </div>
          </div>
        </EnhancedCardHeader>

        <EnhancedCardContent>
          {/* Tab Navigation */}
          <div 
            ref={tabButtonsRef}
            className="flex mb-6 bg-gray-100 rounded-lg p-1"
            role="tablist"
            aria-label="Resume input methods"
          >
            <button
              onClick={(e) => handleTabSwitch('file', e)}
              className={`flex-1 py-2 px-4 text-sm font-medium rounded-md transition-all duration-200 ${
                activeTab === 'file'
                  ? 'bg-white text-blue-600 shadow-sm'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
              role="tab"
              aria-selected={activeTab === 'file'}
              aria-controls="file-upload-panel"
              id="file-upload-tab"
              tabIndex={activeTab === 'file' ? 0 : -1}
            >
              <Upload className="w-4 h-4 inline mr-2" />
              Upload File
            </button>
            <button
              onClick={(e) => handleTabSwitch('text', e)}
              className={`flex-1 py-2 px-4 text-sm font-medium rounded-md transition-all duration-200 ${
                activeTab === 'text'
                  ? 'bg-white text-blue-600 shadow-sm'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
              role="tab"
              aria-selected={activeTab === 'text'}
              aria-controls="text-input-panel"
              id="text-input-tab"
              tabIndex={activeTab === 'text' ? 0 : -1}
            >
              <FileText className="w-4 h-4 inline mr-2" />
              Type/Paste Text
            </button>
          </div>

          {/* File Upload Tab */}
          {activeTab === 'file' && (
            <motion.div
              variants={dropZoneVariants}
              animate={dragActive ? 'dragOver' : 'idle'}
              className="relative border-2 border-dashed rounded-xl p-8 text-center transition-all duration-300"
              onDragEnter={handleDragEnter}
              onDragLeave={handleDragLeave}
              onDragOver={handleDragOver}
              onDrop={handleDrop}
              role="tabpanel"
              id="file-upload-panel"
              aria-labelledby="file-upload-tab"
              data-dropzone
              tabIndex={0}
              aria-label="File upload drop zone. Press Enter to browse files, or drag and drop files here."
              onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                  e.preventDefault();
                  fileInputRef.current?.click();
                }
              }}
            >
              <input
                ref={fileInputRef}
                type="file"
                accept=".pdf,.docx,.txt"
                onChange={handleFileSelect}
                className="hidden"
                id="file-upload"
                aria-describedby="file-upload-description"
              />
              
              <label htmlFor="file-upload" className="cursor-pointer block" id="file-upload-description">
                <AnimatePresence mode="wait">
                  {file ? (
                    <motion.div
                      key="file-uploaded"
                      initial={{ opacity: 0, scale: 0.8 }}
                      animate={{ opacity: 1, scale: 1 }}
                      exit={{ opacity: 0, scale: 0.8 }}
                      className="space-y-4"
                    >
                      <div className="mx-auto w-16 h-16 bg-gradient-to-r from-green-400 to-green-600 rounded-xl flex items-center justify-center">
                        <Check className="w-8 h-8 text-white" />
                      </div>
                      <div>
                        <div className="text-gray-900 font-semibold text-lg">{file.name}</div>
                        <div className="text-sm text-gray-600 mt-1">Click to change file</div>
                      </div>
                      <SuccessIndicator text="File Ready" showCheckmark={false} />
                    </motion.div>
                  ) : (
                    <motion.div
                      key="file-empty"
                      initial={{ opacity: 0, scale: 0.8 }}
                      animate={{ opacity: 1, scale: 1 }}
                      exit={{ opacity: 0, scale: 0.8 }}
                      className="space-y-4"
                    >
                      <div className="mx-auto w-16 h-16 bg-gradient-to-r from-gray-100 to-gray-200 rounded-xl flex items-center justify-center">
                        <Upload className="w-8 h-8 text-gray-400" />
                      </div>
                      <div>
                        <div className="text-gray-900 font-semibold text-lg">
                          {dragActive ? 'Drop your resume here' : 'Drop your resume here'}
                        </div>
                        <div className="text-sm text-gray-600 mt-2">or click to browse files</div>
                      </div>
                      <div className="flex items-center justify-center space-x-4 text-xs text-gray-500">
                        <div className="flex items-center">
                          <div className="w-3 h-3 bg-red-500 rounded mr-1"></div>
                          PDF
                        </div>
                        <div className="flex items-center">
                          <div className="w-3 h-3 bg-blue-500 rounded mr-1"></div>
                          DOCX
                        </div>
                        <div className="flex items-center">
                          <div className="w-3 h-3 bg-green-500 rounded mr-1"></div>
                          TXT
                        </div>
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </label>
            </motion.div>
          )}

          {/* Text Input Tab */}
          {activeTab === 'text' && (
            <div 
              className="space-y-4"
              role="tabpanel"
              id="text-input-panel"
              aria-labelledby="text-input-tab"
            >
              <div className="flex items-center gap-2">
                <FileText className="w-5 h-5 text-blue-600" />
                <label htmlFor="resume-textarea" className="text-sm font-medium text-gray-700">
                  Paste or type your resume
                </label>
              </div>
              
              <textarea
                ref={textareaRef}
                id="resume-textarea"
                value={resumeText || ''}
                onChange={handleTextChange}
                placeholder="Paste your resume text here..."
                className="w-full h-48 p-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none font-mono text-sm"
                aria-describedby="resume-textarea-help"
                onKeyDown={(e) => {
                  // Allow Ctrl+A, Ctrl+C, Ctrl+V, etc.
                  if (e.ctrlKey || e.metaKey) return;
                  
                  // Announce character count on Ctrl+Shift+C
                  if (e.ctrlKey && e.shiftKey && e.key === 'c') {
                    e.preventDefault();
                    announceToScreenReader(`${resumeText?.length || 0} characters entered`);
                  }
                }}
              />
              
              <div id="resume-textarea-help" className="text-xs text-gray-500">
                Press Ctrl+Shift+C to hear character count
              </div>
              
              {resumeText && (
                <div className="flex items-center justify-between text-sm text-gray-600">
                  <SuccessIndicator text="Resume text ready" showCheckmark={false} />
                  <span aria-live="polite">{resumeText.length} characters</span>
                </div>
              )}
            </div>
          )}

          {/* File Preview Section */}
          <AnimatePresence>
            {(file || resumeText?.trim()) && showPreview && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="mt-6"
              >
                <div className="p-4 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg border border-blue-200">
                  <h4 className="text-sm font-medium text-gray-700 mb-3 flex items-center gap-2">
                    <FileText className="w-4 h-4 text-blue-600" />
                    File Preview
                    {isLoadingPreview && (
                      <motion.div
                        animate={{ rotate: 360 }}
                        transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                        className="w-4 h-4 border-2 border-blue-600 border-t-transparent rounded-full"
                      />
                    )}
                  </h4>
                  
                  <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
                    <div className="p-3 bg-gray-50 border-b border-gray-200 flex items-center gap-2">
                      <div className="flex gap-1">
                        <div className="w-2 h-2 bg-red-400 rounded-full"></div>
                        <div className="w-2 h-2 bg-yellow-400 rounded-full"></div>
                        <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                      </div>
                      <span className="text-xs text-gray-500 font-medium">
                        {file ? file.name : 'Resume Text'}
                      </span>
                    </div>
                    
                    <div className="p-4 max-h-40 overflow-y-auto">
                      {isLoadingPreview ? (
                        <div className="flex items-center gap-2 text-gray-500">
                          <LightningIcon size={16} animation="pulse" />
                          <span className="text-sm">Processing file content...</span>
                        </div>
                      ) : (
                        <pre className="text-xs text-gray-700 whitespace-pre-wrap font-mono leading-relaxed">
                          {getFilePreview()}
                        </pre>
                      )}
                    </div>
                  </div>
                  
                  {file && (
                    <div className="mt-3 flex items-center justify-between text-xs text-gray-600">
                      <div className="flex items-center gap-4">
                        <span>Size: {(file.size / 1024).toFixed(1)} KB</span>
                        <span>Type: {file.type.split('/').pop().toUpperCase()}</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <Check className="w-3 h-3 text-green-500" />
                        <span className="text-green-600">Ready for processing</span>
                      </div>
                    </div>
                  )}
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Scan for Issues Section */}
          {(file || resumeText?.trim()) && (
            <div className="mt-6 space-y-4">
              <Button
                ref={scanButtonRef}
                onClick={handleScanForIssues}
                disabled={isScanning}
                className="w-full bg-gradient-to-r from-purple-500 to-blue-600 hover:from-purple-600 hover:to-blue-700 text-white"
                aria-describedby="scan-button-help"
                aria-live="polite"
                aria-busy={isScanning}
              >
                {isScanning ? (
                  <AIActionIndicator isActive={true}>
                    Scanning Resume...
                  </AIActionIndicator>
                ) : (
                  <div className="flex items-center gap-2">
                    <LightningIcon size={16} animation="pulse" />
                    Scan for Issues
                  </div>
                )}
              </Button>
              
              <div id="scan-button-help" className="text-xs text-gray-500 text-center">
                Press 'S' key to scan resume for issues
              </div>

              {/* Scan Results */}
              <AnimatePresence>
                {scanResults && (
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -20 }}
                    className="space-y-4"
                  >
                    {/* Score Header */}
                    <div className="p-4 bg-gradient-to-r from-green-50 to-blue-50 border border-green-200 rounded-lg">
                      <div className="flex items-center justify-between mb-3">
                        <SuccessIndicator 
                          text={`Resume Score: ${scanResults.score}/100`} 
                          showCheckmark={true}
                        />
                        <div className="text-xs text-gray-600 bg-white px-2 py-1 rounded-full">
                          ATS: {scanResults.atsCompatibility}
                        </div>
                      </div>
                      
                      {/* Score Bar */}
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <motion.div
                          className="bg-gradient-to-r from-green-400 to-blue-500 h-2 rounded-full"
                          initial={{ width: 0 }}
                          animate={{ width: `${scanResults.score}%` }}
                          transition={{ duration: 1, ease: "easeOut" }}
                        />
                      </div>
                    </div>

                    {/* Strengths Section */}
                    <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
                      <h5 className="text-sm font-medium text-gray-700 mb-3 flex items-center gap-2">
                        <div className="w-4 h-4 bg-green-500 rounded-full flex items-center justify-center">
                          <Check className="w-2.5 h-2.5 text-white" />
                        </div>
                        Strengths Detected
                      </h5>
                      <ul className="space-y-2">
                        {scanResults.strengths.map((strength, index) => (
                          <motion.li
                            key={index}
                            initial={{ opacity: 0, x: -10 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ delay: index * 0.1 }}
                            className="flex items-start gap-2 text-xs text-gray-700"
                          >
                            <SuccessIndicator 
                              text="" 
                              showCheckmark={true}
                              className="mt-0.5"
                            />
                            <LightningIcon size={12} animation="bounce" />
                            <span>{strength}</span>
                          </motion.li>
                        ))}
                      </ul>
                    </div>

                    {/* Improvements Section */}
                    {scanResults.improvements.length > 0 && (
                      <div className="p-4 bg-amber-50 border border-amber-200 rounded-lg">
                        <h5 className="text-sm font-medium text-gray-700 mb-3 flex items-center gap-2">
                          <LightningIcon size={16} animation="pulse" />
                          AI Suggestions for Improvement
                        </h5>
                        <ul className="space-y-2">
                          {scanResults.improvements.map((improvement, index) => (
                            <motion.li
                              key={index}
                              initial={{ opacity: 0, x: -10 }}
                              animate={{ opacity: 1, x: 0 }}
                              transition={{ delay: index * 0.1 + 0.5 }}
                              className="flex items-start gap-2 text-xs text-gray-700"
                            >
                              <LightningIcon size={12} animation="idle" />
                              <span>{improvement}</span>
                            </motion.li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {/* Keywords Section */}
                    <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
                      <h5 className="text-sm font-medium text-gray-700 mb-3 flex items-center gap-2">
                        <LightningIcon size={16} animation="glow" />
                        Recommended Keywords
                      </h5>
                      <div className="flex flex-wrap gap-2">
                        {scanResults.keywords.map((keyword, index) => (
                          <motion.span
                            key={index}
                            initial={{ opacity: 0, scale: 0.8 }}
                            animate={{ opacity: 1, scale: 1 }}
                            transition={{ delay: index * 0.1 + 1 }}
                            className="px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded-full border border-blue-200"
                          >
                            {keyword}
                          </motion.span>
                        ))}
                      </div>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          )}
        </EnhancedCardContent>
      </EnhancedCard>
    </motion.div>
  );
};

export default AddResumeCard;
import React, { useState } from 'react'

const FileUpload = React.memo(({ file, onFileChange, resumeText, onResumeTextChange }) => {
  const [activeTab, setActiveTab] = useState('file')
  const [showSample, setShowSample] = useState(false)

  const handleDragOver = (e) => {
    e.preventDefault()
    e.stopPropagation()
  }

  const handleDrop = (e) => {
    e.preventDefault()
    e.stopPropagation()
    
    const droppedFile = e.dataTransfer.files[0]
    if (droppedFile && (droppedFile.type === 'application/pdf' || 
        droppedFile.type === 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' ||
        droppedFile.type === 'text/plain')) {
      onFileChange({ target: { files: [droppedFile] } })
    }
  }

  const handleTextChange = (e) => {
    onResumeTextChange(e.target.value)
  }

  const sampleResumeText = `[Your Name]
[Your Address]
[City, State ZIP Code]
[Phone Number]
[Email Address]

PROFESSIONAL SUMMARY
Experienced software engineer with 5+ years of experience in full-stack development, specializing in React, Node.js, and cloud technologies. Proven track record of delivering scalable applications and leading cross-functional teams.

TECHNICAL SKILLS
• Programming Languages: JavaScript, Python, TypeScript, Java
• Frontend: React, Next.js, HTML5, CSS3, Tailwind CSS
• Backend: Node.js, Express, Python, REST APIs
• Databases: PostgreSQL, MongoDB, Redis
• Cloud & DevOps: AWS, Docker, Kubernetes, CI/CD

EXPERIENCE

Senior Software Engineer | Tech Company Inc. | 2020 - Present
• Led development of web applications serving 100,000+ users
• Improved application performance by 40% through code optimization
• Mentored 3 junior developers and conducted technical interviews
• Collaborated with product managers to define technical requirements

Software Engineer | Startup Co. | 2018 - 2020
• Developed responsive web applications using React and Node.js
• Implemented automated testing reducing bugs by 30%
• Participated in agile development processes and sprint planning
• Maintained and optimized legacy systems

EDUCATION
Bachelor of Science in Computer Science | University Name | 2018
• Relevant Coursework: Data Structures, Algorithms, Software Engineering
• GPA: 3.8/4.0

PROJECTS
• E-commerce Platform: Built full-stack application with React and Node.js
• Task Management App: Developed mobile-responsive web application
• Open Source Contributor: Contributed to popular JavaScript libraries`

  const insertSample = () => {
    onResumeTextChange(sampleResumeText)
    setShowSample(false)
  }

  return (
    <div className="bg-white/80 backdrop-light rounded-2xl shadow-lg border border-white/50 p-8 transition-all duration-300 hover:shadow-xl hover:bg-white/90 scroll-optimized">
      <div className="flex items-center gap-4 mb-6">
        <div className="p-4 bg-gradient-to-r from-blue-500 to-purple-600 rounded-xl shadow-lg">
          <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
          </svg>
        </div>
        <div>
          <h2 className="text-xl font-bold text-gray-900">Add Resume</h2>
          <p className="text-sm text-gray-600 mt-1">Upload a file or paste your resume text</p>
        </div>
      </div>
      
      {/* Tab Navigation */}
      <div className="flex mb-6 bg-gray-100 rounded-lg p-1">
        <button
          onClick={() => setActiveTab('file')}
          className={`flex-1 py-2 px-4 text-sm font-medium rounded-md transition-all duration-200 ${
            activeTab === 'file'
              ? 'bg-white text-blue-600 shadow-sm'
              : 'text-gray-500 hover:text-gray-700'
          }`}
        >
          <svg className="w-4 h-4 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
          </svg>
          Upload File
        </button>
        <button
          onClick={() => setActiveTab('text')}
          className={`flex-1 py-2 px-4 text-sm font-medium rounded-md transition-all duration-200 ${
            activeTab === 'text'
              ? 'bg-white text-blue-600 shadow-sm'
              : 'text-gray-500 hover:text-gray-700'
          }`}
        >
          <svg className="w-4 h-4 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
          </svg>
          Type/Paste Text
        </button>
      </div>

      {/* File Upload Tab */}
      {activeTab === 'file' && (
        <div 
          className="relative border-2 border-dashed border-gray-300 rounded-2xl p-8 text-center hover:border-blue-400 transition-all duration-300 bg-gradient-to-br from-gray-50/50 to-blue-50/30"
          onDragOver={handleDragOver}
          onDrop={handleDrop}
        >
          <input
            type="file"
            accept=".pdf,.docx,.txt"
            onChange={onFileChange}
            className="hidden"
            id="file-upload"
          />
          
          <label htmlFor="file-upload" className="cursor-pointer block">
            {file ? (
              <div className="space-y-4 animate-fadeIn">
                <div className="mx-auto w-20 h-20 bg-gradient-to-r from-green-400 to-green-600 rounded-2xl flex items-center justify-center shadow-lg">
                  <svg className="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <div>
                  <div className="text-gray-900 font-semibold text-lg">{file.name}</div>
                  <div className="text-sm text-gray-600 mt-1">Click to change file</div>
                </div>
                <div className="inline-flex items-center px-4 py-2 bg-green-100 text-green-800 rounded-full text-sm font-medium">
                  <svg className="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                  File Ready
                </div>
              </div>
            ) : (
              <div className="space-y-4">
                <div className="mx-auto w-20 h-20 bg-gradient-to-r from-gray-100 to-gray-200 rounded-2xl flex items-center justify-center shadow-inner">
                  <svg className="w-10 h-10 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 13h6m-3-3v6m5 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 2 0 01-2 2z" />
                  </svg>
                </div>
                <div>
                  <div className="text-gray-900 font-semibold text-lg">Drop your resume here</div>
                  <div className="text-sm text-gray-600 mt-2">or click to browse files</div>
                </div>
                <div className="flex items-center justify-center space-x-4 text-xs text-gray-500">
                  <div className="flex items-center">
                    <svg className="w-4 h-4 mr-1 text-red-500" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M4 4a2 2 0 00-2 2v8a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-5L9 2H4z" clipRule="evenodd" />
                    </svg>
                    PDF
                  </div>
                  <div className="flex items-center">
                    <svg className="w-4 h-4 mr-1 text-blue-500" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M4 4a2 2 0 00-2 2v8a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-5L9 2H4z" clipRule="evenodd" />
                    </svg>
                    DOCX
                  </div>
                  <div className="flex items-center">
                    <svg className="w-4 h-4 mr-1 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M4 4a2 2 0 00-2 2v8a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-5L9 2H4z" clipRule="evenodd" />
                    </svg>
                    TXT
                  </div>
                </div>
              </div>
            )}
          </label>
        </div>
      )}

      {/* Text Input Tab */}
      {activeTab === 'text' && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
              </svg>
              <span className="text-sm font-medium text-gray-700">Paste or type your resume</span>
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => setShowSample(!showSample)}
                className="text-xs px-3 py-1 bg-blue-100 text-blue-700 rounded-full hover:bg-blue-200 transition-colors"
              >
                {showSample ? 'Hide Sample' : 'View Sample'}
              </button>
              {showSample && (
                <button
                  onClick={insertSample}
                  className="text-xs px-3 py-1 bg-green-100 text-green-700 rounded-full hover:bg-green-200 transition-colors"
                >
                  Use Sample
                </button>
              )}
            </div>
          </div>
          
          {showSample && (
            <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
              <h4 className="text-sm font-medium text-gray-700 mb-2">Sample Resume Format:</h4>
              <pre className="text-xs text-gray-600 whitespace-pre-wrap max-h-40 overflow-y-auto">
                {sampleResumeText}
              </pre>
            </div>
          )}
          
          <textarea
            value={resumeText || ''}
            onChange={handleTextChange}
            placeholder="Paste your resume text here or use the sample format above..."
            className="w-full h-64 p-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none font-mono text-sm"
          />
          
          {resumeText && (
            <div className="flex items-center justify-between text-sm text-gray-600">
              <div className="flex items-center gap-2">
                <svg className="w-4 h-4 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                <span>Resume text ready</span>
              </div>
              <span>{resumeText.length} characters</span>
            </div>
          )}
        </div>
      )}
    </div>
  )
})

export default FileUpload 
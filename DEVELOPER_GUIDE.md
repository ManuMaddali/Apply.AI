# Apply.AI Developer Guide

## 🏗️ System Architecture

Apply.AI is a full-stack application with a React/Next.js frontend and Python/FastAPI backend, designed for AI-powered resume tailoring with comprehensive testing infrastructure.

### Technology Stack

**Frontend**:
- **Framework**: Next.js 14.2.30 with React 18.3.1
- **Styling**: Tailwind CSS with glassmorphism design system
- **State Management**: React hooks (useState, useCallback, useEffect)
- **Performance**: Optimized with React.memo, useCallback, and CSS optimizations
- **Development**: ESLint, PostCSS, and hot reload

**Backend**:
- **Framework**: FastAPI with Python 3.11+
- **AI/ML**: LangChain 0.3.26, OpenAI GPT models
- **Document Processing**: PyPDF2, python-docx, text extraction libraries
- **Job Scraping**: Custom scrapers for LinkedIn, company sites, job boards
- **Vector Storage**: FAISS for RAG-based resume enhancement

## 📁 Project Structure

```
ApplyAI/
├── frontend/                    # Next.js React application
│   ├── components/             # React components
│   │   ├── FileUpload.jsx     # Resume file upload
│   │   ├── JobUrlsInput.jsx   # Job URL input interface
│   │   ├── CoverLetter.jsx    # Cover letter configuration
│   │   ├── OptionalSections.jsx # Resume section options
│   │   ├── OutputSettings.jsx # Output format settings
│   │   ├── ResultCard.jsx     # Result display component
│   │   └── TestingUtils.jsx   # Advanced testing utilities
│   ├── data/                  # Testing data
│   │   ├── testResumes.js     # Test resume database
│   │   └── testJobUrls.js     # Job URL collections
│   ├── pages/                 # Next.js pages
│   │   ├── index.jsx          # Main application page
│   │   ├── testing.jsx        # Testing suite page
│   │   └── _app.jsx           # App configuration
│   ├── styles/               # Global styles
│   │   └── globals.css       # Tailwind + custom CSS
│   ├── package.json          # Frontend dependencies
│   └── next.config.js        # Next.js configuration
├── backend/                  # Python FastAPI backend
│   ├── main.py              # FastAPI application entry
│   ├── routes/              # API route handlers
│   │   ├── batch_processing.py # Batch resume processing
│   │   ├── generate_resumes.py # Resume generation
│   │   ├── scrape_jobs.py      # Job scraping
│   │   └── upload_resume.py    # File upload handling
│   ├── utils/               # Utility modules
│   │   ├── gpt_prompt.py    # AI prompt engineering
│   │   ├── job_scraper.py   # Job scraping logic
│   │   ├── langchain_processor.py # LangChain integration
│   │   ├── resume_diff.py   # Resume comparison
│   │   └── resume_editor.py # Resume processing
│   ├── uploads/             # Temporary file storage
│   ├── outputs/             # Generated resume storage
│   ├── vector_stores/       # FAISS vector databases
│   └── requirements.txt     # Python dependencies
└── docs/                    # Documentation
    ├── TESTING_GUIDE.md     # Testing infrastructure guide
    ├── DEVELOPER_GUIDE.md   # This developer guide
    └── USER_MANUAL.md       # End user documentation
```

## 🔌 API Architecture

### Core Endpoints

#### Resume Upload
```
POST /api/resumes/upload
Content-Type: multipart/form-data

Body: FormData with 'file' field
Supported: PDF, DOCX, TXT

Response:
{
  "success": true,
  "resume_text": "extracted resume content",
  "filename": "original_filename.pdf"
}
```

#### Batch Processing
```
POST /api/batch/process
Content-Type: application/json

Body:
{
  "resume_text": "string",
  "job_urls": ["url1", "url2", ...],
  "use_rag": true,
  "compare_versions": true,
  "output_format": "pdf|text|both",
  "optional_sections": {
    "includeSummary": boolean,
    "includeSkills": boolean,
    "includeEducation": boolean,
    "educationDetails": {...}
  },
  "cover_letter_options": {
    "tone": "professional|enthusiastic|confident|friendly",
    "emphasis": "experience|skills|achievements|education|balanced",
    "additionalInfo": "string"
  }
}

Response:
{
  "success": true,
  "batch_job_id": "uuid",
  "status": "processing"
}
```

#### Status Monitoring
```
GET /api/batch/status/{batch_job_id}

Response:
{
  "success": true,
  "status": {
    "state": "processing|completed|failed",
    "total": number,
    "completed": number,
    "failed": number,
    "current_job": "description"
  }
}
```

#### Results Retrieval
```
GET /api/batch/results/{batch_job_id}

Response:
{
  "success": true,
  "results": [
    {
      "job_url": "string",
      "job_title": "string",
      "tailored_resume": "string",
      "cover_letter": "string|null",
      "enhancement_score": number,
      "status": "success|failed"
    }
  ]
}
```

#### PDF Generation
```
POST /api/batch/generate-pdf
Content-Type: application/json

Body:
{
  "resume_text": "string",
  "job_title": "string",
  "filename": "optional_filename.pdf"
}

Response: Binary PDF file
```

#### Cover Letter PDF
```
POST /api/batch/generate-cover-letter-pdf
Content-Type: application/json

Body:
{
  "cover_letter_text": "string",
  "job_title": "string",
  "filename": "optional_filename.pdf"
}

Response: Binary PDF file
```

#### ZIP Download
```
POST /api/batch/generate-zip
Content-Type: application/json

Body:
{
  "resumes": [resume_objects],
  "batch_id": "string",
  "include_cover_letters": boolean
}

Response: Binary ZIP file
```

## 🧪 Testing Infrastructure API

### Frontend Testing Components

#### TestingUtils Component
```javascript
import TestingUtils from '../components/TestingUtils';

<TestingUtils
  onRunBatchTest={handleBatchTest}
  onRunPerformanceTest={handlePerformanceTest}
/>
```

**Features**:
- Batch testing across multiple scenarios
- Performance testing with latency/memory monitoring
- Results export to JSON
- Quick action buttons for common tests

#### Test Data Structures

**Test Resume Object**:
```javascript
{
  id: 'unique_identifier',
  name: 'Display Name',
  category: 'Industry Category',
  level: 'Experience Level',
  content: 'Full resume text content'
}
```

**Test Scenario Object**:
```javascript
{
  id: 'scenario_id',
  name: 'Display Name',
  resumeId: 'reference_to_test_resume',
  jobUrls: ['url1', 'url2', 'url3'],
  description: 'Scenario description'
}
```

### Testing Page Architecture

**State Management**:
```javascript
// Core application state
const [file, setFile] = useState(null);
const [jobUrls, setJobUrls] = useState('');
const [coverLetterEnabled, setCoverLetterEnabled] = useState(false);

// Testing-specific state
const [selectedTestResume, setSelectedTestResume] = useState('');
const [selectedJobCategory, setSelectedJobCategory] = useState('');
const [testingMode, setTestingMode] = useState('manual');
```

**Key Functions**:
```javascript
// Load test resume into file state
const loadTestResume = useCallback((resumeId) => {
  const resume = testResumes.find(r => r.id === resumeId);
  const mockFile = new File([resume.content], `${resume.name}.txt`);
  setFile(mockFile);
});

// Load job URLs from category
const loadJobUrls = useCallback((category) => {
  const urls = jobUrlCollections[category];
  setJobUrls(urls.slice(0, 3).join('\n'));
});

// Execute testing scenario
const loadTestScenario = useCallback((scenarioId) => {
  const scenario = testScenarios.find(s => s.id === scenarioId);
  loadTestResume(scenario.resumeId);
  setJobUrls(scenario.jobUrls.join('\n'));
});
```

## 🎨 UI/UX Design System

### Design Principles
- **Glassmorphism**: Modern glass-like effects with backdrop blur
- **Performance-First**: Optimized animations and reduced computational load
- **Accessibility**: WCAG compliant with proper contrast and navigation
- **Responsive**: Mobile-first design with breakpoint optimization

### Key Design Elements

**Colors**:
```css
/* Primary Gradients */
--gradient-primary: linear-gradient(to right, #3b82f6, #8b5cf6);
--gradient-secondary: linear-gradient(to right, #10b981, #059669);
--gradient-accent: linear-gradient(to right, #f59e0b, #d97706);

/* Background */
--bg-main: linear-gradient(to bottom right, #f8fafc, #dbeafe, #e0e7ff);

/* Glass Effects */
--glass-light: rgba(255, 255, 255, 0.8);
--backdrop-blur: backdrop-filter: blur(2px);
```

**Typography**:
```css
/* Headers */
.gradient-text {
  background: linear-gradient(to right, #1f2937, #4b5563);
  -webkit-background-clip: text;
  color: transparent;
}

/* Performance Optimized Classes */
.scroll-optimized {
  transform: translateZ(0);
  will-change: transform;
}

.sticky-optimized {
  position: sticky;
  z-index: 10;
  backdrop-filter: blur(2px);
}
```

### Component Architecture

**Base Component Pattern**:
```jsx
const ComponentName = React.memo(({ prop1, prop2, onPropChange }) => {
  const memoizedValue = useMemo(() => computeValue(prop1), [prop1]);
  
  const handleChange = useCallback((newValue) => {
    onPropChange(newValue);
  }, [onPropChange]);

  return (
    <div className="bg-white/80 backdrop-blur-light rounded-xl">
      {/* Component content */}
    </div>
  );
});
```

## 🚀 Performance Optimizations

### Frontend Optimizations

**React Performance**:
```javascript
// Component memoization
const FileUpload = React.memo(({ onFileSelect, selectedFile }) => {
  // Component implementation
});

// Callback optimization
const handleFileChange = useCallback((file) => {
  onFileSelect(file);
}, [onFileSelect]);

// State optimization
const memoizedResults = useMemo(() => 
  results.filter(r => r.status === 'success'), [results]
);
```

**CSS Performance**:
```css
/* Hardware acceleration */
.performance-optimized {
  transform: translateZ(0);
  will-change: transform, opacity;
  backface-visibility: hidden;
}

/* Reduced blur for performance */
.backdrop-light {
  backdrop-filter: blur(2px);
}

/* Optimized animations */
.hover-scale {
  transition: transform 0.2s ease-out;
}
.hover-scale:hover {
  transform: scale(1.05);
}
```

### Backend Optimizations

**Async Processing**:
```python
# Async job processing
async def process_batch_job(batch_id: str, job_data: dict):
    async with aiofiles.open(f"temp/{batch_id}.json", "w") as f:
        await f.write(json.dumps(job_data))
    
    # Process in background
    asyncio.create_task(execute_batch_processing(batch_id))
```

**Caching Strategy**:
```python
# In-memory caching for job descriptions
@lru_cache(maxsize=100)
def get_job_description(url: str) -> str:
    return scrape_job_content(url)

# Vector store caching
def get_or_create_vector_store(resume_text: str):
    cache_key = hashlib.md5(resume_text.encode()).hexdigest()
    if cache_key in vector_cache:
        return vector_cache[cache_key]
    # Create and cache new vector store
```

## 🔧 Development Setup

### Prerequisites
```bash
# Node.js 16+ and npm 8+
node --version  # >= 16.0.0
npm --version   # >= 8.0.0

# Python 3.11+ and pip
python --version  # >= 3.11.0
pip --version
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev  # Development server on localhost:3000
```

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py  # Development server on localhost:8000
```

### Environment Configuration

**Frontend (.env.local)**:
```env
NODE_ENV=development
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**Backend (.env)**:
```env
OPENAI_API_KEY=your_openai_api_key
ENVIRONMENT=development
DEBUG=true
```

## 🧪 Testing Development

### Adding New Test Resumes

1. **Create Resume Content**:
```javascript
// In frontend/data/testResumes.js
{
  id: 'new_test_resume',
  name: 'Professional Name - Title',
  category: 'Industry Category',
  level: 'Experience Level',
  content: `
FULL RESUME CONTENT
Including all sections, formatting, and details
  `
}
```

2. **Add to Categories**:
```javascript
// In frontend/data/testJobUrls.js
export const jobUrlCollections = {
  'New Category': [
    'https://example.com/job1',
    'https://example.com/job2',
    // 3-5 relevant job URLs
  ]
}
```

3. **Create Test Scenarios**:
```javascript
{
  id: 'new_scenario',
  name: 'Scenario Name',
  resumeId: 'new_test_resume',
  jobUrls: jobUrlCollections['New Category'].slice(0, 3),
  description: 'Scenario description for testing'
}
```

### Custom Testing Components

**Creating Advanced Test Utilities**:
```jsx
const CustomTestingComponent = ({ onTestComplete }) => {
  const [testConfig, setTestConfig] = useState({
    iterations: 5,
    measurePerformance: true,
    customMetrics: []
  });

  const executeCustomTest = async () => {
    // Custom test logic
    const results = await runCustomTestSuite(testConfig);
    onTestComplete(results);
  };

  return (
    <div className="custom-testing-panel">
      {/* Custom test configuration UI */}
    </div>
  );
};
```

## 📊 Monitoring and Analytics

### Performance Monitoring
```javascript
// Frontend performance tracking
const trackPerformance = (operation, startTime) => {
  const endTime = performance.now();
  const duration = endTime - startTime;
  
  console.log(`${operation} took ${duration.toFixed(2)}ms`);
  
  // Send to analytics if needed
  if (window.gtag) {
    window.gtag('event', 'timing_complete', {
      name: operation,
      value: Math.round(duration)
    });
  }
};
```

### Error Handling
```javascript
// Global error boundary
class TestingErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Testing component error:', error, errorInfo);
    // Log to external service if needed
  }

  render() {
    if (this.state.hasError) {
      return <TestingErrorFallback error={this.state.error} />;
    }
    return this.props.children;
  }
}
```

## 🔒 Security Considerations

### Frontend Security
- **Environment Variables**: Use NEXT_PUBLIC_ prefix only for client-safe variables
- **Input Validation**: Validate all user inputs including file uploads and URLs
- **XSS Prevention**: Sanitize all user-generated content before rendering
- **HTTPS**: Use secure connections in production

### Backend Security
- **API Authentication**: Implement API key validation for production
- **File Upload Security**: Validate file types, sizes, and content
- **Rate Limiting**: Implement request rate limiting to prevent abuse
- **Data Sanitization**: Clean and validate all input data

## 📚 Additional Resources

### Documentation Links
- [Next.js Documentation](https://nextjs.org/docs)
- [React Documentation](https://react.dev/)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [LangChain Documentation](https://python.langchain.com/)

### Development Tools
- **VS Code Extensions**: ES7+ React/Redux/React-Native, Tailwind CSS IntelliSense
- **Browser DevTools**: React Developer Tools, Redux DevTools
- **Testing Tools**: Jest, React Testing Library, Playwright
- **Performance Tools**: Lighthouse, Web Vitals, React Profiler

---

This developer guide provides comprehensive technical documentation for the Apply.AI system architecture, testing infrastructure, and development practices. For specific implementation questions or troubleshooting, refer to the inline code comments and additional documentation files. 
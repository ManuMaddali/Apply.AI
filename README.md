# 🚀 Apply.AI - AI-Powered Resume Tailoring

**Transform your resume with AI intelligence for every job opportunity**

Apply.AI is an advanced AI-powered resume tailoring application that uses LangChain, RAG (Retrieval-Augmented Generation), and GPT-4o-mini to create perfectly customized resumes for any job opportunity.

## 🎯 **What Makes Apply.AI Special**

### 🔍 **RAG-Enhanced Intelligence**
- **Vector Storage**: FAISS-based system stores job descriptions for intelligent pattern recognition
- **Semantic Search**: Finds similar job postings to provide industry context
- **Industry Intelligence**: Learns from patterns across thousands of job descriptions
- **Context-Aware Prompting**: Uses historical data to improve resume tailoring

### 🎨 **Modern User Experience**
- **Clean Design**: Inspired by Notion, Tome.app, and Jasper.ai
- **Drag-and-Drop Upload**: Intuitive file handling with visual feedback
- **Bulk Processing**: Handle up to 10 job applications simultaneously
- **Smart Status Tracking**: Real-time progress with elegant animations
- **Professional Output**: Beautifully formatted, ATS-optimized PDFs

### 🧠 **Intelligent Customization**
- **Optional Sections**: Choose which sections to include (Professional Summary, Skills, Education)
- **Education Builder**: Comprehensive form for academic credentials
- **Smart Formatting**: One-page optimized with professional typography
- **Content Detection**: Intelligent parsing of names, companies, and achievements

### 💾 **Powered by Advanced AI**
- **LangChain Workflows**: Multi-step reasoning chains for strategic positioning
- **RAG Architecture**: Retrieval-Augmented Generation for contextual improvements
- **GPT-4o-mini**: Latest language model for natural, professional content
- **Vector Embeddings**: Semantic understanding of job requirements

## 🏗️ **Technical Architecture**

```
Frontend (Next.js + TailwindCSS)
    ↓
Backend API (FastAPI)
    ↓
LangChain Processor ←→ Vector Store (FAISS)
    ↓                      ↓
OpenAI GPT-4o-mini    Job Descriptions DB
    ↓
Professional PDF Generator
    ↓
Tailored Resume Output
```

## 🚀 **Quick Start**

### Prerequisites
- **Python 3.8+** with pip
- **Node.js 16+** with npm
- **OpenAI API Key** ([Get one here](https://platform.openai.com/api-keys))

### 1. Clone & Setup
```bash
git clone <your-repo-url>
cd ApplyAI

# Run the complete setup (installs everything)
./setup.sh
```

### 2. Configure OpenAI
```bash
# Edit the backend/.env file
nano backend/.env

# Add your OpenAI API key
OPENAI_API_KEY=sk-your-actual-api-key-here
```

### 3. Launch Apply.AI
```bash
# Starts both backend and frontend
./run.sh
```

### 4. Access the Application
- **Apply.AI Interface**: http://localhost:3000
- **Backend API**: http://localhost:8000  
- **API Documentation**: http://localhost:8000/docs

### 5. Stop the App
```bash
./stop.sh
```

## 🎯 **How to Use Apply.AI**

### **Step 1: Upload Your Resume**
- **Drag & Drop**: Simply drop your PDF or DOCX file
- **File Preview**: See your uploaded file with format confirmation
- **Instant Processing**: Automatic text extraction and parsing

### **Step 2: Add Job Opportunities**
- **Multiple Jobs**: Add up to 10 job URLs at once
- **Job Counter**: Track how many positions you're applying to
- **URL Validation**: Automatic detection of job posting URLs
- **Smart Extraction**: Pulls job titles, companies, and requirements

### **Step 3: Customize Your Resume**
- **Output Format**: Choose PDF or Text format
- **Optional Sections**: Select which sections to include:
  - ✅ Professional Summary
  - ✅ Skills Section
  - ✅ Education Details (with comprehensive form)
- **Smart Defaults**: Reasonable presets for quick processing

### **Step 4: Generate Tailored Resumes**
- **Bulk Processing**: One click generates resumes for all jobs
- **Live Progress**: "✨ Tailoring resume for [Company]..." updates
- **Smart Status**: Real-time feedback with completion indicators

### **Step 5: Review and Download**
- **Result Cards**: Clean cards showing job title and company
- **Status Indicators**: ✅ Success, ❌ Error, ⏳ Processing
- **Download Options**: Individual or bulk download
- **Resume Comparison**: Side-by-side view of original vs tailored

## 🔥 **Key Features**

### **🎨 Modern Interface**
- ✅ Clean, minimalist design
- ✅ Intuitive drag-and-drop upload
- ✅ Real-time progress animations
- ✅ Responsive layout for all devices
- ✅ Professional color scheme and typography

### **📄 Professional Output**
- ✅ ATS-optimized formatting
- ✅ One-page layout optimization
- ✅ Professional fonts (Helvetica family)
- ✅ Consistent bullet point styling
- ✅ Smart content spacing and margins

### **🔍 AI Intelligence**
- ✅ Strategic keyword integration
- ✅ Industry-specific language adaptation
- ✅ Achievement reframing for target roles
- ✅ Skills section optimization
- ✅ Company-specific customization

### **⚡ Bulk Processing**
- ✅ Handle up to 10 jobs simultaneously
- ✅ Efficient batch processing
- ✅ Individual status tracking
- ✅ Bulk download options
- ✅ Error handling and retry logic

## 🛠️ **Technical Stack**

### **Frontend**
- **Next.js 13+**: React framework with modern features
- **TailwindCSS**: Utility-first styling framework
- **React Hooks**: Modern state management
- **Framer Motion**: Smooth animations and transitions
- **Axios**: HTTP client for API communication

### **Backend**  
- **FastAPI**: High-performance async API framework
- **LangChain**: Advanced AI workflow orchestration
- **OpenAI GPT-4o-mini**: Latest language model
- **FAISS**: Vector similarity search
- **BeautifulSoup**: Web scraping for job postings
- **ReportLab**: Professional PDF generation

### **AI & ML**
- **RAG Architecture**: Retrieval-Augmented Generation
- **Vector Embeddings**: OpenAI text-embedding-ada-002
- **Multi-step Workflows**: LangChain reasoning chains
- **Semantic Search**: Intelligent job matching

## 📊 **Performance & Quality**

Apply.AI delivers:
- **Professional Quality**: Industry-standard resume formatting
- **ATS Compatibility**: Optimized for applicant tracking systems
- **One-Page Layout**: Efficient space utilization
- **Fast Processing**: Bulk generation in seconds
- **High Accuracy**: Maintains factual information integrity

## 🔧 **Advanced Configuration**

### **Environment Variables (.env)**
```bash
# OpenAI Configuration
OPENAI_API_KEY=sk-your-key-here
EMBEDDING_MODEL=text-embedding-ada-002

# LangChain Settings
LANGCHAIN_VERBOSE=False
LANGCHAIN_CACHE=True

# Vector Store Configuration  
VECTOR_STORE_PATH=./vector_stores
MAX_SIMILAR_JOBS=5

# Processing Limits
MAX_FILE_SIZE=10485760  # 10MB
MAX_CONTENT_LENGTH=50000
TEMPERATURE=0.1
```

### **Customization Options**
- **Optional Sections**: Configure which resume sections to include
- **Education Details**: Comprehensive academic credential forms
- **Output Formats**: PDF (default) or plain text
- **Processing Mode**: RAG-enhanced vs standard processing

## 🚀 **Deployment Options**

### **Local Development**
```bash
./run.sh  # Development mode with hot reload
```

### **Production Deployment**
```bash
# Backend
cd backend
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker

# Frontend  
cd frontend
npm run build
npm start
```

### **Docker Deployment**
```bash
# Coming soon - Docker Compose configuration
docker-compose up -d
```

## 🤝 **Contributing**

We welcome contributions to Apply.AI! Areas for enhancement:
- Additional job board integrations
- More output format options
- Advanced customization features
- Industry-specific templates
- Mobile app development

## 📈 **Roadmap**

### **Version 2.1** (Next Release)
- [ ] LinkedIn integration
- [ ] Custom template system
- [ ] Advanced formatting options
- [ ] Mobile-responsive improvements

### **Version 2.2** (Future)
- [ ] Multi-language support
- [ ] Industry-specific models
- [ ] Team collaboration features
- [ ] Advanced analytics dashboard

## 🐛 **Troubleshooting**

### **Common Issues**

**Backend won't start:**
```bash
# Check Python version
python3 --version  # Should be 3.8+

# Reinstall dependencies
cd backend
source resume_env/bin/activate
pip install -r requirements.txt
```

**Frontend build errors:**
```bash
# Clear cache and reinstall
cd frontend
rm -rf node_modules package-lock.json
npm install
```

**OpenAI API errors:**
- Verify API key in `backend/.env`
- Check API quota and billing
- Ensure key has proper permissions

### **Performance Issues**

**Slow processing:**
- Reduce number of simultaneous jobs
- Check internet connection for job URL fetching
- Restart application: `./stop.sh && ./run.sh`

**PDF formatting issues:**
- Ensure resume content isn't too lengthy
- Check for special characters in input
- Verify PDF output directory permissions

## 📞 **Support**

- **Documentation**: Read `PROJECT_STRUCTURE.md` for detailed architecture
- **Issues**: Check logs with `tail -f backend.log` or `tail -f frontend.log`
- **API Reference**: Visit http://localhost:8000/docs when running

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**🎉 Ready to transform your job search with Apply.AI?**

```bash
./setup.sh && ./run.sh
```

*Built with ❤️ using LangChain, OpenAI, Next.js, and TailwindCSS*

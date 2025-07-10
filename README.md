# 🚀 Apply.AI - AI-Powered Resume Tailoring

**"AI resumes that get jobs"** - Transform your resume for every job opportunity with intelligent AI customization.

Apply.AI uses advanced AI to create perfectly tailored resumes for any job posting. Simply upload your resume, paste job URLs, and get professionally formatted, ATS-optimized resumes in seconds.

## ✨ **What Apply.AI Does**

- 🎯 **Smart Tailoring**: AI analyzes job descriptions and customizes your resume accordingly
- 📄 **Perfect Formatting**: Professional, ATS-friendly PDFs that get past screening systems
- ⚡ **Bulk Processing**: Handle up to 10 job applications at once
- 🎨 **Modern Interface**: Clean, intuitive design with drag-and-drop functionality
- 🔍 **Intelligent Analysis**: Uses advanced language models to match your skills to job requirements

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
# Create backend/.env file
echo "OPENAI_API_KEY=sk-your-actual-api-key-here" > backend/.env
```

### 3. Launch Apply.AI
```bash
# Starts both backend and frontend
./run.sh
```

### 4. Open in Browser
- **Apply.AI Interface**: http://localhost:3000
- **Backend API**: http://localhost:8000  

### 5. Stop the App
```bash
./stop.sh
```

## 🎯 **How to Use**

### **Step 1: Upload Your Resume**
- Drag & drop your PDF or DOCX file
- Supports most common resume formats
- Automatic text extraction and parsing

### **Step 2: Add Job URLs**
- Paste job posting URLs (up to 10 at once)
- Works with most major job boards
- Automatic job title and company extraction

### **Step 3: Customize Options**
- **Output Format**: PDF, DOCX, or both
- **Optional Sections**: Add Professional Summary, Skills, or Education
- **Cover Letters**: Generate matching cover letters

### **Step 4: Generate & Download**
- Click "Generate Resumes" 
- Watch real-time progress updates
- Download individual files or bulk zip

## 🔥 **Key Features**

### **🎨 Modern User Experience**
- ✅ Clean, professional interface
- ✅ Drag-and-drop file upload
- ✅ Real-time progress tracking
- ✅ Mobile-responsive design

### **📄 Professional Output**
- ✅ ATS-optimized formatting
- ✅ Consistent professional styling
- ✅ Perfect bullet point formatting
- ✅ One-page layout optimization

### **🧠 AI Intelligence**
- ✅ GPT-4 powered customization
- ✅ Industry-specific language adaptation
- ✅ Strategic keyword integration
- ✅ Achievement reframing for target roles

### **⚡ Bulk Processing**
- ✅ Process multiple jobs simultaneously
- ✅ Individual progress tracking
- ✅ Batch download options
- ✅ Error handling and recovery

## 🛠️ **Technical Stack**

### **Frontend**
- **Next.js**: React framework with modern features
- **TailwindCSS**: Utility-first styling
- **Framer Motion**: Smooth animations

### **Backend**  
- **FastAPI**: High-performance API framework
- **LangChain**: AI workflow orchestration
- **OpenAI GPT-4**: Advanced language processing
- **ReportLab**: Professional PDF generation

### **AI Features**
- **RAG Architecture**: Retrieval-Augmented Generation
- **Vector Embeddings**: Semantic job matching
- **Smart Parsing**: Intelligent content extraction

## 📊 **What You Get**

Apply.AI delivers:
- **Professional Quality**: Industry-standard formatting
- **ATS Compatibility**: Optimized for applicant tracking systems
- **Fast Processing**: Bulk generation in seconds
- **Consistent Results**: Reliable output every time
- **Zero Text Loss**: Perfect PDF generation with no truncation

## 🔧 **Configuration**

### **Environment Variables**
```bash
# Backend (.env)
OPENAI_API_KEY=sk-your-key-here
EMBEDDING_MODEL=text-embedding-ada-002
TEMPERATURE=0.1
MAX_FILE_SIZE=10485760  # 10MB

# Frontend (.env.local) - Optional
ENABLE_TESTING_SUITE=false  # Enable developer testing features
```

### **🧪 Testing Suite (Optional)**
For developers, enable comprehensive testing features:
```bash
# Enable testing suite
echo "ENABLE_TESTING_SUITE=true" > frontend/.env.local
./stop.sh && ./run.sh
```

**Testing Features:**
- Pre-configured test resumes and job URLs
- Batch testing scenarios
- Performance measurement
- API endpoint testing

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

**Frontend errors:**
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
- Check internet connection
- Restart: `./stop.sh && ./run.sh`

**PDF formatting issues:**
- ✅ **Fixed**: Zero text truncation with latest updates
- All content renders perfectly with new PDF engine

## 📈 **Roadmap**

### **Upcoming Features**
- [ ] LinkedIn profile optimization
- [ ] Custom resume templates
- [ ] Advanced formatting options
- [ ] Mobile app support
- [ ] Team collaboration features

### **Future Enhancements**
- [ ] Multi-language support
- [ ] Industry-specific models
- [ ] Interview preparation AI
- [ ] Advanced analytics

## 🤝 **Contributing**

We welcome contributions! Areas for enhancement:
- Additional job board integrations
- More output format options
- Advanced customization features
- Industry-specific templates
- Mobile app development

### **Development Setup**
```bash
# Fork and clone
git clone <your-fork-url>
cd ApplyAI

# Create feature branch
git checkout -b feature/amazing-feature

# Make changes and test
./run.sh

# Submit pull request
git push origin feature/amazing-feature
```

## 📞 **Support**

### **Documentation**
- **Architecture**: `PROJECT_STRUCTURE.md`
- **API Reference**: http://localhost:8000/docs (when running)

### **Getting Help**
- **Backend Logs**: `tail -f backend.log`
- **Frontend Logs**: `tail -f frontend.log`
- **Health Check**: http://localhost:8000/health

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🎉 **Ready to Get Started?**

Transform your job search with AI-powered resume tailoring:

```bash
./setup.sh && ./run.sh
```

**Built with ❤️ using LangChain, OpenAI, Next.js, and TailwindCSS**

*Get the job you deserve with Apply.AI* 🚀

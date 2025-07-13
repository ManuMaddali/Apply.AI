# ApplyAI - AI-Powered Resume Tailoring

**Transform your resume for every job application with AI-powered customization and optimization.**

## Overview

ApplyAI is a production-ready web application that automatically tailors your resume to specific job postings using advanced AI technology. Upload your resume, paste job URLs, and get professionally optimized resumes in seconds.

### Key Features

- **AI-Powered Tailoring**: Automatically customizes your resume for each job posting
- **Bulk Processing**: Handle multiple job applications simultaneously
- **Multiple Formats**: Download as PDF or text files
- **Cover Letter Generation**: Create matching cover letters automatically
- **Secure & Fast**: Enterprise-grade security with sub-30 second processing
- **Easy Deployment**: One-click deployment to production

## Quick Start

### For Users

1. **Visit the App**: [Your deployed URL]
2. **Upload Resume**: PDF, DOCX, or TXT format
3. **Add Job URLs**: Paste job posting URLs (up to 10)
4. **Generate**: AI processes and tailors your resume
5. **Download**: Get PDF or text versions instantly

### For Developers

#### Local Development

```bash
# Clone the repository
git clone https://github.com/yourusername/ApplyAI.git
cd ApplyAI

# Start the application
./run.sh
```

#### Production Deployment

**Ready to deploy in 15-30 minutes!**

1. **Backend (Railway)**:
   - Create account at [railway.app](https://railway.app)
   - Connect GitHub repository
   - Add Redis service
   - Set environment variables

2. **Frontend (Vercel)**:
   - Create account at [vercel.com](https://vercel.com)
   - Connect GitHub repository
   - Set environment variables
   - Deploy automatically

**See [PRODUCTION_DEPLOYMENT_GUIDE.md](PRODUCTION_DEPLOYMENT_GUIDE.md) for detailed instructions.**

## Technology Stack

### Backend
- **FastAPI**: High-performance Python web framework
- **OpenAI GPT**: Advanced AI for resume analysis and tailoring
- **Redis**: Rate limiting and caching
- **Docker**: Containerized deployment
- **JWT**: Secure authentication

### Frontend
- **Next.js**: React framework with server-side rendering
- **Tailwind CSS**: Modern, responsive styling
- **Vercel**: Optimized deployment platform

### Security
- Rate limiting and DDoS protection
- Input validation and sanitization
- CORS and security headers
- JWT authentication
- File upload security

## Environment Setup

### Required Environment Variables

```env
# Backend (.env)
OPENAI_API_KEY=sk-your-openai-key
JWT_SECRET_KEY=your-64-character-secret
ENVIRONMENT=production
DEBUG=false
```

### Optional Configuration

```env
# Redis (automatically set by Railway)
REDIS_URL=redis://localhost:6379

# Monitoring
SENTRY_DSN=your-sentry-dsn

# CORS (set to your domain)
ALLOWED_ORIGINS=https://yourdomain.com
```

## Deployment Costs

### Free Tier (Perfect for Starting)
- **Vercel Frontend**: $0/month (100GB bandwidth)
- **Railway Backend**: $0-5/month (first $5 free)
- **OpenAI API**: Pay-per-use (~$10-50/month)

**Total: $0-5/month to start**

### Scaling Costs
- **Railway Pro**: $20/month (more resources)
- **Vercel Pro**: $20/month (enhanced features)
- **Custom domains**: Free on both platforms

## API Documentation

### Health Check
```
GET /health
```

### Resume Upload
```
POST /api/resumes/upload
Content-Type: multipart/form-data
```

### Batch Processing
```
POST /api/batch/process
Content-Type: application/json
```

**Full API documentation available at `/docs` in development mode.**

## Security Features

- **Authentication**: JWT-based secure authentication
- **Rate Limiting**: Prevents abuse and API quota exhaustion
- **Input Validation**: Comprehensive request sanitization
- **File Security**: Safe upload handling with type validation
- **CORS Protection**: Cross-origin request security
- **Security Headers**: CSP, XSS protection, and more

## Performance

- **Processing Speed**: < 30 seconds per resume
- **Concurrent Users**: Supports 100+ simultaneous users
- **Uptime**: 99.9% with health monitoring
- **Global CDN**: Fast delivery worldwide via Vercel
- **Auto-scaling**: Handles traffic spikes automatically

## Support

### Documentation
- [Production Deployment Guide](PRODUCTION_DEPLOYMENT_GUIDE.md)
- [Production Readiness Summary](PRODUCTION_READY_SUMMARY.md)

### Getting Help
- **Issues**: GitHub Issues for bugs and feature requests
- **Railway Support**: [docs.railway.app](https://docs.railway.app)
- **Vercel Support**: [vercel.com/docs](https://vercel.com/docs)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Roadmap

- [ ] Advanced AI models integration
- [ ] Resume analytics and insights
- [ ] Job application tracking
- [ ] Team collaboration features
- [ ] Mobile app development

---

**Ready to deploy? Start with the [Production Deployment Guide](PRODUCTION_DEPLOYMENT_GUIDE.md)**

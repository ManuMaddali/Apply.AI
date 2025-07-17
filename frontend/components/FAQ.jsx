import React, { useState } from 'react'
import { 
  ChevronDown, 
  ChevronUp,
  FileText, 
  Cpu, 
  Shield, 
  Clock,
  Sparkles,
  BarChart,
  Globe,
  AlertTriangle,
  User,
  Download,
  FlaskConical,
  GraduationCap
} from 'lucide-react'

const FAQ = () => {
  const [openSection, setOpenSection] = useState(null)

  const toggleSection = (index) => {
    setOpenSection(openSection === index ? null : index)
  }

  const faqSections = [
    {
      title: "Getting Started",
      icon: User,
      color: "text-blue-600",
      bgColor: "bg-blue-50",
      questions: [
        {
          question: "How do I get started with tailoring my resume?",
          answer: "Simply upload your resume in PDF, DOCX, or TXT format, then paste the job URLs you're interested in (up to 10 at once). Our AI will analyze the job requirements and automatically tailor your resume to match each position. The entire process takes under 30 seconds per resume."
        },
        {
          question: "What file formats are supported for resume uploads?",
          answer: "We support PDF, DOCX (Microsoft Word), and TXT files. Maximum file size is 10MB. For best results, use a clean, well-formatted resume with clear sections for experience, education, and skills."
        },
        {
          question: "Can I process multiple jobs at once?",
          answer: "Yes! You can paste up to 10 job URLs at once and our system will generate tailored resumes for each position simultaneously. This bulk processing feature saves you hours of manual work."
        },
        {
          question: "Do I need to create an account to use the service?",
          answer: "Yes, you need to create a free account to use the service. We offer multiple signup options including email, Google, LinkedIn, and GitHub. Creating an account allows you to track your usage, save your progress, and access all features based on your plan."
        },
        {
          question: "What authentication options are available?",
          answer: "You can sign up and login using your email address, Google account, LinkedIn profile, or GitHub account. All authentication methods provide the same access to features and are equally secure."
        },
        {
          question: "How do I reset my password?",
          answer: "If you signed up with email, you can reset your password by clicking 'Forgot Password' on the login page. We'll send you a secure reset link. If you signed up with a social provider (Google, LinkedIn, GitHub), you'll need to reset your password through that provider."
        },
        {
          question: "What are the different plan tiers?",
          answer: "We offer two plans: Free (3 resumes/month with basic features) and Pro ($19/month with unlimited resumes, advanced AI features, priority support, and cover letter generation). The Pro plan includes a 7-day free trial."
        }
      ]
    },
    {
      title: "AI Technology & Features",
      icon: Cpu,
      color: "text-purple-600",
      bgColor: "bg-purple-50",
      questions: [
        {
          question: "How does the AI resume tailoring work?",
          answer: "Our AI uses advanced LangChain technology with RAG (Retrieval-Augmented Generation) to analyze job descriptions and your resume. It understands job requirements, identifies key skills and keywords, then intelligently rewrites your experience to match each position while maintaining truthfulness and professional quality."
        },
        {
          question: "What is RAG technology and how does it help?",
          answer: "RAG (Retrieval-Augmented Generation) uses a knowledge base of successful resumes and job patterns to provide context-aware recommendations. It learns from patterns in successful applications, provides industry-specific insights, and improves recommendations by analyzing similar job postings."
        },
        {
          question: "Will the AI make up fake experiences or skills?",
          answer: "Absolutely not. Our AI is designed to transform and optimize your existing experiences, not fabricate new ones. It reframes your actual achievements using language that better matches job requirements while preserving all factual information."
        },
        {
          question: "How accurate is the job description scraping?",
          answer: "Our intelligent scraping system works with major job boards including LinkedIn, Indeed, Greenhouse, Lever, and most standard job posting websites. It extracts key requirements, skills, and company information with high accuracy, even from complex job posting formats."
        }
      ]
    },
    {
      title: "ATS Optimization & Results",
      icon: BarChart,
      color: "text-green-600",
      bgColor: "bg-green-50",
      questions: [
        {
          question: "Are the tailored resumes ATS-friendly?",
          answer: "Yes! All our resumes are optimized for Applicant Tracking Systems (ATS). We use proper formatting, keyword optimization, appropriate section headers, and clean structure that ATS software can easily parse. 75% of resumes fail ATS screening - ours are designed to pass."
        },
        {
          question: "How much do tailored resumes typically improve my chances?",
          answer: "Tailored resumes significantly improve your callback rates because they match job requirements more closely. Our ATS-optimized formatting increases visibility to recruiters, while targeted keywords and relevant experience positioning help you stand out from generic applications."
        },
        {
          question: "Can I see what changed in my resume?",
          answer: "Yes! Our diff analysis feature shows you exactly what changed between your original and tailored resume. You'll see side-by-side comparisons, detailed explanations of each change, and impact assessments to help you understand the optimization process."
        },
        {
          question: "What if I don't like the tailored version?",
          answer: "You can always download your original resume unchanged. We also provide detailed diff analysis so you can see exactly what was modified. The tailoring process is designed to enhance your existing content, not replace it entirely."
        }
      ]
    },
    {
      title: "Security & Privacy",
      icon: Shield,
      color: "text-red-600",
      bgColor: "bg-red-50",
      questions: [
        {
          question: "Is my resume data secure and private?",
          answer: "Yes, we take security seriously. We use enterprise-grade encryption, JWT authentication, and comprehensive security headers. All uploaded files are automatically deleted after 24 hours, and we have a strict no-data-retention policy."
        },
        {
          question: "What happens to my data after processing?",
          answer: "Your resume and job data are processed securely and deleted automatically after 24 hours. We don't store your personal information, resumes, or job applications permanently. The processing is done in real-time with immediate cleanup."
        },
        {
          question: "Do you share my information with third parties?",
          answer: "No, we never share your personal information or resume data with third parties. Your data is used solely for the resume tailoring service and is deleted after processing. We don't sell data or use it for any other purposes."
        },
        {
          question: "How is rate limiting implemented for security?",
          answer: "We implement rate limiting to prevent abuse and ensure fair usage. This protects against spam and maintains service quality for all users. If you hit rate limits, simply wait a moment before trying again."
        }
      ]
    },
    {
      title: "Advanced Features",
      icon: Sparkles,
      color: "text-indigo-600",
      bgColor: "bg-indigo-50",
      questions: [
        {
          question: "Can you generate matching cover letters?",
          answer: "Yes! Our AI can generate professional cover letters that complement your tailored resume. The cover letters maintain consistency in tone, highlight relevant experience, and are customized for each specific job application."
        },
        {
          question: "What is batch processing and how does it work?",
          answer: "Batch processing allows you to upload your resume once and tailor it for multiple job postings simultaneously. You can process up to 10 jobs at once, saving hours of manual work while maintaining consistent quality across all applications."
        },
        {
          question: "Can I get industry-specific insights?",
          answer: "Yes! Our AI provides data-driven recommendations based on successful resumes and hiring patterns in your target industry. This includes trending skills, salary insights, and company culture alignment information."
        },
        {
          question: "How does session management work?",
          answer: "Session management allows you to track your resume tailoring history, compare different versions, and analyze your improvement over time. You can see which approaches work best for your goals and optimize your strategy accordingly."
        }
      ]
    },
    {
      title: "Performance & Reliability",
      icon: Clock,
      color: "text-yellow-600",
      bgColor: "bg-yellow-50",
      questions: [
        {
          question: "How long does it take to process a resume?",
          answer: "Processing is very fast - typically under 30 seconds per resume. Batch processing of multiple jobs is completed in under 2 minutes. The system is designed for real-time processing with immediate results."
        },
        {
          question: "What if the service is temporarily unavailable?",
          answer: "We maintain 99.9% uptime with auto-scaling infrastructure and global CDN. If you encounter issues, the system has built-in error handling and will automatically retry failed requests. For persistent issues, try refreshing the page or contact support."
        },
        {
          question: "Are there any file size or content limits?",
          answer: "Resume files can be up to 10MB in size. You can process up to 10 job URLs per batch. There are no strict limits on resume content length, but very long resumes may take slightly longer to process."
        },
        {
          question: "Does the system work with international job postings?",
          answer: "Yes! Our system works with job postings from around the world and can adapt to different regional resume formats and industry standards. The AI understands various job posting formats and requirements."
        }
      ]
    },
    {
      title: "Troubleshooting",
      icon: AlertTriangle,
      color: "text-orange-600",
      bgColor: "bg-orange-50",
      questions: [
        {
          question: "My resume upload failed. What should I do?",
          answer: "Ensure your file is in PDF, DOCX, or TXT format and under 10MB. Check that the file isn't corrupted and contains readable text. If the issue persists, try converting your file to PDF format or using a different browser."
        },
        {
          question: "The job URL isn't working. What's wrong?",
          answer: "Make sure you're using the direct URL to the job posting (not a search results page). Some job boards require specific URL formats. If a URL consistently fails, try copying the job description text directly into the system instead."
        },
        {
          question: "The generated resume doesn't look right. What happened?",
          answer: "This can happen if the original resume has unusual formatting or if the job description is very brief. Try using a cleaner source resume format or providing more detailed job descriptions. The diff analysis can help identify what was changed."
        },
        {
          question: "I'm getting a 'rate limit exceeded' error. What should I do?",
          answer: "This means you've made too many requests in a short time. Wait a few minutes before trying again. Rate limiting helps ensure fair usage and service quality for all users."
        },
        {
          question: "The processing is taking longer than expected. Is something wrong?",
          answer: "While processing usually takes under 30 seconds, complex resumes or high server load can cause slight delays. If it takes more than 2 minutes, try refreshing the page and restarting the process."
        }
      ]
    },
    {
      title: "Output & Downloads",
      icon: Download,
      color: "text-cyan-600",
      bgColor: "bg-cyan-50",
      questions: [
        {
          question: "What formats can I download my tailored resume in?",
          answer: "You can download your tailored resume in professional PDF format (recommended for applications) or clean text format (useful for ATS systems and further editing). Both formats maintain professional formatting and structure."
        },
        {
          question: "Can I download all my tailored resumes at once?",
          answer: "Yes! When using batch processing, you can download all your tailored resumes as a convenient ZIP file. Each resume is clearly labeled with the job title and company name for easy organization."
        },
        {
          question: "Are the downloaded resumes ready to submit immediately?",
          answer: "Absolutely! All downloads are professionally formatted and ready for submission. The PDF format is optimized for both human readers and ATS systems, with consistent typography and clean layout."
        },
        {
          question: "How long can I access my processed resumes?",
          answer: "Due to our privacy policy, processed resumes are available for download for 24 hours after processing. After that, they're automatically deleted from our servers. Make sure to download your results promptly."
        }
      ]
    }
  ]

  return (
    <div className="max-w-4xl mx-auto">
      <div className="text-center mb-12">
        <h2 className="text-4xl font-bold text-gray-900 mb-4">
          Frequently Asked Questions
        </h2>
        <p className="text-xl text-gray-600 max-w-2xl mx-auto">
          Everything you need to know about using our AI resume tailoring service
        </p>
      </div>

      <div className="space-y-6">
        {faqSections.map((section, sectionIndex) => (
          <div key={sectionIndex} className="bg-white rounded-lg shadow-lg overflow-hidden">
            <button
              onClick={() => toggleSection(sectionIndex)}
              className={`w-full px-6 py-4 ${section.bgColor} border-b border-gray-200 hover:opacity-90 transition-opacity`}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <section.icon className={`h-6 w-6 ${section.color}`} />
                  <span className="text-lg font-semibold text-gray-900">
                    {section.title}
                  </span>
                </div>
                {openSection === sectionIndex ? (
                  <ChevronUp className="h-5 w-5 text-gray-500" />
                ) : (
                  <ChevronDown className="h-5 w-5 text-gray-500" />
                )}
              </div>
            </button>
            
            {openSection === sectionIndex && (
              <div className="p-6 space-y-6">
                {section.questions.map((qa, qaIndex) => (
                  <div key={qaIndex} className="border-b border-gray-100 last:border-b-0 pb-6 last:pb-0">
                    <h3 className="text-lg font-semibold text-gray-900 mb-3">
                      {qa.question}
                    </h3>
                    <p className="text-gray-700 leading-relaxed">
                      {qa.answer}
                    </p>
                  </div>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Contact Support Section */}
      <div className="mt-12 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-8 text-center">
        <h3 className="text-2xl font-bold text-gray-900 mb-4">
          Still have questions?
        </h3>
        <p className="text-gray-600 mb-6">
          Our support team is here to help you get the most out of our AI resume tailoring service.
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <button className="bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors">
            Contact Support
          </button>
          <button className="border border-blue-600 text-blue-600 px-6 py-3 rounded-lg font-semibold hover:bg-blue-50 transition-colors">
            View Documentation
          </button>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-6 text-center">
        <div className="bg-white rounded-lg p-6 shadow-lg">
          <div className="text-3xl font-bold text-blue-600 mb-2">&lt;30s</div>
          <div className="text-gray-600">Average processing time</div>
        </div>
        <div className="bg-white rounded-lg p-6 shadow-lg">
          <div className="text-3xl font-bold text-green-600 mb-2">99.9%</div>
          <div className="text-gray-600">Service uptime</div>
        </div>
        <div className="bg-white rounded-lg p-6 shadow-lg">
          <div className="text-3xl font-bold text-purple-600 mb-2">10+</div>
          <div className="text-gray-600">Job boards supported</div>
        </div>
      </div>
    </div>
  )
}

export default FAQ 
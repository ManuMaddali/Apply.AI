"use client"

import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { 
  FileText, 
  Target, 
  Zap, 
  Award, 
  BarChart, 
  Users, 
  Download, 
  Mail,
  Search,
  Brain,
  Clock,
  Shield,
  TrendingUp,
  CheckCircle,
  ArrowRight,
  ChevronRight,
  Sparkles,
  Layers,
  Settings,
  FileCheck,
  Globe,
  Lightbulb,
  Rocket,
  Star,
  Upload,
  Wand2,
  Eye,
  Database,
  Cpu,
  Network,
  Code,
  Workflow,
  GitBranch,
  Play,
  Monitor,
  Puzzle
} from "lucide-react"
import { useState } from "react"

export default function HowItWorksPage() {
  const [activeView, setActiveView] = useState('user')

  const userSteps = [
    {
      step: "1",
      title: "Upload Your Resume",
      description: "Simply drag and drop your resume in PDF, DOCX, or TXT format. Our secure system processes and analyzes your experience, skills, and achievements.",
      icon: Upload,
      details: [
        "Supports PDF, DOCX, and TXT formats",
        "Automatic text extraction and parsing",
        "Secure processing with 24-hour auto-cleanup",
        "Professional formatting preservation"
      ]
    },
    {
      step: "2",
      title: "Add Job URLs",
      description: "Paste up to 10 job posting URLs from major job boards. Our AI automatically scrapes and analyzes the job requirements.",
      icon: Globe,
      details: [
        "Works with LinkedIn, Indeed, Greenhouse, and 100+ job boards",
        "Automatic job title and company extraction",
        "Requirement analysis and keyword identification",
        "Company culture and value alignment"
      ]
    },
    {
      step: "3",
      title: "AI Processing",
      description: "Our advanced AI analyzes job requirements and tailors your resume to match each position perfectly, optimizing for ATS systems.",
      icon: Brain,
      details: [
        "Keyword optimization for ATS compatibility",
        "Experience reframing to match job requirements",
        "Skills highlighting and emphasis",
        "Achievement quantification and impact focus"
      ]
    },
    {
      step: "4",
      title: "Review & Download",
      description: "Get professionally formatted, tailored resumes in seconds. Review changes, download in multiple formats, and apply with confidence.",
      icon: Download,
      details: [
        "Professional PDF format ready for submission",
        "Side-by-side comparison with original",
        "Multiple format options (PDF, text)",
        "Optional cover letter generation"
      ]
    }
  ]

  const techComponents = [
    {
      title: "LangChain Integration",
      description: "Advanced language model orchestration for intelligent resume processing and contextual understanding.",
      icon: Code,
      details: [
        "Multi-step reasoning chains for complex resume transformations",
        "Prompt engineering for consistent, high-quality outputs",
        "Memory systems for context-aware processing",
        "Adaptive learning from user interactions"
      ]
    },
    {
      title: "RAG (Retrieval-Augmented Generation)",
      description: "Leverages a knowledge base of successful resumes and job patterns to provide data-driven recommendations.",
      icon: Database,
      details: [
        "FAISS vector database for semantic similarity search",
        "Job description embeddings for pattern matching",
        "Historical resume data for industry insights",
        "Dynamic context injection for enhanced accuracy"
      ]
    },
    {
      title: "FAISS Vector Store",
      description: "High-performance vector database for semantic search and similarity matching across job descriptions.",
      icon: Network,
      details: [
        "Facebook AI Similarity Search (FAISS) implementation",
        "Dense vector embeddings for job descriptions",
        "Sub-second similarity search across thousands of jobs",
        "Hierarchical clustering for improved recall"
      ]
    },
    {
      title: "Intelligent Web Scraping",
      description: "Sophisticated scraping system that extracts structured data from diverse job board formats.",
      icon: Globe,
      details: [
        "BeautifulSoup with intelligent parsing heuristics",
        "Dynamic content handling for JavaScript-heavy sites",
        "Rate limiting and respectful crawling practices",
        "Structured data extraction with fallback mechanisms"
      ]
    },
    {
      title: "Document Processing Pipeline",
      description: "Robust text extraction and processing pipeline for handling various resume formats.",
      icon: FileText,
      details: [
        "Multi-format support (PDF, DOCX, TXT)",
        "Intelligent text extraction with layout preservation",
        "Section detection and content categorization",
        "Error handling and format validation"
      ]
    },
    {
      title: "Diff Analysis Engine",
      description: "Advanced comparison system that tracks and analyzes changes between resume versions.",
      icon: GitBranch,
      details: [
        "Section-by-section change tracking",
        "Semantic similarity scoring",
        "Visual diff highlighting",
        "Impact assessment and improvement metrics"
      ]
    }
  ]

  const architectureFlow = [
    {
      phase: "Input Processing",
      description: "Resume and job data ingestion",
      components: ["File Upload", "Text Extraction", "Job Scraping", "Data Validation"]
    },
    {
      phase: "AI Analysis",
      description: "Intelligent content analysis and matching",
      components: ["RAG Retrieval", "Similarity Search", "Context Building", "Prompt Engineering"]
    },
    {
      phase: "Content Generation",
      description: "Tailored resume creation",
      components: ["LangChain Processing", "Content Transformation", "ATS Optimization", "Quality Assurance"]
    },
    {
      phase: "Output Delivery",
      description: "Formatted results and analytics",
      components: ["PDF Generation", "Diff Analysis", "Performance Metrics", "User Interface"]
    }
  ]

  return (
    <div className="flex min-h-[100dvh] flex-col bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
      {/* Header */}
      <header className="px-4 lg:px-6 h-16 flex items-center justify-between border-b bg-white/80 backdrop-blur-sm sticky top-0 z-50">
        <Link className="flex items-center gap-2 font-semibold" href="/">
          <FileText className="h-6 w-6 text-blue-600" />
          <span>ApplyAI</span>
        </Link>
        <nav className="hidden md:flex gap-6">
          <Link className="text-sm font-medium hover:underline underline-offset-4" href="/">
            Home
          </Link>
          <Link className="text-sm font-medium hover:underline underline-offset-4" href="/features">
            Features
          </Link>
          <Link className="text-sm font-medium hover:underline underline-offset-4 text-blue-600" href="/how-it-works">
            How It Works
          </Link>
          <Link className="text-sm font-medium hover:underline underline-offset-4" href="/faq">
            FAQ
          </Link>
          <Link className="text-sm font-medium hover:underline underline-offset-4" href="/about">
            About
          </Link>
          <Link className="text-sm font-medium hover:underline underline-offset-4" href="/blog">
            Blog
          </Link>
          <Link className="text-sm font-medium hover:underline underline-offset-4" href="/contact">
            Contact
          </Link>
        </nav>
        <div className="flex gap-4">
          <Link href="/app">
            <Button variant="outline">Try Now</Button>
          </Link>
          <Link href="/app">
            <Button className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700">
              Get Started
            </Button>
          </Link>
        </div>
      </header>

      <main className="flex-1">
        {/* Hero Section */}
        <section className="w-full py-16 md:py-24">
          <div className="container px-4 md:px-6">
            <div className="text-center max-w-4xl mx-auto">
              <div className="inline-block rounded-lg bg-gradient-to-r from-blue-100 to-purple-100 px-3 py-1 text-sm text-blue-800 mb-4">
                <Lightbulb className="inline h-4 w-4 mr-1" />
                Behind the Scenes
              </div>
              <h1 className="text-4xl md:text-6xl font-bold tracking-tight mb-6 bg-gradient-to-r from-gray-900 to-gray-600 bg-clip-text text-transparent">
                How <span className="text-blue-600">ApplyAI</span> Works
              </h1>
              <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto leading-relaxed">
                Discover the technology and process behind our AI-powered resume tailoring system. From simple user interactions to sophisticated AI processing.
              </p>
              
              {/* Toggle between user and technical views */}
              <div className="flex justify-center mb-8">
                <div className="bg-white/80 backdrop-blur-sm rounded-lg p-1 border">
                  <button
                    onClick={() => setActiveView('user')}
                    className={`px-6 py-3 rounded-md font-medium transition-all ${
                      activeView === 'user' 
                        ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-sm' 
                        : 'text-gray-600 hover:text-gray-900'
                    }`}
                  >
                    <Users className="inline h-4 w-4 mr-2" />
                    For Users
                  </button>
                  <button
                    onClick={() => setActiveView('technical')}
                    className={`px-6 py-3 rounded-md font-medium transition-all ${
                      activeView === 'technical' 
                        ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-sm' 
                        : 'text-gray-600 hover:text-gray-900'
                    }`}
                  >
                    <Code className="inline h-4 w-4 mr-2" />
                    For Developers
                  </button>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* User-Friendly Section */}
        {activeView === 'user' && (
          <>
            <section className="w-full py-16 md:py-24 bg-white/80 backdrop-blur-sm">
              <div className="container px-4 md:px-6">
                <div className="text-center max-w-3xl mx-auto mb-16">
                  <div className="inline-block rounded-lg bg-gradient-to-r from-blue-100 to-purple-100 px-3 py-1 text-sm text-blue-800 mb-4">
                    <Play className="inline h-4 w-4 mr-1" />
                    Step-by-Step Process
                  </div>
                  <h2 className="text-3xl md:text-4xl font-bold mb-4">
                    From Resume to Interview in 4 Simple Steps
                  </h2>
                  <p className="text-lg text-gray-600">
                    Our streamlined process makes resume tailoring effortless, helping you land more interviews with less effort.
                  </p>
                </div>

                <div className="max-w-6xl mx-auto">
                  {userSteps.map((step, index) => (
                    <div key={index} className="mb-16 last:mb-0">
                      <div className="grid lg:grid-cols-2 gap-12 items-center">
                        <div className={`${index % 2 === 1 ? 'lg:order-2' : ''}`}>
                          <div className="flex items-center gap-4 mb-6">
                            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-r from-blue-600 to-purple-600 text-white font-bold text-lg">
                              {step.step}
                            </div>
                            <step.icon className="h-8 w-8 text-blue-600" />
                          </div>
                          <h3 className="text-2xl font-bold mb-4">{step.title}</h3>
                          <p className="text-gray-600 mb-6 text-lg leading-relaxed">{step.description}</p>
                          <ul className="space-y-2">
                            {step.details.map((detail, detailIndex) => (
                              <li key={detailIndex} className="flex items-start gap-2">
                                <CheckCircle className="h-5 w-5 text-green-500 mt-0.5 flex-shrink-0" />
                                <span className="text-gray-700">{detail}</span>
                              </li>
                            ))}
                          </ul>
                        </div>
                        <div className={`${index % 2 === 1 ? 'lg:order-1' : ''}`}>
                          <Card className="bg-gradient-to-br from-blue-50 to-purple-50 border-none shadow-lg">
                            <CardContent className="p-8">
                              <div className="flex items-center justify-center h-48 rounded-lg bg-white/50 backdrop-blur-sm">
                                <step.icon className="h-24 w-24 text-blue-600 opacity-20" />
                              </div>
                            </CardContent>
                          </Card>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </section>

            {/* Why It Works Section */}
            <section className="w-full py-16 md:py-24 bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
              <div className="container px-4 md:px-6">
                <div className="text-center max-w-3xl mx-auto mb-16">
                  <div className="inline-block rounded-lg bg-gradient-to-r from-blue-100 to-purple-100 px-3 py-1 text-sm text-blue-800 mb-4">
                    <Target className="inline h-4 w-4 mr-1" />
                    Why It Works
                  </div>
                  <h2 className="text-3xl md:text-4xl font-bold mb-4">
                    The Science Behind Better Resumes
                  </h2>
                  <p className="text-lg text-gray-600">
                    Our approach is grounded in data science, AI technology, and deep understanding of hiring processes.
                  </p>
                </div>

                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8 max-w-6xl mx-auto">
                  {[
                    {
                      icon: Target,
                      title: "ATS Optimization",
                      description: "75% of resumes are rejected by ATS systems. Our AI ensures your resume passes these filters by optimizing keywords, formatting, and structure."
                    },
                    {
                      icon: Brain,
                      title: "AI-Powered Matching",
                      description: "Advanced language models analyze job requirements and match them with your experience, creating natural, compelling narratives."
                    },
                    {
                      icon: Database,
                      title: "Data-Driven Insights",
                      description: "We analyze thousands of successful resumes and job postings to identify patterns that lead to interview success."
                    },
                    {
                      icon: Zap,
                      title: "Speed & Accuracy",
                      description: "What takes hours manually is done in seconds with higher accuracy, consistency, and professional quality."
                    },
                    {
                      icon: Shield,
                      title: "Professional Quality",
                      description: "Every output maintains professional standards with proper formatting, grammar, and industry-appropriate language."
                    },
                    {
                      icon: TrendingUp,
                      title: "Proven Results",
                      description: "Users report 3x more interviews and 40% faster job placement when using tailored resumes vs. generic ones."
                    }
                  ].map((item, index) => (
                    <Card key={index} className="bg-white/80 backdrop-blur-sm border-none shadow-sm hover:shadow-md transition-shadow">
                      <CardHeader>
                        <item.icon className="h-10 w-10 text-blue-600 mb-2" />
                        <CardTitle className="text-xl">{item.title}</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <p className="text-gray-600">{item.description}</p>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </div>
            </section>
          </>
        )}

        {/* Technical Section */}
        {activeView === 'technical' && (
          <>
            <section className="w-full py-16 md:py-24 bg-white/80 backdrop-blur-sm">
              <div className="container px-4 md:px-6">
                <div className="text-center max-w-3xl mx-auto mb-16">
                  <div className="inline-block rounded-lg bg-gradient-to-r from-blue-100 to-purple-100 px-3 py-1 text-sm text-blue-800 mb-4">
                    <Cpu className="inline h-4 w-4 mr-1" />
                    Technical Architecture
                  </div>
                  <h2 className="text-3xl md:text-4xl font-bold mb-4">
                    LangChain + RAG + FAISS Implementation
                  </h2>
                  <p className="text-lg text-gray-600">
                    Deep dive into our technical stack and how we leverage cutting-edge AI technologies for superior resume processing.
                  </p>
                </div>

                <div className="grid md:grid-cols-2 gap-8 max-w-6xl mx-auto">
                  {techComponents.map((component, index) => (
                    <Card key={index} className="bg-gradient-to-br from-blue-50 to-purple-50 border-none shadow-lg hover:shadow-xl transition-shadow">
                      <CardHeader>
                        <div className="flex items-center gap-3 mb-4">
                          <component.icon className="h-8 w-8 text-blue-600" />
                          <CardTitle className="text-xl">{component.title}</CardTitle>
                        </div>
                        <CardDescription className="text-gray-700 text-base">
                          {component.description}
                        </CardDescription>
                      </CardHeader>
                      <CardContent>
                        <ul className="space-y-2">
                          {component.details.map((detail, detailIndex) => (
                            <li key={detailIndex} className="flex items-start gap-2">
                              <Code className="h-4 w-4 text-blue-600 mt-1 flex-shrink-0" />
                              <span className="text-gray-700 text-sm">{detail}</span>
                            </li>
                          ))}
                        </ul>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </div>
            </section>

            {/* Architecture Flow */}
            <section className="w-full py-16 md:py-24 bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
              <div className="container px-4 md:px-6">
                <div className="text-center max-w-3xl mx-auto mb-16">
                  <div className="inline-block rounded-lg bg-gradient-to-r from-blue-100 to-purple-100 px-3 py-1 text-sm text-blue-800 mb-4">
                    <Workflow className="inline h-4 w-4 mr-1" />
                    Processing Pipeline
                  </div>
                  <h2 className="text-3xl md:text-4xl font-bold mb-4">
                    Data Flow & Processing Architecture
                  </h2>
                  <p className="text-lg text-gray-600">
                    Understanding how data flows through our system from input to optimized output.
                  </p>
                </div>

                <div className="max-w-6xl mx-auto">
                  <div className="grid md:grid-cols-4 gap-8">
                    {architectureFlow.map((phase, index) => (
                      <div key={index} className="relative">
                        <Card className="bg-white/80 backdrop-blur-sm border-none shadow-lg h-full">
                          <CardHeader className="text-center">
                            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-r from-blue-600 to-purple-600 text-white font-bold text-lg mx-auto mb-4">
                              {index + 1}
                            </div>
                            <CardTitle className="text-lg">{phase.phase}</CardTitle>
                            <CardDescription className="text-sm">{phase.description}</CardDescription>
                          </CardHeader>
                          <CardContent>
                            <ul className="space-y-2">
                              {phase.components.map((component, componentIndex) => (
                                <li key={componentIndex} className="flex items-center gap-2">
                                  <div className="h-2 w-2 rounded-full bg-blue-600"></div>
                                  <span className="text-xs text-gray-700">{component}</span>
                                </li>
                              ))}
                            </ul>
                          </CardContent>
                        </Card>
                        {index < architectureFlow.length - 1 && (
                          <div className="hidden md:block absolute top-1/2 -right-4 transform -translate-y-1/2">
                            <ArrowRight className="h-6 w-6 text-blue-600" />
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </section>

            {/* Technical Details */}
            <section className="w-full py-16 md:py-24 bg-white/80 backdrop-blur-sm">
              <div className="container px-4 md:px-6">
                <div className="text-center max-w-3xl mx-auto mb-16">
                  <div className="inline-block rounded-lg bg-gradient-to-r from-blue-100 to-purple-100 px-3 py-1 text-sm text-blue-800 mb-4">
                    <Settings className="inline h-4 w-4 mr-1" />
                    Implementation Details
                  </div>
                  <h2 className="text-3xl md:text-4xl font-bold mb-4">
                    Key Technical Specifications
                  </h2>
                  <p className="text-lg text-gray-600">
                    Detailed technical information about our implementation and performance characteristics.
                  </p>
                </div>

                <div className="grid md:grid-cols-2 gap-8 max-w-6xl mx-auto">
                  <Card className="bg-gradient-to-br from-blue-50 to-purple-50 border-none shadow-lg">
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <Brain className="h-6 w-6 text-blue-600" />
                        LangChain Integration
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <div>
                        <h4 className="font-semibold mb-2">Multi-Step Processing</h4>
                        <p className="text-gray-700 text-sm">Utilizes LangChain's chain abstraction for complex, multi-step resume transformations with context preservation.</p>
                      </div>
                      <div>
                        <h4 className="font-semibold mb-2">Prompt Engineering</h4>
                        <p className="text-gray-700 text-sm">Sophisticated prompting system with dynamic template injection and context-aware generation.</p>
                      </div>
                      <div>
                        <h4 className="font-semibold mb-2">Memory Systems</h4>
                        <p className="text-gray-700 text-sm">Conversation memory for maintaining context across multiple processing steps and user interactions.</p>
                      </div>
                    </CardContent>
                  </Card>

                  <Card className="bg-gradient-to-br from-blue-50 to-purple-50 border-none shadow-lg">
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <Database className="h-6 w-6 text-blue-600" />
                        RAG Implementation
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <div>
                        <h4 className="font-semibold mb-2">Vector Store</h4>
                        <p className="text-gray-700 text-sm">FAISS-based vector database for efficient similarity search across job descriptions and resume patterns.</p>
                      </div>
                      <div>
                        <h4 className="font-semibold mb-2">Embedding Strategy</h4>
                        <p className="text-gray-700 text-sm">Dense embeddings for semantic similarity with hierarchical clustering for improved retrieval performance.</p>
                      </div>
                      <div>
                        <h4 className="font-semibold mb-2">Context Injection</h4>
                        <p className="text-gray-700 text-sm">Dynamic context augmentation based on similar job patterns and successful resume examples.</p>
                      </div>
                    </CardContent>
                  </Card>

                  <Card className="bg-gradient-to-br from-blue-50 to-purple-50 border-none shadow-lg">
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <Network className="h-6 w-6 text-blue-600" />
                        Performance Metrics
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <div>
                        <h4 className="font-semibold mb-2">Processing Speed</h4>
                        <p className="text-gray-700 text-sm">Sub-30 second processing time for complete resume tailoring with quality assurance.</p>
                      </div>
                      <div>
                        <h4 className="font-semibold mb-2">Accuracy</h4>
                        <p className="text-gray-700 text-sm">95%+ keyword matching accuracy with natural language integration and ATS optimization.</p>
                      </div>
                      <div>
                        <h4 className="font-semibold mb-2">Scalability</h4>
                        <p className="text-gray-700 text-sm">Auto-scaling architecture supporting concurrent processing of multiple resume tailoring requests.</p>
                      </div>
                    </CardContent>
                  </Card>

                  <Card className="bg-gradient-to-br from-blue-50 to-purple-50 border-none shadow-lg">
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <Monitor className="h-6 w-6 text-blue-600" />
                        Technology Stack
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <div>
                        <h4 className="font-semibold mb-2">Backend</h4>
                        <p className="text-gray-700 text-sm">FastAPI + LangChain + OpenAI GPT-4o-mini with FAISS vector storage and Redis caching.</p>
                      </div>
                      <div>
                        <h4 className="font-semibold mb-2">Frontend</h4>
                        <p className="text-gray-700 text-sm">Next.js + React + Tailwind CSS with real-time processing status and responsive design.</p>
                      </div>
                      <div>
                        <h4 className="font-semibold mb-2">Infrastructure</h4>
                        <p className="text-gray-700 text-sm">Docker containerization with horizontal scaling and automated deployment pipeline.</p>
                      </div>
                    </CardContent>
                  </Card>
                </div>
              </div>
            </section>
          </>
        )}

        {/* Call to Action */}
        <section className="w-full py-16 md:py-24 bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
          <div className="container px-4 md:px-6">
            <div className="text-center max-w-3xl mx-auto">
              <div className="inline-block rounded-lg bg-gradient-to-r from-blue-100 to-purple-100 px-3 py-1 text-sm text-blue-800 mb-4">
                <Rocket className="inline h-4 w-4 mr-1" />
                Ready to Get Started?
              </div>
              <h2 className="text-3xl md:text-4xl font-bold mb-4">
                Transform Your Job Search Today
              </h2>
              <p className="text-lg text-gray-600 mb-8">
                Join thousands of job seekers who have already improved their interview success rate with ApplyAI.
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <Link href="/app">
                  <Button size="lg" className="gap-2 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700">
                    <Play className="h-5 w-5" />
                    Try ApplyAI Free
                  </Button>
                </Link>
                <Link href="/features">
                  <Button size="lg" variant="outline" className="gap-2">
                    <FileText className="h-5 w-5" />
                    Explore Features
                  </Button>
                </Link>
              </div>
            </div>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="border-t bg-white/80 backdrop-blur-sm">
        <div className="container px-4 md:px-6 py-8">
          <div className="text-center">
            <p className="text-gray-600">
              © 2024 ApplyAI. All rights reserved. Built with LangChain, RAG, and FAISS.
            </p>
          </div>
        </div>
      </footer>
    </div>
  )
} 
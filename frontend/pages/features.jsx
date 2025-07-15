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
  Star
} from "lucide-react"
import { useState } from "react"

export default function FeaturesPage() {
  const [activeCategory, setActiveCategory] = useState('core')

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
          <Link className="text-sm font-medium hover:underline underline-offset-4 text-blue-600" href="/features">
            Features
          </Link>
          <Link className="text-sm font-medium hover:underline underline-offset-4" href="/how-it-works">
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
                <Sparkles className="inline h-4 w-4 mr-1" />
                Comprehensive Feature Overview
              </div>
              <h1 className="text-4xl md:text-6xl font-bold tracking-tight mb-6 bg-gradient-to-r from-gray-900 to-gray-600 bg-clip-text text-transparent">
                Everything You Need to <span className="text-blue-600">Stand Out</span>
              </h1>
              <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto leading-relaxed">
                ApplyAI combines cutting-edge AI technology with deep industry insights to transform your resume for every opportunity. Discover how our features work together to maximize your interview success.
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <Link href="/app">
                  <Button size="lg" className="gap-2 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700">
                    <Rocket className="h-5 w-5" />
                    Try All Features Free
                  </Button>
                </Link>
                <Link href="/how-it-works">
                  <Button size="lg" variant="outline" className="gap-2">
                    <FileText className="h-5 w-5" />
                    See How It Works
                  </Button>
                </Link>
              </div>
            </div>
          </div>
        </section>

        {/* Feature Categories */}
        <section className="w-full py-16 bg-white/80 backdrop-blur-sm">
          <div className="container px-4 md:px-6">
            <div className="text-center mb-12">
              <h2 className="text-3xl font-bold tracking-tight mb-4">Choose Your Feature Category</h2>
              <p className="text-gray-600 max-w-2xl mx-auto">
                Explore our comprehensive feature set organized by functionality to find exactly what you need.
              </p>
            </div>
            
            <div className="flex flex-wrap justify-center gap-4 mb-12">
              {categories.map((category) => (
                <Button
                  key={category.id}
                  variant={activeCategory === category.id ? "default" : "outline"}
                  onClick={() => setActiveCategory(category.id)}
                  className={`gap-2 ${activeCategory === category.id ? 'bg-gradient-to-r from-blue-600 to-purple-600' : ''}`}
                >
                  <category.icon className="h-4 w-4" />
                  {category.name}
                </Button>
              ))}
            </div>

            {/* Active Category Features */}
            <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-3">
              {allFeatures
                .filter(feature => feature.category === activeCategory)
                .map((feature, index) => (
                  <Card key={index} className="group hover:shadow-lg transition-all duration-300 border-0 shadow-sm bg-white/80 backdrop-blur-sm hover:bg-white/90">
                    <CardHeader className="pb-4">
                      <div className="flex items-start gap-4">
                        <div className="p-2 rounded-lg bg-gradient-to-r from-blue-100 to-purple-100 group-hover:from-blue-200 group-hover:to-purple-200 transition-all duration-300">
                          <feature.icon className="h-6 w-6 text-blue-600" />
                        </div>
                        <div className="flex-1">
                          <CardTitle className="text-lg mb-2 group-hover:text-blue-600 transition-colors">
                            {feature.title}
                          </CardTitle>
                          <CardDescription className="text-sm text-gray-600 leading-relaxed">
                            {feature.description}
                          </CardDescription>
                        </div>
                      </div>
                    </CardHeader>
                    <CardContent className="pt-0">
                      <div className="space-y-3">
                        {feature.benefits.map((benefit, benefitIndex) => (
                          <div key={benefitIndex} className="flex items-start gap-2">
                            <CheckCircle className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
                            <span className="text-sm text-gray-700">{benefit}</span>
                          </div>
                        ))}
                      </div>
                      {feature.highlight && (
                        <div className="mt-4 p-3 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg border border-blue-100">
                          <div className="flex items-start gap-2">
                            <Star className="h-4 w-4 text-yellow-500 mt-0.5 flex-shrink-0" />
                            <span className="text-sm text-blue-800 font-medium">{feature.highlight}</span>
                          </div>
                        </div>
                      )}
                    </CardContent>
                  </Card>
                ))}
            </div>
          </div>
        </section>

        {/* How Features Work Together */}
        <section className="w-full py-16">
          <div className="container px-4 md:px-6">
            <div className="text-center mb-12">
              <h2 className="text-3xl font-bold tracking-tight mb-4">How Our Features Work Together</h2>
              <p className="text-gray-600 max-w-3xl mx-auto">
                ApplyAI's features are designed to work seamlessly together, creating a comprehensive resume optimization workflow.
              </p>
            </div>
            
            <div className="grid gap-8 md:grid-cols-3">
              {workflowSteps.map((step, index) => (
                <div key={index} className="text-center">
                  <div className="relative mb-6">
                    <div className="w-16 h-16 mx-auto bg-gradient-to-r from-blue-600 to-purple-600 rounded-full flex items-center justify-center text-white font-bold text-xl shadow-lg">
                      {index + 1}
                    </div>
                    {index < workflowSteps.length - 1 && (
                      <div className="hidden md:block absolute top-8 left-1/2 w-full h-0.5 bg-gradient-to-r from-blue-200 to-purple-200 transform translate-x-8"></div>
                    )}
                  </div>
                  <h3 className="text-xl font-semibold mb-3">{step.title}</h3>
                  <p className="text-gray-600 mb-4">{step.description}</p>
                  <div className="flex flex-wrap justify-center gap-2">
                    {step.features.map((feature, featureIndex) => (
                      <span key={featureIndex} className="px-3 py-1 bg-blue-50 text-blue-700 rounded-full text-sm">
                        {feature}
                      </span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Feature Comparison */}
        <section className="w-full py-16 bg-white/80 backdrop-blur-sm">
          <div className="container px-4 md:px-6">
            <div className="text-center mb-12">
              <h2 className="text-3xl font-bold tracking-tight mb-4">Why Choose ApplyAI?</h2>
              <p className="text-gray-600 max-w-2xl mx-auto">
                See how our comprehensive feature set compares to traditional resume writing approaches.
              </p>
            </div>
            
            <div className="grid gap-6 md:grid-cols-2">
              <Card className="border-red-200 bg-red-50/50">
                <CardHeader>
                  <CardTitle className="text-red-800 flex items-center gap-2">
                    <div className="w-6 h-6 rounded-full bg-red-200 flex items-center justify-center">
                      <span className="text-red-600 text-sm">✗</span>
                    </div>
                    Traditional Approach
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-2">
                    {traditionalApproach.map((item, index) => (
                      <li key={index} className="flex items-start gap-2 text-red-700">
                        <div className="w-4 h-4 rounded-full bg-red-200 flex items-center justify-center mt-0.5">
                          <span className="text-red-600 text-xs">✗</span>
                        </div>
                        <span className="text-sm">{item}</span>
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
              
              <Card className="border-green-200 bg-green-50/50">
                <CardHeader>
                  <CardTitle className="text-green-800 flex items-center gap-2">
                    <div className="w-6 h-6 rounded-full bg-green-200 flex items-center justify-center">
                      <span className="text-green-600 text-sm">✓</span>
                    </div>
                    ApplyAI Approach
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-2">
                    {applyAIApproach.map((item, index) => (
                      <li key={index} className="flex items-start gap-2 text-green-700">
                        <div className="w-4 h-4 rounded-full bg-green-200 flex items-center justify-center mt-0.5">
                          <span className="text-green-600 text-xs">✓</span>
                        </div>
                        <span className="text-sm">{item}</span>
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
            </div>
          </div>
        </section>

        {/* Call to Action */}
        <section className="w-full py-16 bg-gradient-to-r from-blue-600 to-purple-600 text-white">
          <div className="container px-4 md:px-6">
            <div className="text-center max-w-3xl mx-auto">
              <h2 className="text-3xl font-bold tracking-tight mb-4">Ready to Experience All These Features?</h2>
              <p className="text-xl text-blue-100 mb-8">
                Join thousands of job seekers who are already using ApplyAI to land more interviews and advance their careers.
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <Link href="/app">
                  <Button size="lg" className="gap-2 bg-white text-blue-600 hover:bg-blue-50">
                    <Rocket className="h-5 w-5" />
                    Start Free Trial
                  </Button>
                </Link>
                <Link href="/how-it-works">
                  <Button size="lg" variant="outline" className="gap-2 border-white text-white hover:bg-white/10">
                    <FileText className="h-5 w-5" />
                    How It Works
                  </Button>
                </Link>
              </div>
              <p className="text-sm text-blue-100 mt-4">No credit card required • Cancel anytime</p>
            </div>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="w-full border-t py-6 md:py-12 bg-white/80 backdrop-blur-sm">
        <div className="container px-4 md:px-6">
          <div className="grid gap-10 sm:grid-cols-2 md:grid-cols-4">
            <div className="space-y-4">
              <Link className="flex items-center gap-2 font-semibold" href="/">
                <FileText className="h-6 w-6 text-blue-600" />
                <span>ApplyAI</span>
              </Link>
              <p className="text-sm text-gray-500">
                Smart. Targeted. Effective. Resumes that open doors — since 2025.
              </p>
            </div>
            <div className="space-y-4">
              <h4 className="font-medium">Product</h4>
              <nav className="flex flex-col gap-2">
                <Link className="text-sm hover:underline text-gray-500" href="/features">
                  Features
                </Link>
                <Link className="text-sm hover:underline text-gray-500" href="/how-it-works">
                  How It Works
                </Link>
              </nav>
            </div>
            <div className="space-y-4">
              <h4 className="font-medium">Company</h4>
              <nav className="flex flex-col gap-2">
                <Link className="text-sm hover:underline text-gray-500" href="/">
                  About
                </Link>
                                    <Link className="text-sm hover:underline text-gray-500" href="/how-it-works">
                      How It Works
                    </Link>
                <Link className="text-sm hover:underline text-gray-500" href="/contact">
                  Contact
                </Link>
              </nav>
            </div>
            <div className="space-y-4">
              <h4 className="font-medium">Support</h4>
              <nav className="flex flex-col gap-2">
                <Link className="text-sm hover:underline text-gray-500" href="/app">
                  Get Started
                </Link>
                <Link className="text-sm hover:underline text-gray-500" href="/#faq">
                  FAQ
                </Link>
                <Link className="text-sm hover:underline text-gray-500" href="/#help">
                  Help Center
                </Link>
              </nav>
            </div>
          </div>
          <div className="mt-10 flex flex-col items-center justify-between gap-4 border-t border-gray-200 pt-6 md:flex-row">
            <p className="text-xs text-gray-500">© {new Date().getFullYear()} ApplyAI. All rights reserved.</p>
            <div className="flex gap-4">
              <Link className="text-sm hover:underline text-gray-500" href="/privacy">
                Privacy Policy
              </Link>
              <Link className="text-sm hover:underline text-gray-500" href="/terms">
                Terms of Service
              </Link>
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}

// Feature categories
const categories = [
  { id: 'core', name: 'Core Features', icon: Rocket },
  { id: 'ai', name: 'AI Technology', icon: Brain },
  { id: 'optimization', name: 'Optimization', icon: TrendingUp },
  { id: 'automation', name: 'Automation', icon: Zap },
  { id: 'analysis', name: 'Analysis', icon: BarChart }
]

// All features organized by category
const allFeatures = [
  // Core Features
  {
    category: 'core',
    icon: Target,
    title: 'AI-Powered Resume Tailoring',
    description: 'Automatically customize your resume for each job application using advanced AI that understands job requirements and matches your experience perfectly.',
    benefits: [
      'Instant resume customization for any job posting',
      'Maintains your authentic experience while optimizing presentation',
      'Works with any industry or role level',
      'Preserves professional formatting and readability'
    ],
    highlight: 'Our AI processes 100+ data points to create the perfect match'
  },
  {
    category: 'core',
    icon: Layers,
    title: 'Bulk Processing',
    description: 'Process multiple job applications simultaneously. Upload your resume once and tailor it for up to 10 different positions in a single batch.',
    benefits: [
      'Save hours of manual work with batch processing',
      'Apply to multiple positions efficiently',
      'Consistent quality across all applications',
      'Organized results for easy management'
    ],
    highlight: 'Process up to 10 jobs simultaneously in under 2 minutes'
  },
  {
    category: 'core',
    icon: Download,
    title: 'Multiple Output Formats',
    description: 'Download your tailored resumes in professional PDF format or clean text format, ready for any application system or platform.',
    benefits: [
      'Professional PDF format for direct submission',
      'Clean text format for ATS systems',
      'Consistent formatting across all outputs',
      'Industry-standard layouts and typography'
    ]
  },
  {
    category: 'core',
    icon: Mail,
    title: 'Cover Letter Generation',
    description: 'Generate matching cover letters that complement your tailored resume, maintaining consistency in tone and highlighting relevant experience.',
    benefits: [
      'Automatically matches your resume content',
      'Customizable tone and emphasis',
      'Professional formatting and structure',
      'Saves time on manual writing'
    ]
  },

  // AI Technology
  {
    category: 'ai',
    icon: Brain,
    title: 'RAG Technology',
    description: 'Retrieval-Augmented Generation uses a knowledge base of successful resumes and job patterns to provide context-aware recommendations.',
    benefits: [
      'Learns from patterns in successful applications',
      'Provides industry-specific insights',
      'Improves recommendations over time',
      'Uses real job market data'
    ],
    highlight: 'Powered by LangChain and vector databases for superior accuracy'
  },
  {
    category: 'ai',
    icon: Search,
    title: 'Intelligent Job Scraping',
    description: 'Our AI scrapes and analyzes job postings from major job boards, extracting key requirements and preferences automatically.',
    benefits: [
      'Works with LinkedIn, Indeed, Greenhouse, and more',
      'Extracts hidden requirements from job descriptions',
      'Identifies key skills and qualifications',
      'Understands company culture and values'
    ]
  },
  {
    category: 'ai',
    icon: Lightbulb,
    title: 'Industry Insights',
    description: 'Get data-driven recommendations based on successful resumes and hiring patterns in your target industry and role.',
    benefits: [
      'Industry-specific keyword optimization',
      'Trending skills and technologies',
      'Salary and experience level insights',
      'Company culture alignment'
    ]
  },
  {
    category: 'ai',
    icon: Settings,
    title: 'Advanced Prompt Engineering',
    description: 'Our sophisticated prompting system ensures consistent, high-quality outputs that maintain professionalism while maximizing relevance.',
    benefits: [
      'Consistent output quality across all resumes',
      'Maintains professional tone and structure',
      'Adapts to different industries and roles',
      'Preserves your unique voice and experience'
    ]
  },

  // Optimization
  {
    category: 'optimization',
    icon: Target,
    title: 'ATS Optimization',
    description: 'Ensure your resume passes Applicant Tracking Systems with keyword optimization, proper formatting, and structure that ATS software can read.',
    benefits: [
      'Keyword density optimization',
      'ATS-friendly formatting and structure',
      'Proper section headers and organization',
      'Increased visibility to recruiters'
    ],
    highlight: '75% of resumes fail ATS screening - ours are optimized to pass'
  },
  {
    category: 'optimization',
    icon: Award,
    title: 'Skills Highlighting',
    description: 'Automatically identify and emphasize the most relevant skills for each position, ensuring your key qualifications are prominently featured.',
    benefits: [
      'Identifies job-specific skill requirements',
      'Highlights transferable skills',
      'Organizes skills by relevance',
      'Includes both hard and soft skills'
    ]
  },
  {
    category: 'optimization',
    icon: FileCheck,
    title: 'Professional Templates',
    description: 'Choose from ATS-friendly templates designed by industry experts to highlight your experience and achievements effectively.',
    benefits: [
      'Multiple professional layouts',
      'Industry-specific formatting',
      'Clean, modern designs',
      'Optimized for readability'
    ]
  },
  {
    category: 'optimization',
    icon: TrendingUp,
    title: 'Performance Tracking',
    description: 'Monitor your application success rate and get insights into which resume versions and approaches work best for your goals.',
    benefits: [
      'Track application success rates',
      'A/B test different approaches',
      'Identify top-performing resume versions',
      'Optimize strategy based on results'
    ]
  },

  // Automation
  {
    category: 'automation',
    icon: Zap,
    title: 'One-Click Processing',
    description: 'Transform your resume with a single click. Just paste job URLs and let our AI handle the rest - no manual editing required.',
    benefits: [
      'Instant resume transformation',
      'Zero manual editing required',
      'Consistent results every time',
      'Saves hours of work per application'
    ],
    highlight: 'Average processing time: Under 30 seconds per resume'
  },
  {
    category: 'automation',
    icon: Clock,
    title: 'Real-Time Processing',
    description: 'Get your tailored resumes in real-time with live progress updates and instant results, no waiting required.',
    benefits: [
      'Live progress tracking',
      'Instant result delivery',
      'Real-time status updates',
      'No queuing or delays'
    ]
  },
  {
    category: 'automation',
    icon: Globe,
    title: 'Multi-Platform Support',
    description: 'Works seamlessly across all major job boards and career platforms, extracting requirements automatically.',
    benefits: [
      'LinkedIn, Indeed, Glassdoor support',
      'Company career page compatibility',
      'Greenhouse, Lever, Workday integration',
      'Custom job description processing'
    ]
  },
  {
    category: 'automation',
    icon: Shield,
    title: 'Secure Processing',
    description: 'Your data is processed securely with enterprise-grade encryption and automatic cleanup after 24 hours.',
    benefits: [
      'Enterprise-grade security',
      'Automatic file cleanup',
      'No data retention policy',
      'Encrypted processing pipeline'
    ]
  },

  // Analysis
  {
    category: 'analysis',
    icon: BarChart,
    title: 'Match Score Analysis',
    description: 'Get detailed compatibility scores showing how well your resume matches each job description, with specific improvement recommendations.',
    benefits: [
      'Quantitative compatibility scoring',
      'Detailed improvement recommendations',
      'Keyword coverage analysis',
      'Skill gap identification'
    ]
  },
  {
    category: 'analysis',
    icon: FileText,
    title: 'Resume Diff Analysis',
    description: 'See exactly what changed between your original and tailored resume with detailed diff analysis and explanations.',
    benefits: [
      'Side-by-side comparison view',
      'Detailed change explanations',
      'Impact assessment for each change',
      'Learn from optimization patterns'
    ]
  },
  {
    category: 'analysis',
    icon: Users,
    title: 'Competitive Analysis',
    description: 'Understand how your resume compares to others in your field with benchmarking data and competitive insights.',
    benefits: [
      'Industry benchmarking data',
      'Competitive positioning insights',
      'Salary range analysis',
      'Market demand indicators'
    ]
  },
  {
    category: 'analysis',
    icon: TrendingUp,
    title: 'Success Metrics',
    description: 'Track your application success with detailed metrics on interview rates, response times, and conversion rates.',
    benefits: [
      'Interview rate tracking',
      'Response time analysis',
      'Conversion rate optimization',
      'Success pattern identification'
    ]
  }
]

// Workflow steps
const workflowSteps = [
  {
    title: 'Upload & Analyze',
    description: 'Upload your resume and job URLs. Our AI analyzes your experience and job requirements.',
    features: ['File Upload', 'Job Scraping', 'AI Analysis', 'Content Extraction']
  },
  {
    title: 'Process & Optimize',
    description: 'AI tailors your resume using RAG technology and industry insights for maximum impact.',
    features: ['RAG Processing', 'ATS Optimization', 'Keyword Matching', 'Skills Highlighting']
  },
  {
    title: 'Review & Download',
    description: 'Review your tailored resumes with diff analysis and download in your preferred format.',
    features: ['Diff Analysis', 'Match Scoring', 'Multi-format Export', 'Cover Letters']
  }
]

// Comparison data
const traditionalApproach = [
  'Manual resume editing for each job',
  'Guesswork on keyword optimization',
  'Time-consuming research process',
  'No ATS compatibility checking',
  'Limited industry insights',
  'Inconsistent formatting',
  'No performance tracking'
]

const applyAIApproach = [
  'Automated resume tailoring in seconds',
  'AI-powered keyword optimization',
  'Instant job requirement analysis',
  'Built-in ATS compatibility',
  'Data-driven industry insights',
  'Professional formatting guaranteed',
  'Comprehensive success tracking'
] 
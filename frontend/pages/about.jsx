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
  Heart,
  Code,
  Coffee,
  Github,
  Linkedin,
  Twitter,
  User,
  LogOut
} from "lucide-react"
import { useAuth } from '../contexts/AuthContext'

export default function AboutPage() {
  const { isAuthenticated, user, logout } = useAuth()

  const handleLogout = async () => {
    await logout()
  }

  return (
    <div className="flex min-h-[100dvh] flex-col bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
      {/* Header */}
      <header className="px-4 lg:px-6 h-16 flex items-center justify-between border-b bg-white/80 backdrop-blur-sm sticky top-0 z-50">
        <Link className="flex items-center gap-2 font-semibold" href="/">
          <FileText className="h-6 w-6 text-blue-600" />
          <span>ApplyAI</span>
        </Link>
        <nav className="hidden md:flex gap-6">
          <Link className="text-sm font-medium hover:underline underline-offset-4" href="/features">
            Features
          </Link>
          <Link className="text-sm font-medium hover:underline underline-offset-4" href="/how-it-works">
            How It Works
          </Link>
          <Link className="text-sm font-medium hover:underline underline-offset-4" href="/faq">
            FAQ
          </Link>
          <Link className="text-sm font-medium hover:underline underline-offset-4 text-blue-600" href="/about">
            About
          </Link>
          <Link className="text-sm font-medium hover:underline underline-offset-4" href="/blog">
            Blog
          </Link>
          <Link className="text-sm font-medium hover:underline underline-offset-4" href="/contact">
            Contact
          </Link>
        </nav>
        <div className="hidden md:flex gap-4">
          {isAuthenticated ? (
            <>
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
                  <User className="h-4 w-4 text-white" />
                </div>
                <span className="text-sm font-medium">{user?.full_name || user?.email}</span>
              </div>
              <Link href="/app">
                <Button variant="outline">Dashboard</Button>
              </Link>
              <Button variant="outline" onClick={handleLogout}>
                <LogOut className="h-4 w-4 mr-2" />
                Sign Out
              </Button>
            </>
          ) : (
            <>
              <Link href="/login">
                <Button variant="outline">Log In</Button>
              </Link>
              <Link href="/register">
                <Button className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700">Sign Up Free</Button>
              </Link>
            </>
          )}
        </div>
      </header>

      <main className="flex-1">
        {/* Hero Section */}
        <section className="w-full py-16 md:py-24">
          <div className="container px-4 md:px-6">
            <div className="text-center max-w-4xl mx-auto">
              <div className="inline-block rounded-lg bg-gradient-to-r from-blue-100 to-purple-100 px-3 py-1 text-sm text-blue-800 mb-4">
                <Heart className="inline h-4 w-4 mr-1" />
                Our Story
              </div>
              <h1 className="text-4xl md:text-6xl font-bold tracking-tight mb-6 bg-gradient-to-r from-gray-900 to-gray-600 bg-clip-text text-transparent">
                About <span className="text-blue-600">ApplyAI</span>
              </h1>
              <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto leading-relaxed">
                Transforming the job application process with intelligent resume tailoring, one applicant at a time.
              </p>
            </div>
          </div>
        </section>

        {/* App Story Section */}
        <section className="w-full py-16 bg-white/50">
          <div className="container px-4 md:px-6">
            <div className="max-w-4xl mx-auto">
              <div className="text-center mb-12">
                <h2 className="text-3xl md:text-4xl font-bold mb-4 text-gray-900">
                  Why ApplyAI Exists
                </h2>
                <p className="text-lg text-gray-600 max-w-2xl mx-auto">
                  Born from the frustration of generic resumes in a competitive job market
                </p>
              </div>
              
              <div className="grid md:grid-cols-2 gap-8 items-center">
                <div className="space-y-6">
                  <Card className="border-l-4 border-l-blue-600 bg-gradient-to-r from-blue-50 to-white">
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <Target className="h-5 w-5 text-blue-600" />
                        The Problem
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <p className="text-gray-600">
                        Job seekers spend countless hours manually tailoring resumes for each application, often missing key requirements and failing to pass ATS systems. The process is time-consuming, inconsistent, and frustrating.
                      </p>
                    </CardContent>
                  </Card>

                  <Card className="border-l-4 border-l-purple-600 bg-gradient-to-r from-purple-50 to-white">
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <Lightbulb className="h-5 w-5 text-purple-600" />
                        The Solution
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <p className="text-gray-600">
                        ApplyAI leverages advanced AI and natural language processing to intelligently analyze job descriptions and automatically tailor resumes to match specific requirements, keywords, and company culture.
                      </p>
                    </CardContent>
                  </Card>
                </div>

                <div className="space-y-6">
                  <Card className="bg-gradient-to-br from-blue-600 to-purple-600 text-white">
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <Rocket className="h-5 w-5" />
                        Our Mission
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <p className="text-blue-100 mb-4">
                        To democratize access to professional-quality resume tailoring, helping job seekers at all levels compete effectively in today's market.
                      </p>
                      <div className="space-y-2">
                        <div className="flex items-center gap-2">
                          <CheckCircle className="h-4 w-4 text-green-300" />
                          <span className="text-sm">Increase interview success rates</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <CheckCircle className="h-4 w-4 text-green-300" />
                          <span className="text-sm">Save time and reduce stress</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <CheckCircle className="h-4 w-4 text-green-300" />
                          <span className="text-sm">Level the playing field</span>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Founder Section */}
        <section className="w-full py-16">
          <div className="container px-4 md:px-6">
            <div className="max-w-4xl mx-auto">
              <div className="text-center mb-12">
                <h2 className="text-3xl md:text-4xl font-bold mb-4 text-gray-900">
                  Meet the Founder
                </h2>
                <p className="text-lg text-gray-600 max-w-2xl mx-auto">
                  Building the future of job applications with passion and purpose
                </p>
              </div>
              
              <Card className="max-w-3xl mx-auto bg-white/80 backdrop-blur-sm border-2 border-blue-100">
                <CardHeader className="text-center">
                  <div className="w-32 h-32 bg-gradient-to-br from-blue-600 to-purple-600 rounded-full mx-auto mb-4 flex items-center justify-center">
                    <span className="text-4xl font-bold text-white">M</span>
                  </div>
                  <CardTitle className="text-2xl text-gray-900">Manu Maddali</CardTitle>
                  <CardDescription className="text-lg text-blue-600 font-medium">
                    Creator
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  <div className="grid md:grid-cols-2 gap-6">
                    <div className="space-y-4">
                      <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
                        <Code className="h-5 w-5 text-blue-600" />
                        Background
                      </h3>
                      <p className="text-gray-600">
                        Passionate software engineer and entrepreneur with a deep understanding of both technology and the job market challenges. Experienced in AI/ML, full-stack development, and product design.
                      </p>
                    </div>
                    
                    <div className="space-y-4">
                      <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
                        <Target className="h-5 w-5 text-purple-600" />
                        Vision
                      </h3>
                      <p className="text-gray-600">
                        To create tools that empower individuals in their career journeys, leveraging technology to solve real-world problems and make professional opportunities more accessible.
                      </p>
                    </div>
                  </div>
                  
                  <div className="border-t pt-6">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                      <Coffee className="h-5 w-5 text-amber-600" />
                      Personal Note
                    </h3>
                    <p className="text-gray-600 italic">
                      "Having experienced the frustration of manually tailoring resumes for countless applications, I knew there had to be a better way. ApplyAI is my solution to help job seekers focus on what matters most - preparing for interviews and landing their dream jobs, not wrestling with resume formatting and keyword optimization."
                    </p>
                  </div>
                  
                  <div className="flex justify-center gap-4 pt-4">
                    <Button variant="outline" size="sm" className="gap-2">
                      <Github className="h-4 w-4" />
                      GitHub
                    </Button>
                    <Button variant="outline" size="sm" className="gap-2">
                      <Linkedin className="h-4 w-4" />
                      LinkedIn
                    </Button>
                    <Button variant="outline" size="sm" className="gap-2">
                      <Twitter className="h-4 w-4" />
                      Twitter
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </section>

        {/* Technology Section */}
        <section className="w-full py-16 bg-white/50">
          <div className="container px-4 md:px-6">
            <div className="max-w-4xl mx-auto">
              <div className="text-center mb-12">
                <h2 className="text-3xl md:text-4xl font-bold mb-4 text-gray-900">
                  Built with Modern Technology
                </h2>
                <p className="text-lg text-gray-600 max-w-2xl mx-auto">
                  Leveraging cutting-edge AI and robust infrastructure for reliable, scalable performance
                </p>
              </div>
              
              <div className="grid md:grid-cols-3 gap-6">
                <Card className="text-center bg-gradient-to-b from-blue-50 to-white border-blue-200">
                  <CardHeader>
                    <Brain className="h-10 w-10 text-blue-600 mx-auto mb-2" />
                    <CardTitle className="text-lg">AI-Powered</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm text-gray-600">
                      Advanced language models and machine learning algorithms for intelligent content analysis and generation
                    </p>
                  </CardContent>
                </Card>
                
                <Card className="text-center bg-gradient-to-b from-purple-50 to-white border-purple-200">
                  <CardHeader>
                    <Shield className="h-10 w-10 text-purple-600 mx-auto mb-2" />
                    <CardTitle className="text-lg">Secure & Private</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm text-gray-600">
                      Enterprise-grade security measures to protect your personal information and resume data
                    </p>
                  </CardContent>
                </Card>
                
                <Card className="text-center bg-gradient-to-b from-green-50 to-white border-green-200">
                  <CardHeader>
                    <Zap className="h-10 w-10 text-green-600 mx-auto mb-2" />
                    <CardTitle className="text-lg">Fast & Reliable</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm text-gray-600">
                      Optimized for speed and reliability, with robust infrastructure to handle high demand
                    </p>
                  </CardContent>
                </Card>
              </div>
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="w-full py-16 bg-gradient-to-r from-blue-600 to-purple-600 text-white">
          <div className="container px-4 md:px-6">
            <div className="text-center max-w-3xl mx-auto">
              <h2 className="text-3xl md:text-4xl font-bold mb-4">
                Ready to Transform Your Job Search?
              </h2>
              <p className="text-xl text-blue-100 mb-8">
                Join thousands of job seekers who have already discovered the power of AI-tailored resumes
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <Link href="/app">
                  <Button size="lg" className="bg-white text-blue-600 hover:bg-gray-50 gap-2">
                    <Rocket className="h-5 w-5" />
                    Start Tailoring Now
                  </Button>
                </Link>
                <Link href="/features">
                  <Button size="lg" variant="outline" className="border-white text-white hover:bg-white hover:text-blue-600 gap-2">
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
          <div className="flex flex-col md:flex-row justify-between items-center gap-4">
            <div className="flex items-center gap-2">
              <FileText className="h-5 w-5 text-blue-600" />
              <span className="font-semibold">ApplyAI</span>
            </div>
            <div className="flex gap-6">
              <Link className="text-sm text-gray-600 hover:text-blue-600" href="/features">
                Features
              </Link>
              <Link className="text-sm text-gray-600 hover:text-blue-600" href="/how-it-works">
                How It Works
              </Link>
              <Link className="text-sm text-gray-600 hover:text-blue-600" href="/faq">
                FAQ
              </Link>
              <Link className="text-sm text-gray-600 hover:text-blue-600" href="/about">
                About
              </Link>
            </div>
            <p className="text-sm text-gray-600">
              © 2024 ApplyAI. Built with ❤️ for job seekers.
            </p>
          </div>
        </div>
      </footer>
    </div>
  )
} 
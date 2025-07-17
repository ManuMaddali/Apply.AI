"use client"

import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { 
  FileText, 
  Mail,
  MessageSquare,
  Phone,
  MapPin,
  Send,
  User,
  Clock,
  ArrowRight,
  ChevronRight,
  CheckCircle,
  Globe,
  Linkedin,
  Twitter,
  Github,
  Heart,
  Sparkles,
  LogOut
} from "lucide-react"
import { useState } from "react"
import { useAuth } from '../contexts/AuthContext'

export default function ContactPage() {
  const { isAuthenticated, user, logout } = useAuth()
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    subject: '',
    message: ''
  })
  
  const handleLogout = async () => {
    await logout()
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    // TODO: Implement form submission
    console.log('Form submitted:', formData)
    // For now, just show an alert
    alert('Thank you for your message! We\'ll get back to you soon.')
  }

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    })
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
          <Link className="text-sm font-medium hover:underline underline-offset-4" href="/">
            Home
          </Link>
          <Link className="text-sm font-medium hover:underline underline-offset-4" href="/features">
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
          <Link className="text-sm font-medium hover:underline underline-offset-4 text-blue-600" href="/contact">
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
                <MessageSquare className="inline h-4 w-4 mr-1" />
                Get In Touch
              </div>
              <h1 className="text-4xl md:text-6xl font-bold tracking-tight mb-6 bg-gradient-to-r from-gray-900 to-gray-600 bg-clip-text text-transparent">
                Contact <span className="text-blue-600">Us</span>
              </h1>
              <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto leading-relaxed">
                Have questions about ApplyAI? Need help with your account? We're here to help you succeed in your job search.
              </p>
            </div>
          </div>
        </section>

        {/* Contact Methods */}
        <section className="w-full py-16 bg-white/50">
          <div className="container px-4 md:px-6">
            <div className="max-w-6xl mx-auto">
              <div className="grid md:grid-cols-3 gap-8 mb-16">
                <Card className="text-center bg-gradient-to-b from-blue-50 to-white border-blue-200 hover:shadow-lg transition-shadow">
                  <CardHeader>
                    <div className="w-16 h-16 bg-gradient-to-r from-blue-600 to-purple-600 rounded-full mx-auto flex items-center justify-center mb-4">
                      <Mail className="h-8 w-8 text-white" />
                    </div>
                    <CardTitle className="text-xl">Email Support</CardTitle>
                    <CardDescription>Get help with any questions</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <p className="text-lg font-semibold text-blue-600 mb-2">
                      hello@applyai.com
                    </p>
                    <p className="text-sm text-gray-600">
                      We typically respond within 24 hours
                    </p>
                  </CardContent>
                </Card>

                <Card className="text-center bg-gradient-to-b from-purple-50 to-white border-purple-200 hover:shadow-lg transition-shadow">
                  <CardHeader>
                    <div className="w-16 h-16 bg-gradient-to-r from-purple-600 to-pink-600 rounded-full mx-auto flex items-center justify-center mb-4">
                      <Clock className="h-8 w-8 text-white" />
                    </div>
                    <CardTitle className="text-xl">Response Time</CardTitle>
                    <CardDescription>Our commitment to you</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <p className="text-lg font-semibold text-purple-600 mb-2">
                      24 Hours
                    </p>
                    <p className="text-sm text-gray-600">
                      Average response time for all inquiries
                    </p>
                  </CardContent>
                </Card>

                <Card className="text-center bg-gradient-to-b from-green-50 to-white border-green-200 hover:shadow-lg transition-shadow">
                  <CardHeader>
                    <div className="w-16 h-16 bg-gradient-to-r from-green-600 to-teal-600 rounded-full mx-auto flex items-center justify-center mb-4">
                      <Globe className="h-8 w-8 text-white" />
                    </div>
                    <CardTitle className="text-xl">Global Support</CardTitle>
                    <CardDescription>We're here worldwide</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <p className="text-lg font-semibold text-green-600 mb-2">
                      24/7 Available
                    </p>
                    <p className="text-sm text-gray-600">
                      Support available across all time zones
                    </p>
                  </CardContent>
                </Card>
              </div>

              {/* Contact Form */}
              <div className="grid md:grid-cols-2 gap-12 items-start">
                <div className="space-y-8">
                  <Card className="bg-white/80 backdrop-blur-sm border-2 border-blue-100">
                    <CardHeader>
                      <CardTitle className="text-2xl text-gray-900 flex items-center gap-2">
                        <Send className="h-6 w-6 text-blue-600" />
                        Send us a Message
                      </CardTitle>
                      <CardDescription className="text-lg">
                        Fill out the form and we'll get back to you as soon as possible
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      <form onSubmit={handleSubmit} className="space-y-6">
                        <div className="grid md:grid-cols-2 gap-4">
                          <div className="space-y-2">
                            <label htmlFor="name" className="text-sm font-medium text-gray-700">
                              Name *
                            </label>
                            <input
                              type="text"
                              id="name"
                              name="name"
                              required
                              value={formData.name}
                              onChange={handleChange}
                              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                              placeholder="Your full name"
                            />
                          </div>
                          <div className="space-y-2">
                            <label htmlFor="email" className="text-sm font-medium text-gray-700">
                              Email *
                            </label>
                            <input
                              type="email"
                              id="email"
                              name="email"
                              required
                              value={formData.email}
                              onChange={handleChange}
                              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                              placeholder="your.email@example.com"
                            />
                          </div>
                        </div>
                        
                        <div className="space-y-2">
                          <label htmlFor="subject" className="text-sm font-medium text-gray-700">
                            Subject *
                          </label>
                          <input
                            type="text"
                            id="subject"
                            name="subject"
                            required
                            value={formData.subject}
                            onChange={handleChange}
                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                            placeholder="What's this about?"
                          />
                        </div>
                        
                        <div className="space-y-2">
                          <label htmlFor="message" className="text-sm font-medium text-gray-700">
                            Message *
                          </label>
                          <textarea
                            id="message"
                            name="message"
                            required
                            rows={6}
                            value={formData.message}
                            onChange={handleChange}
                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                            placeholder="Tell us how we can help you..."
                          />
                        </div>
                        
                        <Button 
                          type="submit" 
                          className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-semibold py-3 gap-2"
                        >
                          <Send className="h-5 w-5" />
                          Send Message
                        </Button>
                      </form>
                    </CardContent>
                  </Card>
                </div>

                <div className="space-y-8">
                  <Card className="bg-gradient-to-br from-blue-600 to-purple-600 text-white">
                    <CardHeader>
                      <CardTitle className="text-2xl flex items-center gap-2">
                        <Sparkles className="h-6 w-6" />
                        Why Contact Us?
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-6">
                      <div className="space-y-4">
                        <div className="flex items-start gap-3">
                          <CheckCircle className="h-5 w-5 text-green-300 mt-0.5 flex-shrink-0" />
                          <div>
                            <h3 className="font-semibold text-white">Technical Support</h3>
                            <p className="text-blue-100 text-sm">Get help with app functionality, account issues, or technical problems</p>
                          </div>
                        </div>
                        
                        <div className="flex items-start gap-3">
                          <CheckCircle className="h-5 w-5 text-green-300 mt-0.5 flex-shrink-0" />
                          <div>
                            <h3 className="font-semibold text-white">Feature Requests</h3>
                            <p className="text-blue-100 text-sm">Have an idea for a new feature? We'd love to hear from you!</p>
                          </div>
                        </div>
                        
                        <div className="flex items-start gap-3">
                          <CheckCircle className="h-5 w-5 text-green-300 mt-0.5 flex-shrink-0" />
                          <div>
                            <h3 className="font-semibold text-white">Partnership Opportunities</h3>
                            <p className="text-blue-100 text-sm">Interested in partnering with us? Let's explore possibilities</p>
                          </div>
                        </div>
                        
                        <div className="flex items-start gap-3">
                          <CheckCircle className="h-5 w-5 text-green-300 mt-0.5 flex-shrink-0" />
                          <div>
                            <h3 className="font-semibold text-white">General Inquiries</h3>
                            <p className="text-blue-100 text-sm">Any questions about ApplyAI or our services</p>
                          </div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>

                  <Card className="bg-white/80 backdrop-blur-sm">
                    <CardHeader>
                      <CardTitle className="text-xl text-gray-900">Follow Us</CardTitle>
                      <CardDescription>Stay connected on social media</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="flex gap-4">
                        <Button variant="outline" size="sm" className="gap-2">
                          <Twitter className="h-4 w-4" />
                          Twitter
                        </Button>
                        <Button variant="outline" size="sm" className="gap-2">
                          <Linkedin className="h-4 w-4" />
                          LinkedIn
                        </Button>
                        <Button variant="outline" size="sm" className="gap-2">
                          <Github className="h-4 w-4" />
                          GitHub
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* FAQ Quick Links */}
        <section className="w-full py-16 bg-white/50">
          <div className="container px-4 md:px-6">
            <div className="max-w-4xl mx-auto">
              <div className="text-center mb-12">
                <h2 className="text-3xl font-bold mb-4 text-gray-900">
                  Before You Contact Us
                </h2>
                <p className="text-lg text-gray-600">
                  You might find your answer in our frequently asked questions
                </p>
              </div>
              
              <div className="grid md:grid-cols-2 gap-6">
                <Card className="bg-white/80 backdrop-blur-sm border-blue-200 hover:shadow-lg transition-shadow">
                  <CardHeader>
                    <CardTitle className="text-lg">Quick Questions</CardTitle>
                    <CardDescription>Common questions about using ApplyAI</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <ul className="space-y-2 text-sm text-gray-600">
                      <li>• How does AI resume tailoring work?</li>
                      <li>• What file formats are supported?</li>
                      <li>• How secure is my data?</li>
                      <li>• What are the pricing plans?</li>
                    </ul>
                    <Link href="/faq" className="inline-block mt-4">
                      <Button variant="outline" className="gap-2">
                        <ArrowRight className="h-4 w-4" />
                        View All FAQs
                      </Button>
                    </Link>
                  </CardContent>
                </Card>

                <Card className="bg-white/80 backdrop-blur-sm border-purple-200 hover:shadow-lg transition-shadow">
                  <CardHeader>
                    <CardTitle className="text-lg">Getting Started</CardTitle>
                    <CardDescription>Learn how to use ApplyAI effectively</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <ul className="space-y-2 text-sm text-gray-600">
                      <li>• Step-by-step guide to tailoring</li>
                      <li>• Best practices for job applications</li>
                      <li>• Understanding match scores</li>
                      <li>• Maximizing your success rate</li>
                    </ul>
                    <Link href="/how-it-works" className="inline-block mt-4">
                      <Button variant="outline" className="gap-2">
                        <ArrowRight className="h-4 w-4" />
                        How It Works
                      </Button>
                    </Link>
                  </CardContent>
                </Card>
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
              <Link className="text-sm text-gray-600 hover:text-blue-600" href="/contact">
                Contact
              </Link>
            </div>
            <p className="text-sm text-gray-600 flex items-center gap-1">
              © 2024 ApplyAI. Built with <Heart className="h-4 w-4 text-red-500" /> for job seekers.
            </p>
          </div>
        </div>
      </footer>
    </div>
  )
} 
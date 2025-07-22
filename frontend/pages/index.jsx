"use client"

import Link from "next/link"
import Image from "next/image"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Check, ChevronRight, Menu, X, FileText, Target, Zap, Award, BarChart, Users, User, LogOut } from "lucide-react"
import { useState } from "react"
import { useAuth } from "../contexts/AuthContext"
import Layout from "../components/Layout"

export default function LandingPage() {
  const { isAuthenticated, user, logout } = useAuth()

  const handleLogout = async () => {
    await logout()
  }

  return (
    <Layout>
      <div className="flex min-h-[100dvh] flex-col">
      <header className="px-4 lg:px-6 h-16 flex items-center justify-between border-b bg-white/80 backdrop-blur-sm">
        <Link className="flex items-center gap-2 font-semibold" href="#">
          <FileText className="h-6 w-6 text-blue-600" />
          <span>ApplyAI</span>
        </Link>
        <MobileNav />
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
        <section className="w-full py-12 md:py-24 lg:py-32 xl:py-48 bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
          <div className="container px-4 md:px-6">
            <div className="grid gap-6 lg:grid-cols-[1fr_400px] lg:gap-12 xl:grid-cols-[1fr_600px]">
              <div className="flex flex-col justify-center space-y-4">
                <div className="space-y-2">
                  <h1 className="text-3xl font-bold tracking-tighter sm:text-5xl xl:text-6xl/none">
                    Land more interviews with tailored resumes
                  </h1>
                  <p className="max-w-[600px] text-gray-500 md:text-xl">
                    ApplyAI automatically tailors your resume to match job descriptions, increasing your chances of
                    getting past ATS systems and impressing recruiters.
                  </p>
                </div>
                <div className="flex flex-col gap-2 min-[400px]:flex-row">
                  <Link href={isAuthenticated ? "/app" : "/register"}>
                    <Button size="lg" className="gap-1 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700">
                      {isAuthenticated ? "Go to Dashboard" : "Try For Free"} <ChevronRight className="h-4 w-4" />
                    </Button>
                  </Link>
                  <Link href="/how-it-works">
                    <Button size="lg" variant="outline">
                      How It Works
                    </Button>
                  </Link>
                </div>
                <p className="text-sm text-gray-500">No credit card required. Free plan available.</p>
              </div>
              <div className="relative mx-auto lg:order-last">
                <div className="absolute -top-4 -left-4 h-72 w-72 rounded-full bg-gradient-to-br from-blue-100 to-purple-100 blur-3xl opacity-70"></div>
                <Image
                  src="/placeholder.svg?height=550&width=550"
                  width={550}
                  height={550}
                  alt="Resume tailoring app interface showing a resume being matched to a job description"
                  className="relative z-10 mx-auto rounded-xl shadow-xl border"
                />
              </div>
            </div>
          </div>
        </section>

        <section className="w-full py-12 md:py-24 bg-white/80 backdrop-blur-sm">
          <div className="container px-4 md:px-6">
            <div className="flex flex-col items-center justify-center space-y-4 text-center">
              <div className="space-y-2">
                <div className="inline-block rounded-lg bg-gradient-to-r from-blue-100 to-purple-100 px-3 py-1 text-sm text-blue-800">
                  Why ApplyAI?
                </div>
                <h2 className="text-3xl font-bold tracking-tighter md:text-4xl">
                  Get past the ATS and land more interviews
                </h2>
                <p className="max-w-[900px] text-gray-500 md:text-xl">
                  74% of resumes are rejected by ATS systems before a human ever sees them. Our app ensures your resume
                  gets through.
                </p>
              </div>
            </div>
            <div className="mx-auto grid max-w-5xl items-center gap-6 py-12 md:grid-cols-3">
              {stats.map((stat, index) => (
                <Card key={index} className="text-center border-none shadow-sm bg-white/50 backdrop-blur-sm">
                  <CardHeader>
                    <CardTitle className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">{stat.value}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-gray-500">{stat.label}</p>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        </section>

        <section id="features-preview" className="w-full py-12 md:py-24 lg:py-32 bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
          <div className="container px-4 md:px-6">
            <div className="flex flex-col items-center justify-center space-y-4 text-center">
              <div className="space-y-2">
                <div className="inline-block rounded-lg bg-gradient-to-r from-blue-100 to-purple-100 px-3 py-1 text-sm text-blue-800">
                  Features
                </div>
                <h2 className="text-3xl font-bold tracking-tighter md:text-4xl">Everything you need to stand out</h2>
                <p className="max-w-[900px] text-gray-500 md:text-xl">
                  Our intelligent resume tailoring tools help you customize your resume for each job application in
                  minutes.
                </p>
              </div>
            </div>
            <div className="mx-auto grid max-w-5xl items-center gap-6 py-12 md:grid-cols-2 lg:grid-cols-3">
              {features.map((feature, index) => (
                <Card key={index} className="bg-white/80 backdrop-blur-sm border-none shadow-sm">
                  <CardHeader>
                    <feature.icon className="h-10 w-10 text-blue-600" />
                    <CardTitle className="mt-4">{feature.title}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <CardDescription>{feature.description}</CardDescription>
                  </CardContent>
                </Card>
              ))}
            </div>
            <div className="flex justify-center mt-8">
              <Link href="/features">
                <Button size="lg" className="gap-2 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700">
                  View All Features <ChevronRight className="h-4 w-4" />
                </Button>
              </Link>
            </div>
          </div>
        </section>

        <section id="how-it-works" className="w-full py-12 md:py-24 lg:py-32 bg-white/80 backdrop-blur-sm">
          <div className="container px-4 md:px-6">
            <div className="flex flex-col items-center justify-center space-y-4 text-center">
              <div className="space-y-2">
                <div className="inline-block rounded-lg bg-gradient-to-r from-blue-100 to-purple-100 px-3 py-1 text-sm text-blue-800">
                  How It Works
                </div>
                <h2 className="text-3xl font-bold tracking-tighter md:text-4xl">
                  Three simple steps to a tailored resume
                </h2>
                <p className="max-w-[900px] text-gray-500 md:text-xl">
                  Our process is designed to be quick and effective, helping you create the perfect resume in minutes.
                </p>
              </div>
            </div>
            <div className="mx-auto grid max-w-5xl items-center gap-10 py-12 md:grid-cols-3">
              {steps.map((step, index) => (
                <div key={index} className="flex flex-col items-center text-center">
                  <div className="flex h-16 w-16 items-center justify-center rounded-full bg-gradient-to-r from-blue-100 to-purple-100 text-blue-900 mb-4">
                    <span className="text-xl font-bold">{index + 1}</span>
                  </div>
                  <h3 className="text-xl font-bold mb-2">{step.title}</h3>
                  <p className="text-gray-500">{step.description}</p>
                </div>
              ))}
            </div>
            <div className="flex justify-center mt-8">
              <Link href="/app">
                <Button size="lg" className="gap-1 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700">
                  Get Started Now <ChevronRight className="h-4 w-4" />
                </Button>
              </Link>
            </div>
          </div>
        </section>

        <section id="testimonials" className="w-full py-12 md:py-24 lg:py-32 bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
          <div className="container px-4 md:px-6">
            <div className="flex flex-col items-center justify-center space-y-4 text-center">
              <div className="space-y-2">
                <div className="inline-block rounded-lg bg-gradient-to-r from-blue-100 to-purple-100 px-3 py-1 text-sm text-blue-800">
                  Testimonials
                </div>
                <h2 className="text-3xl font-bold tracking-tighter md:text-4xl">Success stories from our users</h2>
                <p className="max-w-[900px] text-gray-500 md:text-xl">
                  Hear from job seekers who landed their dream jobs with the help of ResumeMatch.
                </p>
              </div>
            </div>
            <div className="mx-auto grid max-w-5xl items-center gap-6 py-12 md:grid-cols-2 lg:grid-cols-3">
              {testimonials.map((testimonial, index) => (
                <Card key={index} className="bg-white/80 backdrop-blur-sm border-none shadow-sm">
                  <CardHeader>
                    <div className="flex items-center gap-4">
                      <Image
                        src={testimonial.avatar || "/placeholder.svg"}
                        width={40}
                        height={40}
                        alt={testimonial.name}
                        className="rounded-full"
                      />
                      <div>
                        <CardTitle className="text-base">{testimonial.name}</CardTitle>
                        <CardDescription>{testimonial.position}</CardDescription>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm text-gray-500">{testimonial.quote}</p>
                  </CardContent>
                  <CardFooter>
                    <p className="text-sm font-medium text-blue-600">{testimonial.result}</p>
                  </CardFooter>
                </Card>
              ))}
            </div>
          </div>
        </section>

        {/* FAQ Preview Section */}
        <section className="w-full py-12 md:py-24 bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
          <div className="container px-4 md:px-6">
            <div className="flex flex-col items-center justify-center space-y-4 text-center">
              <div className="space-y-2">
                <div className="inline-block rounded-lg bg-gradient-to-r from-blue-100 to-purple-100 px-3 py-1 text-sm text-blue-800">
                  FAQ
                </div>
                <h2 className="text-3xl font-bold tracking-tighter md:text-4xl">
                  Frequently Asked Questions
                </h2>
                <p className="max-w-[900px] text-gray-500 md:text-xl">
                  Everything you need to know about our AI resume tailoring service
                </p>
              </div>
            </div>
            <div className="mx-auto grid max-w-4xl items-start gap-8 py-12 md:grid-cols-2">
              <div className="space-y-6">
                <div className="bg-white/80 backdrop-blur-sm rounded-lg p-6 shadow-sm">
                  <h3 className="text-lg font-semibold mb-2">How does the AI resume tailoring work?</h3>
                  <p className="text-gray-600">Our AI uses advanced LangChain technology with RAG to analyze job descriptions and intelligently rewrite your experience to match each position while maintaining truthfulness.</p>
                </div>
                <div className="bg-white/80 backdrop-blur-sm rounded-lg p-6 shadow-sm">
                  <h3 className="text-lg font-semibold mb-2">Are the tailored resumes ATS-friendly?</h3>
                  <p className="text-gray-600">Yes! All our resumes are optimized for Applicant Tracking Systems with proper formatting, keyword optimization, and clean structure that ATS software can parse.</p>
                </div>
              </div>
              <div className="space-y-6">
                <div className="bg-white/80 backdrop-blur-sm rounded-lg p-6 shadow-sm">
                  <h3 className="text-lg font-semibold mb-2">How long does it take to process a resume?</h3>
                  <p className="text-gray-600">Processing is very fast - typically under 30 seconds per resume. Batch processing of multiple jobs is completed in under 2 minutes.</p>
                </div>
                <div className="bg-white/80 backdrop-blur-sm rounded-lg p-6 shadow-sm">
                  <h3 className="text-lg font-semibold mb-2">Is my resume data secure and private?</h3>
                  <p className="text-gray-600">Yes, we use enterprise-grade encryption and automatically delete all files after 24 hours. We have a strict no-data-retention policy.</p>
                </div>
              </div>
            </div>
            <div className="text-center">
              <Link href="/faq">
                <Button className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700">
                  View All FAQs
                </Button>
              </Link>
            </div>
          </div>
        </section>

        <section id="pricing" className="w-full py-12 md:py-24 lg:py-32 bg-white/80 backdrop-blur-sm">
          <div className="container px-4 md:px-6">
            <div className="flex flex-col items-center justify-center space-y-4 text-center">
              <div className="space-y-2">
                <div className="inline-block rounded-lg bg-gradient-to-r from-blue-100 to-purple-100 px-3 py-1 text-sm text-blue-800">Pricing</div>
                <h2 className="text-3xl font-bold tracking-tighter md:text-4xl">Simple, transparent pricing</h2>
                <p className="max-w-[900px] text-gray-500 md:text-xl">
                  Choose the plan that's right for your job search needs.
                </p>
              </div>
            </div>
            <div className="mx-auto grid max-w-4xl items-start gap-8 py-12 md:grid-cols-2 justify-center">
              {pricingPlans.map((plan, index) => (
                <Card
                  key={index}
                  className={plan.featured ? "border-blue-600 shadow-lg bg-white/80 backdrop-blur-sm" : "border-gray-200 shadow-sm bg-white/50 backdrop-blur-sm"}
                >
                  {plan.featured && (
                    <div className="absolute -top-4 left-0 right-0 mx-auto w-fit rounded-full bg-gradient-to-r from-blue-600 to-purple-600 px-3 py-1 text-xs text-white">
                      Most Popular
                    </div>
                  )}
                  <CardHeader>
                    <CardTitle>{plan.name}</CardTitle>
                    <div className="flex gap-1">
                      <span className="text-3xl font-bold">${plan.price}</span>
                      <span className="text-gray-500 self-end">{plan.billing}</span>
                    </div>
                    <CardDescription>{plan.description}</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <ul className="grid gap-2">
                      {plan.features.map((feature, featureIndex) => (
                        <li key={featureIndex} className="flex items-center gap-2">
                          <Check className="h-4 w-4 text-blue-600" />
                          <span className="text-sm">{feature}</span>
                        </li>
                      ))}
                    </ul>
                  </CardContent>
                  <CardFooter>
                    <Link href="/app">
                      <Button
                        className="w-full"
                        variant={plan.featured ? "default" : "outline"}
                        style={plan.featured ? { 
                          background: "linear-gradient(to right, #2563eb, #9333ea)",
                          borderColor: "transparent"
                        } : {}}
                      >
                        {plan.buttonText}
                      </Button>
                    </Link>
                  </CardFooter>
                </Card>
              ))}
            </div>
          </div>
        </section>

        <section className="w-full py-12 md:py-24 lg:py-32 bg-gradient-to-r from-blue-600 to-purple-600 text-white">
          <div className="container px-4 md:px-6">
            <div className="grid gap-10 md:grid-cols-2 md:gap-16">
              <div className="space-y-4">
                <h2 className="text-3xl font-bold tracking-tighter md:text-4xl">Ready to land your dream job?</h2>
                <p className="text-blue-100 md:text-xl">
                  Join many job seekers who have boosted their interview chances with ApplyAI.
                </p>
              </div>
              <div className="flex flex-col items-start space-y-4 md:justify-center">
                <Link href={isAuthenticated ? "/app" : "/register"}>
                  <Button size="lg" className="gap-1 bg-white text-blue-600 hover:bg-blue-50">
                    {isAuthenticated ? "Go to Dashboard" : "Get Started For Free"} <ChevronRight className="h-4 w-4" />
                  </Button>
                </Link>
                <p className="text-sm text-blue-100">No credit card required. Cancel anytime.</p>
              </div>
            </div>
          </div>
        </section>
      </main>
      <footer className="w-full border-t py-6 md:py-12 bg-white/80 backdrop-blur-sm">
        <div className="container px-4 md:px-6">
          <div className="grid gap-10 sm:grid-cols-2 md:grid-cols-4">
            <div className="space-y-4">
              <Link className="flex items-center gap-2 font-semibold" href="#">
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
                <Link className="text-sm hover:underline text-gray-500" href="#">
                  FAQ
                </Link>
              </nav>
            </div>
            <div className="space-y-4">
              <h4 className="font-medium">Company</h4>
              <nav className="flex flex-col gap-2">
                <Link className="text-sm hover:underline text-gray-500" href="/about">
                  About
                </Link>
                <Link className="text-sm hover:underline text-gray-500" href="/blog">
                  Blog
                </Link>
                <Link className="text-sm hover:underline text-gray-500" href="/contact">
                  Contact
                </Link>
              </nav>
            </div>
            <div className="space-y-4">
              <h4 className="font-medium">Legal</h4>
              <nav className="flex flex-col gap-2">
                <Link className="text-sm hover:underline text-gray-500" href="/terms">
                  Terms
                </Link>
                <Link className="text-sm hover:underline text-gray-500" href="/privacy">
                  Privacy
                </Link>
                <Link className="text-sm hover:underline text-gray-500" href="/cookies">
                  Cookies
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
    </Layout>
  )
}

function MobileNav() {
  const [isOpen, setIsOpen] = useState(false)
  const { isAuthenticated, user, logout } = useAuth()

  const handleLogout = async () => {
    await logout()
    setIsOpen(false)
  }

  return (
    <div className="md:hidden">
      <Button variant="ghost" size="icon" onClick={() => setIsOpen(!isOpen)}>
        {isOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
      </Button>
      {isOpen && (
        <div className="fixed inset-0 top-16 z-50 bg-white/90 backdrop-blur-sm p-6 shadow-lg">
          <nav className="flex flex-col gap-6">
            {isAuthenticated && (
              <>
                <div className="flex items-center gap-3 p-3 bg-blue-50 rounded-lg">
                  <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
                    <User className="h-4 w-4 text-white" />
                  </div>
                  <div>
                    <p className="font-medium text-gray-900">{user?.full_name || user?.email}</p>
                    <p className="text-sm text-gray-600 capitalize">{user?.role || 'free'} plan</p>
                  </div>
                </div>
                <div className="border-t pt-4">
                  <Link className="text-lg font-medium hover:underline" href="/app" onClick={() => setIsOpen(false)}>
                    Dashboard
                  </Link>
                  <button 
                    onClick={handleLogout}
                    className="text-lg font-medium hover:underline text-red-600"
                  >
                    Sign Out
                  </button>
                </div>
              </>
            )}
            <Link className="text-lg font-medium hover:underline" href="/features" onClick={() => setIsOpen(false)}>
              Features
            </Link>
            <Link className="text-lg font-medium hover:underline" href="/how-it-works" onClick={() => setIsOpen(false)}>
              How It Works
            </Link>
            <Link className="text-lg font-medium hover:underline" href="/faq" onClick={() => setIsOpen(false)}>
              FAQ
            </Link>
            <Link className="text-lg font-medium hover:underline" href="/about" onClick={() => setIsOpen(false)}>
              About
            </Link>
            <Link className="text-lg font-medium hover:underline" href="/blog" onClick={() => setIsOpen(false)}>
              Blog
            </Link>
            <Link className="text-lg font-medium hover:underline" href="/contact" onClick={() => setIsOpen(false)}>
              Contact
            </Link>
            {!isAuthenticated && (
              <div className="flex flex-col gap-2">
                <Link href="/login" onClick={() => setIsOpen(false)}>
                  <Button variant="outline" className="w-full bg-transparent">
                    Log In
                  </Button>
                </Link>
                <Link href="/register" onClick={() => setIsOpen(false)}>
                  <Button className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700">Sign Up Free</Button>
                </Link>
              </div>
            )}
          </nav>
        </div>
      )}
    </div>
  )
}

// Sample data
const stats = [
  {
    value: "3x",
    label: "More likely to get an interview with a tailored resume",
  },
  {
    value: "75%",
    label: "Of resumes are rejected by ATS before a human sees them",
  },
  {
    value: "2 min",
    label: "Average time to tailor your resume with our app",
  },
]

const features = [
  {
    icon: Target,
    title: "ATS Keyword Optimization",
    description:
      "Our AI analyzes your resume and job descriptions to give you customized resumes that will pass ATS systems.",
  },
  {
    icon: FileText,
    title: "Smart Resume Templates",
    description: "Choose from ATS-friendly templates designed to highlight your skills and experience.",
  },
  {
    icon: Zap,
    title: "One-Click Tailoring",
    description: "Paste a job description (up to 10!) and our AI will automatically tailor your resume to match the requirements.",
  },
  {
    icon: BarChart,
    title: "Match Score Analysis",
    description: "See how well your resume matches each job description with a detailed compatibility score.",
  },
  {
    icon: Award,
    title: "Skills Highlighter",
    description: "Automatically identify and emphasize the skills that matter most for each position.",
  },
  {
    icon: Users,
    title: "Industry Insights",
    description: "Get data-driven recommendations based on successful resumes in your target industry.",
  },
]

const steps = [
  {
    title: "Upload Your Resume",
    description: "Upload your existing resume or create a new one using our templates.",
  },
  {
    title: "Paste Job Description",
    description: "Copy and paste the job description (up to 10 for pro and career users)",
  },
  {
    title: "Get Your Tailored Resume",
    description: "Our AI will optimize your resume for the specific jobs you're applying to in seconds.",
  },
]

const testimonials = [
  {
    name: "Alex Johnson",
    position: "Software Engineer",
    avatar: "/placeholder.svg?height=40&width=40",
    quote:
      "I applied to 15 jobs with generic resumes and got zero callbacks. After using ApplyAI, I tailored each application and landed 5 interviews in two weeks.",
    result: "Hired at Google after 3 weeks",
  },
  {
    name: "Sarah Chen",
    position: "Marketing Manager",
    avatar: "/placeholder.svg?height=40&width=40",
    quote:
      "The keyword optimization feature helped me understand exactly what recruiters were looking for. My resume went from being ignored to getting calls for interviews.",
    result: "Received 4 job offers in one month",
  },
  {
    name: "Michael Rodriguez",
    position: "Financial Analyst",
    avatar: "/placeholder.svg?height=40&width=40",
    quote:
      "As a career changer, I was struggling to get noticed. ApplyAI helped me highlight transferable skills I didn't even know I had.",
    result: "Successfully switched industries",
  },
]

const pricingPlans = [
  {
    name: "Free",
    price: "0",
    billing: "/month",
    description: "Perfect for occasional job seekers",
    features: ["3 tailored resumes per week", "Basic ATS optimization", "Basic resume template"],
    buttonText: "Sign Up Free",
  },
  {
    name: "Pro",
    price: "9.99",
    billing: "/month",
    description: "For active job seekers",
    features: [
      "Unlimited tailored resumes",
      "Advanced ATS optimization",
      "All resume templates",
      "Cover letter generator",
      "Match score analysis",
    ],
    buttonText: "Get Started",
    featured: true,
  },

]

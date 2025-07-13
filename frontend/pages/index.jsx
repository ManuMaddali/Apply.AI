"use client"

import Link from "next/link"
import Image from "next/image"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Check, ChevronRight, Menu, X, FileText, Target, Zap, Award, BarChart, Users } from "lucide-react"
import { useState } from "react"

export default function LandingPage() {
  return (
    <div className="flex min-h-[100dvh] flex-col">
      <header className="px-4 lg:px-6 h-16 flex items-center justify-between border-b">
        <Link className="flex items-center gap-2 font-semibold" href="#">
          <FileText className="h-6 w-6 text-emerald-600" />
          <span>ResumeMatch</span>
        </Link>
        <MobileNav />
        <nav className="hidden md:flex gap-6">
          <Link className="text-sm font-medium hover:underline underline-offset-4" href="#features">
            Features
          </Link>
          <Link className="text-sm font-medium hover:underline underline-offset-4" href="#how-it-works">
            How It Works
          </Link>
          <Link className="text-sm font-medium hover:underline underline-offset-4" href="#pricing">
            Pricing
          </Link>
          <Link className="text-sm font-medium hover:underline underline-offset-4" href="#testimonials">
            Testimonials
          </Link>
        </nav>
        <div className="hidden md:flex gap-4">
          <Link href="/app">
            <Button variant="outline">Log In</Button>
          </Link>
          <Link href="/app">
            <Button className="bg-emerald-600 hover:bg-emerald-700">Sign Up Free</Button>
          </Link>
        </div>
      </header>
      <main className="flex-1">
        <section className="w-full py-12 md:py-24 lg:py-32 xl:py-48 bg-gradient-to-b from-emerald-50 to-white">
          <div className="container px-4 md:px-6">
            <div className="grid gap-6 lg:grid-cols-[1fr_400px] lg:gap-12 xl:grid-cols-[1fr_600px]">
              <div className="flex flex-col justify-center space-y-4">
                <div className="space-y-2">
                  <h1 className="text-3xl font-bold tracking-tighter sm:text-5xl xl:text-6xl/none">
                    Land more interviews with tailored resumes
                  </h1>
                  <p className="max-w-[600px] text-gray-500 md:text-xl">
                    ResumeMatch automatically tailors your resume to match job descriptions, increasing your chances of
                    getting past ATS systems and impressing recruiters.
                  </p>
                </div>
                <div className="flex flex-col gap-2 min-[400px]:flex-row">
                  <Link href="/app">
                    <Button size="lg" className="gap-1 bg-emerald-600 hover:bg-emerald-700">
                      Try For Free <ChevronRight className="h-4 w-4" />
                    </Button>
                  </Link>
                  <Link href="#how-it-works">
                    <Button size="lg" variant="outline">
                      How It Works
                    </Button>
                  </Link>
                </div>
                <p className="text-sm text-gray-500">No credit card required. Free plan available.</p>
              </div>
              <div className="relative mx-auto lg:order-last">
                <div className="absolute -top-4 -left-4 h-72 w-72 rounded-full bg-emerald-100 blur-3xl opacity-70"></div>
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

        <section className="w-full py-12 md:py-24 bg-white">
          <div className="container px-4 md:px-6">
            <div className="flex flex-col items-center justify-center space-y-4 text-center">
              <div className="space-y-2">
                <div className="inline-block rounded-lg bg-emerald-100 px-3 py-1 text-sm text-emerald-800">
                  Why ResumeMatch?
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
                <Card key={index} className="text-center border-none shadow-sm">
                  <CardHeader>
                    <CardTitle className="text-4xl font-bold text-emerald-600">{stat.value}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-gray-500">{stat.label}</p>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        </section>

        <section id="features" className="w-full py-12 md:py-24 lg:py-32 bg-gray-50">
          <div className="container px-4 md:px-6">
            <div className="flex flex-col items-center justify-center space-y-4 text-center">
              <div className="space-y-2">
                <div className="inline-block rounded-lg bg-emerald-100 px-3 py-1 text-sm text-emerald-800">
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
                <Card key={index} className="bg-white border-none shadow-sm">
                  <CardHeader>
                    <feature.icon className="h-10 w-10 text-emerald-600" />
                    <CardTitle className="mt-4">{feature.title}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <CardDescription>{feature.description}</CardDescription>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        </section>

        <section id="how-it-works" className="w-full py-12 md:py-24 lg:py-32 bg-white">
          <div className="container px-4 md:px-6">
            <div className="flex flex-col items-center justify-center space-y-4 text-center">
              <div className="space-y-2">
                <div className="inline-block rounded-lg bg-emerald-100 px-3 py-1 text-sm text-emerald-800">
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
                  <div className="flex h-16 w-16 items-center justify-center rounded-full bg-emerald-100 text-emerald-900 mb-4">
                    <span className="text-xl font-bold">{index + 1}</span>
                  </div>
                  <h3 className="text-xl font-bold mb-2">{step.title}</h3>
                  <p className="text-gray-500">{step.description}</p>
                </div>
              ))}
            </div>
            <div className="flex justify-center mt-8">
              <Link href="/app">
                <Button size="lg" className="gap-1 bg-emerald-600 hover:bg-emerald-700">
                  Get Started Now <ChevronRight className="h-4 w-4" />
                </Button>
              </Link>
            </div>
          </div>
        </section>

        <section id="testimonials" className="w-full py-12 md:py-24 lg:py-32 bg-emerald-50">
          <div className="container px-4 md:px-6">
            <div className="flex flex-col items-center justify-center space-y-4 text-center">
              <div className="space-y-2">
                <div className="inline-block rounded-lg bg-emerald-100 px-3 py-1 text-sm text-emerald-800">
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
                <Card key={index} className="bg-white border-none shadow-sm">
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
                    <p className="text-sm font-medium text-emerald-600">{testimonial.result}</p>
                  </CardFooter>
                </Card>
              ))}
            </div>
          </div>
        </section>

        <section id="pricing" className="w-full py-12 md:py-24 lg:py-32 bg-white">
          <div className="container px-4 md:px-6">
            <div className="flex flex-col items-center justify-center space-y-4 text-center">
              <div className="space-y-2">
                <div className="inline-block rounded-lg bg-emerald-100 px-3 py-1 text-sm text-emerald-800">Pricing</div>
                <h2 className="text-3xl font-bold tracking-tighter md:text-4xl">Simple, transparent pricing</h2>
                <p className="max-w-[900px] text-gray-500 md:text-xl">
                  Choose the plan that's right for your job search needs.
                </p>
              </div>
            </div>
            <div className="mx-auto grid max-w-5xl items-start gap-6 py-12 md:grid-cols-3">
              {pricingPlans.map((plan, index) => (
                <Card
                  key={index}
                  className={plan.featured ? "border-emerald-600 shadow-lg" : "border-gray-200 shadow-sm"}
                >
                  {plan.featured && (
                    <div className="absolute -top-4 left-0 right-0 mx-auto w-fit rounded-full bg-emerald-600 px-3 py-1 text-xs text-white">
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
                          <Check className="h-4 w-4 text-emerald-600" />
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
                        style={plan.featured ? { backgroundColor: "#059669", borderColor: "#059669" } : {}}
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

        <section className="w-full py-12 md:py-24 lg:py-32 bg-emerald-600 text-white">
          <div className="container px-4 md:px-6">
            <div className="grid gap-10 md:grid-cols-2 md:gap-16">
              <div className="space-y-4">
                <h2 className="text-3xl font-bold tracking-tighter md:text-4xl">Ready to land your dream job?</h2>
                <p className="text-emerald-100 md:text-xl">
                  Join thousands of job seekers who have boosted their interview chances with ResumeMatch.
                </p>
              </div>
              <div className="flex flex-col items-start space-y-4 md:justify-center">
                <Link href="/app">
                  <Button size="lg" className="gap-1 bg-white text-emerald-600 hover:bg-emerald-50">
                    Get Started For Free <ChevronRight className="h-4 w-4" />
                  </Button>
                </Link>
                <p className="text-sm text-emerald-100">No credit card required. Cancel anytime.</p>
              </div>
            </div>
          </div>
        </section>
      </main>
      <footer className="w-full border-t py-6 md:py-12 bg-gray-50">
        <div className="container px-4 md:px-6">
          <div className="grid gap-10 sm:grid-cols-2 md:grid-cols-4">
            <div className="space-y-4">
              <Link className="flex items-center gap-2 font-semibold" href="#">
                <FileText className="h-6 w-6 text-emerald-600" />
                <span>ResumeMatch</span>
              </Link>
              <p className="text-sm text-gray-500">
                Helping job seekers land more interviews with tailored resumes since 2023.
              </p>
            </div>
            <div className="space-y-4">
              <h4 className="font-medium">Product</h4>
              <nav className="flex flex-col gap-2">
                <Link className="text-sm hover:underline text-gray-500" href="#">
                  Features
                </Link>
                <Link className="text-sm hover:underline text-gray-500" href="#">
                  Pricing
                </Link>
                <Link className="text-sm hover:underline text-gray-500" href="#">
                  Testimonials
                </Link>
                <Link className="text-sm hover:underline text-gray-500" href="#">
                  FAQ
                </Link>
              </nav>
            </div>
            <div className="space-y-4">
              <h4 className="font-medium">Company</h4>
              <nav className="flex flex-col gap-2">
                <Link className="text-sm hover:underline text-gray-500" href="#">
                  About
                </Link>
                <Link className="text-sm hover:underline text-gray-500" href="#">
                  Blog
                </Link>
                <Link className="text-sm hover:underline text-gray-500" href="#">
                  Careers
                </Link>
                <Link className="text-sm hover:underline text-gray-500" href="#">
                  Contact
                </Link>
              </nav>
            </div>
            <div className="space-y-4">
              <h4 className="font-medium">Legal</h4>
              <nav className="flex flex-col gap-2">
                <Link className="text-sm hover:underline text-gray-500" href="#">
                  Terms
                </Link>
                <Link className="text-sm hover:underline text-gray-500" href="#">
                  Privacy
                </Link>
                <Link className="text-sm hover:underline text-gray-500" href="#">
                  Cookies
                </Link>
              </nav>
            </div>
          </div>
          <div className="mt-10 flex flex-col items-center justify-between gap-4 border-t border-gray-200 pt-6 md:flex-row">
            <p className="text-xs text-gray-500">© {new Date().getFullYear()} ResumeMatch. All rights reserved.</p>
            <div className="flex gap-4">
              <Link className="text-sm hover:underline text-gray-500" href="#">
                Privacy Policy
              </Link>
              <Link className="text-sm hover:underline text-gray-500" href="#">
                Terms of Service
              </Link>
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}

function MobileNav() {
  const [isOpen, setIsOpen] = useState(false)

  return (
    <div className="md:hidden">
      <Button variant="ghost" size="icon" onClick={() => setIsOpen(!isOpen)}>
        {isOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
      </Button>
      {isOpen && (
        <div className="fixed inset-0 top-16 z-50 bg-background p-6 shadow-lg">
          <nav className="flex flex-col gap-6">
            <Link className="text-lg font-medium hover:underline" href="#features" onClick={() => setIsOpen(false)}>
              Features
            </Link>
            <Link className="text-lg font-medium hover:underline" href="#how-it-works" onClick={() => setIsOpen(false)}>
              How It Works
            </Link>
            <Link className="text-lg font-medium hover:underline" href="#pricing" onClick={() => setIsOpen(false)}>
              Pricing
            </Link>
            <Link className="text-lg font-medium hover:underline" href="#testimonials" onClick={() => setIsOpen(false)}>
              Testimonials
            </Link>
            <div className="flex flex-col gap-2">
              <Link href="/app" onClick={() => setIsOpen(false)}>
                <Button variant="outline" className="w-full bg-transparent">
                  Log In
                </Button>
              </Link>
              <Link href="/app" onClick={() => setIsOpen(false)}>
                <Button className="w-full bg-emerald-600 hover:bg-emerald-700">Sign Up Free</Button>
              </Link>
            </div>
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
      "Our AI analyzes job descriptions and suggests keywords to include in your resume to pass ATS systems.",
  },
  {
    icon: FileText,
    title: "Smart Resume Templates",
    description: "Choose from ATS-friendly templates designed to highlight your skills and experience.",
  },
  {
    icon: Zap,
    title: "One-Click Tailoring",
    description: "Paste a job description and our AI will automatically tailor your resume to match the requirements.",
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
    description: "Copy and paste the job description you're applying for.",
  },
  {
    title: "Get Your Tailored Resume",
    description: "Our AI will optimize your resume for the specific job in seconds.",
  },
]

const testimonials = [
  {
    name: "Alex Johnson",
    position: "Software Engineer",
    avatar: "/placeholder.svg?height=40&width=40",
    quote:
      "I applied to 15 jobs with generic resumes and got zero callbacks. After using ResumeMatch, I tailored each application and landed 5 interviews in two weeks.",
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
      "As a career changer, I was struggling to get noticed. ResumeMatch helped me highlight transferable skills I didn't even know I had.",
    result: "Successfully switched industries",
  },
]

const pricingPlans = [
  {
    name: "Free",
    price: "0",
    billing: "/month",
    description: "Perfect for occasional job seekers",
    features: ["3 tailored resumes per month", "Basic ATS optimization", "2 resume templates", "Email support"],
    buttonText: "Sign Up Free",
  },
  {
    name: "Pro",
    price: "19",
    billing: "/month",
    description: "For active job seekers",
    features: [
      "Unlimited tailored resumes",
      "Advanced ATS optimization",
      "All resume templates",
      "Match score analysis",
      "Priority support",
    ],
    buttonText: "Get Started",
    featured: true,
  },
  {
    name: "Career",
    price: "39",
    billing: "/month",
    description: "Complete career solution",
    features: [
      "Everything in Pro",
      "Cover letter generator",
      "LinkedIn profile optimization",
      "Interview preparation tools",
      "1-on-1 resume review",
      "24/7 priority support",
    ],
    buttonText: "Get Career",
  },
]

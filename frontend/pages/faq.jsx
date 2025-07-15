import React from 'react'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { FileText, ArrowLeft } from 'lucide-react'
import FAQ from '@/components/FAQ'

const FAQPage = () => {
  return (
    <div className="flex min-h-[100dvh] flex-col">
      {/* Header */}
      <header className="px-4 lg:px-6 h-16 flex items-center justify-between border-b bg-white/80 backdrop-blur-sm">
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
          <Link href="/app">
            <Button variant="outline">Log In</Button>
          </Link>
          <Link href="/app">
            <Button className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700">Sign Up Free</Button>
          </Link>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
        <div className="container mx-auto px-4 py-12 md:py-24">
          {/* Back Navigation */}
          <div className="mb-8">
            <Link href="/" className="inline-flex items-center gap-2 text-blue-600 hover:text-blue-700 transition-colors">
              <ArrowLeft className="h-4 w-4" />
              Back to Home
            </Link>
          </div>

          {/* FAQ Component */}
          <FAQ />
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t bg-white/80 backdrop-blur-sm py-12">
        <div className="container px-4 md:px-6">
          <div className="grid gap-8 md:grid-cols-4">
            <div className="flex flex-col gap-4">
              <Link className="flex items-center gap-2 font-semibold" href="/">
                <FileText className="h-6 w-6 text-blue-600" />
                <span>ApplyAI</span>
              </Link>
              <p className="text-sm text-gray-500">
                Transform your resume for every job application with AI-powered customization.
              </p>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Product</h4>
              <div className="flex flex-col gap-2">
                <Link className="text-sm text-gray-500 hover:text-gray-700" href="/features">Features</Link>
                <Link className="text-sm text-gray-500 hover:text-gray-700" href="/how-it-works">How It Works</Link>
                <Link className="text-sm text-gray-500 hover:text-gray-700" href="/faq">FAQ</Link>
              </div>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Support</h4>
              <div className="flex flex-col gap-2">
                <Link className="text-sm text-gray-500 hover:text-gray-700" href="/faq">Help Center</Link>
                <Link className="text-sm text-gray-500 hover:text-gray-700" href="/contact">Contact Us</Link>
                <Link className="text-sm text-gray-500 hover:text-gray-700" href="#">Documentation</Link>
              </div>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Company</h4>
              <div className="flex flex-col gap-2">
                <Link className="text-sm text-gray-500 hover:text-gray-700" href="#">About Us</Link>
                <Link className="text-sm text-gray-500 hover:text-gray-700" href="#">Privacy Policy</Link>
                <Link className="text-sm text-gray-500 hover:text-gray-700" href="#">Terms of Service</Link>
              </div>
            </div>
          </div>
          <div className="mt-8 pt-8 border-t text-center text-sm text-gray-500">
            <p>&copy; 2024 ApplyAI. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  )
}

export default FAQPage 
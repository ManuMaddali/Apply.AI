import Link from "next/link"
import { Button } from "@/components/ui/button"
import { FileText, ArrowLeft, Shield, Users, AlertTriangle, Scale } from "lucide-react"

export default function TermsOfService() {
  return (
    <div className="flex min-h-[100dvh] flex-col">
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

      <main className="flex-1 bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
        <div className="container mx-auto px-4 py-12 max-w-4xl">
          <div className="mb-8">
            <Link href="/" className="inline-flex items-center gap-2 text-blue-600 hover:text-blue-800 mb-4">
              <ArrowLeft className="h-4 w-4" />
              Back to Home
            </Link>
            <h1 className="text-4xl font-bold tracking-tight mb-4 bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              Terms of Service
            </h1>
            <p className="text-gray-600 text-lg">
              Last updated: {new Date().toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })}
            </p>
          </div>

          <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-sm border border-white/20 overflow-hidden">
            <div className="p-8 space-y-8">
              {/* Introduction */}
              <section>
                <div className="flex items-center gap-3 mb-4">
                  <Shield className="h-6 w-6 text-blue-600" />
                  <h2 className="text-2xl font-semibold">1. Introduction</h2>
                </div>
                <p className="text-gray-700 leading-relaxed">
                  Welcome to ApplyAI. These Terms of Service ("Terms") govern your use of our AI-powered resume tailoring service 
                  ("Service") operated by ApplyAI, LLC ("we", "us", "our"). By accessing or using our Service, you agree to be bound 
                  by these Terms. If you disagree with any part of these terms, then you may not access the Service.
                </p>
              </section>

              {/* Acceptance of Terms */}
              <section>
                <div className="flex items-center gap-3 mb-4">
                  <Users className="h-6 w-6 text-blue-600" />
                  <h2 className="text-2xl font-semibold">2. Acceptance of Terms</h2>
                </div>
                <p className="text-gray-700 leading-relaxed mb-4">
                  By creating an account or using our Service, you acknowledge that you have read, understood, and agree to be bound by these Terms and our Privacy Policy. You must be at least 18 years old to use our Service.
                </p>
                <p className="text-gray-700 leading-relaxed">
                  We reserve the right to modify these Terms at any time. We will notify users of any material changes via email or through the Service. Your continued use of the Service after such modifications constitutes acceptance of the updated Terms.
                </p>
              </section>

              {/* Service Description */}
              <section>
                <h2 className="text-2xl font-semibold mb-4">3. Service Description</h2>
                <p className="text-gray-700 leading-relaxed mb-4">
                  ApplyAI provides an AI-powered resume tailoring service that helps users customize their resumes to match specific job descriptions. Our Service includes:
                </p>
                <ul className="list-disc pl-6 space-y-2 text-gray-700">
                  <li>AI-powered resume analysis and optimization</li>
                  <li>ATS-friendly formatting and keyword optimization</li>
                  <li>Batch processing for multiple job applications</li>
                  <li>Cover letter generation</li>
                  <li>Match score analysis</li>
                  <li>Resume templates and formatting tools</li>
                </ul>
              </section>

              {/* User Accounts */}
              <section>
                <h2 className="text-2xl font-semibold mb-4">4. User Accounts</h2>
                <p className="text-gray-700 leading-relaxed mb-4">
                  To use certain features of our Service, you may be required to create an account. You are responsible for:
                </p>
                <ul className="list-disc pl-6 space-y-2 text-gray-700">
                  <li>Maintaining the confidentiality of your account credentials</li>
                  <li>All activities that occur under your account</li>
                  <li>Providing accurate and complete information</li>
                  <li>Updating your information as necessary</li>
                  <li>Notifying us immediately of any unauthorized use of your account</li>
                </ul>
              </section>

              {/* Acceptable Use */}
              <section>
                <div className="flex items-center gap-3 mb-4">
                  <AlertTriangle className="h-6 w-6 text-amber-600" />
                  <h2 className="text-2xl font-semibold">5. Acceptable Use</h2>
                </div>
                <p className="text-gray-700 leading-relaxed mb-4">
                  You agree to use our Service only for lawful purposes and in accordance with these Terms. You agree NOT to:
                </p>
                <ul className="list-disc pl-6 space-y-2 text-gray-700">
                  <li>Use the Service to create false or misleading information</li>
                  <li>Violate any applicable laws or regulations</li>
                  <li>Infringe on the rights of others</li>
                  <li>Attempt to gain unauthorized access to the Service or its systems</li>
                  <li>Distribute malware or other harmful code</li>
                  <li>Interfere with the proper working of the Service</li>
                  <li>Use the Service for any commercial purposes without our written consent</li>
                  <li>Reverse engineer, decompile, or attempt to extract the source code</li>
                </ul>
              </section>

              {/* Content and Intellectual Property */}
              <section>
                <h2 className="text-2xl font-semibold mb-4">6. Content and Intellectual Property</h2>
                <div className="space-y-4">
                  <div>
                    <h3 className="text-lg font-semibold mb-2">Your Content</h3>
                    <p className="text-gray-700 leading-relaxed">
                      You retain ownership of all content you submit to our Service, including resumes, cover letters, and personal information. 
                      By using our Service, you grant us a limited, non-exclusive license to process your content solely for the purpose of 
                      providing our Service to you.
                    </p>
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold mb-2">Our Content</h3>
                    <p className="text-gray-700 leading-relaxed">
                      The Service and its original content, features, and functionality are and will remain the exclusive property of ApplyAI, LLC and its licensors. 
                      The Service is protected by copyright, trademark, and other laws.
                    </p>
                  </div>
                </div>
              </section>

              {/* Privacy and Data Protection */}
              <section>
                <h2 className="text-2xl font-semibold mb-4">7. Privacy and Data Protection</h2>
                <p className="text-gray-700 leading-relaxed mb-4">
                  We take your privacy seriously. Our collection and use of personal information is governed by our Privacy Policy, 
                  which is incorporated into these Terms by reference. Key points include:
                </p>
                <ul className="list-disc pl-6 space-y-2 text-gray-700">
                  <li>We automatically delete all uploaded files after 24 hours</li>
                  <li>We use enterprise-grade encryption for all data transmission and storage</li>
                  <li>We do not sell, rent, or share your personal information with third parties</li>
                  <li>We comply with GDPR, CCPA, and other applicable privacy laws</li>
                </ul>
              </section>

              {/* Subscription and Payments */}
              <section>
                <h2 className="text-2xl font-semibold mb-4">8. Subscription and Payments</h2>
                <div className="space-y-4">
                  <div>
                    <h3 className="text-lg font-semibold mb-2">Subscription Plans</h3>
                    <p className="text-gray-700 leading-relaxed">
                      We offer both free and paid subscription plans. Paid subscriptions are billed monthly and automatically renew unless cancelled. 
                      You can cancel your subscription at any time through your account settings.
                    </p>
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold mb-2">Refund Policy</h3>
                    <p className="text-gray-700 leading-relaxed">
                      We offer a 30-day money-back guarantee for all paid subscriptions. If you're not satisfied with our Service, 
                      contact us within 30 days of your purchase for a full refund.
                    </p>
                  </div>
                </div>
              </section>

              {/* Limitation of Liability */}
              <section>
                <div className="flex items-center gap-3 mb-4">
                  <Scale className="h-6 w-6 text-blue-600" />
                  <h2 className="text-2xl font-semibold">9. Limitation of Liability</h2>
                </div>
                <p className="text-gray-700 leading-relaxed mb-4">
                  To the fullest extent permitted by law, ApplyAI, LLC shall not be liable for any indirect, incidental, special, 
                  consequential, or punitive damages, including without limitation, loss of profits, data, use, goodwill, or other intangible losses, 
                  resulting from your use of the Service.
                </p>
                <p className="text-gray-700 leading-relaxed">
                  In no event shall our total liability to you for all damages exceed the amount paid by you to us in the 12 months prior to the claim.
                </p>
              </section>

              {/* Termination */}
              <section>
                <h2 className="text-2xl font-semibold mb-4">10. Termination</h2>
                <p className="text-gray-700 leading-relaxed mb-4">
                  Either party may terminate these Terms at any time. We may terminate or suspend your account and access to the Service 
                  immediately, without prior notice, if you breach these Terms.
                </p>
                <p className="text-gray-700 leading-relaxed">
                  Upon termination, all rights and licenses granted to you will cease, and you must stop using the Service. 
                  Sections that by their nature should survive termination will survive.
                </p>
              </section>

              {/* Governing Law */}
              <section>
                <h2 className="text-2xl font-semibold mb-4">11. Governing Law</h2>
                <p className="text-gray-700 leading-relaxed">
                  These Terms shall be governed and construed in accordance with the laws of the State of California, United States, 
                  without regard to its conflict of law provisions. Any legal action or proceeding arising under these Terms will be 
                  brought exclusively in the courts of California.
                </p>
              </section>

              {/* Contact Information */}
              <section>
                <h2 className="text-2xl font-semibold mb-4">12. Contact Information</h2>
                <p className="text-gray-700 leading-relaxed mb-4">
                  If you have any questions about these Terms, please contact us at:
                </p>
                <div className="bg-gray-50 rounded-lg p-4">
                  <p className="text-gray-700">
                    <strong>ApplyAI, LLC</strong><br />
                    Email: legal@applyai.com<br />
                    Address: 123 Innovation Drive, San Francisco, CA 94105
                  </p>
                </div>
              </section>
            </div>
          </div>
        </div>
      </main>

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
                <Link className="text-sm hover:underline text-gray-500" href="/faq">
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
  )
} 
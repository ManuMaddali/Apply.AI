import Link from "next/link"
import { Button } from "@/components/ui/button"
import { FileText, ArrowLeft, Shield, Lock, Eye, Database, Globe, UserCheck } from "lucide-react"

export default function PrivacyPolicy() {
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
              Privacy Policy
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
                <p className="text-gray-700 leading-relaxed mb-4">
                  At ApplyAI, we take your privacy seriously. This Privacy Policy explains how we collect, use, disclose, and safeguard your information when you use our AI-powered resume tailoring service. Please read this privacy policy carefully.
                </p>
                <p className="text-gray-700 leading-relaxed">
                  By using our Service, you agree to the collection and use of information in accordance with this policy. We will not use or share your information with anyone except as described in this Privacy Policy.
                </p>
              </section>

              {/* Information We Collect */}
              <section>
                <div className="flex items-center gap-3 mb-4">
                  <Database className="h-6 w-6 text-blue-600" />
                  <h2 className="text-2xl font-semibold">2. Information We Collect</h2>
                </div>
                
                <div className="space-y-6">
                  <div>
                    <h3 className="text-lg font-semibold mb-3">Personal Information</h3>
                    <p className="text-gray-700 leading-relaxed mb-3">
                      When you create an account or use our Service, we may collect the following personal information:
                    </p>
                    <ul className="list-disc pl-6 space-y-2 text-gray-700">
                      <li>Name and contact information (email address)</li>
                      <li>Resume content and professional information</li>
                      <li>Job descriptions you submit for analysis</li>
                      <li>Payment information (processed by our payment processor)</li>
                      <li>Account preferences and settings</li>
                    </ul>
                  </div>

                  <div>
                    <h3 className="text-lg font-semibold mb-3">Usage Information</h3>
                    <p className="text-gray-700 leading-relaxed mb-3">
                      We automatically collect certain information when you use our Service:
                    </p>
                    <ul className="list-disc pl-6 space-y-2 text-gray-700">
                      <li>IP address and device information</li>
                      <li>Browser type and version</li>
                      <li>Pages visited and features used</li>
                      <li>Time and date of access</li>
                      <li>Referring website or source</li>
                      <li>Usage patterns and performance data</li>
                    </ul>
                  </div>

                  <div>
                    <h3 className="text-lg font-semibold mb-3">Cookies and Similar Technologies</h3>
                    <p className="text-gray-700 leading-relaxed">
                      We use cookies and similar tracking technologies to enhance your experience, analyze usage, and provide personalized content. For more information, please see our Cookie Policy.
                    </p>
                  </div>
                </div>
              </section>

              {/* How We Use Your Information */}
              <section>
                <div className="flex items-center gap-3 mb-4">
                  <Eye className="h-6 w-6 text-blue-600" />
                  <h2 className="text-2xl font-semibold">3. How We Use Your Information</h2>
                </div>
                <p className="text-gray-700 leading-relaxed mb-4">
                  We use the information we collect for the following purposes:
                </p>
                <ul className="list-disc pl-6 space-y-2 text-gray-700">
                  <li>Provide, operate, and maintain our Service</li>
                  <li>Process your resume and job description analysis</li>
                  <li>Generate tailored resumes and cover letters</li>
                  <li>Process payments and manage subscriptions</li>
                  <li>Communicate with you about your account and our Service</li>
                  <li>Improve our Service and develop new features</li>
                  <li>Analyze usage patterns and optimize performance</li>
                  <li>Detect and prevent fraud or abuse</li>
                  <li>Comply with legal obligations</li>
                </ul>
              </section>

              {/* Data Sharing and Disclosure */}
              <section>
                <div className="flex items-center gap-3 mb-4">
                  <Globe className="h-6 w-6 text-blue-600" />
                  <h2 className="text-2xl font-semibold">4. Data Sharing and Disclosure</h2>
                </div>
                <p className="text-gray-700 leading-relaxed mb-4">
                  We do not sell, trade, or rent your personal information to third parties. We may share your information only in the following circumstances:
                </p>
                
                <div className="space-y-4">
                  <div>
                    <h3 className="text-lg font-semibold mb-2">Service Providers</h3>
                    <p className="text-gray-700 leading-relaxed">
                      We may share your information with trusted third-party service providers who assist us in operating our Service, such as cloud hosting providers, payment processors, and analytics services. These providers are contractually bound to protect your information.
                    </p>
                  </div>

                  <div>
                    <h3 className="text-lg font-semibold mb-2">Legal Requirements</h3>
                    <p className="text-gray-700 leading-relaxed">
                      We may disclose your information if required by law, regulation, legal process, or governmental request, or to protect our rights, property, or safety.
                    </p>
                  </div>

                  <div>
                    <h3 className="text-lg font-semibold mb-2">Business Transfers</h3>
                    <p className="text-gray-700 leading-relaxed">
                      In the event of a merger, acquisition, or sale of our company, your information may be transferred to the new owner, subject to the same privacy protections.
                    </p>
                  </div>
                </div>
              </section>

              {/* Data Security */}
              <section>
                <div className="flex items-center gap-3 mb-4">
                  <Lock className="h-6 w-6 text-blue-600" />
                  <h2 className="text-2xl font-semibold">5. Data Security</h2>
                </div>
                <p className="text-gray-700 leading-relaxed mb-4">
                  We implement industry-standard security measures to protect your personal information:
                </p>
                <ul className="list-disc pl-6 space-y-2 text-gray-700">
                  <li>End-to-end encryption for all data transmission</li>
                  <li>Secure, encrypted storage of all personal information</li>
                  <li>Regular security audits and vulnerability assessments</li>
                  <li>Access controls and authentication measures</li>
                  <li>Automatic deletion of uploaded files after 24 hours</li>
                  <li>Employee training on data protection best practices</li>
                </ul>
                <p className="text-gray-700 leading-relaxed mt-4">
                  While we strive to protect your information, no method of transmission over the internet or electronic storage is 100% secure. We cannot guarantee absolute security.
                </p>
              </section>

              {/* Data Retention */}
              <section>
                <h2 className="text-2xl font-semibold mb-4">6. Data Retention</h2>
                <p className="text-gray-700 leading-relaxed mb-4">
                  We retain your personal information only for as long as necessary to fulfill the purposes outlined in this Privacy Policy:
                </p>
                <ul className="list-disc pl-6 space-y-2 text-gray-700">
                  <li>Account information: Until you delete your account</li>
                  <li>Uploaded files (resumes, job descriptions): Automatically deleted after 24 hours</li>
                  <li>Usage data: Up to 2 years for analytics purposes</li>
                  <li>Payment records: As required by law (typically 7 years)</li>
                  <li>Legal compliance data: As required by applicable laws</li>
                </ul>
              </section>

              {/* Your Rights */}
              <section>
                <div className="flex items-center gap-3 mb-4">
                  <UserCheck className="h-6 w-6 text-blue-600" />
                  <h2 className="text-2xl font-semibold">7. Your Rights</h2>
                </div>
                <p className="text-gray-700 leading-relaxed mb-4">
                  Depending on your location, you may have the following rights regarding your personal information:
                </p>
                
                <div className="space-y-4">
                  <div>
                    <h3 className="text-lg font-semibold mb-2">Access and Portability</h3>
                    <p className="text-gray-700 leading-relaxed">
                      You can request access to your personal information and receive a copy in a machine-readable format.
                    </p>
                  </div>

                  <div>
                    <h3 className="text-lg font-semibold mb-2">Correction and Update</h3>
                    <p className="text-gray-700 leading-relaxed">
                      You can update or correct your personal information through your account settings or by contacting us.
                    </p>
                  </div>

                  <div>
                    <h3 className="text-lg font-semibold mb-2">Deletion</h3>
                    <p className="text-gray-700 leading-relaxed">
                      You can request deletion of your personal information, subject to legal requirements.
                    </p>
                  </div>

                  <div>
                    <h3 className="text-lg font-semibold mb-2">Consent Withdrawal</h3>
                    <p className="text-gray-700 leading-relaxed">
                      You can withdraw your consent for data processing at any time.
                    </p>
                  </div>
                </div>
              </section>

              {/* International Data Transfers */}
              <section>
                <h2 className="text-2xl font-semibold mb-4">8. International Data Transfers</h2>
                <p className="text-gray-700 leading-relaxed mb-4">
                  Your information may be transferred to and processed in countries other than your own. We ensure that such transfers comply with applicable data protection laws and implement appropriate safeguards, including:
                </p>
                <ul className="list-disc pl-6 space-y-2 text-gray-700">
                  <li>Standard contractual clauses approved by the European Commission</li>
                  <li>Adequacy decisions for countries with sufficient data protection</li>
                  <li>Additional security measures as required by law</li>
                </ul>
              </section>

              {/* Children's Privacy */}
              <section>
                <h2 className="text-2xl font-semibold mb-4">9. Children's Privacy</h2>
                <p className="text-gray-700 leading-relaxed">
                  Our Service is not intended for children under 18 years of age. We do not knowingly collect personal information from children under 18. If we become aware that we have collected personal information from a child under 18, we will take steps to delete such information.
                </p>
              </section>

              {/* Changes to This Policy */}
              <section>
                <h2 className="text-2xl font-semibold mb-4">10. Changes to This Privacy Policy</h2>
                <p className="text-gray-700 leading-relaxed mb-4">
                  We may update this Privacy Policy from time to time. We will notify you of any material changes by:
                </p>
                <ul className="list-disc pl-6 space-y-2 text-gray-700">
                  <li>Posting the updated policy on our website</li>
                  <li>Sending you an email notification</li>
                  <li>Displaying a prominent notice in our Service</li>
                </ul>
                <p className="text-gray-700 leading-relaxed mt-4">
                  Your continued use of our Service after any changes constitutes acceptance of the updated Privacy Policy.
                </p>
              </section>

              {/* Contact Information */}
              <section>
                <h2 className="text-2xl font-semibold mb-4">11. Contact Information</h2>
                <p className="text-gray-700 leading-relaxed mb-4">
                  If you have any questions about this Privacy Policy or our privacy practices, please contact us:
                </p>
                <div className="bg-gray-50 rounded-lg p-4 space-y-2">
                  <p className="text-gray-700">
                    <strong>Privacy Officer</strong><br />
                    ApplyAI, LLC<br />
                    Email: privacy@applyai.com<br />
                    Address: 123 Innovation Drive, San Francisco, CA 94105
                  </p>
                </div>
                <p className="text-gray-700 leading-relaxed mt-4">
                  For EU residents: You also have the right to lodge a complaint with your local data protection authority.
                </p>
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
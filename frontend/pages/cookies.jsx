import Link from "next/link"
import { Button } from "@/components/ui/button"
import { FileText, ArrowLeft, Cookie, Settings, BarChart, Shield, Globe, Zap } from "lucide-react"

export default function CookiesPolicy() {
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
              Cookie Policy
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
                  <Cookie className="h-6 w-6 text-blue-600" />
                  <h2 className="text-2xl font-semibold">1. What Are Cookies?</h2>
                </div>
                <p className="text-gray-700 leading-relaxed mb-4">
                  Cookies are small text files that are placed on your computer or mobile device when you visit a website. They are widely used to make websites work more efficiently and provide information to website owners.
                </p>
                <p className="text-gray-700 leading-relaxed">
                  This Cookie Policy explains how ApplyAI uses cookies and similar technologies when you visit our website and use our services. It explains what these technologies are, why we use them, and your rights to control our use of them.
                </p>
              </section>

              {/* Why We Use Cookies */}
              <section>
                <div className="flex items-center gap-3 mb-4">
                  <Zap className="h-6 w-6 text-blue-600" />
                  <h2 className="text-2xl font-semibold">2. Why We Use Cookies</h2>
                </div>
                <p className="text-gray-700 leading-relaxed mb-4">
                  We use cookies for several important reasons:
                </p>
                <ul className="list-disc pl-6 space-y-2 text-gray-700">
                  <li>To provide essential functionality and security</li>
                  <li>To remember your preferences and settings</li>
                  <li>To analyze how our website performs and improve user experience</li>
                  <li>To personalize content and features</li>
                  <li>To understand user behavior and optimize our services</li>
                  <li>To ensure our website works properly across different devices and browsers</li>
                </ul>
              </section>

              {/* Types of Cookies */}
              <section>
                <h2 className="text-2xl font-semibold mb-6">3. Types of Cookies We Use</h2>
                
                <div className="space-y-6">
                  <div className="bg-green-50 rounded-lg p-6 border border-green-200">
                    <div className="flex items-center gap-3 mb-3">
                      <Shield className="h-5 w-5 text-green-600" />
                      <h3 className="text-lg font-semibold text-green-800">Essential Cookies</h3>
                      <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded">Required</span>
                    </div>
                    <p className="text-gray-700 leading-relaxed mb-3">
                      These cookies are necessary for the website to function and cannot be switched off. They are usually set in response to actions you take, such as logging in or filling in forms.
                    </p>
                    <div className="text-sm text-gray-600">
                      <strong>Examples:</strong> Authentication tokens, security cookies, load balancing
                    </div>
                  </div>

                  <div className="bg-blue-50 rounded-lg p-6 border border-blue-200">
                    <div className="flex items-center gap-3 mb-3">
                      <Settings className="h-5 w-5 text-blue-600" />
                      <h3 className="text-lg font-semibold text-blue-800">Functional Cookies</h3>
                      <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">Optional</span>
                    </div>
                    <p className="text-gray-700 leading-relaxed mb-3">
                      These cookies enable enhanced functionality and personalization, such as remembering your preferences and choices.
                    </p>
                    <div className="text-sm text-gray-600">
                      <strong>Examples:</strong> Language preferences, theme settings, form auto-fill
                    </div>
                  </div>

                  <div className="bg-purple-50 rounded-lg p-6 border border-purple-200">
                    <div className="flex items-center gap-3 mb-3">
                      <BarChart className="h-5 w-5 text-purple-600" />
                      <h3 className="text-lg font-semibold text-purple-800">Analytics Cookies</h3>
                      <span className="text-xs bg-purple-100 text-purple-800 px-2 py-1 rounded">Optional</span>
                    </div>
                    <p className="text-gray-700 leading-relaxed mb-3">
                      These cookies help us understand how visitors interact with our website by collecting and reporting information anonymously.
                    </p>
                    <div className="text-sm text-gray-600">
                      <strong>Examples:</strong> Google Analytics, usage statistics, performance monitoring
                    </div>
                  </div>

                  <div className="bg-orange-50 rounded-lg p-6 border border-orange-200">
                    <div className="flex items-center gap-3 mb-3">
                      <Globe className="h-5 w-5 text-orange-600" />
                      <h3 className="text-lg font-semibold text-orange-800">Marketing Cookies</h3>
                      <span className="text-xs bg-orange-100 text-orange-800 px-2 py-1 rounded">Optional</span>
                    </div>
                    <p className="text-gray-700 leading-relaxed mb-3">
                      These cookies track your visit to our website and other websites to provide you with more relevant advertising.
                    </p>
                    <div className="text-sm text-gray-600">
                      <strong>Examples:</strong> Advertising pixels, remarketing tags, social media tracking
                    </div>
                  </div>
                </div>
              </section>

              {/* Specific Cookies We Use */}
              <section>
                <h2 className="text-2xl font-semibold mb-4">4. Specific Cookies We Use</h2>
                <div className="overflow-x-auto">
                  <table className="w-full border-collapse border border-gray-200 rounded-lg">
                    <thead>
                      <tr className="bg-gray-50">
                        <th className="border border-gray-200 p-3 text-left font-semibold">Cookie Name</th>
                        <th className="border border-gray-200 p-3 text-left font-semibold">Purpose</th>
                        <th className="border border-gray-200 p-3 text-left font-semibold">Duration</th>
                        <th className="border border-gray-200 p-3 text-left font-semibold">Type</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr>
                        <td className="border border-gray-200 p-3 font-mono text-sm">_session</td>
                        <td className="border border-gray-200 p-3">Maintains your login session</td>
                        <td className="border border-gray-200 p-3">Session</td>
                        <td className="border border-gray-200 p-3">Essential</td>
                      </tr>
                      <tr>
                        <td className="border border-gray-200 p-3 font-mono text-sm">_csrf</td>
                        <td className="border border-gray-200 p-3">Prevents cross-site request forgery</td>
                        <td className="border border-gray-200 p-3">Session</td>
                        <td className="border border-gray-200 p-3">Essential</td>
                      </tr>
                      <tr>
                        <td className="border border-gray-200 p-3 font-mono text-sm">preferences</td>
                        <td className="border border-gray-200 p-3">Remembers your settings and preferences</td>
                        <td className="border border-gray-200 p-3">1 year</td>
                        <td className="border border-gray-200 p-3">Functional</td>
                      </tr>
                      <tr>
                        <td className="border border-gray-200 p-3 font-mono text-sm">_ga</td>
                        <td className="border border-gray-200 p-3">Google Analytics - distinguishes users</td>
                        <td className="border border-gray-200 p-3">2 years</td>
                        <td className="border border-gray-200 p-3">Analytics</td>
                      </tr>
                      <tr>
                        <td className="border border-gray-200 p-3 font-mono text-sm">_gid</td>
                        <td className="border border-gray-200 p-3">Google Analytics - distinguishes users</td>
                        <td className="border border-gray-200 p-3">24 hours</td>
                        <td className="border border-gray-200 p-3">Analytics</td>
                      </tr>
                      <tr>
                        <td className="border border-gray-200 p-3 font-mono text-sm">_fbp</td>
                        <td className="border border-gray-200 p-3">Facebook Pixel - tracks conversions</td>
                        <td className="border border-gray-200 p-3">3 months</td>
                        <td className="border border-gray-200 p-3">Marketing</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </section>

              {/* Third-Party Cookies */}
              <section>
                <h2 className="text-2xl font-semibold mb-4">5. Third-Party Cookies</h2>
                <p className="text-gray-700 leading-relaxed mb-4">
                  We use several third-party services that may place cookies on your device:
                </p>
                
                <div className="space-y-4">
                  <div className="bg-gray-50 rounded-lg p-4">
                    <h3 className="font-semibold mb-2">Google Analytics</h3>
                    <p className="text-gray-700 text-sm leading-relaxed">
                      We use Google Analytics to analyze website traffic and user behavior. You can learn more about Google's privacy practices and opt out at: 
                      <a href="https://policies.google.com/privacy" className="text-blue-600 hover:underline ml-1">Google Privacy Policy</a>
                    </p>
                  </div>

                  <div className="bg-gray-50 rounded-lg p-4">
                    <h3 className="font-semibold mb-2">Payment Processors</h3>
                    <p className="text-gray-700 text-sm leading-relaxed">
                      We use secure payment processors (Stripe, PayPal) that may set cookies to facilitate payment processing and fraud prevention.
                    </p>
                  </div>

                  <div className="bg-gray-50 rounded-lg p-4">
                    <h3 className="font-semibold mb-2">Social Media Platforms</h3>
                    <p className="text-gray-700 text-sm leading-relaxed">
                      If you interact with social media features on our site, those platforms may set cookies to track your activity.
                    </p>
                  </div>
                </div>
              </section>

              {/* Your Cookie Choices */}
              <section>
                <h2 className="text-2xl font-semibold mb-4">6. Your Cookie Choices</h2>
                <p className="text-gray-700 leading-relaxed mb-4">
                  You have several options to control cookies:
                </p>
                
                <div className="space-y-4">
                  <div>
                    <h3 className="text-lg font-semibold mb-2">Browser Settings</h3>
                    <p className="text-gray-700 leading-relaxed mb-2">
                      Most browsers allow you to control cookies through their settings. You can:
                    </p>
                    <ul className="list-disc pl-6 space-y-1 text-gray-700">
                      <li>Block all cookies</li>
                      <li>Allow only first-party cookies</li>
                      <li>Delete cookies when you close your browser</li>
                      <li>Receive notifications when cookies are set</li>
                    </ul>
                  </div>

                  <div>
                    <h3 className="text-lg font-semibold mb-2">Cookie Consent Manager</h3>
                    <p className="text-gray-700 leading-relaxed">
                      We provide a cookie consent manager that allows you to choose which types of cookies you accept. You can access this tool at any time through the cookie settings link in our footer.
                    </p>
                  </div>

                  <div>
                    <h3 className="text-lg font-semibold mb-2">Opt-Out Links</h3>
                    <p className="text-gray-700 leading-relaxed mb-2">
                      You can opt out of specific tracking services:
                    </p>
                    <ul className="list-disc pl-6 space-y-1 text-gray-700">
                      <li>Google Analytics: <a href="https://tools.google.com/dlpage/gaoptout" className="text-blue-600 hover:underline">Google Analytics Opt-out</a></li>
                      <li>Facebook Pixel: <a href="https://www.facebook.com/settings?tab=ads" className="text-blue-600 hover:underline">Facebook Ad Settings</a></li>
                    </ul>
                  </div>
                </div>
              </section>

              {/* Impact of Disabling Cookies */}
              <section>
                <h2 className="text-2xl font-semibold mb-4">7. Impact of Disabling Cookies</h2>
                <p className="text-gray-700 leading-relaxed mb-4">
                  Please note that disabling cookies may affect your experience on our website:
                </p>
                <ul className="list-disc pl-6 space-y-2 text-gray-700">
                  <li>You may need to log in repeatedly</li>
                  <li>Your preferences and settings may not be remembered</li>
                  <li>Some features may not work properly</li>
                  <li>You may see less relevant content</li>
                  <li>Website performance may be affected</li>
                </ul>
              </section>

              {/* Mobile Devices */}
              <section>
                <h2 className="text-2xl font-semibold mb-4">8. Mobile Devices</h2>
                <p className="text-gray-700 leading-relaxed mb-4">
                  On mobile devices, we may use mobile identifiers and similar technologies for tracking and analytics purposes. You can control these through your device settings:
                </p>
                <ul className="list-disc pl-6 space-y-2 text-gray-700">
                  <li><strong>iOS:</strong> Settings → Privacy → Advertising → Limit Ad Tracking</li>
                  <li><strong>Android:</strong> Settings → Google → Ads → Opt out of interest-based ads</li>
                </ul>
              </section>

              {/* Changes to This Policy */}
              <section>
                <h2 className="text-2xl font-semibold mb-4">9. Changes to This Cookie Policy</h2>
                <p className="text-gray-700 leading-relaxed">
                  We may update this Cookie Policy from time to time to reflect changes in our practices or applicable laws. We will notify you of any material changes by posting the updated policy on our website and updating the "Last updated" date. We encourage you to review this policy periodically.
                </p>
              </section>

              {/* Contact Information */}
              <section>
                <h2 className="text-2xl font-semibold mb-4">10. Contact Us</h2>
                <p className="text-gray-700 leading-relaxed mb-4">
                  If you have any questions about this Cookie Policy or our use of cookies, please contact us:
                </p>
                <div className="bg-gray-50 rounded-lg p-4">
                  <p className="text-gray-700">
                    <strong>ApplyAI, LLC</strong><br />
                    Email: cookies@applyai.com<br />
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
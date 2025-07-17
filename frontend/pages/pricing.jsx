import React, { useState } from 'react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { FileText, Check, X, Star, Zap, Crown, Users, ArrowRight, Shield, Support, Clock, Infinity } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

const plans = [
  {
    id: 'free',
    name: 'Free',
    price: '$0',
    period: 'forever',
    description: 'Perfect for getting started with AI resume tailoring',
    icon: FileText,
    features: [
      { name: '3 resumes per month', included: true },
      { name: 'Up to 3 jobs per batch', included: true },
      { name: 'Basic AI tailoring', included: true },
      { name: 'Email support', included: true },
      { name: 'Cover letter generation', included: false },
      { name: 'Advanced AI features', included: false },
      { name: 'Priority support', included: false },
      { name: 'Unlimited resumes', included: false }
    ],
    cta: 'Get Started',
    popular: false
  },
  {
    id: 'pro',
    name: 'Pro',
    price: '$19',
    period: 'per month',
    description: 'For professionals who want the best results',
    icon: Crown,
    features: [
      { name: 'Unlimited resumes', included: true },
      { name: 'Up to 25 jobs per batch', included: true },
      { name: 'Advanced AI tailoring', included: true },
      { name: 'Priority support', included: true },
      { name: 'Cover letter generation', included: true },
      { name: 'Advanced AI features', included: true },
      { name: 'Resume analytics', included: true },
      { name: 'Custom templates', included: true }
    ],
    cta: 'Start Free Trial',
    popular: true
  }
];

export default function PricingPage() {
  const { isAuthenticated, user } = useAuth();
  const [billingCycle, setBillingCycle] = useState('monthly');

  const handlePlanSelect = (planId) => {
    if (!isAuthenticated) {
      window.location.href = '/register';
      return;
    }

    if (planId === 'free') {
      // Already on free plan
      return;
    }

    // For pro plan, redirect to payment (to be implemented)
    alert(`${planId} plan subscription will be implemented soon!`);
  };

  const getCurrentPlan = () => {
    if (!user) return null;
    return user.role || 'free';
  };

  const isCurrentPlan = (planId) => {
    return getCurrentPlan() === planId;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
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
        </nav>
        <div className="flex gap-4">
          {isAuthenticated ? (
            <Link href="/app">
              <Button variant="outline">Back to Dashboard</Button>
            </Link>
          ) : (
            <>
              <Link href="/login">
                <Button variant="outline">Log In</Button>
              </Link>
              <Link href="/register">
                <Button>Sign Up</Button>
              </Link>
            </>
          )}
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-16">
        {/* Hero Section */}
        <div className="text-center mb-16">
          <h1 className="text-4xl md:text-5xl font-bold mb-4">
            Choose the perfect plan for your
            <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent"> job search</span>
          </h1>
          <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
            Get more interviews with AI-powered resume tailoring. Start free, upgrade as you grow.
          </p>

          {/* Billing Toggle */}
          <div className="flex items-center justify-center gap-4 mb-12">
            <span className={`text-sm ${billingCycle === 'monthly' ? 'text-gray-900' : 'text-gray-500'}`}>
              Monthly
            </span>
            <button
              onClick={() => setBillingCycle(billingCycle === 'monthly' ? 'yearly' : 'monthly')}
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                billingCycle === 'yearly' ? 'bg-blue-600' : 'bg-gray-200'
              }`}
            >
              <span
                className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                  billingCycle === 'yearly' ? 'translate-x-6' : 'translate-x-1'
                }`}
              />
            </button>
            <span className={`text-sm ${billingCycle === 'yearly' ? 'text-gray-900' : 'text-gray-500'}`}>
              Yearly
            </span>
            {billingCycle === 'yearly' && (
              <span className="bg-green-100 text-green-800 text-xs px-2 py-1 rounded-full">
                Save 20%
              </span>
            )}
          </div>
        </div>

        {/* Current Plan Banner */}
        {isAuthenticated && (
          <div className="mb-8 p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-blue-600 font-medium">Current Plan</p>
                <p className="text-lg font-semibold text-blue-900 capitalize">
                  {getCurrentPlan()} Plan
                </p>
              </div>
              <div className="text-right">
                <p className="text-sm text-blue-600">
                  {user?.resumes_generated || 0} resumes generated this month
                </p>
                <p className="text-xs text-blue-500">
                  {user?.usage_limits?.resumes_per_month === -1 
                    ? 'Unlimited' 
                    : `${user?.usage_limits?.resumes_per_month || 3} per month limit`}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Pricing Cards */}
        <div className="grid md:grid-cols-2 gap-8 mb-16 max-w-4xl mx-auto">
          {plans.map((plan) => {
            const Icon = plan.icon;
            const price = billingCycle === 'yearly' && plan.price !== '$0' 
              ? `$${Math.round(parseFloat(plan.price.replace('$', '')) * 0.8)}`
              : plan.price;
            
            return (
              <Card 
                key={plan.id} 
                className={`relative bg-white/80 backdrop-blur-sm border-2 transition-all duration-300 hover:shadow-lg ${
                  plan.popular 
                    ? 'border-blue-500 shadow-blue-100' 
                    : 'border-gray-200 hover:border-blue-300'
                } ${isCurrentPlan(plan.id) ? 'ring-2 ring-green-500' : ''}`}
              >
                {plan.popular && (
                  <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
                    <span className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-4 py-1 rounded-full text-sm font-medium">
                      Most Popular
                    </span>
                  </div>
                )}

                {isCurrentPlan(plan.id) && (
                  <div className="absolute -top-3 right-4">
                    <span className="bg-green-500 text-white px-3 py-1 rounded-full text-xs font-medium">
                      Current
                    </span>
                  </div>
                )}

                <CardHeader className="text-center pb-4">
                  <div className="flex justify-center mb-4">
                    <div className={`p-3 rounded-full ${
                      plan.popular 
                        ? 'bg-gradient-to-r from-blue-600 to-purple-600' 
                        : 'bg-gray-100'
                    }`}>
                      <Icon className={`h-6 w-6 ${plan.popular ? 'text-white' : 'text-gray-600'}`} />
                    </div>
                  </div>
                  <CardTitle className="text-2xl font-bold">{plan.name}</CardTitle>
                  <CardDescription>{plan.description}</CardDescription>
                  <div className="mt-4">
                    <span className="text-4xl font-bold">{price}</span>
                    <span className="text-gray-600 ml-2">/{plan.period}</span>
                  </div>
                </CardHeader>

                <CardContent className="space-y-4">
                  <div className="space-y-3">
                    {plan.features.map((feature, index) => (
                      <div key={index} className="flex items-center gap-3">
                        {feature.included ? (
                          <Check className="h-5 w-5 text-green-500 flex-shrink-0" />
                        ) : (
                          <X className="h-5 w-5 text-gray-400 flex-shrink-0" />
                        )}
                        <span className={`text-sm ${feature.included ? 'text-gray-900' : 'text-gray-500'}`}>
                          {feature.name}
                        </span>
                      </div>
                    ))}
                  </div>

                  <Button
                    onClick={() => handlePlanSelect(plan.id)}
                    className={`w-full mt-6 ${
                      plan.popular
                        ? 'bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700'
                        : 'bg-gray-900 hover:bg-gray-800'
                    }`}
                    disabled={isCurrentPlan(plan.id)}
                  >
                    {isCurrentPlan(plan.id) ? 'Current Plan' : plan.cta}
                  </Button>
                </CardContent>
              </Card>
            );
          })}
        </div>

        {/* Features Comparison */}
        <div className="mb-16">
          <h2 className="text-3xl font-bold text-center mb-12">
            Compare all features
          </h2>
          <div className="bg-white/80 backdrop-blur-sm rounded-lg shadow-lg overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-4 text-left text-sm font-medium text-gray-900">Features</th>
                    {plans.map((plan) => (
                      <th key={plan.id} className="px-6 py-4 text-center text-sm font-medium text-gray-900">
                        {plan.name}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {[
                    'Resumes per month',
                    'Jobs per batch',
                    'Cover letter generation',
                    'Advanced AI features',
                    'Priority support',
                    'Resume analytics',
                    'Custom templates'
                  ].map((feature, index) => (
                    <tr key={index} className="hover:bg-gray-50">
                      <td className="px-6 py-4 text-sm font-medium text-gray-900">{feature}</td>
                      {plans.map((plan) => {
                        const planFeature = plan.features.find(f => f.name.toLowerCase().includes(feature.toLowerCase()));
                        return (
                          <td key={plan.id} className="px-6 py-4 text-center">
                            {planFeature ? (
                              planFeature.included ? (
                                <Check className="h-5 w-5 text-green-500 mx-auto" />
                              ) : (
                                <X className="h-5 w-5 text-gray-400 mx-auto" />
                              )
                            ) : (
                              <span className="text-sm text-gray-500">-</span>
                            )}
                          </td>
                        );
                      })}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {/* FAQ Section */}
        <div className="mb-16">
          <h2 className="text-3xl font-bold text-center mb-12">
            Frequently asked questions
          </h2>
          <div className="max-w-3xl mx-auto space-y-6">
            {[
              {
                question: "Can I change my plan anytime?",
                answer: "Yes, you can upgrade or downgrade your plan at any time. Changes take effect immediately, and you'll be charged/credited pro-rata."
              },
              {
                question: "What happens when I hit my monthly limit?",
                answer: "You'll be notified when you're close to your limit. You can either wait for next month or upgrade to a higher plan for more resumes."
              },
              {
                question: "Is there a free trial?",
                answer: "Yes! All paid plans come with a 7-day free trial. You can cancel anytime during the trial period without being charged."
              },
              {
                question: "Can I cancel my subscription?",
                answer: "Yes, you can cancel your subscription at any time. You'll continue to have access to your plan features until the end of your billing cycle."
              }
            ].map((faq, index) => (
              <Card key={index} className="bg-white/80 backdrop-blur-sm">
                <CardHeader>
                  <CardTitle className="text-lg">{faq.question}</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-gray-600">{faq.answer}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        {/* Final CTA */}
        <div className="text-center">
          <h2 className="text-3xl font-bold mb-4">
            Ready to land your dream job?
          </h2>
          <p className="text-xl text-gray-600 mb-8">
            Start with our free plan and upgrade when you're ready for more.
          </p>
          <Link href={isAuthenticated ? "/app" : "/register"}>
            <Button size="lg" className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700">
              {isAuthenticated ? "Go to Dashboard" : "Start Free Now"}
              <ArrowRight className="ml-2 h-5 w-5" />
            </Button>
          </Link>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t bg-white/80 backdrop-blur-sm mt-16">
        <div className="container mx-auto px-4 py-8">
          <div className="text-center text-gray-600">
            <p>&copy; 2024 ApplyAI. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
} 
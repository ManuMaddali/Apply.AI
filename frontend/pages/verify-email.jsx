import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Link from 'next/link';
import { FileText, CheckCircle, XCircle, Loader2, Mail } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { useAuth } from '../contexts/AuthContext';

export default function VerifyEmailPage() {
  const router = useRouter();
  const { verifyEmail, resendVerification, loading } = useAuth();
  const [status, setStatus] = useState('loading'); // 'loading', 'success', 'error'
  const [message, setMessage] = useState('');
  const [email, setEmail] = useState('');

  useEffect(() => {
    const { token } = router.query;
    
    if (token) {
      handleVerification(token);
    } else if (router.isReady) {
      setStatus('error');
      setMessage('No verification token provided');
    }
  }, [router.query, router.isReady]);

  const handleVerification = async (token) => {
    try {
      setStatus('loading');
      setMessage('Verifying your email address...');
      
      const result = await verifyEmail(token);
      
      if (result.success) {
        setStatus('success');
        setMessage('Email verified successfully! You can now log in.');
        // Redirect to login page after 3 seconds
        setTimeout(() => {
          router.push('/login');
        }, 3000);
      } else {
        setStatus('error');
        setMessage(result.error || 'Email verification failed');
      }
    } catch (error) {
      setStatus('error');
      setMessage('An error occurred during verification');
    }
  };

  const handleResendVerification = async () => {
    if (!email) {
      alert('Please enter your email address');
      return;
    }
    
    try {
      const result = await resendVerification(email);
      if (result.success) {
        alert('Verification email sent! Please check your inbox.');
      } else {
        alert(result.error || 'Failed to resend verification email');
      }
    } catch (error) {
      alert('An error occurred while sending verification email');
    }
  };

  const renderContent = () => {
    switch (status) {
      case 'loading':
        return (
          <div className="text-center py-8">
            <Loader2 className="h-16 w-16 animate-spin text-blue-600 mx-auto mb-4" />
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Verifying Email</h2>
            <p className="text-gray-600">{message}</p>
          </div>
        );
      
      case 'success':
        return (
          <div className="text-center py-8">
            <CheckCircle className="h-16 w-16 text-green-600 mx-auto mb-4" />
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Email Verified!</h2>
            <p className="text-gray-600 mb-4">{message}</p>
            <p className="text-sm text-gray-500 mb-6">Redirecting to login page...</p>
            <Button onClick={() => router.push('/login')} className="bg-blue-600 hover:bg-blue-700">
              Continue to Login
            </Button>
          </div>
        );
      
      case 'error':
        return (
          <div className="text-center py-8">
            <XCircle className="h-16 w-16 text-red-600 mx-auto mb-4" />
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Verification Failed</h2>
            <p className="text-gray-600 mb-6">{message}</p>
            
            <div className="space-y-4">
              <div className="border-t pt-4">
                <p className="text-sm text-gray-600 mb-4">
                  Need a new verification email?
                </p>
                <div className="flex space-x-2">
                  <input
                    type="email"
                    placeholder="Enter your email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                  <Button
                    onClick={handleResendVerification}
                    disabled={loading}
                    className="bg-blue-600 hover:bg-blue-700"
                  >
                    {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : 'Resend'}
                  </Button>
                </div>
              </div>
              
              <div className="border-t pt-4">
                <Link href="/login" passHref>
                  <Button variant="outline" className="w-full">
                    Back to Login
                  </Button>
                </Link>
              </div>
            </div>
          </div>
        );
      
      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        {/* Header */}
        <div className="text-center">
          <Link href="/" className="inline-flex items-center justify-center">
            <FileText className="h-10 w-10 text-blue-600" />
            <span className="ml-2 text-2xl font-bold text-gray-900">ApplyAI</span>
          </Link>
        </div>

        {/* Main Content */}
        <Card className="shadow-xl border-0 bg-white/70 backdrop-blur-sm">
          <CardHeader className="space-y-1 pb-4">
            <div className="flex items-center justify-center">
              <Mail className="h-8 w-8 text-blue-600" />
            </div>
            <CardTitle className="text-2xl text-center">Email Verification</CardTitle>
            <CardDescription className="text-center">
              Confirming your email address
            </CardDescription>
          </CardHeader>
          <CardContent>
            {renderContent()}
          </CardContent>
        </Card>

        {/* Footer */}
        <div className="text-center">
          <p className="text-sm text-gray-500">
            Having trouble? {' '}
            <Link href="/contact" className="text-blue-600 hover:text-blue-500">
              Contact support
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
} 
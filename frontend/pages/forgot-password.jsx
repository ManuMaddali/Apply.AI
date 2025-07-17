import React, { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/router';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { FileText, Mail, AlertCircle, CheckCircle, Loader2, ArrowLeft } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

export default function ForgotPasswordPage() {
  const router = useRouter();
  const { requestPasswordReset, loading, error, clearError } = useAuth();
  
  const [email, setEmail] = useState('');
  const [validationErrors, setValidationErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [success, setSuccess] = useState('');

  const handleInputChange = (e) => {
    setEmail(e.target.value);
    
    // Clear validation errors when user starts typing
    if (validationErrors.email) {
      setValidationErrors({});
    }
    
    // Clear global error
    if (error) {
      clearError();
    }
  };

  const validateForm = () => {
    const errors = {};
    
    if (!email) {
      errors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(email)) {
      errors.email = 'Please enter a valid email address';
    }
    
    return errors;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    const errors = validateForm();
    if (Object.keys(errors).length > 0) {
      setValidationErrors(errors);
      return;
    }
    
    setIsSubmitting(true);
    setValidationErrors({});
    clearError();
    
    try {
      const result = await requestPasswordReset(email);
      
      if (result.success) {
        setSuccess(result.message);
        // Show success message and redirect after a delay
        setTimeout(() => {
          router.push('/login');
        }, 5000);
      }
    } catch (error) {
      console.error('Password reset request error:', error);
    } finally {
      setIsSubmitting(false);
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
          <h2 className="mt-6 text-3xl font-bold text-gray-900">
            Forgot your password?
          </h2>
          <p className="mt-2 text-sm text-gray-600">
            Enter your email address and we'll send you a link to reset your password
          </p>
        </div>

        {/* Form */}
        <Card className="bg-white/80 backdrop-blur-sm border-white/50 shadow-xl">
          <CardHeader className="space-y-1">
            <CardTitle className="text-2xl text-center">Reset Password</CardTitle>
            <CardDescription className="text-center">
              We'll send you an email with instructions
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Success Message */}
            {success && (
              <div className="flex items-center p-4 bg-green-50 border border-green-200 rounded-md">
                <CheckCircle className="h-5 w-5 text-green-600 flex-shrink-0" />
                <div className="ml-2">
                  <p className="text-sm text-green-800">{success}</p>
                  <p className="text-xs text-green-600 mt-1">
                    Redirecting to login page in 5 seconds...
                  </p>
                </div>
              </div>
            )}

            {/* Error Message */}
            {error && (
              <div className="flex items-center p-4 bg-red-50 border border-red-200 rounded-md">
                <AlertCircle className="h-5 w-5 text-red-600" />
                <p className="ml-2 text-sm text-red-800">{error}</p>
              </div>
            )}

            {/* Form */}
            <form onSubmit={handleSubmit} className="space-y-4">
              {/* Email Input */}
              <div>
                <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
                  Email address
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <Mail className="h-5 w-5 text-gray-400" />
                  </div>
                  <input
                    id="email"
                    name="email"
                    type="email"
                    value={email}
                    onChange={handleInputChange}
                    className={`block w-full pl-10 pr-3 py-2 border ${
                      validationErrors.email ? 'border-red-300' : 'border-gray-300'
                    } rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent`}
                    placeholder="Enter your email address"
                    disabled={isSubmitting || success}
                  />
                </div>
                {validationErrors.email && (
                  <p className="mt-1 text-sm text-red-600">{validationErrors.email}</p>
                )}
              </div>

              {/* Submit Button */}
              <Button
                type="submit"
                className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700"
                disabled={isSubmitting || success}
              >
                {isSubmitting ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Sending reset link...
                  </>
                ) : (
                  'Send reset link'
                )}
              </Button>
            </form>

            {/* Back to Login */}
            <div className="text-center">
              <Link
                href="/login"
                className="inline-flex items-center text-sm text-blue-600 hover:text-blue-500"
              >
                <ArrowLeft className="h-4 w-4 mr-1" />
                Back to sign in
              </Link>
            </div>
          </CardContent>
        </Card>

        {/* Footer */}
        <div className="text-center">
          <p className="text-xs text-gray-500">
            Don't have an account?{' '}
            <Link href="/register" className="text-blue-600 hover:text-blue-500">
              Sign up for free
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
} 
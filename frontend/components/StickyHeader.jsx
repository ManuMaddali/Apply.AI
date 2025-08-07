import React, { useState, useEffect } from 'react'
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { FileText, Menu, X, User, LogOut, Settings, Star } from "lucide-react"
import { motion, AnimatePresence } from 'framer-motion'
import { PulseLightningIcon } from './ui/lightning-icon'
import { UsageRing } from './ui/donut-chart'
import { TierBadge } from './ui/tier-badge'
import { useAuth } from '../contexts/AuthContext'
import { useSubscription } from '../hooks/useSubscription'
import SubscriptionBadge from './SubscriptionBadge'

// Mobile Navigation Component
function MobileNav() {
  const [isOpen, setIsOpen] = useState(false)
  const { user, logout, isAuthenticated } = useAuth()
  const { weeklyUsage, weeklyLimit, isProUser } = useSubscription()

  const handleLogout = async () => {
    await logout()
    setIsOpen(false)
  }

  // Close menu on escape key
  useEffect(() => {
    const handleEscape = (e) => {
      if (e.key === 'Escape' && isOpen) {
        setIsOpen(false)
      }
    }

    if (isOpen) {
      document.addEventListener('keydown', handleEscape)
      // Prevent body scroll when menu is open
      document.body.style.overflow = 'hidden'
    }

    return () => {
      document.removeEventListener('keydown', handleEscape)
      document.body.style.overflow = 'unset'
    }
  }, [isOpen])

  const navigationItems = [
    { href: '/features', label: 'Features' },
    { href: '/how-it-works', label: 'How It Works' },
    { href: '/faq', label: 'FAQ' },
    { href: '/about', label: 'About' },
    { href: '/blog', label: 'Blog' },
    { href: '/contact', label: 'Contact' }
  ]

  return (
    <div className="md:hidden">
      <Button 
        variant="ghost" 
        size="icon" 
        onClick={() => setIsOpen(!isOpen)}
        aria-label={isOpen ? "Close navigation menu" : "Open navigation menu"}
        aria-expanded={isOpen}
        aria-controls="mobile-navigation"
        className="relative z-50"
      >
        <motion.div
          animate={{ rotate: isOpen ? 180 : 0 }}
          transition={{ duration: 0.2 }}
        >
          {isOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
        </motion.div>
      </Button>
      
      <AnimatePresence>
        {isOpen && (
          <>
            {/* Backdrop */}
            <motion.div
              className="fixed inset-0 bg-black/20 backdrop-blur-sm z-40"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.2 }}
              onClick={() => setIsOpen(false)}
            />
            
            {/* Menu Panel */}
            <motion.div
              id="mobile-navigation"
              className="fixed inset-x-0 top-16 z-50 bg-white/95 backdrop-blur-md border-b border-gray-200 shadow-xl"
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.25, ease: "easeOut" }}
              role="navigation"
              aria-label="Mobile navigation"
            >
              <div className="max-h-[calc(100vh-4rem)] overflow-y-auto">
                <nav className="p-6 space-y-6">
                  {isAuthenticated && (
                    <motion.div
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: 0.1 }}
                    >
                      {/* User info with usage ring */}
                      <div className="flex items-center gap-3 p-4 bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl border border-blue-100">
                        <div className="relative">
                          <div className="w-10 h-10 bg-blue-600 rounded-full flex items-center justify-center">
                            <User className="h-5 w-5 text-white" />
                          </div>
                          <div className="absolute -inset-1">
                            <UsageRing 
                              used={weeklyUsage}
                              limit={weeklyLimit}
                              size={48}
                              strokeWidth={2}
                            />
                          </div>
                        </div>
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <p className="font-medium text-gray-900 truncate">
                              {user?.full_name || user?.email}
                            </p>
                            <TierBadge 
                              tier={isProUser ? 'pro' : 'free'}
                              isActive={isProUser}
                              size="sm"
                              animated={true}
                            />
                          </div>
                          {!isProUser && (
                            <p className="text-xs text-purple-600 font-medium">
                              {weeklyUsage}/{weeklyLimit} sessions used
                            </p>
                          )}
                        </div>
                      </div>
                      
                      {/* User actions */}
                      <div className="border-t border-gray-100 pt-4 space-y-2">
                        <Link 
                          className="flex items-center gap-3 p-3 text-gray-700 hover:bg-gray-50 rounded-lg transition-colors" 
                          href="/dashboard" 
                          onClick={() => setIsOpen(false)}
                        >
                          <Settings className="h-5 w-5" />
                          <span className="font-medium">Dashboard</span>
                        </Link>
                        <Link 
                          className="flex items-center gap-3 p-3 text-purple-700 hover:bg-purple-50 rounded-lg transition-colors border border-purple-200 bg-purple-50/50" 
                          href="/pricing" 
                          onClick={() => setIsOpen(false)}
                        >
                          <Star className="h-5 w-5" />
                          <span className="font-medium">
                            {isProUser ? 'Manage Subscription' : 'Upgrade to Pro'}
                          </span>
                          {!isProUser && (
                            <TierBadge tier="pro" size="sm" className="ml-auto" />
                          )}
                        </Link>
                        <button 
                          onClick={handleLogout}
                          className="w-full flex items-center gap-3 p-3 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                        >
                          <LogOut className="h-5 w-5" />
                          <span className="font-medium">Sign out</span>
                        </button>
                      </div>
                    </motion.div>
                  )}
                  
                  {/* Navigation Links */}
                  <div className="space-y-2">
                    {navigationItems.map((item, index) => (
                      <motion.div
                        key={item.href}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.1 + (index * 0.05) }}
                      >
                        <Link 
                          className="block p-3 text-lg font-medium text-gray-700 hover:bg-gray-50 hover:text-blue-600 rounded-lg transition-colors" 
                          href={item.href} 
                          onClick={() => setIsOpen(false)}
                        >
                          {item.label}
                        </Link>
                      </motion.div>
                    ))}
                  </div>
                  
                  {/* Back to Home for non-authenticated users */}
                  {!isAuthenticated && (
                    <motion.div
                      className="pt-4 border-t border-gray-100"
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: 0.4 }}
                    >
                      <Link href="/" onClick={() => setIsOpen(false)}>
                        <Button variant="outline" className="w-full bg-transparent hover:bg-blue-50 hover:border-blue-200">
                          Back to Home
                        </Button>
                      </Link>
                    </motion.div>
                  )}
                </nav>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </div>
  )
}

// User Dropdown Component
function UserDropdown({ user, onLogout, weeklyUsage, weeklyLimit, isProUser }) {
  const [isOpen, setIsOpen] = useState(false)
  
  // Calculate next Monday for reset date
  const getNextResetDate = () => {
    const now = new Date()
    const nextMonday = new Date(now)
    const daysUntilMonday = (8 - now.getDay()) % 7 || 7
    nextMonday.setDate(now.getDate() + daysUntilMonday)
    return nextMonday
  }

  const resetDate = getNextResetDate()
  const daysUntilReset = Math.ceil((resetDate - new Date()) / (1000 * 60 * 60 * 24))

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 hover:bg-gray-50 rounded-lg p-2 transition-colors"
        aria-label="User menu"
        aria-expanded={isOpen}
      >
        <div className="relative">
          <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
            <User className="h-4 w-4 text-white" />
          </div>
          {/* Usage ring around avatar with hover details */}
          <div className="absolute -inset-1">
            <UsageRing 
              used={weeklyUsage}
              limit={weeklyLimit}
              size={40}
              strokeWidth={2}
              showHoverDetails={true}
              resetDate={resetDate}
            />
          </div>
        </div>
        <span className="text-sm font-medium hidden lg:block">
          {user?.full_name || user?.email}
        </span>
      </button>

      <AnimatePresence>
        {isOpen && (
          <motion.div
            className="absolute right-0 top-full mt-2 w-72 bg-white rounded-lg shadow-lg border border-gray-200 py-2 z-50"
            initial={{ opacity: 0, y: -10, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -10, scale: 0.95 }}
            transition={{ duration: 0.15 }}
          >
            {/* User info section */}
            <div className="px-4 py-3 border-b border-gray-100">
              <div className="flex items-center gap-3">
                <div className="relative">
                  <div className="w-12 h-12 bg-blue-600 rounded-full flex items-center justify-center">
                    <User className="h-6 w-6 text-white" />
                  </div>
                  <div className="absolute -inset-1">
                    <UsageRing 
                      used={weeklyUsage}
                      limit={weeklyLimit}
                      size={56}
                      strokeWidth={3}
                    />
                  </div>
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <p className="font-medium text-gray-900 truncate">
                      {user?.full_name || user?.email}
                    </p>
                    <TierBadge 
                      tier={isProUser ? 'pro' : 'free'}
                      isActive={isProUser}
                      size="sm"
                      animated={true}
                    />
                  </div>
                </div>
              </div>
              
              {/* Enhanced usage details with purple theme */}
              <div className="mt-3 p-3 bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg border border-purple-100">
                <div className="flex items-center justify-between text-sm mb-2">
                  <span className="text-gray-700 font-medium">Weekly Usage</span>
                  <span className="font-bold text-purple-600">
                    {isProUser ? '∞ Unlimited' : `${weeklyUsage}/${weeklyLimit}`}
                  </span>
                </div>
                
                {!isProUser && (
                  <>
                    {/* Progress bar */}
                    <div className="w-full bg-gray-200 rounded-full h-2 mb-2">
                      <div 
                        className="bg-gradient-to-r from-purple-500 to-purple-600 h-2 rounded-full transition-all duration-300"
                        style={{ width: `${Math.min((weeklyUsage / weeklyLimit) * 100, 100)}%` }}
                      />
                    </div>
                    
                    {/* Reset information */}
                    <div className="flex items-center justify-between text-xs">
                      <span className="text-gray-600">
                        {weeklyLimit - weeklyUsage} sessions remaining
                      </span>
                      <span className="text-purple-600 font-medium">
                        Resets in {daysUntilReset} day{daysUntilReset !== 1 ? 's' : ''}
                      </span>
                    </div>
                  </>
                )}
                
                {isProUser && (
                  <div className="text-xs text-purple-600 font-medium">
                    ✨ Pro benefits active
                  </div>
                )}
              </div>
            </div>

            {/* Menu items */}
            <div className="py-1">
              <Link 
                href="/dashboard"
                className="flex items-center gap-2 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                onClick={() => setIsOpen(false)}
              >
                <Settings className="h-4 w-4" />
                Dashboard
              </Link>
              <Link 
                href="/pricing"
                className={`flex items-center gap-2 px-4 py-2 text-sm transition-colors ${
                  isProUser 
                    ? 'text-gray-700 hover:bg-gray-50' 
                    : 'text-purple-700 hover:bg-purple-50 bg-purple-50/50 border-l-2 border-purple-300'
                }`}
                onClick={() => setIsOpen(false)}
              >
                <Star className="h-4 w-4" />
                {isProUser ? 'Manage Subscription' : 'Upgrade to Pro'}
                {!isProUser && (
                  <TierBadge tier="pro" size="sm" className="ml-auto" />
                )}
              </Link>
              <button 
                onClick={() => {
                  setIsOpen(false)
                  onLogout()
                }}
                className="w-full flex items-center gap-2 px-4 py-2 text-sm text-red-600 hover:bg-red-50"
              >
                <LogOut className="h-4 w-4" />
                Sign out
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

// Main StickyHeader Component
export default function StickyHeader() {
  const [isScrolled, setIsScrolled] = useState(false)
  const { user, logout, isAuthenticated } = useAuth()
  const { weeklyUsage, weeklyLimit, isProUser } = useSubscription()

  // Scroll detection effect
  useEffect(() => {
    const handleScroll = () => {
      const scrollTop = window.scrollY
      setIsScrolled(scrollTop > 10)
    }

    window.addEventListener('scroll', handleScroll, { passive: true })
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  const handleLogout = async () => {
    await logout()
    // Redirect to home page after logout
    window.location.href = '/'
  }

  return (
    <motion.header 
      className={`sticky top-0 z-40 px-4 lg:px-6 h-16 flex items-center justify-between border-b bg-white/80 backdrop-blur-sm transition-all duration-200 ${
        isScrolled ? 'shadow-md border-gray-200' : 'border-transparent'
      }`}
      initial={{ y: -64 }}
      animate={{ y: 0 }}
      transition={{ duration: 0.3 }}
    >
      {/* Logo with Lightning Icon */}
      <Link className="flex items-center gap-2 font-semibold" href="/">
        <div className="relative">
          <FileText className="h-6 w-6 text-blue-600" />
          <div className="absolute -top-1 -right-1">
            <PulseLightningIcon size={12} />
          </div>
        </div>
        <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
          ApplyAI
        </span>
      </Link>

      {/* Mobile Navigation */}
      <MobileNav />

      {/* Desktop Navigation */}
      <nav className="hidden md:flex gap-6">
        <Link 
          className="text-sm font-medium hover:underline underline-offset-4 transition-colors hover:text-blue-600" 
          href="/features"
        >
          Features
        </Link>
        <Link 
          className="text-sm font-medium hover:underline underline-offset-4 transition-colors hover:text-blue-600" 
          href="/how-it-works"
        >
          How It Works
        </Link>
        <Link 
          className="text-sm font-medium hover:underline underline-offset-4 transition-colors hover:text-blue-600" 
          href="/faq"
        >
          FAQ
        </Link>
        <Link 
          className="text-sm font-medium hover:underline underline-offset-4 transition-colors hover:text-blue-600" 
          href="/about"
        >
          About
        </Link>
        <Link 
          className="text-sm font-medium hover:underline underline-offset-4 transition-colors hover:text-blue-600" 
          href="/blog"
        >
          Blog
        </Link>
        <Link 
          className="text-sm font-medium hover:underline underline-offset-4 transition-colors hover:text-blue-600" 
          href="/contact"
        >
          Contact
        </Link>
      </nav>

      {/* Desktop User Section */}
      <div className="hidden md:flex gap-4 items-center">
        {isAuthenticated && (
          <>
            <SubscriptionBadge 
              onClick={() => window.open('/pricing', '_blank')}
              compact={true}
              showUsage={true}
              className="mr-2"
            />
            <UserDropdown 
              user={user}
              onLogout={handleLogout}
              weeklyUsage={weeklyUsage}
              weeklyLimit={weeklyLimit}
              isProUser={isProUser}
            />
          </>
        )}
      </div>
    </motion.header>
  )
}
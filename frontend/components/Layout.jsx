import React from 'react'
import ThemeToggle from './ThemeToggle'
import { useTheme } from '../contexts/ThemeContext'

const Layout = ({ children, showThemeToggle = true }) => {
  const { theme } = useTheme()

  return (
    <div className={`min-h-screen transition-colors duration-200 ${
      theme === 'light' 
        ? 'bg-white text-gray-900' 
        : theme === 'dark'
        ? 'bg-gray-900 text-white'
        : 'bg-tokyo-bg text-tokyo-text'
    }`}>
      {showThemeToggle && (
        <div className="fixed top-20 right-4 z-50">
          <ThemeToggle />
        </div>
      )}
      <div className="relative">
        {children}
      </div>
    </div>
  )
}

export default Layout

import React, { createContext, useContext, useEffect, useState } from 'react'

const ThemeContext = createContext()

export const useTheme = () => {
  const context = useContext(ThemeContext)
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider')
  }
  return context
}

export const THEMES = {
  light: 'light',
  dark: 'dark',
  tokyo: 'tokyo'
}

export const ThemeProvider = ({ children }) => {
  const [theme, setTheme] = useState(THEMES.light)

  useEffect(() => {
    // Load theme from localStorage on mount
    const savedTheme = localStorage.getItem('theme')
    if (savedTheme && Object.values(THEMES).includes(savedTheme)) {
      setTheme(savedTheme)
    } else {
      // Check system preference
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
      setTheme(prefersDark ? THEMES.dark : THEMES.light)
    }
  }, [])

  useEffect(() => {
    // Apply theme to document
    const root = document.documentElement
    
    // Remove all theme classes
    root.classList.remove('light', 'dark', 'tokyo')
    
    // Add current theme class
    root.classList.add(theme)
    
    // Save to localStorage
    localStorage.setItem('theme', theme)
  }, [theme])

  const toggleTheme = () => {
    const themes = Object.values(THEMES)
    const currentIndex = themes.indexOf(theme)
    const nextIndex = (currentIndex + 1) % themes.length
    setTheme(themes[nextIndex])
  }

  const setSpecificTheme = (newTheme) => {
    if (Object.values(THEMES).includes(newTheme)) {
      setTheme(newTheme)
    }
  }

  const value = {
    theme,
    setTheme: setSpecificTheme,
    toggleTheme,
    themes: THEMES
  }

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  )
}

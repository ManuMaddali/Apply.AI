import React from 'react'
import { useTheme } from '../contexts/ThemeContext'
import { Sun, Moon, Zap } from 'lucide-react'

const ThemeToggle = ({ className = '' }) => {
  const { theme, toggleTheme, themes } = useTheme()

  const getThemeIcon = () => {
    switch (theme) {
      case themes.light:
        return <Sun className="w-5 h-5" />
      case themes.dark:
        return <Moon className="w-5 h-5" />
      case themes.tokyo:
        return <Zap className="w-5 h-5" />
      default:
        return <Sun className="w-5 h-5" />
    }
  }

  const getThemeLabel = () => {
    switch (theme) {
      case themes.light:
        return 'Light'
      case themes.dark:
        return 'Dark'
      case themes.tokyo:
        return 'Tokyo'
      default:
        return 'Light'
    }
  }

  return (
    <button
      onClick={toggleTheme}
      className={`
        flex items-center gap-2 px-3 py-2 rounded-lg transition-all duration-200
        bg-gray-100 hover:bg-gray-200 text-gray-800
        dark:bg-gray-800 dark:hover:bg-gray-700 dark:text-gray-200
        tokyo:bg-purple-900/20 tokyo:hover:bg-purple-800/30 tokyo:text-purple-200
        border border-gray-200 dark:border-gray-700 tokyo:border-purple-500/30
        ${className}
      `}
      title={`Switch to ${theme === themes.light ? 'Dark' : theme === themes.dark ? 'Tokyo' : 'Light'} theme`}
    >
      {getThemeIcon()}
      <span className="text-sm font-medium hidden sm:inline">
        {getThemeLabel()}
      </span>
    </button>
  )
}

export default ThemeToggle

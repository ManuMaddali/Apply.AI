/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './lib/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  darkMode: 'class',
  theme: {
    extend: {
      animation: {
        'spin-slow': 'spin 3s linear infinite',
        'pulse-lightning': 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'fade-in': 'fadeIn 0.3s ease-in-out',
        'fade-in-up': 'fadeInUp 0.4s ease-out',
        'scale-hover': 'scaleHover 0.2s ease-in-out',
        'slide-in-left': 'slideInLeft 0.3s ease-out',
        'slide-in-right': 'slideInRight 0.3s ease-out',
        'bounce-subtle': 'bounceSubtle 0.6s ease-out',
        'progress-fill': 'progressFill 0.8s ease-out',
        'score-counter': 'scoreCounter 1s ease-out',
        'processing-pulse': 'processingPulse 2s ease-in-out infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        fadeInUp: {
          '0%': { opacity: '0', transform: 'translateY(30px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        scaleHover: {
          '0%': { transform: 'scale(1)' },
          '100%': { transform: 'scale(1.02)' },
        },
        slideInLeft: {
          '0%': { opacity: '0', transform: 'translateX(-30px)' },
          '100%': { opacity: '1', transform: 'translateX(0)' },
        },
        slideInRight: {
          '0%': { opacity: '0', transform: 'translateX(30px)' },
          '100%': { opacity: '1', transform: 'translateX(0)' },
        },
        bounceSubtle: {
          '0%, 20%, 50%, 80%, 100%': { transform: 'translateY(0)' },
          '40%': { transform: 'translateY(-10px)' },
          '60%': { transform: 'translateY(-5px)' },
        },
        progressFill: {
          '0%': { transform: 'scaleX(0)', transformOrigin: 'left' },
          '100%': { transform: 'scaleX(1)', transformOrigin: 'left' },
        },
        scoreCounter: {
          '0%': { opacity: '0', transform: 'scale(0.8)' },
          '50%': { transform: 'scale(1.1)' },
          '100%': { opacity: '1', transform: 'scale(1)' },
        },
        processingPulse: {
          '0%, 100%': { opacity: '0.5', transform: 'scale(1)' },
          '50%': { opacity: '1', transform: 'scale(1.05)' },
        },
      },
      colors: {
        // AI Redesign gradient colors
        'ai-purple': '#A78BFA',
        'ai-white': '#FFFFFF',
        'ai-gradient-start': '#A78BFA',
        'ai-gradient-end': '#FFFFFF',
        
        // App redesign color palette
        redesign: {
          primary: '#6366F1', // Indigo-500
          'primary-light': '#818CF8', // Indigo-400
          'primary-dark': '#4F46E5', // Indigo-600
          secondary: '#10B981', // Emerald-500
          'secondary-light': '#34D399', // Emerald-400
          'secondary-dark': '#059669', // Emerald-600
          accent: '#F59E0B', // Amber-500
          'accent-light': '#FBBF24', // Amber-400
          'accent-dark': '#D97706', // Amber-600
          success: '#10B981', // Emerald-500
          warning: '#F59E0B', // Amber-500
          error: '#EF4444', // Red-500
          info: '#3B82F6', // Blue-500
          neutral: {
            50: '#F9FAFB',
            100: '#F3F4F6',
            200: '#E5E7EB',
            300: '#D1D5DB',
            400: '#9CA3AF',
            500: '#6B7280',
            600: '#4B5563',
            700: '#374151',
            800: '#1F2937',
            900: '#111827',
          }
        },
        
        // Tokyo Night theme colors (preserved)
        tokyo: {
          bg: '#1a1b26',
          'bg-light': '#24283b',
          'bg-dark': '#16161e',
          text: '#c0caf5',
          'text-dim': '#9aa5ce',
          accent: '#7aa2f7',
          'accent-bright': '#bb9af7',
          success: '#9ece6a',
          warning: '#e0af68',
          error: '#f7768e',
          purple: '#bb9af7',
          cyan: '#7dcfff',
          green: '#9ece6a',
          orange: '#ff9e64',
          red: '#f7768e',
          yellow: '#e0af68',
          blue: '#7aa2f7'
        },
        
        // Shadcn UI color system
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        popover: {
          DEFAULT: "hsl(var(--popover))",
          foreground: "hsl(var(--popover-foreground))",
        },
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
      },
      backgroundImage: {
        'ai-gradient': 'linear-gradient(135deg, #A78BFA 0%, #FFFFFF 100%)',
        'ai-gradient-subtle': 'linear-gradient(135deg, #A78BFA 0%, #F3F4F6 100%)',
        'redesign-gradient': 'linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%)',
        'redesign-gradient-light': 'linear-gradient(135deg, #818CF8 0%, #A78BFA 100%)',
        'success-gradient': 'linear-gradient(135deg, #10B981 0%, #059669 100%)',
        'warning-gradient': 'linear-gradient(135deg, #F59E0B 0%, #D97706 100%)',
        'error-gradient': 'linear-gradient(135deg, #EF4444 0%, #DC2626 100%)',
        'neutral-gradient': 'linear-gradient(135deg, #F9FAFB 0%, #E5E7EB 100%)',
      },
      spacing: {
        '18': '4.5rem',
        '88': '22rem',
        '128': '32rem',
      },
      fontSize: {
        '2xs': ['0.625rem', { lineHeight: '0.75rem' }],
        '3xl': ['1.875rem', { lineHeight: '2.25rem' }],
        '4xl': ['2.25rem', { lineHeight: '2.5rem' }],
        '5xl': ['3rem', { lineHeight: '1' }],
        '6xl': ['3.75rem', { lineHeight: '1' }],
      },
      minHeight: {
        '44': '11rem', // Minimum touch target size
        'screen-75': '75vh',
        'screen-50': '50vh',
      },
      maxWidth: {
        '8xl': '88rem',
        '9xl': '96rem',
      },
      zIndex: {
        '60': '60',
        '70': '70',
        '80': '80',
        '90': '90',
        '100': '100',
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
    },
  },
  plugins: [
    // Plugin for accessibility utilities
    function({ addUtilities, theme, addVariant }) {
      // Add reduced motion variants
      addVariant('motion-safe', '@media (prefers-reduced-motion: no-preference)');
      addVariant('motion-reduce', '@media (prefers-reduced-motion: reduce)');
      
      // Add high contrast variants
      addVariant('contrast-more', '@media (prefers-contrast: more)');
      addVariant('contrast-less', '@media (prefers-contrast: less)');
      addVariant('contrast-high', '@media (prefers-contrast: high)');
      
      // Add forced colors variant (Windows High Contrast)
      addVariant('forced-colors', '@media (forced-colors: active)');
      
      // Add print variant
      addVariant('print', '@media print');
      
      // Add focus-visible variant for better keyboard navigation
      addVariant('focus-visible', '&:focus-visible');
      
      // Add utilities for accessibility
      addUtilities({
        '.sr-only': {
          position: 'absolute',
          width: '1px',
          height: '1px',
          padding: '0',
          margin: '-1px',
          overflow: 'hidden',
          clip: 'rect(0, 0, 0, 0)',
          whiteSpace: 'nowrap',
          border: '0',
        },
        '.not-sr-only': {
          position: 'static',
          width: 'auto',
          height: 'auto',
          padding: '0',
          margin: '0',
          overflow: 'visible',
          clip: 'auto',
          whiteSpace: 'normal',
        },
        '.skip-link': {
          position: 'absolute',
          top: '-2.5rem',
          left: '1rem',
          backgroundColor: theme('colors.blue.600'),
          color: theme('colors.white'),
          padding: '0.5rem 1rem',
          borderRadius: theme('borderRadius.md'),
          zIndex: '50',
          transition: 'all 0.3s ease',
          '&:focus': {
            top: '1rem',
          },
        },
        '.focus-ring': {
          '&:focus-visible': {
            outline: 'none',
            boxShadow: `0 0 0 2px ${theme('colors.blue.600')}`,
            borderRadius: theme('borderRadius.sm'),
          },
        },
        '.focus-ring-inset': {
          '&:focus-visible': {
            outline: 'none',
            boxShadow: `inset 0 0 0 2px ${theme('colors.blue.600')}`,
          },
        },
        // High contrast utilities
        '.contrast-high': {
          '@media (prefers-contrast: high)': {
            filter: 'contrast(1.5)',
          },
        },
        '.border-contrast': {
          '@media (prefers-contrast: high)': {
            borderWidth: '2px',
            borderColor: theme('colors.gray.900'),
          },
        },
        // Reduced motion utilities
        '.motion-safe-animate': {
          '@media (prefers-reduced-motion: no-preference)': {
            animation: 'var(--animation)',
          },
        },
        '.motion-safe-transition': {
          '@media (prefers-reduced-motion: no-preference)': {
            transition: 'var(--transition)',
          },
        },
        // Forced colors utilities
        '.forced-colors-adjust': {
          '@media (forced-colors: active)': {
            forcedColorAdjust: 'none',
          },
        },
        // Touch-friendly utilities
        '.touch-target': {
          minHeight: '44px',
          minWidth: '44px',
          touchAction: 'manipulation',
        },
        '.touch-target-large': {
          minHeight: '56px',
          minWidth: '56px',
          touchAction: 'manipulation',
        },
        // Performance utilities
        '.gpu-accelerated': {
          transform: 'translateZ(0)',
          willChange: 'transform',
        },
        '.optimize-legibility': {
          textRendering: 'optimizeLegibility',
          fontSmooth: 'antialiased',
          '-webkit-font-smoothing': 'antialiased',
          '-moz-osx-font-smoothing': 'grayscale',
        },
        // Layout utilities
        '.safe-area-inset': {
          paddingTop: 'env(safe-area-inset-top)',
          paddingRight: 'env(safe-area-inset-right)',
          paddingBottom: 'env(safe-area-inset-bottom)',
          paddingLeft: 'env(safe-area-inset-left)',
        },
        '.safe-area-inset-x': {
          paddingRight: 'env(safe-area-inset-right)',
          paddingLeft: 'env(safe-area-inset-left)',
        },
        '.safe-area-inset-y': {
          paddingTop: 'env(safe-area-inset-top)',
          paddingBottom: 'env(safe-area-inset-bottom)',
        },
        // Accessibility utilities for app redesign
        '.a11y-focus': {
          '&:focus-visible': {
            outline: `2px solid ${theme('colors.redesign.primary')}`,
            outlineOffset: '2px',
            borderRadius: theme('borderRadius.sm'),
          },
        },
        '.a11y-focus-inset': {
          '&:focus-visible': {
            outline: 'none',
            boxShadow: `inset 0 0 0 2px ${theme('colors.redesign.primary')}`,
          },
        },
        '.a11y-button': {
          minHeight: '44px',
          minWidth: '44px',
          touchAction: 'manipulation',
          '&:focus-visible': {
            outline: `2px solid ${theme('colors.redesign.primary')}`,
            outlineOffset: '2px',
          },
          '&:disabled': {
            opacity: '0.6',
            cursor: 'not-allowed',
          },
        },
      });
    },
  ],
}

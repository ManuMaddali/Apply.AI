/**
 * Dynamic Component Loader with advanced code splitting
 */
import React, { Suspense, useState, useEffect, useMemo } from 'react'
import { componentPreloader, modeBasedComponents, proOnlyComponents } from '../lib/code-splitting'
import { LoadingFallback } from '../lib/performance'

// Error boundary for lazy loaded components
class LazyComponentErrorBoundary extends React.Component {
  constructor(props) {
    super(props)
    this.state = { hasError: false, error: null }
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error }
  }

  componentDidCatch(error, errorInfo) {
    console.error('Lazy component loading error:', error, errorInfo)
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="p-6 bg-red-50 border border-red-200 rounded-lg">
          <h3 className="text-red-800 font-medium mb-2">Component Loading Error</h3>
          <p className="text-red-600 text-sm">
            Failed to load component. Please refresh the page or try again.
          </p>
          <button 
            onClick={() => this.setState({ hasError: false, error: null })}
            className="mt-3 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 text-sm"
          >
            Retry
          </button>
        </div>
      )
    }

    return this.props.children
  }
}

// Dynamic component loader with intelligent preloading
export const DynamicComponentLoader = ({ 
  componentName, 
  mode, 
  isProUser, 
  isMobile, 
  fallbackMessage,
  preloadStrategy = 'auto',
  ...props 
}) => {
  const [Component, setComponent] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  // Determine which component to load based on context
  const componentToLoad = useMemo(() => {
    // Mode-based selection
    if (mode && modeBasedComponents[mode]) {
      const modeComponents = modeBasedComponents[mode]
      
      // Mobile-specific component
      if (isMobile && modeComponents.mobile) {
        return modeComponents.mobile
      }
      
      // Default component for mode
      if (modeComponents.interface) {
        return modeComponents.interface
      }
    }

    // Pro-only component selection
    if (isProUser && proOnlyComponents[componentName]) {
      return proOnlyComponents[componentName]
    }

    // Fallback to direct component name
    return null
  }, [componentName, mode, isProUser, isMobile])

  // Load component
  useEffect(() => {
    let isMounted = true

    const loadComponent = async () => {
      try {
        setLoading(true)
        setError(null)

        let loadedComponent = null

        if (componentToLoad) {
          // Use pre-configured lazy component
          loadedComponent = componentToLoad
        } else {
          // Dynamic import fallback
          const importFunc = componentPreloader.getImportFunction(componentName)
          if (importFunc) {
            const module = await importFunc()
            loadedComponent = module.default || module
          }
        }

        if (isMounted && loadedComponent) {
          setComponent(() => loadedComponent)
        }
      } catch (err) {
        console.error(`Failed to load component ${componentName}:`, err)
        if (isMounted) {
          setError(err)
        }
      } finally {
        if (isMounted) {
          setLoading(false)
        }
      }
    }

    loadComponent()

    return () => {
      isMounted = false
    }
  }, [componentName, componentToLoad])

  // Preload related components based on strategy
  useEffect(() => {
    if (preloadStrategy === 'auto') {
      // Preload related components
      if (mode === 'batch') {
        componentPreloader.preloadComponents(['LiveProcessingVisualization', 'ProcessingCelebrationManager'])
      } else if (mode === 'precision') {
        componentPreloader.preloadComponents(['ExperienceTailoringInterface', 'RealTimeImpactPreview'])
      }

      // Preload pro components for pro users
      if (isProUser) {
        componentPreloader.preloadComponents(['TransformationMetricsDashboard', 'KeywordAnalysisEngine'])
      }
    }
  }, [mode, isProUser, preloadStrategy])

  if (error) {
    return (
      <div className="p-6 bg-red-50 border border-red-200 rounded-lg">
        <h3 className="text-red-800 font-medium mb-2">Component Loading Error</h3>
        <p className="text-red-600 text-sm">
          Failed to load {componentName}. Please refresh the page or try again.
        </p>
      </div>
    )
  }

  if (loading || !Component) {
    return <LoadingFallback message={fallbackMessage || `Loading ${componentName}...`} />
  }

  return (
    <LazyComponentErrorBoundary>
      <Suspense fallback={<LoadingFallback message={fallbackMessage} />}>
        <Component {...props} />
      </Suspense>
    </LazyComponentErrorBoundary>
  )
}

// Specialized loaders for different component types
export const ModeInterfaceLoader = ({ mode, isProUser, isMobile, ...props }) => (
  <DynamicComponentLoader
    componentName={`${mode}ModeInterface`}
    mode={mode}
    isProUser={isProUser}
    isMobile={isMobile}
    fallbackMessage={`Loading ${mode} mode interface...`}
    preloadStrategy="auto"
    {...props}
  />
)

export const AnalyticsComponentLoader = ({ componentType, isProUser, ...props }) => {
  if (!isProUser) {
    return (
      <div className="p-6 bg-blue-50 border border-blue-200 rounded-lg">
        <h3 className="text-blue-800 font-medium mb-2">Pro Feature</h3>
        <p className="text-blue-600 text-sm">
          Advanced analytics are available with Pro subscription.
        </p>
      </div>
    )
  }

  return (
    <DynamicComponentLoader
      componentName={componentType}
      isProUser={isProUser}
      fallbackMessage="Loading analytics..."
      preloadStrategy="manual"
      {...props}
    />
  )
}

export const ProcessingComponentLoader = ({ componentType, ...props }) => (
  <DynamicComponentLoader
    componentName={componentType}
    fallbackMessage="Loading processing component..."
    preloadStrategy="auto"
    {...props}
  />
)

// Hook for managing dynamic component loading
export const useDynamicComponent = (componentName, dependencies = []) => {
  const [component, setComponent] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    let isMounted = true

    const loadComponent = async () => {
      try {
        setLoading(true)
        setError(null)

        const importFunc = componentPreloader.getImportFunction(componentName)
        if (!importFunc) {
          throw new Error(`Component ${componentName} not found`)
        }

        const module = await importFunc()
        const Component = module.default || module

        if (isMounted) {
          setComponent(() => Component)
        }
      } catch (err) {
        console.error(`Failed to load component ${componentName}:`, err)
        if (isMounted) {
          setError(err)
        }
      } finally {
        if (isMounted) {
          setLoading(false)
        }
      }
    }

    loadComponent()

    return () => {
      isMounted = false
    }
  }, [componentName, ...dependencies])

  return { component, loading, error }
}

// Component registry for runtime loading
export const ComponentRegistry = {
  // Register a component for dynamic loading
  register: (name, importFunc) => {
    componentPreloader.preloadPromises.set(name, importFunc)
  },

  // Get component by name
  get: async (name) => {
    const importFunc = componentPreloader.getImportFunction(name)
    if (!importFunc) {
      throw new Error(`Component ${name} not registered`)
    }
    
    const module = await importFunc()
    return module.default || module
  },

  // Check if component is available
  has: (name) => {
    return componentPreloader.getImportFunction(name) !== undefined
  }
}

export default DynamicComponentLoader
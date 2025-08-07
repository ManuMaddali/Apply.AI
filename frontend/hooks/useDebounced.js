/**
 * Debounced hooks and utilities for performance optimization
 */
import { useState, useEffect, useCallback, useRef, useMemo } from 'react'
import { debounce, throttle } from '../lib/state-optimization'

// Debounced value hook
export const useDebouncedValue = (value, delay = 300) => {
  const [debouncedValue, setDebouncedValue] = useState(value)

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value)
    }, delay)

    return () => {
      clearTimeout(handler)
    }
  }, [value, delay])

  return debouncedValue
}

// Debounced callback hook
export const useDebouncedCallback = (callback, delay = 300, deps = []) => {
  const callbackRef = useRef(callback)
  
  // Update callback ref when dependencies change
  useEffect(() => {
    callbackRef.current = callback
  }, [callback, ...deps])

  return useMemo(() => {
    return debounce((...args) => {
      callbackRef.current(...args)
    }, delay)
  }, [delay])
}

// Throttled callback hook
export const useThrottledCallback = (callback, delay = 100, deps = []) => {
  const callbackRef = useRef(callback)
  
  useEffect(() => {
    callbackRef.current = callback
  }, [callback, ...deps])

  return useMemo(() => {
    return throttle((...args) => {
      callbackRef.current(...args)
    }, delay)
  }, [delay])
}

// Debounced input hook for form fields
export const useDebouncedInput = (initialValue = '', delay = 300) => {
  const [value, setValue] = useState(initialValue)
  const [debouncedValue, setDebouncedValue] = useState(initialValue)
  const [isDebouncing, setIsDebouncing] = useState(false)

  useEffect(() => {
    if (value === debouncedValue) {
      setIsDebouncing(false)
      return
    }

    setIsDebouncing(true)
    const handler = setTimeout(() => {
      setDebouncedValue(value)
      setIsDebouncing(false)
    }, delay)

    return () => {
      clearTimeout(handler)
    }
  }, [value, delay, debouncedValue])

  const handleChange = useCallback((newValue) => {
    setValue(newValue)
  }, [])

  const reset = useCallback((newValue = '') => {
    setValue(newValue)
    setDebouncedValue(newValue)
    setIsDebouncing(false)
  }, [])

  return {
    value,
    debouncedValue,
    isDebouncing,
    onChange: handleChange,
    reset
  }
}

// Debounced search hook
export const useDebouncedSearch = (searchFunction, delay = 500) => {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  
  const debouncedQuery = useDebouncedValue(query, delay)
  const searchRef = useRef(searchFunction)

  useEffect(() => {
    searchRef.current = searchFunction
  }, [searchFunction])

  useEffect(() => {
    if (!debouncedQuery.trim()) {
      setResults([])
      setLoading(false)
      setError(null)
      return
    }

    const performSearch = async () => {
      setLoading(true)
      setError(null)

      try {
        const searchResults = await searchRef.current(debouncedQuery)
        setResults(searchResults)
      } catch (err) {
        setError(err)
        setResults([])
      } finally {
        setLoading(false)
      }
    }

    performSearch()
  }, [debouncedQuery])

  const clearSearch = useCallback(() => {
    setQuery('')
    setResults([])
    setError(null)
    setLoading(false)
  }, [])

  return {
    query,
    setQuery,
    results,
    loading,
    error,
    clearSearch
  }
}

// Debounced API call hook
export const useDebouncedAPI = (apiFunction, dependencies = [], delay = 300) => {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  
  const debouncedDeps = useDebouncedValue(dependencies, delay)
  const apiRef = useRef(apiFunction)

  useEffect(() => {
    apiRef.current = apiFunction
  }, [apiFunction])

  useEffect(() => {
    // Skip if dependencies are empty or invalid
    if (!debouncedDeps || debouncedDeps.some(dep => dep === undefined || dep === null)) {
      return
    }

    const makeAPICall = async () => {
      setLoading(true)
      setError(null)

      try {
        const result = await apiRef.current(...debouncedDeps)
        setData(result)
      } catch (err) {
        setError(err)
        setData(null)
      } finally {
        setLoading(false)
      }
    }

    makeAPICall()
  }, [debouncedDeps])

  const refetch = useCallback(async () => {
    if (!dependencies || dependencies.some(dep => dep === undefined || dep === null)) {
      return
    }

    setLoading(true)
    setError(null)

    try {
      const result = await apiRef.current(...dependencies)
      setData(result)
    } catch (err) {
      setError(err)
      setData(null)
    } finally {
      setLoading(false)
    }
  }, [dependencies])

  return { data, loading, error, refetch }
}

// Debounced form validation hook
export const useDebouncedValidation = (value, validator, delay = 300) => {
  const [isValid, setIsValid] = useState(true)
  const [errors, setErrors] = useState([])
  const [isValidating, setIsValidating] = useState(false)
  
  const debouncedValue = useDebouncedValue(value, delay)
  const validatorRef = useRef(validator)

  useEffect(() => {
    validatorRef.current = validator
  }, [validator])

  useEffect(() => {
    if (!debouncedValue) {
      setIsValid(true)
      setErrors([])
      setIsValidating(false)
      return
    }

    const validate = async () => {
      setIsValidating(true)

      try {
        const result = await validatorRef.current(debouncedValue)
        
        if (typeof result === 'boolean') {
          setIsValid(result)
          setErrors(result ? [] : ['Validation failed'])
        } else if (result && typeof result === 'object') {
          setIsValid(result.isValid || false)
          setErrors(result.errors || [])
        }
      } catch (err) {
        setIsValid(false)
        setErrors([err.message || 'Validation error'])
      } finally {
        setIsValidating(false)
      }
    }

    validate()
  }, [debouncedValue])

  return { isValid, errors, isValidating }
}

// Debounced auto-save hook
export const useDebouncedAutoSave = (data, saveFunction, delay = 2000) => {
  const [isSaving, setIsSaving] = useState(false)
  const [lastSaved, setLastSaved] = useState(null)
  const [saveError, setSaveError] = useState(null)
  
  const debouncedData = useDebouncedValue(data, delay)
  const saveRef = useRef(saveFunction)

  useEffect(() => {
    saveRef.current = saveFunction
  }, [saveFunction])

  useEffect(() => {
    if (!debouncedData || debouncedData === lastSaved) {
      return
    }

    const autoSave = async () => {
      setIsSaving(true)
      setSaveError(null)

      try {
        await saveRef.current(debouncedData)
        setLastSaved(debouncedData)
      } catch (err) {
        setSaveError(err)
      } finally {
        setIsSaving(false)
      }
    }

    autoSave()
  }, [debouncedData, lastSaved])

  const forceSave = useCallback(async () => {
    if (!data) return

    setIsSaving(true)
    setSaveError(null)

    try {
      await saveRef.current(data)
      setLastSaved(data)
    } catch (err) {
      setSaveError(err)
    } finally {
      setIsSaving(false)
    }
  }, [data])

  return { isSaving, lastSaved, saveError, forceSave }
}

// Throttled scroll hook
export const useThrottledScroll = (callback, delay = 100) => {
  const callbackRef = useRef(callback)
  
  useEffect(() => {
    callbackRef.current = callback
  }, [callback])

  const throttledCallback = useMemo(() => {
    return throttle((event) => {
      callbackRef.current(event)
    }, delay)
  }, [delay])

  useEffect(() => {
    window.addEventListener('scroll', throttledCallback, { passive: true })
    
    return () => {
      window.removeEventListener('scroll', throttledCallback)
    }
  }, [throttledCallback])
}

// Throttled resize hook
export const useThrottledResize = (callback, delay = 250) => {
  const callbackRef = useRef(callback)
  
  useEffect(() => {
    callbackRef.current = callback
  }, [callback])

  const throttledCallback = useMemo(() => {
    return throttle((event) => {
      callbackRef.current(event)
    }, delay)
  }, [delay])

  useEffect(() => {
    window.addEventListener('resize', throttledCallback, { passive: true })
    
    return () => {
      window.removeEventListener('resize', throttledCallback)
    }
  }, [throttledCallback])
}

// Export all hooks
export {
  useDebouncedValue,
  useDebouncedCallback,
  useThrottledCallback,
  useDebouncedInput,
  useDebouncedSearch,
  useDebouncedAPI,
  useDebouncedValidation,
  useDebouncedAutoSave,
  useThrottledScroll,
  useThrottledResize
}
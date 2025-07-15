import '../styles/globals.css'
import { useRouter } from 'next/router'
import { useEffect } from 'react'

export default function App({ Component, pageProps }) {
  const router = useRouter()

  useEffect(() => {
    // Function to save scroll position
    const saveScrollPosition = () => {
      const scrollPosition = window.scrollY
      sessionStorage.setItem(`scroll-position-${router.asPath}`, scrollPosition.toString())
    }

    // Function to restore scroll position
    const restoreScrollPosition = () => {
      const savedPosition = sessionStorage.getItem(`scroll-position-${router.asPath}`)
      if (savedPosition) {
        // Use setTimeout to ensure the page has rendered before scrolling
        setTimeout(() => {
          window.scrollTo(0, parseInt(savedPosition))
        }, 100)
      }
    }

    // Save scroll position before route change
    const handleRouteChangeStart = () => {
      saveScrollPosition()
    }

    // Restore scroll position after route change complete
    const handleRouteChangeComplete = () => {
      restoreScrollPosition()
    }

    // Listen for route changes
    router.events.on('routeChangeStart', handleRouteChangeStart)
    router.events.on('routeChangeComplete', handleRouteChangeComplete)

    // Restore scroll position on initial load
    restoreScrollPosition()

    // Cleanup event listeners
    return () => {
      router.events.off('routeChangeStart', handleRouteChangeStart)
      router.events.off('routeChangeComplete', handleRouteChangeComplete)
    }
  }, [router])

  return <Component {...pageProps} />
} 
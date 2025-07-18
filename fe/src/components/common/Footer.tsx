import React from 'react'
import { useAppStore } from '@/store'
import Button from './Button'
import { api } from '@/services/api'
import toast from 'react-hot-toast'
import { Link } from 'react-router-dom'

const Footer: React.FC = () => {
  const { 
    addNotification, 
    setLoadingOverlay, 
    toggleSearchModal,
    addToSearchHistory,
    addRecentSearch,
    clearSearchHistory,
    clearRecentSearches
  } = useAppStore()

  // Only show in development
  if (process.env.NODE_ENV !== 'development') {
    return (
      <footer className="bg-card border-t border-border py-4">
        <div className="container mx-auto px-4">
          <div className="text-center text-muted-foreground text-sm">
            <p>&copy; 2024 EQDB. All rights reserved.</p>
          </div>
        </div>
      </footer>
    )
  }

  const testNotifications = () => {
    addNotification({
      type: 'success',
      message: 'Success notification test!',
      duration: 3000
    })
    
    setTimeout(() => {
      addNotification({
        type: 'error',
        message: 'Error notification test!',
        duration: 3000
      })
    }, 500)
    
    setTimeout(() => {
      addNotification({
        type: 'warning',
        message: 'Warning notification test!',
        duration: 3000
      })
    }, 1000)
    
    setTimeout(() => {
      addNotification({
        type: 'info',
        message: 'Info notification test!',
        duration: 3000
      })
    }, 1500)
  }

  const testLoadingStates = () => {
    setLoadingOverlay(true)
    setTimeout(() => setLoadingOverlay(false), 3000)
  }

  const testSearchHistory = () => {
    addToSearchHistory('Test Item Search')
    addToSearchHistory('Test Spell Search')
    addToSearchHistory('Test NPC Search')
    addRecentSearch('Test Item', 'items')
    addRecentSearch('Test Spell', 'spells')
    addRecentSearch('Test NPC', 'npcs')
    addNotification({
      type: 'info',
      message: 'Added test search history and recent searches',
      duration: 2000
    })
  }

  const testUIComponents = () => {
    addNotification({
      type: 'info',
      message: 'Check the console for UI component test results',
      duration: 2000
    })
    console.log('UI Components Test:', {
      buttons: 'Check different button variants in the toolbar',
      inputs: 'Form inputs should work properly',
      cards: 'Cards should have hover effects',
      loading: 'Loading spinners should animate'
    })
  }

  const testErrorBoundary = () => {
    addNotification({
      type: 'warning',
      message: 'Testing error boundary - check console for error',
      duration: 2000
    })
    // Simulate an error
    setTimeout(() => {
      console.error('Test error for error boundary')
      throw new Error('Test error for error boundary')
    }, 1000)
  }

  const clearAllData = () => {
    clearSearchHistory()
    clearRecentSearches()
    addNotification({
      type: 'success',
      message: 'Cleared all search history and recent searches',
      duration: 2000
    })
  }

  const clearRedisCache = async () => {
    try {
      await api.post('/cache/clear')
      toast.success('Redis cache cleared successfully!')
    } catch (error) {
      toast.error('Failed to clear Redis cache.')
      console.error('Failed to clear Redis cache:', error)
    }
  }

  const reindexItems = async () => {
    try {
      await api.post('/items/reindex')
      toast.success('Item re-indexing started successfully!')
    } catch (error) {
      toast.error('Failed to start item re-indexing.')
      console.error('Failed to start item re-indexing:', error)
    }
  }

  return (
    <footer className="bg-card border-t border-border">
      {/* Development Toolbar */}
      <div className="bg-warning/10 border-b border-warning/20 py-2">
        <div className="container mx-auto px-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <span className="text-xs font-medium text-warning-foreground bg-warning px-2 py-1 rounded">
                DEV TOOLBAR
              </span>
              <span className="text-xs text-warning-foreground/80">
                Week 2 Testing
              </span>
            </div>
            <div className="flex items-center space-x-2">
              <Button
                size="sm"
                variant="outline"
                onClick={testNotifications}
              >
                Test Notifications
              </Button>
              <Button
                size="sm"
                variant="outline"
                onClick={testLoadingStates}
              >
                Test Loading
              </Button>
              <Button
                size="sm"
                variant="outline"
                onClick={testSearchHistory}
              >
                Test Search History
              </Button>
              <Button
                size="sm"
                variant="outline"
                onClick={testUIComponents}
              >
                Test UI Components
              </Button>
              <Link to="/storybook">
                <Button size="sm" variant="outline">
                  Storybook
                </Button>
              </Link>
              <Button
                size="sm"
                variant="outline"
                onClick={toggleSearchModal}
              >
                Toggle Search Modal
              </Button>
              <Button
                size="sm"
                variant="outline"
                onClick={testErrorBoundary}
              >
                Test Error Boundary
              </Button>
              <Button
                size="sm"
                variant="danger"
                onClick={clearAllData}
              >
                Clear All Data
              </Button>
              <Button
                size="sm"
                variant="danger"
                onClick={clearRedisCache}
              >
                Clear Redis Cache
              </Button>
              <Button
                size="sm"
                variant="warning"
                onClick={reindexItems}
              >
                Re-index Items
              </Button>
            </div>
          </div>
        </div>
      </div>
      
      {/* Regular Footer */}
      <div className="py-4">
        <div className="container mx-auto px-4">
          <div className="text-center text-muted-foreground text-sm">
            <p>&copy; 2024 EQDB. All rights reserved.</p>
            <p className="mt-1 text-xs text-muted-foreground/80">
              Development Mode - Testing Week 2 Infrastructure
            </p>
          </div>
        </div>
      </div>
    </footer>
  )
}

export default Footer

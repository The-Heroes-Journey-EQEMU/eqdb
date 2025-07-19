import React from 'react'
import LoadingSpinner from './LoadingSpinner'

interface LoadingOverlayProps {
  isLoading: boolean
  message?: string
  children?: React.ReactNode
}

const LoadingOverlay: React.FC<LoadingOverlayProps> = ({
  isLoading,
  message = 'Loading...',
  children
}) => {
  if (!isLoading) {
    return <>{children}</>
  }

  return (
    <div className="absolute inset-0 bg-background/75 flex items-center justify-center z-50">
      <div className="text-center">
        <LoadingSpinner size="lg" className="mx-auto mb-4" />
        <p className="text-foreground">{message}</p>
      </div>
    </div>
  )
}

export default LoadingOverlay 
import React, { useEffect, useState } from 'react'

const ThemeTest: React.FC = () => {
  const [cssVariables, setCssVariables] = useState<Record<string, string>>({})
  const [isDark, setIsDark] = useState(false)

  useEffect(() => {
    const root = document.documentElement
    const computedStyle = getComputedStyle(root)
    
    const variables = [
      '--background',
      '--foreground',
      '--primary',
      '--primary-foreground',
      '--card',
      '--card-foreground',
      '--muted',
      '--muted-foreground',
      '--border',
      '--font-sans',
      '--spacing-md',
      '--radius-md'
    ]
    
    const values: Record<string, string> = {}
    variables.forEach(varName => {
      values[varName] = computedStyle.getPropertyValue(varName) || '(not set)'
    })
    
    setCssVariables(values)
    setIsDark(root.classList.contains('dark'))
  }, [])

  const toggleTheme = () => {
    const root = document.documentElement
    root.classList.toggle('dark')
    setIsDark(root.classList.contains('dark'))
    
    // Re-read CSS variables after theme change
    setTimeout(() => {
      const computedStyle = getComputedStyle(root)
      const variables = [
        '--background',
        '--foreground',
        '--primary',
        '--primary-foreground',
        '--card',
        '--card-foreground',
        '--muted',
        '--muted-foreground',
        '--border',
        '--font-sans',
        '--spacing-md',
        '--radius-md'
      ]
      
      const values: Record<string, string> = {}
      variables.forEach(varName => {
        values[varName] = computedStyle.getPropertyValue(varName) || '(not set)'
      })
      
      setCssVariables(values)
    }, 100)
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-foreground">Theme Test Component</h2>
        <button 
          onClick={toggleTheme}
          className="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors"
        >
          Toggle {isDark ? 'Light' : 'Dark'} Theme
        </button>
      </div>
      
      {/* CSS Variables Test */}
      <div className="space-y-4">
        <h3 className="text-lg font-semibold text-foreground">CSS Variables Test</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="p-4 bg-background text-foreground border border-border rounded-md">
            <h4 className="font-medium mb-2">Background & Foreground</h4>
            <p>This uses bg-background and text-foreground classes</p>
          </div>
          
          <div className="p-4 bg-card text-card-foreground border border-border rounded-md">
            <h4 className="font-medium mb-2">Card Theme</h4>
            <p>This uses bg-card and text-card-foreground classes</p>
          </div>
          
          <div className="p-4 bg-primary text-primary-foreground border border-border rounded-md">
            <h4 className="font-medium mb-2">Primary Theme</h4>
            <p>This uses bg-primary and text-primary-foreground classes</p>
          </div>
          
          <div className="p-4 bg-muted text-muted-foreground border border-border rounded-md">
            <h4 className="font-medium mb-2">Muted Theme</h4>
            <p>This uses bg-muted and text-muted-foreground classes</p>
          </div>
        </div>
      </div>

      {/* Direct CSS Variables Test */}
      <div className="space-y-4">
        <h3 className="text-lg font-semibold text-foreground">Direct CSS Variables Test</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div 
            style={{ 
              backgroundColor: 'var(--background)', 
              color: 'var(--foreground)',
              padding: 'var(--spacing-md)',
              border: '1px solid var(--border)',
              borderRadius: 'var(--radius-md)'
            }}
          >
            <h4 className="font-medium mb-2">Background & Foreground</h4>
            <p>This uses direct CSS variables</p>
          </div>
          
          <div 
            style={{ 
              backgroundColor: 'var(--card)', 
              color: 'var(--card-foreground)',
              padding: 'var(--spacing-md)',
              border: '1px solid var(--border)',
              borderRadius: 'var(--radius-md)'
            }}
          >
            <h4 className="font-medium mb-2">Card Theme</h4>
            <p>This uses direct CSS variables</p>
          </div>
        </div>
      </div>

      {/* CSS Variable Values */}
      <div className="space-y-4">
        <h3 className="text-lg font-semibold text-foreground">CSS Variable Values</h3>
        <div className="bg-muted p-4 rounded-md">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-sm font-mono">
            {Object.entries(cssVariables).map(([varName, value]) => (
              <div key={varName} className="flex justify-between">
                <span className="text-muted-foreground">{varName}:</span>
                <span className="text-foreground">{value}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Current Theme Status */}
      <div className="p-4 bg-card border border-border rounded-md">
        <h3 className="text-lg font-semibold text-card-foreground mb-2">Current Theme Status</h3>
        <p className="text-card-foreground">
          Current theme: <span className="font-medium">{isDark ? 'Dark' : 'Light'}</span>
        </p>
        <p className="text-muted-foreground text-sm mt-1">
          HTML element has class: {isDark ? '"dark"' : 'none'}
        </p>
      </div>
    </div>
  )
}

export default ThemeTest 
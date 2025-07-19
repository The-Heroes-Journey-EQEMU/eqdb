import React from 'react'

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string
  error?: string
  helperText?: string
  leftIcon?: React.ReactNode
  rightIcon?: React.ReactNode
  variant?: 'default' | 'search'
}

const Input: React.FC<InputProps> = ({
  label,
  error,
  helperText,
  leftIcon,
  rightIcon,
  variant = 'default',
  className = '',
  id,
  ...props
}) => {
  const inputId = id || `input-${Math.random().toString(36).substr(2, 9)}`
  
  const baseClasses = 'block w-full rounded-[24px] border border-border bg-background text-foreground placeholder-muted-foreground shadow-sm focus:border-ring focus:ring-ring focus:ring-2 focus:ring-offset-2 focus:ring-offset-background sm:text-sm transition-colors duration-200 px-[8px] py-[8px]'
  const errorClasses = 'border-destructive text-destructive placeholder-destructive/50 focus:border-destructive focus:ring-destructive'
  const searchClasses = 'pl-10'
  const iconClasses = 'absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none'
  const rightIconClasses = 'absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none'

  return (
    <div className={className}>
      {label && (
        <label htmlFor={inputId} className="block text-sm font-medium text-foreground mb-1">
          {label}
        </label>
      )}
      
      <div className="relative">
        {leftIcon && (
          <div className={iconClasses}>
            <div className="h-5 w-5 text-muted-foreground">
              {leftIcon}
            </div>
          </div>
        )}
        
        <input
          id={inputId}
          className={`
            ${baseClasses}
            ${error ? errorClasses : ''}
            ${variant === 'search' ? searchClasses : ''}
            ${leftIcon ? 'pl-10' : ''}
            ${rightIcon ? 'pr-10' : ''}
          `}
          {...props}
        />
        
        {rightIcon && (
          <div className={rightIconClasses}>
            <div className="h-5 w-5 text-muted-foreground">
              {rightIcon}
            </div>
          </div>
        )}
      </div>
      
      {error && (
        <p className="mt-1 text-sm text-destructive">
          {error}
        </p>
      )}
      
      {helperText && !error && (
        <p className="mt-1 text-sm text-muted-foreground">
          {helperText}
        </p>
      )}
    </div>
  )
}

export default Input 
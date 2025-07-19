import React from 'react'
import LoadingSpinner from './LoadingSpinner'

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger' | 'warning'
  size?: 'sm' | 'md' | 'lg'
  loading?: boolean
  leftIcon?: React.ReactNode
  rightIcon?: React.ReactNode
  children: React.ReactNode
}

const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  size = 'md',
  loading = false,
  leftIcon,
  rightIcon,
  children,
  className = '',
  disabled,
  ...props
}) => {
  const baseClasses = 'inline-flex items-center justify-center font-medium rounded-[24px] focus:outline-none focus:ring-2 focus:ring-offset-2 transition-colors duration-200 px-[8px] py-[8px]'
  
  const variantClasses = {
    primary: 'bg-primary text-primary-foreground hover:bg-primary/90 focus:ring-primary disabled:bg-primary/50',
    secondary: 'bg-secondary text-secondary-foreground hover:bg-secondary/90 focus:ring-secondary disabled:bg-secondary/50',
    outline: 'border border-border text-foreground hover:bg-muted focus:ring-primary disabled:bg-muted/50',
    ghost: 'text-foreground hover:bg-muted focus:ring-primary disabled:text-muted-foreground',
    danger: 'bg-destructive text-destructive-foreground hover:bg-destructive/90 focus:ring-destructive disabled:bg-destructive/50',
    warning: 'bg-warning text-warning-foreground hover:bg-warning/90 focus:ring-warning disabled:bg-warning/50'
  }

  const sizeClasses = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2 text-sm',
    lg: 'px-6 py-3 text-base'
  }

  const iconSizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-4 h-4',
    lg: 'w-5 h-5'
  }

  const isDisabled = disabled || loading

  return (
    <button
      className={`
        ${baseClasses}
        ${variantClasses[variant]}
        ${sizeClasses[size]}
        ${isDisabled ? 'cursor-not-allowed' : ''}
        ${className}
      `}
      disabled={isDisabled}
      {...props}
    >
      {loading ? (
        <LoadingSpinner size="sm" color="white" className="mr-2" />
      ) : leftIcon ? (
        <span className={`mr-2 ${iconSizeClasses[size]}`}>
          {leftIcon}
        </span>
      ) : null}
      
      {children}
      
      {rightIcon && !loading && (
        <span className={`ml-2 ${iconSizeClasses[size]}`}>
          {rightIcon}
        </span>
      )}
    </button>
  )
}

export default Button

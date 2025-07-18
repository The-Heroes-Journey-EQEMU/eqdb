import React from 'react'

export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'elevated' | 'outlined'
  hover?: boolean
}

const OUTER_RADIUS = '24px';
const INNER_RADIUS = '16px';
const CARD_PADDING = '8px';

const Card: React.FC<CardProps> = ({ 
  className = '', 
  variant = 'default', 
  hover = false,
  children,
  ...props 
}) => {
  const variants = {
    default: `bg-card border border-border`,
    elevated: `bg-card shadow-lg`,
    outlined: `bg-card border-2 border-border`
  }

  const classes = [
    `rounded-[${OUTER_RADIUS}]`,
    variants[variant],
    hover && 'hover:shadow-md transition-shadow duration-200',
    className
  ].filter(Boolean).join(' ')

  return (
    <div
      className={classes}
      {...props}
    >
      {children}
    </div>
  )
}

export const CardTitle: React.FC<React.HTMLAttributes<HTMLHeadingElement>> = ({ className = '', ...props }) => (
  <h3 className={`text-lg font-semibold ${className}`} {...props} />
);

// Card sub-components
export interface CardHeaderProps extends React.HTMLAttributes<HTMLDivElement> {}

export const CardHeader: React.FC<CardHeaderProps> = ({ className = '', children, ...props }) => {
  return (
    <div
      className={`px-[${CARD_PADDING}] py-[${CARD_PADDING}] border-b border-border rounded-t-[${INNER_RADIUS}] ${className}`}
      {...props}
    >
      {children}
    </div>
  )
}

export interface CardBodyProps extends React.HTMLAttributes<HTMLDivElement> {}

export const CardBody: React.FC<CardBodyProps> = ({ className = '', children, ...props }) => {
  return (
    <div
      className={`px-[${CARD_PADDING}] py-[${CARD_PADDING}] rounded-b-[${INNER_RADIUS}] ${className}`}
      {...props}
    >
      {children}
    </div>
  )
}

interface CardFooterProps {
  children: React.ReactNode
  className?: string
}

export const CardFooter: React.FC<CardFooterProps> = ({ children, className = '' }) => (
  <div className={`border-t border-gray-200 pt-3 mt-3 rounded-b-[${INNER_RADIUS}] ${className}`}>
    {children}
  </div>
)

export default Card

import React from 'react'
import { Link } from 'react-router-dom'
import { useAppStore, type NavigationItem } from '@/store'

const Breadcrumb: React.FC = () => {
  const { breadcrumbs } = useAppStore()

  if (breadcrumbs.length === 0) {
    return null
  }

  return (
    <nav className="breadcrumb" aria-label="Breadcrumb">
      {breadcrumbs.map((item: NavigationItem, index: number) => (
        <div key={item.id} className="breadcrumb-item">
          {index > 0 && (
            <span className="breadcrumb-separator">/</span>
          )}
          <Link
            to={item.href}
            className={`
              breadcrumb-link
              ${index === breadcrumbs.length - 1 ? 'breadcrumb-current' : ''}
            `}
          >
            <span className="mr-1">{item.icon}</span>
            {item.name}
          </Link>
        </div>
      ))}
    </nav>
  )
}

export default Breadcrumb 
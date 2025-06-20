import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import { useAppStore } from '@/store'

export interface NavigationItem {
  id: string
  name: string
  href: string
  icon: string
  type?: 'main' | 'search' | 'breadcrumb'
  parentId?: string
  children?: NavigationItem[]
  metadata?: Record<string, any>
}

export interface NavigationState {
  items: NavigationItem[]
  breadcrumbs: NavigationItem[]
  currentPath: string
  searchContext: {
    type: string
    query: string
    filters: Record<string, any>
  } | null
  history: NavigationItem[]
}

const Navigation: React.FC = () => {
  const location = useLocation()
  const { sidebarOpen, toggleSidebar, breadcrumbs, searchContext, history, updateNavigationState } = useAppStore()

  // Base navigation items
  const baseNavigation: NavigationItem[] = [
    { id: 'tools', name: 'Tools', href: '/tools', icon: '🛠️', type: 'main' },
    { id: 'spells', name: 'Spells', href: '/spells', icon: '✨', type: 'main' },
    { id: 'items', name: 'Items', href: '/items', icon: '⚔️', type: 'main' },
    { id: 'zones', name: 'Zones', href: '/zones', icon: '🗺️', type: 'main' },
    { id: 'npcs', name: 'NPCs', href: '/npcs', icon: '👤', type: 'main' },
    { id: 'tradeskills', name: 'Tradeskills', href: '/tradeskills', icon: '🔨', type: 'main' },
    { id: 'factions', name: 'Factions', href: '/factions', icon: '🏛️', type: 'main' },
    { id: 'quests', name: 'Quests', href: '/quests', icon: '📜', type: 'main' },
  ]

  // Get current navigation items (base + dynamic)
  const getCurrentNavigation = (): NavigationItem[] => {
    const items = [...baseNavigation]
    
    // Add search context items if available
    if (searchContext) {
      const { type, query } = searchContext
      items.push({
        id: `search-${type}`,
        name: `Search: ${query}`,
        href: `/search?type=${type}&q=${encodeURIComponent(query)}`,
        icon: '🔍',
        type: 'search',
        metadata: { searchType: type, query }
      })
    }

    // Add breadcrumb items
    if (breadcrumbs.length > 0) {
      items.push(...breadcrumbs.map((item: NavigationItem) => ({ ...item, type: 'breadcrumb' as const })))
    }

    return items
  }

  const isActive = (href: string): boolean => {
    if (href === '/') {
      return location.pathname === '/'
    }
    return location.pathname.startsWith(href)
  }

  const handleNavigationClick = (item: NavigationItem) => {
    // Add to history
    const newHistory = [item, ...history.filter((h: NavigationItem) => h.id !== item.id)].slice(0, 10)
    updateNavigationState({ history: newHistory })
    
    // Close mobile sidebar
    if (sidebarOpen) {
      toggleSidebar()
    }
  }

  const currentItems = getCurrentNavigation()

  return (
    <>
      {/* Desktop Navigation */}
      <nav className="hidden md:flex space-x-2">
        {currentItems.map((item: NavigationItem) => (
          <Link
            key={item.id}
            to={item.href}
            className={`
              nav-item
              ${isActive(item.href) ? 'active' : ''}
              ${item.type === 'search' ? 'bg-warning text-warning-foreground hover:bg-warning/80' : ''}
              ${item.type === 'breadcrumb' ? 'bg-muted text-muted-foreground hover:bg-muted/80' : ''}
            `}
            onClick={() => handleNavigationClick(item)}
          >
            <span className="text-base">{item.icon}</span>
            <span>{item.name}</span>
          </Link>
        ))}
      </nav>

      {/* Mobile Navigation */}
      {sidebarOpen && (
        <div className="md:hidden absolute top-16 left-0 right-0 bg-card border-b border-border shadow-lg z-50">
          <div className="px-2 pt-2 pb-3 space-y-1 sm:px-3">
            {currentItems.map((item: NavigationItem) => (
              <Link
                key={item.id}
                to={item.href}
                className={`
                  nav-item
                  ${isActive(item.href) ? 'active' : ''}
                  ${item.type === 'search' ? 'bg-warning text-warning-foreground hover:bg-warning/80' : ''}
                  ${item.type === 'breadcrumb' ? 'bg-muted text-muted-foreground hover:bg-muted/80' : ''}
                `}
                onClick={() => handleNavigationClick(item)}
              >
                <span className="text-lg">{item.icon}</span>
                <span>{item.name}</span>
              </Link>
            ))}
          </div>
        </div>
      )}
    </>
  )
}

export default Navigation 
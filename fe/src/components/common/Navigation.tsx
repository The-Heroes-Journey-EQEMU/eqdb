import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import { useAppStore } from '@/store'
import Dropdown from './Dropdown'

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
    {
      id: 'items',
      name: 'Items',
      href: '/items',
      icon: '⚔️',
      type: 'main',
      children: [
        { id: 'item-search', name: 'Item Search', href: '/items/search', icon: '🔍', parentId: 'items' },
        { id: 'armor-search', name: 'Armor Search', href: '/items/armor-search', icon: '🛡️', parentId: 'items' },
        { id: 'weapon-search', name: 'Weapon Search', href: '/items/weapon-search', icon: '🗡️', parentId: 'items' },
      ],
    },
    {
      id: 'spells',
      name: 'Spells',
      href: '/spells',
      icon: '✨',
      type: 'main',
      children: [
        { id: 'spell-list', name: 'Spell List', href: '/spells/list', icon: '📜', parentId: 'spells' },
        { id: 'spell-search', name: 'Spell Search', href: '/spells/search', icon: '🔍', parentId: 'spells' },
      ],
    },
    {
      id: 'zones',
      name: 'Zones',
      href: '/zones',
      icon: '🗺️',
      type: 'main',
      children: [
        { id: 'zone-list', name: 'Zone List', href: '/zones/list', icon: '🗺️', parentId: 'zones' },
        { id: 'waypoint-listing', name: 'Waypoint Listing', href: '/zones/waypoint-listing', icon: '📍', parentId: 'zones' },
      ],
    },
    { id: 'npcs', name: 'NPCs', href: '/npcs', icon: '👤', type: 'main' },
    { id: 'tradeskills', name: 'Tradeskills', href: '/tradeskills', icon: '🔨', type: 'main' },
    { id: 'factions', name: 'Factions', href: '/factions', icon: '🏛️', type: 'main' },
    { id: 'quests', name: 'Quests', href: '/quests', icon: '📜', type: 'main' },
  ];

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

  const renderNavItem = (item: NavigationItem, isMobile: boolean) => {
    const hasChildren = item.children && item.children.length > 0

    if (hasChildren) {
      return (
        <Dropdown
          key={item.id}
          item={item}
          isActive={isActive}
          handleNavigationClick={handleNavigationClick}
          isMobile={isMobile}
        />
      )
    }

    return (
      <Link
        key={item.id}
        to={item.href}
        className={`
          nav-item
          ${isActive(item.href) ? 'active' : ''}
          ${item.type === 'search' ? 'bg-warning text-warning-foreground hover:bg-warning/80' : ''}
          ${item.type === 'breadcrumb' ? 'bg-muted text-muted-foreground hover:bg-muted/80' : ''}
          ${isMobile ? 'w-full text-left' : ''}
        `}
        onClick={() => handleNavigationClick(item)}
      >
        <span className={`text-${isMobile ? 'lg' : 'base'}`}>{item.icon}</span>
        <span>{item.name}</span>
      </Link>
    )
  }

  return (
    <>
      {/* Desktop Navigation */}
      <nav className="hidden md:flex space-x-2">
        {currentItems.map((item: NavigationItem) => renderNavItem(item, false))}
      </nav>

      {/* Mobile Navigation */}
      {sidebarOpen && (
        <div className="md:hidden absolute top-16 left-0 right-0 bg-card border-b border-border shadow-lg z-50">
          <div className="px-2 pt-2 pb-3 space-y-1 sm:px-3">
            {currentItems.map((item: NavigationItem) => renderNavItem(item, true))}
          </div>
        </div>
      )}
    </>
  )
}

export default Navigation

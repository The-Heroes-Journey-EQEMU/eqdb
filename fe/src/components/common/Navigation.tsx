import { Link, useLocation } from 'react-router-dom';
import { useAppStore } from '@/store';
import Dropdown from './Dropdown';

export interface NavigationItem {
  id: string
  name: string
  href: string
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
      type: 'main',
      children: [
        { id: 'item-search', name: 'Item Search', href: '/items/search', parentId: 'items' },
        { id: 'armor-search', name: 'Armor Search', href: '/items/armor-search', parentId: 'items' },
        { id: 'weapon-search', name: 'Weapon Search', href: '/items/weapon-search', parentId: 'items' },
      ],
    },
    {
      id: 'spells',
      name: 'Spells',
      href: '/spells',
      type: 'main',
      children: [
        { id: 'spell-list', name: 'Spell List', href: '/spells/list', parentId: 'spells' },
        { id: 'spell-search', name: 'Spell Search', href: '/spells/search', parentId: 'spells' },
      ],
    },
    {
      id: 'zones',
      name: 'Zones',
      href: '/zones',
      type: 'main',
      children: [
        { id: 'zone-list', name: 'Zone List', href: '/zones/list', parentId: 'zones' },
        { id: 'waypoint-listing', name: 'Waypoint Listing', href: '/zones/waypoint-listing', parentId: 'zones' },
      ],
    },
    { id: 'npcs', name: 'NPCs', href: '/npcs', type: 'main' },
    { id: 'tradeskills', name: 'Tradeskills', href: '/tradeskills', type: 'main' },
    { id: 'factions', name: 'Factions', href: '/factions', type: 'main' },
    { id: 'quests', name: 'Quests', href: '/quests', type: 'main' },
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



  const renderNavItem = (item: NavigationItem) => {
    const hasChildren = item.children && item.children.length > 0;

    if (hasChildren) {
      return (
        <Dropdown
          key={item.id}
          item={item}
          isActive={isActive}
          handleNavigationClick={handleNavigationClick}
        />
      );
    }

    return (
      <div key={item.id}>
        <Link
          to={item.href}
          className="nav-item"
          onClick={() => handleNavigationClick(item)}
        >
          <span>{item.name}</span>
        </Link>
        {hasChildren && (
          <div className="pl-4">
            {item.children?.map((child) => renderNavItem(child))}
          </div>
        )}
      </div>
    );
  };

  return (
    <nav className="nav-menu">
      {currentItems.map((item) => renderNavItem(item))}
    </nav>
  );
}

export default Navigation

import { create } from 'zustand'
import { devtools, persist } from 'zustand/middleware'

// Navigation types
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

// User preferences and settings
interface UserPreferences {
  theme: 'light' | 'dark' | 'system'
  searchHistory: string[]
  favorites: {
    items: number[]
    spells: number[]
    npcs: number[]
  }
  settings: {
    autoSearch: boolean
    searchDelay: number
    resultsPerPage: number
  }
}

// UI state
interface UIState {
  sidebarOpen: boolean
  searchModalOpen: boolean
  loadingOverlay: boolean
  notifications: Array<{
    id: string
    type: 'success' | 'error' | 'warning' | 'info'
    message: string
    duration?: number
  }>
}

// Search state
interface SearchState {
  globalSearchQuery: string
  searchFilters: {
    items: Record<string, any>
    spells: Record<string, any>
    npcs: Record<string, any>
    zones: Record<string, any>
    quests: Record<string, any>
  }
  recentSearches: Array<{
    query: string
    type: string
    timestamp: number
  }>
}

// Main store interface
interface AppStore extends UserPreferences, UIState, SearchState, NavigationState {
  // User preferences actions
  setTheme: (theme: 'light' | 'dark' | 'system') => void
  addToSearchHistory: (query: string) => void
  clearSearchHistory: () => void
  toggleFavorite: (type: 'items' | 'spells' | 'npcs', id: number) => void
  updateSettings: (settings: Partial<UserPreferences['settings']>) => void

  // UI actions
  toggleSidebar: () => void
  setSidebarOpen: (open: boolean) => void
  toggleSearchModal: () => void
  setSearchModalOpen: (open: boolean) => void
  setLoadingOverlay: (loading: boolean) => void
  addNotification: (notification: Omit<UIState['notifications'][0], 'id'>) => void
  removeNotification: (id: string) => void
  clearNotifications: () => void

  // Search actions
  setGlobalSearchQuery: (query: string) => void
  setSearchFilters: (type: string, filters: Record<string, any>) => void
  clearSearchFilters: (type: string) => void
  addRecentSearch: (query: string, type: string) => void
  clearRecentSearches: () => void

  // Navigation actions
  updateNavigationState: (updates: Partial<NavigationState>) => void
  addBreadcrumb: (item: NavigationItem) => void
  removeBreadcrumb: (id: string) => void
  clearBreadcrumbs: () => void
  setSearchContext: (context: NavigationState['searchContext']) => void
  clearSearchContext: () => void
  addToHistory: (item: NavigationItem) => void
  clearHistory: () => void
}

// Create the store
export const useAppStore = create<AppStore>()(
  devtools(
    persist(
      (set, get) => ({
        // Initial state
        theme: 'system',
        searchHistory: [],
        favorites: {
          items: [],
          spells: [],
          npcs: []
        },
        settings: {
          autoSearch: true,
          searchDelay: 300,
          resultsPerPage: 20
        },
        sidebarOpen: false,
        searchModalOpen: false,
        loadingOverlay: false,
        notifications: [],
        globalSearchQuery: '',
        searchFilters: {
          items: {},
          spells: {},
          npcs: {},
          zones: {},
          quests: {}
        },
        recentSearches: [],
        // Navigation state
        items: [],
        breadcrumbs: [],
        currentPath: '/',
        searchContext: null,
        history: [],

        // User preferences actions
        setTheme: (theme) => set({ theme }),
        addToSearchHistory: (query) => {
          const { searchHistory } = get()
          const newHistory = [query, ...searchHistory.filter(q => q !== query)].slice(0, 10)
          set({ searchHistory: newHistory })
        },
        clearSearchHistory: () => set({ searchHistory: [] }),
        toggleFavorite: (type, id) => {
          const { favorites } = get()
          const currentFavorites = favorites[type]
          const newFavorites = currentFavorites.includes(id)
            ? currentFavorites.filter(favId => favId !== id)
            : [...currentFavorites, id]
          set({
            favorites: {
              ...favorites,
              [type]: newFavorites
            }
          })
        },
        updateSettings: (newSettings) => {
          const { settings } = get()
          set({
            settings: {
              ...settings,
              ...newSettings
            }
          })
        },

        // UI actions
        toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
        setSidebarOpen: (open) => set({ sidebarOpen: open }),
        toggleSearchModal: () => set((state) => ({ searchModalOpen: !state.searchModalOpen })),
        setSearchModalOpen: (open) => set({ searchModalOpen: open }),
        setLoadingOverlay: (loading) => set({ loadingOverlay: loading }),
        addNotification: (notification) => {
          const id = Math.random().toString(36).substr(2, 9)
          const newNotification = { ...notification, id }
          set((state) => ({
            notifications: [...state.notifications, newNotification]
          }))
          
          // Auto-remove notification after duration
          if (notification.duration !== 0) {
            setTimeout(() => {
              get().removeNotification(id)
            }, notification.duration || 5000)
          }
        },
        removeNotification: (id) => {
          set((state) => ({
            notifications: state.notifications.filter(n => n.id !== id)
          }))
        },
        clearNotifications: () => set({ notifications: [] }),

        // Search actions
        setGlobalSearchQuery: (query) => set({ globalSearchQuery: query }),
        setSearchFilters: (type, filters) => {
          set((state) => ({
            searchFilters: {
              ...state.searchFilters,
              [type]: filters
            }
          }))
        },
        clearSearchFilters: (type) => {
          set((state) => ({
            searchFilters: {
              ...state.searchFilters,
              [type]: {}
            }
          }))
        },
        addRecentSearch: (query, type) => {
          const { recentSearches } = get()
          const newSearch = { query, type, timestamp: Date.now() }
          const filteredSearches = recentSearches.filter(s => !(s.query === query && s.type === type))
          const newSearches = [newSearch, ...filteredSearches].slice(0, 20)
          set({ recentSearches: newSearches })
        },
        clearRecentSearches: () => set({ recentSearches: [] }),

        // Navigation actions
        updateNavigationState: (updates) => set((state) => ({ ...state, ...updates })),
        addBreadcrumb: (item) => {
          const { breadcrumbs } = get()
          const newBreadcrumbs = [...breadcrumbs.filter(b => b.id !== item.id), item]
          set({ breadcrumbs: newBreadcrumbs })
        },
        removeBreadcrumb: (id) => {
          const { breadcrumbs } = get()
          set({ breadcrumbs: breadcrumbs.filter(b => b.id !== id) })
        },
        clearBreadcrumbs: () => set({ breadcrumbs: [] }),
        setSearchContext: (context) => set({ searchContext: context }),
        clearSearchContext: () => set({ searchContext: null }),
        addToHistory: (item) => {
          const { history } = get()
          const newHistory = [item, ...history.filter(h => h.id !== item.id)].slice(0, 10)
          set({ history: newHistory })
        },
        clearHistory: () => set({ history: [] })
      }),
      {
        name: 'eqdb-store',
        partialize: (state) => ({
          theme: state.theme,
          searchHistory: state.searchHistory,
          favorites: state.favorites,
          settings: state.settings,
          recentSearches: state.recentSearches,
          history: state.history
        })
      }
    )
  )
) 
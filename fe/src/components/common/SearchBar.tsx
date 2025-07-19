import React, { useState, useRef, useEffect, useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import Input from './Input'
import { useItems, useSpells, useNPCs, useZones, useQuests } from '../../hooks/useApi'
import { useAppStore } from '../../store'

interface SearchResult {
  type: 'item' | 'spell' | 'npc' | 'zone' | 'quest'
  id: number
  name: string
  description?: string
}

const SearchBar: React.FC = () => {
  const navigate = useNavigate()
  const [query, setQuery] = useState('')
  const [debouncedQuery, setDebouncedQuery] = useState('')
  const [isOpen, setIsOpen] = useState(false)
  const searchRef = useRef<HTMLDivElement>(null)
  const debounceTimeoutRef = useRef<NodeJS.Timeout>()
  
  const { 
    setGlobalSearchQuery, 
    addToSearchHistory, 
    addRecentSearch,
    recentSearches 
  } = useAppStore()

  // Memoize search parameters to prevent infinite re-renders
  const searchParams = useMemo(() => ({ name: debouncedQuery }), [debouncedQuery])
  const queryOptions = useMemo(() => ({ enabled: debouncedQuery.length >= 2 }), [debouncedQuery])

  // API hooks for search - use memoized parameters
  const { data: items, isLoading: itemsLoading } = useItems(searchParams, queryOptions)
  const { data: spells = [], isLoading: spellsLoading } = useSpells(searchParams, queryOptions)
  const { data: npcs = [], isLoading: npcsLoading } = useNPCs(searchParams, queryOptions)
  const { data: zones = [], isLoading: zonesLoading } = useZones(searchParams, queryOptions)
  const { data: quests = [], isLoading: questsLoading } = useQuests(searchParams, queryOptions)

  // Memoize loading state
  const isLoading = useMemo(() => 
    itemsLoading || spellsLoading || npcsLoading || zonesLoading || questsLoading, 
    [itemsLoading, spellsLoading, npcsLoading, zonesLoading, questsLoading]
  )

  // Memoize processed search results
  const results = useMemo(() => {
    if (debouncedQuery.length >= 2) {
      const allResults: SearchResult[] = [
        ...(items && 'results' in items ? items.results : []).map((item: any) => ({
          type: 'item' as const,
          id: item.id,
          name: item.name,
          description: item.type
        })),
        ...spells.map((spell: any) => ({
          type: 'spell' as const,
          id: spell.id,
          name: spell.name,
          description: spell.description || spell.type
        })),
        ...npcs.map((npc: any) => ({
          type: 'npc' as const,
          id: npc.id,
          name: npc.name,
          description: npc.race || npc.class
        })),
        ...zones.map((zone: any) => ({
          type: 'zone' as const,
          id: zone.id,
          name: zone.name,
          description: zone.short_name || zone.type
        })),
        ...quests.map((quest: any) => ({
          type: 'quest' as const,
          id: quest.id,
          name: quest.name,
          description: quest.description || quest.type
        }))
      ]

      // Limit results to first 10 for performance
      return allResults.slice(0, 10)
    }
    return []
  }, [items, spells, npcs, zones, quests, debouncedQuery])

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (searchRef.current && !searchRef.current.contains(event.target as Node)) {
        setIsOpen(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  // Debounce the search query
  useEffect(() => {
    if (debounceTimeoutRef.current) {
      clearTimeout(debounceTimeoutRef.current)
    }

    if (query.length >= 2) {
      debounceTimeoutRef.current = setTimeout(() => {
        setDebouncedQuery(query)
      }, 1000)
    } else {
      setDebouncedQuery('')
    }

    return () => {
      if (debounceTimeoutRef.current) {
        clearTimeout(debounceTimeoutRef.current)
      }
    }
  }, [query])

  // Handle search input changes
  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value
    setQuery(value)
    setGlobalSearchQuery(value)
    
    if (value.length >= 2) {
      setIsOpen(true)
    } else {
      setIsOpen(false)
    }
  }

  // Handle search result selection
  const handleResultClick = (result: SearchResult) => {
    addToSearchHistory(result.name)
    addRecentSearch(result.name, result.type)
    setIsOpen(false)
    setQuery('')
    setGlobalSearchQuery('')
    
    // Navigate to appropriate page
    switch (result.type) {
      case 'item':
        navigate(`/items?name=${encodeURIComponent(result.name)}`)
        break
      case 'spell':
        navigate(`/spells?name=${encodeURIComponent(result.name)}`)
        break
      case 'npc':
        navigate(`/npcs?name=${encodeURIComponent(result.name)}`)
        break
      case 'zone':
        navigate(`/zones?name=${encodeURIComponent(result.name)}`)
        break
      case 'quest':
        navigate(`/quests?name=${encodeURIComponent(result.name)}`)
        break
    }
  }

  // Handle form submission
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (query.trim()) {
      addToSearchHistory(query)
      addRecentSearch(query, 'global')
      setIsOpen(false)
      
      // Navigate to items page with search query
      navigate(`/items?name=${encodeURIComponent(query)}`)
    }
  }

  const getTypeIcon = (type: string) => {
    const icons = {
      item: '⚔️',
      spell: '✨',
      npc: '👤',
      zone: '🗺️',
      quest: '📜'
    }
    return icons[type as keyof typeof icons] || '🔍'
  }

  const getTypeLabel = (type: string) => {
    const labels = {
      item: 'Item',
      spell: 'Spell',
      npc: 'NPC',
      zone: 'Zone',
      quest: 'Quest'
    }
    return labels[type as keyof typeof labels] || 'Unknown'
  }

  return (
    <div ref={searchRef} className="relative w-full max-w-lg">
      <form onSubmit={handleSubmit}>
        <Input
          type="text"
          placeholder="Search items, spells, NPCs, zones..."
          value={query}
          onChange={handleSearchChange}
          variant="search"
          leftIcon={
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          }
          rightIcon={
            isLoading ? (
              <div className="animate-spin rounded-full h-4 w-4 border-2 border-gray-300 border-t-blue-600" />
            ) : undefined
          }
        />
      </form>

      {/* Search Results Dropdown */}
      {isOpen && (results.length > 0 || isLoading) && (
        <div className="absolute top-full left-0 right-0 mt-1 bg-card border border-border rounded-lg shadow-lg z-50 max-h-96 overflow-y-auto">
          {isLoading ? (
            <div className="p-4 text-center text-muted-foreground">
              <div className="animate-spin rounded-full h-6 w-6 border-2 border-muted border-t-primary mx-auto mb-2" />
              Searching...
            </div>
          ) : results.length > 0 ? (
            <div className="py-2">
              {results.map((result, index) => (
                <button
                  key={`${result.type}-${result.id}-${index}`}
                  onClick={() => handleResultClick(result)}
                  className="w-full px-4 py-2 text-left hover:bg-muted focus:bg-muted focus:outline-none transition-colors"
                >
                  <div className="flex items-center space-x-3">
                    <span className="text-lg">{getTypeIcon(result.type)}</span>
                    <div className="flex-1 min-w-0">
                      <div className="text-sm font-medium text-foreground truncate">
                          {result.name}
                      </div>
                      <div className="text-xs text-muted-foreground flex items-center space-x-2">
                        <span className="bg-background px-2 py-1 rounded text-xs border border-border">
                          {getTypeLabel(result.type)}
                        </span>
                        {result.description && (
                          <span className="truncate">{result.description}</span>
                        )}
                      </div>
                    </div>
                  </div>
                </button>
              ))}
            </div>
          ) : debouncedQuery.length >= 2 ? (
            <div className="p-4 text-center text-muted-foreground">
              No results found for "{debouncedQuery}"
            </div>
          ) : null}
        </div>
      )}

          {/* Recent Searches */}
      {isOpen && results.length === 0 && !isLoading && debouncedQuery.length < 2 && recentSearches.length > 0 && (
        <div className="absolute top-full left-0 right-0 mt-1 bg-card border border-border rounded-lg shadow-lg z-50">
          <div className="p-3 border-b border-border">
            <h3 className="text-sm font-medium text-foreground">Recent Searches</h3>
              </div>
          <div className="py-2">
            {recentSearches.slice(0, 5).map((search, index) => (
                <button
                key={index}
                  onClick={() => {
                    setQuery(search.query)
                    setGlobalSearchQuery(search.query)
                    setIsOpen(false)
                  navigate(`/items?name=${encodeURIComponent(search.query)}`)
                  }}
                className="w-full px-4 py-2 text-left hover:bg-muted focus:bg-muted focus:outline-none transition-colors"
                >
                <div className="flex items-center space-x-3">
                  <span className="text-lg">{getTypeIcon(search.type)}</span>
                  <div className="flex-1">
                    <div className="text-sm text-foreground">{search.query}</div>
                    <div className="text-xs text-muted-foreground">{getTypeLabel(search.type)}</div>
                  </div>
                  </div>
                </button>
              ))}
            </div>
        </div>
      )}
    </div>
  )
}

export default SearchBar 
import React, { useState, useEffect, useRef } from 'react'
import { Link } from 'react-router-dom'
import { useAppStore } from '@/store'
import SearchBar from './SearchBar'

const Header: React.FC = () => {
  const { toggleSidebar, sidebarOpen } = useAppStore()
  const [toolsDropdownOpen, setToolsDropdownOpen] = useState(false)
  const dropdownRef = useRef<HTMLDivElement>(null)

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setToolsDropdownOpen(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [])

  return (
    <header className="bg-card shadow-sm border-b border-border">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <div className="flex items-center">
            <Link to="/" className="flex items-center">
              <img 
                src="/eqdb_alt_4.png" 
                alt="EQDB Logo" 
                className="w-16 h-16"
              />
            </Link>
          </div>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center space-x-6">
            {/* Tools Dropdown */}
            <div className="relative" ref={dropdownRef}>
              <button
                onClick={() => setToolsDropdownOpen(!toolsDropdownOpen)}
                className="flex items-center space-x-1 text-foreground hover:text-primary transition-colors"
              >
                <span>Tools</span>
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </button>
              
              {toolsDropdownOpen && (
                <div className="absolute top-full left-0 mt-1 w-48 bg-card border border-border rounded-md shadow-lg z-50">
                  <div className="py-2">
                    <Link to="/search/armor" className="block px-4 py-2 text-sm text-foreground hover:bg-muted">Armor Search</Link>
                    <Link to="/search/weapon" className="block px-4 py-2 text-sm text-foreground hover:bg-muted">Weapon Search</Link>
                    <Link to="/zone/waypoint/listing" className="block px-4 py-2 text-sm text-foreground hover:bg-muted">Waypoint List</Link>
                    <Link to="/spell/listing" className="block px-4 py-2 text-sm text-foreground hover:bg-muted">Class Spell Listing</Link>
                    <Link to="/pet/listing" className="block px-4 py-2 text-sm text-foreground hover:bg-muted">Pet Listing</Link>
                  </div>
                </div>
              )}
            </div>

            {/* Main Navigation Items */}
            <Link to="/search/spell" className="text-foreground hover:text-primary transition-colors">Spells</Link>
            <Link to="/item/search" className="text-foreground hover:text-primary transition-colors">Items</Link>
            <Link to="/zone/listing" className="text-foreground hover:text-primary transition-colors">Zones</Link>
            <Link to="/search/npc" className="text-foreground hover:text-primary transition-colors">NPCs</Link>
            <Link to="/search/tradeskill" className="text-foreground hover:text-primary transition-colors">Tradeskills</Link>
            <Link to="/search/faction" className="text-foreground hover:text-primary transition-colors">Factions</Link>
          </nav>

          {/* Search Bar */}
          <div className="flex-1 max-w-lg mx-8">
            <SearchBar />
          </div>

          {/* Right Side Navigation */}
          <nav className="hidden md:flex items-center space-x-6">
            <Link to="/user/" className="text-foreground hover:text-primary transition-colors">User Area</Link>
            <Link to="/identify/" className="text-foreground hover:text-primary transition-colors">Identify Items</Link>
            <Link to="/about" className="text-foreground hover:text-primary transition-colors">About</Link>
            <Link to="/changelog" className="text-foreground hover:text-primary transition-colors">Changelog</Link>
          </nav>

          {/* Mobile menu button */}
          <button
            onClick={toggleSidebar}
            className="md:hidden p-2 rounded-md text-muted-foreground hover:text-foreground hover:bg-muted"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
        </div>
      </div>

      {/* Mobile Navigation */}
      {sidebarOpen && (
        <div className="md:hidden absolute top-16 left-0 right-0 bg-card border-b border-border shadow-lg z-50">
          <div className="px-4 py-3 space-y-2">
            {/* Tools Section */}
            <div className="border-b border-border pb-2">
              <div className="text-sm font-medium text-muted-foreground mb-2">Tools</div>
              <div className="space-y-1">
                <Link to="/search/armor" className="block px-2 py-1 text-sm text-foreground hover:bg-muted rounded">Armor Search</Link>
                <Link to="/search/weapon" className="block px-2 py-1 text-sm text-foreground hover:bg-muted rounded">Weapon Search</Link>
                <Link to="/zone/waypoint/listing" className="block px-2 py-1 text-sm text-foreground hover:bg-muted rounded">Waypoint List</Link>
                <Link to="/spell/listing" className="block px-2 py-1 text-sm text-foreground hover:bg-muted rounded">Class Spell Listing</Link>
                <Link to="/pet/listing" className="block px-2 py-1 text-sm text-foreground hover:bg-muted rounded">Pet Listing</Link>
              </div>
            </div>

            {/* Main Navigation */}
            <div className="border-b border-border pb-2">
              <div className="space-y-1">
                <Link to="/search/spell" className="block px-2 py-1 text-sm text-foreground hover:bg-muted rounded">Spells</Link>
                <Link to="/item/search" className="block px-2 py-1 text-sm text-foreground hover:bg-muted rounded">Items</Link>
                <Link to="/zone/listing" className="block px-2 py-1 text-sm text-foreground hover:bg-muted rounded">Zones</Link>
                <Link to="/search/npc" className="block px-2 py-1 text-sm text-foreground hover:bg-muted rounded">NPCs</Link>
                <Link to="/search/tradeskill" className="block px-2 py-1 text-sm text-foreground hover:bg-muted rounded">Tradeskills</Link>
                <Link to="/search/faction" className="block px-2 py-1 text-sm text-foreground hover:bg-muted rounded">Factions</Link>
              </div>
            </div>

            {/* User Links */}
            <div className="space-y-1">
              <Link to="/user/" className="block px-2 py-1 text-sm text-foreground hover:bg-muted rounded">User Area</Link>
              <Link to="/identify/" className="block px-2 py-1 text-sm text-foreground hover:bg-muted rounded">Identify Items</Link>
              <Link to="/about" className="block px-2 py-1 text-sm text-foreground hover:bg-muted rounded">About</Link>
              <Link to="/changelog" className="block px-2 py-1 text-sm text-foreground hover:bg-muted rounded">Changelog</Link>
            </div>
          </div>
        </div>
      )}
    </header>
  )
}

export default Header 
import React from 'react';
import { Link } from 'react-router-dom';
import { useAppStore } from '@/store';
import SearchBar from './SearchBar';
import Navigation from './Navigation';

const Header: React.FC = () => {
  const { toggleSidebar, sidebarOpen } = useAppStore();

  return (
    <header className="bg-card shadow-sm border-b border-border">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 flex justify-between items-center h-16">
        {/* Logo */}
        <div className="flex items-center">
          <Link to="/" className="flex items-center">
            <img src="/eqdb_alt_4.png" alt="EQDB Logo" className="w-16 h-16" />
          </Link>
        </div>

        {/* Search Bar */}
        <div className="flex-1 max-w-lg mx-8">
          <SearchBar />
        </div>

        {/* Mobile menu button and dropdown */}
        <div className="relative">
          <button
            onClick={toggleSidebar}
            className="p-2 rounded-md text-muted-foreground hover:text-foreground hover:bg-muted"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
          {sidebarOpen && (
            <div className="nav-dropdown">
              <div className="nav-menu">
                <Navigation />
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};

export default Header

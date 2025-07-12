import React from 'react';
import { Link } from 'react-router-dom';
import { useAppStore } from '@/store';
import SearchBar from './SearchBar';
import Navigation from './Navigation';

const Header: React.FC = () => {
  const { toggleSidebar, sidebarOpen } = useAppStore();

  return (
    <header className="bg-card shadow-sm border-b border-border">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <div className="flex items-center">
            <Link to="/" className="flex items-center">
              <img src="/eqdb_alt_4.png" alt="EQDB Logo" className="w-16 h-16" />
            </Link>
          </div>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-6">
            <Navigation />
          </div>

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
            <Navigation />
          </div>
        </div>
      )}
    </header>
  );
};

export default Header

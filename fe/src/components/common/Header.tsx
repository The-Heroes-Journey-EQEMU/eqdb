import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useAppStore } from '@/store';
import { useAuth } from '@/contexts/AuthContext';
import SearchBar from './SearchBar';
import Navigation from './Navigation';
import LoginForm from '@/components/auth/LoginForm';

const Header: React.FC = () => {
  const { toggleSidebar, sidebarOpen } = useAppStore();
  const { isAuthenticated, user, logout } = useAuth();
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [showLoginModal, setShowLoginModal] = useState(false);

  const handleLogout = () => {
    logout();
    setShowUserMenu(false);
  };

  const handleLoginSuccess = () => {
    setShowLoginModal(false);
  };

  return (
    <>
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

          {/* Mobile menu button and user icon */}
          <div className="flex items-center space-x-2">
            {/* Mobile menu button with dropdown positioning */}
        <div className="relative">
          <button
            onClick={toggleSidebar}
            className="p-2 rounded-md text-muted-foreground hover:text-foreground hover:bg-muted"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
              
              {/* Mobile Navigation Dropdown */}
          {sidebarOpen && (
            <div className="nav-dropdown">
              <div className="nav-menu">
                <Navigation />
              </div>
            </div>
          )}
            </div>

            {/* User Circle Icon */}
            <div className="relative">
              <button
                onClick={() => {
                  if (isAuthenticated) {
                    setShowUserMenu(!showUserMenu);
                  } else {
                    setShowLoginModal(true);
                  }
                }}
                className="p-2 rounded-full text-muted-foreground hover:text-foreground hover:bg-muted transition-colors"
              >
                {isAuthenticated ? (
                  <div className="w-6 h-6 bg-primary rounded-full flex items-center justify-center">
                    <span className="text-primary-foreground text-xs font-medium">
                      {user?.email?.charAt(0).toUpperCase()}
                    </span>
                  </div>
                ) : (
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                  </svg>
                )}
              </button>

              {/* User Dropdown Menu */}
              {isAuthenticated && showUserMenu && (
                <div className="absolute right-0 mt-2 w-48 bg-card border border-border rounded-md shadow-lg z-50">
                  <div className="py-1">
                    <div className="px-4 py-2 text-xs text-muted-foreground border-b border-border">
                      Signed in as: {user?.email}
                    </div>
                    <Link
                      to="/user"
                      className="block px-4 py-2 text-sm text-muted-foreground hover:text-foreground hover:bg-muted"
                      onClick={() => setShowUserMenu(false)}
                    >
                      Profile & Settings
                    </Link>
                    <Link
                      to="/weight-sets"
                      className="block px-4 py-2 text-sm text-muted-foreground hover:text-foreground hover:bg-muted"
                      onClick={() => setShowUserMenu(false)}
                    >
                      Weight Sets
                    </Link>
                    <Link
                      to="/characters"
                      className="block px-4 py-2 text-sm text-muted-foreground hover:text-foreground hover:bg-muted"
                      onClick={() => setShowUserMenu(false)}
                    >
                      Characters
                    </Link>
                    {user?.is_admin && (
                      <Link
                        to="/admin"
                        className="block px-4 py-2 text-sm text-muted-foreground hover:text-foreground hover:bg-muted"
                        onClick={() => setShowUserMenu(false)}
                      >
                        Admin Dashboard
                      </Link>
                    )}
                    <button
                      onClick={handleLogout}
                      className="block w-full text-left px-4 py-2 text-sm text-muted-foreground hover:text-foreground hover:bg-muted"
                    >
                      Sign Out
                    </button>
                  </div>
                </div>
              )}
            </div>
        </div>
      </div>
    </header>

      {/* Login Modal */}
      {showLoginModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-background rounded-lg shadow-xl max-w-md w-full">
            <div className="flex justify-between items-center p-6 border-b border-border">
              <h2 className="text-xl font-semibold">Sign In</h2>
              <button
                onClick={() => setShowLoginModal(false)}
                className="text-muted-foreground hover:text-foreground"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            <div className="p-6">
              <LoginForm onSuccess={handleLoginSuccess} isModal={true} />
            </div>
          </div>
        </div>
      )}

      {/* Click outside to close user menu */}
      {showUserMenu && (
        <div
          className="fixed inset-0 z-40"
          onClick={() => setShowUserMenu(false)}
        />
      )}
    </>
  );
};

export default Header

import React from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Toaster } from 'react-hot-toast'
import { AuthProvider } from '@/contexts/AuthContext'
import { ProtectedRoute } from '@/components/auth/ProtectedRoute'
import Header from '@/components/common/Header'
import Footer from '@/components/common/Footer'
import ErrorBoundary from '@/components/common/ErrorBoundary'
import NotificationContainer from '@/components/common/Notification'
import LoadingOverlay from '@/components/common/LoadingOverlay'
import Home from '@/pages/Home'
import SearchPage from '@/pages/SearchPage'
import SpellSearchPage from '@/pages/SpellSearchPage'
import ZoneListPage from '@/pages/ZoneListPage'
import { ZoneDetailPage } from '@/pages/ZoneDetailPage'
import WaypointListingPage from '@/pages/WaypointListingPage'
import ClassSpellListPage from '@/pages/ClassSpellListPage'
import { WeightSetsPage } from '@/pages/WeightSetsPage'
import LoginForm from '@/components/auth/LoginForm'
import UserProfile from '@/components/auth/UserProfile'
import { useAppStore } from '@/store'
import './styles/custom.css'
import StorybookPage from '@/pages/StorybookPage';

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      retry: 1,
    },
  },
})

const AppContent: React.FC = () => {
  const { loadingOverlay } = useAppStore()

  return (
    <div className="min-h-screen bg-background text-foreground">
      <Header />
      <main className="flex-1">
        <Routes>
          <Route path="/storybook" element={<StorybookPage />} />
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<LoginForm />} />
          <Route path="/user" element={
            <ProtectedRoute>
              <div className="container mx-auto px-4 py-8">
                <UserProfile />
              </div>
            </ProtectedRoute>
          } />
          <Route path="/items/search" element={<SearchPage />} />
          <Route path="/spells/list" element={<ClassSpellListPage />} />
          <Route path="/spells/list/:classNames" element={<ClassSpellListPage />} />
          <Route path="/spells/search" element={<SpellSearchPage />} />
          <Route path="/spells/pets" element={<div className="p-8 text-center">Pet Spells - Coming Soon</div>} />
          <Route path="/zones/list" element={<ZoneListPage />} />
          <Route path="/zones/detail/:shortName" element={<ZoneDetailPage />} />
          <Route path="/zones/waypoint-listing" element={<WaypointListingPage />} />
          <Route path="/items" element={<SearchPage />} />
          <Route path="/spells" element={<SpellSearchPage />} />
          <Route path="/npcs" element={<div className="p-8 text-center">NPC Search - 123 Coming Soon</div>} />
          <Route path="/zones" element={<div className="p-8 text-center">Zone Listing - Coming Soon</div>} />
          <Route path="/tradeskills" element={<div className="p-8 text-center">Tradeskill Search - Coming Soon</div>} />
          <Route path="/quests" element={<div className="p-8 text-center">Quest Search - Coming Soon</div>} />
          <Route path="/factions" element={<div className="p-8 text-center">Faction Search - Coming Soon</div>} />
          
          {/* User-specific routes (protected) */}
          <Route path="/weight-sets" element={
            <ProtectedRoute>
              <WeightSetsPage />
            </ProtectedRoute>
          } />
          <Route path="/weight-sets/list" element={
            <ProtectedRoute>
              <div className="p-8 text-center">My Weight Sets - Coming Soon</div>
            </ProtectedRoute>
          } />
          <Route path="/weight-sets/create" element={
            <ProtectedRoute>
              <div className="p-8 text-center">Create Weight Set - Coming Soon</div>
            </ProtectedRoute>
          } />
          <Route path="/characters" element={
            <ProtectedRoute>
              <div className="p-8 text-center">Characters - Coming Soon</div>
            </ProtectedRoute>
          } />
          <Route path="/characters/list" element={
            <ProtectedRoute>
              <div className="p-8 text-center">My Characters - Coming Soon</div>
            </ProtectedRoute>
          } />
          <Route path="/characters/create" element={
            <ProtectedRoute>
              <div className="p-8 text-center">Create Character - Coming Soon</div>
            </ProtectedRoute>
          } />
          
          <Route path="/about" element={<div className="p-8 text-center">About - Coming Soon</div>} />
          <Route path="/changelog" element={<div className="p-8 text-center">Changelog - Coming Soon</div>} />
          <Route path="/search" element={<div className="p-8 text-center">Global Search Results - Coming Soon</div>} />
          <Route path="*" element={<div className="p-8 text-center">Page Not Found</div>} />
        </Routes>
      </main>
      <Footer />
      <NotificationContainer />
      <LoadingOverlay isLoading={loadingOverlay} />
    </div>
  )
}

const App: React.FC = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <ErrorBoundary>
          <Router future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
            <AppContent />
            <Toaster 
              position="top-right"
              toastOptions={{
                duration: 4000,
                style: {
                  background: 'var(--background)',
                  color: 'var(--foreground)',
                  border: '1px solid var(--border)',
                },
              }}
            />
          </Router>
        </ErrorBoundary>
      </AuthProvider>
    </QueryClientProvider>
  )
}

export default App

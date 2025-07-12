import React from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Toaster } from 'react-hot-toast'
import Header from '@/components/common/Header'
import Footer from '@/components/common/Footer'
import ErrorBoundary from '@/components/common/ErrorBoundary'
import NotificationContainer from '@/components/common/Notification'
import LoadingOverlay from '@/components/common/LoadingOverlay'
import Home from '@/pages/Home'
import ItemSearchPage from '@/pages/ItemSearchPage'
import SpellSearchPage from '@/pages/SpellSearchPage'
import ArmorSearchPage from '@/pages/ArmorSearchPage'
import WeaponSearchPage from '@/pages/WeaponSearchPage'
import ZoneListPage from '@/pages/ZoneListPage'
import WaypointListingPage from '@/pages/WaypointListingPage'
import ClassSpellListPage from '@/pages/ClassSpellListPage'
import { useAppStore } from '@/store'

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
          <Route path="/" element={<Home />} />
          <Route path="/items/search" element={<ItemSearchPage />} />
          <Route path="/items/armor-search" element={<ArmorSearchPage />} />
          <Route path="/items/weapon-search" element={<WeaponSearchPage />} />
          <Route path="/spells/list" element={<ClassSpellListPage />} />
          <Route path="/spells/list/:classNames" element={<ClassSpellListPage />} />
          <Route path="/spells/search" element={<SpellSearchPage />} />
          <Route path="/zones/list" element={<ZoneListPage />} />
          <Route path="/zones/waypoint-listing" element={<WaypointListingPage />} />
          <Route path="/items" element={<ItemSearchPage />} />
          <Route path="/spells" element={<SpellSearchPage />} />
          <Route path="/npcs" element={<div className="p-8 text-center">NPC Search - 123 Coming Soon</div>} />
          <Route path="/zones" element={<div className="p-8 text-center">Zone Listing - Coming Soon</div>} />
          <Route path="/tradeskills" element={<div className="p-8 text-center">Tradeskill Search - Coming Soon</div>} />
          <Route path="/quests" element={<div className="p-8 text-center">Quest Search - Coming Soon</div>} />
          <Route path="/factions" element={<div className="p-8 text-center">Faction Search - Coming Soon</div>} />
          <Route path="/user" element={<div className="p-8 text-center">User Area - Coming Soon</div>} />
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
    </QueryClientProvider>
  )
}

export default App

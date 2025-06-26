import React, { useState } from 'react'
import { useItems } from '@/hooks/useApi'
import { Item } from '@/services/itemService'
import { useAppStore } from '@/store'
import Card, { CardHeader, CardBody } from '@/components/common/Card'
import Button from '@/components/common/Button'
import Input from '@/components/common/Input'
import LoadingSpinner from '@/components/common/LoadingSpinner'

const ItemSearchPage: React.FC = () => {
  const [searchParams, setSearchParams] = useState({
    name: '',
    type: '',
    id: undefined as number | undefined
  })

  const { data: items, isLoading, error } = useItems(searchParams)
  const { addNotification, addRecentSearch } = useAppStore()

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    if (searchParams.name || searchParams.type || searchParams.id) {
      addRecentSearch(searchParams.name || 'Item Search', 'items')
      addNotification({
        type: 'info',
        message: 'Searching for items...',
        duration: 2000
      })
    }
  }

  const handleInputChange = (field: string, value: string | number | undefined) => {
    setSearchParams(prev => ({
      ...prev,
      [field]: value
    }))
  }

  const handleClearSearch = () => {
    setSearchParams({
      name: '',
      type: '',
      id: undefined
    })
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-foreground mb-2">Item Search</h1>
        <p className="text-muted-foreground">Search for weapons, armor, equipment, and consumables</p>
      </div>
      
      {/* Search Form */}
      <Card className="mb-8">
        <CardHeader>
          <h2 className="text-lg font-semibold text-foreground">Search Filters</h2>
        </CardHeader>
        <CardBody>
          <form onSubmit={handleSearch}>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <Input
                label="Item Name"
                placeholder="Search by item name..."
                value={searchParams.name}
                onChange={(e) => handleInputChange('name', e.target.value)}
              />
              
              <Input
                label="Item Type"
                placeholder="Search by item type..."
                value={searchParams.type}
                onChange={(e) => handleInputChange('type', e.target.value)}
              />
              
              <Input
                label="Item ID"
                type="number"
                placeholder="Search by item ID..."
                value={searchParams.id || ''}
                onChange={(e) => handleInputChange('id', e.target.value ? parseInt(e.target.value) : undefined)}
              />
            </div>
            
            <div className="flex items-center space-x-4 mt-6">
              <Button type="submit" loading={isLoading}>
                Search
              </Button>
              <Button variant="outline" onClick={handleClearSearch}>
                Clear
              </Button>
            </div>
          </form>
        </CardBody>
      </Card>

      {/* Results */}
      <div className="space-y-4">
        {isLoading && (
          <div className="text-center py-8">
            <LoadingSpinner size="lg" className="mx-auto mb-4" />
            <p className="text-muted-foreground">Searching for items...</p>
          </div>
        )}

        {error && (
          <Card variant="outlined">
            <CardBody>
              <div className="text-center py-4">
                <div className="text-destructive mb-2">
                  <svg className="w-8 h-8 mx-auto" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                  </svg>
                </div>
                <p className="text-destructive font-medium">Error loading items</p>
                <p className="text-destructive/80 text-sm mt-1">{error.message}</p>
              </div>
            </CardBody>
          </Card>
        )}

        {items && items.length > 0 && (
          <div>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold text-foreground">
                Results ({items.length})
              </h2>
              <Button variant="outline" size="sm">
                Export Results
              </Button>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {items.map((item: Item) => (
                <Card key={item.id} hover>
                  <CardBody>
                    <div className="flex items-start justify-between mb-2">
                      <h3 className="font-semibold text-lg text-foreground truncate">
                        {item.name}
                      </h3>
                      <span className="text-xs text-muted-foreground bg-muted px-2 py-1 rounded">
                        ID: {item.id}
                      </span>
                    </div>
                    
                    <div className="space-y-2 text-sm text-muted-foreground">
                      <p><span className="font-medium">Type:</span> {item.type}</p>
                      {item.serialized && (
                        <div>
                          <span className="font-medium">Data:</span>
                          <p className="text-xs bg-background p-2 rounded mt-1 font-mono overflow-hidden border border-border">
                            {item.serialized.substring(0, 100)}
                            {item.serialized.length > 100 && '...'}
                          </p>
                        </div>
                      )}
                    </div>
                    
                    <div className="flex items-center space-x-2 mt-4">
                      <Button size="sm" variant="outline">
                        View Details
                      </Button>
                      <Button size="sm" variant="ghost">
                        Add to Favorites
                      </Button>
                    </div>
                  </CardBody>
                </Card>
              ))}
            </div>
          </div>
        )}

        {items && items.length === 0 && !isLoading && (
          <Card>
            <CardBody>
              <div className="text-center py-8">
                <div className="text-muted-foreground mb-4">
                  <svg className="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
                </div>
                <p className="text-muted-foreground font-medium">No items found</p>
                <p className="text-muted-foreground/80 text-sm mt-1">
                  Try adjusting your search criteria
                </p>
              </div>
            </CardBody>
          </Card>
        )}

        {!items && !isLoading && !error && (
          <Card>
            <CardBody>
              <div className="text-center py-8">
                <div className="text-muted-foreground mb-4">
                  <svg className="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
                </div>
                <p className="text-muted-foreground font-medium">Ready to search</p>
                <p className="text-muted-foreground/80 text-sm mt-1">
                  Enter your search criteria above to find items
                </p>
              </div>
            </CardBody>
          </Card>
        )}
      </div>
    </div>
  )
}

export default ItemSearchPage 
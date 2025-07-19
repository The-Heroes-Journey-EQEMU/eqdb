import React, { useState } from 'react'
import { useSpells } from '@/hooks/useApi'
import { Spell } from '@/services/spellService'
import Input from '@/components/common/Input'
import Button from '@/components/common/Button'

const SpellSearchPage: React.FC = () => {
  const [searchParams, setSearchParams] = useState({
    name: '',
    class: '',
    id: undefined as number | undefined
  })

  const { data: spells, isLoading, error } = useSpells(searchParams)

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    // The search will trigger automatically when searchParams changes
  }

  const handleInputChange = (field: string, value: string | number | undefined) => {
    setSearchParams(prev => ({
      ...prev,
      [field]: value
    }))
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-8 text-foreground">Spell Search</h1>
      
      {/* Search Form */}
      <form onSubmit={handleSearch} className="mb-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label htmlFor="name" className="block text-sm font-medium mb-2 text-foreground">
              Spell Name
            </label>
            <Input
              type="text"
              id="name"
              value={searchParams.name}
              onChange={(e) => handleInputChange('name', e.target.value)}
              placeholder="Search by spell name..."
            />
          </div>
          
          <div>
            <label htmlFor="class" className="block text-sm font-medium mb-2 text-foreground">
              Spell Class
            </label>
            <Input
              type="text"
              id="class"
              value={searchParams.class}
              onChange={(e) => handleInputChange('class', e.target.value)}
              placeholder="Search by spell class..."
            />
          </div>
          
          <div>
            <label htmlFor="id" className="block text-sm font-medium mb-2 text-foreground">
              Spell ID
            </label>
            <Input
              type="number"
              id="id"
              value={searchParams.id || ''}
              onChange={(e) => handleInputChange('id', e.target.value ? parseInt(e.target.value) : undefined)}
              placeholder="Search by spell ID..."
            />
          </div>
        </div>
        
        <Button
          type="submit"
          className="mt-4"
        >
          Search
        </Button>
      </form>

      {/* Results */}
      <div className="space-y-4">
        {isLoading && (
          <div className="text-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
            <p className="mt-2 text-muted-foreground">Loading spells...</p>
          </div>
        )}

        {error && (
          <div className="bg-destructive/10 border border-destructive/20 rounded-md p-4">
            <p className="text-destructive">Error loading spells: {error.message}</p>
          </div>
        )}

        {spells && spells.length > 0 && (
          <div>
            <h2 className="text-xl font-semibold mb-4 text-foreground">Results ({spells.length})</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {spells.map((spell: Spell) => (
                <div key={spell.id} className="bg-card border border-border rounded-lg p-4 shadow-sm hover:shadow-md transition-shadow">
                  <h3 className="font-semibold text-lg mb-2 text-foreground">{spell.name}</h3>
                  <div className="text-sm text-muted-foreground space-y-1">
                    <p><span className="font-medium">ID:</span> {spell.id}</p>
                    <p><span className="font-medium">Class:</span> {spell.class}</p>
                    <p><span className="font-medium">Level:</span> {spell.level}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {spells && spells.length === 0 && !isLoading && (
          <div className="text-center py-8">
            <p className="text-muted-foreground">No spells found matching your search criteria.</p>
          </div>
        )}
      </div>
    </div>
  )
}

export default SpellSearchPage 
import React from 'react'
import { Link } from 'react-router-dom'
import Card from '@/components/common/Card';

const Home: React.FC = () => {
  const searchCategories = [
    {
      title: 'Items',
      description: 'Search for weapons, armor, equipment, and consumables',
      icon: '⚔️',
      path: '/items',
      color: 'bg-primary hover:bg-primary/80'
    },
    {
      title: 'Spells',
      description: 'Find spells by class, level, and effects',
      icon: '✨',
      path: '/spells',
      color: 'bg-secondary hover:bg-secondary/80'
    },
    {
      title: 'NPCs',
      description: 'Search for NPCs, merchants, and quest givers',
      icon: '👤',
      path: '/npcs',
      color: 'bg-success hover:bg-success/80'
    },
    {
      title: 'Zones',
      description: 'Explore zones and their expansions',
      icon: '🗺️',
      path: '/zones',
      color: 'bg-warning hover:bg-warning/80'
    },
    {
      title: 'Quests',
      description: 'Find quests and their requirements',
      icon: '📜',
      path: '/quests',
      color: 'bg-destructive hover:bg-destructive/80'
    },
    {
      title: 'Expansions',
      description: 'Browse content by expansion',
      icon: '📦',
      path: '/expansions',
      color: 'bg-accent hover:bg-accent/80'
    }
  ]

  return (
    <div className="container mx-auto px-4 py-8">
      
      {/* Hero Section */}
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold mb-4 text-foreground">EQDB - EverQuest Database</h1>
        <p className="text-xl text-muted-foreground mb-8">
          Search and explore EverQuest game data including items, spells, NPCs, zones, and more.
        </p>
        <Card className="p-6 max-w-2xl mx-auto">
          <h2 className="text-lg font-semibold mb-2 text-foreground">About EQDB</h2>
          <p className="text-muted-foreground">
            EQDB is a comprehensive database for EverQuest players. Search for items, spells, NPCs, 
            zones, and quests to help with your adventures in Norrath. All data is sourced from 
            the official EverQuest game files and organized for easy searching.
          </p>
        </Card>
      </div>

      {/* Search Categories */}
      <div className="mb-12">
        <h2 className="text-2xl font-bold mb-6 text-center text-foreground">Search Categories</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {searchCategories.map((category) => (
            <Link
              key={category.path}
              to={category.path}
              className={`shadow-lg hover:shadow-xl transition-all duration-200 transform hover:scale-105`}
            >
              <Card className={`${category.color} text-primary-foreground p-6 flex flex-col items-center`}>
                <div className="text-4xl mb-4">{category.icon}</div>
                <h3 className="text-xl font-semibold mb-2">{category.title}</h3>
                <p className="text-primary-foreground/80">{category.description}</p>
              </Card>
            </Link>
          ))}
        </div>
      </div>

      {/* Quick Stats */}
      <div className="bg-card rounded-lg p-6 mb-8 border border-border">
        <h2 className="text-2xl font-bold mb-4 text-center text-foreground">Database Overview</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
          <div className="bg-background rounded-lg p-4 shadow-sm border border-border">
            <div className="text-2xl font-bold text-primary">10,000+</div>
            <div className="text-sm text-muted-foreground">Items</div>
          </div>
          <div className="bg-background rounded-lg p-4 shadow-sm border border-border">
            <div className="text-2xl font-bold text-secondary">5,000+</div>
            <div className="text-sm text-muted-foreground">Spells</div>
          </div>
          <div className="bg-background rounded-lg p-4 shadow-sm border border-border">
            <div className="text-2xl font-bold text-success">2,000+</div>
            <div className="text-sm text-muted-foreground">NPCs</div>
          </div>
          <div className="bg-background rounded-lg p-4 shadow-sm border border-border">
            <div className="text-2xl font-bold text-warning">500+</div>
            <div className="text-sm text-muted-foreground">Zones</div>
          </div>
        </div>
      </div>

      {/* Features */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <Card className="p-6">
          <h3 className="text-xl font-semibold mb-4 text-foreground">🔍 Advanced Search</h3>
          <p className="text-muted-foreground mb-4">
            Search by name, ID, type, class, and more with our comprehensive search filters.
          </p>
          <ul className="text-sm text-muted-foreground space-y-1">
            <li>• Partial name matching</li>
            <li>• Multiple filter options</li>
            <li>• Real-time search results</li>
          </ul>
        </Card>

        <Card className="p-6">
          <h3 className="text-xl font-semibold mb-4 text-foreground">📊 Detailed Information</h3>
          <p className="text-muted-foreground mb-4">
            Get comprehensive details about items, spells, and game content.
          </p>
          <ul className="text-sm text-muted-foreground space-y-1">
            <li>• Complete item statistics</li>
            <li>• Spell effects and requirements</li>
            <li>• NPC locations and drops</li>
          </ul>
        </Card>
      </div>
    </div>
  )
}

export default Home 
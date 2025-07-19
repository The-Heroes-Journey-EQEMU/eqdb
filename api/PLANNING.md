# EQDB API Development Plan

## Core API Requirements
The following endpoints must be maintained exactly as defined, regardless of internal implementation changes:
```
/api/v1/items?id=            Search items by item id
/api/v1/items?name=          Search items by partial name (50 results maximum)
/api/v1/spells?id=          Search spells by spell id
/api/v1/spells?name=        Search spells by partial name (50 results maximum)
/api/v1/npcs?id=            Search NPCs by NPC id
/api/v1/npcs?name=          Search NPCs by partial name (50 results maximum)
/api/v1/npcs?name=&zone=    Search NPCs by partial name and zone shortname (50 results maximum)
/api/v1/trade?id=          Search Tradeskills by tradeskill id
/api/v1/trade?name=        Search Tradeskills by partial tradeskill name (50 results maximum)
/api/v1/loot?id=            Search Loot Drops by loottable id
/api/v1/loot?npc=           Search Loot Drops by npc id
```

## Database Architecture
- Remote Database (gamedb) - Source of Truth
  - MySQL database containing all game data
  - Read-only access for API
  - No schema modifications allowed

- Local Database (localdb) - Extensions
  - SQLite database for user-specific data
  - Flexible schema for new features
  - User collections, notes, and preferences

## Implementation Phases

### Phase 1: Core API Maintenance
- [ ] Verify all existing endpoints
- [ ] Document with Flask-RESTX
- [ ] Implement proper error handling
- [ ] Add request validation
- [ ] Set up logging

### Phase 2: Database Integration
- [ ] Set up SQLAlchemy models
- [ ] Create migration scripts
- [ ] Implement connection pooling
- [ ] Add caching layer
- [ ] Configure database connections

### Phase 3: Extension Features
- [ ] User collections
- [ ] Custom notes
- [ ] Favorites
- [ ] Search history
- [ ] Quest tracking

## Code Organization
```
api/
├── __init__.py
├── models/
│   ├── __init__.py
│   ├── game_models.py      # gamedb models
│   └── user_models.py      # localdb models
├── routes/
│   ├── __init__.py
│   ├── core/              # Original API endpoints
│   │   ├── items.py
│   │   ├── spells.py
│   │   ├── npcs.py
│   │   ├── trade.py
│   │   └── loot.py
│   └── extensions/        # New functionality
│       ├── user_items.py
│       ├── user_spells.py
│       └── user_quests.py
├── services/
│   ├── __init__.py
│   ├── game_service.py    # gamedb operations
│   └── user_service.py    # localdb operations
└── utils/
    ├── __init__.py
    ├── db.py
    └── cache.py
```

## Implementation Guidelines

### Core API Rules
- Never modify existing endpoint paths
- Maintain exact parameter names
- Keep response formats consistent
- Preserve 50-result limit for searches
- Maintain error response formats

### Database Rules
- gamedb is source of truth for game data
- localdb for user-specific data only
- No modifications to gamedb schema
- Flexible schema for localdb

### Extension Rules
- New features must not interfere with core API
- Clear separation between core and extension code
- Proper error handling and validation
- User authentication for extensions

### Code Modification Rules
- All new code must be contained within the `api/` directory
- No modifications to code outside `api/` without explicit permission
- If changes outside `api/` are required:
  1. Document the required changes
  2. Provide clear reasoning for why the changes are necessary
  3. Submit a formal request for permission
  4. Wait for approval before proceeding
  5. Document all approved changes in the project documentation
- This rule applies to:
  - Database schema changes
  - Configuration file modifications
  - Dependencies updates
  - Any other changes outside the `api/` directory

## Testing Strategy
- Unit tests for all endpoints
- Integration tests for database operations
- Compatibility tests for core API
- Performance testing for caching
- Load testing for concurrent requests

## Documentation Requirements
- API endpoint documentation
- Database schema documentation
- Code modification requests
- Testing results
- Performance metrics

## Progress Tracking
- [ ] Phase 1: Core API Maintenance
- [ ] Phase 2: Database Integration
- [ ] Phase 3: Extension Features
- [ ] Testing
- [ ] Documentation
- [ ] Deployment

## Notes
- All changes must maintain backward compatibility
- Performance optimization should be a continuous process
- Security considerations must be addressed for all new features
- Regular backups of both databases are essential
- Monitoring and logging should be implemented for all operations

## Future Features and API Enhancements

### Advanced Search Capabilities
- [ ] Advanced item search
  - Multiple stat combinations
  - Level range filtering
  - Slot-based filtering
  - Class/race restrictions
  - Augment slot requirements
  - Effect type filtering

- [ ] Advanced spell search
  - Effect type filtering
  - Mana cost ranges
  - Cast time filtering
  - Class combinations
  - Level requirements
  - Duration/range filtering

- [ ] Advanced NPC search
  - Level range filtering
  - Zone-based clustering
  - Faction alignment
  - Loot table correlation
  - Spawn time patterns
  - Quest association

### Data Correlation Features
- [ ] Item Correlations
  - Quest requirements
  - Tradeskill components
  - Similar items
  - Upgrade paths
  - Drop locations
  - Vendor locations

- [ ] Quest System
  - Quest chains
  - Prerequisites
  - Rewards
  - Faction requirements
  - Level requirements
  - Zone requirements

- [ ] Tradeskill System
  - Recipe trees
  - Component sources
  - Skill requirements
  - Success rates
  - Product uses
  - Market value

### User Features
- [ ] Collections
  - Item wishlists
  - Spell collections
  - Quest tracking
  - Achievement tracking
  - Progress monitoring

- [ ] Customization
  - Personal notes
  - Custom tags
  - Favorite items/spells
  - Search history
  - Custom filters

### Integration Features
- [ ] Discord Bot Integration
  - Quick item lookups
  - Spell information
  - NPC locations
  - Quest information
  - Price checks
  - Drop rates

- [ ] AI Integration
  - Item correlation analysis
  - Quest chain optimization
  - NPC behavior patterns
  - Loot probability analysis
  - Market trend analysis
  - Player behavior insights

### API Endpoints for Future Features
```
# Advanced Search
GET /api/v1/items/search
  - stats: JSON array of stat requirements
  - level_range: min/max level
  - slots: array of slot types
  - classes: array of class IDs
  - races: array of race IDs
  - augments: array of augment types

GET /api/v1/spells/search
  - effect_type: array of effect types
  - mana_range: min/max mana cost
  - cast_time: max cast time
  - classes: array of class IDs
  - level_range: min/max level
  - duration: min/max duration

GET /api/v1/npcs/search
  - level_range: min/max level
  - zones: array of zone IDs
  - factions: array of faction IDs
  - loot_tables: array of loot table IDs
  - quest_ids: array of quest IDs

# Correlations
GET /api/v1/items/{id}/related
  - quests: array of quest IDs
  - tradeskills: array of recipe IDs
  - similar: array of similar item IDs
  - upgrades: array of upgrade paths
  - drops: array of drop locations
  - vendors: array of vendor locations

# User Features
GET /api/v1/user/collections
  - items: array of saved items
  - spells: array of saved spells
  - quests: array of tracked quests
  - achievements: array of tracked achievements

POST /api/v1/user/collections
  - type: collection type
  - items: array of item IDs
  - notes: custom notes
  - tags: custom tags
```

### Implementation Priority
1. Core API maintenance and stability
2. Basic search enhancements
3. User collection features
4. Advanced correlation features
5. Integration features
6. AI analysis features

### Technical Considerations
- Caching strategy for frequently accessed data
- Rate limiting for API endpoints
- Pagination for large result sets
- Authentication for user features
- Data validation and sanitization
- Performance optimization
- Monitoring and analytics

## Notes
- All changes must maintain backward compatibility
- Performance optimization should be a continuous process
- Security considerations must be addressed for all new features
- Regular backups of both databases are essential
- Monitoring and logging should be implemented for all operations 
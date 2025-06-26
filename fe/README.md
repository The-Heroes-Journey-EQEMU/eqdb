# EQDB Frontend - TypeScript React Rebuild

## Overview
This is a modern TypeScript React frontend for the EQDB (EverQuest Database) application, designed to replace the current Flask-based templates with a single-page application (SPA) that consumes the existing REST API.

## Project Structure

```
fe/
├── public/
│   ├── index.html
│   ├── favicon.ico
│   └── assets/
│       ├── icons/
│       └── images/
├── src/
│   ├── components/
│   │   ├── common/
│   │   │   ├── Header.tsx
│   │   │   ├── Footer.tsx
│   │   │   ├── Navigation.tsx
│   │   │   ├── SearchBar.tsx
│   │   │   ├── LoadingSpinner.tsx
│   │   │   ├── ErrorBoundary.tsx
│   │   │   └── Tooltip.tsx
│   │   ├── items/
│   │   │   ├── ItemSearch.tsx
│   │   │   ├── ItemDetail.tsx
│   │   │   ├── ItemList.tsx
│   │   │   ├── ItemCard.tsx
│   │   │   ├── WeaponSearch.tsx
│   │   │   └── ArmorSearch.tsx
│   │   ├── spells/
│   │   │   ├── SpellSearch.tsx
│   │   │   ├── SpellDetail.tsx
│   │   │   ├── SpellList.tsx
│   │   │   └── SpellCard.tsx
│   │   ├── npcs/
│   │   │   ├── NPCSearch.tsx
│   │   │   ├── NPCDetail.tsx
│   │   │   └── NPCList.tsx
│   │   ├── zones/
│   │   │   ├── ZoneListing.tsx
│   │   │   ├── ZoneDetail.tsx
│   │   │   └── ZoneCard.tsx
│   │   ├── tradeskills/
│   │   │   ├── TradeskillSearch.tsx
│   │   │   ├── TradeskillDetail.tsx
│   │   │   ├── RecipeList.tsx
│   │   │   └── RecipeCard.tsx
│   │   ├── quests/
│   │   │   ├── QuestSearch.tsx
│   │   │   ├── QuestDetail.tsx
│   │   │   └── QuestList.tsx
│   │   ├── factions/
│   │   │   ├── FactionSearch.tsx
│   │   │   └── FactionDetail.tsx
│   │   ├── tools/
│   │   │   ├── IdentifyGame.tsx
│   │   │   ├── WaypointListing.tsx
│   │   │   ├── PetListing.tsx
│   │   │   └── SpellListing.tsx
│   │   └── user/
│   │       ├── UserHome.tsx
│   │       ├── GearList.tsx
│   │       ├── RestrictSets.tsx
│   │       └── WeightSets.tsx
│   ├── pages/
│   │   ├── Home.tsx
│   │   ├── ItemSearchPage.tsx
│   │   ├── SpellSearchPage.tsx
│   │   ├── NPCSearchPage.tsx
│   │   ├── ZoneListingPage.tsx
│   │   ├── TradeskillSearchPage.tsx
│   │   ├── QuestSearchPage.tsx
│   │   ├── FactionSearchPage.tsx
│   │   ├── ToolsPage.tsx
│   │   ├── UserPage.tsx
│   │   ├── AboutPage.tsx
│   │   └── ChangelogPage.tsx
│   ├── services/
│   │   ├── api.ts
│   │   ├── itemService.ts
│   │   ├── spellService.ts
│   │   ├── npcService.ts
│   │   ├── zoneService.ts
│   │   ├── tradeskillService.ts
│   │   ├── questService.ts
│   │   ├── factionService.ts
│   │   └── userService.ts
│   ├── types/
│   │   ├── item.ts
│   │   ├── spell.ts
│   │   ├── npc.ts
│   │   ├── zone.ts
│   │   ├── tradeskill.ts
│   │   ├── quest.ts
│   │   ├── faction.ts
│   │   └── user.ts
│   ├── hooks/
│   │   ├── useApi.ts
│   │   ├── useSearch.ts
│   │   ├── usePagination.ts
│   │   └── useLocalStorage.ts
│   ├── utils/
│   │   ├── constants.ts
│   │   ├── formatters.ts
│   │   ├── validators.ts
│   │   └── helpers.ts
│   ├── styles/
│   │   ├── base.css
│   │   ├── globals.css
│   │   └── THEMING.md
│   ├── App.tsx
│   ├── index.tsx
│   └── routes.tsx
├── package.json
├── tsconfig.json
├── vite.config.ts
├── tailwind.config.js
└── README.md
```

## Technology Stack

### Core Technologies
- **React 18** - Modern React with hooks and concurrent features
- **TypeScript** - Type safety and better developer experience
- **Vite** - Fast build tool and development server
- **React Router 6** - Client-side routing
- **Tailwind CSS** - Utility-first CSS framework

### State Management
- **React Query (TanStack Query)** - Server state management and caching
- **Zustand** - Lightweight client state management

### UI Components
- **Headless UI** - Unstyled, accessible UI components
- **Heroicons** - Beautiful SVG icons
- **React Hook Form** - Performant forms with validation
- **Zod** - TypeScript-first schema validation

### Development Tools
- **ESLint** - Code linting
- **Prettier** - Code formatting
- **Husky** - Git hooks
- **Vitest** - Unit testing
- **React Testing Library** - Component testing

## Key Features to Implement

### 1. Core Search Functionality
- **Global Search** - Search across all content types
- **Advanced Filters** - Type-specific filtering options
- **Real-time Search** - Debounced search with instant results
- **Search History** - Local storage for recent searches

### 2. Item System
- **Item Search** - By name, ID, type, stats
- **Item Details** - Comprehensive item information display
- **Item Comparison** - Side-by-side item comparison
- **Item Tooltips** - Hover tooltips with item stats
- **Advanced Gear Search** - Weapon and armor specific searches

### 3. Spell System
- **Spell Search** - By name, class, level, effects
- **Spell Details** - Full spell information with effects
- **Class Spell Lists** - Organized by class and level
- **Spell Tooltips** - Hover tooltips with spell details

### 4. NPC & Zone System
- **NPC Search** - By name, zone, level, faction
- **NPC Details** - Stats, drops, location, quests
- **Zone Listing** - Browse zones by expansion
- **Zone Details** - Zone information, NPCs, items

### 5. Tradeskill System
- **Tradeskill Search** - By name, skill type
- **Recipe Details** - Components, requirements, results
- **Recipe Lists** - Organized by tradeskill type

### 6. Quest System
- **Quest Search** - By name, NPC, item, zone
- **Quest Details** - Requirements, rewards, steps
- **Quest Chains** - Related quest sequences

### 7. User Features
- **User Authentication** - Discord OAuth integration
- **Gear Lists** - Save and manage equipment sets
- **Restrict Sets** - Item restriction configurations
- **Weight Sets** - Item weighting for optimization

### 8. Tools & Games
- **Identify Game** - Item identification minigame
- **Waypoint Listing** - Zone waypoints and locations
- **Pet Listing** - Available pets and their stats

## API Integration

### API-Driven Development
This frontend is designed to be **API-driven** and **Swagger-first**. All data models, types, and API calls should be derived from or validated against the Swagger specification.

#### Swagger Integration
- **API Documentation**: Available at `http://localhost:5001/api/v1/` (Swagger UI)
- **API Specification**: JSON schema at `http://localhost:5001/swagger.json`
- **Type Safety**: All frontend types should match the exact schema defined in Swagger
- **Validation**: Runtime validation ensures API responses match expected schemas

#### Development Principles
1. **Schema-Driven**: Data models are derived from API specification
2. **Contract-First**: API contracts (Swagger) define frontend-backend interface
3. **Type Generation**: Consider using `openapi-typescript` for automatic type generation
4. **Versioning**: Handle API versioning gracefully with proper type definitions

#### Implementation Guidelines
- Each API endpoint should have a corresponding service function
- All API responses should be validated against Swagger schemas
- Error handling should cover all possible API error responses
- Testing should verify type compatibility with actual API responses

### Base Configuration
```typescript
// services/api.ts
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api/v1';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});
```

### Service Structure
Each service will handle specific API endpoints:
- `itemService.ts` - `/items` endpoints
- `spellService.ts` - `/spells` endpoints
- `npcService.ts` - `/npcs` endpoints
- etc.

### Error Handling
- Global error boundary for React errors
- API error handling with user-friendly messages
- Retry logic for failed requests
- Offline detection and handling

## UI/UX Design

### Design System
- **Dark Theme** - Consistent with current EQDB design
- **Responsive Design** - Mobile-first approach
- **Accessibility** - WCAG 2.1 AA compliance
- **Performance** - Optimized loading and rendering

### Component Library
- Reusable components with consistent styling
- Loading states and skeleton screens
- Toast notifications for user feedback
- Modal dialogs for detailed views

### Navigation
- **Breadcrumb Navigation** - Clear page hierarchy
- **Search Bar** - Prominent global search
- **Quick Links** - Frequently accessed features
- **Mobile Menu** - Collapsible navigation

## CSS Theming System

The frontend implements a comprehensive CSS theming system using CSS custom properties (variables) for consistent styling and easy theme switching.

### Architecture

- **`base.css`** - Contains all CSS custom properties and theme definitions
- **`globals.css`** - Imports base.css and provides component-specific styles using the variables
- **`THEMING.md`** - Comprehensive documentation of the theming system

### Key Features

- **Semantic Color System** - Colors are named by purpose (primary, success, error) rather than appearance
- **Dark/Light Theme Support** - Automatic theme switching with `.dark` class
- **Component Consistency** - All components use the same design tokens
- **Easy Customization** - Change themes by modifying CSS variables in `base.css`

### Theme Variables

The system includes variables for:
- **Colors** - Primary, secondary, semantic (success, warning, error), backgrounds, text
- **Typography** - Font families, sizes, weights, line heights
- **Spacing** - Consistent spacing scale
- **Border Radius** - Rounded corner values
- **Shadows** - Elevation and depth
- **Transitions** - Animation timing
- **Z-Index** - Layering system

### Usage Examples

```css
/* Using CSS variables */
.my-component {
  background-color: var(--background);
  color: var(--foreground);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  padding: var(--spacing-md);
  font-family: var(--font-sans);
  box-shadow: var(--shadow-sm);
}
```

```tsx
// In React components
<div
  style={{
    backgroundColor: 'var(--background)',
    color: 'var(--foreground)',
    padding: 'var(--spacing-md)'
  }}
>
  Content
</div>
```

### Theme Switching

```javascript
// Enable dark theme
document.documentElement.classList.add('dark');

// Disable dark theme
document.documentElement.classList.remove('dark');
```

For detailed documentation, see [`src/styles/THEMING.md`](src/styles/THEMING.md).

## Development Phases

### Phase 1: Foundation (Week 1-2)
- [ ] Project setup and configuration
- [ ] Basic routing and layout
- [ ] API service layer
- [ ] Core components (Header, Footer, Navigation)
- [ ] Global search functionality

### Phase 2: Core Features (Week 3-4)
- [ ] Item search and detail pages
- [ ] Spell search and detail pages
- [ ] NPC search and detail pages
- [ ] Zone listing and detail pages
- [ ] Basic styling and responsive design

### Phase 3: Advanced Features (Week 5-6)
- [ ] Tradeskill system
- [ ] Quest system
- [ ] Faction system
- [ ] Advanced search filters
- [ ] Tooltips and enhanced UI

### Phase 4: User Features (Week 7-8)
- [ ] User authentication
- [ ] Gear lists and user data
- [ ] Tools and games
- [ ] Performance optimization
- [ ] Testing and bug fixes

### Phase 5: Polish & Deployment (Week 9-10)
- [ ] Final styling and animations
- [ ] Accessibility improvements
- [ ] Performance optimization
- [ ] Documentation
- [ ] Deployment configuration

## Getting Started

### Prerequisites
- Node.js 18+ and npm
- Access to the EQDB API (running on localhost:5000)

### Installation
```bash
cd fe
npm install
```

### Development
```bash
npm run dev
```

### Build
```bash
npm run build
```

### Testing
```bash
npm run test
```

## Configuration

### Environment Variables
```env
REACT_APP_API_URL=http://localhost:5000/api/v1
REACT_APP_DISCORD_CLIENT_ID=your_discord_client_id
REACT_APP_SITE_VERSION=2.0.0
```

### API Endpoints
The frontend will consume the existing REST API endpoints:
- `/api/v1/items` - Item search and details
- `/api/v1/spells` - Spell search and details
- `/api/v1/npcs` - NPC search and details
- `/api/v1/zones` - Zone listing and details
- `/api/v1/tradeskills` - Tradeskill search and details
- `/api/v1/quests` - Quest search and details
- `/api/v1/expansions` - Expansion data

## Migration Strategy

### Phase 1: Parallel Development
- Keep existing Flask frontend running
- Develop new React frontend alongside
- Share API between both frontends

### Phase 2: Feature Parity
- Implement all existing features in React
- Ensure same functionality and data display
- Maintain visual consistency

### Phase 3: Enhancement
- Add new features and improvements
- Better mobile experience
- Enhanced search and filtering
- Modern UI/UX patterns

### Phase 4: Switchover
- Deploy React frontend to production
- Redirect traffic from Flask to React
- Monitor performance and user feedback

## Benefits of React Rebuild

### Performance
- Faster page loads with SPA architecture
- Better caching and state management
- Optimized bundle splitting

### User Experience
- Smoother navigation without page reloads
- Real-time search and filtering
- Better mobile responsiveness
- Modern UI components

### Developer Experience
- TypeScript for better code quality
- Component-based architecture
- Better testing capabilities
- Modern development tools

### Maintainability
- Separated concerns (frontend/backend)
- Easier to add new features
- Better code organization
- Modern development practices

## Notes
- This rebuild maintains full compatibility with the existing API
- All current functionality will be preserved
- The design will remain consistent with the current EQDB theme
- The rebuild focuses on modern web standards and user experience 
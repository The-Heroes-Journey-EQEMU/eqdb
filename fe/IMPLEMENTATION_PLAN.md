# EQDB Frontend Implementation Plan

## API-Driven Development Strategy

### Swagger/OpenAPI Integration
- **Single Source of Truth**: All frontend types and API calls should be generated from or validated against the Swagger specification at `http://localhost:5001/swagger.json`
- **Type Safety**: Ensure all API interfaces match the exact schema defined in the Swagger docs
- **Automatic Updates**: When API changes, frontend types should be updated accordingly
- **Validation**: Use runtime validation to ensure API responses match expected schemas

### API-First Development Principles
1. **Schema-Driven**: All data models should be derived from the API specification
2. **Contract-First**: API contracts (Swagger) define the interface between frontend and backend
3. **Versioning**: Handle API versioning gracefully with proper type definitions
4. **Documentation**: Keep frontend documentation in sync with API documentation

### Implementation Guidelines
- **Service Layer**: Each API endpoint should have a corresponding service function
- **Type Generation**: Consider using tools like `openapi-typescript` to generate types from Swagger
- **Error Handling**: Handle all possible API error responses as defined in Swagger
- **Testing**: Test against actual API responses to ensure type compatibility

## Phase 1: Foundation Setup (Week 1-2)

### Week 1: Project Setup
- [x] Create project structure and configuration files
- [x] Set up TypeScript, Webpack, and Tailwind CSS
- [x] Configure ESLint and Prettier
- [x] Create type definitions for all API entities
- [x] Set up React Router and basic routing
- [x] Create base layout components (Header, Footer, Navigation)
- [x] Set up API service layer with axios
- [x] Configure React Query for state management
- [x] **NEW**: Integrate Swagger specification for type generation
- [x] **NEW**: Set up API response validation
- [x] **COMPLETED**: Create comprehensive service files (itemService, spellService, npcService, zoneService, questService, expansionService)
- [x] **COMPLETED**: Implement useApi hooks for all service types
- [x] **COMPLETED**: Create basic search pages (ItemSearchPage, SpellSearchPage)
- [x] **COMPLETED**: Set up webpack configuration with environment variables
- [x] **COMPLETED**: Fix TypeScript errors and type conflicts
- [x] **COMPLETED**: Create modern Home page with navigation cards
- [x] **COMPLETED**: Document API-driven development approach

### Week 2: Core Infrastructure
- [x] Create global state management with Zustand
- [x] Set up error boundaries and loading states
- [x] Create reusable UI components (Button, Input, Card, etc.)
- [ ] Implement global search functionality
- [x] **COMPLETED**: Implement comprehensive Zustand store with user preferences, UI state, and search state
- [x] **COMPLETED**: Create ErrorBoundary component with development error details
- [x] **COMPLETED**: Create LoadingSpinner, LoadingOverlay, and Skeleton components
- [x] **COMPLETED**: Create reusable Button, Input, Card, and Notification components
- [x] **COMPLETED**: Enhance SearchBar with global search, recent searches, and type filtering
- [x] **COMPLETED**: Update Header with responsive navigation and store integration
- [x] **COMPLETED**: Integrate all components into App.tsx with proper error handling
- [x] **COMPLETED**: Update ItemSearchPage with new UI components and store integration
- [ ] **PARTIAL**: Create responsive navigation system (basic mobile menu implemented, needs full responsive design)

## Phase 2: Core Required Features 

### Week 3a: User System
- [x] **COMPLETED**: Implement User Login - JWT-based authentication with email/password
- [x] **COMPLETED**: Implement User Object - User profile with preferences and admin status
- [x] **COMPLETED**: Implement Frontend Authentication - Login form, protected routes, user context
- [x] **COMPLETED**: Implement User Profile - Settings, preferences, password change
- [x] **COMPLETED**: Implement Admin Panel - User management and system administration
- [x] **COMPLETED**: Add Weight Sets and Characters menu items to navigation (protected routes)
- [x] **COMPLETED**: Implement Weight Sets API - Full CRUD operations with authentication
- [ ] **IN PROGRESS**: Implement Weight Sets Frontend - React components for management and selection
- [ ] **NEXT**: Integrate Weight Sets with Item Search - Apply saved weight sets to search forms
- [ ] **NEXT**: Implement Characters - 3 Class, level, Character Name, and Character Set (all manually set), inventory blob (very large string)

### Weight Sets Integration Status

**✅ API Implementation (COMPLETED):**
The weight sets system is fully implemented in the API with the following capabilities:

**Weight Sets CRUD API:**
- `GET /user/weight-sets` - Get all user's weight sets
- `GET /user/weight-sets/{id}` - Get specific weight set
- `POST /user/weight-sets` - Create new weight set
- `PUT /user/weight-sets/{id}` - Update weight set
- `DELETE /user/weight-sets/{id}` - Delete weight set

**Item Search Integration:**
- `/items/search` endpoint accepts `stat_weights` parameter as JSON array
- Format: `[{"stat": "hp", "weight": 1.5}, {"stat": "damage", "weight": 2.0}]`
- API calculates weighted scores and sorts results by score
- Returns `weight_score` in results when `show_weight_detail=true`
- Supports 100+ stat types including heroic stats, resists, and weapon efficiency

**Advanced Features:**
- Heroic resist calculation (automatically includes base resists)
- Weapon efficiency (damage/delay) calculations  
- Bane damage weighting (body vs race damage types)
- Complex stat filtering combined with weighting
- Zero-weight item filtering options

**🔧 Frontend Components Needed:**

1. **Weight Set Management Components:**
   - `WeightSetCard` - Display individual weight set with stats
   - `WeightSetForm` - Create/edit weight sets with dynamic stat selection
   - `WeightSetList` - List all user's weight sets with actions
   - `WeightSetSelector` - Dropdown to select weight sets in search forms

2. **Search Form Integration:**
   - Update `ItemSearchForm` with weight set selection
   - Update `WeaponSearchForm` with weight set integration
   - Add weight set application to existing search forms
   - Display weight scores in search results

3. **Stat Weight Components:**
   - `StatWeightTable` - Dynamic table for adding/editing stat weights
   - `StatSelector` - Dropdown with categorized stat options
   - `WeightScoreDisplay` - Show calculated weight scores in results

**TypeScript Type Definitions (Already Available):**

```typescript
// Available in fe/src/types/user.ts
export interface WeightSet {
  id: number;
  name: string;
  description: string;
  weights: Array<{
    stat: string;
    value: number;
  }>;
  created_at: string;
  updated_at: string;
}

export interface CreateWeightSetRequest {
  name: string;
  description?: string;
  weights: Array<{
    stat: string;
    value: number;
  }>;
}

export interface UpdateWeightSetRequest {
  name?: string;
  description?: string;
  weights?: Array<{
    stat: string;
    value: number;
  }>;
}
```

**Service Layer Integration (Already Available):**

```typescript
// Available in fe/src/services/userService.ts
export const userService = {
  getWeightSets: async () => {
    const response = await api.get<{ weight_sets: WeightSet[] }>('/user/weight-sets');
    return response.weight_sets;
  },
  
  createWeightSet: async (data: CreateWeightSetRequest) => {
    const response = await api.post<WeightSet>('/user/weight-sets', data);
    return response;
  },
  
  updateWeightSet: async (id: number, data: UpdateWeightSetRequest) => {
    const response = await api.put<WeightSet>(`/user/weight-sets/${id}`, data);
    return response;
  },
  
  deleteWeightSet: async (id: number) => {
    const response = await api.delete(`/user/weight-sets/${id}`);
    return response;
  }
};
```

**React Hooks Needed:**

```typescript
// fe/src/hooks/useWeightSets.ts (to be created)
export const useWeightSets = () => {
  return useQuery({
    queryKey: ['user', 'weight-sets'],
    queryFn: () => userService.getWeightSets(),
    staleTime: 5 * 60 * 1000 // 5 minutes
  });
};

export const useCreateWeightSet = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: userService.createWeightSet,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['user', 'weight-sets'] });
    }
  });
};
```

**Integration with Item Search:**

When integrating weight sets with item search forms, the frontend should:

1. **Weight Set Selection:**
   - Add dropdown to select saved weight sets in search forms
   - Allow users to apply weight set to current search
   - Show preview of weight set stats before applying

2. **Search Parameter Construction:**
   - Convert selected weight set to `stat_weights` JSON array
   - Include `show_weight_detail=true` when weights applied
   - Pass to itemService.searchAdvanced() or weaponService.searchWeapons()

3. **Results Display:**
   - Show weight scores when weights applied
   - Sort results by weight score (API handles this)
   - Highlight items with highest weight scores

**Example Search Integration:**

```typescript
// In search form component
const applyWeightSet = (weightSet: WeightSet) => {
  const searchParams = {
    ...currentSearchParams,
    stat_weights: weightSet.weights,
    show_weight_detail: true
  };
  onSearch(searchParams);
};

// In search results component
{showWeightDetail && (
  <div className="weight-score">
    Score: {item.weight_score?.toFixed(2)}
  </div>
)}
```

### Week 3b: Item System

#### Implementation Guide: Item Search & Detail System
- [ ] Create ItemSearch component with filters using Card wrapper
- [ ] Implement ItemDetail page with comprehensive display using Card layout
- [ ] Create ItemList and ItemCard components using existing Card system
- [ ] Add item tooltips and hover effects using Card hover variants
- [ ] Implement item comparison functionality with Card grid layout
- [ ] Create advanced gear search (weapons/armor) with specialized Card layouts

**Overview:**
The item system provides modular search capabilities across different contexts (armor, weapons, quest items, etc.) with comprehensive detail views. The implementation follows the API-first approach with TypeScript types generated from Swagger specifications.

**Card System & Wrapper Patterns:**
The project uses a consistent Card system with the following patterns:

1. **Card Variants:**
   - `default`: Standard card with border
   - `elevated`: Card with shadow for emphasis
   - `outlined`: Card with thicker border for grouping

2. **Card Structure:**
   - `Card`: Main container with rounded corners (24px outer, 16px inner)
   - `CardHeader`: Top section with border separator
   - `CardBody`: Main content area with padding
   - `CardFooter`: Bottom section with border separator

3. **Wrapper Patterns:**
   - Use `Card` for all content sections
   - Group related content with `CardHeader` + `CardBody`
   - Use `Card` with `hover` prop for interactive elements
   - Apply consistent spacing with `space-y-4` or `gap-4`

4. **Loading States:**
   - Use `SkeletonCard` for individual item loading
   - Use `SkeletonList` for multiple items
   - Apply skeleton patterns to match actual content structure

**API Endpoints Integration:**

1. **`/items`** - Lightweight search (basic fields only)
   - Use for: Quick searches, autocomplete, basic listings
   - Returns: `id`, `name`, `type` only
   - Best for: Performance-critical scenarios

2. **`/items/search`** - Advanced search with full filtering
   - Use for: Complex searches, gear optimization, detailed filtering
   - Returns: Enriched data with stats, effects, NPCs, expansions
   - Supports: All advanced filters (stats, weights, expansions, procs, etc.)

3. **`/items/details/<id>`** - Exhaustive single item data
   - Use for: Item detail pages, tooltips, comprehensive analysis
   - Returns: Raw data + enriched data + NPCs + spells + metadata
   - Best for: Deep item analysis and comparison

**TypeScript Type Definitions:**

```typescript
// Core item interfaces (update fe/src/types/item.ts)
export interface Item {
  id: number;
  name: string;
  type?: string;
  slot_names?: string;
  expansion_name?: string;
  is_quest_item?: boolean;
  itemtype_name?: string;
  serialized?: string;
  npcs?: NPCDrop[];
}

export interface ItemSearchParams {
  // Basic search
  id?: number;
  name?: string;
  item_type?: string;
  
  // Filter options
  tradeskill_only?: boolean;
  equippable_only?: boolean;
  exclude_glamours?: boolean;
  only_augments?: boolean;
  item_slot?: string;
  itemtype_name?: string;
  slot_names?: string;
  itemclass_name?: string;
  
  // Advanced filters
  stat_filters?: Array<{stat: string, value: number}>;
  stat_weights?: Array<{stat: string, weight: number}>;
  exclude_expansions?: string[];
  elemental_damage_type?: string;
  bane_damage_type?: string;
  proc?: 'None' | 'True';
  click?: 'None' | 'True';
  proc_level?: number;
  click_level?: number;
  skillmodtype?: string;
  expansion?: string;
  pet_search?: boolean;
  sympathetic?: string;
  
  // Display options
  show_full_detail?: boolean;
  show_weight_detail?: boolean;
  ignore_zero?: boolean;
  
  // Pagination
  page?: number;
  page_size?: number;
}

export interface ItemSearchResponse {
  results: Item[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}

export interface ItemDetail {
  item_id: number;
  raw_data: Record<string, any>; // All database fields
  enriched_data: {
    id: number;
    name: string;
    type: string;
    slot_names: string;
    expansion_name: string;
    is_quest_item: boolean;
    itemclass_name: string;
    human_readable: {
      type: string;
      slots: string;
      expansion: string;
      classes: string[];
      races: string[];
      deity: string;
      material: string;
      color: string;
      size: string;
    };
  };
  npcs: NPCDrop[];
  spells: Array<{
    type: string;
    spell_id: number;
    spell_data: any;
  }>;
  metadata: {
    last_updated: string;
    data_sources: string[];
    enriched_fields: string[];
  };
}

export interface NPCDrop {
  npc_id: number;
  npc_name: string;
  zone_name: string;
  level?: number;
  drop_rate?: number;
}
```

**Service Layer Implementation:**

```typescript
// fe/src/services/itemService.ts
import { apiClient } from './apiClient';
import { Item, ItemSearchParams, ItemSearchResponse, ItemDetail } from '../types/item';

export const itemService = {
  // Basic search (lightweight)
  searchBasic: async (params: Pick<ItemSearchParams, 'id' | 'name' | 'item_type'>): Promise<Item[]> => {
    const response = await apiClient.get('/items', { params });
    return response.data.results || response.data;
  },

  // Advanced search (full filtering)
  searchAdvanced: async (params: ItemSearchParams): Promise<ItemSearchResponse> => {
    const response = await apiClient.get('/items/search', { params });
    return response.data;
  },

  // Get exhaustive item details
  getDetails: async (itemId: number): Promise<ItemDetail> => {
    const response = await apiClient.get(`/items/details/${itemId}`);
    return response.data;
  },

  // Get item types for dropdowns
  getTypes: async (): Promise<Record<string, string>> => {
    const response = await apiClient.get('/items/types');
    return response.data;
  },

  // Get item slots for dropdowns
  getSlots: async (): Promise<Record<string, string>> => {
    const response = await apiClient.get('/items/slots');
    return response.data;
  }
};
```

**Development Checklist & Best Practices:**

1. **Card System Implementation:**
   - [ ] Always wrap content sections with `Card` component
   - [ ] Use `CardHeader` + `CardBody` for structured layouts
   - [ ] Apply `hover` prop to interactive cards
   - [ ] Use `variant="outlined"` for grouped content
   - [ ] Use `variant="elevated"` for emphasis

2. **Loading States:**
   - [ ] Use `SkeletonCard` for individual item loading
   - [ ] Use `SkeletonList` for multiple items
   - [ ] Match skeleton structure to actual content
   - [ ] Show loading spinners for form submissions

3. **Error Handling:**
   - [ ] Use `Card variant="outlined"` for error states
   - [ ] Include helpful error messages
   - [ ] Provide recovery actions (retry, back navigation)
   - [ ] Use consistent error icons and styling

4. **Responsive Design:**
   - [ ] Use `grid-cols-1 md:grid-cols-2 lg:grid-cols-3` for card grids
   - [ ] Test mobile layouts with proper spacing
   - [ ] Ensure touch targets are accessible
   - [ ] Use responsive text sizing

5. **Accessibility:**
   - [ ] Include proper ARIA labels
   - [ ] Ensure keyboard navigation works
   - [ ] Use semantic HTML structure
   - [ ] Provide alt text for images

6. **Performance:**
   - [ ] Implement proper React Query caching
   - [ ] Use pagination for large result sets
   - [ ] Lazy load images with error fallbacks
   - [ ] Debounce search inputs

**Next Steps for Specialized Search Forms:**

1. **Weapon Search Form:**
   - [ ] Create `WeaponSearchForm` component
   - [ ] Add weapon-specific filters (damage, delay, proc type)
   - [ ] Use Card system for filter grouping
   - [ ] Implement weapon comparison grid

2. **Armor Search Form:**
   - [ ] Create `ArmorSearchForm` component
   - [ ] Add armor-specific filters (AC, stats, slots)
   - [ ] Use Card system for stat requirements
   - [ ] Implement armor set grouping

3. **Quest Item Search:**
   - [ ] Create `QuestItemSearchForm` component
   - [ ] Add quest-specific filters (quest name, zone)
   - [ ] Use Card system for quest information
   - [ ] Link to quest details

**Weapon Search Implementation (Comprehensive):**

Based on the existing `weapon_search.html` template and API analysis, the weapon search system is highly complex with dynamic stat filtering and weighting. Here's the complete implementation plan:

**1. Enhanced TypeScript Types for Weapon Search:**

```typescript
// fe/src/types/weaponSearch.ts
export interface WeaponSearchParams extends ItemSearchParams {
  // Weapon-specific filters
  g_slot?: 'Primary' | 'Secondary' | 'Range' | 'Ammo' | 'None';
  g_class_1?: string;
  g_class_2?: string;
  g_class_3?: string;
  i_type?: string;
  skillmodtype?: string;
  
  // Stat filters (dynamic table)
  stat_filters?: Array<{
    stat: string;
    value: number;
  }>;
  
  // Stat weights (dynamic table)
  stat_weights?: Array<{
    stat: string;
    weight: number;
  }>;
  
  // Expansion exclusions
  exclude_expansions?: string[];
  
  // Weapon-specific attributes
  proc?: 'None' | 'True';
  proc_level?: number;
  elemental_damage_type?: string;
  bane_damage_type?: string;
  
  // Focus effects
  focus_type?: string;
  focus_effect?: string;
  
  // Display options
  show_full_detail?: boolean;
  show_weight_detail?: boolean;
  ignore_zero?: boolean;
  pet_search?: boolean;
}

export interface StatCategory {
  name: string;
  stats: Array<{
    value: string;
    label: string;
  }>;
}

export interface WeaponSearchResult extends Item {
  weight_score?: number;
  w_eff?: number; // Weapon efficiency (damage/delay)
  proc_info?: {
    spell_id: number;
    spell_name: string;
    level_required: number;
  };
  focus_info?: {
    type: string;
    effect: string;
    spell_id: number;
  };
  elemental_damage?: {
    type: string;
    amount: number;
  };
  bane_damage?: {
    type: string;
    amount: number;
    target: string;
  };
}

// Stat categories for dynamic dropdowns
export const STAT_CATEGORIES: StatCategory[] = [
  {
    name: 'Basic Attributes',
    stats: [
      { value: 'hp', label: 'Hit Points' },
      { value: 'mana', label: 'Mana' },
      { value: 'endur', label: 'Endurance' },
      { value: 'ac', label: 'Armor Class' }
    ]
  },
  {
    name: 'Weapon Attributes',
    stats: [
      { value: 'damage', label: 'Damage' },
      { value: 'delay', label: 'Delay (inverted)' },
      { value: 'w_eff', label: 'Weapon Efficiency' },
      { value: 'procrate', label: 'Proc Rate' },
      { value: 'backstabdmg', label: 'Backstab DMG' },
      { value: 'elemdmgamt', label: 'Elemental Damage' },
      { value: 'bane_damage', label: 'Bane Damage' }
    ]
  },
  {
    name: 'Base Stats',
    stats: [
      { value: 'aagi', label: 'Agility' },
      { value: 'acha', label: 'Charisma' },
      { value: 'adex', label: 'Dexterity' },
      { value: 'aint', label: 'Intelligence' },
      { value: 'asta', label: 'Stamina' },
      { value: 'astr', label: 'Strength' },
      { value: 'awis', label: 'Wisdom' }
    ]
  },
  {
    name: 'Heroic Stats',
    stats: [
      { value: 'heroic_agi', label: 'Heroic Agility' },
      { value: 'heroic_cha', label: 'Heroic Charisma' },
      { value: 'heroic_dex', label: 'Heroic Dexterity' },
      { value: 'heroic_int', label: 'Heroic Intelligence' },
      { value: 'heroic_sta', label: 'Heroic Stamina' },
      { value: 'heroic_str', label: 'Heroic Strength' },
      { value: 'heroic_wis', label: 'Heroic Wisdom' }
    ]
  },
  {
    name: 'Resists (Heroic Included)',
    stats: [
      { value: 'cr', label: 'Resist Cold' },
      { value: 'dr', label: 'Resist Disease' },
      { value: 'fr', label: 'Resist Fire' },
      { value: 'mr', label: 'Resist Magic' },
      { value: 'pr', label: 'Resist Poison' }
    ]
  },
  {
    name: 'Mod 1s',
    stats: [
      { value: 'attack', label: 'Attack' },
      { value: 'haste', label: 'Haste' },
      { value: 'regen', label: 'HP Regeneration' },
      { value: 'manaregen', label: 'Mana Regeneration' },
      { value: 'enduranceregen', label: 'Endurance Regeneration' },
      { value: 'healamt', label: 'Healing Amount' },
      { value: 'spelldmg', label: 'Spell Damage' }
    ]
  },
  {
    name: 'Mod 2s',
    stats: [
      { value: 'accuracy', label: 'Accuracy' },
      { value: 'avoidance', label: 'Avoidance' },
      { value: 'combateffects', label: 'Combat Effects' },
      { value: 'damageshield', label: 'Damage Shielding' },
      { value: 'dotshielding', label: 'DoT Shield' },
      { value: 'shielding', label: 'Shielding' },
      { value: 'spellshield', label: 'Spell Shield' },
      { value: 'strikethrough', label: 'Strikethrough' },
      { value: 'stunresist', label: 'Stun Resist' }
    ]
  }
];

export const WEAPON_SLOTS = ['Primary', 'Range', 'Secondary', 'Ammo'];
export const WEAPON_TYPES = [
  'One Hand Slash', 'One Hand Piercing', 'One Hand Blunt',
  'Hand to Hand', 'Any 1H Weapon', 'Exclude 1H Weapon', 
  'Two Hand Slash', 'Two Hand Blunt', 'Two Hand Piercing', 
  'Any 2H Weapon', 'Exclude 2H Weapon', 'Bow', 'Arrow', 'Thrown'
];
export const ELEMENTAL_DAMAGE_TYPES = [
  'Magic', 'Fire', 'Cold', 'Poison', 'Disease', 
  'Chromatic', 'Prismatic', 'Phys', 'Corruption'
];
export const BANE_DAMAGE_TYPES = [
  { value: 'body_14', label: 'Greater Akheva' },
  { value: 'race_217', label: 'Shissar' },
  { value: 'race_236', label: 'Seru' }
];
```

**2. Enhanced Service Layer for Weapon Search:**

```typescript
// fe/src/services/weaponService.ts
import { apiClient } from './apiClient';
import { WeaponSearchParams, WeaponSearchResult } from '../types/weaponSearch';

export const weaponService = {
  // Advanced weapon search with all filters
  searchWeapons: async (params: WeaponSearchParams): Promise<{
    results: WeaponSearchResult[];
    total: number;
    page: number;
    page_size: number;
    pages: number;
  }> => {
    const response = await apiClient.get('/items/search', { params });
    return response.data;
  },

  // Get weapon-specific data
  getWeaponData: async () => {
    const [slots, types, skills] = await Promise.all([
      apiClient.get('/items/slots'),
      apiClient.get('/items/types'),
      apiClient.get('/spells/skills')
    ]);
    
    return {
      slots: slots.data,
      types: types.data,
      skills: skills.data
    };
  },

  // Get user's saved stat filter/weight sets (if authenticated)
  getUserSets: async () => {
    try {
      const response = await apiClient.get('/user/weapon-sets');
      return response.data;
    } catch {
      return { restricts: [], weights: [] };
    }
  }
};
```

**3. Dynamic Stat Filter/Weight Components:**

```typescript
// fe/src/components/weapon/StatFilterTable.tsx
import React, { useState } from 'react';
import { useFieldArray, useFormContext } from 'react-hook-form';
import Card, { CardBody, CardHeader, CardTitle } from '../common/Card';
import Button from '../common/Button';
import Select from '../common/Select';
import Input from '../common/Input';
import { STAT_CATEGORIES } from '../../types/weaponSearch';

interface StatFilterTableProps {
  name: string;
  title: string;
  description: string;
}

export const StatFilterTable: React.FC<StatFilterTableProps> = ({ 
  name, 
  title, 
  description 
}) => {
  const { control, watch } = useFormContext();
  const { fields, append, remove } = useFieldArray({
    control,
    name
  });

  const addFilter = () => {
    append({ stat: '', value: 0 });
  };

  const removeFilter = (index: number) => {
    remove(index);
  };

  // Get all available stats for dropdown
  const allStats = STAT_CATEGORIES.flatMap(category => 
    category.stats.map(stat => ({
      value: stat.value,
      label: `${category.name} - ${stat.label}`
    }))
  );

  return (
    <Card variant="outlined">
      <CardHeader>
        <CardTitle>{title}</CardTitle>
        <p className="text-sm text-muted-foreground">{description}</p>
      </CardHeader>
      <CardBody>
        <div className="space-y-4">
          {fields.map((field, index) => (
            <div key={field.id} className="flex items-center space-x-4">
              <div className="flex-1">
                <Select
                  label="Stat"
                  options={allStats}
                  value={watch(`${name}.${index}.stat`)}
                  onChange={(value) => {
                    // Update the form value
                    const currentValues = watch(name);
                    currentValues[index].stat = value;
                  }}
                />
              </div>
              <div className="w-24">
                <Input
                  label="Value"
                  type="number"
                  value={watch(`${name}.${index}.value`)}
                  onChange={(e) => {
                    const currentValues = watch(name);
                    currentValues[index].value = parseInt(e.target.value) || 0;
                  }}
                />
              </div>
              <Button
                variant="danger"
                size="sm"
                onClick={() => removeFilter(index)}
                className="mt-6"
              >
                Remove
              </Button>
            </div>
          ))}
          
          <Button variant="outline" onClick={addFilter}>
            Add {title}
          </Button>
        </div>
      </CardBody>
    </Card>
  );
};
```

**4. Weapon Search Form Component:**

```typescript
// fe/src/components/weapon/WeaponSearchForm.tsx
import React from 'react';
import { useForm } from 'react-hook-form';
import Card, { CardBody, CardHeader, CardTitle } from '../common/Card';
import Button from '../common/Button';
import Select from '../common/Select';
import Input from '../common/Input';
import Checkbox from '../common/Checkbox';
import { StatFilterTable } from './StatFilterTable';
import { WeaponSearchParams, WEAPON_SLOTS, WEAPON_TYPES, ELEMENTAL_DAMAGE_TYPES, BANE_DAMAGE_TYPES } from '../../types/weaponSearch';

interface WeaponSearchFormProps {
  onSearch: (params: WeaponSearchParams) => void;
  initialParams?: Partial<WeaponSearchParams>;
}

export const WeaponSearchForm: React.FC<WeaponSearchFormProps> = ({ 
  onSearch, 
  initialParams = {} 
}) => {
  const { register, handleSubmit, watch, setValue, control } = useForm<WeaponSearchParams>({
    defaultValues: {
      g_slot: 'None',
      g_class_1: 'None',
      g_class_2: 'None',
      g_class_3: 'None',
      i_type: 'None',
      skillmodtype: 'None',
      proc: 'None',
      proc_level: 0,
      elemental_damage_type: 'all',
      bane_damage_type: 'all',
      focus_type: '',
      focus_effect: '',
      exclude_expansions: [],
      stat_filters: [],
      stat_weights: [],
      show_full_detail: false,
      show_weight_detail: false,
      ignore_zero: false,
      pet_search: false,
      ...initialParams
    }
  });

  const onSubmit = (data: WeaponSearchParams) => {
    // Clean up empty values and validate
    const cleanData = Object.fromEntries(
      Object.entries(data).filter(([_, value]) => 
        value !== '' && value !== null && value !== undefined && 
        (Array.isArray(value) ? value.length > 0 : true)
      )
    ) as WeaponSearchParams;
    
    onSearch(cleanData);
  };

  const classes = [
    'Bard', 'Beastlord', 'Berserker', 'Cleric', 'Druid', 'Enchanter', 
    'Magician', 'Monk', 'Necromancer', 'Paladin', 'Ranger', 'Rogue', 
    'Shadow Knight', 'Shaman', 'Warrior', 'Wizard'
  ];

  const expansions = ['Classic', 'Kunark', 'Velious', 'Luclin', 'Planes'];

  return (
    <Card>
      <CardHeader>
        <CardTitle>Weapon Search</CardTitle>
      </CardHeader>
      <CardBody>
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
          {/* Basic Weapon Filters */}
          <Card variant="outlined">
            <CardHeader>
              <CardTitle>Basic Filters</CardTitle>
            </CardHeader>
            <CardBody>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                <Select
                  label="Slot"
                  options={[
                    { value: 'None', label: '-- Any Slot --' },
                    ...WEAPON_SLOTS.map(slot => ({ value: slot, label: slot }))
                  ]}
                  {...register('g_slot')}
                />
                
                <Select
                  label="Class 1"
                  options={[
                    { value: 'None', label: '-- Any Class --' },
                    ...classes.map(cls => ({ value: cls, label: cls }))
                  ]}
                  {...register('g_class_1')}
                />
                
                <Select
                  label="Class 2"
                  options={[
                    { value: 'None', label: '-- Any Class --' },
                    ...classes.map(cls => ({ value: cls, label: cls }))
                  ]}
                  {...register('g_class_2')}
                />
                
                <Select
                  label="Class 3"
                  options={[
                    { value: 'None', label: '-- Any Class --' },
                    ...classes.map(cls => ({ value: cls, label: cls }))
                  ]}
                  {...register('g_class_3')}
                />
                
                <Select
                  label="Item Type"
                  options={[
                    { value: 'None', label: 'All Types' },
                    ...WEAPON_TYPES.map(type => ({ value: type, label: type }))
                  ]}
                  {...register('i_type')}
                />
                
                <Input
                  label="Item Name (partial allowed)"
                  placeholder="Enter item name..."
                  {...register('item_name')}
                />
              </div>
            </CardBody>
          </Card>

          {/* Weapon-Specific Filters */}
          <Card variant="outlined">
            <CardHeader>
              <CardTitle>Weapon Attributes</CardTitle>
            </CardHeader>
            <CardBody>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-2">Weapons with Proc</label>
                  <div className="space-y-2">
                    <label className="flex items-center space-x-2">
                      <input
                        type="radio"
                        value="None"
                        {...register('proc')}
                        defaultChecked
                      />
                      <span className="text-sm">Include</span>
                    </label>
                    <label className="flex items-center space-x-2">
                      <input
                        type="radio"
                        value="True"
                        {...register('proc')}
                      />
                      <span className="text-sm">Only</span>
                    </label>
                  </div>
                </div>
                
                <Select
                  label="Required Level to Proc"
                  options={[
                    { value: 0, label: 'Any Level' },
                    ...Array.from({ length: 65 }, (_, i) => ({ 
                      value: i + 1, 
                      label: (i + 1).toString() 
                    }))
                  ]}
                  {...register('proc_level')}
                />
                
                <Select
                  label="Elemental Damage Type"
                  options={[
                    { value: 'all', label: 'All Weapons' },
                    ...ELEMENTAL_DAMAGE_TYPES.map(type => ({ value: type, label: type }))
                  ]}
                  {...register('elemental_damage_type')}
                />
                
                <Select
                  label="Bane Damage Type"
                  options={[
                    { value: 'all', label: 'All Weapons' },
                    ...BANE_DAMAGE_TYPES.map(type => ({ value: type.value, label: type.label }))
                  ]}
                  {...register('bane_damage_type')}
                />
              </div>
            </CardBody>
          </Card>

          {/* Stat Filters */}
          <StatFilterTable
            name="stat_filters"
            title="Stat Filters"
            description="Only items with the provided stats will be searched for. Heroic resists are included when resists are selected."
          />

          {/* Stat Weights */}
          <StatFilterTable
            name="stat_weights"
            title="Stat Weights"
            description="Weights take item stat amount and multiply it by the provided number to create a value. Heroic resists are included when resists are selected."
          />

          {/* Expansion Exclusions */}
          <Card variant="outlined">
            <CardHeader>
              <CardTitle>Expansion Exclusions</CardTitle>
            </CardHeader>
            <CardBody>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                {expansions.map(expansion => (
                  <label key={expansion} className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      value={expansion}
                      {...register('exclude_expansions')}
                    />
                    <span className="text-sm">{expansion}</span>
                  </label>
                ))}
              </div>
            </CardBody>
          </Card>

          {/* Display Options */}
          <Card variant="outlined">
            <CardHeader>
              <CardTitle>Display Options</CardTitle>
            </CardHeader>
            <CardBody>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Checkbox
                  label="Include Zero weight items (Requires one weight)"
                  {...register('ignore_zero')}
                />
                <Checkbox
                  label="Search for Pet items"
                  {...register('pet_search')}
                />
                <Checkbox
                  label="Show Item Detail Table"
                  {...register('show_full_detail')}
                />
                <Checkbox
                  label="Show Only Weight Details (Requires one weight)"
                  {...register('show_weight_detail')}
                />
              </div>
            </CardBody>
          </Card>

          <Button type="submit" variant="primary" className="w-full">
            Search Weapons
          </Button>
        </form>
      </CardBody>
    </Card>
  );
};
```

**5. Weapon Search Results Component:**

```typescript
// fe/src/components/weapon/WeaponSearchResults.tsx
import React from 'react';
import Card, { CardBody, CardHeader, CardTitle } from '../common/Card';
import Button from '../common/Button';
import { WeaponSearchResult } from '../../types/weaponSearch';
import { WeaponCard } from './WeaponCard';

interface WeaponSearchResultsProps {
  weapons: WeaponSearchResult[];
  total: number;
  page: number;
  pageSize: number;
  onPageChange: (page: number) => void;
  showWeightDetail: boolean;
  showFullDetail: boolean;
}

export const WeaponSearchResults: React.FC<WeaponSearchResultsProps> = ({
  weapons,
  total,
  page,
  pageSize,
  onPageChange,
  showWeightDetail,
  showFullDetail
}) => {
  const totalPages = Math.ceil(total / pageSize);

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>Weapon Search Results ({total})</CardTitle>
          <Button variant="outline" size="sm">
            Export Results
          </Button>
        </div>
      </CardHeader>
      <CardBody>
        <div className="space-y-4">
          {weapons.map((weapon) => (
            <WeaponCard
              key={weapon.id}
              weapon={weapon}
              showWeightDetail={showWeightDetail}
              showFullDetail={showFullDetail}
            />
          ))}
        </div>
        
        {/* Pagination */}
        {totalPages > 1 && (
          <div className="flex justify-center space-x-2 mt-6">
            <Button
              variant="outline"
              size="sm"
              onClick={() => onPageChange(page - 1)}
              disabled={page <= 1}
            >
              Previous
            </Button>
            
            {Array.from({ length: totalPages }, (_, i) => i + 1).map((pageNum) => (
              <Button
                key={pageNum}
                variant={pageNum === page ? "primary" : "outline"}
                size="sm"
                onClick={() => onPageChange(pageNum)}
              >
                {pageNum}
              </Button>
            ))}
            
            <Button
              variant="outline"
              size="sm"
              onClick={() => onPageChange(page + 1)}
              disabled={page >= totalPages}
            >
              Next
            </Button>
          </div>
        )}
      </CardBody>
    </Card>
  );
};
```

**6. Weapon Card Component:**

```typescript
// fe/src/components/weapon/WeaponCard.tsx
import React from 'react';
import { Link } from 'react-router-dom';
import Card, { CardBody, CardHeader, CardTitle } from '../common/Card';
import Button from '../common/Button';
import { WeaponSearchResult } from '../../types/weaponSearch';

interface WeaponCardProps {
  weapon: WeaponSearchResult;
  showWeightDetail: boolean;
  showFullDetail: boolean;
}

export const WeaponCard: React.FC<WeaponCardProps> = ({
  weapon,
  showWeightDetail,
  showFullDetail
}) => {
  return (
    <Card hover>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <img
              src={`/item_icons/item_${weapon.icon || 'default'}.png`}
              alt={weapon.name}
              className="w-12 h-12 object-contain"
              onError={(e) => {
                e.currentTarget.src = '/item_icons/item_default.png';
              }}
            />
            <div>
              <CardTitle className="text-lg">{weapon.name}</CardTitle>
              <p className="text-sm text-muted-foreground">
                ID: {weapon.id} | {weapon.type}
              </p>
            </div>
          </div>
          {showWeightDetail && weapon.weight_score && (
            <div className="text-right">
              <p className="text-lg font-bold text-primary">
                Score: {weapon.weight_score.toFixed(2)}
              </p>
            </div>
          )}
        </div>
      </CardHeader>
      <CardBody>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {/* Basic Stats */}
          <div className="space-y-2">
            <h4 className="font-medium text-sm">Basic Stats</h4>
            {weapon.damage && <p className="text-sm">Damage: {weapon.damage}</p>}
            {weapon.delay && <p className="text-sm">Delay: {weapon.delay}</p>}
            {weapon.w_eff && <p className="text-sm">Efficiency: {weapon.w_eff}</p>}
            {weapon.ac && <p className="text-sm">AC: {weapon.ac}</p>}
          </div>
          
          {/* Combat Stats */}
          <div className="space-y-2">
            <h4 className="font-medium text-sm">Combat Stats</h4>
            {weapon.hp && <p className="text-sm">HP: {weapon.hp}</p>}
            {weapon.mana && <p className="text-sm">Mana: {weapon.mana}</p>}
            {weapon.attack && <p className="text-sm">Attack: {weapon.attack}</p>}
            {weapon.haste && <p className="text-sm">Haste: {weapon.haste}%</p>}
          </div>
          
          {/* Effects */}
          <div className="space-y-2">
            <h4 className="font-medium text-sm">Effects</h4>
            {weapon.proc_info && (
              <p className="text-sm">Proc: {weapon.proc_info.spell_name}</p>
            )}
            {weapon.focus_info && (
              <p className="text-sm">Focus: {weapon.focus_info.effect}</p>
            )}
            {weapon.elemental_damage && (
              <p className="text-sm">
                {weapon.elemental_damage.type}: {weapon.elemental_damage.amount}
              </p>
            )}
          </div>
        </div>
        
        {/* Full Detail Table (if requested) */}
        {showFullDetail && (
          <div className="mt-4">
            <details className="border rounded p-2">
              <summary className="cursor-pointer font-medium">Full Item Details</summary>
              <div className="mt-2 text-xs">
                <pre className="whitespace-pre-wrap overflow-x-auto">
                  {JSON.stringify(weapon, null, 2)}
                </pre>
              </div>
            </details>
          </div>
        )}
        
        <div className="flex items-center space-x-2 mt-4">
          <Link to={`/items/details/${weapon.id}`}>
            <Button size="sm" variant="outline">
              View Details
            </Button>
          </Link>
          <Button size="sm" variant="ghost">
            Add to Favorites
          </Button>
        </div>
      </CardBody>
    </Card>
  );
};
```

**7. Main Weapon Search Page:**

```typescript
// fe/src/pages/WeaponSearchPage.tsx
import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { WeaponSearchForm } from '../components/weapon/WeaponSearchForm';
import { WeaponSearchResults } from '../components/weapon/WeaponSearchResults';
import { weaponService } from '../services/weaponService';
import { WeaponSearchParams } from '../types/weaponSearch';
import LoadingSpinner from '../components/common/LoadingSpinner';
import { SkeletonList } from '../components/common/Skeleton';

export const WeaponSearchPage: React.FC = () => {
  const [searchParams, setSearchParams] = useState<WeaponSearchParams>({
    page: 1,
    page_size: 20
  });

  const { data, isLoading, error } = useQuery({
    queryKey: ['weapons', 'search', searchParams],
    queryFn: () => weaponService.searchWeapons(searchParams),
    enabled: Object.keys(searchParams).length > 2 // More than just page/page_size
  });

  const handleSearch = (params: WeaponSearchParams) => {
    setSearchParams({ ...params, page: 1 });
  };

  const handlePageChange = (page: number) => {
    setSearchParams({ ...searchParams, page });
  };

  return (
    <div className="container mx-auto px-4 py-8 space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-foreground mb-2">Weapon Search</h1>
        <p className="text-muted-foreground">
          Advanced weapon search with stat filtering, weighting, and comparison tools
        </p>
      </div>

      <WeaponSearchForm onSearch={handleSearch} />
      
      {isLoading ? (
        <Card>
          <CardBody>
            <div className="text-center py-8">
              <LoadingSpinner size="lg" className="mx-auto mb-4" />
              <p className="text-muted-foreground">Searching for weapons...</p>
            </div>
            <SkeletonList count={6} />
          </CardBody>
        </Card>
      ) : error ? (
        <Card variant="outlined">
          <CardBody>
            <div className="text-center py-8">
              <div className="text-destructive mb-4">
                <svg className="w-12 h-12 mx-auto" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
              </div>
              <p className="text-destructive font-medium">Error loading weapons</p>
              <p className="text-destructive/80 text-sm mt-1">
                {error instanceof Error ? error.message : 'An unknown error occurred'}
              </p>
            </div>
          </CardBody>
        </Card>
      ) : data ? (
        <WeaponSearchResults
          weapons={data.results}
          total={data.total}
          page={data.page}
          pageSize={data.page_size}
          onPageChange={handlePageChange}
          showWeightDetail={searchParams.show_weight_detail || false}
          showFullDetail={searchParams.show_full_detail || false}
        />
      ) : null}
    </div>
  );
};
```

**Testing Strategy:**

1. **Component Testing:**
   - [ ] Test Card variants and hover states
   - [ ] Test loading and error states
   - [ ] Test responsive behavior
   - [ ] Test accessibility features

2. **Integration Testing:**
   - [ ] Test search form submission
   - [ ] Test pagination functionality
   - [ ] Test item detail navigation
   - [ ] Test API error handling

3. **E2E Testing:**
   - [ ] Test complete search workflow
   - [ ] Test item detail page navigation
   - [ ] Test mobile responsiveness
   - [ ] Test performance with large datasets

**React Hook Implementation:**

```typescript
// fe/src/hooks/useItemSearch.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { itemService } from '../services/itemService';
import { ItemSearchParams, ItemSearchResponse, ItemDetail } from '../types/item';

export const useItemSearch = (params: ItemSearchParams, enabled = true) => {
  return useQuery({
    queryKey: ['items', 'search', params],
    queryFn: () => itemService.searchAdvanced(params),
    enabled,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

export const useItemDetails = (itemId: number, enabled = true) => {
  return useQuery({
    queryKey: ['items', 'details', itemId],
    queryFn: () => itemService.getDetails(itemId),
    enabled: enabled && !!itemId,
    staleTime: 10 * 60 * 1000, // 10 minutes
  });
};

export const useItemTypes = () => {
  return useQuery({
    queryKey: ['items', 'types'],
    queryFn: () => itemService.getTypes(),
    staleTime: 60 * 60 * 1000, // 1 hour
  });
};

export const useItemSlots = () => {
  return useQuery({
    queryKey: ['items', 'slots'],
    queryFn: () => itemService.getSlots(),
    staleTime: 60 * 60 * 1000, // 1 hour
  });
};
```

**Form Component Implementation:**

```typescript
// fe/src/components/ItemSearchForm.tsx
import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { ItemSearchParams } from '../types/item';
import { useItemTypes, useItemSlots } from '../hooks/useItemSearch';

interface ItemSearchFormProps {
  onSearch: (params: ItemSearchParams) => void;
  initialParams?: Partial<ItemSearchParams>;
}

export const ItemSearchForm: React.FC<ItemSearchFormProps> = ({ 
  onSearch, 
  initialParams = {} 
}) => {
  const { register, handleSubmit, watch, setValue } = useForm<ItemSearchParams>({
    defaultValues: initialParams
  });

  const { data: itemTypes } = useItemTypes();
  const { data: itemSlots } = useItemSlots();

  const onSubmit = (data: ItemSearchParams) => {
    // Clean up empty values
    const cleanData = Object.fromEntries(
      Object.entries(data).filter(([_, value]) => 
        value !== '' && value !== null && value !== undefined
      )
    ) as ItemSearchParams;
    
    onSearch(cleanData);
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Item Search</CardTitle>
      </CardHeader>
      <CardBody>
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          {/* Basic Search */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">
                Item Name (partial allowed)
              </label>
              <input
                type="text"
                {...register('name')}
                className="w-full px-3 py-2 border rounded-md"
                placeholder="Enter item name..."
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium mb-1">Item Type</label>
              <select {...register('item_type')} className="w-full px-3 py-2 border rounded-md">
                <option value="">All Types</option>
                {itemTypes && Object.entries(itemTypes).map(([id, name]) => (
                  <option key={id} value={name}>{name}</option>
                ))}
              </select>
            </div>
          </div>

          {/* Filter Checkboxes */}
          <Card variant="outlined">
            <CardBody>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <label className="flex items-center space-x-2">
                  <input type="checkbox" {...register('tradeskill_only')} />
                  <span className="text-sm">Tradeskill Only</span>
                </label>
                
                <label className="flex items-center space-x-2">
                  <input type="checkbox" {...register('equippable_only')} />
                  <span className="text-sm">Equippable Only</span>
                </label>
                
                <label className="flex items-center space-x-2">
                  <input type="checkbox" {...register('exclude_glamours')} />
                  <span className="text-sm">Exclude Glamours</span>
                </label>
                
                <label className="flex items-center space-x-2">
                  <input type="checkbox" {...register('only_augments')} />
                  <span className="text-sm">Only Augments</span>
                </label>
              </div>
            </CardBody>
          </Card>

          {/* Advanced Filters (collapsible) */}
          <Card variant="outlined">
            <CardBody>
              <details className="space-y-4">
                <summary className="cursor-pointer font-medium">
                  Advanced Filters
                </summary>
        
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <label className="block text-sm font-medium mb-1">Slot</label>
                    <select {...register('item_slot')} className="w-full px-3 py-2 border rounded-md">
                      <option value="">Any Slot</option>
                      {itemSlots && Object.entries(itemSlots).map(([id, name]) => (
                        <option key={id} value={name}>{name}</option>
                      ))}
                    </select>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium mb-1">Expansion</label>
                    <select {...register('expansion')} className="w-full px-3 py-2 border rounded-md">
                      <option value="">All Expansions</option>
                      <option value="Classic">Classic</option>
                      <option value="Kunark">Kunark</option>
                      <option value="Velious">Velious</option>
                      <option value="Luclin">Luclin</option>
                      <option value="Planes">Planes of Power</option>
                    </select>
                  </div>
                  
                  <div>
            <label className="block text-sm font-medium mb-1">Proc Effect</label>
            <select {...register('proc')} className="w-full px-3 py-2 border rounded-md">
              <option value="None">Include All</option>
              <option value="True">Only With Proc</option>
            </select>
          </div>
        </div>
      </details>

      <button
        type="submit"
        className="w-full md:w-auto px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
      >
        Search
      </button>
    </form>
  );
};
```

**Search Results Component:**

```typescript
// fe/src/components/ItemSearchResults.tsx
import React from 'react';
import { Item } from '../types/item';
import { ItemCard } from './ItemCard';

interface ItemSearchResultsProps {
  items: Item[];
  total: number;
  page: number;
  pageSize: number;
  onPageChange: (page: number) => void;
  onItemClick: (item: Item) => void;
}

export const ItemSearchResults: React.FC<ItemSearchResultsProps> = ({
  items,
  total,
  page,
  pageSize,
  onPageChange,
  onItemClick
}) => {
  const totalPages = Math.ceil(total / pageSize);

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <p className="text-sm text-gray-600">
          Showing {((page - 1) * pageSize) + 1} to {Math.min(page * pageSize, total)} of {total} items
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {items.map((item) => (
          <ItemCard
            key={item.id}
            item={item}
            onClick={() => onItemClick(item)}
          />
        ))}
      </div>

      {totalPages > 1 && (
        <div className="flex justify-center space-x-2">
          <button
            onClick={() => onPageChange(page - 1)}
            disabled={page <= 1}
            className="px-3 py-1 border rounded disabled:opacity-50"
          >
            Previous
          </button>
          
          {Array.from({ length: totalPages }, (_, i) => i + 1).map((pageNum) => (
            <button
              key={pageNum}
              onClick={() => onPageChange(pageNum)}
              className={`px-3 py-1 border rounded ${
                pageNum === page ? 'bg-blue-600 text-white' : ''
              }`}
            >
              {pageNum}
            </button>
          ))}
          
          <button
            onClick={() => onPageChange(page + 1)}
            disabled={page >= totalPages}
            className="px-3 py-1 border rounded disabled:opacity-50"
          >
            Next
          </button>
        </div>
      )}
    </div>
  );
};
```

**Main Search Page:**

```typescript
// fe/src/pages/ItemSearchPage.tsx
import React, { useState } from 'react';
import { useItemSearch } from '../hooks/useItemSearch';
import { ItemSearchForm } from '../components/ItemSearchForm';
import { ItemSearchResults } from '../components/ItemSearchResults';
import { Item } from '../types/item';
import { useNavigate } from 'react-router-dom';

export const ItemSearchPage: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useState<ItemSearchParams>({
    page: 1,
    page_size: 20
  });

  const { data, isLoading, error } = useItemSearch(searchParams);

  const handleSearch = (params: ItemSearchParams) => {
    setSearchParams({ ...params, page: 1 });
  };

  const handlePageChange = (page: number) => {
    setSearchParams({ ...searchParams, page });
  };

  const handleItemClick = (item: Item) => {
    navigate(`/items/details/${item.id}`);
  };

  return (
    <div className="container mx-auto px-4 py-8 space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-foreground mb-2">Item Search</h1>
        <p className="text-muted-foreground">
          Search for items across all expansions with advanced filtering options
        </p>
      </div>

      <ItemSearchForm onSearch={handleSearch} />
      
      <ItemSearchResults
        items={data?.results || []}
        total={data?.total || 0}
        page={searchParams.page || 1}
        pageSize={searchParams.page_size || 20}
        onPageChange={handlePageChange}
        onItemClick={handleItemClick}
        isLoading={isLoading}
        error={error}
      />
    </div>
  );
};
```

**Updated ItemCard Component (using Card system):**

```typescript
// fe/src/components/items/ItemCard.tsx
import React from 'react';
import { Link } from 'react-router-dom';
import Card, { CardBody } from '../common/Card';
import { Item } from '../../types/item';

interface ItemCardProps {
  item: Item;
  onClick?: () => void;
}

const ItemCard: React.FC<ItemCardProps> = ({ item, onClick }) => {
  const handleImageError = (e: React.SyntheticEvent<HTMLImageElement, Event>) => {
    e.currentTarget.src = '/item_icons/item_default.png';
  };

  const cardContent = (
    <CardBody>
      <div className="flex flex-col items-center text-center space-y-3">
        <img
          src={`/item_icons/item_${item.icon || 'default'}.png`}
          alt={item.name}
          onError={handleImageError}
          className="w-16 h-16 object-contain"
        />
        <div className="space-y-1">
          <h3 className="font-semibold text-foreground text-sm leading-tight">
            {item.name}
          </h3>
          {item.type && (
            <p className="text-xs text-muted-foreground">{item.type}</p>
          )}
          {item.slot_names && (
            <p className="text-xs text-muted-foreground">{item.slot_names}</p>
          )}
        </div>
      </div>
    </CardBody>
  );

  if (onClick) {
    return (
      <Card hover onClick={onClick} className="cursor-pointer">
        {cardContent}
      </Card>
    );
  }

  return (
    <Link to={`/items/details/${item.id}`}>
      <Card hover className="cursor-pointer">
        {cardContent}
      </Card>
    </Link>
  );
};

export default ItemCard;
```

**Updated SearchResults Component (using Card wrappers):**

```typescript
// fe/src/components/items/SearchResults.tsx
import React from 'react';
import { Item } from '../../types/item';
import Card, { CardBody, CardHeader, CardTitle } from '../common/Card';
import Button from '../common/Button';
import LoadingSpinner from '../common/LoadingSpinner';
import { SkeletonList } from '../common/Skeleton';

interface SearchResultsProps {
  items: Item[] | null;
  isLoading: boolean;
  error: Error | null;
  total?: number;
  page?: number;
  pageSize?: number;
  onPageChange?: (page: number) => void;
}

const SearchResults: React.FC<SearchResultsProps> = ({ 
  items, 
  isLoading, 
  error,
  total = 0,
  page = 1,
  pageSize = 20,
  onPageChange
}) => {
  if (isLoading) {
    return (
      <Card>
        <CardBody>
          <div className="text-center py-8">
            <LoadingSpinner size="lg" className="mx-auto mb-4" />
            <p className="text-muted-foreground">Searching for items...</p>
          </div>
          <SkeletonList count={6} />
        </CardBody>
      </Card>
    );
  }

  if (error) {
    return (
      <Card variant="outlined">
        <CardBody>
          <div className="text-center py-4">
            <div className="text-destructive mb-2">
              <svg className="w-8 h-8 mx-auto" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
            </div>
            <p className="text-destructive font-medium">Error loading items</p>
            <p className="text-destructive/80 text-sm mt-1">{error.message}</p>
          </div>
        </CardBody>
      </Card>
    );
  }

  if (items && items.length > 0) {
    return (
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Search Results ({total})</CardTitle>
            <Button variant="outline" size="sm">
              Export Results
            </Button>
          </div>
        </CardHeader>
        <CardBody>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {items.map((item: Item) => (
              <ItemCard key={item.id} item={item} />
            ))}
          </div>
          
          {/* Pagination */}
          {onPageChange && total > pageSize && (
            <div className="flex justify-center space-x-2 mt-6">
              <Button
                variant="outline"
                size="sm"
                onClick={() => onPageChange(page - 1)}
                disabled={page <= 1}
              >
                Previous
              </Button>
              
              {Array.from({ length: Math.ceil(total / pageSize) }, (_, i) => i + 1).map((pageNum) => (
                <Button
                  key={pageNum}
                  variant={pageNum === page ? "primary" : "outline"}
                  size="sm"
                  onClick={() => onPageChange(pageNum)}
                >
                  {pageNum}
                </Button>
              ))}
              
              <Button
                variant="outline"
                size="sm"
                onClick={() => onPageChange(page + 1)}
                disabled={page >= Math.ceil(total / pageSize)}
              >
                Next
              </Button>
            </div>
          )}
        </CardBody>
      </Card>
    );
  }

  if (items && items.length === 0) {
    return (
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
    );
  }

  return (
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
  );
};

export default SearchResults;
```

**ItemDetail Page Implementation (using Card system):**

```typescript
// fe/src/pages/ItemDetailPage.tsx
import React from 'react';
import { useParams, Link } from 'react-router-dom';
import { useItemDetails } from '../hooks/useItemSearch';
import Card, { CardBody, CardHeader, CardTitle } from '../components/common/Card';
import Button from '../components/common/Button';
import LoadingSpinner from '../components/common/LoadingSpinner';
import { SkeletonCard } from '../components/common/Skeleton';

export const ItemDetailPage: React.FC = () => {
  const { itemId } = useParams<{ itemId: string }>();
  const { data: itemDetail, isLoading, error } = useItemDetails(Number(itemId));

  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-8 space-y-6">
        <div className="flex items-center space-x-4">
          <Button variant="outline" size="sm" onClick={() => window.history.back()}>
            ← Back
          </Button>
          <SkeletonCard />
        </div>
      </div>
    );
  }

  if (error || !itemDetail) {
    return (
      <div className="container mx-auto px-4 py-8 space-y-6">
        <Button variant="outline" size="sm" onClick={() => window.history.back()}>
          ← Back
        </Button>
        <Card variant="outlined">
          <CardBody>
            <div className="text-center py-8">
              <div className="text-destructive mb-4">
                <svg className="w-12 h-12 mx-auto" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
              </div>
              <p className="text-destructive font-medium">Item not found</p>
              <p className="text-destructive/80 text-sm mt-1">
                {error?.message || 'The requested item could not be loaded'}
              </p>
            </div>
          </CardBody>
        </Card>
      </div>
    );
  }

  const { enriched_data, npcs, spells, metadata } = itemDetail;

  return (
    <div className="container mx-auto px-4 py-8 space-y-6">
      {/* Header */}
      <div className="flex items-center space-x-4">
        <Button variant="outline" size="sm" onClick={() => window.history.back()}>
          ← Back
        </Button>
        <div>
          <h1 className="text-3xl font-bold text-foreground">{enriched_data.name}</h1>
          <p className="text-muted-foreground">Item ID: {enriched_data.id}</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Item Info */}
        <div className="lg:col-span-2 space-y-6">
          {/* Basic Information */}
          <Card>
            <CardHeader>
              <CardTitle>Item Information</CardTitle>
            </CardHeader>
            <CardBody>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium text-muted-foreground">Type</label>
                  <p className="text-foreground">{enriched_data.human_readable.type}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-muted-foreground">Slots</label>
                  <p className="text-foreground">{enriched_data.human_readable.slots}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-muted-foreground">Expansion</label>
                  <p className="text-foreground">{enriched_data.human_readable.expansion}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-muted-foreground">Classes</label>
                  <p className="text-foreground">{enriched_data.human_readable.classes.join(', ')}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-muted-foreground">Races</label>
                  <p className="text-foreground">{enriched_data.human_readable.races.join(', ')}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-muted-foreground">Material</label>
                  <p className="text-foreground">{enriched_data.human_readable.material}</p>
                </div>
              </div>
            </CardBody>
          </Card>

          {/* NPC Drops */}
          {npcs && npcs.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>NPC Drops ({npcs.length})</CardTitle>
              </CardHeader>
              <CardBody>
                <div className="space-y-2">
                  {npcs.map((npc, index) => (
                    <div key={index} className="flex justify-between items-center p-2 bg-muted rounded">
                      <div>
                        <p className="font-medium">{npc.npc_name}</p>
                        <p className="text-sm text-muted-foreground">{npc.zone_name}</p>
                      </div>
                      <div className="text-right">
                        {npc.level && <p className="text-sm">Level {npc.level}</p>}
                        {npc.drop_rate && <p className="text-sm text-muted-foreground">{npc.drop_rate}%</p>}
                      </div>
                    </div>
                  ))}
                </div>
              </CardBody>
            </Card>
          )}

          {/* Spells */}
          {spells && spells.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>Spell Effects ({spells.length})</CardTitle>
              </CardHeader>
              <CardBody>
                <div className="space-y-3">
                  {spells.map((spell, index) => (
                    <div key={index} className="p-3 bg-muted rounded">
                      <p className="font-medium">{spell.type}</p>
                      <p className="text-sm text-muted-foreground">Spell ID: {spell.spell_id}</p>
                    </div>
                  ))}
                </div>
              </CardBody>
            </Card>
          )}
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Item Icon */}
          <Card>
            <CardBody>
              <div className="flex flex-col items-center space-y-4">
                <img
                  src={`/item_icons/item_${enriched_data.id}.png`}
                  alt={enriched_data.name}
                  className="w-32 h-32 object-contain"
                  onError={(e) => {
                    e.currentTarget.src = '/item_icons/item_default.png';
                  }}
                />
                <div className="text-center">
                  <p className="text-sm text-muted-foreground">Last Updated</p>
                  <p className="text-sm">{new Date(metadata.last_updated).toLocaleDateString()}</p>
                </div>
              </div>
            </CardBody>
          </Card>

          {/* Actions */}
          <Card>
            <CardHeader>
              <CardTitle>Actions</CardTitle>
            </CardHeader>
            <CardBody>
              <div className="space-y-2">
                <Button variant="outline" className="w-full">
                  Add to Favorites
                </Button>
                <Button variant="outline" className="w-full">
                  Compare Items
                </Button>
                <Button variant="outline" className="w-full">
                  Share Item
                </Button>
              </div>
            </CardBody>
          </Card>

          {/* Metadata */}
          <Card variant="outlined">
            <CardHeader>
              <CardTitle>Data Sources</CardTitle>
            </CardHeader>
            <CardBody>
              <div className="space-y-2">
                {metadata.data_sources.map((source, index) => (
                  <p key={index} className="text-sm text-muted-foreground">{source}</p>
                ))}
              </div>
            </CardBody>
          </Card>
        </div>
      </div>
    </div>
  );
};
```

**Error Handling & Development Patterns:**

```typescript
// Error handling utilities
export const handleApiError = (error: any, context: string) => {
  if (process.env.NODE_ENV === 'development') {
    console.error(`API Error in ${context}:`, error);
    console.error('Full error object:', error);
  }
  
  // Return user-friendly error message
  if (error.response?.status === 404) {
    return 'Item not found';
  } else if (error.response?.status === 500) {
    return 'Server error - please try again later';
  } else if (error.code === 'NETWORK_ERROR') {
    return 'Network error - check your connection';
  }
  
  return 'An unexpected error occurred';
};

// Type validation utilities
export const validateItemResponse = (data: any): Item => {
  if (!data.id || !data.name) {
    throw new Error('Invalid item data received from API');
  }
  return data as Item;
};
```

**Implementation Checklist:**

- [ ] Update TypeScript types in `fe/src/types/item.ts`
- [ ] Create service layer with API integration
- [ ] Implement React hooks for data fetching
- [ ] Build form components with proper validation
- [ ] Create search results display components
- [ ] Add error handling and loading states
- [ ] Implement pagination and filtering
- [ ] Add responsive design for mobile
- [ ] Test with actual API endpoints
- [ ] Add keyboard navigation support
- [ ] Implement search history (optional)

**Next Steps:**
After completing the basic item search, we can implement specialized search forms for:
- Weapon search (with damage, proc, elemental types)
- Armor search (with AC, resists, focus effects)
- Quest item search (with NPC drops, zone information)
- Tradeskill item search (with recipe requirements)

Each specialized search will reuse the core components while adding context-specific filters and display options.

### Week 4: Spell & NPC Systems
- [ ] Create SpellSearch component with class/level filters
- [ ] Implement SpellDetail page with effects display
- [ ] Create NPCSearch with zone/level filters
- [ ] Implement NPCDetail with drops and quests
- [ ] Add spell tooltips and hover effects
- [ ] Create class spell listing pages

## Phase 3: Advanced Features (Week 5-6)

### Week 5: Zone & Tradeskill Systems
- [x] **COMPLETED**: Create ZoneListing with expansion grouping
- [ ] Implement ZoneDetail with NPCs and items
- [ ] Create TradeskillSearch with recipe counts
- [ ] Implement TradeskillDetail with recipes
- [ ] Add recipe component display
- [x] **COMPLETED**: Create waypoint listing functionality

### Week 6: Quest & Faction Systems
- [ ] Create QuestSearch with multiple filters
- [ ] Implement QuestDetail with requirements/rewards
- [ ] Create FactionSearch and FactionDetail
- [ ] Add quest chain functionality
- [ ] Implement faction standing display
- [ ] Create pet listing functionality

## Phase 4: User Features (Week 7-8)

### Week 7: User Management & Authentication
- [x] **COMPLETED**: Implement local user account system with JWT authentication
- [x] **COMPLETED**: Create API key management system for programmatic access
- [x] **COMPLETED**: Add user preferences and profile management
- [x] **COMPLETED**: Implement password change functionality
- [x] **COMPLETED**: Create admin user management features
- [x] **COMPLETED**: Set up anonymous API access for read operations
- [x] **COMPLETED**: Implement authentication middleware for protected endpoints
- [ ] Set up authentication context (Discord OAuth)
- [ ] Create user profile and preferences
- [ ] Add gear list management
- [ ] Implement restrict set functionality
- [ ] Create weight set management
- [ ] Add user data persistence

### Week 8: Tools & Games
- [ ] Create Identify Game minigame
- [ ] Implement search history and favorites
- [ ] Add export/import functionality
- [ ] Create advanced filtering system
- [ ] Implement bulk operations
- [ ] Add keyboard shortcuts

## Phase 5: Polish & Deployment (Week 9-10)

### Week 9: Performance & UX
- [ ] Optimize bundle size and loading
- [ ] Implement virtual scrolling for large lists
- [ ] Add progressive loading and caching
- [ ] Create mobile-responsive design
- [ ] Implement accessibility features
- [ ] Add comprehensive error handling

### Week 10: Testing & Deployment
- [ ] Write unit tests for components
- [ ] Create integration tests for API calls
- [ ] Perform cross-browser testing
- [ ] Optimize for production build
- [ ] Set up CI/CD pipeline
- [ ] Deploy to staging environment

## Key Implementation Details

### API Integration Strategy
1. **Service Layer**: Create dedicated service files for each entity type
2. **Caching**: Use React Query for intelligent caching and background updates
3. **Error Handling**: Implement global error boundaries and user-friendly error messages
4. **Loading States**: Create skeleton screens and loading indicators
5. **Pagination**: Implement infinite scroll or pagination for large datasets

### State Management
1. **Server State**: React Query for API data and caching
2. **Client State**: Zustand for UI state, user preferences, and local data
3. **Form State**: React Hook Form for form management and validation
4. **URL State**: React Router for navigation and search parameters

### Authentication System
1. **Local Accounts**: Email/password authentication with JWT tokens
2. **API Keys**: Long-lived keys for programmatic access and integrations
3. **Anonymous Access**: Read-only operations available without authentication
4. **Admin Functions**: User management and system administration
5. **Discord OAuth**: Legacy authentication system (to be integrated)

### Performance Optimizations
1. **Code Splitting**: Lazy load routes and large components
2. **Memoization**: Use React.memo and useMemo for expensive operations
3. **Virtual Scrolling**: For large lists of items/spells/NPCs
4. **Image Optimization**: Lazy load images and use appropriate formats
5. **Bundle Optimization**: Tree shaking and dynamic imports

### Accessibility Features
1. **Keyboard Navigation**: Full keyboard support for all interactions
2. **Screen Reader Support**: Proper ARIA labels and semantic HTML
3. **Color Contrast**: Ensure WCAG 2.1 AA compliance
4. **Focus Management**: Proper focus indicators and management
5. **Alternative Text**: Descriptive alt text for images and icons

### Mobile Responsiveness
1. **Mobile-First Design**: Design for mobile devices first
2. **Touch-Friendly**: Appropriate touch targets and gestures
3. **Responsive Navigation**: Collapsible menu for mobile
4. **Optimized Forms**: Mobile-friendly form inputs and layouts
5. **Performance**: Optimize for slower mobile connections

## Success Metrics

### Performance
- Initial page load < 2 seconds
- Search results display < 500ms
- Smooth 60fps animations
- Lighthouse score > 90

### User Experience
- Intuitive navigation and search
- Consistent design language
- Responsive across all devices
- Accessible to users with disabilities

### Functionality
- 100% feature parity with current Flask frontend
- All API endpoints properly integrated
- Error handling for all edge cases
- Comprehensive search and filtering

## Risk Mitigation

### Technical Risks
- **API Changes**: Maintain backward compatibility and versioning
- **Performance Issues**: Implement monitoring and optimization strategies
- **Browser Compatibility**: Test across major browsers and versions

### User Experience Risks
- **Learning Curve**: Provide clear navigation and help documentation
- **Feature Loss**: Ensure all current features are preserved
- **Mobile Experience**: Extensive mobile testing and optimization

### Timeline Risks
- **Scope Creep**: Stick to defined phases and features
- **Technical Debt**: Regular code reviews and refactoring
- **Dependencies**: Monitor and update dependencies regularly

## Post-Launch Plan

### Monitoring
- Performance monitoring with real user metrics
- Error tracking and alerting
- User feedback collection and analysis

### Iteration
- Regular feature updates based on user feedback
- Performance optimizations based on usage data
- Accessibility improvements and compliance updates

### Maintenance
- Regular dependency updates and security patches
- Code quality improvements and refactoring
- Documentation updates and maintenance 
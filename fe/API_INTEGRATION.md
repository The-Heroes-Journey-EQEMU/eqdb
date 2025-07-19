# API Integration Guide

## Overview

The EQDB frontend follows an **API-driven development** approach where all data models, types, and API calls are derived from or validated against the Swagger/OpenAPI specification. This ensures type safety, consistency, and maintainability.

## Swagger Integration

### API Documentation
- **Swagger UI**: `http://localhost:5001/api/v1/`
- **OpenAPI JSON**: `http://localhost:5001/swagger.json`
- **API Base URL**: `http://localhost:5001/api/v1/`

### Key Principles

1. **Single Source of Truth**: The Swagger specification is the authoritative source for all API contracts
2. **Type Safety**: All frontend types must match the exact schema defined in Swagger
3. **Contract-First**: API contracts define the interface between frontend and backend
4. **Validation**: Runtime validation ensures API responses match expected schemas

## Implementation Strategy

### 1. Type Generation (Recommended)

Consider using `openapi-typescript` to automatically generate TypeScript types from the Swagger specification:

```bash
npm install --save-dev openapi-typescript
```

```json
// package.json script
{
  "scripts": {
    "generate-types": "openapi-typescript http://localhost:5001/swagger.json -o src/types/api.ts"
  }
}
```

### 2. Manual Type Definition (Current Approach)

Currently, we manually define types based on the Swagger specification. Each service file includes:

```typescript
// Example from itemService.ts
export interface Item {
  id: number
  name: string
  type: string
  serialized: string
}

export interface ItemSearchParams {
  id?: number
  name?: string
  type?: string
}
```

### 3. Service Layer Pattern

Each API endpoint has a corresponding service function:

```typescript
export const itemService = {
  searchItems: async (params: ItemSearchParams = {}): Promise<Item[]> => {
    const response = await api.get<Item[]>('/items', params)
    return response.data
  },
  
  getItemById: async (id: number): Promise<Item[]> => {
    const response = await api.get<Item[]>('/items', { id })
    return response.data
  }
}
```

## API Endpoints

Based on the Swagger specification, the following endpoints are available:

### Items
- `GET /items` - Search items by name, type, or ID
- Parameters: `name`, `type`, `id`

### Spells
- `GET /spells` - Search spells by name, class, or ID
- Parameters: `name`, `class`, `id`

### NPCs
- `GET /npcs` - Search NPCs by name, zone, or ID
- Parameters: `name`, `zone`, `id`

### Zones
- `GET /zones` - Search zones by name
- Parameters: `name`

### Quests
- `GET /quests` - Search quests with multiple filters
- Parameters: `name`, `npc_name`, `item_id`, `item_name`, `min_level`, `max_level`, `zone`, `expansion`

### Expansions
- `GET /expansions` - Get all expansions
- `GET /expansions/{id}` - Get specific expansion
- `GET /expansions/search` - Search expansions by name
- `GET /expansions/{id}/zones` - Get zones by expansion

### Tradeskills
- `GET /tradeskills` - Search tradeskills by name or ID
- `GET /recipes` - Search recipes with filters

### Expansion Items
- `GET /expansion-items` - Get expansion items with filters
- `GET /expansion-items/summary` - Get expansion items summary
- `GET /expansion-items/custom` - Get custom items
- `POST /expansion-items/custom` - Add custom item
- `DELETE /expansion-items/custom/{item_id}/{expansion_id}` - Remove custom item

## Error Handling

All API calls should handle the following error scenarios as defined in Swagger:

### HTTP Status Codes
- `400` - Bad Request (Invalid parameters)
- `401` - Unauthorized (Authentication required)
- `403` - Forbidden (Access denied)
- `404` - Not Found (Resource not found)
- `429` - Too Many Requests (Rate limiting)
- `500` - Internal Server Error

### Error Response Format
```typescript
interface ApiError {
  message: string
}
```

### Implementation Example
```typescript
// In api.ts
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      const status = error.response.status
      const message = error.response.data?.message || 'An error occurred'
      
      switch (status) {
        case 401:
          toast.error('Authentication required. Please log in.')
          break
        case 404:
          toast.error('Resource not found.')
          break
        default:
          toast.error(message)
      }
    }
    return Promise.reject(error)
  }
)
```

## Validation

### Runtime Validation
Consider implementing runtime validation using libraries like `zod`:

```typescript
import { z } from 'zod'

const ItemSchema = z.object({
  id: z.number(),
  name: z.string(),
  type: z.string(),
  serialized: z.string()
})

export const validateItem = (data: unknown): Item => {
  return ItemSchema.parse(data)
}
```

### Type Checking
Ensure all API responses are properly typed:

```typescript
const response = await api.get<Item[]>('/items', params)
// TypeScript will ensure response.data is Item[]
```

## Testing

### API Integration Tests
Test against actual API responses to ensure type compatibility:

```typescript
describe('Item API', () => {
  it('should return items with correct types', async () => {
    const items = await itemService.searchItems({ name: 'dagger' })
    expect(items).toBeInstanceOf(Array)
    expect(items[0]).toHaveProperty('id')
    expect(items[0]).toHaveProperty('name')
    expect(items[0]).toHaveProperty('type')
  })
})
```

### Mock API Responses
Use the Swagger specification to create accurate mocks:

```typescript
const mockItem: Item = {
  id: 12345,
  name: 'Fine Steel Dagger',
  type: 'Weapon',
  serialized: '{"stats": {"damage": "1-5"}}'
}
```

## Best Practices

1. **Keep Types in Sync**: When API changes, update frontend types immediately
2. **Use Strict Typing**: Avoid `any` types, use proper interfaces
3. **Handle All Cases**: Account for all possible API responses and errors
4. **Document Changes**: Update documentation when API contracts change
5. **Test Thoroughly**: Verify type compatibility with actual API responses

## Future Improvements

1. **Automatic Type Generation**: Implement `openapi-typescript` for automatic type generation
2. **Runtime Validation**: Add comprehensive runtime validation using `zod`
3. **API Versioning**: Implement proper API versioning support
4. **Caching Strategy**: Optimize caching based on API response patterns
5. **Error Recovery**: Implement intelligent error recovery and retry logic 
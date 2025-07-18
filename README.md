EverQuest Database for The Heroes Journey Emulator Server

ABOUT
EQDB is intended as a full-featured search interface to the THJ database to find items, spells, npcs, zones, and more.

## Development Setup

### Quick Start (Recommended)
1. Clone EQDB from the official GitHub repository (https://github.com/The-Heroes-Journey-EQEMU/eqdb)
2. Run `python3 setup.py` to install the necessary packages
3. Run `python3 configure.py` to set up the configuration file
4. Run `python3 create_local_db.py` to set up the local database for storing restrict and weight sets
5. Edit the configuration file for the required database fields
   - The 'remote' database is expected to be a THJ / EQEMU compatible database schema. Typically, this takes the form of the 'content' database.
6. **Start the unified development server:**
   ```bash
   python3 dev_server.py
   ```

This will start both the backend and frontend servers:
- **Frontend (React/TypeScript)**: http://localhost:3100
- **Backend API**: http://localhost:5001
- **API Documentation (Swagger)**: http://localhost:5001/api/v1/

### Manual Setup (Alternative)

#### Backend Only
```bash
python3 eqdb.py
```
This will create a locally available EQDB instance that you can reach by using your browser and going to `127.0.0.1:5001` or `localhost:5001`

#### Frontend Only
```bash
cd fe/
npm install
npm run dev
```
This will start the React development server at http://localhost:3100

## Authentication System

EQDB includes a comprehensive local user account system with JWT authentication and API key management.

### Default Admin Account
- **Email**: aepod23@gmail.com
- **Password**: frogluck23
- **Role**: Administrator

### Authentication Methods
1. **JWT Tokens**: Standard Bearer token authentication for web applications
2. **API Keys**: Long-lived keys for programmatic access and integrations

### API Authentication
All API endpoints require authentication. You can authenticate using either:
- **JWT Token**: Include `Authorization: Bearer <token>` header
- **API Key**: Include `X-API-KEY: <your-api-key>` header

### User Management Features
- **User Registration**: Admin can create new user accounts
- **Password Management**: Users can change their passwords
- **Profile Management**: View and update user preferences
- **API Key Management**: Create, view, and delete API keys
- **Admin Functions**: User management and system administration

### Authentication Endpoints
- `POST /api/v1/auth/login` - User login (returns JWT tokens)
- `POST /api/v1/auth/refresh` - Refresh JWT access token
- `GET /api/v1/auth/profile` - Get current user profile
- `POST /api/v1/auth/change-password` - Change user password
- `GET /api/v1/auth/preferences` - Get user preferences
- `PUT /api/v1/auth/preferences` - Update user preferences
- `GET /api/v1/auth/api-keys` - List user's API keys
- `POST /api/v1/auth/api-keys` - Create new API key
- `DELETE /api/v1/auth/api-keys/<id>` - Delete API key
- `GET /api/v1/auth/users` - List all users (admin only)
- `POST /api/v1/auth/users` - Create new user (admin only)

### Frontend Authentication
The frontend now includes a complete authentication system:
- **Login Page**: `/login` - User authentication with email/password
- **User Profile**: `/user` - Protected route for user settings and preferences
- **Protected Routes**: Automatic redirection for unauthenticated users
- **User Menu**: Header integration with user status and logout functionality

### Database Storage
- **Current**: SQLite database (`local_db.db`) for user data
- **Future**: Planned migration to MariaDB for production use
- **Tables**: `users`, `api_keys`, and related user data tables

## Project Structure

- **Backend**: Flask-based Python application with SQLAlchemy ORM
- **Frontend**: Modern React/TypeScript application with Tailwind CSS
- **API**: RESTful API with Swagger documentation at `/api/v1/`
- **Database**: External MySQL database for game data + local SQLite database for user data
- **Authentication**: Local user accounts with JWT and API key support

## Features

- **Modern Web Interface**: React-based frontend with responsive design
- **RESTful API**: Complete API for programmatic access to game data
- **Swagger Documentation**: Interactive API documentation
- **Local User Accounts**: Email/password authentication with JWT tokens
- **API Key Management**: Long-lived keys for integrations and automation
- **Discord OAuth2**: User authentication and personal features (legacy)
- **Comprehensive Search**: Items, spells, NPCs, zones, tradeskills, and more
- **User Features**: Personal gear lists, weight sets, and restrictions
- **Admin Functions**: User management and system administration

## Frontend Development

The frontend is built using modern React/TypeScript and follows an **API-driven development** approach:

### Key Principles
- **Swagger-First**: All frontend types and API calls are derived from the Swagger specification
- **Type Safety**: Complete TypeScript integration with API contracts
- **Modern Stack**: React 18, TypeScript, Tailwind CSS, React Query
- **Responsive Design**: Mobile-first approach with modern UI/UX

### Development Approach
- **API Documentation**: Available at `http://localhost:5001/api/v1/`
- **Type Generation**: Frontend types are generated from or validated against Swagger
- **Service Layer**: Clean separation between UI and API logic
- **Error Handling**: Comprehensive error handling for all API scenarios

### Recent Updates (v2.1.0.1)

#### Authentication System
- **Complete Frontend Integration**: Login, user profile, and protected routes
- **JWT Token Management**: Automatic token refresh and storage
- **User Context**: Global authentication state management
- **Protected Routes**: Automatic redirection for unauthenticated users
- **User Menu**: Header integration with authentication status

#### Theming System
- **CSS Variables**: Implemented comprehensive theming using CSS custom properties
- **Dark Theme**: Default dark theme with proper contrast and accessibility
- **Component Consistency**: All components updated to use theme variables
- **Color Palette**: 
  - Background: `#212529` (dark gray)
  - Content Box: `rgb(43 48 53)` (darker gray)
  - Borders: `#495057` (medium gray)
  - Text: Proper contrast ratios for accessibility

#### Header & Navigation
- **Live Site Parity**: Header now matches the exact structure of [eqdb.net](https://eqdb.net/)
- **Logo Integration**: Uses the official EQDB logo (`eqdb_alt_4.png`)
- **Tools Dropdown**: Interactive dropdown menu with all tool categories:
  - Armor Search
  - Weapon Search
  - Waypoint List
  - Class Spell Listing
  - Pet Listing
- **Navigation Structure**: Spells, Items, Zones, NPCs, Tradeskills, Factions
- **User Links**: User Area, Identify Items, About, Changelog
- **Mobile Responsive**: Full mobile navigation with organized sections

#### Component Updates
- **Input Components**: Dark backgrounds with proper text contrast
- **Button Components**: Consistent theming across all buttons
- **Search Components**: Improved dropdown styling and accessibility
- **Card Components**: Proper background and border theming
- **Loading States**: Consistent spinner and loading indicators

For detailed frontend development information, see:
- [Frontend README](fe/README.md) - Complete frontend documentation
- [API Integration Guide](fe/API_INTEGRATION.md) - API-driven development approach
- [Implementation Plan](fe/IMPLEMENTATION_PLAN.md) - Development roadmap

### Storybook / Style Guide
- A static style guide is now available at `/storybook` in the frontend. This page demonstrates the current design system and component styles, including cards, buttons, inputs, skeletons, and more. No API calls are made from this page, so it is safe for design review and UI testing.
- **Design System Update:**
  - All cards, boxes, and buttons now use:
    - Outer border radius: 24px
    - Inner border radius: 16px
    - Padding: 8px
  - These values are applied consistently for a modern, unified look. See `/storybook` for live examples.

## Map Conversion System

EQDB includes an advanced map conversion system that transforms Brewall mapping format files into interactive 3D models for Babylon.js rendering.

### Overview
The map conversion system converts EverQuest zone maps from the Brewall mapping format into 3D glTF models that can be viewed in a web browser using Babylon.js. This provides an immersive way to explore game zones with full 3D navigation.

### Features
- **3D Zone Visualization**: Convert 2D map files to interactive 3D models
- **Interactive Navigation**: Arc Rotate Camera with zoom, pan, and rotate controls
- **Label System**: Display NPCs, merchants, zones, and points of interest
- **Color Preservation**: Maintain original map colors and styling
- **Performance Optimized**: Efficient rendering with geometry batching and LOD systems

### File Format Support
- **Main Geometry**: Line segments representing terrain, walls, and boundaries
- **Labels**: Point markers with text labels for NPCs and locations
- **Secondary Elements**: UI elements, compass markers, and overlays

### Development Status
- **Phase 1**: Foundation & Analysis - File parsing and data structure design
- **Phase 2**: Core Conversion Engine - Geometry generation and glTF export
- **Phase 3**: Proof of Concept - Overthere zone conversion and Babylon.js integration
- **Phase 4**: Enhanced Features - Performance optimization and interactive features
- **Phase 5**: Multi-Zone Support - Batch processing and database integration
- **Phase 6**: Production Deployment - Quality assurance and web integration

### Technical Stack
- **Python**: Core conversion logic with pygltflib for glTF generation
- **Babylon.js**: 3D rendering engine for web-based visualization
- **glTF**: Standard 3D format for efficient web delivery
- **NumPy**: Coordinate processing and mathematical operations

### Getting Started
The map conversion system is currently in development. For detailed information about the project plan and implementation, see:
- [Map Conversion Plan](maps/MAP_CONVERSION_PLAN.md) - Comprehensive development roadmap
- [Brewall Mapping Standards](https://www.eqmaps.info/eq-map-files/mapping-standards/) - Original format documentation

### Future Enhancements
- **Real-time Updates**: Live zone data integration
- **User Annotations**: Personal notes and markers
- **Pathfinding**: Visual navigation between points
- **Mobile Support**: Responsive design for mobile devices
- **VR/AR Support**: Virtual and augmented reality viewing

## Zone Static Data

- Large static dictionaries such as `ZONE_LEVEL_CHART` and `continent_zones` have been moved to `api/db/zone_settings.py`.
- If you need to add or update static zone-related data, edit `api/db/zone_settings.py` instead of `api/db/zone.py`.
- This keeps the main codebase cleaner and makes static data easier to maintain and share across modules.

## API Response Enhancement for Items

The item detail API now returns both the raw and human-readable values for item type and slots:

```
{
  "itemtype": 1,
  "itemtype_name": "2H Slashing",
  "slots": 2,
  "slot_names": "Primary",
  ...
}
```

- `itemtype_name` is generated using `get_type_string` from `utils.py`.
- `slot_names` is generated using `get_slot_string` from `utils.py`.
- The mapping logic for these fields is based on the `db_str` table (`type=4` for itemtype, `type=24` for slots) and the logic in `utils.py`.

See `knowledge_graph.md` for more details on the mapping tables and logic.

## Refactor: db_str Lookups Now Use Canonical Python Mappings

- All standard lookups for item types, slots, and classes now use canonical Python mappings and utility functions from `utils.py`:
  - Item types: `Util.get_categorized_item_types()`
  - Item slots: `Util.get_categorized_item_slots()`
  - Item classes: `{i: get_class_string(i) for i in range(1, 17)}`
  - Races: `get_bane_dmg_race(race_id)`
- The application no longer queries the `db_str` table for these mappings during item indexing, enrichment, or API lookups.
- **Rare/legacy cases:**
  - If a race ID is not mapped in `get_bane_dmg_race`, the code falls back to a direct `db_str` query (type=12). This is documented in `api/db/npc.py` and should be rare.
- This change significantly reduces database load and improves performance, especially for bulk operations like Redis indexing.
- If you add new mappings, update the relevant utility in `utils.py`.

## Recent Changes

### Performance Optimization for Item Search
- The `/api/v1/items/search` endpoint now uses Redis for fast item search and item detail retrieval.
- If item details are missing from the Redis cache, the system will fall back to the database, populate the cache, and return the enriched result.
- This change significantly improves response times for most item search queries, especially for common lookups.

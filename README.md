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

EQDB now includes a comprehensive local user account system with JWT authentication and API key management.

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

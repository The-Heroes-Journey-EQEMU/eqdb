Brewall Mapping standards: https://www.eqmaps.info/eq-map-files/mapping-standards/
Examples of renderings from it: https://www.eqmaps.info/map-comparisons/

Using the maps in maps/ directory. We want to generate 3d geometry that can be fed into babylon.js for viewing.

**Storage Architecture:**
- 3D geometry (glTF) files are stored in the filesystem (or CDN) for fast serving and browser/CDN caching.
- Only metadata (zone info, file path, stats, waypoints) is stored in the database for fast queries and relationships.
- This hybrid approach is the recommended and implemented strategy for the map conversion system, ensuring both performance and flexibility.

Initial Stage:
Proof of concept, single map (overthere). 
 1) Analyze files based on mapping standards
 2) Generate glTF Model using pygltflib 
 3) Render a test using babylon.js 
    a) Arc Rotate Camera: Zoom, pan, and rotate with mouse controls.
    b) Geometry from file should show visibly, so it may need to be immesive
    c) Add labels from _1 file, including text colors etc.

**Phase 2 Complete:**
- Geometry generation, material system, and glTF export are fully implemented and tested.
- Output glTF files are validated and ready for Babylon.js integration.

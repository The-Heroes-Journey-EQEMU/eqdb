Brewall Mapping standards: https://www.eqmaps.info/eq-map-files/mapping-standards/
Examples of renderings from it: https://www.eqmaps.info/map-comparisons/

Using the maps in maps/ directory. We want to generate 3d geometry that can be fed into babylon.js for viewing.

Initial Stage:
Proof of concept, single map (overthere). 
 1) Analyze files based on mapping standards
 2) Generate glTF Model using pygltflib 
 3) Render a test using babylon.js 
    a) Arc Rotate Camera: Zoom, pan, and rotate with mouse controls.
    b) Geometry from file should show visibly, so it may need to be immesive
    c) Add labels from _1 file, including text colors etc.

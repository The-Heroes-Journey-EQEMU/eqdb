import React, { useEffect, useRef } from 'react';
import { Zone } from '../../services/zoneService';
import { SVG } from '@svgdotjs/svg.js';
import '@svgdotjs/svg.panzoom.js';

interface ZoneMapProps {
  zone: Zone;
}

const ZoneMap: React.FC<ZoneMapProps> = ({ zone }) => {
  const svgRef = useRef<HTMLDivElement>(null);
  const mousePositionRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!svgRef.current || !zone.mapping || zone.mapping.length === 0) return;

    // Calculate bounding box
    let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
    zone.mapping.forEach(line => {
        minX = Math.min(minX, line.x1, line.x2);
        minY = Math.min(minY, line.y1, line.y2);
        maxX = Math.max(maxX, line.x1, line.x2);
        maxY = Math.max(maxY, line.y1, line.y2);
    });

    const width = maxX - minX;
    const height = maxY - minY;
    
    // Add some padding
    const padding = 50;
    const viewBoxX = minX - padding;
    const viewBoxY = minY - padding;
    const viewBoxWidth = width + padding * 2;
    const viewBoxHeight = height + padding * 2;

    if (!svgRef.current) return;
    svgRef.current.innerHTML = '';
    const draw = SVG().addTo(svgRef.current).size('100%', '100%');
    draw.viewbox(viewBoxX, viewBoxY, viewBoxWidth, viewBoxHeight);

    zone.mapping.forEach(line => {
      let color = `rgb(${line.rgb})`;
      if (line.rgb === '0, 0, 0') {
        color = 'white';
      }
      draw.line(line.x1, line.y1, line.x2, line.y2).stroke({ width: 2, color: color });
    });

    if (zone.waypoint) {
      draw.circle(25).center(zone.waypoint.y * -1, zone.waypoint.x * -1).fill('blue');
    }

    if (zone.safe_x && zone.safe_y) {
        draw.circle(25).center(zone.safe_y * -1, zone.safe_x * -1).fill('green');
    }

    draw.panZoom({ zoomMin: 0.1, zoomMax: 10, zoomFactor: 0.05 });

    const svgElement = svgRef.current.querySelector('svg');
    if (svgElement) {
      const pt = svgElement.createSVGPoint();

      const cursorPoint = (evt: MouseEvent) => {
        pt.x = evt.clientX;
        pt.y = evt.clientY;
        const ctm = svgElement.getScreenCTM();
        if (ctm) {
            return pt.matrixTransform(ctm.inverse());
        }
        return pt;
      };

      const mouseMoveHandler = (evt: MouseEvent) => {
        const loc = cursorPoint(evt);
        if (mousePositionRef.current) {
          const flippedY = -Math.round(loc.y);
          const flippedX = -Math.round(loc.x);
          mousePositionRef.current.textContent = `Y: ${flippedY}, X: ${flippedX}`;
        }
      };

      const zoomHandler = (event: any) => {
        const zoomLevel = event.detail.level;
        let newStrokeWidth;

        if (zoomLevel >= 0.25) {
          newStrokeWidth = 2;
        } else if (zoomLevel >= 0.9) {
          newStrokeWidth = 1;
        } else if (zoomLevel >= 0.1) {
          // Linear interpolation between (0.35, 2) and (0.1, 20)
          const zoomProgress = (0.25 - zoomLevel) / (0.25 - 0.1);
          newStrokeWidth = 2 + zoomProgress * 8;
        } else {
          newStrokeWidth = 2 / zoomLevel;
        }

        draw.find('line').forEach(line => {
          line.stroke({ width: newStrokeWidth });
        });
      };

      svgElement.addEventListener('mousemove', mouseMoveHandler);
      svgElement.addEventListener('zoom', zoomHandler);


      return () => {
        svgElement.removeEventListener('mousemove', mouseMoveHandler);
        svgElement.removeEventListener('zoom', zoomHandler);
      };
    }
  }, [zone]);

  return (
    <div style={{ position: 'relative', width: '100%', height: '100%', backgroundColor: 'black' }}>
      <div ref={svgRef} style={{ width: '100%', height: '100%', border: '1px solid black' }} />
      <div ref={mousePositionRef} style={{
        position: 'absolute',
        bottom: '10px',
        left: '10px',
        backgroundColor: 'rgba(255, 255, 255, 0.7)',
        padding: '5px',
        borderRadius: '5px',
        fontFamily: 'Arial, sans-serif',
        fontSize: '14px',
        color: 'black',
      }}>
        X: 0, Y: 0
      </div>
    </div>
  );
};

export default ZoneMap;

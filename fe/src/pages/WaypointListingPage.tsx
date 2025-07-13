import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { zoneService } from '../services/zoneService';

interface Waypoint {
    x: number;
    y: number;
    z: number;
}

interface ZoneData {
    id: number;
    short_name: string;
    waypoint: Waypoint;
}

interface ContinentData {
    [zoneName: string]: ZoneData;
}

interface WaypointsByContinent {
    [continentName: string]: ContinentData;
}

const WaypointListingPage: React.FC = () => {
  const [waypointsByContinent, setWaypointsByContinent] = useState<WaypointsByContinent>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchZones = async () => {
      try {
        const data = await zoneService.getZonesWithWaypoints();
        setWaypointsByContinent(data);
      } catch (err) {
        setError('Failed to fetch zones with waypoints.');
      } finally {
        setLoading(false);
      }
    };

    fetchZones();
  }, []);

  if (loading) {
    return <div>Loading...</div>;
  }

  if (error) {
    return <div>{error}</div>;
  }

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-4">Zones with Waypoints</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {Object.entries(waypointsByContinent).map(([continent, zones]) => (
          <div key={continent} className="p-4 bg-card text-card-foreground border border-border rounded-md">
            <h2 className="text-2xl font-semibold pb-2 mb-4 text-foreground">{continent}</h2>
            <table className="w-full text-left border-t-2 border-gray-700">
              <tbody>
                {Object.entries(zones).map(([zoneName, zoneData]) => (
                  <tr key={zoneData.id} className="card-background border-b-2 border-gray-700">
                    <td className="p-1 border-b-1 border-gray-600">
                      <Link to={`/zones/detail/${zoneData.short_name}`} className="text-blue-100 hover:underline">
                        {zoneName}
                      </Link>
                    </td>
                    <td className="p-1 text-sm card-foreground">( {`${zoneData.waypoint.x}, ${zoneData.waypoint.y}, ${zoneData.waypoint.z}`} )</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ))}
      </div>
    </div>
  );
};

export default WaypointListingPage;

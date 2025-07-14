import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { zoneService, Zone, ZonesByExpansion } from '../services/zoneService';


const ZoneListPage: React.FC = () => {
  const [zonesByExpansion, setZonesByExpansion] = useState<ZonesByExpansion>({});
  const [activeExpansion, setActiveExpansion] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const zonesData = await zoneService.getZonesByExpansion();
        const processedZones: ZonesByExpansion = {};

        for (const expansionName in zonesData) {
          const zones = zonesData[expansionName];
          const uniqueZones = Array.from(new Map(zones.map(zone => [zone.short_name, zone])).values());
          processedZones[expansionName] = uniqueZones.sort((a, b) => a.long_name.localeCompare(b.long_name));
        }

        setZonesByExpansion(processedZones);

        const expansionNames = Object.keys(processedZones);
        if (expansionNames.length > 0) {
          // Set the initial active tab to the first expansion in the list
          // We'll rely on the backend to send them in the correct order.
          setActiveExpansion(expansionNames[0]);
        }
      } catch (err) {
        setError('Failed to fetch zone data.');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) {
    return <div>Loading...</div>;
  }

  if (error) {
    return <div>{error}</div>;
  }

  return (
    <div className="container mx-auto p-4">
      <div className="flex border-b border-gray-600 overflow-x-auto">
        {Object.keys(zonesByExpansion).map((expansionName) => (
          <button
            key={expansionName}
            className={`py-2 px-4 text-lg font-medium whitespace-nowrap ${
              activeExpansion === expansionName
                ? 'border-b-2 border-blue-500 text-blue-400'
                : 'text-gray-400 hover:text-white'
            }`}
            onClick={() => setActiveExpansion(expansionName)}
            
          >
            {expansionName}
          </button>
        ))}
      </div>
      <div className="py-4">
        {activeExpansion && zonesByExpansion[activeExpansion] && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-x-6 gap-y-4">
            {zonesByExpansion[activeExpansion].map((zone: Zone) => (
              <Link key={zone.short_name} to={`/zones/detail/${zone.short_name}`}>
                <div className="card rounded-md">
                    <div className="text-blue-100 hover:underline font-bold flex justify-between items-center py-2 px-5">
                      <span className="text-sm">{zone.long_name}</span>
                      <i className="text-xs font-normal">{zone.short_name}</i>
                    </div>
                    <div className="bg-gray-700 px-5 py-2 flex justify-between">
                      <div className="text-sm text-muted-foreground">
                        ZEM: {zone.zone_exp_multiplier}
                      </div>
                      <div className="text-sm text-muted-foreground">
                        Level Range: {zone.zone_level_range}
                      </div>
                    </div>
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default ZoneListPage;

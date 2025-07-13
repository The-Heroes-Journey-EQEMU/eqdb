import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { zoneService, Zone } from '../services/zoneService';

type ZonesByContinent = Record<string, Zone[]>;

const ZoneListPage: React.FC = () => {
  const [zonesByContinent, setZonesByContinent] = useState<ZonesByContinent>({});
  const [activeContinent, setActiveContinent] = useState<string>('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const includedExpansions = [
    'Classic',
    'The Ruins of Kunark',
    'The Scars of Velious',
    'The Shadows of Luclin',
    'The Planes of Power',
  ];

  useEffect(() => {
    const fetchZones = async () => {
      try {
        const data = await zoneService.getZonesByExpansion();
        const allZones = Object.entries(data)
          .filter(([expansionName]) => includedExpansions.includes(expansionName))
          .flatMap(([, zones]) => zones);

        const groupedByContinent = allZones.reduce((acc, zone) => {
          const continent = zone.continent || 'Unknown';
          if (!acc[continent]) {
            acc[continent] = [];
          }
          acc[continent].push(zone);
          return acc;
        }, {} as ZonesByContinent);

        const orderedContinents = ['Antonica', 'Faydwer', 'Odus', 'Kunark', 'Velious', 'Luclin', 'Planes'].filter(c => groupedByContinent[c]);
        const otherContinents = Object.keys(groupedByContinent).filter(c => !orderedContinents.includes(c));
        const finalOrder = [...orderedContinents, ...otherContinents];

        const orderedZonesByContinent = finalOrder.reduce((acc, continent) => {
            acc[continent] = groupedByContinent[continent];
            return acc;
        }, {} as ZonesByContinent);
        
        setZonesByContinent(orderedZonesByContinent);

        if (finalOrder.length > 0) {
          setActiveContinent(finalOrder[0]);
        }
      } catch (err) {
        setError('Failed to fetch zones.');
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
      <div className="flex border-b border-gray-600">
        {Object.keys(zonesByContinent).map((continent) => (
          <button
            key={continent}
            className={`py-2 px-4 text-lg font-medium px-10 ${
              activeContinent === continent
                ? 'border-b-2 border-blue-500 text-blue-400'
                : 'text-gray-400 hover:text-white'
            }`}
            onClick={() => setActiveContinent(continent)}
          >
            {continent}
          </button>
        ))}
      </div>
      <div className="py-4">
        {activeContinent && zonesByContinent[activeContinent] && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-x-6 gap-y-4">
            {zonesByContinent[activeContinent].map((zone, index) => (
              <div key={`${zone.short_name}-${index}`}>
                <Link to={`/zones/detail/${zone.short_name}`} className="text-blue-400 hover:underline">
                  {zone.long_name}
                </Link>
                <div className="text-sm text-muted-foreground">
                  ({zone.short_name})
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default ZoneListPage;

import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { zoneService, Zone } from '../services/zoneService';

type ZonesByContinent = Record<string, Zone[]>;

const continent_zones: Record<string, string[]> = {
    'Antonica': ['blackburrow', 'commons', 'ecommons', 'feerrott', 'freportw', 'grobb', 'everfrost', 'halas', 'highkeep', 'lavastorm', 'neriakb', 'northkarana', 'eastkarana', 'oasis', 'oggok', 'oot', 'qey2hh1', 'qeynos2', 'qrg', 'rivervale', 'gukbottom', 'lakerathe', 'southkarana'],
    'Faydwer': ['akanon', 'cauldron', 'felwithea', 'gfaydark', 'kaladima', 'mistmoore'],
    'Odus': ['erudnext', 'hole', 'paineel', 'tox', 'stonebrunt', 'dulak', 'gunthak'],
    'Kunark': ['burningwood', 'cabeast', 'citymist', 'dreadlands', 'fieldofbone', 'firiona', 'frontiermtns', 'karnor', 'lakeofillomen', 'overthere', 'skyfire', 'timorous', 'trakanon', 'chardokb'],
    'Velious': ['cobaltscar', 'eastwastes', 'greatdivide', 'iceclad', 'wakening', 'westwastes', 'sirens'],
    'Luclin': ['dawnshroud', 'fungusgrove', 'sharvahl', 'ssratemple', 'tenebrous', 'umbral', 'twilight', 'scarlet', 'paludal', 'bazaar'],
    'Planes': ['airplane', 'fearplane', 'hateplaneb', 'poknowledge', 'potranquility', 'potimea']
};

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
        const filteredZones = Object.entries(data)
          .filter(([expansionName]) => includedExpansions.includes(expansionName))
          .flatMap(([, zones]) => zones);

        const groupedByContinent = Object.keys(continent_zones).reduce((acc, continent) => {
          acc[continent] = filteredZones.filter(zone => continent_zones[continent].includes(zone.short_name));
          return acc;
        }, {} as ZonesByContinent);

        setZonesByContinent(groupedByContinent);
        if (Object.keys(groupedByContinent).length > 0) {
          setActiveContinent(Object.keys(groupedByContinent)[0]);
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
                <Link to={`/zone/${zone.short_name}`} className="text-blue-400 hover:underline">
                  {zone.long_name}
                </Link>
                <div className="text-sm text-muted-foreground">
                  ({zone.short_name})
                </div>
                <div className="text-sm">ZEM: 2.00</div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default ZoneListPage;

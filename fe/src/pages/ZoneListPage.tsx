import React, { useEffect, useState, useMemo } from 'react';
import { Link } from 'react-router-dom';
import { zoneService, Zone, ZonesByExpansion } from '../services/zoneService';
import Card from '@/components/common/Card';

const ZoneListPage: React.FC = () => {
  const [zonesByExpansion, setZonesByExpansion] = useState<ZonesByExpansion>({});
  const [activeExpansion, setActiveExpansion] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [minLevel, setMinLevel] = useState(0);
  const [maxLevel, setMaxLevel] = useState(70);

  const minLevelOptions = Array.from({ length: 12 }, (_, i) => i * 5); // 0, 5, ..., 55
  const maxLevelOptions = Array.from({ length: 15 }, (_, i) => 70 - i * 5); // 70, 65, ..., 5

  const handleMinLevelChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const newMinLevel = parseInt(e.target.value, 10);
    setMinLevel(newMinLevel);
    if (newMinLevel >= maxLevel) {
      setMaxLevel(newMinLevel + 5);
    }
  };

  const handleMaxLevelChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const newMaxLevel = parseInt(e.target.value, 10);
    setMaxLevel(newMaxLevel);
    if (newMaxLevel <= minLevel) {
      setMinLevel(newMaxLevel - 5);
    }
  };

  const filteredZones = useMemo(() => {
    if (!activeExpansion || !zonesByExpansion[activeExpansion]) {
      return [];
    }
    return zonesByExpansion[activeExpansion].filter(zone => {
      const zoneMin = zone.min_level ?? 0;
      const zoneMax = zone.max_level ?? 70;
      return zoneMin <= maxLevel && zoneMax >= minLevel;
    });
  }, [activeExpansion, zonesByExpansion, minLevel, maxLevel]);

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
      <div className="flex flex-col lg:flex-row lg:justify-between lg:items-center border-b border-gray-600 pb-4">
        <div className="flex flex-wrap gap-1 mb-4 lg:mb-0">
          {Object.keys(zonesByExpansion).map((expansionName) => (
            <button
              key={expansionName}
              className={`py-2 px-3 text-sm font-medium rounded-t-lg transition-colors duration-200 ${
                activeExpansion === expansionName
                  ? 'bg-blue-600 text-white border-b-2 border-blue-400'
                  : 'text-gray-400 hover:text-white hover:bg-gray-700'
              }`}
              onClick={() => setActiveExpansion(expansionName)}
            >
              {expansionName}
            </button>
          ))}
        </div>
        <div className="flex items-center space-x-2">
          <span className="text-sm text-gray-400">Level Range:</span>
          <select value={minLevel} onChange={handleMinLevelChange} className="bg-gray-700 text-white rounded p-1 text-sm">
            {minLevelOptions.filter(level => level < maxLevel - 5).map(level => (
              <option key={level} value={level}>{level}</option>
            ))}
          </select>
          <span className="text-gray-400">-</span>
          <select value={maxLevel} onChange={handleMaxLevelChange} className="bg-gray-700 text-white rounded p-1 text-sm">
            {maxLevelOptions.filter(level => level > minLevel + 5).map(level => (
              <option key={level} value={level}>{level}</option>
            ))}
          </select>
        </div>
      </div>
      <div className="py-4">
        {activeExpansion && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-x-6 gap-y-4">
            {filteredZones.map((zone: Zone) => (
              <Link key={zone.short_name} to={`/zones/detail/${zone.short_name}`}>
                <Card className="h-full">
                  <div className="text-blue-100 hover:underline font-bold flex justify-between items-center py-2 px-5">
                    <span className="text-sm">{zone.long_name}</span>
                    <i className="text-xs font-normal">{zone.short_name}</i>
                  </div>
                  <div className="bg-gray-700 px-5 py-2 flex justify-between rounded-b-[16px]">
                    <div className="text-sm text-muted-foreground">
                      ZEM: {zone.zone_exp_multiplier}
                    </div>
                    <div className="text-sm text-muted-foreground">
                      Level Range: {zone.min_level} - {zone.max_level}
                    </div>
                  </div>
                </Card>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default ZoneListPage;
